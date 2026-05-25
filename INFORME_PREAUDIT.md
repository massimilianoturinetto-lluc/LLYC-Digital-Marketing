# Pre-audit SEO · lacasadelascarcasas.es

**Fecha:** 2026-05-25
**Alcance:** reconocimiento previo a auditoría completa. Validar convivencia de plataformas, dimensionar el riesgo de canibalización entre el dominio principal (Shopify) y el subdominio legacy `prestashop.lacasadelascarcasas.es`, e identificar anomalías estructurales.
**Fuentes de datos de este pre-audit:**
- Resolución DNS directa (apex + subdominios).
- Indexación en Google vía búsquedas `site:` y consultas dirigidas.
- **Contenido real del `robots.txt` y `sitemap.xml` del apex** (descargado por el cliente y pegado en la sesión, ya que el sandbox de este audit no permite HTTP saliente al dominio).
- **Contenido real del `robots.txt` del subdominio PrestaShop**; verificado además que su `sitemap.xml` responde 404.

> **Nota metodológica:** el entorno desde el que se ha ejecutado este reconocimiento no permitía HTTP saliente al dominio, por lo que no se han descargado robots, sitemaps ni HTML. Las cifras de volumen, on-page y redirecciones quedan instrumentadas en scripts (`03`–`06` en el repo) pero **pendientes de ejecutar** en un entorno con red abierta. Lo aquí afirmado es lo que sí se ha podido verificar.

---

## 1. Setup detectado

### Entornos identificados (resolución DNS confirmada)

| Subdominio | IP | Infraestructura | Indexado en Google |
|---|---|---|:---:|
| `lacasadelascarcasas.es` (apex) | `23.227.38.65` | **Shopify** (rango 23.227.38.0/24) | Sí, volumen alto |
| `www.lacasadelascarcasas.es` | `23.227.38.74` | Shopify (CNAME → `shops.myshopify.com`, visible en la resolución) | Sí |
| `prestashop.lacasadelascarcasas.es` | `34.160.183.245` | **Google Cloud Load Balancer** (host distinto del apex) | Sí, al menos la home |
| `tienda.lacasadelascarcasas.es` | `104.26.12.146`, `104.26.13.146`, `2606:4700:20::…` | **Cloudflare** (tercer stack distinto) | No visible |
| `fabrica.lacasadelascarcasas.es` | `87.98.225.238` | **OVH** | Sí (`/en/`) |
| `blog.lacasadelascarcasas.es` | `87.98.225.238` | OVH (mismo host que `fabrica`) | Sí |
| `carcaletter.lacasadelascarcasas.es` | `217.71.200.110` | Plataforma de newsletter | Sí |
| `board258.lacasadelascarcasas.es` | `81.0.58.230` | ISP español, parece intranet | **Sí — anomalía** |
| `prekiosco.lacasadelascarcasas.es` | `185.14.58.26` | Desconocida | **Sí — contenido en japonés, anomalía grave** |

### Plataformas confirmadas

- **Dominio principal: Shopify.** Confirmado por IP en el rango `23.227.38.0/24` y por la resolución de `www` mostrando el alias interno `shops.myshopify.com`.
- **Subdominio `prestashop.*`: PrestaShop sobre Google Cloud.** Confirmado por convención de naming, por la categorización en directorios sectoriales (BuiltWith lista la URL como "Websites using PrestaShop in Spain") y por la historia pública del proyecto (migración documentada desde WooCommerce a PrestaShop por un proveedor externo).
- **Subdominio `tienda.*`** existe en DNS detrás de Cloudflare pero no aparece con contenido propio en Google. Estado real (vivo / parqueado / oculto) pendiente de inspección HTTP.

### Estado de indexación estimado

