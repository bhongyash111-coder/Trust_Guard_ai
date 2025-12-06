import re
import tldextract

class RulesEngine:
    def __init__(self):
        pass

    # Extract company name from text (simple heuristic)
    def extract_company(self, text):
        match = re.search(r"Company[:\s]+(.+)", text, re.I)
        if match:
            name = match.group(1).strip()
            name = name.split("(")[0].strip()
            return name
        return None

    def domain_mismatch(self, text, company):
        urls = re.findall(r'https?://\S+', text)
        if not urls or not company:
            return False

        for url in urls:
            domain = tldextract.extract(url).domain.lower()
            if company.lower().replace(" ", "") not in domain:
                return True
        return False

    def uses_messaging_apps(self, text):
        return bool(re.search(r"\b(telegram|whatsapp|signal|dm me|contact on)\b", text, re.I))

    def hidden_fees(self, text):
        patterns = [
            r"refundable",
            r"processing fee",
            r"charges may apply",
            r"orientation fee",
            r"verification charge",
            r"deposit",
            r"registration fee",
            r"security deposit",
            r"pay first",
            r"activation fee"
        ]
        return any(re.search(p, text, re.I) for p in patterns)

    def low_hours_high_pay(self, text):
        low_hours = re.search(r"(1|2|3)\s*hours", text, re.I)
        # Matches Rs. 20,000, Rs 20000, etc.
        good_salary = re.search(r"(?:Rs\.?|INR)\s*(2|3|4|5)[\d,]{3,}", text, re.I)
        return bool(low_hours and good_salary)

    def vague_description(self, text):
        vague_terms = [
            "update logs",
            "verify documents",
            "coordinate tasks",
            "daily reports",
            "simple tasks",
            "basic responsibilities"
        ]
        return sum(v in text.lower() for v in vague_terms) >= 2

    def missing_hiring_manager(self, text):
        return not bool(re.search(r"(hiring manager|recruiter|manager:|report to)", text, re.I))

    def analyze(self, text):
        company = self.extract_company(text)

        return {
            "domain_mismatch": self.domain_mismatch(text, company),
            "messaging_apps": self.uses_messaging_apps(text),
            "hidden_fees": self.hidden_fees(text),
            "low_hours_high_pay": self.low_hours_high_pay(text),
            "vague_description": self.vague_description(text),
            "missing_manager_name": self.missing_hiring_manager(text),
        }
