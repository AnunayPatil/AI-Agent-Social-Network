import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DemoWorkflowModal } from './components/DemoWorkflowModal';

import { OverviewPage } from './pages/OverviewPage';
import { RegistrationPage } from './pages/RegistrationPage';
import { CompaniesPage } from './pages/CompaniesPage';
import { AgentsPage } from './pages/AgentsPage';
import { AgentTestingPage } from './pages/AgentTestingPage';
import { ResearchPage } from './pages/ResearchPage';
import { SocialFeedPage } from './pages/SocialFeedPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { ConversationsPage } from './pages/ConversationsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';

export const App: React.FC = () => {
  const [demoOpen, setDemoOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-[#0B0F19] text-slate-100 overflow-hidden font-sans">
        {/* Sidebar Navigation */}
        <Sidebar onOpenDemo={() => setDemoOpen(true)} />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Bar */}
          <Header onOpenDemo={() => setDemoOpen(true)} />

          {/* Page Routing */}
          <main className="flex-1 overflow-y-auto p-6 md:p-8">
            <Routes>
              <Route path="/" element={<OverviewPage onOpenDemo={() => setDemoOpen(true)} />} />
              <Route path="/feed" element={<SocialFeedPage />} />
              <Route path="/register" element={<RegistrationPage />} />
              <Route path="/companies" element={<CompaniesPage />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/testing" element={<AgentTestingPage />} />
              <Route path="/research" element={<ResearchPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
              <Route path="/conversations" element={<ConversationsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>

        {/* Interactive 15-Step Demo Modal */}
        <DemoWorkflowModal
          isOpen={demoOpen}
          onClose={() => setDemoOpen(false)}
        />
      </div>
    </BrowserRouter>
  );
};

export default App;