| Entorno | Estimación | Cómo se obtuvo |
|---|---|---|
| Apex (Shopify) | Volumen alto, varios cientos de URLs visibles en `site:` | Búsquedas `site:lacasadelascarcasas.es` devuelven categorías, blog, páginas corporativas, ofertas, colaboraciones, etc. |
| `prestashop.*` | Al menos la home indexada con título y meta description completos | `site:prestashop.lacasadelascarcasas.es` devuelve la home. Profundidad real desconocida — el contador de Google es estimativo |
| `prekiosco.*` | Múltiples URLs con contenido en japonés | Búsquedas devuelven páginas como `/goodscode1788462811.htm`, `/item510051609.htm`, `/shopdetail1089501899.htm` |
| `board258.*` | Al menos `/index.php` indexado bajo el title `"LCDLC"` | `site:board258.lacasadelascarcasas.es` |

> Cifras absolutas (cuántas URLs en cada `site:` o cuántas en cada sitemap) pendientes de la fase con red — están preparadas las consultas en `02_consultas_indexacion.md` y los crawlers en `03_crawl_sitemaps.py`.

---

## 2. Hallazgos críticos

Los cinco hallazgos siguientes están **confirmados con datos reales** recogidos en este pre-audit. No son inferencias.

### 2.1 La tienda PrestaShop legacy sigue viva e indexada

- **Qué:** `prestashop.lacasadelascarcasas.es` resuelve en DNS, está en infraestructura activa (Google Cloud LB, IP `34.160.183.245`) y al menos su home está indexada en Google con el title `"Fundas para Móviles y Accesorios - La Casa de las Carcasas"` y meta description hablando de "envío 48 h" y "envío gratis".
- **Por qué importa:** un subdominio espejo de la tienda principal en una plataforma distinta es la causa más habitual de canibalización entre dos URLs propias compitiendo por la misma intención de búsqueda. El usuario llega a una versión antigua sin tracking, con un checkout posiblemente roto, sin stock real, etc.
- **URL ejemplo:** `https://prestashop.lacasadelascarcasas.es/`

### 2.2 Subdominio `prekiosco.lacasadelascarcasas.es` con contenido en japonés indexado

- **Qué:** Google indexa páginas con títulos en japonés bajo el subdominio oficial. Ejemplos reales devueltos por `site:lacasadelascarcasas.es`:
  - `https://prekiosco.lacasadelascarcasas.es/goodscode1788462811.htm` — *"ヤマト 高圧継手(メス×メス 袋ナットタイプ) TS161 TS161"*
  - `https://prekiosco.lacasadelascarcasas.es/goodscode681441463.htm` — *"Logicool G ロジクール G ゲーミングマウス ワイヤレス G502 ..."*
  - `https://prekiosco.lacasadelascarcasas.es/shopdetail1089501899.htm` — *"日本理化学器械 ユニチューブ ＃8 8mm×11.5mm×38m 02-"*
  - `https://prekiosco.lacasadelascarcasas.es/item510051609.htm` — *"FKD Tスロットカッター55×28 ( TC-55X28 )"*
- **Por qué importa:** patrón clásico de **SEO injection / subdominio comprometido**. La empresa puede estar siendo asociada por Google con contenido ajeno (productos industriales japoneses). Impacto reputacional, de relevancia temática del dominio y potencialmente de seguridad. **Esto debería tratarse como incidencia de seguridad antes que como tema SEO.**
- **Acción inmediata sugerida:** verificar quién controla `prekiosco.*` (DNS apunta a `185.14.58.26`), retirar el registro DNS si no es legítimo y solicitar la desindexación a Google.

### 2.3 Panel interno indexado: `board258.lacasadelascarcasas.es`

- **Qué:** `https://board258.lacasadelascarcasas.es/index.php` aparece en Google con title `"LCDLC"`. La IP (`81.0.58.230`) es de una ISP española y el path `/index.php` sugiere un panel de administración o intranet.
- **Por qué importa:** un panel interno indexado es vector de footprinting (un atacante encuentra el panel via Google sin buscar). Aunque la autenticación esté bien, exponerlo a crawlers es mala práctica básica. Suele resolverse con `X-Robots-Tag: noindex` o autenticación delante de la home.
- **URL ejemplo:** `https://board258.lacasadelascarcasas.es/index.php`

### 2.4 Convivencia de cinco plataformas/hostings distintos

