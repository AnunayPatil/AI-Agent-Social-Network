export interface Company {
  id: string;
  name: string;
  industry: string;
  website_url: string;
  description: string;
  products_services: string;
  business_objectives: string;
  target_audience: string;
  research_topics: string[];
  avatar_url?: string;
  created_at: string;
  agents_count?: number;
}

export interface Agent {
  id: string;
  company_id: string;
  company_name?: string;
  identity_name: string;
  role: string;
  status: 'Pending' | 'Testing' | 'Active' | 'Failed' | 'Disabled';
  system_instructions: string;
  created_at: string;
  updated_at: string;
  research_topics?: string[];
  relevance_threshold?: number;
  is_paused?: boolean;
}

export interface AgentTestResult {
  id: string;
  agent_id: string;
  test_type: string;
  test_prompt: string;
  test_response: string;
  score: number;
  passed: boolean;
  feedback: string;
  created_at: string;
}

export interface ResearchResult {
  id: string;
  agent_id: string;
  agent_name?: string;
  source_url: string;
  title: string;
  cleaned_content: string;
  extracted_topics: string[];
  summary: string;
  post_id?: string;
  created_at: string;
}

export interface Post {
  id: string;
  company_id: string;
  company_name: string;
  company_avatar?: string;
  industry: string;
  agent_id: string;
  agent_name: string;
  title: string;
  content: string;
  source_url?: string;
  topic?: string;
  category?: string;
  likes_count: number;
  comments_count: number;
  matched_count: number;
  is_simulated: boolean;
  created_at: string;
}

export interface AgentMatch {
  id: string;
  post_id: string;
  matched_agent_id: string;
  matched_company_name: string;
  matched_agent_name: string;
  matched_industry: string;
  relevance_score: number;
  matching_reason: string;
  notification_status: string;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  recipient_agent_id: string;
  recipient_agent_name?: string;
  recipient_company_name?: string;
  post_id: string;
  post_title?: string;
  match_id?: string;
  title: string;
  message: string;
  status: 'Pending' | 'Delivered' | 'Read' | 'Responded' | 'Ignored';
  created_at: string;
}

export interface CommentItem {
  id: string;
  post_id: string;
  company_id: string;
  company_name: string;
  company_avatar?: string;
  agent_id: string;
  agent_name: string;
  parent_comment_id?: string;
  content: string;
  decision: string;
  reasoning?: string;
  is_simulated: boolean;
  created_at: string;
  replies?: CommentItem[];
}

export interface ConversationItem {
  id: string;
  post_id: string;
  post_title: string;
  original_company: string;
  original_agent: string;
  participating_agents: Array<{
    agent_id: string;
    agent_name: string;
    company_name: string;
  }>;
  message_count: number;
  depth: number;
  status: 'ACTIVE' | 'PAUSED' | 'CLOSED';
  created_at: string;
  updated_at: string;
  comments: CommentItem[];
}

export interface SystemMetrics {
  total_companies: number;
  total_agents: number;
  active_agents: number;
  total_research: number;
  total_posts: number;
  total_notifications: number;
  total_conversations: number;
}

export interface ActivityEvent {
  id: string;
  type: string;
  title: string;
  detail: string;
  timestamp: string;
  actor: string;
  badge: string;
}
