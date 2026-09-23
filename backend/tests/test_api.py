import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_url_scan_unauthorized_error():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/scan/url", json={
            "url": "https://example.com",
            "authorized": False
        })
    assert response.status_code == 400
    assert "authorized" in response.json()["detail"]

@pytest.mark.asyncio
async def test_advanced_audit_request_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create audit request
        req_res = await ac.post("/api/v1/audits/request", json={
            "target_url": "https://myshop.com",
            "contact_name": "Test Client",
            "contact_email": "client@example.com",
            "organization": "Shopify Merchant",
            "scope_notes": "Main checkout and landing page",
            "authorized": True
        })
        assert req_res.status_code == 200
        audit_data = req_res.json()
        audit_id = audit_data["id"]
        assert audit_data["payment_status"] == "pending"
        assert audit_data["amount_inr"] == 1999

        # 2. Process mock payment
        pay_res = await ac.post(f"/api/v1/audits/{audit_id}/payment", json={
            "audit_request_id": audit_id,
            "payment_method": "upi"
        })
        assert pay_res.status_code == 200
        pay_data = pay_res.json()
        assert pay_data["status"] == "completed"
        assert pay_data["amount"] == 1999.0

        # 3. Check updated request status
        check_res = await ac.get(f"/api/v1/audits/{audit_id}")
        assert check_res.status_code == 200
        updated = check_res.json()
        assert updated["payment_status"] == "paid"
        assert updated["status"] == "in_review"

@pytest.mark.asyncio
async def test_admin_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/admin/login", json={
            "email": settings.ADMIN_DEFAULT_EMAIL,
            "password": settings.ADMIN_DEFAULT_PASSWORD
        })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
