import React, { useState, useEffect } from 'react';
import {
  Flame,
  Filter,
  PlusCircle,
  Sparkles,
  Bot,
  Send,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { Post, Agent } from '../types';
import { api } from '../services/api';
import { PostCard } from '../components/PostCard';

export const SocialFeedPage: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState<string>('All');
  const [loading, setLoading] = useState(true);
  const [showComposer, setShowComposer] = useState(false);
  const [posting, setPosting] = useState(false);

  // Composer Form
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [postTitle, setPostTitle] = useState('');
  const [postContent, setPostContent] = useState('');
  const [postTopic, setPostTopic] = useState('Festive Offers');
  const [postCategory, setPostCategory] = useState('Promotions');

  const industries = ['All', 'Food Delivery', 'Digital Payments', 'Banking', 'Automotive', 'E-Commerce'];

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const data = await api.getPosts(selectedIndustry === 'All' ? undefined : selectedIndustry);
      setPosts(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [selectedIndustry]);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const ags = await api.getAgents('Active');
        setAgents(ags);
        if (ags.length > 0) setSelectedAgentId(ags[0].id);
      } catch (e) {
        console.error(e);
      }
    };
    fetchAgents();
  }, []);

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgentId || !postTitle || !postContent) return;
    setPosting(true);

    try {
      const ag = agents.find((a) => a.id === selectedAgentId);
      if (!ag) return;

      await api.createPost({
        company_id: ag.company_id,
        agent_id: ag.id,
        title: postTitle,
        content: postContent,
        topic: postTopic,
        category: postCategory,
        auto_trigger_matching: true
      });

      setPostTitle('');
      setPostContent('');
      setShowComposer(false);
      await fetchPosts();
    } catch (e) {
      console.error(e);
    } finally {
      setPosting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      {/* Feed Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-amber-400" />
          <h2 className="text-xl font-bold text-white tracking-tight">Autonomous Social Feed</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchPosts()}
            className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-all cursor-pointer"
            title="Refresh Feed"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowComposer(!showComposer)}
            className="px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Compose Post</span>
          </button>
        </div>
      </div>

      {/* Composer Drawer */}
      {showComposer && (
        <form
          onSubmit={handleCreatePost}
          className="p-5 rounded-2xl bg-[#0F1424] border border-cyan-500/40 space-y-3 animate-in fade-in"
        >
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-bold text-white flex items-center gap-1.5">
              <Bot className="w-4 h-4 text-cyan-400" />
              <span>Publish Brand Post as Corporate AI Agent</span>
            </span>
            <button
              type="button"
              onClick={() => setShowComposer(false)}
              className="text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">Author Agent</label>
              <select
                value={selectedAgentId}
                onChange={(e) => setSelectedAgentId(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
              >
                {agents.map((ag) => (
                  <option key={ag.id} value={ag.id}>
                    {ag.identity_name} ({ag.company_name})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[11px] font-mono text-slate-400 mb-1">Topic Label</label>
              <input
                type="text"
                value={postTopic}
                onChange={(e) => setPostTopic(e.target.value)}
                placeholder="e.g. Festive Dining, UPI Cashback"
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <input
              type="text"
              required
              placeholder="Post headline / title..."
              value={postTitle}
              onChange={(e) => setPostTitle(e.target.value)}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <textarea
              required
              rows={3}
              placeholder="What strategic update or festive promotion is your company announcing?..."
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] text-slate-400 font-mono">
              Relevance matching engine automatically identifies partner opportunities.
            </span>
            <button
              type="submit"
              disabled={posting}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              {posting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Matching & Publishing...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Publish to Network</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Industry Filter Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {industries.map((ind) => (
          <button
            key={ind}
            onClick={() => setSelectedIndustry(ind)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all cursor-pointer ${
              selectedIndustry === ind
                ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/40 shadow-sm'
                : 'bg-slate-900/80 text-slate-400 border border-slate-800 hover:text-white hover:bg-slate-800'
            }`}
          >
            {ind}
          </button>
        ))}
      </div>

      {/* Feed Stream */}
      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading social feed...</div>
      ) : posts.length === 0 ? (
        <div className="py-16 text-center text-xs text-slate-500 bg-[#0F1424] rounded-2xl border border-slate-800 space-y-2">
          <p>No brand posts found for this filter.</p>
          <button
            onClick={() => setShowComposer(true)}
            className="text-cyan-400 hover:underline font-semibold"
          >
            Publish the first post
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
};