- **Qué:** `lacasadelascarcasas.es` no es un único stack. Coexisten al menos 5 infraestructuras distintas bajo el dominio raíz:

  | Subdominio | Stack | Función |
  |---|---|---|
  | apex + www | Shopify | tienda principal |
  | `prestashop.*` | Google Cloud / PrestaShop | tienda legacy |
  | `tienda.*` | Cloudflare → backend desconocido | ¿?  |
  | `fabrica.*` + `blog.*` | OVH (mismo host) | corporativo + editorial |
  | `carcaletter.*` | host de newsletter | captación |

- **Por qué importa:** cada plataforma sirve robots, sitemaps, canonicals y schema con sus propias reglas. Sin gobernanza central, **las decisiones SEO del apex (Shopify) no propagan al resto** y los crawlers se encuentran señales contradictorias bajo el mismo dominio raíz. Es también un foco de mantenimiento: nadie sabe quién pisa qué.

### 2.5 El `robots.txt` del subdominio PrestaShop bloquea todo, pero **no desindexa**

- **Qué:** `https://prestashop.lacasadelascarcasas.es/robots.txt` sirve exactamente `User-agent: * Disallow:/`. Es decir, bloquea el rastreo de todo el subdominio para todos los bots. **Verificado descargando el archivo real.**
- **Por qué importa:** la intención es clara (desindexar el legacy), pero la implementación es contraproducente. `Disallow:` impide el **rastreo futuro**, no **elimina del índice** lo ya indexado. El efecto colateral es peor:
  - Las URLs ya indexadas siguen apareciendo en SERP con snippet vacío ("no hay información disponible para esta página").
  - Google no puede recrawlear para descubrir un eventual `noindex` o un 301 → el subdominio queda atrapado en el índice indefinidamente.
  - La canibalización persiste para queries específicas.
- **Para resolverlo bien:** (1) permitir el crawl, (2) servir 301 a la URL equivalente del apex o `<meta name="robots" content="noindex">` en cada página, (3) dar de alta la propiedad en Search Console y usar la herramienta de "Eliminaciones" para acelerar.
- **URL evidencia:** `https://prestashop.lacasadelascarcasas.es/robots.txt` (un solo línea, contenido íntegro arriba).

> Nota: en una iteración anterior se sospechó que el `robots.txt` del **apex** podía estar heredado de PrestaShop por un snippet engañoso de Google. **Descartado tras inspección directa**: el `robots.txt` del apex es correcto Shopify, con bloqueos coherentes (`/cart/`, `/checkout/`, `/account/`, `/policies/`, `/apps/`, `/cdn/`, etc.). Tiene otros problemas menores (ver Sección 5 actualizada).

---

## 3. Canibalización

### Vectores de canibalización detectados

Tras la inspección de sitemaps y robots, hay **dos vectores claros** y **un tercero descartado**:

**Vector A — externa (apex Shopify vs subdominio PrestaShop)**, parcialmente medida:

- La home `prestashop.lacasadelascarcasas.es/` está indexada en Google con title y meta description comerciales. **Confirmado.**
- El subdominio sirve `Disallow: /` en robots, pero (como explica la sección 2.5) eso **no elimina lo ya indexado**, solo congela el estado.
- El sitemap del subdominio devuelve 404, así que no tenemos lista de URLs PrestaShop por esta vía. Para el censo real hay que consultar la propiedad de Search Console del subdominio o un proveedor de datos con histórico (Ahrefs / Sistrix).
- **Magnitud pendiente de cuantificar** con datos de impressions/clicks (GSC) o de visibilidad histórica (Sistrix).

**Vector B — interna del apex (Shopify ↔ Shopify), confirmada con datos:**

El sitemap del apex contiene **patrones de duplicación interna** que probablemente importen más que el propio legado de PrestaShop:

1. **Colecciones Shopify legacy todavía en sitemap:**
   - `/frontpage/` — sirve el mismo contenido que la home (`/`). Duplicado puro.
   - `/all/` — listado completo del catálogo, duplica todas las categorías.
   - `/inkybay-all/` — generado por la app de personalización de fundas.

