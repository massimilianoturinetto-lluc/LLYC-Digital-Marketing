# 03 — Análisis de sitemaps y robots.txt

**Fecha:** 2026-05-25
**Datos crudos en:** `data/apex_sitemap_index.xml`, `data/apex_products_1.xml`, `data/apex_collections_1.xml`, `data/apex_robots.txt`, `data/prestashop_robots.txt`, `data/prestashop_sitemap_status.txt`

---

## 1. Estructura de sitemaps del apex (Shopify)

### Índice general (`/sitemap.xml`)

**46 sub-sitemaps** referenciados, agrupados así:

| Tipo | Cantidad |
|---|---:|
| `/sitemap/products/N.xml` | 32 |
| `/sitemap/collections/N.xml` | 12 (11 numerados + 1 `static.xml`) |
| `/sitemap/pages/N.xml` | 2 (1 numerado + 1 `static.xml`) |
| `/sitemap/blogs/*.xml` | **0** — no existe sitemap de blog en el apex |

**Patrón de URL atípico:** `/sitemap/products/1.xml` (con barras). Shopify nativo usa `/sitemap_products_1.xml?from=…&to=…` (con guiones bajos). Confirma que **hay una capa de reescritura / theme custom / arquitectura headless** delante del Shopify nativo — el equipo de desarrollo del cliente sabrá quién la opera.

### Estimación de volumen total

Una muestra real (sub-sitemap `products/1.xml`) contiene **250 URLs**. Si los 32 sub-sitemaps son del mismo orden, el total de productos en sitemap es **≈ 8.000**. (Shopify cappa cada sub-sitemap a 5.000 URLs; con 250 estamos lejos del techo, así que el dato real podría salir de 5.000 a 10.000 productos.) Para censo exacto hay que descargar los 32 ficheros.

`collections/1.xml` tiene solo **26 URLs**. Con 11 sub-sitemaps numerados, el total de colecciones es del orden de **300-500**, dependiendo de si los demás llenos.

---

## 2. Productos: análisis de `products/1.xml` (muestra 250 URLs)

### Distribución por marca (primer segmento del path)

| Marca | URLs | % muestra |
|---|---:|---:|
| apple | 143 | 57% |
| samsung | 82 | 33% |
| xiaomi | 15 | 6% |
| oppo | 4 | 2% |
| huawei | 3 | 1% |
| honor | 1 | <1% |
| lenovo | 1 | <1% |
| google | 1 | <1% |

→ El sub-sitemap está fuertemente sesgado a iPhone/Galaxy. Hay además **103 modelos únicos** de móvil/tablet en solo este sub-sitemap.

### Hallazgo crítico: explosión cartesiana de URLs

El mismo **diseño de funda** se publica como URL independiente para cada modelo de móvil compatible. Top patrones:

| Diseño | Nº de URLs (modelos distintos) en esta muestra |
|---|---:|
| `funda-brillantes-para-...` | 37 |
| `funda-ultra-suave-para-...` | 26 |
| `funda-ultra-suave-compatible-con-magsafe-para-...` | 21 |
| `funda-bumper-3-en-1-para-...` | 18 |
| `funda-ultra-suave-colgante-para-...` | 13 |
| `funda-bumper-compatible-con-magsafe-para-...` | 12 |
| `funda-bumper-con-vaso-de-purpurina-para-...` | 11 |
| `funda-business-compatible-con-magsafe-para-...` | 11 |
| `funda-bumper-reforzada-degradada-para-...` | 11 |
| `funda-bumper-reforzada-degradada-compatible-con-magsafe-para-...` | 10 |
| `funda-360-para-...` | 10 |
| `funda-multiperlitas-para-...` | 10 |

**18 diseños distintos generan ≥4 URLs cada uno → 227 de las 250 URLs muestreadas (91 %) son variantes "mismo diseño × modelo distinto".**

**Implicaciones:**

