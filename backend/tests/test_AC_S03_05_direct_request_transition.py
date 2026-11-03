"""
Backend API Tests สำหรับ AC-S03-05: Direct Appointment Request & Audit Logging
รองรับ UC-03, REQ-SEC-001, MD-STM-04, AC-S03-05, P-05, Q-01
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S03_05_direct_appointment_request_success():
    """
    ทดสอบการส่งคำขอนัดหมายเจาะจงบุคคล:
    - สถานะคำขอเปลี่ยนเป็น S2 (Matched / Pending)
    - กำหนด assigned_saleng_id และเวลารอตอบรับ 15 นาที
    - บันทึก Audit Log 'COLLECTOR_DIRECT_REQUESTED'
    """
    order_id = "order-direct-test-01"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S1",
    }

    payload = {
        "saleng_id": "saleng-01",
        "notes": "สะดวกช่วงบ่ายสองครับ",
    }
    response = client.post(
        f"/api/v1/buyer-search/orders/{order_id}/direct-request?seller_id=seller-01",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "S2"
    assert data["assigned_saleng"]["saleng_id"] == "saleng-01"
    assert "direct_request_expires_at" in data

    # ตรวจสอบคำขอใน store
    updated_order = supabase_store.get_order(order_id)
    assert updated_order is not None
    assert updated_order["status"] == "S2"
    assert updated_order["assigned_saleng_id"] == "saleng-01"

    # ตรวจสอบ Audit Log
    logs = [
        l for l in supabase_store.audit_logs
        if l.get("action") == "COLLECTOR_DIRECT_REQUESTED" and l.get("entity_id") == order_id
    ]
    assert len(logs) >= 1
    assert logs[-1]["actor_id"] == "seller-01"


def test_AC_S03_05_direct_request_blocked_for_unverified_or_offline():
    """ทดสอบการบล็อกไม่ให้ส่งคำขอไปยังซาเล้งที่ยังไม่ยืนยันตัวตน หรือปิดรับงาน"""
    order_id = "order-blocked-test"

    # 1. ซาเล้งยังไม่ผ่าน KYC (saleng-05)
    res_unverified = client.post(
        f"/api/v1/buyer-search/orders/{order_id}/direct-request?seller_id=seller-01",
        json={"saleng_id": "saleng-05"},
    )
    assert res_unverified.status_code == 400
    assert "ยืนยันตัวตน" in res_unverified.json()["detail"]

    # 2. ซาเล้งปิดรับงาน (saleng-04)
    res_offline = client.post(
        f"/api/v1/buyer-search/orders/{order_id}/direct-request?seller_id=seller-01",
        json={"saleng_id": "saleng-04"},
    )
    assert res_offline.status_code == 400
    assert "ปิดสถานะรับงาน" in res_offline.json()["detail"]

