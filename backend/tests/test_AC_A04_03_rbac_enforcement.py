"""
Automated Test for AC-A04-03: Role-Based Access Control (RBAC) Enforcement
รองรับ UC-13, CC-03, D-A04-02
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_rbac_admin_full_access():
    """ADMIN เข้าถึงได้ทุกฟังก์ชัน"""
    # 1. Audit logs
    r1 = client.get("/api/v1/admin/compliance/audit-logs", headers={"X-Admin-Role": "ADMIN"})
    assert r1.status_code == 200

    # 2. Verify integrity
    r2 = client.post("/api/v1/admin/compliance/audit-logs/verify-integrity", headers={"X-Admin-Role": "ADMIN"})
    assert r2.status_code == 200

    # 3. Community report
    r3 = client.get("/api/v1/admin/compliance/reports/community-waste", headers={"X-Admin-Role": "ADMIN"})
    assert r3.status_code == 200

    # 4. Retention status
    r4 = client.get("/api/v1/admin/compliance/retention-status", headers={"X-Admin-Role": "ADMIN"})
    assert r4.status_code == 200


def test_rbac_auditor_permissions():
    """AUDITOR ดู Audit Log, ตรวจ Integrity และรายงานชุมชนได้ แต่ห้ามเข้าถึง PDPA Retention / Purge"""
    # Allowed
    r1 = client.get("/api/v1/admin/compliance/audit-logs", headers={"X-Admin-Role": "AUDITOR"})
    assert r1.status_code == 200

    r2 = client.post("/api/v1/admin/compliance/audit-logs/verify-integrity", headers={"X-Admin-Role": "AUDITOR"})
    assert r2.status_code == 200

    r3 = client.get("/api/v1/admin/compliance/reports/community-waste", headers={"X-Admin-Role": "AUDITOR"})
    assert r3.status_code == 200

    # Forbidden
    r4 = client.get("/api/v1/admin/compliance/retention-status", headers={"X-Admin-Role": "AUDITOR"})
    assert r4.status_code == 403

    r5 = client.post(
        "/api/v1/admin/compliance/purge-expired",
        headers={"X-Admin-Role": "AUDITOR"},
        json={"admin_id": "auditor-01", "confirm_purge": True},
    )
    assert r5.status_code == 403


def test_rbac_dpo_permissions():
    """DPO ดูรายงานชุมชน ตรวจสอบ Retention และสั่ง Purge ได้ แต่ห้ามดู Audit Log ละเอียด"""
    # Allowed
    r1 = client.get("/api/v1/admin/compliance/reports/community-waste", headers={"X-Admin-Role": "DPO"})
    assert r1.status_code == 200

    r2 = client.get("/api/v1/admin/compliance/retention-status", headers={"X-Admin-Role": "DPO"})
    assert r2.status_code == 200

    # Forbidden
    r3 = client.get("/api/v1/admin/compliance/audit-logs", headers={"X-Admin-Role": "DPO"})
    assert r3.status_code == 403

    r4 = client.post("/api/v1/admin/compliance/audit-logs/verify-integrity", headers={"X-Admin-Role": "DPO"})
    assert r4.status_code == 403


def test_rbac_support_blocked():
    """SUPPORT ไม่มีสิทธิ์เข้าถึงฟังก์ชัน Compliance เชิงลึก (HTTP 403 Forbidden)"""
    for endpoint in [
        "/api/v1/admin/compliance/audit-logs",
        "/api/v1/admin/compliance/reports/community-waste",
        "/api/v1/admin/compliance/retention-status",
    ]:
        resp = client.get(endpoint, headers={"X-Admin-Role": "SUPPORT"})
        assert resp.status_code == 403


def test_rbac_missing_header_blocked():
    """ไม่ส่ง X-Admin-Role ต้องถูกปฏิเสธด้วย HTTP 403 Forbidden"""
    resp = client.get("/api/v1/admin/compliance/audit-logs")
    assert resp.status_code == 403

