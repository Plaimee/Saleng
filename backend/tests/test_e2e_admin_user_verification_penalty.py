"""
Integration E2E Test สำหรับระบบตรวจสอบอนุมัติผู้ใช้งานและจัดการบทลงโทษ (Admin Feature 01)
ทดสอบครบวงจรตั้งแต่:
1. การตรวจสอบสิทธิ์ Admin RBAC (X-Admin-Role: ADMIN) ปฏิเสธ 403 Forbidden เมื่อไม่มีสิทธิ์
2. การเรียกดูคิวคำขอ KYC ซาเล้ง และตรวจสอบ PII Masking (1-1002-XXXXX-XX-X)
3. การอนุมัติ KYC ปลดล็อกสิทธิ์ saleng_profiles.verified = True ตามเกณฑ์ D-00-01
4. การปฏิเสธ KYC พร้อมบังคับระบุเหตุผล (rejection_reason)
5. การสั่งระงับสิทธิ์ชั่วคราว (SUSPENDED_TEMPORARY) และแบนถาวร (BANNED) สำหรับทั้งซาเล้งและผู้ขาย
6. การปลดระงับสิทธิ์ (Reactivate) คืนสถานะ ACTIVE
7. การค้นหาและกรองรายชื่อผู้ใช้
8. การตรวจสอบ Audit Log ครบทุกขั้นตอนอย่างถูกต้อง (REQ-SEC-001)

รองรับ: UC-11, D-00-01, D-A01-01..06, REQ-SEC-001, REQ-SEC-002, REQ-UX-001, REQ-QA-001, CC-01..06, AC-A01-01..05
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)
ADMIN_HEADERS = {"X-Admin-Role": "ADMIN"}


def test_e2e_admin_user_verification_and_penalty_lifecycle():
    # -------------------------------------------------------------------------
    # 0. เตรียมข้อมูลทดสอบใน Memory Store
    # -------------------------------------------------------------------------
    test_saleng_1 = "e2e-saleng-01"
    test_saleng_2 = "e2e-saleng-02"
    test_seller_1 = "e2e-seller-01"

    supabase_store.saleng_profiles[test_saleng_1] = {
        "saleng_id": test_saleng_1,
        "name": "สมชาย ซาเล้งทดสอบ 1",
        "phone": "0811112222",
        "verified": False,
        "kyc_status": "PENDING_REVIEW",
        "account_status": "ACTIVE",
        "penalty_reason": None,
    }
    supabase_store.saleng_profiles[test_saleng_2] = {
        "saleng_id": test_saleng_2,
        "name": "วิชัย ซาเล้งทดสอบ 2",
        "phone": "0822223333",
        "verified": False,
        "kyc_status": "PENDING_REVIEW",
        "account_status": "ACTIVE",
        "penalty_reason": None,
    }
    supabase_store.sellers[test_seller_1] = {
        "seller_id": test_seller_1,
        "name": "สมหญิง ร้านกาแฟทดสอบ",
        "phone": "0899998888",
        "account_status": "ACTIVE",
        "penalty_reason": None,
    }

    # เพิ่มคำขอ KYC 2 รายการ
    sub1_id = "e2e-kyc-sub-01"
    sub2_id = "e2e-kyc-sub-02"

    supabase_store.collector_kyc_submissions[sub1_id] = {
        "id": sub1_id,
        "saleng_id": test_saleng_1,
        "full_name": "สมชาย ซาเล้งทดสอบ 1",
        "id_card_no": "1100201234567",
        "id_card_photo_url": "https://storage.saleng.app/kyc/e2e-1-id.jpg",
        "selfie_with_id_photo_url": "https://storage.saleng.app/kyc/e2e-1-selfie.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/e2e-1-vehicle.jpg",
        "vehicle_plate": "1กข-1111 กทม.",
        "status": "PENDING_REVIEW",
        "rejection_reason": None,
        "submitted_at": "2026-11-04T10:00:00Z",
    }
    supabase_store.collector_kyc_submissions[sub2_id] = {
        "id": sub2_id,
        "saleng_id": test_saleng_2,
        "full_name": "วิชัย ซาเล้งทดสอบ 2",
        "id_card_no": "1100207654321",
        "id_card_photo_url": "https://storage.saleng.app/kyc/e2e-2-id.jpg",
        "selfie_with_id_photo_url": "https://storage.saleng.app/kyc/e2e-2-selfie.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/e2e-2-vehicle.jpg",
        "vehicle_plate": "2กค-2222 กทม.",
        "status": "PENDING_REVIEW",
        "rejection_reason": None,
        "submitted_at": "2026-11-04T10:05:00Z",
    }

    initial_log_count = len(supabase_store.audit_logs)

    # -------------------------------------------------------------------------
    # 1. ทดสอบการปฏิเสธเมื่อไม่มีสิทธิ์ Admin (CC-03, D-A01-05, AC-A01-05)
    # -------------------------------------------------------------------------
    no_auth_res = client.get("/api/v1/admin/kyc/submissions")
    assert no_auth_res.status_code == 403
    assert "เฉพาะผู้ดูแลระบบ" in no_auth_res.json()["detail"]

    invalid_role_res = client.get("/api/v1/admin/kyc/submissions", headers={"X-Admin-Role": "COLLECTOR"})
    assert invalid_role_res.status_code == 403

    # -------------------------------------------------------------------------
    # 2. เรียกดูคิวคำขอ KYC พร้อมตรวจ PII Masking (AC-A01-01, CC-06)
    # -------------------------------------------------------------------------
    queue_res = client.get("/api/v1/admin/kyc/submissions?status=PENDING_REVIEW", headers=ADMIN_HEADERS)
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert isinstance(queue_data, list)
    assert len(queue_data) >= 2

    # ตรวจสอบ Masking เลขบัตรประชาชน
    sub1_found = next((item for item in queue_data if item["id"] == sub1_id), None)
    assert sub1_found is not None
    assert sub1_found["id_card_no_masked"] == "1-1002-XXXXX-XX-7"
    assert "1234567" not in sub1_found["id_card_no_masked"]
    assert "id_card_no" not in sub1_found  # ข้อมูลจริงต้องไม่หลุดออกมา

    # -------------------------------------------------------------------------
    # 3. อนุมัติ KYC ซาเล้งคนที่ 1 -> เปิดสิทธิ์ verified = True (AC-A01-02, D-00-01)
    # -------------------------------------------------------------------------
    approve_res = client.post(
        "/api/v1/admin/kyc/review",
        json={
            "submission_id": sub1_id,
            "action": "APPROVE",
            "admin_notes": "เอกสารถูกต้องครบถ้วน ชัดเจน",
        },
        headers=ADMIN_HEADERS,
    )
    assert approve_res.status_code == 200
    approve_data = approve_res.json()
    assert approve_data["kyc_status"] == "VERIFIED"
    assert approve_data["verified"] is True

    # ตรวจสอบสถานะใน saleng_profiles โดยตรง
    saleng_1_profile = supabase_store.saleng_profiles[test_saleng_1]
    assert saleng_1_profile["verified"] is True
    assert saleng_1_profile["kyc_status"] == "VERIFIED"

    # -------------------------------------------------------------------------
    # 4. ปฏิเสธ KYC ซาเล้งคนที่ 2 พร้อมตรวจการบังคับเหตุผล (AC-A01-02)
    # -------------------------------------------------------------------------
    # ลองส่งโดยไม่ใส่เหตุผล -> 400
    fail_reject_res = client.post(
        "/api/v1/admin/kyc/review",
        json={
            "submission_id": sub2_id,
            "action": "REJECT",
            "rejection_reason": "",
        },
        headers=ADMIN_HEADERS,
    )
    assert fail_reject_res.status_code == 422

    # ปฏิเสธพร้อมเหตุผลถูกต้อง
    reject_res = client.post(
        "/api/v1/admin/kyc/review",
        json={
            "submission_id": sub2_id,
            "action": "REJECT",
            "rejection_reason": "ภาพถ่ายเซลฟี่ไม่ชัดเจน ไม่ตรงกับรูปบนบัตร",
        },
        headers=ADMIN_HEADERS,
    )
    assert reject_res.status_code == 200
    reject_data = reject_res.json()
    assert reject_data["kyc_status"] == "REJECTED"
    assert reject_data["verified"] is False
    assert reject_data["rejection_reason"] == "ภาพถ่ายเซลฟี่ไม่ชัดเจน ไม่ตรงกับรูปบนบัตร"

    # ตรวจสอบ saleng_profiles
    saleng_2_profile = supabase_store.saleng_profiles[test_saleng_2]
    assert saleng_2_profile["verified"] is False
    assert saleng_2_profile["kyc_status"] == "REJECTED"

    # -------------------------------------------------------------------------
    # 5. สั่งระงับสิทธิ์ผู้ใช้ (User Penalty - Suspend & Ban) (AC-A01-03)
    # -------------------------------------------------------------------------
    # 5.1 ระงับชั่วคราวซาเล้ง 1
    penalize_saleng_res = client.post(
        "/api/v1/admin/users/penalty",
        json={
            "user_id": test_saleng_1,
            "role": "COLLECTOR",
            "action": "SUSPEND_TEMPORARY",
            "penalty_reason": "มีการร้องเรียนเรื่องการกดรับงานแล้วไม่ไปรับ (No-show 3 ครั้ง)",
        },
        headers=ADMIN_HEADERS,
    )
    assert penalize_saleng_res.status_code == 200
    saleng_penalty_data = penalize_saleng_res.json()
    assert saleng_penalty_data["account_status"] == "SUSPENDED_TEMPORARY"
    assert supabase_store.saleng_profiles[test_saleng_1]["account_status"] == "SUSPENDED_TEMPORARY"

    # 5.2 แบนถาวรผู้ขาย 1
    penalize_seller_res = client.post(
        "/api/v1/admin/users/penalty",
        json={
            "user_id": test_seller_1,
            "role": "SELLER",
            "action": "BAN",
            "penalty_reason": "ตรวจพบการโพสต์ขยะเคมีอันตรายและพฤติกรรมคุกคาม",
        },
        headers=ADMIN_HEADERS,
    )
    assert penalize_seller_res.status_code == 200
    seller_penalty_data = penalize_seller_res.json()
    assert seller_penalty_data["account_status"] == "BANNED"
    assert supabase_store.sellers[test_seller_1]["account_status"] == "BANNED"

    # -------------------------------------------------------------------------
    # 6. ค้นหาและกรองผู้ใช้งาน (AC-A01-03, CC-06 PII Phone Masking)
    # -------------------------------------------------------------------------
    users_res = client.get("/api/v1/admin/users?role=COLLECTOR&status=SUSPENDED_TEMPORARY", headers=ADMIN_HEADERS)
    assert users_res.status_code == 200
    users_list = users_res.json()
    assert any(u["user_id"] == test_saleng_1 for u in users_list)
    for u in users_list:
        assert u["role"] == "COLLECTOR"
        assert u["account_status"] == "SUSPENDED_TEMPORARY"
        assert u["phone_masked"].startswith("08")
        assert "XXX" in u["phone_masked"]

    # -------------------------------------------------------------------------
    # 7. ปลดระงับสิทธิ์ คืนสถานะ ACTIVE (AC-A01-04)
    # -------------------------------------------------------------------------
    reactivate_saleng_res = client.post(
        "/api/v1/admin/users/reactivate",
        json={"user_id": test_saleng_1, "role": "COLLECTOR"},
        headers=ADMIN_HEADERS,
    )
    assert reactivate_saleng_res.status_code == 200
    assert reactivate_saleng_res.json()["account_status"] == "ACTIVE"
    assert supabase_store.saleng_profiles[test_saleng_1]["account_status"] == "ACTIVE"
    assert supabase_store.saleng_profiles[test_saleng_1]["penalty_reason"] is None

    reactivate_seller_res = client.post(
        "/api/v1/admin/users/reactivate",
        json={"user_id": test_seller_1, "role": "SELLER"},
        headers=ADMIN_HEADERS,
    )
    assert reactivate_seller_res.status_code == 200
    assert reactivate_seller_res.json()["account_status"] == "ACTIVE"
    assert supabase_store.sellers[test_seller_1]["account_status"] == "ACTIVE"
    assert supabase_store.sellers[test_seller_1]["penalty_reason"] is None

    # -------------------------------------------------------------------------
    # 8. ตรวจสอบความถูกต้องของ Audit Log ครบทุกขั้นตอน (REQ-SEC-001, AC-A01-05)
    # -------------------------------------------------------------------------
    final_logs = supabase_store.audit_logs[initial_log_count:]
    actions = [log["action"] for log in final_logs]

    assert "ADMIN_APPROVED_KYC" in actions
    assert "ADMIN_REJECTED_KYC" in actions
    assert "ADMIN_PENALIZED_USER" in actions
    assert "ADMIN_UNSUSPENDED_USER" in actions

    for log in final_logs:
        if log["action"].startswith("ADMIN_"):
            assert log["actor_role"] == "ADMIN"
            assert log["timestamp"] is not None
