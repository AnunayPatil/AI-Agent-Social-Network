import re
import hashlib
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import httpx

from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class ResearchService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AI-Agent-Research/1.0"
        }

    # Step 3, 4, 5: Fetch, extract, strip tags & normalize
    def fetch_and_clean_url(self, url: str) -> Dict[str, Any]:
        """Scrapes webpage using BeautifulSoup, strips ads/scripts/nav, and normalizes text."""
        try:
            with httpx.Client(timeout=2.0, follow_redirects=True, headers=self.headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    # Remove unwanted tags
                    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
                        element.extract()
                    
                    # Extract page title
                    title_tag = soup.find("title")
                    title = title_tag.get_text().strip() if title_tag else "Extracted Intelligence Article"
                    
                    # Extract article or main paragraphs
                    article = soup.find("article") or soup.find("main") or soup.body
                    if article:
                        paragraphs = article.find_all("p")
                        text_content = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
                    else:
                        text_content = soup.get_text()

                    cleaned_text = self.clean_and_normalize(text_content)
                    return {
                        "url": url,
                        "title": title,
                        "cleaned_text": cleaned_text,
                        "raw_length": len(resp.text),
                        "is_simulated": False
                    }
        except Exception as e:
            logger.warning(f"Live web fetch for {url} failed: {e}. Generating high-fidelity simulated intelligence.")

        # Fallback simulated research data based on URL or generic news
        simulated = self._get_simulated_feed_for_url(url)
        return simulated

    def clean_and_normalize(self, text: str) -> str:
        """Removes extra whitespace, ad fragments, and normalizes sentences."""
        # Remove repeated whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common ad disclaimers
        text = re.sub(r'advertisement|sponsored content|click here to subscribe', '', text, flags=re.IGNORECASE)
        # Clean unicode artifacts
        text = text.encode("ascii", "ignore").decode("ascii")
        return text.strip()

    def compute_content_hash(self, text: str) -> str:
        """Computes SHA-256 hash for deduplication."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    # Step 8: Classify relevant topics using NLP
    def classify_topics(self, text: str, configured_topics: List[str]) -> List[str]:
        """Identifies relevant topics matching company research configuration and NLP keywords."""
        extracted = []
        text_lower = text.lower()
        for topic in configured_topics:
            if topic.lower() in text_lower:
                extracted.append(topic)
        
        # General domain heuristics
        heuristics = {
            "Festive Offers": ["diwali", "festive", "discount", "cashback", "sale", "offer"],
            "Digital Payments": ["upi", "wallet", "payments", "transaction", "cashless"],
            "Consumer Banking": ["credit card", "savings", "banking", "lending", "interest rate"],
            "Food Logistics": ["food delivery", "quick commerce", "cloud kitchen", "groceries"],
            "Electric Vehicles": ["ev", "electric bike", "battery", "two-wheeler", "mobility"]
        }
        for category, kws in heuristics.items():
            if any(kw in text_lower for kw in kws) and category not in extracted:
                extracted.append(category)

        return extracted[:5] if extracted else ["Corporate Strategy"]

    # Generate structured summary and post drafting
    def process_research_pipeline(self, company_name: str, industry: str, configured_topics: List[str], source_url: str) -> Dict[str, Any]:
        """Executes full autonomous research pipeline (Steps 1 to 11)."""
        scraped = self.fetch_and_clean_url(source_url)
        cleaned_text = scraped["cleaned_text"]
        title = scraped["title"]
        content_hash = self.compute_content_hash(cleaned_text)
        
        topics = self.classify_topics(cleaned_text, configured_topics)
        
        # Create concise summary
        sentences = cleaned_text.split(". ")
        summary = ". ".join(sentences[:3]) + "." if len(sentences) >= 3 else cleaned_text
        if len(summary) > 400:
            summary = summary[:397] + "..."

        # Generate company-voiced post via Gemini
        post_draft = gemini_service.generate_post_from_research(
            company_name=company_name,
            industry=industry,
            summary=summary,
            title=title,
            source_url=source_url
        )

        return {
            "source_url": source_url,
            "title": title,
            "cleaned_content": cleaned_text,
            "extracted_topics": topics,
            "summary": summary,
            "content_hash": content_hash,
            "post_title": post_draft["title"],
            "post_content": post_draft["content"],
            "post_topic": post_draft["topic"],
            "post_category": post_draft["category"],
            "is_simulated": scraped.get("is_simulated", False) or post_draft.get("is_simulated", False)
        }

    def _get_simulated_feed_for_url(self, url: str) -> Dict[str, Any]:
        """Provides high-quality realistic news extraction for demo mode when public web is blocked."""
        url_lower = url.lower()
        if "swiggy" in url_lower or "food" in url_lower or "diwali" in url_lower:
            title = "Festive Dining Boom: Indian Consumers Surge Food Delivery Volumes by 40%"
            content = "The festive quarter is witnessing record consumer expenditure across metropolitan and tier-2 markets. Online food delivery platforms are introducing dynamic discount campaigns and merchant subsidies to drive festive cheer. Swiggy announced nationwide festival partner tie-ups with an additional 5% discount across prominent culinary hubs. Industry observers highlight that digital payment rewards and bank card tie-ups will be instrumental in maximizing cart conversions."
        elif "phonepe" in url_lower or "payment" in url_lower or "upi" in url_lower:
            title = "Digital Payment Networks Scale to Record Highs Ahead of National Holidays"
            content = "Unified Payments Interface (UPI) logs over 15 billion monthly transactions as contactless digital spending cements its position. Leading digital payment major PhonePe expanded merchant cashback integrations, targeting seamless checkout experiences across grocery, delivery, and entertainment verticals. Strategic interoperability with retail merchants remains a central driver of customer retention."
        elif "hdfc" in url_lower or "bank" in url_lower or "finance" in url_lower:
            title = "Consumer Banking Trends: Credit Card Rewards Redefine Merchant Partnerships"
            content = "Private sector commercial banking giants, led by HDFC Bank, have unveiled targeted card reward structures tailored to seasonal consumer lifestyle expenditure. Enhanced dining reward multipliers, instant point redemptions, and co-branded merchant promotions are projected to accelerate card spend velocity by 25% year-on-year."
        elif "bajaj" in url_lower or "tvs" in url_lower or "auto" in url_lower:
            title = "Automotive Industry Expands Two-Wheeler EV Fleet Deployments"
            content = "Automotive manufacturers including Bajaj Auto and TVS Motors report accelerating commercial fleet adoption of electric two-wheelers for urban mobility and last-mile logistics. Sustainable battery performance and infrastructure expansion remain key focus areas."
        else:
            title = "Enterprise AI and Ecosystem Interoperability Drive Next-Gen Growth"
            content = "Corporate organizations are increasingly deploying autonomous digital agents to coordinate cross-industry partnerships, automate market intelligence, and deepen consumer engagement across digital platforms."

        return {
            "url": url,
            "title": title,
            "cleaned_text": content,
            "raw_length": len(content),
            "is_simulated": True
        }

research_service = ResearchService()
