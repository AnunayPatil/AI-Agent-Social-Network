import axios from 'axios';
import {
  Company,
  Agent,
  AgentTestResult,
  ResearchResult,
  Post,
  AgentMatch,
  NotificationItem,
  CommentItem,
  ConversationItem,
  SystemMetrics,
  ActivityEvent
} from '../types';

const API_BASE = '/api';

export const api = {
  // Companies
  getCompanies: async (): Promise<Company[]> => {
    const res = await axios.get(`${API_BASE}/companies`);
    return res.data;
  },
  getCompany: async (id: string): Promise<Company> => {
    const res = await axios.get(`${API_BASE}/companies/${id}`);
    return res.data;
  },
  registerCompany: async (payload: Partial<Company>): Promise<Company> => {
    const res = await axios.post(`${API_BASE}/companies/register`, payload);
    return res.data;
  },

  // Agents
  getAgents: async (status?: string): Promise<Agent[]> => {
    const res = await axios.get(`${API_BASE}/agents`, { params: { status } });
    return res.data;
  },
  getAgent: async (id: string): Promise<Agent> => {
    const res = await axios.get(`${API_BASE}/agents/${id}`);
    return res.data;
  },
  testAgent: async (id: string, custom_prompt?: string): Promise<AgentTestResult> => {
    const res = await axios.post(`${API_BASE}/agents/${id}/test`, { custom_prompt });
    return res.data;
  },
  getAgentTestHistory: async (id: string): Promise<AgentTestResult[]> => {
    const res = await axios.get(`${API_BASE}/agents/${id}/tests`);
    return res.data;
  },
  activateAgent: async (id: string): Promise<Agent> => {
    const res = await axios.post(`${API_BASE}/agents/${id}/activate`);
    return res.data;
  },
  toggleAgentPause: async (id: string): Promise<Agent> => {
    const res = await axios.post(`${API_BASE}/agents/${id}/toggle-pause`);
    return res.data;
  },

  // Research
  runResearch: async (agentId: string, payload: { source_url_override?: string; auto_generate_post?: boolean }): Promise<ResearchResult> => {
    const res = await axios.post(`${API_BASE}/research/${agentId}/run`, payload);
    return res.data;
  },
  getAgentResearch: async (agentId: string): Promise<ResearchResult[]> => {
    const res = await axios.get(`${API_BASE}/research/${agentId}/results`);
    return res.data;
  },
  getAllResearch: async (): Promise<ResearchResult[]> => {
    const res = await axios.get(`${API_BASE}/research/all/results`);
    return res.data;
  },

  // Posts & Feed
  getPosts: async (industry?: string): Promise<Post[]> => {
    const res = await axios.get(`${API_BASE}/posts`, { params: { industry } });
    return res.data;
  },
  getPost: async (id: string): Promise<Post> => {
    const res = await axios.get(`${API_BASE}/posts/${id}`);
    return res.data;
  },
  createPost: async (payload: {
    company_id: string;
    agent_id: string;
    title: string;
    content: string;
    source_url?: string;
    topic?: string;
    category?: string;
    auto_trigger_matching?: boolean;
  }): Promise<Post> => {
    const res = await axios.post(`${API_BASE}/posts`, payload);
    return res.data;
  },
  likePost: async (id: string): Promise<Post> => {
    const res = await axios.post(`${API_BASE}/posts/${id}/like`);
    return res.data;
  },

  // Matching
  triggerMatching: async (postId: string, threshold?: number): Promise<AgentMatch[]> => {
    const res = await axios.post(`${API_BASE}/matching/${postId}`, null, { params: { threshold } });
    return res.data;
  },
  getMatches: async (postId: string): Promise<AgentMatch[]> => {
    const res = await axios.get(`${API_BASE}/matching/${postId}/results`);
    return res.data;
  },

  // Notifications
  getNotifications: async (agentId?: string): Promise<NotificationItem[]> => {
    const url = agentId ? `${API_BASE}/notifications/${agentId}` : `${API_BASE}/notifications`;
    const res = await axios.get(url);
    return res.data;
  },
  markNotificationRead: async (id: string): Promise<NotificationItem> => {
    const res = await axios.post(`${API_BASE}/notifications/${id}/read`);
    return res.data;
  },

  // Communication & Comments
  getPostComments: async (postId: string): Promise<CommentItem[]> => {
    const res = await axios.get(`${API_BASE}/posts/${postId}/comments`);
    return res.data;
  },
  addComment: async (postId: string, payload: {
    company_id: string;
    agent_id: string;
    content: string;
    parent_comment_id?: string;
    decision?: string;
    reasoning?: string;
  }): Promise<CommentItem> => {
    const res = await axios.post(`${API_BASE}/posts/${postId}/comments`, payload);
    return res.data;
  },
  triggerAgentRespond: async (agentId: string, payload: {
    post_id: string;
    notification_id?: string;
    override_decision?: string;
  }) => {
    const res = await axios.post(`${API_BASE}/agents/${agentId}/respond`, payload);
    return res.data;
  },
  getConversation: async (id: string): Promise<ConversationItem> => {
    const res = await axios.get(`${API_BASE}/conversations/${id}`);
    return res.data;
  },
  toggleConversationStatus: async (id: string, status?: string) => {
    const res = await axios.post(`${API_BASE}/conversations/${id}/toggle-status`, null, { params: { status } });
    return res.data;
  },

  // Analytics & Demo
  getMetrics: async (): Promise<SystemMetrics> => {
    const res = await axios.get(`${API_BASE}/analytics/metrics`);
    return res.data;
  },
  getActivity: async (): Promise<ActivityEvent[]> => {
    const res = await axios.get(`${API_BASE}/analytics/activity`);
    return res.data;
  },
  runE2EDemo: async () => {
    const res = await axios.post(`${API_BASE}/workflow/e2e-demo`);
    return res.data;
  }
};
