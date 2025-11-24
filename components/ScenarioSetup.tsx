import React, { useState, useRef, FormEvent, ChangeEvent } from 'react';
import { ScenarioConfig } from '../types';

interface ScenarioSetupProps {
  onStart: (config: ScenarioConfig) => void;
  isLoading: boolean;
}

const ScenarioSetup: React.FC<ScenarioSetupProps> = ({ onStart, isLoading }) => {
  const [config, setConfig] = useState<ScenarioConfig>({
    clientName: '',
    rawContext: '',
    files: [],
    opportunityType: '',
    mediaRole: '',
    digitalMaturity: '',
  });

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmedConfig: ScenarioConfig = {
      ...config,
      clientName: config.clientName.trim(),
      rawContext: config.rawContext.trim(),
    };
    if (!isValid(trimmedConfig)) return;
    onStart(trimmedConfig);
  };

  const isValid = (c: ScenarioConfig = config) =>
    c.clientName.trim().length > 0 && c.rawContext.trim().length > 0;

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setConfig((prev) => ({
        ...prev,
        files: [...prev.files, ...newFiles],
      }));
      // reset para poder volver a subir el mismo archivo si hace falta
      e.target.value = '';
    }
  };

  const removeFile = (index: number) => {
    setConfig((prev) => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index),
    }));
  };

  const handleSkip = () => {
    onStart({
      ...config,
      clientName: config.clientName.trim() || 'Cliente confidencial',
      rawContext:
        config.rawContext.trim() ||
        'Reto estratégico estándar para evaluar oportunidades desde medios, datos y adtech.',
      opportunityType: config.opportunityType || 'newbiz',
      mediaRole: config.mediaRole || 'mixed',
      digitalMaturity: config.digitalMaturity || 'mid',
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 animate-fadeIn">
      {/* Nombre del cliente */}
      <div>
        <label className="block text-sm font-semibold text-brand-dark mb-2">
          Nombre del Cliente <span className="text-brand-red">*</span>
        </label>
        <input
          type="text"
          className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-brand-dark focus:outline-none focus:border-brand-teal focus:ring-1 focus:ring-brand-teal transition-all placeholder-gray-400"
          placeholder="e.g., Acme Corp, LLYC Foundation"
          value={config.clientName}
          onChange={(e) =>
            setConfig((prev) => ({ ...prev, clientName: e.target.value }))
          }
        />
      </div>

      {/* Contexto en bruto */}
      <div>
        <label className="block text-sm font-semibold text-brand-dark mb-2">
          Contexto en bruto (notas, briefing o inputs desordenados){' '}
          <span className="text-brand-red">*</span>
        </label>
        <textarea
          className="w-full h-40 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-brand-dark focus:outline-none focus:border-brand-teal focus:ring-1 focus:ring-brand-teal transition-all placeholder-gray-400 resize-y"
          placeholder="Pega aquí notas de reunión, briefing o cualquier contexto desordenado que quieras que la IA ordene."
          value={config.rawContext}
          onChange={(e) =>
            setConfig((prev) => ({ ...prev, rawContext: e.target.value }))
          }
        />
        <p className="mt-1 text-xs text-brand-text">
          Incluye: contexto de negocio, rol de medios, retos actuales de data y
          medición, plazos y restricciones relevantes.
        </p>
      </div>

      {/* Archivos adjuntos */}
      <div>
        <label className="block text-sm font-semibold text-brand-dark mb-2">
          Archivos adjuntos (PDF, DOCX, PPTX, TXT, imágenes o vídeo)
        </label>
        <div className="flex flex-col space-y-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-brand-teal hover:bg-slate-50 transition-colors"
          >
            <input
              type="file"
              ref={fileInputRef}
              multiple
              accept=".pdf,.docx,.pptx,.txt,.jpg,.jpeg,.png,.mp4"
              className="hidden"
              onChange={handleFileChange}
            />
            <span className="text-brand-teal font-semibold text-sm">
              Haz clic para subir archivos
            </span>
            <p className="text-xs text-brand-text mt-1">
              Opcional: briefing, presentaciones, flujos, capturas, etc.
            </p>
          </button>

          {config.files.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {config.files.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center bg-gray-100 rounded-full pl-3 pr-2 py-1 text-xs text-gray-700 border border-gray-200"
                >
                  <span className="max-w-[180px] truncate mr-2">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(idx)}
                    className="w-5 h-5 flex items-center justify-center rounded-full bg-gray-300 hover:bg-gray-400 text-white transition-colors"
                    aria-label={`Eliminar archivo ${file.name}`}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Selects */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-semibold text-brand-dark mb-2">
            Tipo de oportunidad
          </label>
          <select
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-brand-dark focus:outline-none focus:border-brand-teal focus:ring-1 focus:ring-brand-teal appearance-none"
            value={config.opportunityType}
            onChange={(e) =>
              setConfig((prev) => ({ ...prev, opportunityType: e.target.value }))
            }
          >
            <option value="">Seleccionar…</option>
            <option value="newbiz">Newbiz</option>
            <option value="upsell">Upsell</option>
            <option value="cross-sell">Cross-sell</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-brand-dark mb-2">
            Rol prioritario de medios
          </label>
          <select
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-brand-dark focus:outline-none focus:border-brand-teal focus:ring-1 focus:ring-brand-teal appearance-none"
            value={config.mediaRole}
            onChange={(e) =>
              setConfig((prev) => ({ ...prev, mediaRole: e.target.value }))
            }
          >
            <option value="">Seleccionar…</option>
            <option value="brand">Brand</option>
            <option value="performance">Performance</option>
            <option value="retail">Retail</option>
            <option value="mixed">Mixto</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-brand-dark mb-2">
            Madurez digital del cliente
          </label>
          <select
            className="w-full bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 text-brand-dark focus:outline-none focus:border-brand-teal focus:ring-1 focus:ring-brand-teal appearance-none"
            value={config.digitalMaturity}
            onChange={(e) =>
              setConfig((prev) => ({
                ...prev,
                digitalMaturity: e.target.value,
              }))
            }
          >
            <option value="">Seleccionar…</option>
            <option value="low">Baja</option>
            <option value="mid">Media</option>
            <option value="high">Alta</option>
          </select>
        </div>
      </div>

      {/* Botones */}
      <div className="pt-6 border-t border-gray-100 flex flex-col items-end gap-2">
        <button
          type="submit"
          disabled={isLoading || !isValid()}
          className="bg-brand-red text-white font-heading font-semibold text-base rounded-full px-8 py-3 hover:bg-[#D63E56] transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Formular el reto
        </button>
        <button
          type="button"
          className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
          onClick={handleSkip}
        >
          Omitir este paso (usar valores por defecto)
        </button>
      </div>
    </form>
  );
};

export default ScenarioSetup;
