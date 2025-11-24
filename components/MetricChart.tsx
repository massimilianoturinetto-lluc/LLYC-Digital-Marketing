import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import { Metric } from '../types';

interface MetricChartProps {
  metrics: Metric[];
  title?: string;
  description?: string;
}

const MetricChart: React.FC<MetricChartProps> = ({
  metrics,
  title = 'Indicadores estratégicos',
  description = 'Lectura rápida del estado del reto desde la perspectiva de medios y datos.',
}) => {
  // Normalizamos y acotamos valores (0–100) para evitar cosas raras
  const safeMetrics = useMemo(
    () =>
      (metrics || []).map((m) => ({
        ...m,
        value: Math.max(0, Math.min(100, Number.isFinite(m.value) ? m.value : 0)),
      })),
    [metrics],
  );

  const hasData = safeMetrics.length > 0;

  return (
    <div className="w-full bg-white rounded-2xl shadow-soft border border-gray-100 p-5 md:p-6">
      <div className="flex items-baseline justify-between mb-4 gap-2">
        <div>
          <h3 className="text-sm md:text-base font-heading font-semibold text-brand-dark">
            {title}
          </h3>
          {description && (
            <p className="text-xs md:text-sm text-brand-text mt-1">
              {description}
            </p>
          )}
        </div>
      </div>

      {!hasData ? (
        <p className="text-xs md:text-sm text-brand-grey italic">
          Aún no hay indicadores disponibles. Primero formula el reto y genera
          el análisis para visualizar el impacto estratégico.
        </p>
      ) : (
        <div className="h-64 md:h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={safeMetrics}
              layout="vertical"
              margin={{ top: 10, right: 24, left: 40, bottom: 10 }}
            >
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis
                dataKey="name"
                type="category"
                tick={{
                  fill: '#6D7475', // brand-text
                  fontSize: 11,
                  fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Open Sans", sans-serif',
                }}
                width={120}
              />
              <Tooltip
                cursor={{ fill: 'rgba(148, 163, 184, 0.08)' }}
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderColor: '#E2E8F0',
                  borderRadius: 12,
                  boxShadow: '0 8px 24px rgba(15, 23, 42, 0.08)',
                  color: '#0A263B',
                  fontSize: 12,
                }}
                labelStyle={{ fontWeight: 600, color: '#0A263B' }}
                formatter={(value: number) => [`${value.toFixed(0)} / 100`, 'Nivel']}
              />
              <Bar dataKey="value" barSize={12} radius={[0, 6, 6, 0]}>
                {safeMetrics.map((entry, index) => {
                  // Semáforo adaptado a la lógica de madurez media/data
                  let color = '#36A7B7'; // brand-teal (correcto/bueno)
                  if (entry.value < 40) color = '#F54963'; // brand-red (crítico)
                  else if (entry.value >= 40 && entry.value <= 70) color = '#B0B8BA'; // brand-grey (zona media)

                  return <Cell key={`cell-${index}`} fill={color} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default MetricChart;
