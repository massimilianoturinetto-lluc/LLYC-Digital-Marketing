# 01 — Reconocimiento SEO: lacasadelascarcasas.es

**Fecha:** 2026-05-25
**Alcance:** dominio principal + detección de subdominio PrestaShop activo + identificación de plataformas.
**Estado:** recopilación de datos sin interpretación.

---

## 0. Restricciones del entorno

El sandbox de ejecución bloquea todo el tráfico HTTP/HTTPS saliente a `lacasadelascarcasas.es` y a cualquier otro host externo (la respuesta es `HTTP 403 x-deny-reason: host_not_allowed` desde el proxy de salida, no desde el servidor de origen). Esto afecta tanto a `curl` como a `WebFetch`.

**Implicaciones para este reconocimiento:**
- No se pueden descargar `robots.txt` ni `sitemap.xml` directamente desde este entorno.
- No se puede inspeccionar el HTML del home en vivo.
- No se pueden ver headers reales (`X-Powered-By`, `Server`, `Set-Cookie`) de los servidores de origen.

**Lo que sí se puede hacer y se ha hecho:**
- Resolución DNS (apex + subdominios) → da la huella de hosting/plataforma.
- WebSearch (Google) → snapshot de indexación y snippets descriptivos del contenido cacheado.

Las descargas de `robots.txt`, `sitemap.xml` e inspección de headers/HTML quedan pendientes para una fase con red abierta (entorno local del consultor o herramienta SEO externa tipo Screaming Frog, Sitebulb, curl manual).

---

## 1. Subdominios probados

Se probaron por `curl -I` con timeout de 10 s los subdominios habituales sugeridos: `www2`, `shop`, `old`, `tienda`, `prestashop`, `m`, `store`, `classic`.

| Subdominio | HTTP curl (sandbox) | DNS resuelve | Notas |
|---|---|---|---|
| www2.lacasadelascarcasas.es | 000 (sin conexión) | No | NXDOMAIN |
| shop.lacasadelascarcasas.es | 000 | No | NXDOMAIN |
| old.lacasadelascarcasas.es | 000 | No | NXDOMAIN |
| **tienda.lacasadelascarcasas.es** | 403 (deny proxy) | **Sí — Cloudflare** | `104.26.12.146`, `104.26.13.146`, `2606:4700:20::*` |
| **prestashop.lacasadelascarcasas.es** | 403 (deny proxy) | **Sí — GCP** | `34.160.183.245` (Google Cloud Load Balancer) |
| m.lacasadelascarcasas.es | 000 | No | NXDOMAIN |
| store.lacasadelascarcasas.es | 000 | No | NXDOMAIN |
| classic.lacasadelascarcasas.es | 000 | No | NXDOMAIN |

> Aclaración: los `403` de `tienda` y `prestashop` son del proxy del sandbox (`x-deny-reason: host_not_allowed`), no del servidor de origen. Lo informativo es que **estos dos subdominios sí resuelven DNS y apuntan a hosting real distinto del dominio principal**.

---

## 2. Subdominios adicionales descubiertos (via Google)

Búsquedas tipo `site:lacasadelascarcasas.es` revelaron más subdominios que no estaban en la lista a probar:

| Subdominio | IP | Notas |
|---|---|---|
| `fabrica.lacasadelascarcasas.es` | `87.98.225.238` | OVH. Resultado indexado: "Discover how we recycle at the LCDLC Factory" — sección corporativa en `/en/`. |
| `blog.lacasadelascarcasas.es` | `87.98.225.238` | Mismo IP que `fabrica` (host compartido). Resultado indexado: "SuaveFest: El festival que fusiona la música y el estilo de la Casa de Las Carcasas". |
| `carcaletter.lacasadelascarcasas.es` | `217.71.200.110` | Resultado indexado: "Carcaseando" — newsletter / landing de captación. |
| `board258.lacasadelascarcasas.es` | `81.0.58.230` | IP española. Indexado como "LCDLC" en `/index.php` — **panel interno/intranet expuesto en Google**. |
| `prekiosco.lacasadelascarcasas.es` | `185.14.58.26` | **Anómalo**: Google indexa URLs con títulos en japonés (`ヤマト 高圧継手...`, `Logicool G ゲーミングマウス...`, paths tipo `/goodscode1788462811.htm`, `/item510051609.htm`, `/shopdetail*.htm`). Patrón típico de **subdominio comprometido / SEO spam japonés** o hosting parqueado mal configurado. |