2. **Duplicado estructural de URL de modelo:** existen `/iphone-16-pro/` (a raíz) **y** `/apple/iphone-16-pro/` (bajo prefijo de marca). Hay 7 productos en la muestra colgando del segundo path; el primero también está en el sitemap. Si ambos rendern listados de modelo, es canibalización pura entre dos URLs propias.

3. **Explosión cartesiana de PDPs:** el mismo diseño de funda genera una URL distinta por cada modelo de móvil compatible. En la muestra de 250 productos, **18 diseños generan ≥4 URLs cada uno y suman 227 (91 %)** del total. Ejemplos:
   - `funda-brillantes-para-*` → 37 URLs (37 modelos distintos)
   - `funda-ultra-suave-para-*` → 26 URLs
   - `funda-ultra-suave-compatible-con-magsafe-para-*` → 21 URLs
   - `funda-bumper-3-en-1-para-*` → 18 URLs

   Cada URL es legítimamente única (la funda es compatible con un modelo concreto), pero el **title, meta description, JSON-LD y H1 muy probablemente compartirán plantilla**. Si no hay diferenciación on-page genuina, Google selecciona una URL ganadora por diseño y descarta las otras. Esto se confirma en la fase on-page (Sección 5).

**Vector descartado — `robots.txt` heredado:** la sospecha de que el apex servía un robots.txt de PrestaShop **no se confirmó**. El archivo real es correctamente Shopify (ver sección 5 actualizada).

### Ejemplos representativos (URLs reales del sitemap)

| Tipo | Ejemplo (apex) | Posible duplicado |
|---|---|---|
| Colección Shopify-legacy | `https://lacasadelascarcasas.es/frontpage/` | mismo contenido que `https://lacasadelascarcasas.es/` |
| Colección Shopify-legacy | `https://lacasadelascarcasas.es/all/` | superpone con todas las `/apple/`, `/samsung/`, etc. |
| Duplicado estructural | `https://lacasadelascarcasas.es/iphone-16-pro/` | vs `https://lacasadelascarcasas.es/apple/iphone-16-pro/` |
| PDP cartesiana | `https://lacasadelascarcasas.es/apple/iphone-15/funda-brillantes-para-iphone-15-p/` | vs misma plantilla en `iphone-16`, `iphone-16-pro`, `iphone-16-plus`, … (37 modelos para esta funda) |

---

## 4. Estado de redirecciones

**Pendiente de medición real** (script `06_redirect_chains.py` listo, no ejecutado por el bloqueo de red del entorno actual).

Lo que sí indica el reconocimiento es que **el subdominio PrestaShop no está redirigiendo masivamente al apex en su raíz**. Si lo hiciera, Google no mostraría el title y meta description originales del subdominio. Esto se interpretará como "alto porcentaje sin redirección" hasta que la medición lo desmienta — pero la cifra exacta (`% URLs PS sin redirect`, `% con 302 en lugar de 301`, `% que acaban en home`) requiere la pasada del script `06` sobre la muestra de 30 URLs estratificadas (15 productos + 15 categorías).

Los patrones que el script identifica y reportará:

- `no_redirect`: URL PrestaShop sigue viva (200 directo) — el caso peor.
- `has_302_temporary`: redirect existe pero es 302 / 307 en lugar de 301 / 308 → no transfiere autoridad.
- `long_chain`: más de un salto en cadena → pérdida progresiva de equity.
- `redirects_to_home`: acaba en el apex root sin preservar la intención → pérdida total de relevancia.
- `loop`: ciclo de redirects → URL inaccesible.
- `meta_refresh` / `js`: redirect a nivel HTML/JS (Google los maneja peor que 301 servidos).

---

## 5. Configuración Shopify

### Sitemap y estructura de URLs (confirmado con datos)

