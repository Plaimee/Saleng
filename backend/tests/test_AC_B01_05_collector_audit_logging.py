"""
Automated Tests สำหรับ AC-B01-05: Security Audit Logging for Collector Accounts
รองรับ REQ-SEC-001, EV-08, CC-04, P-01..P-06, Q-06
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store
from backend.tests.test_AC_B01_03_kyc_submission import get_valid_thai_id

client = TestClient(app)


def test_AC_B01_05_all_collector_security_actions_logged():
    """
    ทดสอบว่าทุกกิจกรรมด้านความปลอดภัยของซาเล้งถูกบันทึกลง Audit Log ตาม REQ-SEC-001:
    1. COLLECTOR_OTP_REQUESTED
    2. COLLECTOR_LOGIN_SUCCESS
    3. COLLECTOR_VEHICLE_UPDATED
    4. COLLECTOR_KYC_SUBMITTED
    5. COLLECTOR_KYC_REJECTED
    6. COLLECTOR_KYC_APPROVED
    """
    initial_log_count = len(supabase_store.audit_logs)
    phone = "0879998877"
    valid_id = get_valid_thai_id()

    # 1. ขอ OTP -> COLLECTOR_OTP_REQUESTED
    client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})

    # 2. ยืนยัน OTP -> COLLECTOR_LOGIN_SUCCESS
    login_res = client.post(
        "/api/v1/collectors/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"}
    )
    saleng_id = login_res.json()["saleng_id"]

    # 3. อัปเดตรถ -> COLLECTOR_VEHICLE_UPDATED
    client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "SIDE_CAR_MOTORCYCLE",
            "license_plate": "5กก-1111",
            "max_capacity_kg": 300.0,
        }
    )

    # 4. ส่งเอกสาร KYC -> COLLECTOR_KYC_SUBMITTED
    client.post(
        f"/api/v1/collectors/{saleng_id}/kyc/submit",
        json={
            "id_card_no": valid_id,
            "full_name": "นายสมศักดิ์ สายตรวจ",
            "id_card_photo_url": "https://storage.saleng.app/kyc/id.jpg",
            "selfie_photo_url": "https://storage.saleng.app/kyc/selfie.jpg",
        }
    )

    # 5. จำลองการปฏิเสธ -> COLLECTOR_KYC_REJECTED
    client.post(
        f"/api/v1/collectors/{saleng_id}/mock-kyc-rejection",
        json={"rejection_reason": "รูปไม่ชัดเจน"}
    )

    # 6. จำลองการอนุมัติ -> COLLECTOR_KYC_APPROVED
    client.post(f"/api/v1/collectors/{saleng_id}/mock-kyc-approval")

    # ตรวจสอบรายการในตาราง audit_logs
    recent_logs = supabase_store.audit_logs[initial_log_count:]
    actions = [log["action"] for log in recent_logs]

    assert "COLLECTOR_OTP_REQUESTED" in actions
    assert "COLLECTOR_LOGIN_SUCCESS" in actions
    assert "COLLECTOR_VEHICLE_UPDATED" in actions
    assert "COLLECTOR_KYC_SUBMITTED" in actions
    assert "COLLECTOR_KYC_REJECTED" in actions
    assert "COLLECTOR_KYC_APPROVED" in actions

    # ตรวจสอบโครงสร้างและความสมบูรณ์ของ Log แต่ละรายการ (Append-only & Traceable)
    for log in recent_logs:
        assert "log_id" in log
        assert "action" in log
        assert "timestamp" in log
        assert "actor_id" in log
        assert "entity_id" in log
        assert isinstance(log["details"], dict)

