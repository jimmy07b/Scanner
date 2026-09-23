import os
import tempfile
import zipfile
import pytest
from pathlib import Path
from app.services.file_scanner import file_scanner
from app.services.url_auditor import url_auditor

def test_clean_text_scan():
    f = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8")
    f.write("Hello world, this is a clean benign document for business records.")
    f.close()

    try:
        hashes = {"md5": "abc", "sha1": "def", "sha256": "123"}
        risk_score, status, summary, findings, meta = file_scanner.scan(
            file_path=f.name,
            original_filename="sample.txt",
            hashes=hashes
        )
        assert risk_score == 0
        assert status == "clean"
        assert len(findings) == 0
    finally:
        os.unlink(f.name)

def test_sensitive_credentials_detection():
    f = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8")
    f.write("-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----")
    f.close()

    try:
        hashes = {"md5": "abc", "sha1": "def", "sha256": "123"}
        risk_score, status, summary, findings, meta = file_scanner.scan(
            file_path=f.name,
            original_filename="secret.txt",
            hashes=hashes
        )
        assert risk_score == 25  # 1 critical finding = 25
        assert status == "medium"  # 21-45 = medium
        assert any("Private Cryptographic Key" in f["title"] for f in findings)
        assert meta["checks"]["sensitive_patterns"] is True
    finally:
        os.unlink(f.name)

def test_archive_executable_and_traversal_detection():
    f = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    temp_zip_path = f.name
    f.close()

    try:
        with zipfile.ZipFile(temp_zip_path, "w") as zf:
            zf.writestr("benign.txt", "harmless text")
            zf.writestr("malicious_script.bat", "@echo off\necho test")
            zf.writestr("../traversal.txt", "escaped file")

        hashes = {"md5": "abc", "sha1": "def", "sha256": "123"}
        risk_score, status, summary, findings, meta = file_scanner.scan(
            file_path=temp_zip_path,
            original_filename="archive.zip",
            hashes=hashes
        )
        assert risk_score == 40  # 1 critical (25) + 1 high (15) = 40
        assert status == "medium"  # 21-45 = medium
        assert any("Executable Files" in f["title"] for f in findings)
        assert any("Directory Traversal" in f["title"] for f in findings)
        assert meta["checks"]["archive_traversal"] is True
        assert meta["checks"]["archive_executables"] is True
    finally:
        os.unlink(temp_zip_path)

def test_pdf_javascript_indicator():
    f = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb")
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R /Names << /JavaScript 3 0 R >> >>\nendobj\n%%EOF"
    f.write(pdf_content)
    f.close()

    try:
        hashes = {"md5": "abc", "sha1": "def", "sha256": "123"}
        risk_score, status, summary, findings, meta = file_scanner.scan(
            file_path=f.name,
            original_filename="form.pdf",
            hashes=hashes
        )
        assert any("JavaScript" in f["title"] for f in findings)
        assert risk_score > 0
    finally:
        os.unlink(f.name)

@pytest.mark.asyncio
async def test_url_auditor_normalization_and_headers():
    score, status, summary, findings, meta = await url_auditor.audit("example.com")
    assert meta["domain"] == "example.com"
    assert meta["scheme"] == "https"
    assert isinstance(findings, list)
    assert len(findings) > 0  # Missing security headers like CSP/HSTS are flagged
