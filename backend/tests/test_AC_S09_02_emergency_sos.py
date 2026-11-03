"""
Automated Backend Tests สำหรับ AC-S09-02: Emergency SOS One-Tap Trigger & Dispatch
รองรับ UC-09, REQ-UX-001, REQ-QA-001, AC-S09-02, P-02, REQ-SEC-001, Q-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_emergency_sos_dispatch_success_under_2_seconds():
    """
    AC-S09-02 / REQ-QA-001:
    1. ผู้ขายกดปุ่ม SOS ฉุกเฉินในสถานะ S4
    2. ได้รับรหัส SOS-YYYYMMDD-XXXX
    3. บันทึกพิกัดและข้อมูลซาเล้ง
    4. เวลาประมวลผล response_time_ms < 2000 ms (2 วินาที)
    5. ส่งเบอร์โทรด่วนกลับมา (Direct Dial)
    6. บันทึก Audit Log SELLER_TRIGGER_SOS
    """
    seller_id = "SELLER-SOS-01"
    collector_id = "SALENG-SOMCHAI-01"
    order_id = "ORDER-SOS-TEST-01"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "collector_id": collector_id,
        "status": "S4",  # ซาเล้งมาถึงหน้างาน
    }

    # ตั้งค่าเบอร์ผู้ติดต่อฉุกเฉิน
    supabase_store.upsert_emergency_contact({
        "seller_id": seller_id,
        "contact_name": "นายสมบูรณ์ (พี่ชาย)",
        "relationship": "พี่ชาย",
        "contact_phone": "0891234567",
    })

    payload = {
        "current_lat": 13.7563,
        "current_lng": 100.5018,
        "notes": "รู้สึกไม่ปลอดภัย",
    }

    response = client.post(
        f"/api/v1/orders/{order_id}/safety/sos?seller_id={seller_id}",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()

    assert data["order_id"] == order_id
    assert data["seller_id"] == seller_id
    assert data["saleng_id"] == collector_id
    assert data["sos_id"].startswith("SOS-")
    assert data["geo_point"]["lat"] == 13.7563
    assert data["geo_point"]["lng"] == 100.5018

    # REQ-QA-001: ประมวลผลภายใน 2 วินาที (2000 ms)
    assert data["response_time_ms"] < 2000.0

    # เบอร์สำหรับโทรออกด่วน
    assert data["emergency_phone_to_call"] == "0891234567"
    assert data["emergency_contact_name"] == "นายสมบูรณ์ (พี่ชาย)"

    # ตรวจสอบ Audit Log (REQ-SEC-001, AC-S09-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_TRIGGER_SOS" and l["entity_id"] == data["sos_id"]
    ]
    assert len(logs) >= 1
    assert logs[-1]["details"]["saleng_id"] == collector_id


def test_emergency_sos_fallback_to_hotline():
    """
    AC-S09-02: หากผู้ขายไม่ได้ตั้งเบอร์ญาติ ให้ Fallback เป็นสายด่วน Saleng Hotline 02-123-4567
    """
    seller_id = "SELLER-SOS-NO-CONTACT"
    order_id = "ORDER-SOS-TEST-HOTLINE"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "collector_id": "COLLECTOR-99",
        "status": "S3",  # ซาเล้งกำลังเดินทางมา
    }

    payload = {}
    response = client.post(
        f"/api/v1/orders/{order_id}/safety/sos?seller_id={seller_id}",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()

    assert data["emergency_phone_to_call"] == "02-123-4567"
    assert "Saleng Hotline" in data["emergency_contact_name"]

