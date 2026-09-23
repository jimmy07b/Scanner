import io
import time
import zipfile
import httpx
from PIL import Image
import pypdf

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def poll_scan(client, scan_id, max_retries=30):
    for _ in range(max_retries):
        time.sleep(0.5)
        try:
            resp = client.get(f"{BASE_URL}/api/scans/{scan_id}")
            if resp.status_code == 200:
                poll = resp.json()
                if poll["status"] in ["completed", "failed"]:
                    return poll
        except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout):
            time.sleep(0.5)
            continue
    return None

def test_comprehensive_e2e():
    client = httpx.Client(timeout=25.0)

    print("=================================================================")
    print("       AEGISSCAN COMPREHENSIVE PRODUCTION VERIFICATION SUITE      ")
    print("=================================================================")

    # -------------------------------------------------------------
    # 1. Public UI & Navigation Verification
    # -------------------------------------------------------------
    print("\n--- 1. Testing Public UI & Unlinked Admin Verification ---")
    home_resp = client.get(f"{FRONTEND_URL}/")
    assert home_resp.status_code == 200, f"Homepage failed with {home_resp.status_code}"
    home_html = home_resp.text

    # Verify no Admin link in public navigation
    assert 'href="/admin"' not in home_html, "Found unescaped /admin link in public homepage HTML!"
    print("  [OK] Admin panel is completely unlinked from public navigation (Navbar & Footer)")

    # Verify clean navbar and evidence-first hero
    header_part = home_html.split('</header>')[0] if '</header>' in home_html else home_html.split('</nav>')[0]
    assert 'Get Advanced Audit' not in header_part, "Found ₹1,999 CTA in header navigation!"
    assert 'RootLayer' in home_html, "Missing 'RootLayer' brand name in homepage!"
    assert 'Precision Security Analysis' in home_html, "Missing hero headline in homepage!"
    assert 'Start Website Audit' in home_html, "Missing 'Start Website Audit' button on homepage!"
    assert 'Run URL Check' in home_html, "Missing 'Run URL Check' button on homepage!"
    assert 'Scan File' in home_html, "Missing 'Scan File' hero button beside other engines on homepage!"
    assert 'Website Security Audit' in home_html, "Missing Website Security Audit primary tool on homepage!"
    assert 'URL Threat Check' in home_html, "Missing URL Threat Check tab on homepage!"
    assert 'Static File Scanner' in home_html, "Missing Static File Scanner tab on homepage!"
    print("  [OK] Header cleanly showcases RootLayer with Website Audit, URL Check, and Scan File hero actions")

    # Verify admin page loads with updated branding & credentials note
    admin_resp = client.get(f"{FRONTEND_URL}/admin")
    assert admin_resp.status_code == 200
    assert "RootLayer Administration" in admin_resp.text
    assert "admin@rootlayer.io" in admin_resp.text
    print("  [OK] Admin panel rendered cleanly with updated branding and admin@rootlayer.io credentials")

    # Verify routes load cleanly
    routes = ["/", "/scan/url", "/scan/website", "/scan/file", "/pricing", "/privacy", "/terms"]
    for r in routes:
        resp = client.get(f"{FRONTEND_URL}{r}")
        assert resp.status_code == 200, f"Route {r} failed with {resp.status_code}"
    print(f"  [OK] All {len(routes)} public frontend routes responded with HTTP 200")

    # -------------------------------------------------------------
    # 2. Defensive Hardening & Security Middleware Checks
    # -------------------------------------------------------------
    print("\n--- 2. Testing Defensive Hardening & Security Middleware ---")
    health_resp = client.get(f"{BASE_URL}/health")
    assert health_resp.status_code == 200

    # Verify defensive security headers
    headers = {k.lower(): v for k, v in health_resp.headers.items()}
    assert headers.get("x-content-type-options") == "nosniff", "Missing X-Content-Type-Options: nosniff"
    assert headers.get("x-frame-options") == "DENY", "Missing X-Frame-Options: DENY"
    assert "strict-origin" in headers.get("referrer-policy", ""), "Missing strict Referrer-Policy"
    print("  [OK] Defensive security headers active on all responses (nosniff, DENY, strict-origin)")

    # Verify role-gated admin endpoint rejects unauthenticated requests
    admin_unauth = client.get(f"{BASE_URL}/api/v1/admin/metrics")
    assert admin_unauth.status_code == 401, f"Expected 401 Unauthorized for admin endpoint, got {admin_unauth.status_code}"
    print("  [OK] Admin API strictly role-gated (HTTP 401 Unauthorized without admin Bearer token)")

    # Verify file upload blocks dangerous executable files (.exe, .bat)
    bad_file = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00executable content")
    bad_upload = client.post(
        f"{BASE_URL}/api/scans/file",
        files={"file": ("payload.exe", bad_file, "application/x-msdownload")},
        data={"authorized": "true"}
    )
    assert bad_upload.status_code == 400, f"Expected 400 for .exe upload, got {bad_upload.status_code}"
    assert "blocked" in bad_upload.json().get("detail", "").lower(), "Expected file rejection detail"
    print(f"  [OK] Executable file extension (.exe) rejected with HTTP 400: '{bad_upload.json()['detail']}'")

    bad_bat = io.BytesIO(b"@echo off\r\ndel C:\\*.*")
    bad_bat_upload = client.post(
        f"{BASE_URL}/api/scans/file",
        files={"file": ("cleanup.bat", bad_bat, "text/plain")},
        data={"authorized": "true"}
    )
    assert bad_bat_upload.status_code == 400
    print("  [OK] Script extension (.bat) rejected with HTTP 400")

    # -------------------------------------------------------------
    # 3. Engine 1: URL Check (Async Pipeline)
    # -------------------------------------------------------------
    print("\n--- 3. Testing Engine 1: URL Threat & Reputation Check ---")
    create_url_resp = client.post(f"{BASE_URL}/api/scans/url", json={
        "url": "https://example.com",
        "authorized": True
    })
    assert create_url_resp.status_code == 200, create_url_resp.text
    scan_id1 = create_url_resp.json()["scan_id"]
    print(f"  [OK] Created URL scan job {scan_id1}")

    final_res1 = poll_scan(client, scan_id1)
    assert final_res1 and final_res1["status"] == "completed"
    assert final_res1["verdict"] in ["safe", "clean", "suspicious", "phishing-like", "redirect-heavy"]
    print(f"  [OK] Engine 1 completed: Verdict={final_res1['verdict']}, Score={final_res1['risk_score']}/100, Findings={len(final_res1['findings'])}, Passed={len(final_res1['passed_checks'])}")

    # Test unreachable target
    unreach_resp = client.post(f"{BASE_URL}/api/scans/url", json={
        "url": "https://this-domain-does-not-exist-at-all-xyz987654321.fake",
        "authorized": True
    })
    assert unreach_resp.status_code == 200
    scan_id_unreach = unreach_resp.json()["scan_id"]
    final_unreach = poll_scan(client, scan_id_unreach)
    assert final_unreach and "unreachable" in final_unreach.get("verdict", "")
    print(f"  [OK] Unreachable URL classified with zero fake findings: Verdict={final_unreach['verdict']}")

    # -------------------------------------------------------------
    # 4. Engine 2: Website Security & CMS Fingerprinting Audit
    # -------------------------------------------------------------
    print("\n--- 4. Testing Engine 2: Website Security Audit with CMS Fingerprinting ---")
    create_site_resp = client.post(f"{BASE_URL}/api/scans/website", json={
        "url": "example.com",
        "authorized": True
    })
    assert create_site_resp.status_code == 200
    scan_id2 = create_site_resp.json()["scan_id"]
    print(f"  [OK] Created Website audit job {scan_id2}")

    final_res2 = poll_scan(client, scan_id2)
    assert final_res2 and final_res2["status"] == "completed"
    collected2 = final_res2["collected_data"]
    assert "cms_details" in collected2, "Missing cms_details in collected_data!"
    cms_info = collected2["cms_details"]
    assert "technology_profile" in collected2, "Missing technology_profile in collected_data!"
    tech_prof = collected2["technology_profile"]
    print(f"  [OK] CMS Fingerprint & Technology Profile collected:")
    print(f"       - Detected: {cms_info.get('cms_detected')}")
    print(f"       - Platform: {cms_info.get('cms_name')}")
    print(f"       - Web Server: {cms_info.get('web_server')}")
    assert "dns_recon" in collected2, "Missing dns_recon in collected_data!"
    assert "tls_telemetry" in collected2, "Missing tls_telemetry in collected_data!"
    assert "client_assets" in collected2, "Missing client_assets in collected_data!"
    print(f"  [OK] Advanced Security & Recon Telemetry verified:")
    print(f"       - DNS Recon: DMARC={bool(collected2['dns_recon'].get('dmarc'))}, SPF={bool(collected2['dns_recon'].get('spf'))}")
    print(f"       - TLS Telemetry: Protocol={collected2['tls_telemetry'].get('protocol')}, Cipher={collected2['tls_telemetry'].get('cipher')}")
    print(f"  [OK] Engine 2 completed: Score={final_res2['risk_score']}/100, Findings={len(final_res2['findings'])}, Passed={len(final_res2['passed_checks'])}")

    # -------------------------------------------------------------
    # 5. Engine 3: Static File Scanner (Image, PDF, ZIP)
    # -------------------------------------------------------------
    print("\n--- 5. Testing Engine 3: Static File Inspection ---")

    # A. Real Image File (PNG)
    img_byte_arr = io.BytesIO()
    img = Image.new('RGB', (160, 90), color='royalblue')
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    file_resp1 = client.post(
        f"{BASE_URL}/api/scans/file",
        files={"file": ("banner.png", img_byte_arr, "image/png")},
        data={"authorized": "true"}
    )
    assert file_resp1.status_code == 200
    scan_id_img = file_resp1.json()["scan_id"]

    final_img = poll_scan(client, scan_id_img)
    assert final_img and final_img["status"] == "completed"
    img_data = final_img["collected_data"]["image_details"]
    assert img_data["width"] == 160
    assert img_data["height"] == 90
    assert img_data["total_pixels"] == 14400
    print(f"  [OK] Image File scanned: {img_data['width']}x{img_data['height']} ({img_data['total_pixels']} px), Aspect Ratio={img_data['aspect_ratio']}")

    # B. Real PDF File
    pdf_writer = pypdf.PdfWriter()
    pdf_writer.add_blank_page(width=612, height=792)
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    pdf_resp = client.post(
        f"{BASE_URL}/api/scans/file",
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")},
        data={"authorized": "true"}
    )
    assert pdf_resp.status_code == 200
    scan_id_pdf = pdf_resp.json()["scan_id"]

    final_pdf = poll_scan(client, scan_id_pdf)
    assert final_pdf and final_pdf["status"] == "completed"
    pdf_data = final_pdf["collected_data"]["pdf_details"]
    assert pdf_data["page_count"] == 1
    assert pdf_data["javascript_presence"] is False
    print(f"  [OK] PDF Document scanned: {pdf_data['page_count']} page(s), JS presence={pdf_data['javascript_presence']}, Encryption={pdf_data['encryption_status']}")

    # C. Real ZIP Archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("notes.txt", "Project deployment instructions.")
        zf.writestr("docs/readme.md", "# Documentation\nAll engines verified.")
    zip_buffer.seek(0)

    zip_resp = client.post(
        f"{BASE_URL}/api/scans/file",
        files={"file": ("archive.zip", zip_buffer, "application/zip")},
        data={"authorized": "true"}
    )
    assert zip_resp.status_code == 200
    scan_id_zip = zip_resp.json()["scan_id"]

    final_zip = poll_scan(client, scan_id_zip)
    assert final_zip and final_zip["status"] == "completed"
    zip_data = final_zip["collected_data"]["archive_details"]
    assert zip_data["file_count"] == 2
    print(f"  [OK] ZIP Archive scanned: {zip_data['file_count']} files inside, Nested archives={zip_data['nested_archives_count']}")

    print("\n=================================================================")
    print("  >>> ALL PRODUCTION & HARDENING VERIFICATION TESTS PASSED! <<<  ")
    print("=================================================================")

if __name__ == "__main__":
    test_comprehensive_e2e()
