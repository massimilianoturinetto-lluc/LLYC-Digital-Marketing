/*  
|--------------------------------------------------------------------------
| MODELO DE IA
|--------------------------------------------------------------------------
| Motor principal: Gemini 3 Pro
*/
export const MODEL_NAME = "gemini-3-pro";


/*  
|--------------------------------------------------------------------------
| MÉTRICAS ESTRATÉGICAS DEFAULT
|--------------------------------------------------------------------------
| Qué indicadores iniciales puede mostrar la app si no hay otros definidos.
| Pensado para medios, data y madurez digital.
*/
export const INITIAL_METRICS_COUNT = 4;

export const DEFAULT_METRICS = [
  { name: "Madurez Digital", value: 45 },
  { name: "Eficiencia de Medios", value: 55 },
  { name: "Fiabilidad del Dato", value: 35 },
  { name: "Alineación Negocio–Medios", value: 60 },
];


/*  
|--------------------------------------------------------------------------
| SUGERENCIAS / HINTS PARA INPUT DEL EQUIPO
|--------------------------------------------------------------------------
| Textos que ayudan al equipo a introducir contexto claro en ScenarioSetup.
| Muy alineado al prisma de Digital Media + Adtech.
*/
export const DEFAULT_HINTS = [
  "Incluye el objetivo de negocio y el rol que medios debe cumplir.",
  "Describe los principales bloqueos de medición (GA4, CAPI, tagging).",
  "Explica el funnel actual y dónde se atasca la conversión.",
  "Añade señales sobre competencia o tensiones del mercado.",
  "Indica si hay restricciones de presupuesto, timing o tech stack.",
];


/*  
|--------------------------------------------------------------------------
| SUGERENCIAS REDACTADAS PARA EL CONTEXTO EN BRUTO
|--------------------------------------------------------------------------
| Las que verás visibles justo debajo del textarea para guiar al equipo.
*/
export const RAW_CONTEXT_PLACEHOLDERS = [
  "Notas de reunión, briefing inicial, hipótesis del equipo…",
  "Problemas detectados en performance, medición o atribución.",
  "Bloqueos entre CRM, web y paid media.",
  "Cualquier información desordenada que necesite estructurarse.",
];


/*  
|--------------------------------------------------------------------------
| TIPOS DE OPORTUNIDAD (OPCIONES VISIBLES EN SELECT)
|--------------------------------------------------------------------------
*/
export const OPPORTUNITY_TYPES = [
  { value: "newbiz", label: "Newbiz" },
  { value: "upsell", label: "Upsell" },
  { value: "cross-sell", label: "Cross-sell" },
];


/*  
|--------------------------------------------------------------------------
| ROLES PRIORITARIOS DE MEDIOS
|--------------------------------------------------------------------------
*/
export const MEDIA_ROLES = [
  { value: "brand", label: "Brand" },
  { value: "performance", label: "Performance" },
  { value: "retail", label: "Retail Media" },
  { value: "mixed", label: "Mixto" },
];


/*  
|--------------------------------------------------------------------------
| MADUREZ DIGITAL
|--------------------------------------------------------------------------
*/
export const DIGITAL_MATURITY_LEVELS = [
  { value: "low", label: "Baja" },
  { value: "mid", label: "Media" },
  { value: "high", label: "Alta" },
];


/*  
|--------------------------------------------------------------------------
| TEXTOS DE SISTEMA (frases reutilizables)
|--------------------------------------------------------------------------
*/
export const SYSTEM_TEXT = {
  analysisHeader: "Lectura generada por el motor Maxicomm CSO (Gemini 3 Pro).",
  defaultClientName: "Cliente confidencial",
  skipContext: "Reto estratégico estándar para evaluar oportunidades desde medios, datos y adtech.",
};


/*  
|--------------------------------------------------------------------------
| COLORES DEL BRANDING (si deseas usarlos desde JS)
|--------------------------------------------------------------------------
*/
export const BRAND_COLORS = {
  red: "#F54963",
  teal: "#36A7B7",
  dark: "#0A263B",
  grey: "#6D7475",
  softGrey: "#B0B8BA",
};
