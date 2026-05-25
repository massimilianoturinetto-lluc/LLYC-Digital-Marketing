#!/usr/bin/env python3
"""
Sigue las cadenas de redirección para URLs PrestaShop y clasifica patrones.

Lee 30 URLs PrestaShop del CSV de 03_crawl_sitemaps.py (muestra estratificada
50/50 entre productos y categorías) y para cada una:

  1. Sigue la cadena de redirecciones HTTP (301/302/303/307/308) manualmente.
  2. Si el status final es 200, descarga el body y detecta:
       - meta refresh:  <meta http-equiv="refresh" content="0;url=...">
       - JS redirect:   window.location / location.href / location.replace
  3. Registra cada salto y clasifica el patrón.

Detección de patrones problemáticos:
  - has_302_temporary: algún salto fue 302/307 (debería ser 301/308 si es permanente)
  - long_chain:       > 1 salto
  - redirects_to_home: URL final es el apex root
  - loop:             se visitó dos veces la misma URL
  - no_redirect:      sin redirect, devolvió 200 directamente (URL viva en PS)
  - meta_refresh:     redirect vía <meta refresh>
  - js_redirect:      redirect vía JavaScript (heurístico)

Uso:
    python3 06_redirect_chains.py
    python3 06_redirect_chains.py --sample 50 --input 03_sitemaps.csv

Salida:
    06_redirecciones.csv
    Resumen agregado en stdout.

Dependencias: solo stdlib.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 15
MAX_HOPS = 10
DELAY_MIN = 1.0
DELAY_MAX = 2.0
RANDOM_SEED = 42

SHOPIFY_APEX = "https://lacasadelascarcasas.es"


@dataclass
class Hop:
    url: str
    status: int | str
    location: str = ""
    kind: str = ""  # "http-301" | "http-302" | "meta-refresh" | "js" | "final" | "error"


@dataclass
class Chain:
    initial_url: str
    type_initial: str
    hops: list[Hop] = field(default_factory=list)
    flags: set[str] = field(default_factory=set)
    notes: str = ""

    @property
    def final_url(self) -> str:
        return self.hops[-1].url if self.hops else self.initial_url

    @property
    def final_status(self) -> int | str:
        return self.hops[-1].status if self.hops else ""

    @property
    def redirect_kinds(self) -> list[str]:
        return [h.kind for h in self.hops if h.kind not in ("final", "error")]


# ---------- HTTP con manejo manual de redirects ----------

class NoFollow(urllib.request.HTTPRedirectHandler):
    """No sigue redirects automáticamente — los manejamos en follow_chain."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def head_or_get(url: str, get: bool = False) -> tuple[int | str, dict, bytes]:
    """Devuelve (status, headers, body). HEAD por defecto; body vacío en HEAD."""
    method = "GET" if get else "HEAD"
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept-Language": "es-ES,es"})
    opener = urllib.request.build_opener(NoFollow())
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            body = resp.read() if get else b""
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as e:
        body = e.read() if get else b""
        return e.code, dict(e.headers or {}), body
    except urllib.error.URLError as e:
        return f"ERR:{e.reason}", {}, b""
    except Exception as e:
        return f"ERR:{type(e).__name__}", {}, b""


META_REFRESH_RX = re.compile(
    r'<meta[^>]+http-equiv\s*=\s*["\']?refresh["\']?[^>]+content\s*=\s*["\']\s*\d+\s*;\s*url\s*=\s*([^"\'> ]+)',
    re.I,
)
JS_REDIRECT_RX = re.compile(
    r'(?:window\.location|location\.href|location\.replace|location\.assign)\s*[=(]\s*["\']([^"\']+)["\']',
    re.I,
)


def detect_html_redirect(body: bytes, base_url: str) -> tuple[str | None, str | None]:
    """Devuelve (url_destino, kind) si hay meta refresh o JS redirect en el HTML."""
    try:
        text = body.decode("utf-8", errors="replace")
    except Exception:
        return None, None
    # Solo miramos los primeros 200 KB (head/start of body)
    head = text[:200_000]
    m = META_REFRESH_RX.search(head)
    if m:
        return urllib.parse.urljoin(base_url, m.group(1)), "meta-refresh"
    m = JS_REDIRECT_RX.search(head)
    if m:
        return urllib.parse.urljoin(base_url, m.group(1)), "js"
    return None, None


def follow_chain(initial: str) -> Chain:
    chain = Chain(initial_url=initial, type_initial=classify_ps_url(initial))
    visited: set[str] = set()
    current = initial

    for hop_idx in range(MAX_HOPS + 1):
        if current in visited:
            chain.hops.append(Hop(current, "LOOP", kind="error"))
            chain.flags.add("loop")
            return chain
        visited.add(current)

        status, headers, _ = head_or_get(current, get=False)

        if isinstance(status, int) and status in (301, 302, 303, 307, 308):
            loc = headers.get("Location") or headers.get("location") or ""
            loc = urllib.parse.urljoin(current, loc) if loc else ""
            kind = f"http-{status}"
            chain.hops.append(Hop(current, status, loc, kind))
            if status in (302, 307):
                chain.flags.add("has_302_temporary")
            if not loc:
                chain.flags.add("redirect_without_location")
                return chain
            current = loc
            continue

        if isinstance(status, int) and status == 200:
            # Posible meta refresh / JS redirect → GET body
            status2, _, body = head_or_get(current, get=True)
            target, kind = detect_html_redirect(body, current)
            if target:
                chain.hops.append(Hop(current, 200, target, kind))
                chain.flags.add(kind.replace("-", "_"))
                current = target
                continue
            chain.hops.append(Hop(current, 200, kind="final"))
            return chain

        # Cualquier otro status → final
        chain.hops.append(Hop(current, status, kind="final" if isinstance(status, int) else "error"))
        return chain

    chain.flags.add("max_hops_exceeded")
    chain.hops.append(Hop(current, "MAX_HOPS", kind="error"))
    return chain


