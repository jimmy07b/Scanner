import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="admin", nullable=False)  # admin, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    sha256 = Column(String(64), index=True, nullable=False)
    md5 = Column(String(32), nullable=True)
    sha1 = Column(String(40), nullable=True)
    retention_expires_at = Column(DateTime, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    scan_results = relationship("ScanResult", back_populates="upload", cascade="all, delete-orphan")
    retention_jobs = relationship("FileRetentionJob", back_populates="upload", cascade="all, delete-orphan")

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_type = Column(String(20), nullable=False)  # "file" or "url"
    target_name = Column(String(500), nullable=False)  # filename or URL
    risk_score = Column(Integer, default=0)  # 0 to 100
    status = Column(String(30), default="queued")  # queued, running, completed, failed, clean, low, medium, high, critical
    stage = Column(String(50), default="queued")  # queued, fetching, analyzing, extracting, scoring, completed, failed
    progress = Column(Integer, default=0)  # 0 to 100
    verdict = Column(String(50), nullable=True)  # safe, suspicious, phishing-like, redirect-heavy, malware-linked, unreachable
    summary = Column(Text, nullable=False, default="")
    raw_metadata = Column(JSON, default=dict)
    upload_id = Column(String(36), ForeignKey("uploads.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    upload = relationship("Upload", back_populates="scan_results")
    findings = relationship("Finding", back_populates="scan_result", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan_result", cascade="all, delete-orphan")

    @property
    def scan_id(self):
        return self.id

    @property
    def target(self):
        return self.target_name

    @property
    def checks(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("checks", {})
        return {}

    @property
    def passed_checks(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("passed_checks", [])
        return []

    @property
    def collected_data(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("collected_data", {})
        return {}

    @property
    def evidence_collected(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("evidence_collected", True)
        return True

    @property
    def scope_and_method(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("scope_and_method", {})
        return {}

    @property
    def observed_technologies(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("observed_technologies", {})
        return {}

    @property
    def methodology_notes(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("methodology_notes", {})
        return {}

    @property
    def executive_summary(self):
        if isinstance(self.raw_metadata, dict):
            return self.raw_metadata.get("executive_summary", self.summary)
        return self.summary

class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_result_id = Column(String(36), ForeignKey("scan_results.id"), nullable=False)
    finding_key = Column(String(100), nullable=True)  # e.g. "http.headers.csp.missing"
    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)  # info, low, medium, high, critical
    confidence = Column(String(20), default="high")  # high, medium, low
    category = Column(String(100), nullable=False)  # metadata, security_header, macro, etc.
    evidence = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    scan_result = relationship("ScanResult", back_populates="findings")

class WebsiteAuditRequest(Base):
    __tablename__ = "website_audit_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    target_url = Column(String(500), nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    scope_notes = Column(Text, nullable=True)
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    amount_inr = Column(Integer, default=1999)
    status = Column(String(50), default="pending")  # pending, in_review, in_progress, completed
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    payments = relationship("Payment", back_populates="audit_request", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="audit_request", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    audit_request_id = Column(String(36), ForeignKey("website_audit_requests.id"), nullable=False)
    payment_gateway = Column(String(50), default="razorpay_mock")
    transaction_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Float, default=1999.00)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="completed")  # initiated, completed, failed
    receipt_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    audit_request = relationship("WebsiteAuditRequest", back_populates="payments")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_result_id = Column(String(36), ForeignKey("scan_results.id"), nullable=True)
    audit_request_id = Column(String(36), ForeignKey("website_audit_requests.id"), nullable=True)
    report_type = Column(String(50), nullable=False)  # basic_file, basic_url, advanced_audit
    executive_summary = Column(Text, nullable=False)
    technical_findings_json = Column(JSON, default=list)
    remediation_checklist_json = Column(JSON, default=list)
    retest_notes = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    scan_result = relationship("ScanResult", back_populates="reports")
    audit_request = relationship("WebsiteAuditRequest", back_populates="reports")

class AdminNote(Base):
    __tablename__ = "admin_notes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    target_type = Column(String(50), nullable=False)  # scan, audit, upload
    target_id = Column(String(36), nullable=False, index=True)
    author = Column(String(255), default="Security Admin")
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

class FileRetentionJob(Base):
    __tablename__ = "file_retention_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    upload_id = Column(String(36), ForeignKey("uploads.id"), nullable=False)
    scheduled_deletion_at = Column(DateTime, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")  # pending, completed, failed
    details = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    upload = relationship("Upload", back_populates="retention_jobs")
