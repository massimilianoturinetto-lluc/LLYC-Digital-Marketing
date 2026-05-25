# 02 — Consultas de indexación en Google

**Fecha:** 2026-05-25
**Objetivo:** estimar el volumen indexado de cada entorno y detectar URLs que no deberían estar en el índice.
**Método:** consultas manuales en navegador. No se hace scraping de Google (rompe ToS y el SERP cambia el layout al detectar automatización).

---

## Cómo usar este documento

1. Abre cada URL de la columna **"Consulta"** en una pestaña nueva, con el navegador en modo incógnito (evita personalización).
2. Lee el contador que aparece bajo la barra de búsqueda: *"Aproximadamente X resultados"*.
3. Apunta ese número en la columna **"Resultados (rellenar)"**.
4. Si Google muestra al final *"Se han omitido algunas entradas muy similares"*, **vuelve a abrir la URL** — todas llevan `&filter=0` para desactivar ese filtro, pero a veces Google lo reactiva.
5. Si la cuenta supera 100, hojea el último SERP: Google trunca a veces a ~300–400 incluso con miles indexadas; anota si **"Página X de unos N"** parece truncado.

### Parámetros que llevan todas las URLs

| Parámetro | Valor | Para qué |
|---|---|---|
| `num=100` | 100 resultados por página | Reduce paginación |
| `filter=0` | sin filtro de "similares" | Cuenta real |
| `hl=es&gl=es` | locale España | Mismo SERP que el usuario final |
| `pws=0` | sin personalización | Reduce sesgo de sesión |

### Notas importantes sobre las cifras

- El contador de `site:` de Google es **una estimación**, no un censo. Puede diferir un 20–50 % del real. Sirve para órdenes de magnitud y comparativa entre entornos, no como dato absoluto.
- Para un censo real hay que cruzar con: Search Console (impressions + páginas indexadas), `sitemap.xml` (cuántas URLs declaras) y un crawl de Screaming Frog.

---

## A. Volumen global por entorno