- Es la estructura típica del retailer de fundas: cada PDP es legítimamente única (la funda se ajusta a un modelo concreto). No es duplicado *del catálogo* en sentido estricto.
- Pero a nivel SEO, **canibalización interna casi garantizada**: la copy del producto, el title, la meta description y el schema serán muy similares entre, p. ej., `funda-brillantes-para-iphone-15-p/` y `funda-brillantes-para-iphone-16-p/`. Si no hay diferenciación on-page real ni canonicals bien planteados, Google selecciona una URL ganadora y descarta el resto.
- Hace **muy importante** revisar en la fase on-page (script `05_audit_onpage_shopify.py`) que cada PDP tenga title, description y JSON-LD diferenciados por modelo.

### Normalización

- **250/250 productos terminan en `/`** — coherente.
- **0 URLs con querystring, 0 con mayúsculas, 0 con paginación**, 0 con búsqueda interna en sitemap. Limpio.

---

## 3. Colecciones: análisis de `collections/1.xml` (26 URLs completas)

Listado completo y clasificación:

| URL | Tipo | Estado |
|---|---|---|
| `/frontpage/` | Shopify default | ⚠️ Legacy. Same content as home. Debería canonicalizar a `/`. |
| `/all/` | Shopify default | ⚠️ Legacy. Catálogo completo duplicado. Debería tener noindex o estar fuera del sitemap. |
| `/inkybay-all/` | App "Inky Bay" | ⚠️ Generado por una app de personalización. Probablemente debería estar noindex. |
| `/fundas/` | Categoría principal | Limpio |
| `/fundas/compatible-con-magsafe/` | Sub-categoría | Limpio |
| `/fundas/basicos/` | Sub-categoría | Limpio |
| `/fundas/transparentes/` | Sub-categoría | Limpio |
| `/fundas/maxima-proteccion/` | Sub-categoría | Limpio |
| `/fundas/brillo-y-color/` | Sub-categoría | Limpio |
| `/colecciones/antiyellow/` | Colección puntual | Limpio (aunque usa raíz `/colecciones/` distinta de `/fundas/`) |
| `/accesorios/` | Categoría principal | Limpio |
| `/accesorios/powerbank/` | Sub-categoría | Limpio |
| `/accesorios/auriculares/` | Sub-categoría | Limpio |
| `/cristal-templado/` | Categoría top-level | Limpio |
| `/apple/` | Categoría por marca | Limpio |
| `/samsung/` | Categoría por marca | Limpio |
| `/xiaomi/` | Categoría por marca | Limpio |
| `/google/` | Categoría por marca | Limpio |
| `/huawei/` | Categoría por marca | Limpio |
| `/oppo/` | Categoría por marca | Limpio |
| `/apple/accesorios-iphone/` | Marca + accesorios | Limpio |
| `/samsung/accesorios-samsung/` | Marca + accesorios | Limpio |
| `/xiaomi/accesorios-xiaomi/` | Marca + accesorios | Limpio |
| `/huawei/accesorios-huawei/` | Marca + accesorios | Limpio |
| `/oppo/accesorios-oppo/` | Marca + accesorios | Limpio |
| `/iphone-16-pro/` | **Modelo standalone** | ⚠️ Existe también `/apple/iphone-16-pro/...` (hay 7 productos bajo ese path en la muestra) → **duplicado estructural** |

### Hallazgos:

**a) Tres colecciones Shopify-legacy en el sitemap:** `/frontpage/`, `/all/`, `/inkybay-all/`. Son colecciones que Shopify crea por defecto (o las apps generan automáticamente) y no se han limpiado. `/frontpage/` sirve el mismo contenido que la home, `/all/` lista todos los productos del catálogo, `/inkybay-all/` viene de una app de personalización de fundas.

**b) Duplicado estructural de modelo:** existe `/iphone-16-pro/` (a nivel root) **y** `/apple/iphone-16-pro/` (con prefijo de marca). Si ambos URLs renderizan contenido similar, es **canibalización interna pura**. Pendiente comprobar con HTTP qué sirve cada una.

**c) Inconsistencia de jerarquía:** la mayoría de colecciones temáticas viven bajo `/fundas/<tema>/`, pero existe una bajo `/colecciones/antiyellow/`. Dos raíces distintas para el mismo concepto → ruido para el bot y posible reparto de equity.

