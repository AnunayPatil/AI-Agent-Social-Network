import React, { useState, useEffect } from 'react';
import {
  Bell,
  Bot,
  CheckCircle2,
  Clock,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Zap,
  Filter,
  Check,
  Loader2
} from 'lucide-react';
import { NotificationItem, Agent } from '../types';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('All');
  const [loading, setLoading] = useState(true);
  const [respondingId, setRespondingId] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [notifs, agList] = await Promise.all([
        api.getNotifications(selectedAgentId === 'All' ? undefined : selectedAgentId),
        api.getAgents()
      ]);
      setNotifications(notifs);
      setAgents(agList);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedAgentId]);

  const handleMarkRead = async (notifId: string) => {
    try {
      await api.markNotificationRead(notifId);
      await fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleTriggerRespond = async (notif: NotificationItem) => {
    setRespondingId(notif.id);
    try {
      await api.triggerAgentRespond(notif.recipient_agent_id, {
        post_id: notif.post_id,
        notification_id: notif.id
      });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setRespondingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Responded':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            Responded
          </span>
        );
      case 'Read':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30">
            Read
          </span>
        );
      case 'Ignored':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-500/10 text-slate-400 border border-slate-500/30">
            Ignored
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Delivered
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-cyan-400" />
            <span>Stage 3 Part B: Agent Notification Inbox</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Relevance-matched partner alerts dispatched automatically upon post publication.
          </p>
        </div>

        {/* Filter by recipient */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedAgentId}
            onChange={(e) => setSelectedAgentId(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Agent Inboxes</option>
            {agents.map((ag) => (
              <option key={ag.id} value={ag.id}>
                {ag.identity_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs text-slate-400">Loading inbox...</div>
      ) : notifications.length === 0 ? (
        <div className="py-16 text-center text-xs text-slate-500 bg-[#0F1424] rounded-2xl border border-slate-800">
          No notifications in inbox. Post a new announcement to trigger partner matching!
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className="p-5 rounded-2xl bg-[#0F1424] border border-slate-800 hover:border-slate-700 transition-all space-y-3"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
                    <Zap className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">{notif.title}</h4>
                    <span className="text-[11px] text-cyan-300 font-mono">
                      To: {notif.recipient_agent_name} ({notif.recipient_company_name})
                    </span>
                  </div>
                </div>
                {getStatusBadge(notif.status)}
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-300 font-mono">
                {notif.message}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(notif.created_at).toLocaleString()}
                </span>

                <div className="flex items-center gap-2">
                  {notif.status !== 'Read' && notif.status !== 'Responded' && (
                    <button
                      onClick={() => handleMarkRead(notif.id)}
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-all flex items-center gap-1 cursor-pointer"
                    >
                      <Check className="w-3 h-3" />
                      <span>Mark Read</span>
                    </button>
                  )}

                  {notif.status !== 'Responded' && (
                    <button
                      disabled={respondingId === notif.id}
                      onClick={() => handleTriggerRespond(notif)}
                      className="px-3.5 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                    >
                      {respondingId === notif.id ? (
                        <>
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span>Evaluating...</span>
                        </>
                      ) : (
                        <>
                          <Bot className="w-3 h-3" />
                          <span>LangGraph Autonomous Respond</span>
                        </>
                      )}
                    </button>
                  )}

                  <button
                    onClick={() => navigate('/feed')}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all cursor-pointer"
                    title="View in Feed"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
