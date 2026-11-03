"""
Automated Test สำหรับ AC-S01-03: PII Protection & PDPA Phone Masking
รองรับ REQ-SEC-002, EV-09, DR-02, Q-04, P-03
- เบอร์โทรศัพท์ของผู้ขายต้องถูกแปลงเป็น 08X-XXX-XXXX ในทุกหน้าจอและ Response
- แยกฟิลด์ sub_district ออกจาก address_text และ geo_point
- แก้ไขชื่อโปรไฟล์ displayName
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app


client = TestClient(app)


def test_AC_S01_03_phone_masking_and_profile():
    """ทดสอบ PDPA Masking และการแก้ไขชื่อโปรไฟล์ (AC-S01-03, REQ-SEC-002)"""
    phone = "0867778899"
    # สมัครสมาชิก
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    auth_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"},
    )
    seller_id = auth_resp.json()["seller_id"]

    # 1. ตรวจสอบ Response ในการ Login ว่า Masked หรือไม่
    assert auth_resp.json()["phone_masked"] == "08X-XXX-8899"
    assert "phone" not in auth_resp.json()

    # 2. ตรวจสอบ API ดึงโปรไฟล์
    prof_resp = client.get(f"/api/v1/sellers/{seller_id}/profile")
    assert prof_resp.status_code == 200
    prof = prof_resp.json()
    assert prof["phone_masked"] == "08X-XXX-8899"
    assert "phone" not in prof
    assert prof["status"] == "ACTIVE"

    # 3. แก้ไขชื่อที่แสดง (displayName)
    update_resp = client.put(
        f"/api/v1/sellers/{seller_id}/profile",
        json={"display_name": "คุณสมชาย รักสะอาด"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["display_name"] == "คุณสมชาย รักสะอาด"
    assert update_resp.json()["phone_masked"] == "08X-XXX-8899"


def test_AC_S01_03_pickup_location_schema_separation():
    """ทดสอบการแยก sub_district ออกจาก address_text และ geo_point (DR-02, Q-04)"""
    phone = "0871112233"
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    auth_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"},
    )
    seller_id = auth_resp.json()["seller_id"]

    loc_payload = {
        "label": "บ้านสวน",
        "sub_district": "ทวีวัฒนา",
        "address_text": "12/3 ถนนเลียบคลองทวีวัฒนา ซอย 5",
        "geo_point": {"lat": 13.7800, "lng": 100.3500},
        "is_default": True,
    }
    create_resp = client.post(f"/api/v1/sellers/{seller_id}/locations", json=loc_payload)
    assert create_resp.status_code == 201
    loc = create_resp.json()

    # ตรวจสอบว่ามีฟิลด์แยกกันอย่างชัดเจน
    assert "sub_district" in loc and loc["sub_district"] == "ทวีวัฒนา"
    assert "address_text" in loc and "12/3" in loc["address_text"]
    assert "geo_point" in loc and loc["geo_point"]["lat"] == 13.7800