---

## 4. robots.txt del apex (`lacasadelascarcasas.es/robots.txt`)

### Lo que está bien

- **Es robots.txt de Shopify, no de PrestaShop.** Confirma que el snippet de Google que vimos en el reconocimiento previo era engañoso (probable descripción auto-generada). Los bloqueos típicos PrestaShop (`my-account`, `guest-tracking`, controladores) **no están** en el archivo real.
- **Directiva `Sitemap:`** declarada correctamente: `https://lacasadelascarcasas.es/sitemap.xml`.
- **Bloqueo de parámetros de tracking**: cubre `utm_*`, `gclid`, `fbclid`, `mc_cid`, `mc_eid`, además de los paramétros Shopify (`session_id`, `cart_sig`, `preview_theme_id`, `preview_script_id`, `pbcid`) y los introducidos en un bloque "añadido solicitado" (`cursor`, `direction`, `filters`).
- **Política AI/GEO explícita y exhaustiva**: 16 bots de IA permitidos por nombre (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, applebot-extended, etc). Buen posicionamiento para descubrimiento en LLMs.
- **Static assets permitidos** (CSS, JS, fonts, imágenes, `/cdn/`, `/cdn-cgi/`) — necesario para que Google rendere el sitio correctamente.

### Problemas detectados

**a) User-agents duplicados con bloques en conflicto.** Cuatro casos:

| User-agent | Bloques | Conflicto |
|---|---:|---|
| `*` | 4 | reglas distintas dispersas en 4 secciones |
| `AhrefsBot` | 2 | uno con `Crawl-delay: 5`, otro con `Disallow: /` → al final aplica `Disallow: /`, pero la lectura es ambigua |
| `AhrefsSiteAudit` | 2 | mismo patrón que AhrefsBot |
| `Slurp` | 2 | uno con `Allow: /` + `Crawl-delay: 1`, otro con sola la declaración → bien interpretado, pero malformado |

Google une todos los bloques del mismo user-agent, así que **funcionalmente no hay daño grave**, pero es difícil mantenerlo: el siguiente que edite el archivo no sabrá cuál es la regla efectiva sin trazarlo a mano.

**b) Directivas WordPress en sitio Shopify** (reglas muertas, no tienen efecto pero sugieren copy-paste de plantilla):

- `Disallow: /comments/feed/`
- `Disallow: /*/trackback/`
- `Disallow: /feed/rss/`
- y derivados con `*/`

Ninguna de estas rutas existe en Shopify. Indica que el robots fue copiado de otro proyecto (WordPress / WooCommerce, posiblemente el sitio anterior pre-PrestaShop).

**c) Errores de formato:**

- `DisAllow:` con "A" mayúscula (línea: `DisAllow: /*?*pbcid=`). Google es case-insensitive en directivas, así que funciona, pero es señal de revisión apurada.
- `User-agent: WGet` con W mayúsculas (debería ser `Wget`). Google es case-insensitive en user-agent también, no afecta.

**d) Encoding mal servido.** El archivo contiene mojibake (`Ãšltima actualizaciÃ³n`, `BÃšSQUEDA`, `Pinterestbot`, etc.). El fichero está codificado en UTF-8 pero el server lo entrega con header sin charset o con charset Latin-1, y Google lo procesa con encoding incorrecto. Funcionalmente no rompe nada (los comentarios son ignorados por el parser), pero queda feo en cualquier auditoría manual.

**e) Bloqueo a Screaming Frog, Ahrefs, Semrush, DotBot…** decisión deliberada para preservar presupuesto de rastreo y dificultar análisis competencial, pero implica que **el cliente no puede contratar una auditoría externa con esas herramientas sin levantarles el bloqueo temporalmente**. A tener en cuenta para el audit completo.

---

## 5. robots.txt del subdominio PrestaShop (`prestashop.lacasadelascarcasas.es/robots.txt`)

Contenido literal:

```
User-agent: * Disallow:/
```

