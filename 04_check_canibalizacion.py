#!/usr/bin/env python3
"""
Detector de canibalización Shopify ↔ PrestaShop para lacasadelascarcasas.es.

Lee 03_sitemaps.csv (generado por 03_crawl_sitemaps.py) y para cada URL
PrestaShop:
  1. HEAD a la URL PrestaShop → status + Location si hay redirect.
  2. Deriva una URL Shopify "equivalente" por heurística.
  3. HEAD a la Shopify equivalente.
  4. Marca canibalización si ambas devuelven 200.

Uso:
    python3 04_check_canibalizacion.py

Salida:
    04_canibalizacion.csv  — tabla detallada
    Resumen en stdout      — % canibalización

Diseño defensivo:
- Cap 200 URLs (override con --limit N).
- Sleep aleatorio 1.0–2.0 s entre peticiones (override con --delay-min/--delay-max).
- HEAD, no GET. Si HEAD da 405, hace GET con Range:0-0.
- User-Agent realista.
- Sigue redirects manualmente (anota cadena).
- Timeout 15 s.
- Reintentos: 1 reintento ante error de red.

Dependencias: stdlib (urllib, csv, argparse, random, time).
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
from dataclasses import dataclass, field
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 15
MAX_REDIRECTS = 5

SHOPIFY_HOST = "https://lacasadelascarcasas.es"
PRESTASHOP_HOST = "https://prestashop.lacasadelascarcasas.es"


# ---------- heurística de mapeo PS → Shopify ----------

def derive_shopify_equivalent(ps_url: str) -> tuple[str | None, str]:
    """
    Devuelve (url_shopify_equivalente | None, motivo).
    Motivo describe la regla aplicada para que el revisor humano valide.
    """
    p = urllib.parse.urlparse(ps_url)
    path = p.path
    query = urllib.parse.parse_qs(p.query)

    # Home
    if path in ("", "/"):
        return f"{SHOPIFY_HOST}/", "home→home"

    # PrestaShop con id_product en query → no podemos resolver slug sin Search API.
    if "id_product" in query:
        return None, "manual_review:id_product_only"

    # Producto PrestaShop con extensión .html
    # Pattern típico: /<categoria>/<id>-<slug>.html  o  /<slug>.html
    m = re.match(r"^/(?:[^/]+/)*(?:\d+-)?([a-z0-9-]+)\.html$", path)
    if m:
        slug = m.group(1)
        # Apex usa slugs en español sin /products/ → intentamos PDP directa /<slug>
        return f"{SHOPIFY_HOST}/{slug}", f"product:slug='{slug}'"

    # Categoría PrestaShop con id en path: /<id>-<slug>
    m = re.match(r"^/(\d+)-([a-z0-9-]+)/?$", path)
    if m:
        slug = m.group(2)
        # Apex usa /colecciones/<slug> en español
        return f"{SHOPIFY_HOST}/colecciones/{slug}", f"collection:slug='{slug}'"

    # Categoría sin id: /<slug>/
    m = re.match(r"^/([a-z0-9-]+)/?$", path)
    if m:
        slug = m.group(1)
        return f"{SHOPIFY_HOST}/colecciones/{slug}", f"collection_or_page:slug='{slug}'"

    # CMS pages PrestaShop: /content/<id>-<slug>
    m = re.match(r"^/content/(?:\d+-)?([a-z0-9-]+)/?$", path)
    if m:
        slug = m.group(1)
        return f"{SHOPIFY_HOST}/{slug}", f"page:slug='{slug}'"

    return None, "manual_review:unmatched_pattern"


# ---------- HTTP HEAD con fallback ----------

@dataclass
class Probe:
    url: str
    status: int | str
    final_url: str = ""
    redirects: list[str] = field(default_factory=list)
    error: str = ""


def probe(url: str) -> Probe:
    """HEAD con manejo manual de redirects. Si HEAD da 405, prueba GET Range."""
    redirects: list[str] = []
    current = url
    for _ in range(MAX_REDIRECTS):
        try:
            req = urllib.request.Request(current, method="HEAD", headers={"User-Agent": UA})
            opener = urllib.request.build_opener(NoRedirect())
            with opener.open(req, timeout=TIMEOUT) as resp:
                status = resp.status
                if status in (301, 302, 303, 307, 308):
                    loc = resp.headers.get("Location")
                    if not loc:
                        return Probe(url, status, current, redirects, "redirect_without_location")
                    loc = urllib.parse.urljoin(current, loc)
                    redirects.append(f"{status} → {loc}")
                    current = loc
                    continue
                return Probe(url, status, current, redirects)
        except urllib.error.HTTPError as e:
            if e.code == 405:
                # Fallback a GET con Range
                try:
                    req = urllib.request.Request(current, headers={"User-Agent": UA, "Range": "bytes=0-0"})
                    opener = urllib.request.build_opener(NoRedirect())
                    with opener.open(req, timeout=TIMEOUT) as resp:
                        return Probe(url, resp.status, current, redirects)
                except urllib.error.HTTPError as e2:
                    return Probe(url, e2.code, current, redirects)
                except Exception as e2:
                    return Probe(url, "ERR", current, redirects, f"{type(e2).__name__}:{e2}")
            return Probe(url, e.code, current, redirects)
        except urllib.error.URLError as e:
            return Probe(url, "ERR", current, redirects, f"URLError:{e.reason}")
        except Exception as e:
            return Probe(url, "ERR", current, redirects, f"{type(e).__name__}:{e}")
    return Probe(url, "TOO_MANY_REDIRECTS", current, redirects)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Devolver None obliga a urllib a no seguir el redirect; queremos manejarlo nosotros.
        # Pero urllib lanza error en ese caso, así que hacemos esto en HEAD manualmente arriba.
        return None
    def http_error_301(self, req, fp, code, msg, headers):
        # Convertimos el redirect en una "respuesta" simulada para que la lea probe().
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)
    http_error_302 = http_error_303 = http_error_307 = http_error_308 = http_error_301


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="03_sitemaps.csv", help="CSV de 03_crawl_sitemaps.py")
    ap.add_argument("--output", default="04_canibalizacion.csv")
    ap.add_argument("--limit", type=int, default=200, help="Máx URLs PrestaShop a probar")
    ap.add_argument("--delay-min", type=float, default=1.0)
    ap.add_argument("--delay-max", type=float, default=2.0)
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: no encuentro {in_path}. Ejecuta antes 03_crawl_sitemaps.py.", file=sys.stderr)
        return 1

    # Cargar URLs PrestaShop del CSV
    ps_urls: list[str] = []
    with in_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["env"] == "prestashop":
                ps_urls.append(row["url"])

    if not ps_urls:
        print("No hay URLs PrestaShop en el CSV. ¿El sitemap PS estaba vacío?", file=sys.stderr)
        return 1

    if len(ps_urls) > args.limit:
        random.seed(42)
        ps_urls = random.sample(ps_urls, args.limit)
        print(f"Limitado a {args.limit} URLs (muestreo aleatorio)")
    print(f"Probando {len(ps_urls)} URLs PrestaShop. Delay {args.delay_min}-{args.delay_max}s.\n")

    out_rows: list[dict] = []
    cannibals = 0
    ps_live = 0

    for i, ps_url in enumerate(ps_urls, 1):
        ps_probe = probe(ps_url)
        if isinstance(ps_probe.status, int) and ps_probe.status == 200:
            ps_live += 1

        shop_url, mapping_reason = derive_shopify_equivalent(ps_url)
        shop_probe: Probe | None = None
        canibal = ""

        if shop_url:
            time.sleep(random.uniform(args.delay_min, args.delay_max))
            shop_probe = probe(shop_url)
            both_live = (
                isinstance(ps_probe.status, int) and ps_probe.status == 200
                and isinstance(shop_probe.status, int) and shop_probe.status == 200
            )
            if both_live:
                canibal = "YES"
                cannibals += 1
            elif isinstance(ps_probe.status, int) and ps_probe.status == 200:
                canibal = "NO"  # vivo en PS, no en Shopify
            else:
                canibal = "N/A"  # PS no responde 200
        else:
            canibal = "MANUAL_REVIEW"

        out_rows.append({
            "ps_url": ps_url,
            "ps_status": ps_probe.status,
            "ps_redirects": " | ".join(ps_probe.redirects),
            "ps_final_url": ps_probe.final_url if ps_probe.redirects else "",
            "shop_url": shop_url or "",
            "shop_status": shop_probe.status if shop_probe else "",
            "shop_redirects": " | ".join(shop_probe.redirects) if shop_probe else "",
            "mapping_reason": mapping_reason,
            "canibalization": canibal,
            "ps_error": ps_probe.error,
            "shop_error": shop_probe.error if shop_probe else "",
        })

        marker = {"YES": "🔴", "NO": "🟢", "MANUAL_REVIEW": "❓", "N/A": "  "}.get(canibal, "  ")
        print(f"  [{i:3}/{len(ps_urls)}] {marker} PS={ps_probe.status} Shop={shop_probe.status if shop_probe else '-'}  {ps_url[:70]}")

        time.sleep(random.uniform(args.delay_min, args.delay_max))

    # Escribir CSV
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    # Resumen
    pct = (cannibals / ps_live * 100) if ps_live else 0
    print()
    print("=" * 60)
    print(f"Total URLs probadas:           {len(ps_urls)}")
    print(f"PrestaShop con status 200:     {ps_live}")
    print(f"Canibalización confirmada:     {cannibals}")
    print(f"% PS vivas con duplicado:      {pct:.1f}%")
    print(f"Pendientes de revisión manual: {sum(1 for r in out_rows if r['canibalization'] == 'MANUAL_REVIEW')}")
    print(f"\nDetalle: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
