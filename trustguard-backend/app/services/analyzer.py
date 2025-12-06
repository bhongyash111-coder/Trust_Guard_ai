from app.models import AnalyzeRequest, AnalyzeResponse, EnhancedAnalyzeResponse, CompanyInfo
from app.services.domain_checker import DomainChecker
from app.services.rules_engine import RulesEngine
from app.services.llm_client import LLMClient
from app.services.company_analyzer import CompanyAnalyzer
from typing import Optional

class Analyzer:
    def __init__(self):
        self.domain_checker = DomainChecker()
        self.rules_engine = RulesEngine()
        self.llm_client = LLMClient()
        self.company_analyzer = CompanyAnalyzer()

    def analyze(self, request: AnalyzeRequest) -> AnalyzeResponse:
        # 1. Domain Analysis
        domain_reputation_score = 0
        domain_reasons = []
        if request.url:
            domain_result = self.domain_checker.analyze_url(request.url)
            domain_reputation_score = domain_result["score_deduction"] # This is actually a deduction, so it's "Risk Score"
            domain_reasons = domain_result["reasons"]

        # 2. Rules Engine Analysis
        rules_data = self.rules_engine.analyze(request.text or "")
        
        # 3. LLM Semantic Analysis
        # No extra context needed now
        llm_data = self.llm_client.analyze(request.text or "")

        # 4. Scoring Engine
        from app.services.scoring_engine import ScoringEngine
        scoring_engine = ScoringEngine()
        
        score_result = scoring_engine.combine(rules_data, llm_data, domain_reputation_score)
        
        # Collect Reasons
        all_reasons = []
        all_reasons.extend(domain_reasons)
        
        # Map rules to reasons
        if rules_data["domain_mismatch"]: all_reasons.append("Application link does not match company domain")
        if rules_data["messaging_apps"]: all_reasons.append("Uses Telegram/WhatsApp for hiring")
        if rules_data["hidden_fees"]: all_reasons.append("Mentions hidden fees or deposits")
        if rules_data["low_hours_high_pay"]: all_reasons.append("Unrealistic high pay for low hours")
        if rules_data["vague_description"]: all_reasons.append("Vague job description")
        if rules_data["missing_manager_name"]: all_reasons.append("No hiring manager or recruiter name")
        
        # Map LLM flags to reasons
        if llm_data.get("error"):
            all_reasons.append("⚠️ AI Analysis Failed: Could not connect to local model. Results are based on rules only.")
        
        if llm_data.get("phishing_attempt"): all_reasons.append("AI detected PHISHING attempt (Security Alert Scam)")
        if llm_data.get("hidden_fees"): all_reasons.append("AI detected hidden fees")
        if llm_data.get("unrealistic_salary"): all_reasons.append("AI detected unrealistic salary")
        if llm_data.get("company_unclear"): all_reasons.append("AI detected unclear company identity")

        # Structured Logging (Privacy Aware)
        print(f"Analysis Log: JobURL={bool(request.url)}, JobText={bool(request.text)}")
        print(f"Result: Score={score_result['final_score']}, Label={score_result['risk_level']}")

        return AnalyzeResponse(
            trust_score=score_result["final_score"],
            label=score_result["risk_level"],
            reasons=list(set(all_reasons)),
            recommended_action="Proceed with caution." if score_result["final_score"] > 60 else "Do NOT pay or share personal details."
        )
    
    def analyze_with_company(self, job_data: AnalyzeRequest, company_url: Optional[str] = None) -> EnhancedAnalyzeResponse:
        """
        Enhanced analysis that includes company verification.
        
        Args:
            job_data: Job posting data to analyze
            company_url: Optional company website URL for verification
        
        Returns:
            EnhancedAnalyzeResponse with job and company analysis
        """
        # First, do the standard job analysis
        job_analysis = self.analyze(job_data)
        
        # Initialize response with job analysis results
        response_data = {
            "trust_score": job_analysis.trust_score,
            "label": job_analysis.label,
            "reasons": job_analysis.reasons,
            "recommended_action": job_analysis.recommended_action,
            "company_verified": False
        }
        
        # If company URL provided, analyze the company
        if company_url:
            try:
                company_result = self.company_analyzer.analyze_company_website(company_url)
                
                if company_result.get("success"):
                    company_info = company_result.get("company_info", {})
                    company_trust = company_result.get("company_trust_score", 0)
                    
                    # Create CompanyInfo object
                    company_info_obj = CompanyInfo(**company_info) if company_info else None
                    
                    # Calculate combined trust score (60% job, 40% company)
                    combined_score = int((job_analysis.trust_score * 0.6) + (company_trust * 0.4))
                    
                    # Update response with company data
                    response_data.update({
                        "company_verified": True,
                        "company_trust_score": company_trust,
                        "company_name": company_info.get("company_name", "Unknown"),
                        "company_risk_factors": company_result.get("risk_factors", []),
                        "combined_trust_score": combined_score,
                        "company_info": company_info_obj
                    })
                    
                    # Update label based on combined score
                    if combined_score >= 70:
                        response_data["label"] = "Low Risk (Verified)"
                    elif combined_score >= 50:
                        response_data["label"] = "Medium Risk (Verified)"
                    elif combined_score >= 30:
                        response_data["label"] = "High Risk (Verified)"
                    else:
                        response_data["label"] = "Critical Risk (Verified)"
                    
                    # Add company insights to reasons
                    if company_trust < 50:
                        response_data["reasons"].append(f"⚠️ Company website shows low legitimacy (Trust: {company_trust}/100)")
                    elif company_trust >= 70:
                        response_data["reasons"].append(f"✓ Company website appears legitimate (Trust: {company_trust}/100)")
                    
                    # Update recommended action based on combined analysis
                    if combined_score >= 60:
                        response_data["recommended_action"] = "Company verified - proceed with normal caution."
                    else:
                        response_data["recommended_action"] = "CAUTION: Both job and company show risk factors. Do NOT share personal details or pay fees."
                
                else:
                    # Company analysis failed
                    response_data["reasons"].append(f"⚠️ Could not verify company website: {company_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                # Handle company analysis errors gracefully
                print(f"Company analysis error: {str(e)}")
                response_data["reasons"].append("⚠️ Company verification failed - error during analysis")
        
        return EnhancedAnalyzeResponse(**response_data)

