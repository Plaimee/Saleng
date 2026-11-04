"""
ชุดทดสอบ AC-A01-05: Admin RBAC & Audit Logging Protection (REQ-SEC-001, REQ-SEC-002, CC-03, CC-06)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_rbac_test_data():
    """เตรียมข้อมูลและกู้คืนหลังทดสอบ"""
    orig_audit = list(supabase_store.audit_logs)
    orig_submissions = dict(supabase_store.collector_kyc_submissions)
    orig_profiles = {k: dict(v) for k, v in supabase_store.saleng_profiles.items()}

    supabase_store.saleng_profiles["saleng-rbac-test"] = {
        "saleng_id": "saleng-rbac-test",
        "name": "ทดสอบ RBAC",
        "phone": "0899990000",
        "verified": False,
        "kyc_status": "PENDING_REVIEW",
    }

    supabase_store.collector_kyc_submissions["sub-rbac-test"] = {
        "id": "sub-rbac-test",
        "saleng_id": "saleng-rbac-test",
        "id_card_no": "1100200112233",
        "full_name": "ทดสอบ RBAC",
        "id_card_photo_url": "https://storage.saleng.app/test.jpg",
        "selfie_photo_url": "https://storage.saleng.app/test.jpg",
        "vehicle_photo_url": None,
        "status": "PENDING_REVIEW",
        "rejection_reason": None,
        "submitted_at": "2026-11-04T12:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
    }

    yield

    supabase_store.audit_logs = orig_audit
    supabase_store.collector_kyc_submissions = orig_submissions
    supabase_store.saleng_profiles = orig_profiles


def test_AC_A01_05_all_admin_endpoints_enforce_rbac_403():
    """
    ทดสอบ AC-A01-05 / CC-03: ทุก Endpoint ภายใต้ /api/v1/admin ต้องปฏิเสธคำขอที่ไม่มี Header X-Admin-Role: ADMIN ด้วย 403 Forbidden
    """
    endpoints = [
        ("GET", "/api/v1/admin/kyc/submissions"),
        ("POST", "/api/v1/admin/kyc/review", {"submission_id": "sub-rbac-test", "action": "APPROVE"}),
        ("GET", "/api/v1/admin/users"),
        ("POST", "/api/v1/admin/users/penalty", {"user_id": "saleng-01", "role": "COLLECTOR", "action": "BAN", "penalty_reason": "ทดสอบ"}),
        ("POST", "/api/v1/admin/users/reactivate", {"user_id": "saleng-01", "role": "COLLECTOR"}),
    ]

    for method, path, *body in endpoints:
        json_data = body[0] if body else None
        # 1. ไม่มี Header
        if method == "GET":
            resp1 = client.get(path)
        else:
            resp1 = client.post(path, json=json_data)
        assert resp1.status_code == 403, f"{path} did not return 403 without header"
        assert "เฉพาะผู้ดูแลระบบ" in resp1.json()["detail"]

        # 2. ส่ง Header ผิด เช่น X-Admin-Role: BUYER
        if method == "GET":
            resp2 = client.get(path, headers={"X-Admin-Role": "BUYER"})
        else:
            resp2 = client.post(path, json=json_data, headers={"X-Admin-Role": "BUYER"})
        assert resp2.status_code == 403, f"{path} did not return 403 with wrong role"


def test_AC_A01_05_audit_logs_contain_admin_identity():
    """
    ทดสอบ AC-A01-05 / REQ-SEC-001: บันทึก Audit Log ทุกเหตุการณ์แอดมินต้องมี actor_role = 'ADMIN' และเวลาประทับที่ถูกต้อง
    """
    initial_log_count = len(supabase_store.audit_logs)

    # ดำเนินการอนุมัติ KYC
    resp = client.post(
        "/api/v1/admin/kyc/review",
        json={"submission_id": "sub-rbac-test", "action": "APPROVE"},
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-auditor-99"},
    )
    assert resp.status_code == 200

    assert len(supabase_store.audit_logs) > initial_log_count
    latest_log = supabase_store.audit_logs[-1]

    assert latest_log["action"] == "ADMIN_APPROVED_KYC"
    assert latest_log["actor_id"] == "admin-auditor-99"
    assert latest_log["actor_role"] == "ADMIN"
    assert "timestamp" in latest_log
    assert latest_log["details"]["verified"] is True