def classify_pattern(chain: Chain) -> None:
    """Añade flags al chain según los patrones del enunciado."""
    redirect_count = len(chain.redirect_kinds)
    if redirect_count == 0 and isinstance(chain.final_status, int) and chain.final_status == 200:
        chain.flags.add("no_redirect")
    if redirect_count > 1:
        chain.flags.add("long_chain")
    # ¿final apex root?
    final_parsed = urllib.parse.urlparse(chain.final_url)
    if final_parsed.netloc.endswith("lacasadelascarcasas.es") \
       and not final_parsed.netloc.startswith("prestashop.") \
       and final_parsed.path.rstrip("/") == "":
        chain.flags.add("redirects_to_home")


# ---------- muestreo ----------

def classify_ps_url(url: str) -> str:
    if re.search(r"\.html(\?|$)", url) or "id_product=" in url:
        return "product"
    if re.search(r"^https?://[^/]+/?$", url):
        return "home"
    if re.search(r"/(category|categoria)/", url, re.I) or re.match(r"^https?://[^/]+/\d+-[a-z0-9-]+/?$", url):
        return "collection"
    if "id_cms=" in url or "/content/" in url:
        return "page"
    return "other"


def stratified_sample(ps_urls: list[str], total: int) -> list[str]:
    """Mitad productos / mitad categorías, completa con otros si no llega."""
    rng = random.Random(RANDOM_SEED)
    by_type: dict[str, list[str]] = {"product": [], "collection": [], "other": []}
    for u in ps_urls:
        t = classify_ps_url(u)
        by_type[t if t in by_type else "other"].append(u)

    target_each = total // 2
    sampled: list[str] = []
    sampled += rng.sample(by_type["product"], min(target_each, len(by_type["product"])))
    sampled += rng.sample(by_type["collection"], min(target_each, len(by_type["collection"])))
    # rellenar
    if len(sampled) < total:
        rest = [u for u in ps_urls if u not in sampled]
        sampled += rng.sample(rest, min(total - len(sampled), len(rest)))
    return sampled[:total]


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="03_sitemaps.csv")
    ap.add_argument("--output", default="06_redirecciones.csv")
    ap.add_argument("--sample", type=int, default=30)
    ap.add_argument("--delay-min", type=float, default=DELAY_MIN)
    ap.add_argument("--delay-max", type=float, default=DELAY_MAX)
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: no encuentro {in_path}. Ejecuta antes 03_crawl_sitemaps.py.", file=sys.stderr)
        return 1

    ps_urls: list[str] = []
    with in_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["env"] == "prestashop":
                ps_urls.append(row["url"])
    if not ps_urls:
        print("No hay URLs PrestaShop en el CSV.", file=sys.stderr)
        return 1

    sample = stratified_sample(ps_urls, args.sample)
    print(f"Muestreadas {len(sample)} URLs PrestaShop ({sum(1 for u in sample if classify_ps_url(u)=='product')} productos, "
          f"{sum(1 for u in sample if classify_ps_url(u)=='collection')} categorías).\n")

    chains: list[Chain] = []
    rng = random.Random(RANDOM_SEED)
    for i, url in enumerate(sample, 1):
        chain = follow_chain(url)
        classify_pattern(chain)
        chains.append(chain)
        markers = " ".join(sorted(chain.flags)) or "—"
        print(f"  [{i:2}/{len(sample)}] {len(chain.hops)} hops → {chain.final_status}  flags: {markers}")
        time.sleep(rng.uniform(args.delay_min, args.delay_max))

    write_csv(chains, args.output)
    print_summary(chains)
    print(f"\nDetalle: {args.output}")
    return 0


def write_csv(chains: list[Chain], path: str) -> None:
    fieldnames = [
        "initial_url", "type_initial", "hops_count", "redirect_kinds",
        "final_url", "final_status", "hop_chain", "pattern_flags", "notes",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for c in chains:
            hop_chain = " >> ".join(f"{h.url} [{h.status} {h.kind}]" for h in c.hops)
            w.writerow({
                "initial_url": c.initial_url,
                "type_initial": c.type_initial,
                "hops_count": sum(1 for h in c.hops if h.kind not in ("final", "error")),
                "redirect_kinds": "|".join(c.redirect_kinds),
                "final_url": c.final_url,
                "final_status": c.final_status,
                "hop_chain": hop_chain,
                "pattern_flags": "|".join(sorted(c.flags)),
                "notes": c.notes,
            })


def print_summary(chains: list[Chain]) -> None:
    n = len(chains)
    flags = Counter(f for c in chains for f in c.flags)
    finals = Counter(c.final_status for c in chains)
    print("\n" + "=" * 60)
    print(f"Total cadenas analizadas:  {n}")
    print("\nDistribución de status final:")
    for s, count in finals.most_common():
        print(f"  {s}: {count}  ({count/n:.0%})")
    print("\nPatrones detectados:")
    for flag, count in flags.most_common():
        print(f"  {flag:30s} {count:3d}  ({count/n:.0%})")
    if not flags:
        print("  (ninguno)")


if __name__ == "__main__":
    sys.exit(main())
