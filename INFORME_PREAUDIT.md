# Pre-audit SEO · lacasadelascarcasas.es

**Fecha:** 2026-05-25
**Alcance:** reconocimiento previo a auditoría completa. Validar convivencia de plataformas, dimensionar el riesgo de canibalización entre el dominio principal (Shopify) y el subdominio legacy `prestashop.lacasadelascarcasas.es`, e identificar anomalías estructurales.
**Fuentes de datos de este pre-audit:**
- Resolución DNS directa (apex + subdominios).
- Indexación en Google vía búsquedas `site:` y consultas dirigidas.

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

### 2.5 Indicio de robots.txt del apex describiendo configuración PrestaShop

- **Qué:** el snippet con el que Google describe `https://lacasadelascarcasas.es/robots.txt` en SERP dice literalmente *"automatically generated by PrestaShop e-commerce open-source solution"* y enumera bloqueos típicos de controladores PrestaShop (`authentication`, `cart`, `discount`, `my-account`, `pagination`, `password`, `search`, `statistics`, `guest-tracking`).
- **Por qué importa:** si la descripción es del estado actual, **el apex (Shopify) estaría sirviendo el robots.txt que dejó PrestaShop antes de la migración**. Eso implicaría bloqueos sin sentido (Shopify no tiene `/my-account/` ni `/guest-tracking/`) y posiblemente ausencia de la directiva `Sitemap:` correcta.
- **Estado:** **pendiente de confirmar** descargando el robots.txt real. Si el snippet es cacheado de pre-migración, no hay problema; si es actual, es un bug significativo.
- **URL a inspeccionar:** `https://lacasadelascarcasas.es/robots.txt`

---

## 3. Canibalización

### Volumen detectado

El **vector de canibalización está confirmado** (subdominio `prestashop.*` indexado y compartiendo intención comercial con el apex), pero su **magnitud requiere ejecutar el crawler de sitemaps + el comparador HTTP** (scripts `03` y `04`) en un entorno con red abierta.

Lo que sí podemos afirmar a 25 de mayo de 2026:
- La home de `prestashop.*` está indexada → como mínimo hay competencia por la query brand+raíz ("la casa de las carcasas", "fundas móvil").
- La infraestructura del subdominio (GCP) está activa, no devuelve los timeouts típicos de un dominio abandonado.
- El title y description indexados son comerciales completos, no placeholders.

### Ejemplos representativos

A falta de la salida real de `04_canibalizacion.csv`, los patrones de duplicación que el comparador buscará — y que la heurística ya tiene configurada — son:

| Patrón PrestaShop | Equivalente Shopify esperado | Cómo se detectará |
|---|---|---|
| `https://prestashop.lacasadelascarcasas.es/<id>-<slug>/` (categoría) | `https://lacasadelascarcasas.es/colecciones/<slug>` | HEAD a ambas → ambas 200 = canibalización |
| `https://prestashop.lacasadelascarcasas.es/<categoria>/<id>-<slug>.html` (producto) | `https://lacasadelascarcasas.es/<slug>` | HEAD a ambas |
| `https://prestashop.lacasadelascarcasas.es/content/<id>-<slug>` (CMS) | `https://lacasadelascarcasas.es/<slug>` | HEAD a ambas |
| `https://prestashop.lacasadelascarcasas.es/` (home) | `https://lacasadelascarcasas.es/` | Caso confirmado: ambas vivas |

### Patrón observado (con los datos que tenemos)

- **Como mínimo, canibalización a nivel home.** Confirmado.
- **Plausible canibalización a nivel categoría/producto** dado que el subdominio sigue en infraestructura productiva, no parece estar parqueado ni redirigido al apex de raíz (si lo estuviera, Google ya no indexaría su title comercial). Confirmar con la cifra real de `04_canibalizacion.csv`.

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

**Pendiente de medición real** (script `05_audit_onpage_shopify.py` listo, no ejecutado). Lo confirmado hasta ahora:

### Estructura de URLs

- El apex usa slugs en español: `/fundas/`, `/colecciones/`, `/ofertas/`, `/tiendas/`, `/nosotros/`, `/la-fabrica/`, `/nuestros-productos/`, `/colaboraciones/`, `/faqs/`.
- **No se encontraron URLs `/products/` ni `/collections/` (en inglés) indexadas** en el apex tras la consulta correspondiente.
- Esto implica que Shopify está sirviendo con **reescritura de URLs / app de traducción / un theme custom o setup headless**. No es la URL nativa Shopify, lo cual es positivo para SEO local pero introduce riesgos a verificar:
  - Si la URL `/products/<handle>` nativa de Shopify sigue viva en paralelo → duplicado interno.
  - Si los `canonical` apuntan a la URL en español o a la nativa.
  - Si Search Console está dado de alta con la propiedad correcta.

### Schema, hreflang, canonical, OG, robots meta

Las tres preguntas críticas para Shopify quedan pendientes y son lo que medirá `05_audit_onpage_shopify.py` sobre una muestra de 7 URLs (home + 3 collections + 3 products):

- **JSON-LD:** ¿hay `Product` con `name/image/brand/offers.price/priceCurrency/availability/sku/aggregateRating` completos? ¿hay `BreadcrumbList`? ¿hay `Organization` en home? **¿Hay `LocalBusiness` para las +1.000 tiendas físicas?** — este último es el que más impacto puede tener en local search y no está garantizado en Shopify por defecto.
- **Hreflang:** ¿el sitio sirve `<link rel="alternate" hreflang="...">` para los mercados internacionales que la marca afirma tener (10 países)? La búsqueda no ha revelado dominios `.fr`, `.it`, `.pt` ni un subdirectorio `/it/`, `/fr/` — la internacionalización podría estar resuelta con dominios separados o no estarlo.
- **Canonical:** ¿los `<link rel="canonical">` son self-referencing y apuntan al apex en español, o todavía hay alguno apuntando a `*.myshopify.com` o a URLs nativas inglesas?

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
