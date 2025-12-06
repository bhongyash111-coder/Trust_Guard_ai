from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    AnalyzeResponse, AnalyzeRequest, 
    CompanyAnalysisRequest, CompanyAnalysisResponse,
    EnhancedAnalyzeRequest, EnhancedAnalyzeResponse
)
from app.services.analyzer import Analyzer
from app.services.company_analyzer import CompanyAnalyzer
import sys
import re

# Force UTF-8 encoding for Windows console
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

app = FastAPI(title="TrustGuard AI API", version="1.1.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for hackathon/demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = Analyzer()
company_analyzer = CompanyAnalyzer()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_scam(
    job_url: str = Form(None),
    job_description: str = Form(None)
):
    # 1. Input Constraints & Validation
    if not job_url and not job_description:
        raise HTTPException(status_code=400, detail="Please provide either a Job URL or Job Description.")
    
    # Validate Job Description Length
    if job_description:
        if len(job_description) < 50:
            raise HTTPException(status_code=400, detail="Job description is too short. Please provide at least 50 characters for accurate analysis.")
        if len(job_description) > 20000:
            raise HTTPException(status_code=400, detail="Job description is too long (max 20,000 characters).")

    # 2. Construct Request Object
    
    # Sanitize inputs
    sanitized_text = job_description
    if sanitized_text:
        sanitized_text = sanitized_text.replace("₹", "Rs. ").replace("\u20b9", "Rs. ")
        sanitized_text = sanitized_text.replace("–", "-").replace("—", "-")
        sanitized_text = sanitized_text.replace("“", '"').replace("”", '"')
        sanitized_text = sanitized_text.replace("‘", "'").replace("’", "'")
        sanitized_text = sanitized_text.encode('ascii', 'ignore').decode('ascii')

    try:
        request_data = AnalyzeRequest(
            url=job_url,
            text=sanitized_text
        )
        
        result = analyzer.analyze(request_data)
        return result
    except Exception as e:
        safe_error = str(e).encode('ascii', 'replace').decode('ascii')
        print(f"Error analyzing request: {safe_error}")
        raise HTTPException(status_code=500, detail=safe_error)

@app.post("/analyze/company", response_model=CompanyAnalysisResponse)
async def analyze_company(request: CompanyAnalysisRequest):
    """
    Analyze a company website for legitimacy and trustworthiness.
    
    Args:
        request: CompanyAnalysisRequest with company_url
    
    Returns:
        CompanyAnalysisResponse with company trust score and details
    """
    if not request.company_url:
        raise HTTPException(status_code=400, detail="Company URL is required")
    
    try:
        result = company_analyzer.analyze_company_website(request.company_url)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Company analysis failed"))
        
        # Determine recommended action
        trust_score = result.get("company_trust_score", 0)
        if trust_score >= 70:
            action = "Company appears legitimate - proceed with normal verification"
        elif trust_score >= 50:
            action = "Company shows mixed signals - verify through additional sources"
        else:
            action = "CAUTION: Company shows multiple red flags - thoroughly verify before proceeding"
        
        return CompanyAnalysisResponse(
            success=True,
            company_info=result.get("company_info"),
            company_trust_score=trust_score,
            legitimacy_indicators=result.get("legitimacy_indicators", {}),
            risk_factors=result.get("risk_factors", []),
            recommended_action=action
        )
    
    except HTTPException:
        raise
    except Exception as e:
        safe_error = str(e).encode('ascii', 'replace').decode('ascii')
        print(f"Error analyzing company: {safe_error}")
        raise HTTPException(status_code=500, detail=safe_error)

@app.post("/analyze/enhanced", response_model=EnhancedAnalyzeResponse)
async def analyze_enhanced(
    job_url: str = Form(None),
    job_description: str = Form(None),
    company_url: str = Form(None)
):
    """
    Enhanced job analysis with automatic job scraping and company verification.
    
    NEW: If job_url is provided, automatically scrapes the posting to extract:
    - Job description
    - Company name
    - Company website (for verification)
    """
    from app.services.job_posting_scraper import JobPostingScraper
    
    if not job_url and not job_description:
        raise HTTPException(status_code=400, detail="Please provide either a Job URL or Job Description.")
    
    auto_scraped = False
    extracted_company_name = ""
    
    # AUTO-SCRAPING: If job URL provided, extract everything
    if job_url:
        try:
            job_scraper = JobPostingScraper()
            scrape_result = job_scraper.scrape_job_posting(job_url)
            
            if scrape_result.get("success"):
                job_description = scrape_result.get("job_description", "")
                extracted_company_name = scrape_result.get("company_name", "")
                
                if not company_url:
                    company_url = scrape_result.get("company_website", "")
                
                auto_scraped = True
                print(f"✓ Auto-scraped: Company={extracted_company_name}, URL={company_url}")
            else:
                if not job_description:
                    raise HTTPException(status_code=400, detail=f"Failed to scrape: {scrape_result.get('error')}")
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            if not job_description:
                raise HTTPException(status_code=400, detail=f"Failed to scrape: {str(e)}")
    
    # Extract company from description if not scraped
    if not company_url and job_description and not auto_scraped:
        try:
            job_scraper = JobPostingScraper()
            extracted_company_name = job_scraper.extract_company_from_description(job_description)
            
            if extracted_company_name:
                clean_name = re.sub(r'[^a-z0-9\s]', '', extracted_company_name.lower())
                clean_name = re.sub(r'\s+', '', clean_name)
                company_url = f"https://www.{clean_name}.com"
                print(f"✓ Extracted: {extracted_company_name} -> {company_url}")
        except Exception as e:
            print(f"Extraction error: {str(e)}")
    
    # Validate description
    if job_description:
        if len(job_description) < 50:
            raise HTTPException(status_code=400, detail="Description too short (min 50 chars)")
        if len(job_description) > 20000:
            raise HTTPException(status_code=400, detail="Description too long (max 20,000 chars)")
    
    # Sanitize
    sanitized_text = job_description
    if sanitized_text:
        sanitized_text = sanitized_text.replace("₹", "Rs. ").replace("\u20b9", "Rs. ")
        sanitized_text = sanitized_text.replace("–", "-").replace("—", "-")
        sanitized_text = sanitized_text.replace(""", '"').replace(""", '"')
        sanitized_text = sanitized_text.replace("'", "'").replace("'", "'")
        sanitized_text = sanitized_text.encode('ascii', 'ignore').decode('ascii')
    
    try:
        job_request = AnalyzeRequest(url=job_url, text=sanitized_text)
        result = analyzer.analyze_with_company(job_request, company_url)
        return result
    except Exception as e:
        safe_error = str(e).encode('ascii', 'replace').decode('ascii')
        print(f"Analysis error: {safe_error}")
        raise HTTPException(status_code=500, detail=safe_error)


@app.get("/health/firecrawl")
def firecrawl_health_check():
    """Check if Firecrawl API is configured and accessible."""
    from app.services.firecrawl_client import FirecrawlClient
    
    firecrawl = FirecrawlClient()
    is_configured = bool(firecrawl.api_key)
    
    # Don't actually call the API for health check to avoid rate limits
    return {
        "configured": is_configured,
        "status": "ready" if is_configured else "not_configured",
        "message": "Firecrawl API key found" if is_configured else "Firecrawl API key not set in environment"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