| # | Consulta | URL | Qué extraer | Resultados (rellenar) |
|---|---|---|---|---|
| A1 | `site:lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Total estimado indexado en el apex (Shopify). Cifra de referencia. | _____ |
| A2 | `site:www.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Awww.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Lo indexado bajo `www` en concreto. Comparar con A1 — si difieren mucho hay problema de canonicalización host. | _____ |
| A3 | `site:prestashop.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | **Indexación de la tienda PrestaShop legacy.** Cifra clave para dimensionar la canibalización. | _____ |
| A4 | `site:tienda.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Atienda.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Tercer entorno detectado (Cloudflare). Confirmar si está vacío o tiene contenido oculto. | _____ |
| A5 | `site:fabrica.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Afabrica.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Subdominio corporativo (OVH). Volumen probablemente bajo. | _____ |
| A6 | `site:blog.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Ablog.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Blog. Comprobar si duplica contenido editorial del apex. | _____ |
| A7 | `site:carcaletter.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Acarcaletter.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Landing de newsletter. Marginal. | _____ |
| A8 | `site:board258.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Aboard258.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | **Anomalía**: panel interno expuesto. Inventariar qué URLs indexa. | _____ |
| A9 | `site:prekiosco.lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3Aprekiosco.lacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | **Anomalía/posible compromiso**: contenido en japonés. Dimensionar gravedad. | _____ |
| A10 | `site:*.lacasadelascarcasas.es -site:www.lacasadelascarcasas.es -site:lacasadelascarcasas.es` | <https://www.google.com/search?q=site%3A*.lacasadelascarcasas.es+-site%3Awww.lacasadelascarcasas.es+-site%3Alacasadelascarcasas.es&num=100&filter=0&hl=es&gl=es&pws=0> | Caza-subdominios olvidados. Si aparece algo no listado arriba, añadirlo a la auditoría. | _____ |

---

## B. Patrón de URLs Shopify en el apex

Detecta si el apex tiene los slugs por defecto de Shopify (`/products/`, `/collections/`) — su presencia confirmaría que la migración no ha limpiado URLs nativas o que el theme las sirve en paralelo a los slugs en español.

| # | Consulta | URL | Qué extraer | Resultados (rellenar) |
|---|---|---|---|---|
| B1 | `site:lacasadelascarcasas.es inurl:/products/` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+inurl%3A%2Fproducts%2F&num=100&filter=0&hl=es&gl=es&pws=0> | URLs `/products/<slug>` (PDP nativa Shopify). Esperado: 0. Si > 0, hay duplicado nativo vs slug ES. | _____ |
| B2 | `site:lacasadelascarcasas.es inurl:/collections/` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+inurl%3A%2Fcollections%2F&num=100&filter=0&hl=es&gl=es&pws=0> | URLs `/collections/<handle>` (PLP nativa Shopify). Esperado: 0. Si > 0, ídem. | _____ |
| B3 | `site:lacasadelascarcasas.es inurl:.myshopify.com` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+inurl%3A.myshopify.com&num=100&filter=0&hl=es&gl=es&pws=0> | Fugas del dominio interno `*.myshopify.com`. Esperado: 0. | _____ |
| B4 | `site:lacasadelascarcasas.es inurl:?variant=` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+inurl%3A%3Fvariant%3D&num=100&filter=0&hl=es&gl=es&pws=0> | Variantes con parámetro `?variant=`. Tienen que estar canonicalizadas al producto padre — un volumen alto sugiere canonical mal. | _____ |
| B5 | `site:lacasadelascarcasas.es inurl:/colecciones/` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+inurl%3A%2Fcolecciones%2F&num=100&filter=0&hl=es&gl=es&pws=0> | PLPs en español. Esperado: igual al nº de colecciones reales. Comparar con B2. | _____ |
| B6 | `site:lacasadelascarcasas.es inurl:/fundas/` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+inurl%3A%2Ffundas%2F&num=100&filter=0&hl=es&gl=es&pws=0> | Categorías de fundas. | _____ |

---

## C. Patrón de URLs PrestaShop en el subdominio legacy

Si en el SERP del apex (B) aparecen patrones PrestaShop, sería evidencia de que hubo fugas en la migración. Si aparecen aquí (C) en gran volumen, mide el problema del legacy.

| # | Consulta | URL | Qué extraer | Resultados (rellenar) |
|---|---|---|---|---|
| C1 | `site:prestashop.lacasadelascarcasas.es inurl:/index.php` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3A%2Findex.php&num=100&filter=0&hl=es&gl=es&pws=0> | URLs con `/index.php` sin URL rewriting. Indica config PrestaShop sin friendly URLs. | _____ |
| C2 | `site:prestashop.lacasadelascarcasas.es inurl:.html` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3A.html&num=100&filter=0&hl=es&gl=es&pws=0> | PDPs PrestaShop con extensión `.html` (formato URL típico). Estimador de productos indexados. | _____ |
| C3 | `site:prestashop.lacasadelascarcasas.es inurl:id_product` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3Aid_product&num=100&filter=0&hl=es&gl=es&pws=0> | PDPs con parámetro `id_product` (URLs sin reescribir). | _____ |
| C4 | `site:prestashop.lacasadelascarcasas.es inurl:controller=` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3Acontroller%3D&num=100&filter=0&hl=es&gl=es&pws=0> | URLs `?controller=` (controladores PrestaShop expuestos). Deberían estar en `Disallow`. | _____ |
| C5 | `site:prestashop.lacasadelascarcasas.es inurl:/module/` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3A%2Fmodule%2F&num=100&filter=0&hl=es&gl=es&pws=0> | URLs de módulos PrestaShop indexados. No deberían estarlo. | _____ |
| C6 | `site:prestashop.lacasadelascarcasas.es inurl:/themes/` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3A%2Fthemes%2F&num=100&filter=0&hl=es&gl=es&pws=0> | Recursos estáticos del theme indexados (CSS/JS/imgs accesibles vía URL). | _____ |
| C7 | `site:prestashop.lacasadelascarcasas.es inurl:?search_query=` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+inurl%3A%3Fsearch_query%3D&num=100&filter=0&hl=es&gl=es&pws=0> | Búsquedas internas indexadas (thin content). Deberían estar bloqueadas. | _____ |
| C8 | `site:prestashop.lacasadelascarcasas.es inurl:?orderby=` OR `inurl:?p=` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+%28inurl%3Aorderby%3D+OR+inurl%3Ap%3D%29&num=100&filter=0&hl=es&gl=es&pws=0> | Facetas/orden y paginación indexadas. Síntoma clásico PrestaShop sin parámetros canonicalizados. | _____ |
| C9 | `site:prestashop.lacasadelascarcasas.es -inurl:index.php -inurl:.html` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+-inurl%3Aindex.php+-inurl%3A.html&num=100&filter=0&hl=es&gl=es&pws=0> | Lo que queda fuera de los dos patrones grandes (categorías, CMS pages, etc.). | _____ |

---

## D. Detección de duplicado cruzado (canibalización directa)

Aquí está el núcleo del análisis. Cogemos productos/slugs que aparecen en ambos entornos y vemos si Google muestra los dos.

| # | Consulta | URL | Qué extraer | Resultados (rellenar) |
|---|---|---|---|---|
| D1 | `"funda" site:lacasadelascarcasas.es OR site:prestashop.lacasadelascarcasas.es` | <https://www.google.com/search?q=%22funda%22+%28site%3Alacasadelascarcasas.es+OR+site%3Aprestashop.lacasadelascarcasas.es%29&num=100&filter=0&hl=es&gl=es&pws=0> | Para una query genérica del negocio, ¿Google prefiere apex o subdominio? Apuntar el orden de los 10 primeros. | _____ |
| D2 | `"iphone 15" site:lacasadelascarcasas.es OR site:prestashop.lacasadelascarcasas.es` | <https://www.google.com/search?q=%22iphone+15%22+%28site%3Alacasadelascarcasas.es+OR+site%3Aprestashop.lacasadelascarcasas.es%29&num=100&filter=0&hl=es&gl=es&pws=0> | Ídem para query muy comercial. | _____ |
| D3 | Una PDP cualquiera del apex (coge un slug largo y único, p. ej. `"Funda Capibara iPhone 15"`) en los dos entornos | construir manualmente: `https://www.google.com/search?q=%22<TITULO+EXACTO+ENTRE+COMILLAS>%22&num=100&filter=0&hl=es&gl=es&pws=0` | Misma ficha de producto en apex y en prestashop. Si Google muestra las dos, hay duplicado servido. | _____ |
| D4 | `site:lacasadelascarcasas.es intitle:"PrestaShop"` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+intitle%3A%22PrestaShop%22&num=100&filter=0&hl=es&gl=es&pws=0> | Restos de title PrestaShop dentro del apex. Esperado: 0. | _____ |
| D5 | `site:prestashop.lacasadelascarcasas.es intitle:"Shopify"` | <https://www.google.com/search?q=site%3Aprestashop.lacasadelascarcasas.es+intitle%3A%22Shopify%22&num=100&filter=0&hl=es&gl=es&pws=0> | Cruce contrario. Esperado: 0. | _____ |

