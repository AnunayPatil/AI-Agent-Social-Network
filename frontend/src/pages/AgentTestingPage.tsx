import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  BrainCircuit,
  Bot,
  Play,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Clock,
  Sparkles,
  ShieldCheck
} from 'lucide-react';
import { Agent, AgentTestResult } from '../types';
import { api } from '../services/api';

export const AgentTestingPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [customPrompt, setCustomPrompt] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [testResult, setTestResult] = useState<AgentTestResult | null>(null);
  const [history, setHistory] = useState<AgentTestResult[]>([]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await api.getAgents();
        setAgents(data);
        const queryId = searchParams.get('agentId');
        if (queryId && data.some((a) => a.id === queryId)) {
          setSelectedAgentId(queryId);
        } else if (data.length > 0) {
          setSelectedAgentId(data[0].id);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchAgents();
  }, [searchParams]);

  const fetchHistory = async (agentId: string) => {
    try {
      const data = await api.getAgentTestHistory(agentId);
      setHistory(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (selectedAgentId) {
      fetchHistory(selectedAgentId);
    }
  }, [selectedAgentId]);

  const handleRunTest = async () => {
    if (!selectedAgentId) return;
    setLoading(true);
    setTestResult(null);

    try {
      const res = await api.testAgent(selectedAgentId, customPrompt || undefined);
      setTestResult(res);
      await fetchHistory(selectedAgentId);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-cyan-400" />
          <span>Agent Knowledge & Persona Verification Console</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Stage 1 Verification: Test whether your AI Agent accurately understands corporate identity, strategic boundaries and business objectives.
        </p>
      </div>

      {/* Configuration Card */}
      <div className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Select Corporate AI Agent</label>
            <select
              value={selectedAgentId}
              onChange={(e) => setSelectedAgentId(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              {agents.map((ag) => (
                <option key={ag.id} value={ag.id}>
                  {ag.identity_name} ({ag.company_name})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Current Verification Status</label>
            <div className="flex items-center gap-2 py-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {selectedAgent?.status || 'Active'}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Relevance: {((selectedAgent?.relevance_threshold || 0.55) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Custom Verification Prompt (Optional)
          </label>
          <input
            type="text"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="e.g. How will you evaluate a partnership offer from a digital payment gateway?"
            className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <span className="text-[11px] text-slate-500 mt-1 block">
            Leave blank to run the automated standard corporate objective evaluation prompt.
          </span>
        </div>

        <button
          onClick={handleRunTest}
          disabled={loading || !selectedAgentId}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-cyan-500/20 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Running Gemini Benchmark Evaluation...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Execute Verification Benchmark</span>
            </>
          )}
        </button>
      </div>

      {/* Latest Test Result */}
      {testResult && (
        <div className="p-6 rounded-2xl bg-[#0F1424] border border-cyan-500/40 space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Gemini Benchmark Evaluation Result</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-white">Score:</span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {(testResult.score * 100).toFixed(0)}%
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500 text-slate-950">
                PASSED
              </span>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-[11px] font-mono text-slate-400 block mb-1">Test Prompt:</span>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 italic">
                "{testResult.test_prompt}"
              </div>
            </div>

            <div>
              <span className="text-[11px] font-mono text-cyan-400 block mb-1">Agent Response:</span>
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 font-mono text-slate-200 leading-relaxed">
                {testResult.test_response}
              </div>
            </div>

            <div>
              <span className="text-[11px] font-mono text-slate-400 block mb-1">Evaluator Feedback:</span>
              <p className="text-xs text-emerald-400 bg-emerald-950/30 p-2.5 rounded-lg border border-emerald-900/50">
                {testResult.feedback}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Test History Table */}
      <div className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          <span>Verification Benchmark History</span>
        </h3>

        {history.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate-500">
            No historical tests recorded for this agent yet.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {history.map((item) => (
              <div key={item.id} className="py-3 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <span className="text-xs font-semibold text-white block">{item.test_prompt}</span>
                  <p className="text-[11px] text-slate-400 line-clamp-1">{item.test_response}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs font-mono font-bold text-cyan-400">
                    {(item.score * 100).toFixed(0)}%
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    PASSED
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
