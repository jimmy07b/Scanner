import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

logger = logging.getLogger("aegisscan")

from app.core.database import get_db
from app.core.config import settings
from app.core.storage import storage_manager
from app.core.security import check_rate_limit
from app.models.models import Upload, ScanResult, Finding
from app.schemas.schemas import UrlScanRequest, ScanJobResponse, ScanResultResponse
from app.services.scan_queue import scan_queue

router = APIRouter(tags=["Scan Jobs Pipeline"])

@router.post("/url", response_model=ScanJobResponse, dependencies=[Depends(check_rate_limit)])
async def create_url_check(
    payload: UrlScanRequest,
    db: AsyncSession = Depends(get_db)
):
    """Engine 1: Creates an asynchronous URL risk, phishing, and redirection analysis job."""
    if not payload.authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm you are authorized to inspect this target URL."
        )

    job = await scan_queue.create_job(
        scan_type="url_check",
        target_name=payload.url.strip()
    )
    logger.info(f"Audit log: URL Check job created id={job.id} target={job.target_name}")

    return ScanJobResponse(
        scan_id=job.id,
        target=job.target_name,
        scan_type="url_check",
        status=job.status,
        stage=job.stage or "queued",
        progress=job.progress or 0,
        message="URL check queued for background analysis",
        created_at=job.created_at
    )

@router.post("/website", response_model=ScanJobResponse, dependencies=[Depends(check_rate_limit)])
async def create_website_audit(
    payload: UrlScanRequest,
    db: AsyncSession = Depends(get_db)
):
    """Engine 2: Creates an asynchronous Website Security & Posture Audit job."""
    if not payload.authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm you own or are authorized to audit this target website."
        )

    job = await scan_queue.create_job(
        scan_type="website",
        target_name=payload.url.strip()
    )
    logger.info(f"Audit log: Website Audit job created id={job.id} target={job.target_name}")

    return ScanJobResponse(
        scan_id=job.id,
        target=job.target_name,
        scan_type="website",
        status=job.status,
        stage=job.stage or "queued",
        progress=job.progress or 0,
        message="Website security audit queued for background analysis",
        created_at=job.created_at
    )

@router.post("/file", response_model=ScanJobResponse, dependencies=[Depends(check_rate_limit)])
async def create_file_scan(
    file: UploadFile = File(...),
    authorized: bool = Form(..., description="Confirmation of authorization to scan file"),
    db: AsyncSession = Depends(get_db)
):
    """Engine 3: Creates an asynchronous static file inspection job."""
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
            detail=f"The selected file '{original_name}' is an incomplete in-progress download ({ext}). Please upload a completed file."
        )

    DANGEROUS_EXTS = {".exe", ".bat", ".cmd", ".sh", ".vbs", ".ps1", ".msi", ".com", ".scr"}
    if ext in DANGEROUS_EXTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Direct upload of executable binary or script formats ({ext}) is blocked for safety. Please submit inside a password-free .zip archive for static structural inspection."
        )

    # Save file safely to disk
    saved_filename, file_path, file_size, hashes = await storage_manager.save_upload(file)
    logger.info(f"Audit log: File upload received name={original_name} size={file_size} sha256={hashes['sha256'][:16]}...")

    now = datetime.now(timezone.utc)
    retention_expires = now + timedelta(hours=settings.RETENTION_HOURS)

    # Record Upload in DB
    upload = Upload(
        filename=saved_filename,
        original_name=original_name,
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
    await db.commit()
    await db.refresh(upload)

    # Dispatch to background scan queue
    job = await scan_queue.create_job(
        scan_type="file",
        target_name=upload.original_name,
        upload_id=upload.id,
        file_path=file_path,
        hashes=hashes
    )

    return ScanJobResponse(
        scan_id=job.id,
        target=job.target_name,
        scan_type="file",
        status=job.status,
        stage=job.stage or "queued",
        progress=job.progress or 0,
        message="File scan queued for background analysis",
        created_at=job.created_at
    )

@router.get("/{scan_id}", response_model=ScanResultResponse)
async def get_scan_status_or_result(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Returns the live stage, progress, status, and full verified report when complete."""
    stmt = (
        select(ScanResult)
        .where(ScanResult.id == scan_id)
        .options(selectinload(ScanResult.findings))
    )
    res = await db.execute(stmt)
    scan_result = res.scalars().first()

    if not scan_result:
        raise HTTPException(status_code=404, detail="Scan job not found")

    return scan_result
