# Kickoff LCDLC — briefing de alineamiento con Natalia

**Reunión:** kickoff con cliente (La Casa de las Carcasas)
**Duración estimada:** 60 min
**Asistentes por LLYC:** Massimiliano (senior lead / account) + Natalia (consultora responsable del delivery)
**Objetivo interno:** validar diagnóstico, extraer todo lo necesario para arrancar F0, cerrar con próximos pasos claros.

---

## Reparto de roles

| Persona | Franja | Rol |
|---|---|---|
| **Massimiliano** | 0-30' + cierre | Abre, encuadra, expone hallazgos, hace las preguntas estratégicas / incómodas, negocia si sale un tema económico |
| **Natalia** | 30-55' | Coge el testigo, conduce el elicitation técnico, valida deliverables y RACI |

**Regla de sala:** si sale algo comercial / político → habla Massimiliano. Si sale algo de arquitectura, medición, stack o accesos → habla Natalia. No corregirse en directo: si uno se pisa, el otro apoya y se ajusta offline.

---

## Timeline — storytelling minuto a minuto

### 0-05' · Apertura (Massimiliano)
- [ ] Bienvenida y agradecimiento por la reunión anterior + envío del detalle de proyecto
- [ ] Presentar a Natalia como consultora al frente del delivery: *"a partir de ahora ella es vuestro punto de contacto principal en el día a día; yo me quedo como sponsor del proyecto"*
- [ ] Encuadre: *"hoy queremos alinear el diagnóstico, recoger información y cerrar con próximos pasos concretos"*
- [ ] Agenda visible en pantalla (4 bloques: diagnóstico → preguntas → elicitation → próximos pasos)

### 5-20' · Diagnóstico y hallazgos (Massimiliano)
- [ ] Recap ultra-breve del pre-audit — **datos, no opiniones**
- [ ] Top 3 hallazgos que abren conversación:
  - [ ] Subdominio PrestaShop legacy vivo + `Disallow: /` que **no desindexa**
  - [ ] Canibalización interna en el apex (colecciones legacy `/frontpage/`, `/all/`, `/inkybay-all/` + duplicado `/iphone-16-pro/` + explosión cartesiana de PDPs)
  - [ ] Anomalías en subdominios (`prekiosco.*`, `board258.*`)
- [ ] Framing suave: *"no es una crítica al trabajo previo, es el punto de partida para decidir qué priorizamos"*

### 20-30' · Preguntas incómodas (Massimiliano)
→ ver bloque dedicado abajo. Objetivo: sacar información política y de gobernanza que Natalia no debería tener que preguntar en su primera interacción.

### 30-32' · Handoff explícito
Frase de Massimiliano para pasar el testigo:
> *"Hasta aquí el marco. A partir de ahora Natalia coge el turno y baja al detalle técnico que necesitamos para arrancar. Yo me quedo escuchando y saltaré solo si sale algo comercial."*

- [ ] Que se note el cambio de voz en la sala — Natalia toma pantalla / se acerca al micro
- [ ] Massimiliano cierra su portátil visualmente, gesto que refuerza el handoff

### 32-55' · Elicitation técnico (Natalia)
→ ver bloque dedicado abajo. Objetivo: irse con lo necesario para arrancar F0 el lunes siguiente.

### 55-60' · Cierre (Massimiliano cierra, Natalia acompaña)
- [ ] Recap de compromisos: quién manda qué y para cuándo (accesos, contactos, decisiones pendientes)
- [ ] Cadencia acordada (weekly + daily durante F2 España)
- [ ] Fecha de próxima reunión
- [ ] Frase de cierre: *"os mandamos recap por email en menos de 24 h"*

---

## Preguntas incómodas — turno Massimiliano (20-30')

Ordenadas de menos a más sensible. Objetivo: información que necesitamos pero que quema si la pregunta la consultora en frío.

### Sobre el histórico de la migración
- [ ] *"¿Qué motivó la migración WooCommerce/PrestaShop → Shopify y qué se midió en su momento?"*
- [ ] *"¿La migración se acompañó de un plan de redirecciones y desindexación del subdominio antiguo?"*
- [ ] *"¿Habéis notado caídas de tráfico orgánico atribuibles a la migración? ¿Se ha reportado eso a comité?"*

### Sobre gobernanza y decisión técnica
- [ ] *"¿Quién tiene la última palabra en la arquitectura de URLs — product, tech, o un partner externo?"*
- [ ] *"El sitemap del apex usa un patrón `/sitemap/products/1.xml` que no es Shopify nativo. ¿Sabéis qué capa lo genera — theme custom, headless, una app?"*
- [ ] *"Search Console y Analytics 4 — ¿están en vuestro workspace o en el de una agencia anterior?"*

