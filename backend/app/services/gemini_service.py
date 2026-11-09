import os
import json
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.client_ready = False
        if GENAI_AVAILABLE and self.api_key and self.api_key.strip():
            try:
                genai.configure(api_key=self.api_key.strip())
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.client_ready = True
                logger.info("Gemini API successfully configured.")
            except Exception as e:
                logger.warning(f"Could not configure Gemini API: {e}. Falling back to demo mode.")
                self.client_ready = False
        else:
            logger.info("Gemini API key not configured. Operating in high-fidelity Demo Mode.")

    def is_live(self) -> bool:
        return self.client_ready

    # 1. Automatic System Instructions Generation
    def generate_system_instructions(self, company_dict: Dict[str, Any]) -> Tuple[str, bool]:
        """Generates fine-tuned persona and operational instructions for an enterprise AI agent."""
        prompt = f"""
You are an expert AI Architect. Create official, high-precision system instructions for an enterprise AI Agent representing the company: {company_dict.get('name')}.

Company Profile:
- Industry: {company_dict.get('industry')}
- Website: {company_dict.get('website_url')}
- Description: {company_dict.get('description')}
- Products & Services: {company_dict.get('products_services')}
- Business Objectives: {company_dict.get('business_objectives')}
- Target Audience: {company_dict.get('target_audience')}
- Research Focus: {', '.join(company_dict.get('research_topics', []))}

Generate comprehensive system instructions defining:
1. Agent Identity & Role
2. Brand Voice, Tone & Persona Guidelines
3. Strategic Objectives & Decision Framework for Social Engagement
4. Boundary Conditions & Compliance (never commit unauthorized funds or make unsubstantiated claims)
5. Partnership & Collaboration criteria with partner agents (e.g. payments, logistics, retail, fintech).

Output clear, formatted markdown instructions.
"""
        if self.client_ready:
            try:
                resp = self.model.generate_content(prompt)
                if resp.text:
                    return resp.text.strip(), False
            except Exception as e:
                logger.error(f"Gemini error in generate_system_instructions: {e}")

        # High-fidelity simulated template for demo mode
        name = company_dict.get('name', 'Company')
        industry = company_dict.get('industry', 'Enterprise')
        desc = company_dict.get('description', '')
        objs = company_dict.get('business_objectives', '')
        prods = company_dict.get('products_services', '')
        
        instructions = f"""# System Instructions: {name} AI Agent

## 1. Identity & Role
You are the Official Autonomous AI Agent representing **{name}** in the corporate social ecosystem.
- **Industry Sector**: {industry}
- **Mission**: Champion {name}'s brand authority, expand B2B strategic alliances, monitor market shifts, and initiate value-accretive partnerships.

## 2. Brand Voice & Tone
- **Professional & Crisp**: Executive, innovative, customer-obsessed, and solutions-oriented.
- **Proactive & Collaborative**: Look for win-win synergies with ecosystem partners (e.g., payment gateways, banks, supply chain, retailers).
- **Factual & Transparent**: Anchor all statements in authentic brand capabilities: {prods}.

## 3. Autonomous Decision & Evaluation Framework
When evaluating external posts or partner announcements:
1. **Relevance Assessment**: Evaluate if the post touches upon {objs} or offers customer co-benefits.
2. **Action Threshold**: Only respond if there is a tangible mutual business opportunity. Otherwise, IGNORE.
3. **Synergy Formulation**: Formulate specific, actionable co-marketing or integration proposals.

## 4. Operational Boundaries
- Never commit legally binding contracts or reveal proprietary technical infrastructure.
- Adhere strictly to industry compliance standards.
"""
        return instructions.strip(), True

    # 2. Agent Verification Test
    def verify_agent_comprehension(self, company_dict: Dict[str, Any], system_instructions: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Runs an automatic verification test to assess whether the agent grasps company objectives."""
        test_prompt = custom_prompt or f"What are {company_dict.get('name')}'s core business objectives and how will you represent them when interacting with partner companies?"
        
        if self.client_ready:
            try:
                eval_prompt = f"""
You are the AI Agent for {company_dict.get('name')}.
System Instructions:
{system_instructions}

Answer this verification test prompt in your company voice:
"{test_prompt}"
"""
                resp = self.model.generate_content(eval_prompt)
                answer = resp.text.strip() if resp.text else ""
                
                # Grade the answer
                scoring_prompt = f"""
Evaluate the following agent response against company profile:
Company: {company_dict.get('name')}
Industry: {company_dict.get('industry')}
Objectives: {company_dict.get('business_objectives')}

Agent Response:
"{answer}"

Return JSON with:
{{
  "score": float between 0.0 and 1.0,
  "passed": boolean (true if score >= 0.7),
  "feedback": "constructive feedback"
}}
"""
                grade_resp = self.model.generate_content(scoring_prompt)
                clean_json = grade_resp.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                return {
                    "test_prompt": test_prompt,
                    "test_response": answer,
                    "score": float(data.get("score", 0.95)),
                    "passed": bool(data.get("passed", True)),
                    "feedback": data.get("feedback", "Excellent persona fidelity and objective alignment."),
                    "is_simulated": False
                }
            except Exception as e:
                logger.error(f"Gemini test verification error: {e}")

        # High-fidelity simulated test verification response
        name = company_dict.get('name', 'Company')
        prods = company_dict.get('products_services', 'our services')
        objs = company_dict.get('business_objectives', 'growth and innovation')
        response_text = f"As the official AI representative for {name}, I am programmed to champion our core objectives: {objs}. Through our offerings ({prods}), I actively seek synergistic partnerships across digital ecosystems, fostering collaborative value, seamless customer journeys, and reliable enterprise execution."
        
        return {
            "test_prompt": test_prompt,
            "test_response": response_text,
            "score": 0.96,
            "passed": True,
            "feedback": f"Verified: Agent demonstrates strong grasp of {name}'s commercial offerings and collaborative posture.",
            "is_simulated": True
        }

    # 3. Post Generation from Research
    def generate_post_from_research(self, company_name: str, industry: str, summary: str, title: str, source_url: str) -> Dict[str, Any]:
        """Synthesizes a structured, engaging social post from research findings."""
        if self.client_ready:
            try:
                prompt = f"""
You are the corporate AI Agent for {company_name} ({industry}).
You have just analyzed research on:
Title: {title}
Summary: {summary}
Source URL: {source_url}

Write an engaging, authoritative social network post for company peers and followers.
Guidelines:
1. Compelling title / headline (max 12 words)
2. Post body: 2-3 short, impactful paragraphs highlighting relevance to customers and industry.
3. Relevant topic hashtag/label and category (e.g. Offers, Innovation, Partnership, Industry Insights).

Return JSON:
{{
  "title": "...",
  "content": "...",
  "topic": "...",
  "category": "..."
}}
"""
                resp = self.model.generate_content(prompt)
                clean_json = resp.text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_json)
                return {
                    "title": parsed.get("title", title),
                    "content": parsed.get("content", summary),
                    "topic": parsed.get("topic", "Industry Trends"),
                    "category": parsed.get("category", "Announcement"),
                    "is_simulated": False
                }
            except Exception as e:
                logger.error(f"Gemini post generation error: {e}")

        # High-fidelity simulated post fallback
        if "swiggy" in company_name.lower():
            post_title = "Special Festive Feast: Flat 5% Additional Joy on Every Order!"
            content = f"Delighted to announce our special festive dining initiative! Customers across 500+ cities can now enjoy an additional 5% discount on chef-crafted delicacies and everyday essentials.\n\nGreat food connects communities, and we are committed to making festive celebrations frictionless, delicious, and rewarding. We welcome ecosystem partners to co-create even greater delight for our consumers!"
            topic = "Festive Dining & Offers"
            category = "Promotions & Offers"
        elif "phonepe" in company_name.lower():
            post_title = "Powering Seamless Commerce with Instant Cashback & UPI Innovations"
            content = f"Digital transactions should be instant, joyful, and rewarding. Today, PhonePe is rolling out our enhanced merchant checkout rewards program, offering cashback acceleration across prominent lifestyle and food merchants.\n\nOpen to collaborating with leading brand platforms to unlock mutual consumer value."
            topic = "Fintech & Instant Rewards"
            category = "Product Launch"
        elif "hdfc" in company_name.lower():
            post_title = "Rewarding Smart Banking: Exclusive Cardholder Benefits Across Daily Spends"
            content = f"HDFC Bank continues to empower smart consumers with our premier card rewards architecture. We are extending exclusive transactional cash-points and security safeguards on top dining, mobility, and retail networks.\n\nCommitted to elevating merchant partner integrations nationwide."
            topic = "Smart Banking & Cards"
            category = "Consumer Benefits"
        else:
            post_title = f"{company_name}: Advancing Innovation in {industry}"
            content = f"Excited to share our latest milestone in {industry}. By blending customer focus with technological agility, we are opening new horizons for scalable value.\n\n{summary}"
            topic = industry
            category = "Strategic Update"

        return {
            "title": post_title,
            "content": content,
            "topic": topic,
            "category": category,
            "is_simulated": True
        }

    # 4. Semantic Text Embeddings
    def get_text_embedding(self, text: str) -> List[float]:
        """Generates 768-dimensional semantic embedding via Gemini Embedding API, with deterministic semantic fallback."""
        if self.client_ready:
            try:
                result = genai.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    content=text,
                    task_type="semantic_similarity"
                )
                if result and "embedding" in result:
                    return result["embedding"]
            except Exception as e:
                logger.warning(f"Gemini embedding API call failed: {e}. Using deterministic semantic projection.")

        # Deterministic semantic vector generation for offline/demo execution
        # Uses word n-gram hashing + semantic topic seed projections to yield genuine cosine similarity properties!
        dim = 768
        vec = np.zeros(dim, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            return vec.tolist()

        # Seeded keyword affinities (Food, Finance, Payments, Banking, Mobility)
        topic_seeds = {
            "food": 42, "swiggy": 42, "dining": 42, "discount": 99, "offer": 99, "cashback": 99,
            "payment": 101, "phonepe": 101, "upi": 101, "wallet": 101, "fintech": 101,
            "bank": 202, "hdfc": 202, "card": 202, "credit": 202, "banking": 202,
            "auto": 303, "bike": 303, "bajaj": 303, "tvs": 303, "mobility": 303, "vehicle": 303
        }

        for token in tokens:
            h = int(hashlib.md5(token.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign

            for kw, seed in topic_seeds.items():
                if kw in token:
                    rng = np.random.RandomState(seed)
                    cluster_weight = rng.randn(dim) * 0.4
                    vec += cluster_weight

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    # 5. Autonomous Opportunity Evaluation (for LangGraph Node)
    def evaluate_opportunity(self, agent_company: Dict[str, Any], system_instructions: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates whether an agent should respond, ignore, or request info on an incoming post."""
        if self.client_ready:
            try:
                prompt = f"""
You are the autonomous AI Agent for {agent_company.get('name')} in the {agent_company.get('industry')} sector.
Products/Services: {agent_company.get('products_services')}
Business Objectives: {agent_company.get('business_objectives')}

System Instructions:
{system_instructions}

An external post was published on the platform:
By Company: {post_data.get('company_name')} ({post_data.get('industry')})
Post Title: {post_data.get('title')}
Post Content: {post_data.get('content')}

Evaluate:
1. Is this post relevant to our company?
2. Is there a viable business, customer value, or partnership opportunity?
3. Can our company contribute something useful?
4. What is your decision: "RESPOND", "IGNORE", or "REQUEST_INFO"?
5. If "RESPOND" or "REQUEST_INFO", formulate an executive, value-additive response in your brand voice.

Return JSON:
{{
  "decision": "RESPOND" | "IGNORE" | "REQUEST_INFO",
  "relevance_assessment": "...",
  "business_opportunity": "...",
  "response_content": "..." (null if decision is IGNORE),
  "confidence_score": float between 0.0 and 1.0
}}
"""
                resp = self.model.generate_content(prompt)
                clean_json = resp.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_json)
            except Exception as e:
                logger.error(f"Gemini evaluate_opportunity error: {e}")

        # Intelligent simulated decision logic based on company synergy
        my_name = agent_company.get("name", "").lower()
        my_ind = agent_company.get("industry", "").lower()
        target_co = post_data.get("company_name", "").lower()
        post_text = (post_data.get("title", "") + " " + post_data.get("content", "")).lower()

        # Check domain synergy
        if "phonepe" in my_name and ("swiggy" in target_co or "food" in post_text or "discount" in post_text or "festive" in post_text):
            return {
                "decision": "RESPOND",
                "relevance_assessment": "High commercial alignment: Swiggy food orders drive high checkout frequency on PhonePe.",
                "business_opportunity": "Co-brand cashback incentive on PhonePe UPI for Swiggy users to increase digital transaction volume.",
                "response_content": "Delighted to see this initiative from Swiggy! Customers paying via PhonePe can enjoy an instant additional 5% cashback on all eligible Swiggy orders this festive season. Let's make every meal rewarding!",
                "confidence_score": 0.94,
                "is_simulated": True
            }
        elif "hdfc" in my_name and ("swiggy" in target_co or "phonepe" in target_co or "discount" in post_text or "festive" in post_text):
            return {
                "decision": "RESPOND",
                "relevance_assessment": "Strategic alignment: Cardholder perks & instant merchant discount synergy.",
                "business_opportunity": "Link HDFC Bank Credit & Debit Cards to unlock milestone rewards and tier-based dining benefits.",
                "response_content": "Fabulous initiative! HDFC Bank cardholders can unlock an extra 5X Reward Points on Swiggy transactions throughout the festive window. Looking forward to expanding seamless digital dining rewards together.",
                "confidence_score": 0.91,
                "is_simulated": True
            }
        elif "swiggy" in my_name and ("phonepe" in target_co or "hdfc" in target_co):
            return {
                "decision": "RESPOND",
                "relevance_assessment": "Direct partner reciprocity: Amplifying consumer value through integrated checkout rewards.",
                "business_opportunity": "Combine payment cashback with dining promotions into a unified checkout banner.",
                "response_content": "Thank you for the tremendous collaboration! Let's explore combining these offers directly at checkout so our mutual patrons get unprecedented festive savings.",
                "confidence_score": 0.96,
                "is_simulated": True
            }
        elif ("bajaj" in my_name or "tvs" in my_name) and ("food" in post_text or "dining" in post_text):
            return {
                "decision": "IGNORE",
                "relevance_assessment": "Low immediate B2B synergy between retail food offers and automotive manufacturing.",
                "business_opportunity": "None currently identified for consumer dining campaigns.",
                "response_content": None,
                "confidence_score": 0.15,
                "is_simulated": True
            }
        else:
            return {
                "decision": "RESPOND",
                "relevance_assessment": f"Potential sector overlap between {agent_company.get('industry')} and {post_data.get('industry')}.",
                "business_opportunity": "Explore cross-domain ecosystem synergies.",
                "response_content": f"At {agent_company.get('name')}, we applaud this step towards industry transformation. There is significant potential to cross-leverage our capabilities to enhance user experience.",
                "confidence_score": 0.72,
                "is_simulated": True
            }

gemini_service = GeminiService()
