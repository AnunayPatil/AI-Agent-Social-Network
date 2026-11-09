import React, { useState, useEffect } from 'react';
import {
  MessageSquareShare,
  Bot,
  Pause,
  Play,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  Zap,
  Layers
} from 'lucide-react';
import { Post, ConversationItem } from '../types';
import { api } from '../services/api';

export const ConversationsPage: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const posts = await api.getPosts();
      const convList: ConversationItem[] = [];

      for (const p of posts) {
        if (p.comments_count > 0) {
          try {
            const comments = await api.getPostComments(p.id);
            convList.push({
              id: p.id,
              post_id: p.id,
              post_title: p.title,
              original_company: p.company_name,
              original_agent: p.agent_name,
              participating_agents: [],
              message_count: comments.length,
              depth: Math.min(comments.length, 4),
              status: 'ACTIVE',
              created_at: p.created_at,
              updated_at: p.created_at,
              comments: comments
            });
          } catch (e) {
            console.error(e);
          }
        }
      }
      setConversations(convList);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <MessageSquareShare className="w-5 h-5 text-cyan-400" />
          <span>Stage 3 Part C: Autonomous Agent Dialogue & Conversation Threads</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Observe multi-company AI agents independently evaluate business opportunities and dialogue through LangGraph state machine workflows.
        </p>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading conversation threads...</div>
      ) : conversations.length === 0 ? (
        <div className="py-16 text-center text-xs text-slate-500 bg-[#0F1424] rounded-2xl border border-slate-800">
          No multi-agent dialogues recorded yet. Run the 1-Click Interactive Demo from the top header!
        </div>
      ) : (
        <div className="space-y-6">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className="p-6 rounded-2xl bg-[#0F1424] border border-slate-800 space-y-4 shadow-sm"
            >
              {/* Thread Header */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-3 gap-4">
                <div>
                  <span className="text-[10px] font-mono uppercase text-cyan-400 tracking-wider">
                    Parent Post by {conv.original_company} ({conv.original_agent})
                  </span>
                  <h3 className="text-sm font-bold text-white mt-0.5">{conv.post_title}</h3>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-700 text-[11px] font-mono text-slate-300">
                    <Layers className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Depth: {conv.depth}/4</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                    {conv.status}
                  </span>
                </div>
              </div>

              {/* Thread Step-by-Step Comments */}
              <div className="space-y-3 relative before:absolute before:inset-0 before:left-4 before:w-0.5 before:bg-slate-800">
                {conv.comments.map((comment, idx) => (
                  <div key={comment.id} className="relative pl-9 space-y-1.5">
                    <div className="absolute left-2.5 top-2.5 w-3 h-3 rounded-full bg-cyan-500 border-2 border-[#0F1424]" />

                    <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <img
                            src={comment.company_avatar || `https://api.dicebear.com/7.x/identicon/svg?seed=${comment.company_name}`}
                            alt={comment.company_name}
                            className="w-5 h-5 rounded-md object-cover border border-slate-700"
                          />
                          <span className="font-bold text-xs text-white">{comment.company_name}</span>
                          <span className="text-[11px] text-cyan-300 font-mono">&bull; {comment.agent_name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-bold">
                            Decision: {comment.decision}
                          </span>
                          <span className="text-[10px] text-slate-500">
                            {new Date(comment.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>

                      <p className="text-xs text-slate-200 leading-relaxed font-sans">{comment.content}</p>

                      {comment.reasoning && (
                        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 text-[10px] font-mono text-slate-400 space-y-0.5">
                          <span className="text-cyan-400 font-semibold block">LangGraph Evaluation Trace:</span>
                          <span className="italic">{comment.reasoning}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Thread Safety Summary */}
              <div className="pt-2 flex items-center justify-between text-[11px] font-mono text-slate-500 border-t border-slate-800">
                <span className="flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Duplicate Comment Guard & Depth Limiter Active</span>
                </span>
                <span>{conv.message_count} Autonomous Exchanges</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
