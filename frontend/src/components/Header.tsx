import React from 'react';
import { Sparkles, Activity, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onOpenDemo: () => void;
  activeCount?: number;
}

export const Header: React.FC<HeaderProps> = ({ onOpenDemo, activeCount = 3 }) => {
  return (
    <header className="h-16 bg-[#0E1322]/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between z-10 sticky top-0">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-medium font-mono text-[11px]">{activeCount} AI Agents Live & Autonomous</span>
        </div>
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px] font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span>Gemini & LangGraph Orchestrated</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onOpenDemo}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-medium text-xs shadow-md shadow-cyan-500/20 transition-all cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5 animate-spin-slow" />
          <span>Launch 15-Step E2E Demo</span>
        </button>
      </div>
    </header>
  );
};
