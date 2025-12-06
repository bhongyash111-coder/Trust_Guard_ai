import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        # Using Nvidia NIM Cloud API
        self.api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        self.model_id = "mistralai/mixtral-8x7b-instruct-v0.1"
        self.api_key = os.getenv("LLM_API_KEY", "dummy") # Use env key if present, else dummy

    def analyze(self, job_text: str, context: str = "") -> dict:
        """
        Analyzes text using local LLM to detect scam patterns.
        Returns a dictionary with structured risk flags and scam probability.
        """
        if not job_text:
            return {"llm_score": 0}

        # Heuristic fallback for explicit keywords (Fail-Secure)
        if "fake" in job_text.lower() or "scam" in job_text.lower():
             return {
                "hidden_fees": True,
                "domain_mismatch": False,
                "messaging_apps": False,
                "unrealistic_salary": False,
                "vague_role": False,
                "company_unclear": False,
                "llm_score": 100 # Max scam score
            }

        prompt = f"""
You are a scam detection AI. You analyze text from job posts, emails, and messages to detect fraud.

Analyze the following text and return the findings in pure JSON only.

Text to analyze:
\"""{job_text}\"""

Context (User Profile):
\"""{context}\"""

Evaluate the following:

1. Is this a "Security Alert" or "Phishing" attempt (e.g., "verify account", "unusual login")?
2. Are there hints of hidden fees or deposits?
3. Does the application URL match the company name?
4. Is the job using Telegram/WhatsApp for hiring?
5. Is the salary unrealistic for the hours?
6. Is the job description vague?
7. Is the company identity unclear?
8. Final scam probability score from 0 to 100 (0 = Safe, 100 = Scam).

Return JSON only in this format:
{{
    "phishing_attempt": true/false,
    "hidden_fees": true/false,
    "domain_mismatch": true/false,
    "messaging_apps": true/false,
    "unrealistic_salary": true/false,
    "vague_role": true/false,
    "company_unclear": true/false,
    "llm_score": number
}}
"""

        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.1
        }

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            print(f"DEBUG LLM RAW RESPONSE: {content}") # Debug log

            # Clean content
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)

        except Exception as e:
            safe_error = str(e).encode('ascii', 'replace').decode('ascii')
            print(f"LLM API Error: {safe_error}")
            return {"llm_score": 0, "error": safe_error}

