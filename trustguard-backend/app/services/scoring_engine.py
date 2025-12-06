class ScoringEngine:
    WEIGHTS = {
        "domain_mismatch": 25,
        "messaging_apps": 25,
        "hidden_fees": 40,
        "low_hours_high_pay": 20,
        "vague_description": 10,
        "missing_manager_name": 5,
        "phishing_attempt": 100, # Immediate Scam
    }

    def combine(self, rules, llm, domain_reputation_score):
        # Compute rule-based score
        rule_score = sum(
            self.WEIGHTS[key] for key, val in rules.items() if val
        )
        
        # Add LLM-detected phishing flag to rule score (as it's a binary flag like rules)
        if llm.get("phishing_attempt"):
            rule_score += self.WEIGHTS["phishing_attempt"]

        # Use LLM's score directly
        llm_score = llm.get("llm_score", 0)

        # Final score
        # Note: The user's snippet adds them up. 
        # If rules find fees (+40) and LLM says scam (+80), total is 120.
        # We cap at 100.
        # This means HIGHER score = HIGHER RISK (SCAM).
        # My previous logic was Higher Score = SAFE.
        # I MUST ADAPT THIS. The user's prompt says "scam probability score".
        # So 100 = Scam.
        # My frontend expects 100 = Safe.
        # I will need to INVERT the final score before returning to frontend, 
        # OR update frontend to understand Risk Score.
        # Let's stick to the backend returning "Trust Score" (Safe) to minimize frontend changes.
        # So I will calculate Risk Score first, then Trust Score = 100 - Risk Score.
        
        risk_score = rule_score + llm_score + domain_reputation_score
        final_risk = min(risk_score, 100)
        
        # Invert for Trust Score (0 = Scam, 100 = Safe)
        trust_score = 100 - final_risk

        return {
            "rule_score": rule_score,
            "llm_score": llm_score,
            "domain_reputation_score": domain_reputation_score,
            "final_score": trust_score, 
            "risk_level": (
                "Likely Scam" if final_risk >= 60 else
                "Suspicious" if final_risk >= 30 else
                "Likely Safe"
            ),
            "raw_risk_score": final_risk
        }
