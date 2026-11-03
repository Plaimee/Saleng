"""
Automated Tests สำหรับ AC-B01-02: Vehicle Profile & Capacity Setup
รองรับ REQ-FN-001, MD-DOM-04, BR-03, REQ-SEC-001, CC-01, P-02, Q-04
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_B01_02_get_and_update_profile():
    """
    ทดสอบการดึงข้อมูลและอัปเดตชื่อโปรไฟล์ซาเล้ง (P-01, AC-B01-02)
    """
    # ใช้ saleng-01 ที่ seed ไว้ในระบบ
    res = client.get("/api/v1/collectors/saleng-01/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["saleng_id"] == "saleng-01"
    assert data["phone_masked"] == "08X-XXX-5678"
    assert data["verified"] is True
    assert data["vehicle_type"] == "TRICYCLE"

    # อัปเดตชื่อโปรไฟล์
    update_res = client.put(
        "/api/v1/collectors/saleng-01/profile",
        json={"display_name": "ลุงสมชาย ซาเล้งโฉมใหม่"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["display_name"] == "ลุงสมชาย ซาเล้งโฉมใหม่"

    # ตรวจสอบว่าดึงอีกครั้งต้องเป็นชื่อใหม่
    get_res = client.get("/api/v1/collectors/saleng-01/profile")
    assert get_res.json()["display_name"] == "ลุงสมชาย ซาเล้งโฉมใหม่"

    # คืนค่าเดิมเพื่อไม่ให้กระทบ test อื่น
    supabase_store.update_saleng_profile("saleng-01", {"display_name": "ลุงสมชาย ซาเล้งสุทธิสาร"})


def test_AC_B01_02_get_profile_not_found():
    """
    ทดสอบการเรียกดูโปรไฟล์ที่ไม่พบในระบบ (404 Not Found)
    """
    res = client.get("/api/v1/collectors/non-existent-id/profile")
    assert res.status_code == 404
    assert "ไม่พบข้อมูลซาเล้ง" in res.json()["detail"]


def test_AC_B01_02_update_vehicle_standard_profiles():
    """
    ทดสอบการตั้งค่ายานพาหนะ 3 รูปแบบมาตรฐาน (AC-B01-02, Q-04, BR-03)
    1. TRICYCLE (150 กก.)
    2. SIDE_CAR_MOTORCYCLE (300 กก.)
    3. PICKUP_TRUCK (1,000 กก.)
    """
    saleng_id = "saleng-01"

    # 1. ปรับเป็น มอเตอร์ไซค์พ่วงข้าง (SIDE_CAR_MOTORCYCLE 300 กก.)
    res1 = client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "SIDE_CAR_MOTORCYCLE",
            "license_plate": "1กข-5555 กทม.",
            "max_capacity_kg": 300.0,
        }
    )
    assert res1.status_code == 200
    d1 = res1.json()
    assert d1["vehicle_type"] == "SIDE_CAR_MOTORCYCLE"
    assert d1["license_plate"] == "1กข-5555 กทม."
    assert d1["max_capacity_kg"] == 300.0

    # 2. ปรับเป็น รถกระบะ (PICKUP_TRUCK 1,000 กก.)
    res2 = client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "PICKUP_TRUCK",
            "license_plate": "ผข-9999 นนทบุรี",
            "max_capacity_kg": 1000.0,
        }
    )
    assert res2.status_code == 200
    d2 = res2.json()
    assert d2["vehicle_type"] == "PICKUP_TRUCK"
    assert d2["max_capacity_kg"] == 1000.0

    # ตรวจสอบ Audit Log COLLECTOR_VEHICLE_UPDATED
    logs = [log for log in supabase_store.audit_logs if log["action"] == "COLLECTOR_VEHICLE_UPDATED"]
    assert len(logs) >= 2
    assert logs[-1]["details"]["vehicle_type"] == "PICKUP_TRUCK"

    # คืนค่าเดิมเพื่อไม่ให้กระทบ test อื่น
    supabase_store.update_saleng_profile("saleng-01", {
        "vehicle_type": "TRICYCLE",
        "license_plate": "1กข-9999",
        "max_capacity_kg": 200.0,
    })


def test_AC_B01_02_update_vehicle_custom_capacity_and_validation():
    """
    ทดสอบการปรับแต่งความจุจริง และการปฏิเสธค่าน้ำหนักที่เป็น 0 หรือติดลบ (REQ-FN-001, MD-DOM-04)
    """
    saleng_id = "saleng-02"

    # ปรับแต่งความจุจริง (Custom Capacity > 0)
    res_custom = client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "PICKUP_TRUCK",
            "license_plate": "2ฒณ-8888",
            "max_capacity_kg": 1250.5,
        }
    )
    assert res_custom.status_code == 200
    assert res_custom.json()["max_capacity_kg"] == 1250.5

    # ค่าน้ำหนัก 0 หรือติดลบ ต้องถูกปฏิเสธ (422 Pydantic Validation Error)
    res_zero = client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "TRICYCLE",
            "max_capacity_kg": 0.0,
        }
    )
    assert res_zero.status_code == 422

    res_neg = client.put(
        f"/api/v1/collectors/{saleng_id}/vehicle",
        json={
            "vehicle_type": "TRICYCLE",
            "max_capacity_kg": -50.0,
        }
    )
    assert res_neg.status_code == 422
