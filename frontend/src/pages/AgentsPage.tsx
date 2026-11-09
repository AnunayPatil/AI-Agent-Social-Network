import React, { useState, useEffect } from 'react';
import {
  Bot,
  BrainCircuit,
  Pause,
  Play,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  Search,
  BookOpen,
  X,
  ExternalLink,
  Globe2,
  Sparkles
} from 'lucide-react';
import { Agent } from '../types';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const navigate = useNavigate();

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const data = await api.getAgents();
      setAgents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleTogglePause = async (agent: Agent) => {
    try {
      await api.toggleAgentPause(agent.id);
      await fetchAgents();
    } catch (e) {
      console.error(e);
    }
  };

  const getStatusBadge = (status: string, isPaused?: boolean) => {
    if (isPaused) {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1">
          <Pause className="w-2.5 h-2.5" /> Paused
        </span>
      );
    }
    switch (status) {
      case 'Active':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5" /> Active
          </span>
        );
      case 'Testing':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30 flex items-center gap-1">
            <Clock className="w-2.5 h-2.5 animate-spin" /> Testing
          </span>
        );
      case 'Pending':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-500/10 text-slate-400 border border-slate-500/30">
            Pending
          </span>
        );
      case 'Failed':
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1">
            <AlertTriangle className="w-2.5 h-2.5" /> Failed
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-500/10 text-slate-400 border border-slate-500/30">
            {status}
          </span>
        );
    }
  };

  const filtered = agents.filter((a) => {
    if (statusFilter === 'All') return true;
    return a.status === statusFilter;
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-cyan-400" />
            <span>AI Agent Registry & Management Dashboard</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Monitor autonomous company agents, inspect custom Gemini system prompts, and configure pause controls.
          </p>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          {['All', 'Active', 'Testing', 'Pending', 'Failed'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                statusFilter === st
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading AI agents...</div>
      ) : filtered.length === 0 ? (
        <div className="py-12 text-center text-xs text-slate-500 bg-[#0F1424] rounded-2xl border border-slate-800">
          No agents found with status "{statusFilter}".
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((agent) => (
            <div
              key={agent.id}
              className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600/30 to-indigo-600/30 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-white">{agent.identity_name}</h4>
                      <span className="text-xs text-slate-400 block font-mono">{agent.company_name}</span>
                    </div>
                  </div>
                  {getStatusBadge(agent.status, agent.is_paused)}
                </div>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-1.5 text-xs text-slate-300">
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Role:</span>
                    <span className="text-cyan-400 truncate max-w-[150px]">{agent.role}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Relevance Threshold:</span>
                    <span className="text-white font-bold">{((agent.relevance_threshold || 0.55) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Autonomous Mode:</span>
                    <span className={agent.is_paused ? 'text-amber-400' : 'text-emerald-400 font-semibold'}>
                      {agent.is_paused ? 'Suspended' : 'Live & Active'}
                    </span>
                  </div>
                </div>

                {agent.research_topics && agent.research_topics.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {agent.research_topics.slice(0, 3).map((topic, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded text-[9px] bg-slate-900 text-slate-400 border border-slate-800">
                        #{topic}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <button
                  onClick={() => setSelectedAgent(agent)}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-xs text-slate-200 transition-all flex items-center gap-1 cursor-pointer"
                >
                  <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Instructions</span>
                </button>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => navigate(`/testing?agentId=${agent.id}`)}
                    className="p-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20 transition-all cursor-pointer"
                    title="Test Agent Comprehension"
                  >
                    <BrainCircuit className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleTogglePause(agent)}
                    className={`p-1.5 rounded-lg transition-all cursor-pointer border ${
                      agent.is_paused
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30 hover:bg-amber-500/20'
                    }`}
                    title={agent.is_paused ? 'Resume Agent' : 'Pause Agent'}
                  >
                    {agent.is_paused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* System Instructions Drawer Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-[#0F1424] border border-slate-700 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl p-6 space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <Bot className="w-5 h-5 text-cyan-400" />
                <div>
                  <h3 className="font-bold text-sm text-white">{selectedAgent.identity_name}</h3>
                  <span className="text-[11px] text-slate-400 font-mono">Gemini Enterprise System Instructions</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedAgent(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 rounded-xl bg-slate-950/80 border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
              {selectedAgent.system_instructions}
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-500">Autonomous LLM persona compiled during Stage 1</span>
              <button
                onClick={() => setSelectedAgent(null)}
                className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-all cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