- **El sitemap del apex** (`/sitemap.xml`) declara **46 sub-sitemaps**: 32 de productos, 12 de colecciones (11 numerados + 1 `static.xml`), 2 de pages (1 + `static.xml`), y **0 de blog**.
- **Patrón de URL del sitemap**: `/sitemap/products/N.xml` (con barras), no `/sitemap_products_N.xml` (Shopify nativo con guiones bajos). Confirma que **hay una capa de reescritura / theme custom / arquitectura headless** delante del Shopify nativo. El equipo de desarrollo del cliente sabrá quién la opera.
- **Volumen estimado**: una muestra (`products/1.xml`) tiene 250 URLs. Con 32 sub-sitemaps similares, el total de productos en sitemap es del orden de **8.000 ± 2.000**. Las colecciones suman del orden de 300-500.
- **El blog editorial no está en el sitemap del apex** — vive en `blog.lacasadelascarcasas.es` (subdominio OVH del reconocimiento). Cada artículo del blog construye autoridad para el subdominio, no para el apex que vende. **Fragmentación de equity**.
- **Pattern URL productos**: `/<marca>/<modelo>/<funda-slug>-p/` (p. ej. `/apple/iphone-15/funda-brillantes-para-iphone-15-p/`). Todas las URLs terminan con `/`, normalización consistente.

### robots.txt del apex (descargado y analizado)

**Lo que está bien:**

- Directiva `Sitemap:` declarada correctamente.
- Política AI/GEO **explícita y exhaustiva**: 16 bots de IA permitidos por nombre (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, applebot-extended, OAI-SearchBot, Bard, cohere-ai, etc). Buen posicionamiento para descubrimiento en LLMs.
- Bloqueos de parámetros de tracking sólidos: `utm_*`, `gclid`, `fbclid`, `mc_cid`, `mc_eid`, además de los Shopify-específicos (`session_id`, `cart_sig`, `preview_theme_id`, `pbcid`) y los añadidos posteriormente (`cursor`, `direction`, `filters`).
- Static assets permitidos (CSS, JS, fonts, imágenes, `/cdn/`, `/cdn-cgi/`) — necesario para que Google rendere correctamente el sitio.

**Problemas detectados (riesgo bajo-medio, todos accionables):**

- **User-agents duplicados con bloques en conflicto**: `*` aparece 4 veces, `AhrefsBot` 2 veces (`Crawl-delay: 5` en un bloque y `Disallow: /` en otro), `AhrefsSiteAudit` 2 veces, `Slurp` 2 veces. Google merge los bloques del mismo UA y aplica el resultado, pero el archivo es difícil de mantener.
- **Directivas WordPress en sitio Shopify** (líneas muertas que no aplican): `/comments/feed/`, `/*/trackback/`, `/feed/rss/`. Sugiere copy-paste desde otro proyecto, probablemente el sitio anterior pre-PrestaShop.
- **Errores de formato menores**: `DisAllow:` con A mayúscula (1 línea); `User-agent: WGet` (debería ser `Wget`). Funcionan, pero son señal de revisión apurada.
- **Encoding mal servido**: el archivo contiene mojibake (`Ãšltima actualizaciÃ³n`, `BÃšSQUEDA`…). El archivo está en UTF-8 pero el server lo entrega con charset incorrecto. No afecta al parser de Google (los comentarios se ignoran), pero queda feo.
- **Bloqueo a Ahrefs, Semrush, Screaming Frog, DotBot, SEOkicks** — decisión deliberada para proteger presupuesto de crawl, pero implica que **una auditoría externa con esas herramientas requerirá levantar el bloqueo temporalmente**.

### Schema, hreflang, canonical, OG, robots meta

**Pendiente de medición real con HTML** (script `05_audit_onpage_shopify.py` listo, requiere ejecución con red abierta). Las preguntas a contestar siguen abiertas:

