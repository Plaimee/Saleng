"""
Automated Test สำหรับ AC-S01-02: Pickup Location Management & GPS Pinning
รองรับ UC-01, UC-02, MD-DOM-04, Q-02, Q-03, P-02, P-06
- ผู้ขายสามารถเพิ่มที่อยู่นัดหมาย พร้อมตำบล/แขวง และพิกัด GPS
- สลับการตั้งค่าที่อยู่เริ่มต้น (Default Location)
- แก้ไข และลบที่อยู่นัดหมาย
- ดึงที่อยู่นัดหมายเริ่มต้นเพื่อเตรียมส่งต่อให้ UC-02
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S01_02_pickup_location_crud_and_default():
    """ทดสอบ CRUD และการจัดการ Default Location (AC-S01-02)"""
    # 1. สมัครผู้ขาย
    phone = "0845556677"
    client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    auth_resp = client.post(
        "/api/v1/sellers/auth/verify-otp",
        json={"phone": phone, "otp_code": "123456"},
    )
    seller_id = auth_resp.json()["seller_id"]

    # 2. เพิ่มที่อยู่แห่งแรก -> ต้องเป็น Default อัตโนมัติแม้ส่ง is_default=False
    loc1_payload = {
        "label": "บ้านพักอาศัย",
        "sub_district": "บางเขน",
        "address_text": "55/12 หมู่บ้านร่มรื่น ซอย 3",
        "geo_point": {"lat": 13.8700, "lng": 100.5900},
        "is_default": False,
    }
    create_resp1 = client.post(f"/api/v1/sellers/{seller_id}/locations", json=loc1_payload)
    assert create_resp1.status_code == 201
    loc1 = create_resp1.json()
    assert loc1["is_default"] is True
    assert loc1["sub_district"] == "บางเขน"
    loc1_id = loc1["location_id"]

    # 3. เพิ่มที่อยู่แห่งที่สอง ตั้งเป็น Default -> ที่อยู่อันแรกต้องหลุดจาก Default
    loc2_payload = {
        "label": "ร้านของชำ",
        "sub_district": "สายไหม",
        "address_text": "88/9 ตลาดสดสายไหม ห้อง 4",
        "geo_point": {"lat": 13.9100, "lng": 100.6400},
        "is_default": True,
    }
    create_resp2 = client.post(f"/api/v1/sellers/{seller_id}/locations", json=loc2_payload)
    assert create_resp2.status_code == 201
    loc2 = create_resp2.json()
    assert loc2["is_default"] is True
    loc2_id = loc2["location_id"]

    # 4. ดึงรายการที่อยู่ทั้งหมด -> ต้องมี 2 รายการ และ loc2 (default) ขึ้นก่อน
    list_resp = client.get(f"/api/v1/sellers/{seller_id}/locations")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total_locations"] == 2
    assert list_data["locations"][0]["location_id"] == loc2_id
    assert list_data["locations"][1]["location_id"] == loc1_id
    assert list_data["locations"][1]["is_default"] is False

    # 5. ทดสอบ API ดึง Default Location (P-06 เตรียมส่งต่อให้ UC-02)
    def_resp = client.get(f"/api/v1/sellers/{seller_id}/locations/default")
    assert def_resp.status_code == 200
    assert def_resp.json()["location_id"] == loc2_id

    # 6. สลับ loc1 กลับมาเป็น Default
    set_def_resp = client.patch(f"/api/v1/sellers/{seller_id}/locations/{loc1_id}/default")
    assert set_def_resp.status_code == 200
    assert set_def_resp.json()["is_default"] is True

    # ตรวจสอบ loc2 ว่ากลายเป็น False หรือไม่
    def_resp2 = client.get(f"/api/v1/sellers/{seller_id}/locations/default")
    assert def_resp2.json()["location_id"] == loc1_id

    # 7. แก้ไขที่อยู่ loc1
    update_resp = client.put(
        f"/api/v1/sellers/{seller_id}/locations/{loc1_id}",
        json={"label": "บ้านคุณแม่", "address_text": "55/12 หมู่บ้านร่มรื่น ซอย 3 (บ้านรั้วสีขาว)"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["label"] == "บ้านคุณแม่"
    assert "บ้านรั้วสีขาว" in update_resp.json()["address_text"]

    # 8. ลบ loc1 -> loc2 ที่เหลืออยู่ต้องกลายเป็น Default อัตโนมัติ
    del_resp = client.delete(f"/api/v1/sellers/{seller_id}/locations/{loc1_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    def_resp3 = client.get(f"/api/v1/sellers/{seller_id}/locations/default")
    assert def_resp3.json()["location_id"] == loc2_id
    assert def_resp3.json()["is_default"] is True

