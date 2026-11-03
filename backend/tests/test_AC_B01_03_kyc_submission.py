"""
Automated Tests สำหรับ AC-B01-03: Thai-ID / DBD-ID KYC Submission & Lifecycle Status
รองรับ SC-04, D-00-01, REQ-SEC-001, CC-01, P-03, P-04, P-06, Q-02, Q-03, Q-06
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store
from backend.app.models.collector_account_models import validate_thai_id

client = TestClient(app)


def get_valid_thai_id():
    """สร้างเลขบัตรประชาชนไทย 13 หลักที่มี Checksum ถูกต้องสำหรับการทดสอบ"""
    digits = [1, 1, 0, 0, 7, 0, 1, 2, 3, 4, 5, 6]
    total = sum(d * (13 - i) for i, d in enumerate(digits))
    valid_cd = (11 - (total % 11)) % 10
    return "110070123456" + str(valid_cd)


def test_AC_B01_03_kyc_lifecycle_full_cycle():
    """
    ทดสอบวงจรชีวิต KYC 4 สถานะ (AC-B01-03, Q-03):
    UNVERIFIED -> PENDING_REVIEW -> REJECTED -> PENDING_REVIEW -> VERIFIED
    """
    valid_id = get_valid_thai_id()

    # 1. สร้างซาเล้งใหม่ผ่านการยืนยัน OTP
    phone = "0861113355"
    client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    login_res = client.post(
        "/api/v1/collectors/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"}
    )
    saleng_id = login_res.json()["saleng_id"]

    # ตรวจสอบสถานะเริ่มต้นต้องเป็น UNVERIFIED
    status_res1 = client.get(f"/api/v1/collectors/{saleng_id}/kyc/status")
    assert status_res1.status_code == 200
    assert status_res1.json()["kyc_status"] == "UNVERIFIED"
    assert status_res1.json()["verified"] is False

    # 2. ส่งเอกสาร KYC ครั้งที่ 1
    submit_payload = {
        "id_card_no": valid_id,
        "full_name": "นายสมชาย ใจดี",
        "id_card_photo_url": "https://storage.saleng.app/kyc/id_card.jpg",
        "selfie_photo_url": "https://storage.saleng.app/kyc/selfie.jpg",
        "vehicle_photo_url": "https://storage.saleng.app/kyc/vehicle.jpg",
    }
    submit_res = client.post(
        f"/api/v1/collectors/{saleng_id}/kyc/submit",
        json=submit_payload
    )
    assert submit_res.status_code == 201
    sub_data = submit_res.json()
    assert sub_data["kyc_status"] == "PENDING_REVIEW"
    assert sub_data["verified"] is False
    assert sub_data["full_name"] == "นายสมชาย ใจดี"
    assert sub_data["id_card_masked"].startswith("1-XXXX-XXXXX-")

    # ตรวจสอบ Audit Log COLLECTOR_KYC_SUBMITTED
    logs_sub = [l for l in supabase_store.audit_logs if l["action"] == "COLLECTOR_KYC_SUBMITTED"]
    assert len(logs_sub) > 0
    assert logs_sub[-1]["actor_id"] == saleng_id

    # 3. จำลองการปฏิเสธ (REJECTED) พร้อมระบุเหตุผล
    reject_res = client.post(
        f"/api/v1/collectors/{saleng_id}/mock-kyc-rejection",
        json={"rejection_reason": "รูปถ่ายบัตรประชาชนสะท้อนแสงจนมองไม่เห็นตัวเลข"}
    )
    assert reject_res.status_code == 200
    rej_data = reject_res.json()
    assert rej_data["kyc_status"] == "REJECTED"
    assert rej_data["verified"] is False
    assert rej_data["rejection_reason"] == "รูปถ่ายบัตรประชาชนสะท้อนแสงจนมองไม่เห็นตัวเลข"

    # ตรวจสอบ Audit Log COLLECTOR_KYC_REJECTED
    logs_rej = [l for l in supabase_store.audit_logs if l["action"] == "COLLECTOR_KYC_REJECTED"]
    assert len(logs_rej) > 0
    assert logs_rej[-1]["entity_id"] == saleng_id

    # 4. ส่งเอกสารใหม่อีกครั้งหลังถูกปฏิเสธ (Resubmit) -> กลับเป็น PENDING_REVIEW
    submit_res2 = client.post(
        f"/api/v1/collectors/{saleng_id}/kyc/submit",
        json=submit_payload
    )
    assert submit_res2.status_code == 201
    assert submit_res2.json()["kyc_status"] == "PENDING_REVIEW"

    # 5. จำลองการอนุมัติ (VERIFIED)
    approve_res = client.post(f"/api/v1/collectors/{saleng_id}/mock-kyc-approval")
    assert approve_res.status_code == 200
    app_data = approve_res.json()
    assert app_data["kyc_status"] == "VERIFIED"
    assert app_data["verified"] is True
    assert app_data["rejection_reason"] is None

    # ตรวจสอบ Audit Log COLLECTOR_KYC_APPROVED
    logs_app = [l for l in supabase_store.audit_logs if l["action"] == "COLLECTOR_KYC_APPROVED"]
    assert len(logs_app) > 0
    assert logs_app[-1]["entity_id"] == saleng_id

    # ตรวจสอบว่าใน Profile ข้อมูล verified และ kyc_status ถูกปรับเป็น VERIFIED
    prof_res = client.get(f"/api/v1/collectors/{saleng_id}/profile")
    assert prof_res.json()["verified"] is True
    assert prof_res.json()["kyc_status"] == "VERIFIED"


def test_AC_B01_03_kyc_submit_invalid_checksum():
    """
    ทดสอบการปฏิเสธเลขบัตรประชาชนที่ไม่ผ่านการคำนวณ Checksum ของกรมการปกครอง
    """
    saleng_id = "saleng-05"
    payload = {
        "id_card_no": "1234567890123",  # เลขมั่วไม่ผ่าน Checksum
        "full_name": "ทดสอบ เลขมั่ว",
        "id_card_photo_url": "https://storage.saleng.app/kyc/id.jpg",
        "selfie_photo_url": "https://storage.saleng.app/kyc/selfie.jpg",
    }
    res = client.post(f"/api/v1/collectors/{saleng_id}/kyc/submit", json=payload)
    assert res.status_code == 422
    assert "Checksum ของกรมการปกครอง" in str(res.json())

