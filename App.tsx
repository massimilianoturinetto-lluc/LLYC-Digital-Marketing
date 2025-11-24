import React, { useState } from 'react';
import { GameStatus, ScenarioConfig, StrategyAnalysis } from './types';
import { generateStrategy } from './services/geminiService';
import ScenarioSetup from './components/ScenarioSetup';
import StrategyResult from './components/StrategyResult';

const App: React.FC = () => {
  const [status, setStatus] = useState<GameStatus>(GameStatus.IDLE);
  const [analysisData, setAnalysisData] = useState<StrategyAnalysis | null>(null);
  const [scenarioConfig, setScenarioConfig] = useState<ScenarioConfig | null>(null);

  /**
   * PERSONALIDAD Y CONTEXTO DEL MODELO
   * Este bloque asegura que Gemini responde siempre igual, sin depender de ChatGPT.
   */
  const MODEL_PERSONALITY = `
Eres un Chief Strategy Officer experto en:
- Digital Media (Meta, Google Ads, Programmatic)
- Adtech (GA4, CAPI, Tagging, Modelos Data-Driven)
- Medición estadística (atribución, causalidad, MMM)
- Full Funnel Paid Media
- Estrategia aplicada a negocio
- Optimización basada en datos
- Inteligencia Artificial aplicada a activación

Tu misión:
Convertir inputs desestructurados (notas, PDFs, conversaciones) en:
1) Dos propuestas de reto estratégico
2) Una Diagnosis Rumelt (root cause)
3) Una Guiding Policy (no táctica)
4) Tensión cultural
5) Oportunidad de mercado
6) Insight del consumidor
7) Justificación conductual (behavioural economics)
8) Supuestos claves
9) Modelos mentales
10) Tres interpretaciones: challenger, consultiva y mixta

Reglas estrictas:
- NO entregar tácticas de medios.
- NO sugerir creatividades, slogans o claims.
- NO generar propuestas que requieran grandes inversiones, cambios estructurales o desarrollos tecnológicos pesados.
- Todo debe ser accionable vía medios, datos y adtech.
- No usar nombres de herramientas o plataformas concretas.
- Responder SIEMPRE en español.
- Mantener tono profesional, claro y directo.
`;

  /**
   * Envelope enriquecido que se envía SIEMPRE al modelo.
   */
  const buildEnhancedPayload = (config: ScenarioConfig) => {
    return {
      ...config,
      _meta: {
        personality: MODEL_PERSONALITY,
        version: "Maxicomm_CSO_v1",
        timestamp: new Date().toISOString(),
        instructions: `
Usa la personalidad definida en _meta.personality.
Siempre mantén enfoque digital media & adtech.
La salida debe conectar con la Fase 2 del proceso (Brief Builder).
Evita ambigüedad, evita texto redundante y enfócate en claridad estratégica.
        `
      }
    };
  };

  const handleStart = async (config: ScenarioConfig) => {
    setStatus(GameStatus.LOADING);
    const enriched = buildEnhancedPayload(config);

    setScenarioConfig(enriched);

    try {
      const result = await generateStrategy(enriched);
      setAnalysisData(result);
      setStatus(GameStatus.ACTIVE);
    } catch (error) {
      console.error(error);
      setStatus(GameStatus.ERROR);
    }
  };

  const handleReset = () => {
    setStatus(GameStatus.IDLE);
    setAnalysisData(null);
    setScenarioConfig(null);
  };

  cons
