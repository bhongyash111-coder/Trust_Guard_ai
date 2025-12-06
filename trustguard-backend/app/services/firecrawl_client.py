import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import requests
import validators

load_dotenv()


class FirecrawlClient:
    """Client for interacting with Firecrawl API for web scraping."""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY", "")
        self.timeout = int(os.getenv("FIRECRAWL_TIMEOUT", "30"))
        self.base_url = "https://api.firecrawl.dev/v1"
        
        if not self.api_key:
            print("WARNING: FIRECRAWL_API_KEY not found in environment variables")
    
    def scrape_url(self, url: str, formats: List[str] = None) -> Dict[str, Any]:
        """
        Scrape a single webpage and return its content.
        
        Args:
            url: The URL to scrape
            formats: List of output formats (markdown, html, etc.)
        
        Returns:
            Dictionary containing scraped data and metadata
        """
        if not validators.url(url):
            return {"success": False, "error": "Invalid URL format"}
        
        if not self.api_key:
            return {"success": False, "error": "Firecrawl API key not configured"}
        
        if formats is None:
            formats = ["markdown", "html"]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": url,
                "formats": formats
            }
            
            response = requests.post(
                f"{self.base_url}/scrape",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "data": data.get("data", {}),
                "metadata": data.get("data", {}).get("metadata", {})
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout - website took too long to respond"}
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 429:
                return {"success": False, "error": "Rate limit exceeded - please try again later"}
            elif status_code == 403:
                return {"success": False, "error": "Access forbidden - website blocked scraping"}
            else:
                return {"success": False, "error": f"HTTP error: {status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Scraping failed: {str(e)}"}
    
    def crawl_website(self, url: str, max_pages: int = 10) -> Dict[str, Any]:
        """
        Crawl multiple pages of a website.
        
        Args:
            url: The starting URL to crawl
            max_pages: Maximum number of pages to crawl
        
        Returns:
            Dictionary containing crawl data and metadata
        """
        if not validators.url(url):
            return {"success": False, "error": "Invalid URL format"}
        
        if not self.api_key:
            return {"success": False, "error": "Firecrawl API key not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": url,
                "limit": max_pages,
                "scrapeOptions": {
                    "formats": ["markdown"]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/crawl",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Get the crawl ID to check status
            crawl_id = data.get("id")
            
            if crawl_id:
                # Note: In production, you'd poll for completion
                # For now, return the initial response
                return {
                    "success": True,
                    "crawl_id": crawl_id,
                    "status": data.get("status", "started"),
                    "message": "Crawl initiated - use crawl_id to check status"
                }
            
            return {"success": False, "error": "No crawl ID returned"}
            
        except Exception as e:
            return {"success": False, "error": f"Crawl failed: {str(e)}"}
    
    def extract_structured_data(self, url: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract structured data from a webpage using AI.
        
        Args:
            url: The URL to extract data from
            schema: Optional schema defining the data structure to extract
        
        Returns:
            Dictionary containing extracted structured data
        """
        if not validators.url(url):
            return {"success": False, "error": "Invalid URL format"}
        
        if not self.api_key:
            return {"success": False, "error": "Firecrawl API key not configured"}
        
        try:
            # For structured extraction, we use scrape with extract options
            result = self.scrape_url(url, formats=["markdown"])
            
            if not result.get("success"):
                return result
            
            # Return the scraped data - LLM will do the structured extraction
            return {
                "success": True,
                "content": result.get("data", {}).get("markdown", ""),
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            return {"success": False, "error": f"Extraction failed: {str(e)}"}
    
    def health_check(self) -> bool:
        """Check if Firecrawl API is accessible."""
        if not self.api_key:
            return False
        
        try:
            # Try scraping a simple page as health check
            result = self.scrape_url("https://example.com", formats=["markdown"])
            return result.get("success", False)
        except:
            return False
