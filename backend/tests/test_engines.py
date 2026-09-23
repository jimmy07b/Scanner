import pytest
from app.services.url_checker import url_checker
from app.services.website_auditor import website_auditor
from app.services.risk_engine import risk_engine

@pytest.mark.asyncio
async def test_url_checker_ip_and_port():
    score, status, verdict, summary, findings, passed_checks, collected = await url_checker.check_url(
        "http://192.168.1.1:8080/login"
    )
    assert collected["has_ip_host"] is True
    assert any("ip_host" in f["finding_key"] for f in findings)
    assert any("suspicious_port" in f["finding_key"] for f in findings)
    assert verdict in ["suspicious", "phishing-like", "unreachable / broken"]

@pytest.mark.asyncio
async def test_url_checker_brand_impersonation():
    score, status, verdict, summary, findings, passed_checks, collected = await url_checker.check_url(
        "https://paypal-security-update.xyz/verify-account"
    )
    assert collected["brand_detected"] == "paypal"
    assert any("brand_impersonation" in f["finding_key"] for f in findings)
    assert verdict == "phishing-like" or verdict == "unreachable / broken"

@pytest.mark.asyncio
async def test_url_checker_clean_site():
    score, status, verdict, summary, findings, passed_checks, collected = await url_checker.check_url(
        "example.com"
    )
    assert collected["has_ip_host"] is False
    assert collected["has_punycode"] is False
    assert len(passed_checks) > 0
    assert verdict in ["safe", "suspicious"]
    assert "threat_analysis" in collected
    assert collected["threat_analysis"]["is_phishing"] is False
    assert collected["threat_analysis"]["is_malware"] is False

@pytest.mark.asyncio
async def test_url_checker_malware_executable_link():
    score, status, verdict, summary, findings, passed_checks, collected = await url_checker.check_url(
        "http://suspicious-share.test/downloads/invoice_update.exe"
    )
    assert collected["has_malware_extension"] is True
    assert any("executable_file_link" in f["finding_key"] for f in findings)
    assert "threat_analysis" in collected
    assert collected["threat_analysis"]["is_malware"] is True
    assert collected["threat_analysis"]["malware_verdict"] == "MALWARE / VIRUS RISK"

@pytest.mark.asyncio
async def test_website_auditor_clean():
    score, status, verdict, summary, findings, passed_checks, collected = await website_auditor.audit_website(
        "example.com"
    )
    assert collected["status_code"] == 200
    assert len(passed_checks) > 0
    assert "findings" in locals()

@pytest.mark.asyncio
async def test_website_auditor_advanced_recon():
    score, status, verdict, summary, findings, passed_checks, collected = await website_auditor.audit_website(
        "example.com"
    )
    # 1. DNS Recon
    assert "dns_recon" in collected
    dns = collected["dns_recon"]
    assert "dmarc" in dns
    assert "spf" in dns
    assert "caa" in dns
    assert "mx" in dns

    # 2. TLS Telemetry
    assert "tls_telemetry" in collected
    tls = collected["tls_telemetry"]
    assert "protocol" in tls
    assert "cipher" in tls

    # 3. Security.txt & Assets
    assert "security_txt" in collected
    assert "client_assets" in collected
    assert "cross_origin_headers" in collected
    assert len(passed_checks) >= 5
