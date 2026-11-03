"""
Backend API Tests สำหรับ AC-S05-05: Audit Logging for Booking & Cancellation
รองรับ UC-04, REQ-SEC-001, AC-S05-05, P-01, P-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_AC_S05_05_audit_logging_booking_and_cancellation():
    """
    ทดสอบว่าทุกการส่งคำขอนัดหมาย และการกดยกเลิก ต้องถูกบันทึกประวัติลงใน audit_logs
    """
    order_id = "order-audit-test-s05"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "status": "S1",
    }

    # 1. ส่งคำขอจองคิว S1 -> S2
    client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/book?seller_id=seller-01",
        json={"booking_type": "IMMEDIATE"},
    )
    submit_logs = [
        l for l in supabase_store.audit_logs
        if l.get("action") == "ORDER_SUBMITTED" and l.get("entity_id") == order_id
    ]
    assert len(submit_logs) >= 1
    assert submit_logs[-1]["actor_id"] == "seller-01"

    # 2. กดยกเลิกคำขอ S2 -> S8
    client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/cancel?seller_id=seller-01",
        json={"reason": "ขอยกเลิกนัดหมายเพื่อทดสอบ audit log"},
    )
    cancel_logs = [
        l for l in supabase_store.audit_logs
        if l.get("action") == "ORDER_CANCELLED_BY_SELLER" and l.get("entity_id") == order_id
    ]
    assert len(cancel_logs) >= 1
    assert cancel_logs[-1]["actor_id"] == "seller-01"
    assert "ขอยกเลิกนัดหมายเพื่อทดสอบ audit log" in str(cancel_logs[-1]["details"])

