from typing import Dict, Any, List, Tuple
from app.services.website_auditor import website_auditor

class UrlAuditor:
    """Backward compatibility wrapper for website auditor."""
    async def audit(self, raw_url: str) -> Tuple[int, str, str, List[dict], dict]:
        risk_score, status_label, verdict, summary, findings, passed_checks, collected_data = await website_auditor.audit_website(raw_url)
        raw_metadata = {
            **collected_data,
            "passed_checks": passed_checks,
            "collected_data": collected_data,
            "verdict": verdict,
            "evidence_collected": True
        }
        return risk_score, status_label, summary, findings, raw_metadata

url_auditor = UrlAuditor()
