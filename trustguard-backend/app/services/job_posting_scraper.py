import re
from typing import Dict, Optional, Any
from app.services.firecrawl_client import FirecrawlClient
import tldextract


class JobPostingScraper:
    """Automatically scrapes job postings from URLs and extracts structured information."""
    
    def __init__(self):
        self.firecrawl = FirecrawlClient()
    
    def scrape_job_posting(self, job_url: str) -> Dict[str, Any]:
        """
        Scrape a job posting URL and extract job details + company information.
        
        Args:
            job_url: URL to job posting (LinkedIn, Indeed, company career page, etc.)
        
        Returns:
            Dictionary containing job description, company name, company website
        """
        # Scrape the job posting page
        scrape_result = self.firecrawl.scrape_url(job_url, formats=["markdown", "html"])
        
        if not scrape_result.get("success"):
            return {
                "success": False,
                "error": scrape_result.get("error", "Failed to scrape job posting"),
                "job_description": "",
                "company_name": "",
                "company_website": ""
            }
        
        data = scrape_result.get("data", {})
        metadata = scrape_result.get("metadata", {})
        markdown_content = data.get("markdown", "")
        
        # Extract job description (clean content)
        job_description = self._extract_job_description(markdown_content, job_url)
        
        # Extract company name
        company_name = self._extract_company_name(markdown_content, metadata, job_url)
        
        # Find company website
        company_website = self._find_company_website(company_name, markdown_content, job_url)
        
        return {
            "success": True,
            "job_description": job_description,
            "company_name": company_name,
            "company_website": company_website,
            "job_url": job_url
        }
    
    def _extract_job_description(self, content: str, url: str) -> str:
        """Extract clean job description from scraped content."""
        # Remove navigation, headers, footers
        lines = content.split('\n')
        
        # Filter out common non-job-description content
        filtered_lines = []
        skip_patterns = [
            r'sign\s+in',
            r'log\s+in',
            r'register',
            r'cookie',
            r'privacy\s+policy',
            r'terms\s+of\s+service',
            r'copyright',
            r'all\s+rights\s+reserved', 
            r'follow\s+us',
            r'social\s+media'
        ]
        
        for line in lines:
            line_lower = line.lower()
            # Skip if matches skip patterns
            if any(re.search(pattern, line_lower) for pattern in skip_patterns):
                continue
            # Skip very short lines (likely navigation)
            if len(line.strip()) < 10:
                continue
            filtered_lines.append(line)
        
        description = '\n'.join(filtered_lines).strip()
        
        # Ensure minimum length
        if len(description) < 100:
            # Fallback: return original content
            description = content
        
        return description[:10000]  # Cap at 10k chars
    
    def _extract_company_name(self, content: str, metadata: Dict, url: str) -> str:
        """Extract company name from job posting."""
        company_name = ""
        
        # Method 1: Try metadata title
        if metadata.get("title"):
            title = metadata["title"]
            # LinkedIn format: "Job Title at Company Name | LinkedIn"
            if " at " in title:
                parts = title.split(" at ")
                if len(parts) > 1:
                    company_name = parts[1].split("|")[0].strip()
            # Indeed format: "Job Title - Company Name"
            elif " - " in title:
                parts = title.split(" - ")
                if len(parts) > 1:
                    company_name = parts[1].strip()
        
        # Method 2: Search for common patterns in content
        if not company_name:
            patterns = [
                r'Company:\s*([A-Z][A-Za-z0-9\s&,.]+?)(?:\n|$)',
                r'Employer:\s*([A-Z][A-Za-z0-9\s&,.]+?)(?:\n|$)',
                r'Organization:\s*([A-Z][A-Za-z0-9\s&,.]+?)(?:\n|$)',
                r'at\s+([A-Z][A-Za-z0-9\s&,.]{2,30})\s+(?:is|seeks|looking)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    company_name = match.group(1).strip()
                    break
        
        # Method 3: LinkedIn-specific extraction
        if not company_name and "linkedin.com" in url:
            # Look for company name in LinkedIn format
            match = re.search(r'\n([A-Z][A-Za-z0-9\s&,.]{2,50})\n(?:.*?)\n(?:\d+[,\d]*\s+followers|Posted)', content)
            if match:
                company_name = match.group(1).strip()
        
        # Clean up
        if company_name:
            # Remove trailing punctuation
            company_name = re.sub(r'[,.\s]+$', '', company_name)
            # Remove "Inc", "LLC", etc. if very long
            if len(company_name) > 50:
                company_name = re.sub(r',?\s+(Inc\.?|LLC|Ltd\.?|Corporation|Corp\.?)$', '', company_name)
        
        return company_name or "Unknown Company"
    
    def _find_company_website(self, company_name: str, content: str, job_url: str) -> str:
        """
        Find company's official website.
        
        Strategy:
        1. Look for explicit website links in job posting
        2. Extract from job posting domain (if company hosted)
        3. Use company name to search/construct likely domain
        """
        # Method 1: Look for website links in content
        url_patterns = [
            r'(?:Website|Company Website|Visit us|Apply at):\s*(https?://[^\s\)]+)',
            r'(https?://(?:www\.)?[a-zA-Z0-9\-]+\.[a-z]{2,})(?:\s|$|/careers|/jobs)',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match if isinstance(match, str) else match[0]
                # Filter out job boards and social media
                if not any(site in url.lower() for site in ['linkedin', 'indeed', 'glassdoor', 'facebook', 'twitter', 'instagram']):
                    # Basic validation
                    if '.' in url and len(url) > 10:
                        return url.rstrip('/')
        
        # Method 2: If job URL is from company domain (not job board)
        extracted = tldextract.extract(job_url)
        domain = extracted.domain.lower()
        
        # Check if it's NOT a job board
        job_boards = ['linkedin', 'indeed', 'glassdoor', 'monster', 'ziprecruiter', 'careerbuilder']
        if domain not in job_boards and extracted.suffix:
            # This might be the company's career page
            return f"https://www.{extracted.domain}.{extracted.suffix}"
        
        # Method 3: Construct from company name
        if company_name and company_name != "Unknown Company":
            # Clean company name for domain
            clean_name = company_name.lower()
            clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
            clean_name = re.sub(r'\s+', '', clean_name)  # Remove spaces
            
            # Try .com first (most common)
            return f"https://www.{clean_name}.com"
        
        return ""
    
    def extract_company_from_description(self, job_description: str) -> str:
        """
        Extract company name from job description text.
        Used when user provides description text instead of URL.
        """
        patterns = [
            r'(?:Company|Employer|Organization):?\s*([A-Z][A-Za-z0-9\s&,.]{2,50})',
            r'(?:at|@)\s+([A-Z][A-Za-z0-9\s&,.]{2,40})\s+(?:is|are|seeks|looking|hiring)',
            r'Join\s+(?:the\s+)?([A-Z][A-Za-z0-9\s&,.]{2,40})\s+team',
            r'([A-Z][A-Za-z0-9\s&,.]{2,40})\s+is\s+(?:seeking|hiring|looking\s+for)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_description)
            if match:
                company_name = match.group(1).strip()
                # Clean up
                company_name = re.sub(r'[,.\s]+$', '', company_name)
                return company_name
        
        return ""
