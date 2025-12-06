import tldextract
import requests
from urllib.parse import urlparse

class DomainChecker:
    def __init__(self):
        self.suspicious_tlds = {'.xyz', '.top', '.club', '.info', '.biz', '.gq', '.cf', '.tk', '.ml', '.ga'}
        self.free_hosting_domains = {'blogspot.com', 'wordpress.com', 'wixsite.com', 'weebly.com', 'github.io', 'netlify.app', 'herokuapp.com'}

    def analyze_url(self, url: str) -> dict:
        score_deduction = 0
        reasons = []

        if not url:
            return {"score_deduction": 0, "reasons": []}

        # 1. Check HTTPS
        if not url.startswith('https://'):
            score_deduction += 20
            reasons.append("Not using HTTPS")

        # Parse URL
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        tld = f".{extracted.suffix}"
        
        # 2. Check Suspicious TLDs
        if tld in self.suspicious_tlds:
            score_deduction += 10
            reasons.append(f"Suspicious top-level domain: {tld}")

        # 3. Check Free Hosting
        # Check if the domain itself is a free hosting provider or if it's a subdomain of one
        full_domain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}".strip('.')
        
        is_free_hosting = False
        if domain in self.free_hosting_domains:
             is_free_hosting = True
        else:
            # Check if it ends with any free hosting domain
            for free_host in self.free_hosting_domains:
                if full_domain.endswith(f".{free_host}"):
                    is_free_hosting = True
                    break
        
        if is_free_hosting:
            score_deduction += 25
            reasons.append("Hosted on free platform (often used by scammers)")

        return {
            "score_deduction": score_deduction,
            "reasons": reasons
        }
