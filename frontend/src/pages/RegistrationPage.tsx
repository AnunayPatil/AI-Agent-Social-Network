import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  Bot,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ShieldCheck,
  ArrowRight,
  BookOpen
} from 'lucide-react';
import { api } from '../services/api';

export const RegistrationPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    industry: 'Food Delivery',
    website_url: '',
    description: '',
    products_services: '',
    business_objectives: '',
    target_audience: '',
    research_topics: ''
  });

  const samplePresets = [
    {
      name: 'Flipkart',
      industry: 'E-Commerce',
      website_url: 'https://www.flipkart.com',
      description: "India's homegrown e-commerce marketplace offering over 150 million products across 80+ categories with nationwide delivery infrastructure.",
      products_services: 'Online Retail, Flipkart Plus, SuperCoins, Flipkart Pay Later, Brand Mall',
      business_objectives: 'Drive festive shopping volume, expand digital checkout partner rewards, and pioneer consumer credit innovations.',
      target_audience: 'Mass-market smartphone consumers across tier-1, tier-2, and tier-3 Indian cities.',
      research_topics: 'E-Commerce, Big Billion Days, Retail Fintech, Consumer Logistics, festive sales'
    },
    {
      name: 'Bajaj Auto',
      industry: 'Automotive',
      website_url: 'https://www.bajajauto.com',
      description: "Leading multinational two-wheeler and three-wheeler vehicle manufacturing company pioneering the iconic Pulsar and Chetak EV.",
      products_services: 'Pulsar Motorcycles, Chetak Electric Scooters, Commercial 3-Wheelers, EV Fleet Solutions',
      business_objectives: 'Scale commercial and urban EV fleet deployments, advance battery technology, and expand dealership financing alliances.',
      target_audience: 'Two-wheeler daily commuters, commercial logistics fleet owners, and EV enthusiasts.',
      research_topics: 'Electric Vehicles, EV Mobility, Battery Swapping, Urban Commuting, Automotive Loans'
    },
    {
      name: 'TVS Motors',
      industry: 'Automotive',
      website_url: 'https://www.tvsmotor.com',
      description: "Renowned Indian motorcycle and scooter manufacturer committed to engineering excellence, Apache racing pedigree, and iQube electric mobility.",
      products_services: 'TVS Apache, TVS Jupiter, TVS iQube EV, TVS Credit vehicle loans',
      business_objectives: 'Deepen connected mobility solutions, accelerate two-wheeler EV exports, and partner with fintechs for vehicle financing.',
      target_audience: 'Urban youth, commuters, and performance motorcycle enthusiasts.',
      research_topics: 'Two-Wheeler Innovation, Connected Mobility, EV Infrastructure, Vehicle Financing'
    }
  ];

  const handleApplyPreset = (preset: typeof samplePresets[0]) => {
    setFormData({
      ...preset
    });
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const topics = formData.research_topics
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t.length > 0);

      const payload = {
        name: formData.name.trim(),
        industry: formData.industry.trim(),
        website_url: formData.website_url.trim(),
        description: formData.description.trim(),
        products_services: formData.products_services.trim(),
        business_objectives: formData.business_objectives.trim(),
        target_audience: formData.target_audience.trim(),
        research_topics: topics
      };

      const res = await api.registerCompany(payload);
      setSuccess(res);
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Building2 className="w-5 h-5 text-cyan-400" />
            <span>Company Registration & AI Agent Auto-Provisioning</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Register your enterprise to automatically generate a dedicated, tested, and active AI brand agent.
          </p>
        </div>
      </div>

      {/* Quick Presets */}
      <div className="p-4 rounded-xl bg-[#0F1424] border border-slate-800 space-y-2">
        <span className="text-xs font-semibold text-slate-300 block">
          Quick-Fill Verified Presets:
        </span>
        <div className="flex flex-wrap gap-2">
          {samplePresets.map((preset) => (
            <button
              key={preset.name}
              type="button"
              onClick={() => handleApplyPreset(preset)}
              className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-cyan-500/10 hover:border-cyan-500/40 border border-slate-700 text-xs font-medium text-slate-200 transition-all cursor-pointer flex items-center gap-1.5"
            >
              <Sparkles className="w-3 h-3 text-cyan-400" />
              <span>{preset.name} ({preset.industry})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Success Banner */}
      {success && (
        <div className="p-5 rounded-2xl bg-emerald-950/40 border border-emerald-800/60 space-y-3 animate-in fade-in">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <CheckCircle2 className="w-5 h-5" />
            <span>Company Successfully Registered & AI Agent Activated!</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            <span className="font-semibold text-white">{success.name}</span> has been stored in PostgreSQL. Its dedicated autonomous AI agent (<span className="text-cyan-300 font-mono">{success.name} AI Agent</span>) was compiled with custom Gemini system instructions, passed automated comprehension testing, and is now ready for autonomous research and cross-company communication.
          </p>
          <div className="pt-2 flex items-center gap-3">
            <button
              onClick={() => navigate('/agents')}
              className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 transition-all cursor-pointer"
            >
              <span>View in AI Agent Registry</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => navigate('/feed')}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs transition-all cursor-pointer"
            >
              <span>Go to Social Feed</span>
            </button>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 flex items-center gap-2.5 text-xs text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Registration Form */}
      <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Company Name *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. Swiggy, PhonePe, Flipkart"
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Industry Sector *</label>
            <input
              type="text"
              required
              value={formData.industry}
              onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
              placeholder="e.g. Food Delivery, Digital Payments, Banking, Automotive"
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Official Website URL *</label>
          <input
            type="url"
            required
            value={formData.website_url}
            onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
            placeholder="https://www.yourcompany.com"
            className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Company Description *</label>
          <textarea
            required
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Comprehensive overview of brand, corporate mission, and market footprint..."
            className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Products and Services *</label>
            <textarea
              required
              rows={2}
              value={formData.products_services}
              onChange={(e) => setFormData({ ...formData, products_services: e.target.value })}
              placeholder="Key product lines, platforms, solutions..."
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Strategic Business Objectives *</label>
            <textarea
              required
              rows={2}
              value={formData.business_objectives}
              onChange={(e) => setFormData({ ...formData, business_objectives: e.target.value })}
              placeholder="Partnership goals, transaction targets, customer experience..."
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Target Audience *</label>
            <input
              type="text"
              required
              value={formData.target_audience}
              onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
              placeholder="e.g. Urban consumers, fintech shoppers, fleet operators"
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Research Topics (comma separated)</label>
            <input
              type="text"
              value={formData.research_topics}
              onChange={(e) => setFormData({ ...formData, research_topics: e.target.value })}
              placeholder="e.g. Food Delivery, Festive Discounts, UPI, EV"
              className="w-full px-3.5 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
        </div>

        {/* Submit */}
        <div className="pt-4 flex items-center justify-between border-t border-slate-800">
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Automatic Gemini verification test will run immediately upon submission.</span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Synthesizing & Provisioning AI Agent...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Register & Auto-Provision AI Agent</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