---

## 3. Datos DNS clave

```
lacasadelascarcasas.es        →  23.227.38.65        (Shopify edge — rango 23.227.38.0/24)
www.lacasadelascarcasas.es    →  23.227.38.74        (CNAME a shops.myshopify.com — visible en getent)
prestashop.lacasadelascarcasas.es → 34.160.183.245   (Google Cloud Load Balancer)
tienda.lacasadelascarcasas.es →  104.26.12.146 / 104.26.13.146 / 2606:4700:20::*  (Cloudflare)
fabrica.lacasadelascarcasas.es → 87.98.225.238       (OVH)
blog.lacasadelascarcasas.es   →  87.98.225.238       (OVH, mismo host que fabrica)
carcaletter.lacasadelascarcasas.es → 217.71.200.110
board258.lacasadelascarcasas.es → 81.0.58.230
prekiosco.lacasadelascarcasas.es → 185.14.58.26
```

Evidencia directa de la CNAME de Shopify (output literal de `getent ahosts www.lacasadelascarcasas.es`):
```
23.227.38.74    STREAM shops.myshopify.com
```

---

## 4. Subdominio PrestaShop activo

**Identificado: `prestashop.lacasadelascarcasas.es`**

Indicadores recogidos:

- **DNS:** apunta a `34.160.183.245` (Google Cloud LB), infraestructura distinta del apex (Shopify).
- **Indexación Google:** `site:prestashop.lacasadelascarcasas.es` devuelve la home indexada con title `"Fundas para Móviles y Accesorios - La Casa de las Carcasas"` y meta description hablando de "48 horas", "miles de diseños", "envío gratis".
- **Snippet de Google sobre la URL `lacasadelascarcasas.es/robots.txt`** (literal del resultado de búsqueda):
  > *"The robots.txt file for this site was automatically generated by PrestaShop e-commerce open-source solution. This file contains multiple Disallow directives for various controllers including authentication, cart, discount, footer, get-file, header, history, identity, images, initialization, my-account, order-related pages, pagination, password, PDF generation, product-sort, registration, search, statistics, and guest-tracking."*

  → Pendiente: confirmar si esa descripción corresponde al robots.txt **actual** del apex (Shopify) o al **cacheado de cuando el apex era PrestaShop antes de la migración**. No interpretar aún.

- **Búsqueda externa** ("Websites using PrestaShop in Spain" en BuiltWith trends listó este sitio): confirma plataforma PrestaShop asociada al dominio.
- **Snippet de eXtremaNET** (proveedor) sobre el proyecto: *"migración de WooCommerce/WordPress a PrestaShop"* — historial de plataforma.

---

## 5. robots.txt y sitemap.xml

**No se ha podido descargar el contenido** (sandbox bloquea HTTP saliente). Pendiente para fase con red abierta.

URLs candidatas a inspeccionar manualmente:

```
https://lacasadelascarcasas.es/robots.txt
https://lacasadelascarcasas.es/sitemap.xml
https://www.lacasadelascarcasas.es/sitemap.xml
https://lacasadelascarcasas.es/sitemap_index.xml          (Shopify suele usar sitemap.xml a secas)
https://prestashop.lacasadelascarcasas.es/robots.txt
https://prestashop.lacasadelascarcasas.es/sitemap.xml
https://prestashop.lacasadelascarcasas.es/1_index_sitemap.xml   (patrón típico módulo gsitemap PrestaShop)
```

Lo único recogido vía Google sobre el contenido del robots.txt del apex es el snippet del punto 4 (descripción genérica PrestaShop, sin las líneas literales). Sin contenido bruto no puedo listar Disallow ni Sitemap directives reales.

---

## 6. Indicios de plataforma por entorno

### 6.1 Dominio principal (apex + www)

| Señal | Valor recogido | Fuente |
|---|---|---|
| IP / hosting | `23.227.38.65` (apex) / `23.227.38.74` (www) — rango Shopify | DNS local |
| CNAME | `shops.myshopify.com` | DNS local (`getent ahosts www`) |
| Headers HTTP | **No recogidos** (proxy denegó) | — |
| Meta generator | **No recogido** (proxy denegó) | — |
| Patrón de URLs indexadas | `/tiendas/`, `/nosotros/`, `/la-fabrica/`, `/nuestros-productos/`, `/fundas/`, `/colecciones/`, `/ofertas/`, `/colaboraciones/`, `/faqs/` — slugs en español, **no** `/collections/` ni `/products/` Shopify-default | Google search |
| inurl:/products/ | 0 resultados propios en el apex | Google search |
| inurl:/collections/ | 0 resultados propios; sí hay `/colecciones/` (con C, en español) | Google search |

