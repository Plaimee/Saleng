"""
Integration E2E Lifecycle Test สำหรับระบบบัญชีและการเข้าใช้งานของผู้ขาย (AC-S01-01..05)
รองรับ UC-01, UC-02, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-002, CC-01..06, P-01..P-06
"""

import time
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_e2e_seller_account_and_access_lifecycle():
    """
    ทดสอบครบวงจร:
    1. ผู้ขายกรอกเบอร์มือถือเพื่อขอรับ OTP (AC-S01-01)
    2. ยืนยัน OTP และได้ Session Token + ข้อมูลโปรไฟล์พร้อม Masking (AC-S01-01, AC-S01-03)
    3. บันทึกที่อยู่นัดหมายแห่งที่ 1 และ 2 พร้อมพิกัด GPS (AC-S01-02)
    4. สลับที่อยู่เริ่มต้น และดึง Default Location เตรียมส่งต่อให้ UC-02 (AC-S01-02, P-06)
    5. แก้ไขชื่อผู้ขาย displayName ในหน้าโปรไฟล์ (AC-S01-01)
    6. ตรวจสอบความถูกต้องของ Session Token (AC-S01-04)
    7. ออกจากระบบ (Logout)
    8. ตรวจสอบ Audit Log ครบถ้วนทุก Action (AC-S01-05, REQ-SEC-001)
    """
    phone = "0815554321"

    # Step 1: ขอรับ OTP
    t0 = time.time()
    req_otp_res = client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    assert req_otp_res.status_code == 200
    assert time.time() - t0 < 2.0
    otp_data = req_otp_res.json()
    assert otp_data["phone_masked"] == "08X-XXX-4321"
    otp_code = otp_data.get("mock_otp") or "123456"

    # Step 2: ยืนยัน OTP และสร้างบัญชี
    t1 = time.time()
    auth_res = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": otp_code},
    )
    assert auth_res.status_code == 200
    assert time.time() - t1 < 2.0
    auth = auth_res.json()
    seller_id = auth["seller_id"]
    token = auth["session_token"]
    assert auth["is_new_user"] is True
    assert auth["phone_masked"] == "08X-XXX-4321"

    # Step 3: เพิ่มที่อยู่นัดหมายแห่งที่ 1 (บ้าน)
    loc1_res = client.post(
        f"/api/v1/sellers/{seller_id}/locations",
        json={
            "label": "บ้านหลัก",
            "sub_district": "ลาดพร้าว",
            "address_text": "99/1 ซอยลาดพร้าว 101",
            "geo_point": {"lat": 13.7950, "lng": 100.6200},
            "is_default": False,
        },
    )
    assert loc1_res.status_code == 201
    loc1 = loc1_res.json()
    loc1_id = loc1["location_id"]
    # ที่อยู่อันแรกต้องเป็น default เสมอ
    assert loc1["is_default"] is True

    # เพิ่มที่อยู่นัดหมายแห่งที่ 2 (ร้านค้า)
    loc2_res = client.post(
        f"/api/v1/sellers/{seller_id}/locations",
        json={
            "label": "ร้านค้าพาณิชย์",
            "sub_district": "วังทองหลาง",
            "address_text": "250 ถนนโชคชัย 4",
            "geo_point": {"lat": 13.8010, "lng": 100.6010},
            "is_default": True,
        },
    )
    assert loc2_res.status_code == 201
    loc2 = loc2_res.json()
    loc2_id = loc2["location_id"]
    assert loc2["is_default"] is True

    # Step 4: ตรวจสอบ Default Location สำหรับส่งต่อให้ UC-02
    def_res = client.get(f"/api/v1/sellers/{seller_id}/locations/default")
    assert def_res.status_code == 200
    assert def_res.json()["location_id"] == loc2_id

    # Step 5: แก้ไขชื่อผู้ขาย displayName
    upd_prof_res = client.put(
        f"/api/v1/sellers/{seller_id}/profile",
        json={"display_name": "เจ๊หมวย ลาดพร้าว"},
    )
    assert upd_prof_res.status_code == 200
    assert upd_prof_res.json()["display_name"] == "เจ๊หมวย ลาดพร้าว"
    assert upd_prof_res.json()["phone_masked"] == "08X-XXX-4321"

    # Step 6: ตรวจสอบว่า session_token ใน store ยังคงใช้ได้
    sess = supabase_store.get_seller_session(token)
    assert sess is not None
    assert sess["seller_id"] == seller_id

    # Step 7: Logout
    logout_res = client.post(
        "/api/v1/sellers/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_res.status_code == 200
    assert supabase_store.get_seller_session(token) is None

    # Step 8: ตรวจสอบ Audit Log ทุก Action
    actions = [log["action"] for log in supabase_store.audit_logs if log["actor_id"] in (phone, seller_id)]
    assert "OTP_REQUESTED" in actions
    assert "LOGIN_SUCCESS" in actions
    assert "LOCATION_CREATED" in actions
    assert "PROFILE_UPDATED" in actions
    assert "LOGOUT" in actions