---

## E. Sondeos de anomalías (board258 / prekiosco)

| # | Consulta | URL | Qué extraer | Resultados (rellenar) |
|---|---|---|---|---|
| E1 | `site:board258.lacasadelascarcasas.es inurl:/index.php` | <https://www.google.com/search?q=site%3Aboard258.lacasadelascarcasas.es+inurl%3A%2Findex.php&num=100&filter=0&hl=es&gl=es&pws=0> | URLs internas indexadas del panel. | _____ |
| E2 | `site:board258.lacasadelascarcasas.es inurl:login OR inurl:admin` | <https://www.google.com/search?q=site%3Aboard258.lacasadelascarcasas.es+%28inurl%3Alogin+OR+inurl%3Aadmin%29&num=100&filter=0&hl=es&gl=es&pws=0> | Endpoints sensibles expuestos. | _____ |
| E3 | `site:prekiosco.lacasadelascarcasas.es inurl:.htm` | <https://www.google.com/search?q=site%3Aprekiosco.lacasadelascarcasas.es+inurl%3A.htm&num=100&filter=0&hl=es&gl=es&pws=0> | Cuántas URLs `.htm` (spam JP) hay indexadas. Esperado: alto si está comprometido. | _____ |
| E4 | `site:prekiosco.lacasadelascarcasas.es inurl:goodscode` | <https://www.google.com/search?q=site%3Aprekiosco.lacasadelascarcasas.es+inurl%3Agoodscode&num=100&filter=0&hl=es&gl=es&pws=0> | Patrón concreto visto en SERP previo. Dimensionar el spam injection. | _____ |
| E5 | `site:lacasadelascarcasas.es "ヤマト" OR "ロジクール"` | <https://www.google.com/search?q=site%3Alacasadelascarcasas.es+%28%22%E3%83%A4%E3%83%9E%E3%83%88%22+OR+%22%E3%83%AD%E3%82%B8%E3%82%AF%E3%83%BC%E3%83%AB%22%29&num=100&filter=0&hl=es&gl=es&pws=0> | Palabras en japonés del spam visto en `prekiosco` — comprobar si han contaminado también el apex. | _____ |