### Lectura correcta

La directiva bloquea **todo el rastreo** del subdominio para **todos los bots**. La intención es clara: el equipo quiere que Google deje de molestarse con el subdominio legacy.

### El problema: esto no desindexa

`Disallow:` **prohíbe que Google vuelva a crawlear** la URL. Pero **no la quita del índice si ya estaba indexada**. El efecto colateral es peor que dejarla abierta:

1. **Las URLs ya indexadas siguen apareciendo en resultados** — con snippet vacío o "no hay información disponible" (lo que afea la marca).
2. **Google no puede recrawlear** para descubrir un eventual `noindex` o un redirect 301 a la versión Shopify → el subdominio queda atrapado en el índice indefinidamente.
3. **La canibalización persiste**: para queries específicas, Google puede seguir prefiriendo la URL antigua del subdominio sobre la versión nueva en el apex.

### Lo correcto sería:

1. **Permitir el crawl** (`Allow: /` o no servir robots.txt).
2. **Servir un 301 a la URL equivalente del apex** desde el server de PrestaShop, o un `<meta name="robots" content="noindex">` en cada página.
3. **Esperar 4-12 semanas** a que Google reprocese y borre del índice.
4. **Acelerar con Search Console**: dar de alta la propiedad `prestashop.lacasadelascarcasas.es` y usar la herramienta de "Eliminaciones".

Sin esos pasos, el `Disallow: /` actual **no resuelve la canibalización** — solo congela el estado.

---

## 6. Sitemap del subdominio PrestaShop

**Estado verificado:** `https://prestashop.lacasadelascarcasas.es/sitemap.xml` → **404 Not Found** ("la página no se encuentra").

Lectura: el equipo no está re-publicando un sitemap del legacy. Es coherente con la intención de desindexar (no quieres ofrecer a Google un mapa de las URLs que quieres retirar). No hay nada que descargar para mapear el catálogo PrestaShop por esta vía.

**Implicación para el análisis de canibalización:** la lista de URLs PS indexadas hay que obtenerla de otra fuente — Google Search Console (propiedad del subdominio), una consulta `site:prestashop.lacasadelascarcasas.es` paginada manualmente, o un crawl externo con un servicio que tenga histórico (Ahrefs / Sistrix).

---

## 7. CSV generado

`03_sitemaps.csv` — **276 filas** (250 productos + 26 colecciones de la muestra apex disponible).

| Campo | Notas |
|---|---|
| `url` | URL completa |
| `env` | `shopify` (todas en esta pasada — no hay datos del entorno PrestaShop por el 404) |
| `type` | `product` o `collection` |
| `lastmod` | Fecha del sitemap (todas: `2026-05-25` para products, varias para collections) |
| `source_sitemap` | `apex_products_1.xml` o `apex_collections_1.xml` |
| `suspects` | flags pipe-separated (`shopify_legacy_collection` para `/frontpage/`, `/all/`, `/inkybay-all/`) |

---

## 8. Próximas iteraciones (si quieres seguir profundizando sin red)

Si me pasas también:

1. `sitemap/products/2.xml` (o cualquier otro número) → confirmamos si todos los sub-sitemaps siguen el mismo tamaño (~250 URLs cada uno) y refinamos el censo total.
2. `sitemap/pages/static.xml` y `sitemap/collections/static.xml` → vemos qué hay manualmente curado.
3. **HTML de** `https://lacasadelascarcasas.es/iphone-16-pro/` vs `https://lacasadelascarcasas.es/apple/iphone-16-pro/` → confirmamos si el duplicado estructural sirve contenido idéntico (esa sería la "prueba" de canibalización interna).
4. **HTML de** `https://lacasadelascarcasas.es/frontpage/` y `https://lacasadelascarcasas.es/all/` → verificamos si llevan `noindex` o si están realmente sirviendo contenido duplicado.
5. **Una PDP cualquiera** (p. ej. `funda-brillantes-para-iphone-16-p/`) → comprobamos canonical, title, meta description, JSON-LD Product, hreflang.
