from typing import List, Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_admin
)
from app.models.models import (
    User, ScanResult, WebsiteAuditRequest, Payment, Upload, AdminNote, Finding
)
from app.schemas.schemas import (
    AdminLogin, Token, AdminMetrics, AdminNoteCreate, AdminNoteResponse,
    WebsiteAuditRequestResponse, WebsiteAuditRequestUpdate
)
from app.services.retention_service import retention_service

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.post("/login", response_model=Token)
async def admin_login(payload: AdminLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin email or password"
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer", user_email=user.email)

@router.get("/metrics", response_model=AdminMetrics)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    total_scans = (await db.execute(select(func.count(ScanResult.id)))).scalar() or 0
    website_scans = (await db.execute(
        select(func.count(ScanResult.id)).where(ScanResult.scan_type.in_(["website", "website_audit"]))
    )).scalar() or 0
    file_scans = (await db.execute(
        select(func.count(ScanResult.id)).where(ScanResult.scan_type == "file")
    )).scalar() or 0
    url_scans = (await db.execute(
        select(func.count(ScanResult.id)).where(ScanResult.scan_type.in_(["url", "url_check"]))
    )).scalar() or 0
    
    threats = (await db.execute(
        select(func.count(ScanResult.id)).where(ScanResult.status.in_(["high", "critical"]))
    )).scalar() or 0
    
    audit_count = (await db.execute(select(func.count(WebsiteAuditRequest.id)))).scalar() or 0
    pending_audits = (await db.execute(
        select(func.count(WebsiteAuditRequest.id)).where(WebsiteAuditRequest.status != "completed")
    )).scalar() or 0

    revenue = (await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == "completed")
    )).scalar() or 0.0

    active_files = (await db.execute(
        select(func.count(Upload.id)).where(Upload.is_deleted == False)
    )).scalar() or 0

    return AdminMetrics(
        total_scans=total_scans,
        total_website_scans=website_scans,
        total_file_scans=file_scans,
        total_url_scans=url_scans,
        threats_flagged=threats,
        audit_requests_count=audit_count,
        pending_audits=pending_audits,
        total_revenue_inr=int(revenue),
        active_files_stored=active_files
    )

@router.get("/scans")
async def list_scans(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    stmt = select(ScanResult).order_by(desc(ScanResult.created_at)).limit(limit)
    res = await db.execute(stmt)
    scans = res.scalars().all()
    
    output = []
    for s in scans:
        output.append({
            "id": s.id,
            "scan_type": s.scan_type,
            "target_name": s.target_name,
            "risk_score": s.risk_score,
            "status": s.status,
            "summary": s.summary,
            "created_at": s.created_at,
            "has_file": s.upload_id is not None
        })
    return output

@router.get("/audits", response_model=List[WebsiteAuditRequestResponse])
async def list_audits(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    stmt = select(WebsiteAuditRequest).order_by(desc(WebsiteAuditRequest.created_at)).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.patch("/audits/{audit_id}", response_model=WebsiteAuditRequestResponse)
async def update_audit_status(
    audit_id: str,
    payload: WebsiteAuditRequestUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    stmt = select(WebsiteAuditRequest).where(WebsiteAuditRequest.id == audit_id)
    res = await db.execute(stmt)
    audit_req = res.scalars().first()

    if not audit_req:
        raise HTTPException(status_code=404, detail="Audit request not found")

    if payload.status:
        audit_req.status = payload.status
    if payload.payment_status:
        audit_req.payment_status = payload.payment_status

    await db.commit()
    await db.refresh(audit_req)
    return audit_req

@router.post("/notes", response_model=AdminNoteResponse)
async def create_admin_note(
    payload: AdminNoteCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    note = AdminNote(
        target_type=payload.target_type,
        target_id=payload.target_id,
        author=admin.email,
        note=payload.note
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@router.get("/notes/{target_type}/{target_id}", response_model=List[AdminNoteResponse])
async def get_admin_notes(
    target_type: str,
    target_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    stmt = select(AdminNote).where(
        AdminNote.target_type == target_type,
        AdminNote.target_id == target_id
    ).order_by(desc(AdminNote.created_at))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/retention/purge")
async def trigger_retention_purge(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    summary = await retention_service.cleanup_expired_files(db)
    return {"message": "Retention purge completed", "stats": summary}