### Sobre los subdominios anómalos
- [ ] *"Hemos detectado `board258.lacasadelascarcasas.es` en Google, parece un panel interno. ¿Sabéis quién lo opera?"*
- [ ] *"Y algo más delicado: `prekiosco.lacasadelascarcasas.es` está indexado con contenido en japonés que no encaja con la marca. Preferimos comentarlo en voz alta porque puede que os interese verificar el registro DNS con vuestro equipo de sistemas."*
  - Tono neutro. No es acusación, es aviso. Bajar intensidad si el interlocutor se pone tenso.

### Sobre presupuesto y decisión
- [ ] *"El detalle económico que os pasamos, ¿lo estáis viendo como bloques independientes o pensáis en la opción integrada (A)?"*
- [ ] *"¿Hay fecha realista de decisión, o esto pasa por comité?"*
- [ ] *"¿Necesitáis que preparemos un memo interno para vuestro CFO / management?"*

---

## Elicitation técnico — turno Natalia (32-55')

Objetivo: irse con lo necesario para arrancar F0 el lunes siguiente. Solo lo que bloquea si no lo tenemos.

### Accesos (crítico para no perder días)
- [ ] Search Console — permiso *owner*
- [ ] Google Analytics 4 — permiso *edit*
- [ ] Shopify admin — usuario staff con acceso a temas y navigation
- [ ] Repositorio del theme (GitHub/GitLab) — read
- [ ] Repositorio del headless / BFF si existe — read
- [ ] Panel DNS o contacto que pueda cambiar registros bajo demanda
- [ ] Google Business Profile Manager — permiso *manager* sobre las +1.000 fichas
- [ ] Contacto directo: PM de dev del cliente + responsable de infra

### Stack y arquitectura
- [ ] *"¿Qué theme corre el Shopify actual y qué apps están instaladas?"*
- [ ] *"¿La capa que sirve `/sitemap/products/1.xml` es una app, un theme custom o un frontend headless?"*
- [ ] *"¿Hay entorno de staging separado de producción? ¿Cómo es el proceso de despliegue?"*
- [ ] *"¿Cómo está montada la internacionalización — Shopify Markets, dominios separados, subdirectorios?"*

### Roadmap del cliente
- [ ] *"¿Calendario de releases y ventanas de mantenimiento?"*
- [ ] *"¿Algún hito de negocio en los próximos 6-7 meses que condicione la ventana de migración ES (Black Friday, campañas, tienda 1.001)?"*
- [ ] *"¿Cuándo consideráis una ventana aceptable para la migración crítica de ES (F2)?"*

### Datos y medición
- [ ] *"¿Qué KPI mide hoy éxito de negocio online?"*
- [ ] *"¿Tenéis histórico ≥12 meses de sesiones + revenue por país en GA4?"*
- [ ] *"¿Cómo se atribuye la venta física originada online (store locator → tienda)? ¿Hay pixel, GBP tracking, encuestas?"*

### Contactos por mercado
- [ ] *"¿Product owner o content lead por mercado, o todo se decide desde ES?"*
- [ ] *"¿Quién revisa y aprueba copy en IT, FR, PT…?"*
- [ ] *"GBP: ¿quién gestiona hoy las +1.000 fichas — equipo interno, proveedor?"*

### Deliverables y cadencia
- [ ] Confirmar en pantalla: qué producimos nosotros vs qué produce su equipo
- [ ] Cadencia: weekly + daily durante F2 ES
- [ ] Canal de comunicación: Slack compartido / MS Teams / email
- [ ] Reporting: Looker Studio, ppt semanal, tablero público

---

## Reglas de sala (para los dos)

- [ ] No prometer cifras concretas de tráfico ni ranking recuperado — solo % de riesgo mitigable
- [ ] No comentar números económicos si el interlocutor comercial no ha aceptado el bloque
- [ ] Pregunta que no podemos responder → *"lo miramos hoy y os contestamos por email antes de mañana"*
- [ ] Tema nuevo grande fuera de agenda → parking lot y volver al hilo

## Materiales a tener a mano
- [ ] `INFORME_PREAUDIT.md` — mostrar en pantalla, no enviar por email todavía
- [ ] `03_sitemaps_analysis.md` como respaldo si piden detalle URL
- [ ] Xlsx del proyecto — ya enviado, solo referenciar
- [ ] Plantilla RACI vacía por si da tiempo a rellenarla en directo

## Después del kickoff (mismo día)
- [ ] Recap por email antes de 24 h: compromisos, accesos solicitados, próxima fecha
- [ ] Abrir canal de comunicación acordado
- [ ] Natalia arranca F0 el lunes siguiente si los accesos han llegado

---

## Nota para Natalia

Este documento es para checkear en directo. Si detectas algo que quieras adelantar tú o algo que prefieras que yo no toque, avísame antes de la reunión y lo movemos. La lista de "preguntas incómodas" son las que quiero llevar yo porque queman menos si vienen del sponsor que si vienen de la consultora al frente. Pero si en la sala ves que una encaja mejor por tu boca, la sueltas y yo apoyo.
