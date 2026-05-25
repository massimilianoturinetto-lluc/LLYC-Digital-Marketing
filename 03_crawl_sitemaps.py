#!/usr/bin/env python3
"""
Crawler de sitemaps para auditoría SEO de lacasadelascarcasas.es.

Uso:
    python3 03_crawl_sitemaps.py

Salida:
    03_sitemaps.csv             — todas las URLs muestreadas (cap 500/entorno)
    03_sitemaps_analysis.md     — totales por entorno y tipo + URLs sospechosas

Dependencias: solo stdlib (urllib, xml.etree, gzip, csv). Python 3.9+.

Notas:
- Recorre sitemap indexes recursivamente (depth max 3).
- Soporta sitemap.xml y sitemap.xml.gz.
- Si un entorno supera 500 URLs, hace muestreo aleatorio estratificado por tipo.
- Clasifica URL por patrón heurístico (Shopify vs PrestaShop, ver TYPE_RULES).
"""

from __future__ import annotations

import csv
import gzip
import io
import random
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# ---------- configuración ----------

ENVS = {
    "shopify": [
        "https://lacasadelascarcasas.es/sitemap.xml",
        "https://www.lacasadelascarcasas.es/sitemap.xml",
    ],
    "prestashop": [
        "https://prestashop.lacasadelascarcasas.es/sitemap.xml",
        "https://prestashop.lacasadelascarcasas.es/1_index_sitemap.xml",
    ],
}

SAMPLE_CAP = 500
MAX_DEPTH = 3
TIMEOUT = 30
RANDOM_SEED = 42
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SM_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

OUT_CSV = Path("03_sitemaps.csv")
OUT_MD = Path("03_sitemaps_analysis.md")


# ---------- clasificación por patrón ----------

# (env, regex, type). Primera coincidencia gana. Orden importa.
TYPE_RULES: list[tuple[str, re.Pattern[str], str]] = [
    ("shopify",    re.compile(r"^https?://[^/]+/?$"),                                 "home"),
    ("shopify",    re.compile(r"/collections/[^/?#]+/products/"),                     "product"),
    ("shopify",    re.compile(r"/products/"),                                         "product"),
    ("shopify",    re.compile(r"/colecciones/"),                                      "collection"),
    ("shopify",    re.compile(r"/collections/"),                                      "collection"),
    ("shopify",    re.compile(r"/blogs?/"),                                           "blog"),
    ("shopify",    re.compile(r"/pages/"),                                            "page"),
    ("shopify",    re.compile(r"/(fundas|ofertas|colaboraciones|tiendas|nosotros|faqs|la-fabrica|nuestros-productos)(/|$)"),  "page"),
    ("prestashop", re.compile(r"^https?://[^/]+/?$"),                                 "home"),
    ("prestashop", re.compile(r"\.html(\?|$)"),                                       "product"),
    ("prestashop", re.compile(r"id_product=\d+"),                                     "product"),
    ("prestashop", re.compile(r"/(category|categoria)/", re.I),                       "collection"),
    ("prestashop", re.compile(r"/blog(/|$)"),                                         "blog"),
    ("prestashop", re.compile(r"/(content|cms|module)/"),                             "page"),
    ("prestashop", re.compile(r"id_category=\d+"),                                    "collection"),
    ("prestashop", re.compile(r"id_cms=\d+"),                                         "page"),
]


# ---------- detección de URLs sospechosas ----------

SUSPECT_RULES = {
    "with_query":           lambda u: "?" in u or "&" in u,
    "pagination":           lambda u: bool(re.search(r"[?&](p|page)=\d+|/page/\d+", u)),
    "internal_search":      lambda u: bool(re.search(r"[?&](q|s|search|search_query|controller=search)=", u)),
    "uppercase_in_path":    lambda u: bool(re.search(r"[A-Z]", urllib.parse.urlparse(u).path)),
    "session_id":           lambda u: bool(re.search(r"[?&](sid|phpsessid|sessionid)=", u, re.I)),
    "controller_param":     lambda u: "controller=" in u,
    "fragment":             lambda u: "#" in u,
}


# ---------- modelo de datos ----------

@dataclass
class SitemapURL:
    url: str
    env: str
    type_: str
    lastmod: str
    source_sitemap: str
    suspects: list[str]


# ---------- helpers ----------

