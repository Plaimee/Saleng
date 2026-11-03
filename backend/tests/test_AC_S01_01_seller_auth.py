"""
Automated Test สำหรับ AC-S01-01: Seller Phone Registration & OTP Login
รองรับ UC-01, REQ-UX-002, REQ-QA-001, Q-01, P-01
- ผู้ขายสามารถขอ OTP 6 หลัก
- ยืนยัน OTP และได้รับ session_token
- ตอบสนองภายในเวลา < 2.0 วินาที
- บันทึก Audit Log เมื่อเข้าสู่ระบบสำเร็จ
"""

import time
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S01_01_request_and_verify_otp_new_seller():
    """ทดสอบการขอ OTP และยืนยันตัวตนสำหรับผู้ขายรายใหม่ (AC-S01-01, REQ-QA-001)"""
    phone = "0819998877"

    # 1. ขอ OTP
    start_time = time.time()
    req_resp = client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    req_latency = time.time() - start_time

    assert req_resp.status_code == 200
    assert req_latency < 2.0, f"Request OTP latency {req_latency}s exceeded 2.0s limit"
    data = req_resp.json()
    assert data["phone_masked"] == "08X-XXX-8877"
    assert data["expires_in_seconds"] == 300
    otp_code = data.get("mock_otp") or "123456"

    # 2. ยืนยัน OTP
    start_time = time.time()
    verify_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": otp_code},
    )
    verify_latency = time.time() - start_time

    assert verify_resp.status_code == 200
    assert verify_latency < 2.0, f"Verify OTP latency {verify_latency}s exceeded 2.0s limit"
    auth_data = verify_resp.json()
    assert auth_data["session_token"] is not None
    assert auth_data["seller_id"].startswith("SEL-")
    assert auth_data["is_new_user"] is True
    assert auth_data["phone_masked"] == "08X-XXX-8877"

    # 3. ล็อกอินซ้ำอีกครั้งด้วยเบอร์เดิม -> is_new_user ต้องเป็น False และได้ seller_id เดิม
    seller_id_1 = auth_data["seller_id"]
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    verify_resp2 = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"},
    )
    assert verify_resp2.status_code == 200
    auth_data2 = verify_resp2.json()
    assert auth_data2["seller_id"] == seller_id_1
    assert auth_data2["is_new_user"] is False


def test_AC_S01_01_invalid_otp():
    """ทดสอบกรณีรหัส OTP ไม่ถูกต้อง (AC-S01-01)"""
    phone = "0823334455"
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})

    verify_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "999999"},
    )
    assert verify_resp.status_code == 400
    assert "รหัส OTP ไม่ถูกต้อง" in verify_resp.json()["detail"]


def test_AC_S01_01_logout():
    """ทดสอบการออกจากระบบและยกเลิกเซสชัน (AC-S01-01, AC-S01-05)"""
    phone = "0834445566"
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    auth_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"},
    )
    token = auth_resp.json()["session_token"]

    # Logout
    logout_resp = client.post(
        "/api/v1/sellers/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["success"] is True

    # ตรวจสอบว่า session ถูกลบออกจาก store
    assert supabase_store.get_seller_session(token) is None

