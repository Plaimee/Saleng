"""
ชุดทดสอบ AC-A01-02: Driver KYC Approval & Rejection (UC-11, D-00-01, REQ-SEC-001)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_kyc_review_data():
    """เตรียมข้อมูลคำขอ KYC และกู้คืนสถานะหลังทดสอบ"""
    orig_submissions = dict(supabase_store.collector_kyc_submissions)
    orig_profiles = {k: dict(v) for k, v in supabase_store.saleng_profiles.items()}
    orig_audit = list(supabase_store.audit_logs)

    # สร้างคำขอ KYC 2 รายการสำหรับทดสอบ Approve และ Reject
    supabase_store.collector_kyc_submissions["sub-to-approve"] = {
        "id": "sub-to-approve",
        "saleng_id": "saleng-05",
        "id_card_no": "1100200112233",
        "full_name": "เอกชัย ขยันเก็บ",
        "id_card_photo_url": "https://storage.saleng.app/kyc/id_cards/saleng-05.jpg",
        "selfie_photo_url": "https://storage.saleng.app/kyc/selfies/saleng-05.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/vehicles/saleng-05.jpg",
        "status": "PENDING_REVIEW",
        "rejection_reason": None,
        "submitted_at": "2026-11-04T09:00:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
    }
    supabase_store.collector_kyc_submissions["sub-to-reject"] = {
        "id": "sub-to-reject",
        "saleng_id": "saleng-05",
        "id_card_no": "1100200112233",
        "full_name": "เอกชัย ขยันเก็บ",
        "id_card_photo_url": "https://storage.saleng.app/kyc/id_cards/saleng-05.jpg",
        "selfie_photo_url": "https://storage.saleng.app/kyc/selfies/saleng-05.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/vehicles/saleng-05.jpg",
        "status": "PENDING_REVIEW",
        "rejection_reason": None,
        "submitted_at": "2026-11-04T09:30:00Z",
        "reviewed_at": None,
        "reviewed_by": None,
    }
    # กำหนดสถานะเริ่มต้นของ saleng-05 เป็น UNVERIFIED
    supabase_store.saleng_profiles["saleng-05"]["verified"] = False
    supabase_store.saleng_profiles["saleng-05"]["kyc_status"] = "PENDING_REVIEW"

    yield

    supabase_store.collector_kyc_submissions = orig_submissions
    supabase_store.saleng_profiles = orig_profiles
    supabase_store.audit_logs = orig_audit


def test_AC_A01_02_approve_kyc_success():
    """
    ทดสอบ AC-A01-02: แอดมินกดอนุมัติ KYC -> status = VERIFIED, saleng.verified = True (ปลดล็อก D-00-01) และมี Audit Log
    """
    response = client.post(
        "/api/v1/admin/kyc/review",
        json={
            "submission_id": "sub-to-approve",
            "action": "APPROVE",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-super"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "APPROVE"
    assert data["kyc_status"] == "VERIFIED"
    assert data["verified"] is True
    assert data["reviewed_by"] == "admin-super"

    # ตรวจสอบว่า saleng_profiles ได้รับการปลดล็อกสิทธิ์ verified = True ตาม D-00-01
    profile = supabase_store.get_saleng_profile("saleng-05")
    assert profile["verified"] is True
    assert profile["kyc_status"] == "VERIFIED"

    # ตรวจสอบ Audit Log ตาม REQ-SEC-001
    audit_entry = next(
        (log for log in supabase_store.audit_logs if log.get("action") == "ADMIN_APPROVED_KYC"),
        None
    )
    assert audit_entry is not None
    assert audit_entry["actor_id"] == "admin-super"
    assert audit_entry["actor_role"] == "ADMIN"
    assert audit_entry["entity_id"] == "saleng-05"


def test_AC_A01_02_reject_kyc_with_reason():
    """
    ทดสอบ AC-A01-02: แอดมินกดปฏิเสธ KYC พร้อมระบุเหตุผล -> status = REJECTED, saleng.verified = False และมี Audit Log
    """
    response = client.post(
        "/api/v1/admin/kyc/review",
        json={
            "submission_id": "sub-to-reject",
            "action": "REJECT",
            "rejection_reason": "ภาพถ่ายคู่กับบัตรประชาชนไม่ชัดเจน ไม่สามารถอ่านข้อมูลได้",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-super"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["action"] == "REJECT"
    assert data["kyc_status"] == "REJECTED"
    assert data["verified"] is False
    assert "ไม่สามารถอ่านข้อมูลได้" in data["rejection_reason"]

    # ตรวจสอบว่า saleng_profiles ไม่ได้รับสิทธิ์ (verified = False)
    profile = supabase_store.get_saleng_profile("saleng-05")
    assert profile["verified"] is False
    assert profile["kyc_status"] == "REJECTED"
    assert "ไม่สามารถอ่านข้อมูลได้" in profile["rejection_reason"]

    # ตรวจสอบ Audit Log
    audit_entry = next(
        (log for log in supabase_store.audit_logs if log.get("action") == "ADMIN_REJECTED_KYC"),
        None
    )
    assert audit_entry is not None
    assert audit_entry["actor_id"] == "admin-super"
    assert audit_entry["details"]["rejection_reason"] == "ภาพถ่ายคู่กับบัตรประชาชนไม่ชัดเจน ไม่สามารถอ่านข้อมูลได้"


def test_AC_A01_02_reject_without_reason_fails():
    """
    ทดสอบ AC-A01-02: ปฏิเสธคำขอ KYC โดยไม่ระบุเหตุผล ต้องถูกปฏิเสธด้วย 422 Unprocessable Entity
    """
    response = client.post(
        "/api/v1/admin/kyc/review",
        json={
            "submission_id": "sub-to-reject",
            "action": "REJECT",
            "rejection_reason": "",
        },
        headers={"X-Admin-Role": "ADMIN", "X-Admin-Id": "admin-super"},
    )
    assert response.status_code == 422