---

## F. Patrón sugerido si en el futuro hubiera que automatizar

**No hacerlo contra Google directamente.** Si llega un momento en que necesitas series temporales, las vías limpias son:

1. **Google Search Console (GSC) de la propiedad** — datos reales (no estimaciones), por URL, con clicks/impresiones/CTR/posición. Si LLYC no tiene acceso, pedirlo al cliente. Es la fuente canónica.
2. **API de Bing Webmaster Tools** — gratis, da `urlList()` y `crawlStats()` con datos reales.
3. **SEO suites comerciales** (Ahrefs, Semrush, Sistrix) — usan crawl propio + clickstream. Ahrefs `Site Explorer → Best by links / Pages → Indexed pages` da una estimación independiente. Sistrix tiene specifically un "Indexierungsstand" por dominio.
4. **Crawl propio con Screaming Frog / Sitebulb** — combinado con la API de Google Search Console (modo "URL Inspection") permite saber pieza-a-pieza qué está indexada.

Si por lo que sea hubiera que parsear SERPs (por ejemplo, monitorizar canibalización real query a query), usa un proveedor de SERP API legítimo (DataForSEO, SerpAPI, ScrapingBee) que paga las queries y devuelve JSON limpio. **Nunca** rascar `google.com/search` desde tu IP — bloquean en pocas decenas de queries y contamina cookies del navegador del que lo haga.

Pattern teórico de extracción (sólo referencia, no para ejecutar):

- Contador agregado: selector CSS `#result-stats` → texto "Aproximadamente X resultados (Y segundos)" → regex `\d[\d.\s]*` sobre el primer grupo.
- Resultados orgánicos: cada bloque `div.g` o `div[data-hveid]`, dentro `a[href^="http"]` (excluir `webcache.googleusercontent.com` y `translate.google.com`).
- Detección de "results omitted": presencia del enlace con texto *"repetir la búsqueda e incluir los resultados que se han omitido"*.
- Truncado de SERP: el botón "Página X de N" — si pulsas a la última y la cifra cae respecto al contador inicial, el contador es promocional.

---

## G. Plantilla de informe para `03_indexacion_resultados.md` (siguiente paso)

Cuando hayas rellenado las columnas de arriba, copia los números a la siguiente tabla y volveremos a interpretar:

```
| Entorno                                    | Indexado estimado | Productos | Categorías | Anomalías |
| ------------------------------------------ | ----------------- | --------- | ---------- | --------- |
| lacasadelascarcasas.es (Shopify)           |                   |           |            |           |
| prestashop.lacasadelascarcasas.es          |                   |           |            |           |
| tienda.lacasadelascarcasas.es              |                   |           |            |           |
| fabrica / blog / carcaletter               |                   |           |            |           |
| board258 (intranet)                        |                   |           |            |           |
| prekiosco (posible spam)                   |                   |           |            |           |
```

Pregúntame cuando tengas la columna de resultados llena y monto la interpretación en `03_indexacion_resultados.md`.
