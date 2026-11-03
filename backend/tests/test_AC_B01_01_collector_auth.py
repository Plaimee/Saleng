"""
Automated Tests สำหรับ AC-B01-01: Collector Phone Registration & Session Persistence
รองรับ UC-01, REQ-QA-001, REQ-SEC-001, REQ-SEC-002, REQ-UX-001, CC-01, CC-04, P-01, Q-01
"""

import time
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_B01_01_request_otp_success_and_latency():
    """
    ทดสอบการขอรับรหัส OTP 6 หลัก เข้าสู่ระบบซาเล้ง (AC-B01-01)
    - ต้องตอบกลับภายใน < 2.0 วินาที ตาม REQ-QA-001
    - ต้อง Mask เบอร์โทรศัพท์เป็น 08X-XXX-XXXX ตาม REQ-SEC-002
    - ต้องมีรหัส Mock OTP 123456 ในโหมดทดสอบ
    """
    phone = "0891112233"
    start_time = time.time()
    response = client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    elapsed = time.time() - start_time

    assert response.status_code == 200
    assert elapsed < 2.0  # REQ-QA-001: เวลาตอบสนองต้องไม่เกิน 2.0 วินาที

    data = response.json()
    assert data["phone_masked"] == "08X-XXX-2233"
    assert data["expires_in_seconds"] == 300
    assert data["cooldown_seconds"] == 60
    assert data["mock_otp"] == "123456"

    # ตรวจสอบการบันทึก Audit Log COLLECTOR_OTP_REQUESTED
    logs = [log for log in supabase_store.audit_logs if log["action"] == "COLLECTOR_OTP_REQUESTED"]
    assert len(logs) > 0
    assert logs[-1]["details"]["phone_masked"] == "08X-XXX-2233"


def test_AC_B01_01_request_otp_cooldown_rate_limit():
    """
    ทดสอบการป้องกันการกดขอ OTP ถี่เกินไป (Cooldown 60s) (AC-B01-01)
    """
    phone = "0891112234"
    # ขอครั้งแรกสำเร็จ
    res1 = client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    assert res1.status_code == 200

    # ขอซ้ำทันทีต้องได้รับ 429 Too Many Requests
    res2 = client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    assert res2.status_code == 429
    assert "วินาทีก่อนขอรหัส OTP" in res2.json()["detail"]


def test_AC_B01_01_request_otp_invalid_phone():
    """
    ทดสอบการปฏิเสธเบอร์โทรศัพท์ที่ไม่ถูกต้อง (ไม่ใช่ 10 หลัก หรือไม่ขึ้นต้นด้วย 0)
    """
    res = client.post("/api/v1/collectors/auth/request-otp", json={"phone": "12345"})
    assert res.status_code == 422


def test_AC_B01_01_verify_otp_new_collector_and_session():
    """
    ทดสอบการยืนยันรหัส OTP และสร้างโปรไฟล์ซาเล้งใหม่อัตโนมัติ (AC-B01-01, P-01)
    - ได้รับ session_token
    - สถานะเริ่มต้น verified = False, kyc_status = UNVERIFIED
    - รถเริ่มต้น TRICYCLE ความจุ 150.0 กก.
    """
    phone = "0897778899"
    # 1. ขอ OTP
    res_req = client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    assert res_req.status_code == 200

    # 2. ยืนยัน OTP
    start_time = time.time()
    res_verify = client.post(
        "/api/v1/collectors/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"}
    )
    elapsed = time.time() - start_time

    assert res_verify.status_code == 200
    assert elapsed < 2.0  # REQ-QA-001

    data = res_verify.json()
    assert data["saleng_id"].startswith("saleng-")
    assert data["phone_masked"] == "08X-XXX-8899"
    assert data["session_token"].startswith("saleng_tok_")
    assert data["verified"] is False
    assert data["kyc_status"] == "UNVERIFIED"
    assert data["vehicle_type"] == "TRICYCLE"
    assert data["max_capacity_kg"] == 150.0

    # ตรวจสอบ Audit Log COLLECTOR_LOGIN_SUCCESS
    logs = [log for log in supabase_store.audit_logs if log["action"] == "COLLECTOR_LOGIN_SUCCESS"]
    assert len(logs) > 0
    assert logs[-1]["actor_id"] == data["saleng_id"]


def test_AC_B01_01_verify_otp_invalid_code():
    """
    ทดสอบการยืนยันรหัส OTP ที่ไม่ถูกต้อง
    """
    phone = "0895556677"
    client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})

    res = client.post(
        "/api/v1/collectors/auth/verify-otp",
        json={"phone": phone, "otp_code": "999999"}
    )
    assert res.status_code == 400
    assert "รหัส OTP ไม่ถูกต้อง" in res.json()["detail"]


def test_AC_B01_01_logout():
    """
    ทดสอบการออกจากระบบและยกเลิก Session Token (AC-B01-01)
    """
    phone = "0894443322"
    client.post("/api/v1/collectors/auth/request-otp", json={"phone": phone})
    login_res = client.post(
        "/api/v1/collectors/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"}
    )
    token = login_res.json()["session_token"]

    # ออกจากระบบ
    logout_res = client.post(
        "/api/v1/collectors/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "ออกจากระบบสำเร็จ"

    # เซสชันใน Store ต้องถูกลบแล้ว
    assert supabase_store.get_collector_session(token) is None
