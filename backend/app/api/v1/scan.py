from pathlib import Path
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.storage import storage_manager
from app.core.security import check_rate_limit
from app.models.models import Upload, ScanResult, Finding
from app.schemas.schemas import UrlScanRequest, ScanResultResponse
from app.services.file_scanner import file_scanner
from app.services.url_auditor import url_auditor
from app.services.retention_service import retention_service

router = APIRouter(prefix="/scan", tags=["Scanning"])

@router.post("/file", response_model=ScanResultResponse, dependencies=[Depends(check_rate_limit)])
async def scan_file(
    file: UploadFile = File(...),
    authorized: bool = Form(..., description="Confirmation of authorization to scan file"),
    db: AsyncSession = Depends(get_db)
):
    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm you are authorized to scan this file."
        )

    original_name = file.filename or "uploaded_file"
    ext = Path(original_name).suffix.lower()

    if ext in [".crdownload", ".tmp", ".part", ".download"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The selected file '{original_name}' is an incomplete in-progress download ({ext}). Please wait for the download to complete or upload a finished file."
        )

    # 1. Secure file storage & chunked hash calculation
    saved_filename, file_path, file_size, hashes = await storage_manager.save_upload(file)

    now = datetime.now(timezone.utc)
    retention_expires = now + timedelta(hours=settings.RETENTION_HOURS)

    # 2. Record Upload entity
    upload = Upload(
        filename=saved_filename,
        original_name=file.filename or "uploaded_file",
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        file_path=file_path,
        sha256=hashes["sha256"],
        md5=hashes.get("md5"),
        sha1=hashes.get("sha1"),
        retention_expires_at=retention_expires,
        is_deleted=False
    )
    db.add(upload)
    await db.flush()

    # 3. Execute static file scan
    risk_score, status_label, summary, findings_data, raw_metadata = file_scanner.scan(
        file_path=file_path,
        original_filename=upload.original_name,
        hashes=hashes
    )

    # 4. Save ScanResult and Findings
    scan_result = ScanResult(
        scan_type="file",
        target_name=upload.original_name,
        risk_score=risk_score,
        status=status_label,
        summary=summary,
        raw_metadata=raw_metadata,
        upload_id=upload.id
    )
    db.add(scan_result)
    await db.flush()

    for item in findings_data:
        finding = Finding(
            scan_result_id=scan_result.id,
            finding_key=item.get("finding_key"),
            title=item["title"],
            severity=item["severity"],
            confidence=item.get("confidence", "high"),
            category=item["category"],
            evidence=item.get("evidence"),
            recommendation=item.get("recommendation")
        )
        db.add(finding)

    await db.commit()

    # Reload with findings
    stmt = select(ScanResult).where(ScanResult.id == scan_result.id).options(selectinload(ScanResult.findings))
    res = await db.execute(stmt)
    loaded_result = res.scalars().first()
    return loaded_result

@router.post("/url", response_model=ScanResultResponse, dependencies=[Depends(check_rate_limit)])
async def scan_url(
    payload: UrlScanRequest,
    db: AsyncSession = Depends(get_db)
):
    if not payload.authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm you own or are authorized to audit this target website."
        )

    # 1. Execute static URL and HTTP hygiene audit
    risk_score, status_label, summary, findings_data, raw_metadata = await url_auditor.audit(payload.url)

    # 2. Save ScanResult and Findings
    scan_result = ScanResult(
        scan_type="url",
        target_name=payload.url,
        risk_score=risk_score,
        status=status_label,
        summary=summary,
        raw_metadata=raw_metadata,
        upload_id=None
    )
    db.add(scan_result)
    await db.flush()

    for item in findings_data:
        finding = Finding(
            scan_result_id=scan_result.id,
            finding_key=item.get("finding_key"),
            title=item["title"],
            severity=item["severity"],
            confidence=item.get("confidence", "high"),
            category=item["category"],
            evidence=item.get("evidence"),
            recommendation=item.get("recommendation")
        )
        db.add(finding)

    await db.commit()

    # Reload with findings
    stmt = select(ScanResult).where(ScanResult.id == scan_result.id).options(selectinload(ScanResult.findings))
    res = await db.execute(stmt)
    loaded_result = res.scalars().first()
    return loaded_result

@router.get("/{scan_id}", response_model=ScanResultResponse)
async def get_scan_result(scan_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ScanResult).where(ScanResult.id == scan_id).options(selectinload(ScanResult.findings))
    res = await db.execute(stmt)
    scan_result = res.scalars().first()

    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan result not found")

    return scan_result

@router.post("/{scan_id}/shred")
async def shred_scan_file(scan_id: str, db: AsyncSession = Depends(get_db)):
    """
    Immediate file destruction endpoint for user privacy.
    """
    stmt = select(ScanResult).where(ScanResult.id == scan_id)
    res = await db.execute(stmt)
    scan_result = res.scalars().first()

    if not scan_result or not scan_result.upload_id:
        raise HTTPException(status_code=404, detail="Scan result or associated file not found")

    success = await retention_service.shred_upload_immediately(scan_result.upload_id, db)
    return {"message": "File was securely wiped from storage", "shredded": success}
