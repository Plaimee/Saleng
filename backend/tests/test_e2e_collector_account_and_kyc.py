"""
Integration E2E Test สำหรับระบบบัญชีและการยืนยันตัวตนซาเล้ง (Buyer 01: Account & KYC)
ทดสอบครบวงจรตั้งแต่ลงทะเบียน -> ตั้งค่ารถ -> ยื่นเอกสาร KYC -> บล็อกรับงาน (D-00-01) -> อนุมัติ -> ปลดล็อกรับงาน
รองรับ UC-01, REQ-FN-001, MD-DOM-04, BR-03, D-00-01, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, CC-01..06, AC-B01-01..05, P-01..P-06
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store
from backend.tests.test_AC_B01_03_kyc_submission import get_valid_thai_id

client = TestClient(app)


def test_e2e_collector_account_and_kyc_lifecycle():
    """
    ทดสอบครบวงจรการทำงานของผู้ซื้อ/ซาเล้ง:
    1. ขอรหัส OTP 6 หลัก และยืนยันเพื่อเข้าสู่ระบบ
    2. ตั้งค่าโปรไฟล์และประเภทยานพาหนะ (SIDE_CAR_MOTORCYCLE 320 กก.)
    3. ตรวจสอบ Gate บล็อกรับงานขณะ UNVERIFIED (403 Forbidden)
    4. ยื่นเอกสาร KYC เข้าสู่สถานะ PENDING_REVIEW
    5. ตรวจสอบ Gate บล็อกรับงานขณะ PENDING_REVIEW (403 Forbidden)
    6. จำลองการปฏิเสธ (REJECTED) พร้อมเหตุผล และตรวจสอบ Gate (403 Forbidden)
    7. ส่งเอกสารแก้ไขใหม่ (Resubmit) -> PENDING_REVIEW
    8. จำลองการอนุมัติ (VERIFIED) -> ปลดล็อกสิทธิ์รับงานสำเร็จ (200 OK)
    9. ตรวจสอบ Audit Log ครบทุกขั้นตอนอย่างถูกต้อง
    """
    phone = "0851234567"
    valid_id = get_valid_thai_id()
    initial_log_count = len(supabase_store.audit_logs)

    # -------------------------------------------------------------
    # 1. ขอรหัส OTP และเข้าสู่ระบบ (AC-B01-01)
    # -------------------------------------------------------------
    req_otp_res = client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    assert req_otp_res.status_code == 200
    otp_data = req_otp_res.json()
    assert otp_data["phone_masked"] == "08X-XXX-4567"
    assert otp_data["mock_otp"] == "123456"

    verify_otp_res = client.post(
        "/api/v1/collectors/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"}
    )
    assert verify_otp_res.status_code == 200
    auth_data = verify_otp_res.json()
    saleng_id = auth_data["saleng_id"]
    session_token = auth_data["session_token"]

    assert saleng_id.startswith("saleng-")
    assert auth_data["phone_masked"] == "08X-XXX-4567"
    assert auth_data["verified"] is False
    assert auth_data["kyc_status"] == "UNVERIFIED"

    # -------------------------------------------------------------
    # 2. ตั้งค่าโปรไฟล์และประเภทยานพาหนะ (AC-B01-02, BR-03)
    # -------------------------------------------------------------
    update_prof_res = client.put(
        f"/api/v1/collectors/{saleng_id}/profile",
        json={"display_name": "นายสมชาย ซาเล้งพัฒนาการ"}
    )
    assert update_prof_res.status_code == 200
    assert update_prof_res.json()["display_name"] == "นายสมชาย ซาเล้งพัฒนาการ"

    vehicle_res = client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "SIDE_CAR_MOTORCYCLE",
            "license_plate": "7กข-8888 กทม.",
            "max_capacity_kg": 320.0,
        }
    )
    assert vehicle_res.status_code == 200
    veh_data = vehicle_res.json()
    assert veh_data["vehicle_type"] == "SIDE_CAR_MOTORCYCLE"
    assert veh_data["max_capacity_kg"] == 320.0
    assert veh_data["license_plate"] == "7กข-8888 กทม."

    # -------------------------------------------------------------
    # 3. ตรวจสอบ Gate บล็อกรับงานขณะ UNVERIFIED (AC-B01-04, D-00-01)
    # -------------------------------------------------------------
    gate_unverified = client.get(f"/api/v1/collectors/{saleng_id}/job-claim-gate")
    assert gate_unverified.status_code == 403
    assert "ยังไม่ได้ยื่นเอกสารยืนยันตัวตน (KYC)" in gate_unverified.json()["detail"]

    # -------------------------------------------------------------
    # 4. ยื่นเอกสาร KYC ครั้งที่ 1 (AC-B01-03)
    # -------------------------------------------------------------
    kyc_payload = {
        "id_card_no": valid_id,
        "full_name": "นายสมชาย ใจมั่นคง",
        "id_card_photo_url": "https://storage.saleng.app/kyc/test_id.jpg",
        "selfie_photo_url": "https://storage.saleng.app/kyc/test_selfie.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/test_vehicle.jpg",
    }
    submit_res1 = client.post(f"/api/v1/collectors/{saleng_id}/kyc/submit", json=kyc_payload)
    assert submit_res1.status_code == 201
    assert submit_res1.json()["kyc_status"] == "PENDING_REVIEW"
    assert submit_res1.json()["verified"] is False

    # -------------------------------------------------------------
    # 5. ตรวจสอบ Gate บล็อกรับงานขณะ PENDING_REVIEW (AC-B01-04, D-00-01)
    # -------------------------------------------------------------
    gate_pending = client.get(f"/api/v1/collectors/{saleng_id}/job-claim-gate")
    assert gate_pending.status_code == 403
    assert "อยู่ระหว่างการตรวจสอบ" in gate_pending.json()["detail"]

    # -------------------------------------------------------------
    # 6. จำลองการปฏิเสธ (REJECTED) และตรวจ Gate (AC-B01-03, Q-06)
    # -------------------------------------------------------------
    reject_res = client.post(
        f"/api/v1/collectors/{saleng_id}/mock-kyc-rejection",
        json={"rejection_reason": "ภาพถ่ายบัตรประชาชนไม่ชัดเจน"}
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["kyc_status"] == "REJECTED"

    gate_rejected = client.get(f"/api/v1/collectors/{saleng_id}/job-claim-gate")
    assert gate_rejected.status_code == 403
    assert "ไม่ผ่านการอนุมัติ" in gate_rejected.json()["detail"]

    # -------------------------------------------------------------
    # 7. ยื่นเอกสารใหม่ (Resubmit) -> PENDING_REVIEW
    # -------------------------------------------------------------
    submit_res2 = client.post(f"/api/v1/collectors/{saleng_id}/kyc/submit", json=kyc_payload)
    assert submit_res2.status_code == 201
    assert submit_res2.json()["kyc_status"] == "PENDING_REVIEW"

    # -------------------------------------------------------------
    # 8. จำลองการอนุมัติ (VERIFIED) และปลดล็อกรับงานสำเร็จ
    # -------------------------------------------------------------
    approve_res = client.post(f"/api/v1/collectors/{saleng_id}/mock-kyc-approval")
    assert approve_res.status_code == 200
    assert approve_res.json()["kyc_status"] == "VERIFIED"
    assert approve_res.json()["verified"] is True

    # ตรวจสอบ Gate ครั้งสุดท้าย -> 200 OK
    gate_verified = client.get(f"/api/v1/collectors/{saleng_id}/job-claim-gate")
    assert gate_verified.status_code == 200
    assert gate_verified.json()["can_claim_job"] is True
    assert gate_verified.json()["verified"] is True

    # -------------------------------------------------------------
    # 9. ตรวจสอบ Audit Log ครบทุกขั้นตอน (AC-B01-05, REQ-SEC-001)
    # -------------------------------------------------------------
    recent_logs = supabase_store.audit_logs[initial_log_count:]
    actions = [l["action"] for l in recent_logs]

    assert "COLLECTOR_OTP_REQUESTED" in actions
    assert "COLLECTOR_LOGIN_SUCCESS" in actions
    assert "COLLECTOR_VEHICLE_UPDATED" in actions
    assert "COLLECTOR_KYC_SUBMITTED" in actions
    assert "COLLECTOR_KYC_REJECTED" in actions
    assert "COLLECTOR_KYC_APPROVED" in actions

