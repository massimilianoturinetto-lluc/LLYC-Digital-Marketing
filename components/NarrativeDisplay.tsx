import React, { useEffect, useRef } from 'react';
import { HistoryEntry } from '../types';

interface NarrativeDisplayProps {
  history: HistoryEntry[];
  isTyping: boolean;
}

const NarrativeDisplay: React.FC<NarrativeDisplayProps> = ({ history, isTyping }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history, isTyping]);

  const hasHistory = history && history.length > 0;

  const renderText = (text: string) =>
    text.split('\n').map((line, idx) => (
      <p key={idx} className="mb-1 last:mb-0">
        {line}
      </p>
    ));

  return (
    <div className="flex flex-col h-full overflow-hidden bg-white border border-gray-100 rounded-2xl shadow-soft">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-slate-50 rounded-t-2xl">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-brand-teal animate-pulse" />
          <div>
            <span className="block text-xs font-heading text-brand-dark uppercase tracking-widest">
              Diálogo con el motor estratégico
            </span>
            <span className="block text-[11px] text-brand-text">
              Conversación entre el equipo y Maxicomm CSO (IA).
            </span>
          </div>
        </div>
      </div>

      {/* Body */}
      <div
        ref={sc
