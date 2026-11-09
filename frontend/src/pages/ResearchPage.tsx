import React, { useState, useEffect } from 'react';
import {
  Globe2,
  Bot,
  Play,
  CheckCircle2,
  ExternalLink,
  Loader2,
  Hash,
  Sparkles,
  FileText,
  Flame,
  ArrowRight
} from 'lucide-react';
import { Agent, ResearchResult } from '../types';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const ResearchPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [targetUrl, setTargetUrl] = useState<string>('https://swiggy.com/news/festive-discount-2026');
  const [autoPost, setAutoPost] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [latestResult, setLatestResult] = useState<ResearchResult | null>(null);
  const [results, setResults] = useState<ResearchResult[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agList, allRes] = await Promise.all([
          api.getAgents('Active'),
          api.getAllResearch()
        ]);
        setAgents(agList);
        if (agList.length > 0) setSelectedAgentId(agList[0].id);
        setResults(allRes);
      } catch (e) {
        console.error(e);
      }
    };
    fetchData();
  }, []);

  const handleRunResearch = async () => {
    if (!selectedAgentId) return;
    setLoading(true);
    setLatestResult(null);

    try {
      const res = await api.runResearch(selectedAgentId, {
        source_url_override: targetUrl || undefined,
        auto_generate_post: autoPost
      });
      setLatestResult(res);
      const updated = await api.getAllResearch();
      setResults(updated);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Title */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Globe2 className="w-5 h-5 text-cyan-400" />
          <span>Stage 2: Autonomous Web Research & Content Extraction Lab</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Agent web scraping via BeautifulSoup, noise and ad removal, text normalization, deduplication, and Gemini post synthesis.
        </p>
      </div>

      {/* Control Panel */}
      <div className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Select Researching AI Agent</label>
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
            <label className="block text-xs font-semibold text-slate-300 mb-1">Target Intelligence URL</label>
            <input
              type="text"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="e.g. https://news.google.com/... or company blog URL"
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
            <input
              type="checkbox"
              checked={autoPost}
              onChange={(e) => setAutoPost(e.target.checked)}
              className="w-4 h-4 rounded text-cyan-500 focus:ring-0 bg-slate-900 border-slate-700"
            />
            <span>Automatically synthesize and publish Gemini brand post to Social Feed</span>
          </label>

          <button
            onClick={handleRunResearch}
            disabled={loading || !selectedAgentId}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-xs shadow-md shadow-cyan-500/20 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Scraping & Synthesizing...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Start Autonomous Research</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Latest Research Extraction Result */}
      {latestResult && (
        <div className="p-6 rounded-2xl bg-[#0F1424] border border-cyan-500/40 space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Extracted Intelligence & Synthesis</h3>
            </div>
            <span className="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Cleaned & Deduplicated
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-[11px] font-mono text-slate-400 block mb-1">Article Headline:</span>
              <h4 className="text-sm font-semibold text-white">{latestResult.title}</h4>
            </div>

            <div>
              <span className="text-[11px] font-mono text-cyan-400 block mb-1">Structured Summary:</span>
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 leading-relaxed">
                {latestResult.summary}
              </div>
            </div>

            <div>
              <span className="text-[11px] font-mono text-slate-400 block mb-1">Extracted NLP Topics:</span>
              <div className="flex flex-wrap gap-1.5">
                {latestResult.extracted_topics.map((t, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md text-[10px] bg-slate-800 text-cyan-300 font-mono border border-slate-700">
                    #{t}
                  </span>
                ))}
              </div>
            </div>

            {latestResult.post_id && (
              <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-800/50 flex items-center justify-between">
                <span className="text-xs text-indigo-300 font-medium">
                  Brand post successfully synthesized and published to Social Feed!
                </span>
                <button
                  onClick={() => navigate('/feed')}
                  className="px-3 py-1 rounded-lg bg-indigo-500 hover:bg-indigo-400 text-white font-semibold text-xs flex items-center gap-1 cursor-pointer"
                >
                  <span>View Post</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Global Extracted Research Stream */}
      <div className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-400" />
          <span>Extracted Research Intelligence Archives</span>
        </h3>

        {results.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">
            No research extractions recorded yet. Trigger research above!
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {results.map((res) => (
              <div key={res.id} className="py-4 space-y-2">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="text-xs font-semibold text-white">{res.title}</h4>
                    <span className="text-[11px] font-mono text-cyan-400">Agent: {res.agent_name}</span>
                  </div>
                  <a
                    href={res.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-cyan-400 hover:text-cyan-300 text-[11px] font-mono flex items-center gap-1 shrink-0"
                  >
                    <span>Source</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">{res.summary}</p>
                <div className="flex flex-wrap gap-1">
                  {res.extracted_topics.map((t, idx) => (
                    <span key={idx} className="px-1.5 py-0.5 rounded text-[9px] bg-slate-900 text-slate-400 border border-slate-800">
                      #{t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
