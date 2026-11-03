"""
Automated Test สำหรับ AC-S01-05: Security Audit Logging for Account & Address Actions
รองรับ REQ-SEC-001, EV-08, P-05
- ทุกการขอ OTP, ยืนยัน OTP, ออกจากระบบ, เพิ่มที่อยู่, แก้ไขที่อยู่, ลบที่อยู่, เปลี่ยน Default ต้องบันทึกลง audit_logs
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S01_05_audit_logging_lifecycle():
    """ทดสอบการบันทึก Audit Log ทุกเหตุการณ์ในระบบบัญชีและที่อยู่นัดหมาย (AC-S01-05)"""
    initial_log_count = len(supabase_store.audit_logs)
    phone = "0891239876"

    # 1. ขอ OTP -> ต้องมี action OTP_REQUESTED
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    assert any(log["action"] == "OTP_REQUESTED" and log["actor_id"] == phone for log in supabase_store.audit_logs)

    # 2. ยืนยัน OTP -> ต้องมี action LOGIN_SUCCESS
    auth_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"},
    )
    seller_id = auth_resp.json()["seller_id"]
    token = auth_resp.json()["session_token"]
    assert any(log["action"] == "LOGIN_SUCCESS" and log["actor_id"] == seller_id for log in supabase_store.audit_logs)

    # 3. แก้ไขโปรไฟล์ -> ต้องมี action PROFILE_UPDATED
    client.put(f"/api/v1/sellers/{seller_id}/profile", json={"display_name": "ชื่อใหม่ ทดสอบ"})
    assert any(log["action"] == "PROFILE_UPDATED" and log["actor_id"] == seller_id for log in supabase_store.audit_logs)

    # 4. เพิ่มที่อยู่ -> ต้องมี action LOCATION_CREATED
    loc_resp = client.post(
        f"/api/v1/sellers/{seller_id}/locations",
        json={
            "label": "บ้านหลัก",
            "sub_district": "ดอนเมือง",
            "address_text": "111 ถ.สรงประภา",
            "geo_point": {"lat": 13.92, "lng": 100.59},
            "is_default": True,
        },
    )
    loc_id = loc_resp.json()["location_id"]
    assert any(log["action"] == "LOCATION_CREATED" and log["entity_id"] == loc_id for log in supabase_store.audit_logs)

    # 5. แก้ไขที่อยู่ -> ต้องมี action LOCATION_UPDATED
    client.put(
        f"/api/v1/sellers/{seller_id}/locations/{loc_id}",
        json={"label": "บ้านหลัก ปรับปรุงใหม่"},
    )
    assert any(log["action"] == "LOCATION_UPDATED" and log["entity_id"] == loc_id for log in supabase_store.audit_logs)

    # 6. ตั้งค่า Default -> ต้องมี action DEFAULT_LOCATION_CHANGED
    client.patch(f"/api/v1/sellers/{seller_id}/locations/{loc_id}/default")
    assert any(log["action"] == "DEFAULT_LOCATION_CHANGED" and log["entity_id"] == loc_id for log in supabase_store.audit_logs)

    # 7. ลบที่อยู่ -> ต้องมี action LOCATION_DELETED
    client.delete(f"/api/v1/sellers/{seller_id}/locations/{loc_id}")
    assert any(log["action"] == "LOCATION_DELETED" and log["entity_id"] == loc_id for log in supabase_store.audit_logs)

    # 8. Logout -> ต้องมี action LOGOUT
    client.post(
        "/api/v1/sellers/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert any(log["action"] == "LOGOUT" and log["actor_id"] == seller_id for log in supabase_store.audit_logs)

