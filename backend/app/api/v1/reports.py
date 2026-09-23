from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import ScanResult, Report
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{report_id}")
async def get_report_json(report_id: str, db: AsyncSession = Depends(get_db)):
    # Check if report_id matches a scan result first
    stmt = select(ScanResult).where(ScanResult.id == report_id).options(selectinload(ScanResult.findings))
    res = await db.execute(stmt)
    scan_result = res.scalars().first()

    if scan_result:
        return {
            "id": scan_result.id,
            "report_type": f"basic_{scan_result.scan_type}",
            "target_name": scan_result.target_name,
            "risk_score": scan_result.risk_score,
            "status": scan_result.status,
            "summary": scan_result.summary,
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity,
                    "category": f.category,
                    "evidence": f.evidence,
                    "recommendation": f.recommendation
                } for f in scan_result.findings
            ],
            "raw_metadata": scan_result.raw_metadata,
            "created_at": scan_result.created_at
        }

    # Otherwise check Report model
    stmt2 = select(Report).where(Report.id == report_id)
    res2 = await db.execute(stmt2)
    report = res2.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "report_type": report.report_type,
        "executive_summary": report.executive_summary,
        "technical_findings": report.technical_findings_json,
        "remediation_checklist": report.remediation_checklist_json,
        "retest_notes": report.retest_notes,
        "created_at": report.created_at
    }

@router.get("/{report_id}/export", response_class=HTMLResponse)
async def export_printable_report(report_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ScanResult).where(ScanResult.id == report_id).options(selectinload(ScanResult.findings))
    res = await db.execute(stmt)
    scan_result = res.scalars().first()

    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan result not found for printable export")

    html = report_service.build_printable_html(scan_result, scan_result.findings)
    return HTMLResponse(content=html)