→ Hosting es Shopify confirmado; el patrón de URLs no es el default de Shopify (sugiere reescritura de URLs / app de traducción / headless). Pendiente confirmar con HTML real.

### 6.2 Subdominio prestashop.lacasadelascarcasas.es

| Señal | Valor recogido | Fuente |
|---|---|---|
| IP / hosting | `34.160.183.245` — Google Cloud LB | DNS local |
| Headers HTTP | **No recogidos** (proxy denegó) | — |
| Meta generator | **No recogido** | — |
| Patrón de URLs en Google | Solo la home `/` aparece indexada con `site:prestashop.lacasadelascarcasas.es` | Google search |
| inurl:id_product | 0 hits propios | Google search |
| inurl:index.php | 0 hits propios | Google search |
| Plataforma confirmada externamente | BuiltWith / Webempresa / blogs sectoriales: "PrestaShop e-commerce" | Google snippets |

→ La home está indexada. Profundidad de indexación real no verificada (Google `site:` infrarreporta).

### 6.3 tienda.lacasadelascarcasas.es

| Señal | Valor |
|---|---|
| Hosting | Cloudflare (104.26.12.146 / 104.26.13.146) — tercer entorno distinto de Shopify y PrestaShop |
| Indexación | `site:tienda.lacasadelascarcasas.es` no devuelve resultados propios (Google muestra fallbacks del apex) |

→ Existe DNS y CDN activa, pero sin contenido indexado visible. Estado de uso real desconocido.

---

## 7. Resumen de subdominios para auditoría

| Subdominio | Plataforma probable | Indexado | Acción pendiente |
|---|---|---|---|
| `lacasadelascarcasas.es` (+ www) | Shopify | Sí (gran volumen) | Inspeccionar robots / sitemap / HTML |
| `prestashop.lacasadelascarcasas.es` | PrestaShop sobre GCP | Sí (al menos home) | **Foco principal de la canibalización** — descargar sitemap, contar URLs, verificar indexación |
| `tienda.lacasadelascarcasas.es` | Detrás de Cloudflare, plataforma desconocida | No visible | Verificar si sirve contenido o redirige |
| `fabrica.lacasadelascarcasas.es` | Hosting OVH | Sí (corporativo, `/en/`) | Fuera de scope canibalización; revisar links cruzados |
| `blog.lacasadelascarcasas.es` | Mismo host que `fabrica` | Sí (posts) | Comprobar si blog del apex está duplicado aquí |
| `carcaletter.lacasadelascarcasas.es` | Newsletter landing | Sí | Marginal |
| `board258.lacasadelascarcasas.es` | Intranet con `/index.php` indexado | Sí | **Anomalía** — panel interno expuesto a Google |
| `prekiosco.lacasadelascarcasas.es` | Desconocido, contenido en japonés indexado | Sí (spam JP) | **Anomalía / posible compromiso** — investigar prioridad seguridad |

---

## 8. Limitaciones y siguientes pasos para la fase 2

Para poder responder a las tres preguntas que pediste sin huecos, en la siguiente fase necesito ejecutarse en un entorno con red abierta (o que tú me pases los outputs):

1. `curl -sIL -A "Mozilla/..." https://lacasadelascarcasas.es/` y mismo para los tres subdominios sospechosos → headers de servidor, cookies, server-pushed generator.
2. `curl -s https://lacasadelascarcasas.es/robots.txt` y mismo en `prestashop.*` → diff de bloqueos.
3. `curl -s https://lacasadelascarcasas.es/sitemap.xml | grep -c '<loc>'` y mismo en `prestashop.*` → conteo de URLs y dominio al que apuntan los `<loc>`.
4. `curl -s https://lacasadelascarcasas.es/ | grep -Ei 'generator|shopify|prestashop|cdn.shopify|/skin/frontend|/themes/'` → fingerprint HTML.

Si me pasas los outputs en bruto de esos 4 comandos, completo `02_canibalizacion.md` con los hallazgos interpretados.
