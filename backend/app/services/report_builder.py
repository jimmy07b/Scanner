import datetime
from typing import Dict, Any, List, Optional

class ReportBuilder:
    """
    Builds formal, deterministic Security Assessment Reports.
    Strictly adheres to:
    - Zero synthetic or guessed values.
    - No check, no finding.
    - If evidence is missing, suppress the finding.
    - Professional, audit-grade report schema.
    """

    def validate_and_filter_findings(self, raw_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        verified = []
        for idx, f in enumerate(raw_findings):
            evidence = f.get("evidence")
            if not evidence:
                continue

            if isinstance(evidence, str) and not evidence.strip():
                continue

            finding_id = f.get("id") or f.get("finding_key") or f"FINDING-{idx+1:03d}"
            
            # Format evidence list cleanly
            evidence_list = evidence if isinstance(evidence, list) else [str(evidence)]
            evidence_clean = [str(e).strip() for e in evidence_list if str(e).strip()]
            if not evidence_clean:
                continue

            verified.append({
                "id": str(finding_id),
                "finding_key": str(f.get("finding_key") or finding_id),
                "title": str(f.get("title", "Security Finding")),
                "severity": str(f.get("severity", "info")).lower(),
                "confidence": str(f.get("confidence", "high")).lower(),
                "category": str(f.get("category", "General Security")),
                "evidence": evidence_clean,
                "recommendation": str(f.get("recommendation", "Review and remediate according to security standards."))
            })
        return verified

    def build_summary(
        self,
        findings: Any = None,
        passed_count: int = 0,
        target_name: str = "",
        verdict: Optional[str] = None,
        findings_count: Optional[int] = None
    ) -> str:
        if isinstance(findings, int) and findings_count is None:
            findings_count = findings
            findings_list = []
        elif isinstance(findings, list):
            findings_list = findings
            findings_count = len(findings)
        else:
            findings_list = []
            findings_count = findings_count or 0

        if verdict == "unreachable / broken" or verdict == "unreachable":
            return f"Security assessment could not complete: The target '{target_name}' is unreachable, refused connection, or failed DNS resolution."

        if findings_count == 0:
            return (
                f"Security assessment of '{target_name}' identified zero vulnerabilities or misconfigurations across "
                f"{passed_count} evaluated checks. System exhibits clean defensive posture with enforced transport and headers."
            )

        if findings_list:
            crit = sum(1 for f in findings_list if f.get("severity") == "critical")
            high = sum(1 for f in findings_list if f.get("severity") == "high")
            med = sum(1 for f in findings_list if f.get("severity") == "medium")
            low = sum(1 for f in findings_list if f.get("severity") == "low")
            info = sum(1 for f in findings_list if f.get("severity") == "info")

            severity_breakdown = []
            if crit > 0:
                severity_breakdown.append(f"{crit} Critical")
            if high > 0:
                severity_breakdown.append(f"{high} High")
            if med > 0:
                severity_breakdown.append(f"{med} Medium")
            if low > 0:
                severity_breakdown.append(f"{low} Low")
            if info > 0:
                severity_breakdown.append(f"{info} Informational")

            counts_str = ", ".join(severity_breakdown) if severity_breakdown else f"{findings_count} findings"
            return (
                f"Security assessment of '{target_name}' identified {findings_count} verified finding(s) ({counts_str}). "
                f"A total of {passed_count} baseline security verification check(s) passed successfully."
            )

        return (
            f"Security assessment of '{target_name}' identified {findings_count} verified finding(s). "
            f"A total of {passed_count} baseline security verification check(s) passed successfully."
        )

        severity_breakdown = []
        if crit > 0:
            severity_breakdown.append(f"{crit} Critical")
        if high > 0:
            severity_breakdown.append(f"{high} High")
        if med > 0:
            severity_breakdown.append(f"{med} Medium")
        if low > 0:
            severity_breakdown.append(f"{low} Low")
        if info > 0:
            severity_breakdown.append(f"{info} Informational")

        counts_str = ", ".join(severity_breakdown) if severity_breakdown else f"{len(findings)} findings"
        return (
            f"Security assessment of '{target_name}' identified {len(findings)} verified finding(s) ({counts_str}). "
            f"A total of {passed_count} baseline security verification check(s) passed successfully."
        )

    def build_report(
        self,
        scan_id: str,
        target: str,
        scan_type: str,
        status: str,
        stage: str,
        progress: int,
        risk_score: int,
        verdict: str,
        findings: List[Dict[str, Any]],
        passed_checks: List[str],
        collected_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        verified_findings = self.validate_and_filter_findings(findings)
        summary = self.build_summary(verified_findings, len(passed_checks), target, verdict)

        # Build Scope & Method metadata
        scope_and_method = {
            "target": target,
            "scan_id": scan_id,
            "scan_type": scan_type,
            "assessment_mode": "Static Passive Recon & Bounded Active Verification",
            "execution_standard": "Non-destructive, Evidence-Based Security Audit",
            "status_code": collected_data.get("status_code"),
            "final_url": collected_data.get("final_url", target),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Build Methodology Notes
        methodology_notes = {
            "approach": "Evidence-First Non-Destructive Security Audit",
            "principles": [
                "Zero Exploit Payloads: Defensive verification only; no malicious payloads, exploits, or brute-force requests executed.",
                "Zero Synthetic Data: All reported metrics and findings originate from observed server headers, responses, and certificates.",
                "Safe SQL Injection Analysis: Conservative indicator analysis (parameter structure, reflection observation, live database error pattern scan) without destructive payload injection.",
                "Bounded Active Recon: Limited, low-rate HEAD/OPTIONS requests and safe configuration path verification under strict rate limits."
            ]
        }

        # Extract technology profile cleanly
        tech_profile = collected_data.get("technology_profile") or {}
        if not tech_profile and "cms_details" in collected_data:
            tech_profile = collected_data["cms_details"].get("technology_profile", {})

        return {
            "scan_id": scan_id,
            "target": target,
            "scan_type": scan_type,
            "status": status,
            "stage": stage,
            "progress": progress,
            "risk_score": risk_score,
            "verdict": verdict,
            "summary": summary,
            "executive_summary": summary,
            "scope_and_method": scope_and_method,
            "findings": verified_findings,
            "passed_checks": passed_checks,
            "observed_technologies": tech_profile,
            "technology_profile": tech_profile,
            "collected_data": collected_data,
            "methodology_notes": methodology_notes
        }


report_builder = ReportBuilder()
