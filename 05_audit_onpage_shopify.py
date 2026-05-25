#!/usr/bin/env python3
"""
Auditoría on-page del Shopify actual (apex).

Muestra fija de 7 URLs: home + 3 collections + 3 products.
Extrae title, meta description, canonical, hreflang, JSON-LD, Open Graph,
robots meta. Detecta UTMs en links internos, completitud de schema Product,
presencia de LocalBusiness.

Uso:
    pip install beautifulsoup4   # única dependencia externa
    python3 05_audit_onpage_shopify.py

Override de URLs (opcional):
    python3 05_audit_onpage_shopify.py \\
        --home https://lacasadelascarcasas.es/ \\
        --collection https://lacasadelascarcasas.es/colecciones/xxx \\
        --product https://lacasadelascarcasas.es/producto-y

Sin argumentos, intenta autodescubrir 3 collections y 3 products del sitemap.

Salida:
    05_onpage_shopify.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Falta beautifulsoup4. Instala con: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT = 20
APEX = "https://lacasadelascarcasas.es"
OUT_MD = Path("05_onpage_shopify.md")


@dataclass
class PageAudit:
    url: str
    label: str
    status: int | str = 0
    title: str = ""
    meta_description: str = ""
    canonical: str = ""
    canonical_self: bool | None = None
    hreflang: list[tuple[str, str]] = field(default_factory=list)
    robots_meta: str = ""
    og: dict[str, str] = field(default_factory=dict)
    jsonld_types: list[str] = field(default_factory=list)
    jsonld_blocks: list[dict] = field(default_factory=list)
    internal_links_with_utm: list[str] = field(default_factory=list)
    product_schema_complete: bool | None = None
    product_schema_missing: list[str] = field(default_factory=list)
    has_localbusiness: bool = False
    error: str = ""


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-ES,es"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
    except Exception as e:
        return 0, f"__ERROR__:{type(e).__name__}:{e}"


def audit_page(url: str, label: str) -> PageAudit:
    a = PageAudit(url=url, label=label)
    status, html = fetch(url)
    a.status = status
    if html.startswith("__ERROR__:"):
        a.error = html
        return a

    soup = BeautifulSoup(html, "html.parser")

    # <title>
    t = soup.find("title")
    a.title = (t.get_text(strip=True) if t else "")

    # meta description
    md = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    a.meta_description = (md.get("content", "") if md else "")

    # canonical
    can = soup.find("link", attrs={"rel": lambda v: v and "canonical" in (v if isinstance(v, list) else [v])})
    if can and can.get("href"):
        a.canonical = can["href"]
        a.canonical_self = urllib.parse.urldefrag(a.canonical)[0].rstrip("/") == urllib.parse.urldefrag(url)[0].rstrip("/")

    # hreflang
    for link in soup.find_all("link", rel="alternate"):
        if link.get("hreflang"):
            a.hreflang.append((link["hreflang"], link.get("href", "")))

    # robots meta
    rb = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    a.robots_meta = (rb.get("content", "") if rb else "")

    # Open Graph
    for og in soup.find_all("meta", attrs={"property": re.compile(r"^og:", re.I)}):
        a.og[og["property"].lower()] = og.get("content", "")

    # JSON-LD
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "{}")
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            graph = item.get("@graph") if isinstance(item, dict) else None
            for node in (graph if isinstance(graph, list) else [item]):
                if not isinstance(node, dict):
                    continue
                t = node.get("@type")
                if isinstance(t, list):
                    a.jsonld_types.extend(t)
                elif t:
                    a.jsonld_types.append(t)
                a.jsonld_blocks.append(node)
                if t == "LocalBusiness" or (isinstance(t, list) and "LocalBusiness" in t):
                    a.has_localbusiness = True

    # Completitud Product (si label == 'product')
    if label == "product":
        prod = next((b for b in a.jsonld_blocks if (b.get("@type") == "Product" or (isinstance(b.get("@type"), list) and "Product" in b["@type"]))), None)
        if prod:
            required = {
                "name": prod.get("name"),
                "image": prod.get("image"),
                "brand": prod.get("brand"),
                "offers.price": _deep(prod, "offers", "price"),
                "offers.priceCurrency": _deep(prod, "offers", "priceCurrency"),
                "offers.availability": _deep(prod, "offers", "availability"),
                "aggregateRating": prod.get("aggregateRating"),
                "sku": prod.get("sku"),
            }
            a.product_schema_missing = [k for k, v in required.items() if not v]
            a.product_schema_complete = len(a.product_schema_missing) == 0
        else:
            a.product_schema_complete = False
            a.product_schema_missing = ["__no_product_jsonld__"]

    # UTMs en links internos
    host = urllib.parse.urlparse(url).netloc
    for link in soup.find_all("a", href=True):
        href = link["href"]
        absu = urllib.parse.urljoin(url, href)
        if urllib.parse.urlparse(absu).netloc != host:
            continue
        if re.search(r"[?&](utm_|fbclid|gclid|mc_cid|mc_eid)", absu):
            a.internal_links_with_utm.append(absu)
    a.internal_links_with_utm = list(dict.fromkeys(a.internal_links_with_utm))[:20]

    return a


def _deep(d: dict, *path):
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def discover_sample(home_html: str, base: str) -> tuple[list[str], list[str]]:
    """Heurística: extrae 3 collections y 3 products del HTML del home."""
    soup = BeautifulSoup(home_html, "html.parser")
    collections, products = [], []
    host = urllib.parse.urlparse(base).netloc
    for link in soup.find_all("a", href=True):
        absu = urllib.parse.urljoin(base, link["href"])
        if urllib.parse.urlparse(absu).netloc != host:
            continue
        path = urllib.parse.urlparse(absu).path
        if re.search(r"/(colecciones|collections|fundas)/[^/]+/?$", path) and absu not in collections:
            collections.append(absu)
        # heurística producto: path con varios segmentos y no parece sección institucional
        if (re.search(r"/products/[^/]+", path) or path.count("/") >= 1) \
           and not re.search(r"/(tiendas|nosotros|faqs|la-fabrica|colaboraciones|ofertas|colecciones|collections|fundas|blog|blogs)", path) \
           and path not in ("", "/") and absu not in products:
            products.append(absu)
        if len(collections) >= 3 and len(products) >= 3:
            break
    return collections[:3], products[:3]


def render_md(audits: list[PageAudit]) -> str:
    lines: list[str] = []
    lines.append("# 05 — Auditoría on-page del Shopify (apex)\n")
    lines.append(f"**Muestra:** {len(audits)} URLs (home + 3 collections + 3 products)\n")

    # Tabla resumen
    lines.append("## Resumen\n")
    lines.append("| # | URL | Status | Canonical self | Hreflang | JSON-LD types | Robots |")
    lines.append("|---|---|---|:---:|:---:|---|---|")
    for i, a in enumerate(audits, 1):
        canonical_self = "—" if a.canonical_self is None else ("sí" if a.canonical_self else "**NO**")
        types = ", ".join(sorted(set(a.jsonld_types))) or "—"
        hl = str(len(a.hreflang)) if a.hreflang else "0"
        lines.append(f"| {i} | `{a.url}` | {a.status} | {canonical_self} | {hl} | {types} | {a.robots_meta or '—'} |")
    lines.append("")

    # Detalle por URL
    for i, a in enumerate(audits, 1):
        lines.append(f"## {i}. [{a.label}] {a.url}\n")
        if a.error:
            lines.append(f"**ERROR:** `{a.error}`\n")
            continue
        lines.append(f"- **Status:** {a.status}")
        lines.append(f"- **Title:** {a.title!r} ({len(a.title)} caracteres)")
        lines.append(f"- **Meta description:** {a.meta_description!r} ({len(a.meta_description)} caracteres)")
        lines.append(f"- **Canonical:** `{a.canonical or '(ausente)'}`  → self: **{a.canonical_self}**")
        lines.append(f"- **Robots meta:** `{a.robots_meta or '(ausente — implícita index,follow)'}`")
        if a.hreflang:
            lines.append("- **Hreflang:**")
            for code, href in a.hreflang:
                lines.append(f"  - `{code}` → {href}")
        else:
            lines.append("- **Hreflang:** ninguno")
        lines.append(f"- **JSON-LD types:** {sorted(set(a.jsonld_types)) or 'ninguno'}")
        if a.has_localbusiness:
            lines.append("- **LocalBusiness schema:** sí")
        else:
            lines.append("- **LocalBusiness schema:** no")
        if a.label == "product":
            lines.append(f"- **Product schema completo:** {a.product_schema_complete}")
            if a.product_schema_missing:
                lines.append(f"  - Campos faltantes: `{a.product_schema_missing}`")
        if a.og:
            lines.append("- **Open Graph:**")
            for k, v in a.og.items():
                lines.append(f"  - `{k}` = {v!r}")
        if a.internal_links_with_utm:
            lines.append(f"- **Links internos con UTM/tracking ({len(a.internal_links_with_utm)}):**")
            for link in a.internal_links_with_utm:
                lines.append(f"  - `{link}`")
        else:
            lines.append("- **Links internos con UTM/tracking:** ninguno detectado")
        lines.append("")

    # Hallazgos transversales
    lines.append("## Hallazgos transversales\n")
    any_localbiz = any(a.has_localbusiness for a in audits)
    lines.append(f"- **LocalBusiness schema en alguna URL:** {'sí' if any_localbiz else '**no** — relevante con +1000 tiendas físicas'}")
    products = [a for a in audits if a.label == "product"]
    if products:
        complete = sum(1 for p in products if p.product_schema_complete)
        lines.append(f"- **Productos con schema completo:** {complete}/{len(products)}")
        common_missing = set()
        for p in products:
            common_missing.update(p.product_schema_missing or [])
        if common_missing:
            lines.append(f"  - Campos faltantes (unión): `{sorted(common_missing)}`")
    canon_mismatches = [a for a in audits if a.canonical and a.canonical_self is False]
    if canon_mismatches:
        lines.append(f"- **Canonicals que apuntan fuera:** {len(canon_mismatches)}")
        for a in canon_mismatches:
            lines.append(f"  - `{a.url}` → `{a.canonical}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=f"{APEX}/")
    ap.add_argument("--collection", action="append", default=[])
    ap.add_argument("--product", action="append", default=[])
    args = ap.parse_args()

    # Si no se pasan suficientes, autodescubrir
    if len(args.collection) < 3 or len(args.product) < 3:
        print("Autodescubriendo URLs desde el home…")
        _, home_html = fetch(args.home)
        if home_html.startswith("__ERROR__"):
            print(f"No se pudo obtener home: {home_html}", file=sys.stderr)
            return 1
        coll, prod = discover_sample(home_html, args.home)
        args.collection = (args.collection + coll)[:3]
        args.product = (args.product + prod)[:3]
        print(f"  collections: {args.collection}")
        print(f"  products:    {args.product}")
        if len(args.collection) < 3 or len(args.product) < 3:
            print("ADVERTENCIA: no se encontraron suficientes URLs automáticamente. Usa --collection y --product.", file=sys.stderr)

    targets: list[tuple[str, str]] = [(args.home, "home")]
    targets += [(u, "collection") for u in args.collection[:3]]
    targets += [(u, "product") for u in args.product[:3]]

    audits: list[PageAudit] = []
    for url, label in targets:
        print(f"  → {label}: {url}")
        audits.append(audit_page(url, label))
        time.sleep(1.0)

    OUT_MD.write_text(render_md(audits), encoding="utf-8")
    print(f"\nReporte: {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
