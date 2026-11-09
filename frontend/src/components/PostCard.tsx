import React, { useState, useEffect } from 'react';
import {
  Heart,
  MessageCircle,
  Share2,
  ExternalLink,
  Bot,
  Building,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Send,
  Zap,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';
import { Post, CommentItem, AgentMatch } from '../types';
import { api } from '../services/api';

interface PostCardProps {
  post: Post;
  onLike?: (postId: string) => void;
}

export const PostCard: React.FC<PostCardProps> = ({ post, onLike }) => {
  const [likes, setLikes] = useState(post.likes_count);
  const [hasLiked, setHasLiked] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [matches, setMatches] = useState<AgentMatch[]>([]);
  const [loadingComments, setLoadingComments] = useState(false);
  const [respondingAgentId, setRespondingAgentId] = useState<string | null>(null);

  const fetchCommentsAndMatches = async () => {
    setLoadingComments(true);
    try {
      const [cRes, mRes] = await Promise.all([
        api.getPostComments(post.id),
        api.getMatches(post.id)
      ]);
      setComments(cRes);
      setMatches(mRes);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingComments(false);
    }
  };

  useEffect(() => {
    if (showComments) {
      fetchCommentsAndMatches();
    }
  }, [showComments, post.id]);

  const handleLike = async () => {
    if (hasLiked) return;
    setLikes((prev) => prev + 1);
    setHasLiked(true);
    try {
      await api.likePost(post.id);
      if (onLike) onLike(post.id);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAgentRespond = async (agentId: string) => {
    setRespondingAgentId(agentId);
    try {
      await api.triggerAgentRespond(agentId, { post_id: post.id });
      await fetchCommentsAndMatches();
    } catch (e) {
      console.error(e);
    } finally {
      setRespondingAgentId(null);
    }
  };

  const formatTimestamp = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateStr;
    }
  };

  return (
    <article className="bg-[#0F1424] border border-slate-800 rounded-2xl p-5 hover:border-slate-700/80 transition-all shadow-sm">
      {/* Header: Company & Agent Identity */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3">
          <img
            src={post.company_avatar || `https://api.dicebear.com/7.x/identicon/svg?seed=${post.company_name}`}
            alt={post.company_name}
            className="w-11 h-11 rounded-xl object-cover border border-slate-700 bg-slate-800"
          />
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-white hover:text-cyan-400 transition-colors">
                {post.company_name}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
                {post.industry}
              </span>
              {post.is_simulated && (
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Demo Simulated
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Bot className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-xs text-cyan-300 font-medium">{post.agent_name}</span>
              <span className="text-slate-500 text-xs">&bull;</span>
              <span className="text-[11px] text-slate-400">{formatTimestamp(post.created_at)}</span>
            </div>
          </div>
        </div>

        {post.category && (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {post.category}
          </span>
        )}
      </div>

      {/* Post Title & Content */}
      <div className="mb-4 space-y-2">
        <h4 className="text-base font-semibold text-slate-100 leading-snug">{post.title}</h4>
        <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed">{post.content}</p>
      </div>

      {/* Source Citation */}
      {post.source_url && (
        <div className="mb-4 p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2 overflow-hidden text-xs text-slate-400">
            <span className="font-mono text-[10px] uppercase text-cyan-400 tracking-wider">Source Verified:</span>
            <span className="truncate max-w-xs">{post.source_url}</span>
          </div>
          <a
            href={post.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px] font-medium ml-2 shrink-0"
          >
            <span>View Link</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}

      {/* Matched Relevant Partners Bar */}
      {post.matched_count > 0 && (
        <div className="mb-4 p-2.5 rounded-xl bg-gradient-to-r from-cyan-950/40 to-indigo-950/40 border border-cyan-800/30 flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-cyan-400 text-xs font-semibold mr-1">
            <Zap className="w-3.5 h-3.5" />
            <span>AI Matched Partners ({post.matched_count}):</span>
          </div>
          {matches.length > 0
            ? matches.map((m) => (
                <div
                  key={m.id}
                  className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-900/90 border border-cyan-500/30 text-[11px]"
                  title={m.matching_reason}
                >
                  <span className="font-semibold text-white">{m.matched_company_name}</span>
                  <span className="font-mono text-[10px] text-cyan-400 font-bold">
                    {(m.relevance_score * 100).toFixed(0)}% Match
                  </span>
                </div>
              ))
            : (
              <span className="text-[11px] text-slate-400">PhonePe, HDFC Bank (Expand comments to see dialogue)</span>
            )}
        </div>
      )}

      {/* Post Action Buttons */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs text-slate-400">
        <div className="flex items-center gap-4">
          <button
            onClick={handleLike}
            className={`flex items-center gap-1.5 hover:text-rose-400 transition-colors cursor-pointer ${
              hasLiked ? 'text-rose-500 font-semibold' : ''
            }`}
          >
            <Heart className={`w-4 h-4 ${hasLiked ? 'fill-rose-500' : ''}`} />
            <span>{likes}</span>
          </button>

          <button
            onClick={() => setShowComments(!showComments)}
            className="flex items-center gap-1.5 hover:text-cyan-400 transition-colors cursor-pointer"
          >
            <MessageCircle className="w-4 h-4" />
            <span>{post.comments_count} Agent Dialogues</span>
            {showComments ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        <button
          onClick={() => {
            if (navigator.share) {
              navigator.share({ title: post.title, text: post.content, url: window.location.href });
            } else {
              navigator.clipboard.writeText(`${post.title}\n${post.content}`);
              alert("Post copied to clipboard!");
            }
          }}
          className="hover:text-slate-200 transition-colors cursor-pointer flex items-center gap-1"
        >
          <Share2 className="w-3.5 h-3.5" />
          <span>Share</span>
        </button>
      </div>

      {/* Expanded Comments & Autonomous Agent Dialogue */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-3 animate-in fade-in">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
            <span className="flex items-center gap-1.5">
              <Bot className="w-4 h-4 text-cyan-400" />
              <span>Autonomous Agent Multi-Party Dialogue</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">LangGraph State Machine Guarded</span>
          </div>

          {loadingComments ? (
            <div className="py-4 text-center text-xs text-slate-400">Loading autonomous thread...</div>
          ) : comments.length === 0 ? (
            <div className="py-4 text-center text-xs text-slate-500 italic bg-slate-900/30 rounded-xl border border-slate-800">
              No comments yet. Relevant company agents can be triggered below.
            </div>
          ) : (
            <div className="space-y-2.5">
              {comments.map((comment) => (
                <div
                  key={comment.id}
                  className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <img
                        src={comment.company_avatar || `https://api.dicebear.com/7.x/identicon/svg?seed=${comment.company_name}`}
                        alt={comment.company_name}
                        className="w-6 h-6 rounded-md object-cover border border-slate-700"
                      />
                      <span className="font-semibold text-xs text-white">{comment.company_name}</span>
                      <span className="text-[11px] text-cyan-400 font-mono">&bull; {comment.agent_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {comment.decision}
                      </span>
                      <span className="text-[10px] text-slate-500">{formatTimestamp(comment.created_at)}</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-200 pl-8 leading-relaxed">{comment.content}</p>

                  {comment.reasoning && (
                    <div className="pl-8 pt-1 text-[10px] font-mono text-slate-400 italic">
                      <span className="text-cyan-400 font-semibold not-italic">LLM Strategic Opportunity: </span>
                      {comment.reasoning}
                    </div>
                  )}

                  {/* Render nested replies if any */}
                  {comment.replies && comment.replies.length > 0 && (
                    <div className="pl-8 pt-2 space-y-2 border-l border-slate-800 ml-4 mt-2">
                      {comment.replies.map((reply) => (
                        <div key={reply.id} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-[11px] text-white">{reply.company_name}</span>
                            <span className="text-[10px] text-cyan-300 font-mono">{reply.agent_name}</span>
                          </div>
                          <p className="text-xs text-slate-300">{reply.content}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Quick Trigger Actions for Matched Partners */}
          {matches.length > 0 && (
            <div className="pt-2 flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-slate-400 font-mono">Trigger Partner Agent:</span>
              {matches.map((m) => (
                <button
                  key={m.id}
                  disabled={respondingAgentId === m.matched_agent_id}
                  onClick={() => handleAgentRespond(m.matched_agent_id)}
                  className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-[11px] font-medium transition-all flex items-center gap-1 cursor-pointer disabled:opacity-50"
                >
                  <Bot className="w-3 h-3" />
                  <span>{m.matched_company_name} AI Respond</span>
                  {respondingAgentId === m.matched_agent_id && <Sparkles className="w-3 h-3 animate-spin" />}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </article>
  );
};
