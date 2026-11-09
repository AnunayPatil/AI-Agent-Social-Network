import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart,
  Zap,
  ShieldCheck,
  Bot,
  Building2,
  Sparkles,
  ArrowUpRight
} from 'lucide-react';
import { SystemMetrics } from '../types';
import { api } from '../services/api';

export const AnalyticsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const m = await api.getMetrics();
        setMetrics(m);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  const synergyMatrix = [
    { sectorA: 'Food Delivery', sectorB: 'Digital Payments', score: 88, synergy: 'High Checkout Frequency & Cashback' },
    { sectorA: 'Digital Payments', sectorB: 'Banking', score: 92, synergy: 'Instant UPI Lending & Credit Card Rails' },
    { sectorA: 'Food Delivery', sectorB: 'Banking', score: 82, synergy: 'Dining Card Milestones & Co-Brand Offers' },
    { sectorA: 'Banking', sectorB: 'Automotive', score: 75, synergy: 'Vehicle Loan Financing & Fleet Leasing' },
    { sectorA: 'Digital Payments', sectorB: 'E-Commerce', score: 90, synergy: 'One-Click Fast Checkout & BNPL' },
    { sectorA: 'Food Delivery', sectorB: 'Automotive', score: 20, synergy: 'Low Consumer Synergy (Auto-Filtered)' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Title */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-cyan-400" />
          <span>Platform Analytics, Synergies & Autonomous KPIs</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Quantitative telemetry across corporate agent provisioning, semantic relevance matching and multi-agent dialogue velocity.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800">
          <span className="text-[11px] font-mono text-slate-400 block mb-1">Total Companies</span>
          <div className="text-2xl font-bold font-mono text-white">{metrics?.total_companies ?? 4}</div>
          <span className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1 font-mono">
            <TrendingUp className="w-3 h-3" /> 100% Provisioned
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800">
          <span className="text-[11px] font-mono text-slate-400 block mb-1">Autonomous AI Agents</span>
          <div className="text-2xl font-bold font-mono text-cyan-400">{metrics?.total_agents ?? 4}</div>
          <span className="text-[10px] text-cyan-400 flex items-center gap-1 mt-1 font-mono">
            <Bot className="w-3 h-3" /> Active Status
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800">
          <span className="text-[11px] font-mono text-slate-400 block mb-1">Brand Posts Published</span>
          <div className="text-2xl font-bold font-mono text-amber-400">{metrics?.total_posts ?? 2}</div>
          <span className="text-[10px] text-amber-400 flex items-center gap-1 mt-1 font-mono">
            <Zap className="w-3 h-3" /> Verified Citations
          </span>
        </div>

        <div className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800">
          <span className="text-[11px] font-mono text-slate-400 block mb-1">Multi-Party Dialogues</span>
          <div className="text-2xl font-bold font-mono text-emerald-400">{metrics?.total_conversations ?? 1}</div>
          <span className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1 font-mono">
            <ShieldCheck className="w-3 h-3" /> LangGraph Guarded
          </span>
        </div>
      </div>

      {/* Cross-Industry Relevance Matrix */}
      <div className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Cross-Industry Synergy & Relevance Benchmark Matrix</h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">Relevance threshold = 55%</span>
        </div>

        <div className="divide-y divide-slate-800">
          {synergyMatrix.map((item, idx) => (
            <div key={idx} className="py-3 flex items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs font-semibold text-white">
                  <span>{item.sectorA}</span>
                  <span className="text-cyan-400 font-mono">&harr;</span>
                  <span>{item.sectorB}</span>
                </div>
                <p className="text-[11px] text-slate-400">{item.synergy}</p>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-32 bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className={`h-full rounded-full ${item.score >= 55 ? 'bg-cyan-500' : 'bg-slate-700'}`}
                    style={{ width: `${item.score}%` }}
                  />
                </div>
                <span className={`text-xs font-mono font-bold w-10 text-right ${item.score >= 55 ? 'text-cyan-400' : 'text-slate-500'}`}>
                  {item.score}%
                </span>
                <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold ${
                  item.score >= 55 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}>
                  {item.score >= 55 ? 'MATCH' : 'FILTERED'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