- **JSON-LD:** ¿hay `Product` con `name/image/brand/offers.price/priceCurrency/availability/sku/aggregateRating` completos? ¿hay `BreadcrumbList`? ¿hay `Organization` en home? **¿Hay `LocalBusiness` para las +1.000 tiendas físicas?** — este último es el que más impacto puede tener en local search.
- **Hreflang:** ¿el sitio sirve `<link rel="alternate" hreflang="...">` para los mercados internacionales que la marca afirma tener (10 países)? La búsqueda no ha revelado dominios `.fr`, `.it`, `.pt` ni subdirectorios `/it/`, `/fr/`. La internacionalización podría estar resuelta con dominios separados o no estarlo.
- **Canonical:** ¿los `<link rel="canonical">` son self-referencing, o todavía hay alguno apuntando a `*.myshopify.com`, a URLs nativas inglesas, o a `/products/<handle>` paralelas?
- **Crítico tras los hallazgos del sitemap:** ¿qué canonical sirven los 18+ PDPs que comparten plantilla por modelo? ¿Cada uno self-referencing (canibalización pasiva) o todos apuntan a un "padre" del diseño?

---

## 6. Limitaciones del pre-audit

Honestidad de método: este pre-audit ha sido un reconocimiento basado en **DNS público + índice de Google + estructura visible**. Para cuantificar el impacto en negocio y validar todo lo de las secciones 3, 4 y 5 hace falta lo siguiente:

| Para responder a... | Necesitamos |
|---|---|
| **Tráfico orgánico real por URL** y qué se pierde si una URL canibalizada se ranquea por la versión equivocada | **Google Search Console** del cliente (clicks + impresiones + CTR + posición por query y URL) — no hay sustituto: es el único dato real, gratis y propiedad del cliente |
| **Rankings históricos por keyword** y si la posición ha caído desde la migración | **SISTRIX** o **Semrush** (Visibility Index histórico, picos de ranking, fluctuaciones por update de Google) |
| **Backlinks** del apex vs del subdominio PrestaShop (¿se está perdiendo autoridad de enlaces apuntando al legacy?) | **Ahrefs** o Majestic (backlink profile completo, anchor text, calidad de dominios referrers) |
| **Presencia en respuestas de IA generativa** (ChatGPT, Perplexity, Gemini, Claude) y cómo se cita la marca | **PEEC AI**, **Bluefish**, **Profound** u otra suite de GEO/AI search monitoring |
| **Tráfico/conversión perdida específicamente por canibalización** | Cruce de GSC + GA4 + el output de `04_canibalizacion.csv` — requiere ambos accesos y unas semanas de datos |
| **Core Web Vitals reales por URL** | **CrUX dataset** (BigQuery) o PageSpeed Insights field data |
| **Estado real del robots.txt, sitemap, HTML y redirects** | Ejecutar los scripts `03`–`06` del repo en un entorno con red abierta — los scripts ya están escritos y son stdlib pura |

Sin estas fuentes:
- No podemos poner un número a *"cuánto tráfico se está perdiendo"*.
- No podemos demostrar si la canibalización ha empeorado o mejorado tras la migración a Shopify.
- No podemos comparar la posición de la marca frente a competidores directos (Fundas24, Tutecnomovil, etc.).
- No podemos verificar la presencia de la marca en LLMs y asistentes de IA, que es relevante para descubrimiento en 2026.

---

## 7. Recomendación

Este pre-audit ha confirmado, sólo con datos públicos, **tres focos críticos** (subdominio PrestaShop indexado y vivo, subdominio `prekiosco.*` con SEO injection en japonés, panel interno `board258.*` indexado) y ha levantado **dos sospechas estructurales** (robots.txt del apex posiblemente heredado de PrestaShop, ausencia visible de hreflang/LocalBusiness pese al alcance internacional y +1.000 tiendas físicas).

Una auditoría completa con acceso a Search Console, una suite de rank tracking (SISTRIX o equivalente), una de backlinks (Ahrefs) y una de monitorización GEO/AI permitiría **cuantificar el coste actual** de estas incidencias —tráfico perdido por canibalización, pérdida de visibilidad post-migración, footprint de marca en LLMs— y priorizarlas frente al esfuerzo de remediación.

Sin esa cuantificación, los hallazgos de este pre-audit ya justifican abrir tres tickets inmediatos (PrestaShop legacy, `prekiosco` como incidencia de seguridad, `board258` como exposición de panel), pero **no permiten estimar el ROI** de la corrección. Esa estimación es el objetivo del audit completo.
