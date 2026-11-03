"""
Backend API Tests สำหรับ AC-S05-03: Pre-Transit Cancellation Guard & BR-03
รองรับ UC-04, BR-03, REQ-FN-003, AC-S05-03, P-03, Q-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S05_03_cancel_in_s2_and_s3_allowed():
    """
    ทดสอบว่าผู้ขายสามารถกดยกเลิกนัดหมายได้ในสถานะ S1..S3 ตามกฎ BR-03
    สถานะจะเปลี่ยนเป็น S8 และบันทึกเหตุผล
    """
    order_id = "order-cancel-allowed-s3"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S3",  # มีผู้รับงานแล้วแต่ยังไม่ออกเดินทาง
        "assigned_saleng_id": "saleng-01",
    }

    payload = {"reason": "ติดธุระด่วน ต้องออกจากบ้าน"}
    response = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/cancel?seller_id=seller-01",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "S8"
    assert data["can_cancel"] is False
    assert data["cancellation_reason"] == "ติดธุระด่วน ต้องออกจากบ้าน"

    # ตรวจสอบใน Store
    order_in_db = supabase_store.get_order(order_id)
    assert order_in_db is not None
    assert order_in_db["status"] == "S8"
    assert order_in_db["cancellation_reason"] == "ติดธุระด่วน ต้องออกจากบ้าน"


def test_AC_S05_03_cancel_in_s4_blocked_by_br03():
    """
    ทดสอบกฎเหล็ก BR-03: หากซาเล้งเริ่มออกเดินทาง (S4 In-Transit) แล้ว
    ระบบต้องปฏิเสธและบล็อกการยกเลิกของผู้ขายทันที (HTTP 400 Bad Request)
    """
    order_id = "order-cancel-blocked-s4"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S4",  # กำลังเดินทาง
        "assigned_saleng_id": "saleng-01",
    }

    # ตรวจสอบว่า can_cancel เป็น False
    status_res = client.get(f"/api/v1/booking-tracking/orders/{order_id}/status")
    assert status_res.json()["can_cancel"] is False

    # พยายามยิง API ยกเลิก
    payload = {"reason": "อยากยกเลิกตอนซาเล้งกำลังวิ่งรถ"}
    cancel_res = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/cancel?seller_id=seller-01",
        json=payload,
    )
    assert cancel_res.status_code == 400
    detail = cancel_res.json()["detail"]
    assert "BR-03" in detail
    assert "กำลังเดินทาง" in detail

    # สถานะคำขอต้องไม่เปลี่ยน ยังคงเป็น S4
    assert supabase_store.orders[order_id]["status"] == "S4"

