import React, { useState } from 'react';
import { StrategyAnalysis } from '../types';

interface StrategyResultProps {
  data: StrategyAnalysis;
  clientName: string;
  onReset: () => void;
}

const Card: React.FC<{
  title: string;
  children: React.ReactNode;
  className?: string;
}> = ({ title, children, className = '' }) => (
  <div
    className={`bg-white border border-gray-100 rounded-xl p-6 shadow-soft ${className}`}
  >
    <h3 className="text-xs font-heading font-bold text-brand-teal uppercase tracking-wider mb-4">
      {title}
    </h3>
    <div className="text-brand-text text-sm leading-relaxed whitespace-pre-line">
      {children}
    </div>
  </div>
);

type NarrativeTab = 'challenger' | 'consultive' | 'mixed';

const StrategyResult: React.FC<StrategyResultProps> = ({
  data,
  clientName,
  onReset,
}) => {
  const [activeTab, setActiveTab] = useState<NarrativeTab>('mixed');

  const handleExport = () => {
    const now = new Date();
    const datetime = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);

    const title = `Reto Estratégico – ${clientName || 'Cliente'}`;

    const assumptions =
      data.keyAssumptions && data.keyAssumptions.length
        ? `- ${data.keyAssumptions.join('\n- ')}`
        : '- (Sin supuestos declarados)';

    const mentalModels =
      data.relevantMentalModels && data.relevantMentalModels.length
        ? `- ${data.relevantMentalModels.join('\n- ')}`
        : '- (Sin modelos mentales declarados)';

    const docBody = `
## Propuestas de reto
### A)
${data.challengeStatement_A}

### B)
${data.challengeStatement_B}

---

## Diagnosis Rumelt
${data.rumeltDiagnosis}

## Guiding Policy
${data.rumeltGuidingPolicy}

---

## Tensión Cultural
${data.culturalTension}

## Oportunidad de Mercado
${data.marketOpportunity}

## Insight del Consumidor
${data.consumerInsight}

## Justificación Conductual
${data.behavioralJustification}

## Supuestos Clave
${assumptions}

## Modelos Mentales Relevantes
${mentalModels}

---

## Tres Lecturas Estratégicas
### Challenger
${data.interpretation_challenger}

### Consultiva
${data.interpretation_consultive}

### Mixta
${data.interpretation_mixed}
`.trim();

    const fullContent = `# ${title}\n\n${docBody}`;
    const safeClientName =
      clientName && clientName.trim().length > 0
        ? clientName.trim().replace(/[^a-z0-9]/gi, '_')
        : 'Cliente';

    const filename = `${safeClientName}_Challenge_${datetime}.md`;

    const blob = new Blob([fullContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getActiveNarrative = () => {
    switch (activeTab) {
      case 'challenger':
        return data.interpretation_challenger;
      case 'consultive':
        return data.interpretation_consultive;
      case 'mixed':
      default:
        return data.interpretation_mixed;
    }
  };

  const TAB_LABELS: Record<NarrativeTab, string> = {
    challenger: 'Challenger',
    consultive: 'Consultiva',
    mixed: 'Mixta',
  };

  return (
    <div className="flex flex-col h-full animate-fadeIn pb-12">
      {/* Cabecera de resultado */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-gray-200 pb-6 mb-8">
        <div>
          <div className="flex items-center space-x-2 text-brand-teal mb-2">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm font-bold uppercase tracking-widest">
              Análisis completado
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-heading font-bold text-brand-dark tracking-tight">
            Núcleo del Reto Estratégico
          </h1>
          <p className="text-brand-text text-sm mt-1">
            Generado para:{' '}
            <span className="font-semibold">
              {clientName || 'Cliente confidencial'}
            </span>
          </p>
          <p className="text-[11px] text-brand-text mt-1">
            Lectura generada por el motor Maxicomm CSO (Gemini 3 Pro) a partir
            del diagnóstico inicial.
          </p>
        </div>
        <div className="flex space-x-3 mt-4 md:mt-0">
          <button
            onClick={handleExport}
            className="flex items-center space-x-2 bg-white border border-brand-teal text-brand-teal hover:bg-slate-50 font-heading font-semibold text-xs uppercase tracking-wider px
