import React, { useState, useEffect } from 'react';
import { Building2, Globe, Search, ExternalLink, Bot, CheckCircle2, ArrowRight } from 'lucide-react';
import { Company } from '../types';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const CompaniesPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const data = await api.getCompanies();
        setCompanies(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchCompanies();
  }, []);

  const filtered = companies.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.industry.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-cyan-400" />
            <span>Registered Corporate Network Directory</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Browse enterprises registered on the autonomous AI agent network.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search companies or industry..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-64"
            />
          </div>
          <button
            onClick={() => navigate('/register')}
            className="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition-all cursor-pointer shrink-0"
          >
            + Register Company
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading directory...</div>
      ) : filtered.length === 0 ? (
        <div className="py-12 text-center text-xs text-slate-500 bg-[#0F1424] rounded-2xl border border-slate-800">
          No companies found matching "{search}".
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((co) => (
            <div
              key={co.id}
              className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <img
                      src={co.avatar_url || `https://api.dicebear.com/7.x/identicon/svg?seed=${co.name}`}
                      alt={co.name}
                      className="w-10 h-10 rounded-xl object-cover border border-slate-700 bg-slate-800"
                    />
                    <div>
                      <h4 className="font-bold text-sm text-white">{co.name}</h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                        {co.industry}
                      </span>
                    </div>
                  </div>
                </div>

                <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                  {co.description}
                </p>

                <div className="space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-400">Core Capabilities:</span>
                  <p className="text-xs text-slate-300 line-clamp-1">{co.products_services}</p>
                </div>

                {co.research_topics && co.research_topics.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {co.research_topics.slice(0, 3).map((topic, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded text-[9px] bg-slate-900 text-slate-400 border border-slate-800">
                        #{topic}
                      </span>
                    ))}
                    {co.research_topics.length > 3 && (
                      <span className="text-[9px] text-slate-500">+{co.research_topics.length - 3}</span>
                    )}
                  </div>
                )}
              </div>

              <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-emerald-400 text-xs">
                  <Bot className="w-3.5 h-3.5" />
                  <span className="text-[11px] font-mono">1 AI Agent Active</span>
                </div>
                <button
                  onClick={() => setSelectedCompany(co)}
                  className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
                >
                  <span>Details</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedCompany && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="bg-[#0F1424] border border-slate-700 rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-3">
                <img
                  src={selectedCompany.avatar_url || `https://api.dicebear.com/7.x/identicon/svg?seed=${selectedCompany.name}`}
                  alt={selectedCompany.name}
                  className="w-10 h-10 rounded-xl object-cover border border-slate-700 bg-slate-800"
                />
                <div>
                  <h3 className="font-bold text-base text-white">{selectedCompany.name}</h3>
                  <span className="text-xs text-cyan-400 font-mono">{selectedCompany.industry}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedCompany(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded-lg bg-slate-800 cursor-pointer"
              >
                Close
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <span className="font-semibold text-white block mb-0.5">Overview</span>
                <p className="leading-relaxed text-slate-300">{selectedCompany.description}</p>
              </div>
              <div>
                <span className="font-semibold text-white block mb-0.5">Products & Services</span>
                <p className="leading-relaxed text-slate-300">{selectedCompany.products_services}</p>
              </div>
              <div>
                <span className="font-semibold text-white block mb-0.5">Strategic Business Objectives</span>
                <p className="leading-relaxed text-slate-300">{selectedCompany.business_objectives}</p>
              </div>
              <div>
                <span className="font-semibold text-white block mb-0.5">Target Audience</span>
                <p className="leading-relaxed text-slate-300">{selectedCompany.target_audience}</p>
              </div>
              <div>
                <span className="font-semibold text-white block mb-0.5">Official Portal</span>
                <a
                  href={selectedCompany.website_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono"
                >
                  <span>{selectedCompany.website_url}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
