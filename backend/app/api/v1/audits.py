import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.security import check_rate_limit
from app.models.models import WebsiteAuditRequest, Payment
from app.schemas.schemas import (
    WebsiteAuditRequestCreate,
    WebsiteAuditRequestResponse,
    PaymentSimulateRequest,
    PaymentResponse
)

router = APIRouter(prefix="/audits", tags=["Advanced Website Audits"])

@router.post("/request", response_model=WebsiteAuditRequestResponse, dependencies=[Depends(check_rate_limit)])
async def create_audit_request(
    payload: WebsiteAuditRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    if not payload.authorized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm explicit authorization to audit the designated target domain."
        )

    audit_req = WebsiteAuditRequest(
        target_url=payload.target_url,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        organization=payload.organization,
        scope_notes=payload.scope_notes,
        payment_status="pending",
        amount_inr=settings.ADVANCED_AUDIT_PRICE_INR,
        status="pending"
    )
    db.add(audit_req)
    await db.commit()
    await db.refresh(audit_req)
    return audit_req

@router.get("/{audit_id}", response_model=WebsiteAuditRequestResponse)
async def get_audit_request(audit_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(WebsiteAuditRequest).where(WebsiteAuditRequest.id == audit_id)
    res = await db.execute(stmt)
    audit_req = res.scalars().first()
    if not audit_req:
        raise HTTPException(status_code=404, detail="Audit request not found")
    return audit_req

@router.post("/{audit_id}/payment", response_model=PaymentResponse)
async def process_payment(
    audit_id: str,
    payload: PaymentSimulateRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WebsiteAuditRequest).where(WebsiteAuditRequest.id == audit_id)
    res = await db.execute(stmt)
    audit_req = res.scalars().first()

    if not audit_req:
        raise HTTPException(status_code=404, detail="Audit request not found")

    txn_id = f"pay_{uuid.uuid4().hex[:14]}"
    
    payment = Payment(
        audit_request_id=audit_req.id,
        payment_gateway=f"razorpay_{payload.payment_method}",
        transaction_id=txn_id,
        amount=float(audit_req.amount_inr),
        currency="INR",
        status="completed",
        receipt_url=f"/receipts/{txn_id}"
    )
    db.add(payment)

    # Transition audit request workflow status
    audit_req.payment_status = "paid"
    audit_req.status = "in_review"

    await db.commit()
    await db.refresh(payment)
    return payment
