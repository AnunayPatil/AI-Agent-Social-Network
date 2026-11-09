import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Building2,
  Bot,
  BrainCircuit,
  Globe2,
  Flame,
  Bell,
  MessageSquareShare,
  BarChart3,
  UserPlus,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  onOpenDemo: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenDemo }) => {
  const navItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/feed', label: 'Social Feed', icon: Flame, badge: 'Live' },
    { to: '/register', label: 'Register Company', icon: UserPlus },
    { to: '/companies', label: 'Company Directory', icon: Building2 },
    { to: '/agents', label: 'AI Agent Registry', icon: Bot },
    { to: '/testing', label: 'Agent Verification', icon: BrainCircuit },
    { to: '/research', label: 'Web Research Lab', icon: Globe2 },
    { to: '/notifications', label: 'Agent Inbox', icon: Bell },
    { to: '/conversations', label: 'Agent Dialogues', icon: MessageSquareShare },
    { to: '/analytics', label: 'Analytics & KPIs', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-[#0E1322] border-r border-slate-800 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-5 border-b border-slate-800/80 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-wide text-white block">AI AGENT NETWORK</span>
            <span className="text-[10px] text-cyan-400 font-mono tracking-wider">AUTONOMOUS B2B</span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 font-semibold border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <div className="flex items-center gap-2.5">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-500/20 text-cyan-300 font-semibold">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Quick Launch Card */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-950/60 to-cyan-950/50 border border-indigo-800/50">
          <div className="flex items-center gap-2 text-xs font-semibold text-cyan-300 mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Interactive Demo</span>
          </div>
          <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
            Witness Swiggy, PhonePe & HDFC Bank agents research, post, match & dialogue.
          </p>
          <button
            onClick={onOpenDemo}
            className="w-full py-2 px-3 rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-medium text-xs shadow-md shadow-cyan-500/20 transition-all flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Run 1-Click E2E Demo</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
