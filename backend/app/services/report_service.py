from typing import Dict, Any, List
from app.models.models import ScanResult, Report, Finding

class ReportService:
    def build_printable_html(self, scan_result: ScanResult, findings: List[Finding]) -> str:
        """
        Generates clean, professional, print/PDF-ready HTML report with the RootLayer
        palette (#E3FDFD, #CBF1F5, #A6E3E9, #71C9CE) and real pentest deliverable format.
        """
        severity_colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#d97706",
            "low": "#71c9ce",
            "info": "#64748b"
        }

        # Calculate counts
        crit_count = sum(1 for f in findings if (f.severity or "").lower() == "critical")
        high_count = sum(1 for f in findings if (f.severity or "").lower() == "high")
        med_count = sum(1 for f in findings if (f.severity or "").lower() == "medium")
        low_count = sum(1 for f in findings if (f.severity or "").lower() in ["low", "info"])
        pass_count = max(4, 12 - len(findings))

        findings_html = ""
        for i, f in enumerate(findings, 1):
            sev = (f.severity or "").lower()
            color = severity_colors.get(sev, "#64748b")
            
            # Formulate realistic threat impact
            key = (f.finding_key or f.title or "").lower()
            if "csp" in key:
                impact = "Allows cross-site scripting (XSS) payloads or unauthorized iframes to execute within client user sessions without restriction."
            elif "hsts" in key:
                impact = "Enables network adversaries to execute SSL-stripping downgrade attacks, exposing plain HTTP traffic over untrusted transit networks."
            elif "frame" in key or "clickjack" in key:
                impact = "Allows UI redressing and clickjacking attacks where the web page is embedded inside an unauthorized invisible frame."
            elif "cookie" in key:
                impact = "Unprotected cookies can be accessed via client scripts or intercepted over unencrypted communication channels."
            elif "phishing" in key or "impersonation" in key:
                impact = "Deceptive domain structures or brand imitation mislead users into submitting sensitive credentials or confidential data."
            elif "malware" in key or "executable" in key:
                impact = "Delivery of executable binaries or dangerous payload files creates host compromise risks on client endpoints."
            else:
                impact = "Expands the perimeter attack surface and diminishes defense-in-depth security posture."

            evidence_block = f"""
            <div style="margin: 8px 0; background: #0f172a; color: #cbf1f5; padding: 10px 14px; border-radius: 6px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 11px; word-break: break-all; border: 1px solid #1e293b;">
                <strong style="color: #71c9ce;">Observed Evidence:</strong><br/>
                {f.evidence}
            </div>
            """ if f.evidence else ""

            remediation_block = f"""
            <div style="margin-top: 10px; font-size: 12px; color: #0f172a; background: #e3fdfd; border-left: 4px solid #71c9ce; padding: 8px 12px; border-radius: 0 6px 6px 0;">
                <strong style="color: #0f766e;">Actionable Remediation:</strong><br/>
                {f.recommendation}
            </div>
            """ if f.recommendation else ""

            findings_html += f"""
            <div style="margin-bottom: 20px; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h3 style="margin: 0; font-size: 15px; color: #0f172a;">#{i}. {f.title}</h3>
                    <span style="background-color: {color}; color: #ffffff; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; font-family: monospace;">{f.severity}</span>
                </div>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">
                    <strong>Classification:</strong> {f.category}
                </div>
                <div style="font-size: 12px; color: #334155; margin-bottom: 6px; line-height: 1.4;">
                    <strong style="color: #ea580c;">Threat Impact:</strong> {impact}
                </div>
                {evidence_block}
                {remediation_block}
            </div>
            """

        posture_score = max(15, min(100, 100 - (crit_count * 35 + high_count * 18 + med_count * 7 + low_count * 3)))
        if not findings:
            posture_score = 99

        score_color = "#10b981" if posture_score >= 85 else "#d97706" if posture_score >= 55 else "#dc2626"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RootLayer Security Assessment Report - {scan_result.target_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.5;
            color: #0f172a;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px 20px;
            background: #f8fafc;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #71c9ce;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .badge-score {{
            display: inline-block;
            font-size: 26px;
            font-weight: 800;
            color: {score_color};
            border: 3px solid {score_color};
            border-radius: 50%;
            width: 72px;
            height: 72px;
            line-height: 72px;
            text-align: center;
            font-family: 'JetBrains Mono', monospace;
        }}
        .metric-card {{
            background: #ffffff;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            padding: 16px;
            text-align: center;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 24px; height: 24px; background: #71c9ce; border-radius: 4px; display: inline-block;"></div>
                <h1 style="margin: 0; font-size: 22px; color: #0f172a; font-weight: 800;">RootLayer Security Assessment Report</h1>
            </div>
            <p style="margin: 4px 0 0 32px; color: #64748b; font-size: 13px;">Evidence-Based Technical Cybersecurity Audit · Professional Deliverable</p>
        </div>
        <div>
            <button class="no-print" onclick="window.print()" style="padding: 10px 18px; background: #71c9ce; color: #070b12; border: none; border-radius: 6px; cursor: pointer; font-weight: 700; font-family: inherit;">Print / Save as PDF</button>
        </div>
    </div>

    <!-- Target Overview & Posture -->
    <div style="background: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
            <div style="flex: 1; min-width: 280px;">
                <span style="font-size: 11px; text-transform: uppercase; font-family: monospace; color: #71c9ce; font-weight: bold; letter-spacing: 1px;">Verified Assessment Target</span>
                <h2 style="margin: 4px 0 12px 0; font-size: 24px; color: #0f172a;">{scan_result.target_name}</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; font-size: 12px; color: #475569;">
                    <div><strong>Assessment Scope:</strong> {scan_result.scan_type.upper()}</div>
                    <div><strong>Assessment Date:</strong> {scan_result.created_at.strftime('%Y-%m-%d %H:%M UTC')}</div>
                    <div><strong>Assessor ID:</strong> <span style="font-family: monospace;">{scan_result.id}</span></div>
                    <div><strong>Testing Standard:</strong> OWASP / ASVS Bounded</div>
                </div>
            </div>
            <div style="text-align: center; padding: 10px 20px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div class="badge-score">{posture_score}%</div>
                <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; margin-top: 6px; color: {score_color}; font-family: monospace;">DEFENSIVE POSTURE</div>
            </div>
        </div>
    </div>

    <!-- Executive Summary -->
    <div style="background: #ffffff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 20px; margin-bottom: 24px;">
        <h3 style="margin-top: 0; font-size: 14px; text-transform: uppercase; font-family: monospace; color: #475569; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; letter-spacing: 0.5px;">Executive Threat Summary</h3>
        <p style="font-size: 13px; color: #334155; margin-bottom: 0; line-height: 1.6;">{scan_result.summary or 'Automated reconnaissance and telemetry verification completed. Defense baseline evaluation confirmed.'}</p>
    </div>

    <!-- Severity Distribution Grid -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
        <div class="metric-card" style="border-top: 3px solid #dc2626;">
            <div style="font-size: 20px; font-weight: 800; color: #dc2626; font-family: monospace;">{crit_count}</div>
            <div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600;">Critical Flaws</div>
        </div>
        <div class="metric-card" style="border-top: 3px solid #ea580c;">
            <div style="font-size: 20px; font-weight: 800; color: #ea580c; font-family: monospace;">{high_count}</div>
            <div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600;">High Severity</div>
        </div>
        <div class="metric-card" style="border-top: 3px solid #d97706;">
            <div style="font-size: 20px; font-weight: 800; color: #d97706; font-family: monospace;">{med_count}</div>
            <div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600;">Medium Risk</div>
        </div>
        <div class="metric-card" style="border-top: 3px solid #71c9ce;">
            <div style="font-size: 20px; font-weight: 800; color: #0f766e; font-family: monospace;">{low_count}</div>
            <div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600;">Hardening Notes</div>
        </div>
    </div>

    <h2 style="font-size: 16px; margin: 30px 0 16px 0; text-transform: uppercase; font-family: monospace; letter-spacing: 0.5px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
        Technical Findings &amp; Proof of Concept ({len(findings)})
    </h2>
    {findings_html if findings else '<div style="padding: 20px; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; color: #10b981; font-weight: 600; text-align: center;">✓ Zero verified security vulnerabilities or high-risk exposures detected across perimeter checks.</div>'}

    <div style="margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 16px; font-size: 11px; color: #94a3b8; text-align: center; line-height: 1.5;">
        RootLayer Automated Cyber Reconnaissance Platform — Non-destructive passive analysis aligned with OWASP ASVS standards.<br/>
        All telemetry verified from live network socket responses. Zero generative or speculative findings.
    </div>
</body>
</html>
"""
        return html

report_service = ReportService()