def fetch(url: str) -> bytes:
    """GET con UA. Maneja gzip por extensión y por Content-Encoding."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
            raw = gzip.decompress(raw)
        return raw


def parse_sitemap(raw: bytes) -> tuple[list[tuple[str, str]], list[str]]:
    """
    Devuelve (urls_con_lastmod, child_sitemaps).
    urls_con_lastmod = [(loc, lastmod), ...]
    child_sitemaps = [loc, ...] (de sitemapindex)
    """
    tree = ET.fromstring(raw)
    tag = tree.tag.split("}", 1)[-1]

    urls: list[tuple[str, str]] = []
    children: list[str] = []

    if tag == "sitemapindex":
        for sm in tree.findall("sm:sitemap", SM_NS) or tree.findall("sitemap"):
            loc = sm.findtext("sm:loc", default="", namespaces=SM_NS) or sm.findtext("loc", default="")
            if loc.strip():
                children.append(loc.strip())
    elif tag == "urlset":
        for u in tree.findall("sm:url", SM_NS) or tree.findall("url"):
            loc = u.findtext("sm:loc", default="", namespaces=SM_NS) or u.findtext("loc", default="")
            lastmod = u.findtext("sm:lastmod", default="", namespaces=SM_NS) or u.findtext("lastmod", default="")
            if loc.strip():
                urls.append((loc.strip(), lastmod.strip()))
    return urls, children


def classify(url: str, env: str) -> str:
    for env_rule, rx, t in TYPE_RULES:
        if env_rule == env and rx.search(url):
            return t
    return "other"


def detect_suspects(url: str) -> list[str]:
    return [name for name, test in SUSPECT_RULES.items() if test(url)]


def crawl_env(env: str, seeds: list[str]) -> tuple[list[SitemapURL], list[str]]:
    """Recorre sitemaps de un entorno hasta agotar (o MAX_DEPTH). Devuelve URLs + log."""
    log: list[str] = []
    seen_sitemaps: set[str] = set()
    queue: list[tuple[str, int]] = [(s, 0) for s in seeds]
    all_urls: list[SitemapURL] = []

    while queue:
        sm_url, depth = queue.pop(0)
        if sm_url in seen_sitemaps or depth > MAX_DEPTH:
            continue
        seen_sitemaps.add(sm_url)
        try:
            raw = fetch(sm_url)
        except urllib.error.HTTPError as e:
            log.append(f"[{env}] HTTP {e.code} en {sm_url}")
            continue
        except Exception as e:
            log.append(f"[{env}] FAIL {type(e).__name__} en {sm_url}: {e}")
            continue

        try:
            urls, children = parse_sitemap(raw)
        except ET.ParseError as e:
            log.append(f"[{env}] XML parse error en {sm_url}: {e}")
            continue

        log.append(f"[{env}] OK {sm_url} → {len(urls)} URLs, {len(children)} sub-sitemaps")

        for loc, lastmod in urls:
            t = classify(loc, env)
            all_urls.append(SitemapURL(
                url=loc, env=env, type_=t, lastmod=lastmod,
                source_sitemap=sm_url, suspects=detect_suspects(loc),
            ))
        for c in children:
            queue.append((c, depth + 1))

    return all_urls, log


def stratified_sample(urls: list[SitemapURL], cap: int) -> tuple[list[SitemapURL], bool]:
    """Si len(urls) > cap, muestrea de forma estratificada por tipo manteniendo proporciones."""
    if len(urls) <= cap:
        return urls, False
    rng = random.Random(RANDOM_SEED)
    by_type: dict[str, list[SitemapURL]] = defaultdict(list)
    for u in urls:
        by_type[u.type_].append(u)
    total = len(urls)
    sampled: list[SitemapURL] = []
    # cuotas proporcionales, garantizando al menos 1 por tipo no vacío
    for t, group in by_type.items():
        quota = max(1, round(len(group) * cap / total))
        sampled.extend(rng.sample(group, min(quota, len(group))))
    # ajustar a cap exacto
    if len(sampled) > cap:
        sampled = rng.sample(sampled, cap)
    elif len(sampled) < cap:
        remaining = [u for u in urls if u not in sampled]
        extra = rng.sample(remaining, min(cap - len(sampled), len(remaining)))
        sampled.extend(extra)
    return sampled, True


def trailing_slash_duplicates(urls: list[str]) -> list[tuple[str, str]]:
    """Detecta pares (con-slash, sin-slash) que coexisten en el sitemap."""
    seen = set(urls)
    dups = []
    for u in urls:
        if u.endswith("/"):
            counterpart = u.rstrip("/")
        else:
            counterpart = u + "/"
        if counterpart in seen and (u, counterpart) not in dups and (counterpart, u) not in dups:
            dups.append((u, counterpart))
    return dups


# ---------- main ----------

def main() -> int:
    print("Crawl de sitemaps — lacasadelascarcasas.es")
    print(f"User-Agent: {UA[:60]}...")
    print()

    all_records: list[SitemapURL] = []
    all_log: list[str] = []
    env_stats: dict[str, dict] = {}

    for env, seeds in ENVS.items():
        print(f"=== {env} ===")
        urls, log = crawl_env(env, seeds)
        for line in log:
            print(" ", line)
        print(f"  total descubiertas: {len(urls)}")

        sampled, was_sampled = stratified_sample(urls, SAMPLE_CAP)
        if was_sampled:
            print(f"  muestreo estratificado aplicado: {len(sampled)}/{len(urls)}")

        env_stats[env] = {
            "discovered": len(urls),
            "sampled": len(sampled),
            "was_sampled": was_sampled,
            "by_type": Counter(u.type_ for u in urls),
            "by_type_sampled": Counter(u.type_ for u in sampled),
            "suspects": Counter(s for u in urls for s in u.suspects),
            "trailing_slash_dupes": trailing_slash_duplicates([u.url for u in urls]),
        }
        all_records.extend(sampled)
        all_log.extend(log)
        print()

    # CSV
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "env", "type", "lastmod", "source_sitemap", "suspects"])
        for r in all_records:
            w.writerow([r.url, r.env, r.type_, r.lastmod, r.source_sitemap, "|".join(r.suspects)])
    print(f"CSV escrito: {OUT_CSV} ({len(all_records)} filas)")

    # MD
    write_analysis_md(env_stats, all_log)
    print(f"Análisis escrito: {OUT_MD}")
    return 0


def write_analysis_md(env_stats: dict, log: list[str]) -> None:
    lines: list[str] = []
    lines.append("# 03 — Análisis de sitemaps\n")
    lines.append(f"**Fecha de crawl:** {datetime.utcnow().isoformat()}Z  ")
    lines.append(f"**Cap por entorno:** {SAMPLE_CAP} URLs (muestreo aleatorio estratificado por tipo si supera).\n")

    lines.append("## Totales por entorno\n")
    lines.append("| Entorno | URLs descubiertas | URLs muestreadas | ¿Se aplicó muestreo? |")
    lines.append("|---|---:|---:|:---:|")
    for env, s in env_stats.items():
        lines.append(f"| {env} | {s['discovered']} | {s['sampled']} | {'sí' if s['was_sampled'] else 'no'} |")
    lines.append("")

    lines.append("## Distribución por tipo (sobre el total descubierto)\n")
    types_seen = sorted({t for s in env_stats.values() for t in s["by_type"]})
    header = "| Tipo | " + " | ".join(env_stats.keys()) + " |"
    sep = "|---|" + "|".join(["---:"] * len(env_stats)) + "|"
    lines.append(header)
    lines.append(sep)
    for t in types_seen:
        row = f"| {t} | " + " | ".join(str(env_stats[e]["by_type"].get(t, 0)) for e in env_stats) + " |"
        lines.append(row)
    lines.append("")

    lines.append("## URLs sospechosas (sobre el total descubierto)\n")
    suspect_names = sorted({n for s in env_stats.values() for n in s["suspects"]})
    if not suspect_names:
        lines.append("_Ninguna URL sospechosa detectada._\n")
    else:
        lines.append("| Patrón | " + " | ".join(env_stats.keys()) + " |")
        lines.append("|---|" + "|".join(["---:"] * len(env_stats)) + "|")
        for name in suspect_names:
            row = f"| {name} | " + " | ".join(str(env_stats[e]["suspects"].get(name, 0)) for e in env_stats) + " |"
            lines.append(row)
        lines.append("")
        lines.append("Explicación de patrones:")
        lines.append("- `with_query`: URL con parámetros — los sitemaps deberían contener URLs canónicas sin querystring.")
        lines.append("- `pagination`: facetas/paginación de listados — no deberían estar en sitemap.")
        lines.append("- `internal_search`: resultados de búsqueda interna — thin content, no deberían estar.")
        lines.append("- `uppercase_in_path`: mayúsculas en el path — riesgo de duplicado por case-sensitivity.")
        lines.append("- `session_id`: parámetros de sesión expuestos — síntoma grave.")
        lines.append("- `controller_param`: controladores PrestaShop expuestos.")
        lines.append("- `fragment`: anclas `#` — no deberían estar en sitemap.\n")

    lines.append("## Duplicados con/sin trailing slash\n")
    for env, s in env_stats.items():
        dupes = s["trailing_slash_dupes"]
        lines.append(f"### {env}\n")
        if not dupes:
            lines.append("_Sin duplicados detectados._\n")
        else:
            lines.append(f"**{len(dupes)} pares duplicados detectados.** Primeros 20:\n")
            lines.append("| Variante A | Variante B |")
            lines.append("|---|---|")
            for a, b in dupes[:20]:
                lines.append(f"| `{a}` | `{b}` |")
            lines.append("")

    lines.append("## Log de descarga\n")
    lines.append("```")
    lines.extend(log)
    lines.append("```")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
