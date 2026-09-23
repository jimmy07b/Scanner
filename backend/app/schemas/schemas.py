from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl, Field, ConfigDict

# Base Schemas
class FindingBase(BaseModel):
    finding_key: Optional[str] = None
    title: str
    severity: str  # "info", "low", "medium", "high", "critical"
    confidence: str = "high"  # "high", "medium", "low"
    category: str
    evidence: Optional[str] = None
    recommendation: Optional[str] = None

class FindingCreate(FindingBase):
    pass

class FindingResponse(FindingBase):
    id: str
    scan_result_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Scan Schemas
class UrlScanRequest(BaseModel):
    url: str = Field(..., description="Target website URL to audit")
    authorized: bool = Field(..., description="Confirmation that user owns or is authorized to audit this target")

class ScanJobResponse(BaseModel):
    scan_id: str
    target: str
    scan_type: str  # "url_check", "website", "file"
    status: str  # "queued", "running", "completed", "failed"
    stage: str   # "queued", "fetching", "analyzing", "extracting", "scoring", "completed", "failed"
    progress: int  # 0 to 100
    message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ScanResultResponse(BaseModel):
    id: str
    scan_id: Optional[str] = None
    target: Optional[str] = None  # Friendly target alias (URL or filename)
    scan_type: str  # "url_check", "website", "file"
    target_name: str
    status: str  # "queued", "running", "completed", "failed", "clean", "low", "medium", "high", "critical"
    stage: Optional[str] = "completed"
    progress: Optional[int] = 100
    verdict: Optional[str] = None  # "safe", "suspicious", "phishing-like", "redirect-heavy", "malware-linked", "unreachable", "clean", etc.
    risk_score: int
    summary: str
    raw_metadata: Dict[str, Any] = {}
    created_at: datetime
    findings: List[FindingResponse] = []
    upload_id: Optional[str] = None
    checks: Dict[str, Any] = {}
    passed_checks: List[str] = []
    collected_data: Dict[str, Any] = {}
    evidence_collected: bool = True
    scope_and_method: Dict[str, Any] = {}
    observed_technologies: Dict[str, Any] = {}
    methodology_notes: Dict[str, Any] = {}
    executive_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Website Audit Request (₹1,999 Service)
class WebsiteAuditRequestCreate(BaseModel):
    target_url: str = Field(..., description="Website domain or URL to audit")
    contact_name: str = Field(..., min_length=2)
    contact_email: EmailStr
    organization: Optional[str] = None
    scope_notes: Optional[str] = None
    authorized: bool = Field(..., description="Confirmation of explicit authorization to test target")

class WebsiteAuditRequestUpdate(BaseModel):
    status: Optional[str] = None  # "pending", "in_review", "in_progress", "completed"
    payment_status: Optional[str] = None

class WebsiteAuditRequestResponse(BaseModel):
    id: str
    target_url: str
    contact_name: str
    contact_email: str
    organization: Optional[str]
    scope_notes: Optional[str]
    payment_status: str
    amount_inr: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Payment Simulation / Integration
class PaymentSimulateRequest(BaseModel):
    audit_request_id: str
    payment_method: str = "card"  # "card", "upi", "netbanking"

class PaymentResponse(BaseModel):
    id: str
    audit_request_id: str
    payment_gateway: str
    transaction_id: str
    amount: float
    currency: str
    status: str
    receipt_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Report Schemas
class ReportResponse(BaseModel):
    id: str
    report_type: str
    executive_summary: str
    technical_findings_json: List[Dict[str, Any]]
    remediation_checklist_json: List[Dict[str, Any]]
    retest_notes: Optional[str] = None
    pdf_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Admin Auth & Management
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str

class AdminNoteCreate(BaseModel):
    target_type: str  # "scan", "audit", "upload"
    target_id: str
    note: str

class AdminNoteResponse(BaseModel):
    id: str
    target_type: str
    target_id: str
    author: str
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminMetrics(BaseModel):
    total_scans: int
    total_website_scans: int = 0
    total_file_scans: int
    total_url_scans: int
    threats_flagged: int
    audit_requests_count: int
    pending_audits: int
    total_revenue_inr: int
    active_files_stored: int
