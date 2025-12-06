import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import tldextract
from app.services.firecrawl_client import FirecrawlClient
from app.services.llm_client import LLMClient


class CompanyAnalyzer:
    """Analyzes company websites to determine legitimacy and trustworthiness."""
    
    def __init__(self):
        self.firecrawl = FirecrawlClient()
        self.llm_client = LLMClient()
    
    def analyze_company_website(self, company_url: str) -> Dict[str, Any]:
        """
        Analyze a company's website to extract information and assess legitimacy.
        
        Args:
            company_url: The company's website URL
        
        Returns:
            Dictionary containing company analysis results
        """
        # Scrape the company website
        scrape_result = self.firecrawl.scrape_url(company_url, formats=["markdown", "html"])
        
        if not scrape_result.get("success"):
            return {
                "success": False,
                "error": scrape_result.get("error", "Failed to scrape company website"),
                "company_trust_score": 0,
                "legitimacy_indicators": {}
            }
        
        data = scrape_result.get("data", {})
        metadata = scrape_result.get("metadata", {})
        markdown_content = data.get("markdown", "")
        html_content = data.get("html", "")
        
        # Extract company information
        company_info = self._extract_company_info(company_url, markdown_content, metadata)
        
        # Check legitimacy indicators
        legitimacy = self._check_legitimacy_indicators(markdown_content, html_content, company_url)
        
        # Analyze with LLM for deeper insights
        llm_analysis = self._llm_company_analysis(markdown_content, company_url)
        
        # Calculate company trust score
        trust_score = self._calculate_company_trust_score(legitimacy, llm_analysis)
        
        # Merge LLM profile data into company info
        if llm_analysis.get("company_profile"):
            profile = llm_analysis.get("company_profile", {})
            company_info.update({
                "industry": profile.get("industry", "Unknown"),
                "employee_count": profile.get("employee_count", "Unknown"),
                "company_type": profile.get("company_type", "Unknown"),
                "revenue": profile.get("revenue", "Unknown"),
                "location": profile.get("location", "Unknown"),
                "founding_year": profile.get("founding_year", "Unknown"),
                "tagline": profile.get("tagline", "")
            })
        
        # Add timeline and social stats
        company_info["timeline"] = llm_analysis.get("timeline", [])
        if llm_analysis.get("social_media_stats"):
            company_info["social_media_stats"] = llm_analysis.get("social_media_stats", [])

        return {
            "success": True,
            "company_info": company_info,
            "legitimacy_indicators": legitimacy,
            "llm_insights": llm_analysis,
            "company_trust_score": trust_score,
            "risk_factors": self._identify_risk_factors(legitimacy, llm_analysis)
        }
    
    def _extract_company_info(self, url: str, content: str, metadata: Dict) -> Dict[str, Any]:
        """Extract basic company information from scraped content."""
        extracted_domain = tldextract.extract(url)
        domain = f"{extracted_domain.domain}.{extracted_domain.suffix}"
        
        # Extract from metadata
        company_name = metadata.get("title", "").split("-")[0].strip() if metadata.get("title") else ""
        description = metadata.get("description", "")
        
        # Look for contact information in content
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        emails = list(set(re.findall(email_pattern, content)))[:3]  # Max 3 emails
        phones = list(set(re.findall(phone_pattern, content)))[:2]  # Max 2 phones
        
        # Look for social media links
        social_links = {
            "linkedin": bool(re.search(r'linkedin\.com/company/', content, re.I)),
            "twitter": bool(re.search(r'twitter\.com/', content, re.I) or re.search(r'x\.com/', content, re.I)),
            "facebook": bool(re.search(r'facebook\.com/', content, re.I)),
        }
        
        # Regex fallbacks for enhanced fields
        founding_year = "Unknown"
        year_match = re.search(r'(?:founded|established|started)\s+(?:in\s+)?(\d{4})', content, re.I)
        if year_match:
            founding_year = year_match.group(1)
            
        location = "Unknown"
        loc_match = re.search(r'(?:headquartered|based|located)\s+in\s+([A-Z][a-zA-Z\s,]+)(?:\.|,)', content)
        if loc_match:
            location = loc_match.group(1).strip()
            
        employee_count = "Unknown"
        emp_match = re.search(r'(\d+(?:,\d+)?\+?)\s+employees', content, re.I)
        if emp_match:
            employee_count = emp_match.group(1)

        return {
            "domain": domain,
            "company_name": company_name,
            "description": description,
            "emails": emails,
            "phones": phones,
            "social_media": social_links,
            "has_contact_info": bool(emails or phones),
            # Initialize enhanced fields with fallbacks
            "industry": "Unknown",
            "employee_count": employee_count,
            "company_type": "Unknown",
            "revenue": "Unknown",
            "location": location,
            "founding_year": founding_year,
            "tagline": "",
            "social_media_stats": [],
            "timeline": []
        }
    
    def _check_legitimacy_indicators(self, markdown: str, html: str, url: str) -> Dict[str, Any]:
        """Check various legitimacy indicators on the website."""
        indicators = {}
        
        content_lower = markdown.lower()
        
        # Check for essential pages
        indicators["has_about_page"] = bool(
            re.search(r'\babout\s+(us|page|company)\b', content_lower) or
            re.search(r'\bour\s+story\b', content_lower) or
            '/about' in content_lower
        )
        
        indicators["has_contact_page"] = bool(
            re.search(r'\bcontact\s+(us|page)\b', content_lower) or
            '/contact' in content_lower
        )
        
        indicators["has_careers_page"] = bool(
            re.search(r'\bcareers?\b', content_lower) or
            re.search(r'\bjobs?\b', content_lower) or
            '/careers' in content_lower or
            '/jobs' in content_lower
        )
        
        indicators["has_privacy_policy"] = bool(
            re.search(r'\bprivacy\s+policy\b', content_lower) or
            '/privacy' in content_lower
        )
        
        indicators["has_terms_of_service"] = bool(
            re.search(r'\bterms\s+(of\s+service|and\s+conditions)\b', content_lower) or
            '/terms' in content_lower
        )
        
        # Check for SSL (https)
        indicators["has_ssl"] = url.startswith("https://")
        
        # Check for professional language (heuristic)
        spam_keywords = ['earn money fast', 'work from home easy', 'guaranteed income', 
                        'no experience needed', 'get rich quick', 'limited time offer']
        indicators["has_spam_language"] = any(keyword in content_lower for keyword in spam_keywords)
        
        # Check content length (legitimate companies usually have substantial content)
        indicators["sufficient_content"] = len(markdown) > 500
        
        # Check for company registration/legal info
        indicators["has_legal_info"] = bool(
            re.search(r'\b(registered|incorporated|llc|ltd|inc|corporation)\b', content_lower)
        )
        
        return indicators
    
    def _llm_company_analysis(self, content: str, url: str) -> Dict[str, Any]:
        """Use LLM to analyze company website content for legitimacy."""
        # Truncate content if too long
        max_length = 3000
        truncated_content = content[:max_length] if len(content) > max_length else content
        
        prompt = f"""
Analyze this company website content and provide a detailed profile and legitimacy assessment.

Website URL: {url}

Content:
\"\"\"{truncated_content}\"\"\"

Evaluate and return JSON with:
1. Legitimacy Assessment (Score 0-100, Fraud/Scam indicators)
2. Company Profile (Industry, Employee Count, Revenue, Type, Location, Founding Year, Tagline)
3. Social Media Stats (Estimate follower counts if mentioned, e.g., "10k+ followers")
4. Company Timeline (Chronological list of major events/milestones found in text)

Return JSON only:
{{
    "appears_legitimate": true/false,
    "appears_fraudulent": true/false,
    "has_red_flags": true/false,
    "provides_clear_info": true/false,
    "legitimacy_score": number,
    "key_observations": ["observation1", "observation2"],
    "company_profile": {{
        "industry": "string",
        "employee_count": "string (e.g. '1000-5000')",
        "company_type": "string (Public/Private)",
        "revenue": "string (e.g. '$10M+')",
        "location": "string",
        "founding_year": "string",
        "tagline": "string"
    }},
    "social_media_stats": [
        {{"platform": "LinkedIn", "url": "string", "followers": "string"}},
        {{"platform": "Twitter", "url": "string", "followers": "string"}}
    ],
    "timeline": [
        {{"year": "YYYY", "event": "Description of event"}}
    ]
}}
"""
        
        try:
            # Use existing LLM client infrastructure
            # Note: We're reusing the analyze method but with a custom prompt
            import requests
            import json
            import os
            
            api_key = os.getenv("LLM_API_KEY", "")
            api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            payload = {
                "model": "mistralai/mixtral-8x7b-instruct-v0.1",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
                "temperature": 0.1
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Clean JSON response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
        
        except Exception as e:
            print(f"LLM Company Analysis Error: {str(e)}")
            return {
                "appears_legitimate": None,
                "appears_fraudulent": None,
                "has_red_flags": None,
                "provides_clear_info": None,
                "legitimacy_score": 50,  # Neutral when LLM fails
                "error": str(e)
            }
    
    def _calculate_company_trust_score(self, indicators: Dict, llm_analysis: Dict) -> int:
        """Calculate overall company trust score from 0-100."""
        score = 50  # Start with neutral
        
        # Add points for legitimacy indicators
        if indicators.get("has_ssl"): score += 5
        if indicators.get("has_about_page"): score += 5
        if indicators.get("has_contact_page"): score += 5
        if indicators.get("has_careers_page"): score += 5
        if indicators.get("has_privacy_policy"): score += 3
        if indicators.get("has_terms_of_service"): score += 3
        if indicators.get("has_legal_info"): score += 4
        if indicators.get("sufficient_content"): score += 5
        
        # Deduct points for red flags
        if indicators.get("has_spam_language"): score -= 20
        
        # Incorporate LLM analysis
        llm_score = llm_analysis.get("legitimacy_score", 50)
        if llm_analysis.get("appears_fraudulent"): score -= 30
        if llm_analysis.get("has_red_flags"): score -= 15
        if llm_analysis.get("appears_legitimate"): score += 10
        if llm_analysis.get("provides_clear_info"): score += 5
        
        # Weighted average with LLM score
        final_score = int((score * 0.6) + (llm_score * 0.4))
        
        # Clamp between 0-100
        return max(0, min(100, final_score))
    
    def _identify_risk_factors(self, indicators: Dict, llm_analysis: Dict) -> List[str]:
        """Identify specific risk factors from the analysis."""
        risks = []
        
        if not indicators.get("has_ssl"):
            risks.append("Website does not use HTTPS encryption")
        
        if not indicators.get("has_contact_page"):
            risks.append("No contact page found")
        
        if not indicators.get("has_about_page"):
            risks.append("No 'About Us' page found")
        
        if indicators.get("has_spam_language"):
            risks.append("Contains spam or suspicious language")
        
        if not indicators.get("sufficient_content"):
            risks.append("Website has minimal content")
        
        if llm_analysis.get("appears_fraudulent"):
            risks.append("AI detected fraudulent indicators")
        
        if llm_analysis.get("has_red_flags"):
            risks.append("AI detected red flags in content")
        
        if not indicators.get("has_legal_info"):
            risks.append("No company registration or legal information found")
        
        # Add LLM observations
        if llm_analysis.get("key_observations"):
            for obs in llm_analysis.get("key_observations", [])[:3]:  # Max 3
                risks.append(f"AI: {obs}")
        
        return risks
    
    def analyze_job_history(self, company_url: str) -> Dict[str, Any]:
        """
        Analyze company's job posting history and patterns.
        Currently returns basic analysis - can be enhanced with crawling.
        """
        # For now, scrape the careers page
        careers_urls = [
            f"{company_url}/careers",
            f"{company_url}/jobs",
            f"{company_url}/careers.html",
            f"{company_url}/about/careers"
        ]
        
        job_content = ""
        for careers_url in careers_urls:
            result = self.firecrawl.scrape_url(careers_url, formats=["markdown"])
            if result.get("success"):
                job_content = result.get("data", {}).get("markdown", "")
                break
        
        if not job_content:
            return {
                "success": False,
                "message": "No careers page found",
                "job_count_estimate": 0
            }
        
        # Simple heuristic: count job-related patterns
        job_patterns = [
            r'\bjob\s+title\b',
            r'\bposition\b',
            r'\bapply\s+now\b',
            r'\bopen\s+position',
            r'\bhiring\b'
        ]
        
        job_mentions = sum(len(re.findall(pattern, job_content, re.I)) for pattern in job_patterns)
        
        return {
            "success": True,
            "job_count_estimate": min(job_mentions, 50),  # Cap at 50
            "has_active_listings": job_mentions > 0,
            "careers_page_found": True
        }
