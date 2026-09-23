from typing import List, Dict, Any, Tuple

class RiskEngine:
    """
    Standardized, Evidence-Calibrated Risk Scoring & Verdict Classification.
    Strictly follows:
    - Critical: +25
    - High: +15
    - Medium: +8
    - Low: +3
    - Info: +0
    Capped at 100.
    """

    SEVERITY_WEIGHTS = {
        "critical": 25,
        "high": 15,
        "medium": 8,
        "low": 3,
        "info": 0,
    }

    def compute_score(self, findings: List[Dict[str, Any]]) -> int:
        score = 0
        for f in findings:
            sev = f.get("severity", "info").lower()
            score += self.SEVERITY_WEIGHTS.get(sev, 0)
        return min(score, 100)

    def classify_status(self, score: int) -> str:
        if score == 0:
            return "clean"
        elif score <= 20:
            return "low"
        elif score <= 45:
            return "medium"
        elif score <= 75:
            return "high"
        return "critical"

    def classify_url_verdict(
        self,
        score: int,
        findings: List[Dict[str, Any]],
        is_unreachable: bool = False,
        redirect_hops: int = 0
    ) -> str:
        """
        Determines URL check verdict:
        - unreachable / broken
        - phishing-like
        - malware-linked
        - redirect-heavy
        - suspicious
        - safe
        """
        if is_unreachable:
            return "unreachable / broken"

        keys = [f.get("finding_key", "").lower() for f in findings]

        # Check for phishing indicators
        has_phishing = any("phishing" in k or "impersonation" in k or "credential" in k for k in keys)
        if has_phishing:
            return "phishing-like"

        # Check for malware-linked
        has_malware = any("malware" in k or "shell" in k or "execution" in k for k in keys)
        if has_malware:
            return "malware-linked"

        # Check for redirect-heavy
        if redirect_hops >= 3 or any("redirect.excessive" in k for k in keys):
            return "redirect-heavy"

        # Check for suspicious heuristics
        if score >= 35 or any("heuristics" in k or "homograph" in k for k in keys):
            return "suspicious"

        return "safe"

    def classify_file_verdict(self, score: int, findings: List[Dict[str, Any]]) -> str:
        if score == 0:
            return "clean"
        elif score <= 20:
            return "low"
        elif score <= 45:
            return "medium"
        elif score <= 75:
            return "high"
        return "critical"


risk_engine = RiskEngine()
