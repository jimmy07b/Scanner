from typing import Dict, Any, List
from app.models.models import ScanResult, Report, Finding

class ReportService:
    def build_printable_html(self, scan_result: ScanResult, findings: List[Finding]) -> str:
        """
        Generates clean, professional, print/PDF-ready HTML report with styling.
        """
        severity_colors = {
            "critical": "#ef4444",
            "high": "#f97316",
            "medium": "#eab308",
            "low": "#3b82f6",
            "info": "#64748b"
        }

        findings_html = ""
        for i, f in enumerate(findings, 1):
            color = severity_colors.get(f.severity.lower(), "#64748b")
            findings_html += f"""
            <div style="margin-bottom: 20px; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; background: #ffffff;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h3 style="margin: 0; font-size: 16px; color: #0f172a;">#{i}. {f.title}</h3>
                    <span style="background-color: {color}; color: #ffffff; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; text-transform: uppercase;">{f.severity}</span>
                </div>
                <p style="margin: 4px 0; font-size: 13px; color: #64748b;"><strong>Category:</strong> {f.category}</p>
                {f'<p style="margin: 6px 0; font-size: 13px; background: #f8fafc; padding: 8px; border-radius: 4px; font-family: monospace; word-break: break-all;"><strong>Evidence:</strong> {f.evidence}</p>' if f.evidence else ''}
                {f'<div style="margin-top: 8px; font-size: 13px; color: #1e293b; background: #f0fdf4; border-left: 4px solid #22c55e; padding: 8px 12px;"><strong>Remediation:</strong> {f.recommendation}</div>' if f.recommendation else ''}
            </div>
            """

        risk_color = "#22c55e" if scan_result.risk_score < 25 else "#eab308" if scan_result.risk_score < 60 else "#ef4444"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RootLayer Security Report - {scan_result.target_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
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
            border-bottom: 2px solid #0f172a;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .badge-score {{
            display: inline-block;
            font-size: 28px;
            font-weight: 800;
            color: {risk_color};
            border: 3px solid {risk_color};
            border-radius: 50%;
            width: 70px;
            height: 70px;
            line-height: 70px;
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
            <h1 style="margin: 0; font-size: 24px; color: #0284c7;">RootLayer Security Assessment Report</h1>
            <p style="margin: 4px 0; color: #64748b; font-size: 14px;">Evidence-Based Technical Audit</p>
        </div>
        <div>
            <button class="no-print" onclick="window.print()" style="padding: 8px 16px; background: #0284c7; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">Print / Save as PDF</button>
        </div>
    </div>

    <div style="background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 24px; margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0 0 8px 0; font-size: 20px;">Target: {scan_result.target_name}</h2>
                <p style="margin: 2px 0; font-size: 14px; color: #64748b;"><strong>Scan Type:</strong> {scan_result.scan_type.upper()}</p>
                <p style="margin: 2px 0; font-size: 14px; color: #64748b;"><strong>Generated At:</strong> {scan_result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p style="margin: 2px 0; font-size: 14px; color: #64748b;"><strong>Assessment ID:</strong> {scan_result.id}</p>
            </div>
            <div style="text-align: center;">
                <div class="badge-score">{scan_result.risk_score}</div>
                <div style="font-size: 12px; font-weight: bold; text-transform: uppercase; margin-top: 4px; color: {risk_color};">{scan_result.status} RISK</div>
            </div>
        </div>
    </div>

    <div style="background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 24px; margin-bottom: 24px;">
        <h3 style="margin-top: 0; font-size: 16px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">Executive Summary</h3>
        <p style="font-size: 14px; color: #334155; margin-bottom: 0;">{scan_result.summary}</p>
    </div>

    <h2 style="font-size: 18px; margin-bottom: 16px;">Security Findings ({len(findings)})</h2>
    {findings_html if findings else '<p style="color: #64748b; font-style: italic;">No security issues or suspicious indicators detected.</p>'}

    <div style="margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 16px; font-size: 12px; color: #94a3b8; text-align: center;">
        RootLayer Platform — Safe Static Inspection Engine. All uploaded files are automatically shredded after the configured retention window.
    </div>
</body>
</html>
"""
        return html

report_service = ReportService()
