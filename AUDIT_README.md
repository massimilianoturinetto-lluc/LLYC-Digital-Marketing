# Auditoría SEO — lacasadelascarcasas.es

Herramientas para auditar la convivencia Shopify (apex) ↔ PrestaShop (subdominio `prestashop.lacasadelascarcasas.es`).

## ⚠️ Restricción del entorno actual

Este repo está corriendo en un sandbox cloud de Claude Code donde **todo el HTTP/HTTPS saliente a `lacasadelascarcasas.es` está bloqueado** (proxy devuelve `403 x-deny-reason: host_not_allowed`). Por eso los scripts 03-05 están **listos para ejecutar localmente**, pero los CSVs/MDs de salida no se generan desde aquí.

Lo que sí se hizo desde el sandbox (ver `01_reconocimiento.md`):
- DNS de apex + subdominios → confirma Shopify en apex, GCP en `prestashop.*`, 5 subdominios extra (incluyendo dos anómalos: `board258.*` y `prekiosco.*`).
- Indexación en Google vía `WebSearch` → confirma la home de `prestashop.*` indexada y el patrón de URLs del apex.

## Ejecución local

```bash
# Requisitos: Python 3.9+
pip install beautifulsoup4   # solo para 05; 03 y 04 usan stdlib

# 1. Crawl de sitemaps (apex + prestashop)
python3 03_crawl_sitemaps.py
# → 03_sitemaps.csv, 03_sitemaps_analysis.md

# 2. Detección de canibalización (lee el CSV anterior)
python3 04_check_canibalizacion.py
# → 04_canibalizacion.csv + resumen en stdout

# 3. Auditoría on-page de la muestra Shopify
python3 05_audit_onpage_shopify.py
# → 05_onpage_shopify.md

# 4. Cadenas de redirección PrestaShop (30 URLs, lee el CSV de 03)
python3 06_redirect_chains.py
# → 06_redirecciones.csv
```

## Mapa de archivos

| Archivo | Tipo | Estado |
|---|---|---|
| `01_reconocimiento.md` | datos reales recogidos en sandbox (DNS + Google) | ✅ completo |
| `02_consultas_indexacion.md` | hoja de cálculo de SERPs `site:` para rellenar manualmente | ✅ completo, pendiente que el operador rellene |
| `03_crawl_sitemaps.py` | crawler de sitemaps (recursivo, cap 500, muestreo estratificado) | ✅ listo, ejecutar local |
| `04_check_canibalizacion.py` | probador HEAD apex vs PrestaShop (cap 200, delay 1-2s) | ✅ listo, ejecutar local |
| `05_audit_onpage_shopify.py` | extracción on-page con BeautifulSoup (7 URLs) | ✅ listo, ejecutar local |
| `06_redirect_chains.py` | seguimiento de cadenas de redirección PrestaShop (30 URLs, detecta 302/loops/meta-refresh/JS) | ✅ listo, ejecutar local |
| `03_sitemaps.csv` / `03_sitemaps_analysis.md` | output de 03 | ⏳ se genera al ejecutar |
| `04_canibalizacion.csv` | output de 04 | ⏳ se genera al ejecutar |
| `05_onpage_shopify.md` | output de 05 | ⏳ se genera al ejecutar |
| `06_redirecciones.csv` | output de 06 | ⏳ se genera al ejecutar |

## Parámetros configurables

- `03_crawl_sitemaps.py`: edita constantes al principio (`SAMPLE_CAP`, `ENVS`, `TYPE_RULES`).
- `04_check_canibalizacion.py`: `--limit N`, `--delay-min`, `--delay-max`.
- `05_audit_onpage_shopify.py`: `--home`, `--collection URL` (×3), `--product URL` (×3). Sin argumentos hace autodescubrimiento desde el home.
- `06_redirect_chains.py`: `--sample N` (default 30), `--input PATH` (default `03_sitemaps.csv`), `--delay-min/--delay-max`.

## Si quieres que yo procese los resultados

Una vez generes los CSVs/MDs en tu máquina, pégalos aquí (o súbelos al repo) y los interpretamos juntos en `06_hallazgos.md`.
