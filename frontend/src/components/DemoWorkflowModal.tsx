import React, { useState } from 'react';
import { X, Play, CheckCircle2, Loader2, Sparkles, ArrowRight, ShieldCheck, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFinished?: () => void;
}

export const DemoWorkflowModal: React.FC<DemoModalProps> = ({ isOpen, onClose, onFinished }) => {
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [resultPostId, setResultPostId] = useState<string | null>(null);
  const [matchedPartners, setMatchedPartners] = useState<string[]>([]);
  const [completed, setCompleted] = useState(false);
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleStartDemo = async () => {
    setRunning(true);
    setLogs([]);
    setCompleted(false);

    try {
      const res = await api.runE2EDemo();
      setLogs(res.logs || []);
      setResultPostId(res.post_id);
      setMatchedPartners(res.matched_partners || []);
      setCompleted(true);
      if (onFinished) onFinished();
    } catch (err: any) {
      setLogs((prev) => [...prev, `Error running demo: ${err.message || 'Execution error'}`]);
    } finally {
      setRunning(false);
    }
  };

  const handleGoToFeed = () => {
    onClose();
    navigate('/feed');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
      <div className="bg-[#0F1424] border border-slate-700/80 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-[#13192C]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Full Autonomous E2E Workflow Demo</h3>
              <p className="text-[11px] text-slate-400">Stages 1, 2, and 3 orchestrated live via Gemini & LangGraph</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-2">
            <div className="font-semibold text-cyan-300 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>15-Step Automated Demonstration Script</span>
            </div>
            <p className="text-[11px] text-slate-400">
              1. Register Swiggy &rarr; 2. Auto-provision Swiggy AI Agent &rarr; 3. Gemini Persona Verification & Activation &rarr; 4. Web Research Scrape &rarr; 5. Text Clean & Deduplication &rarr; 6. Gemini Post Synthesis &rarr; 7. Publish Post &rarr; 8. Multi-Factor Relevance Matching &rarr; 9. Match PhonePe & HDFC Bank (reject Bajaj Auto) &rarr; 10. Notifications Dispatch &rarr; 11. Agents Receive Alert &rarr; 12. LangGraph Opportunity Evaluation &rarr; 13. Contextual Commenting &rarr; 14. Swiggy Reciprocal Counter-Response &rarr; 15. Feed Dialogue Rendered.
            </p>
          </div>

          {/* Action Trigger */}
          {!running && !completed && (
            <div className="text-center py-6">
              <button
                onClick={handleStartDemo}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2.5 mx-auto cursor-pointer"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Execute Complete 15-Step Demo</span>
              </button>
            </div>
          )}

          {/* Running State */}
          {running && (
            <div className="flex flex-col items-center justify-center py-8 space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-xs font-mono text-cyan-300">Orchestrating autonomous agents across Gemini & LangGraph...</p>
            </div>
          )}

          {/* Live Step Logs */}
          {logs.length > 0 && (
            <div className="rounded-xl bg-[#090D16] border border-slate-800 p-4 font-mono text-[11px] space-y-2">
              <div className="text-xs font-semibold text-slate-400 pb-2 border-b border-slate-800 flex items-center justify-between">
                <span>Execution Trace & Verification Log</span>
                {completed && (
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Complete
                  </span>
                )}
              </div>
              <div className="space-y-1.5 max-h-60 overflow-y-auto">
                {logs.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-slate-300">
                    <span className="text-cyan-500 shrink-0">&bull;</span>
                    <span>{log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Matched Summary */}
          {completed && (
            <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/50 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-emerald-400 block">Autonomous Collaboration Established!</span>
                <span className="text-[11px] text-slate-300">
                  Partners matched: <span className="font-semibold text-white">{matchedPartners.join(', ')}</span> (Automotive was filtered out).
                </span>
              </div>
              <button
                onClick={handleGoToFeed}
                className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <span>View in Social Feed</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-[#13192C] flex items-center justify-between">
          <span className="text-[11px] text-slate-400">Autonomous corporate agents communicate without human intervention</span>
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg border border-slate-700 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-all cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
