"""
Automated Test for AC-S06-02: Dispute & Re-Weigh Options
รองรับ REQ-FN-006, REQ-SEC-001, AC-S06-02, P-02, Q-02
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_seller_requests_reweigh_successfully():
    """
    AC-S06-02: ผู้ขายเลือก 'ขอให้ชั่งซ้ำ'
    คำขอกลับสู่สถานะ S4 เพื่อให้ซาเล้งตรวจสอบและชั่งใหม่ พร้อมบันทึก Audit Log
    """
    order_data = {
        "seller_id": "usr-seller-rw01",
        "buyer_id": "usr-saleng-rw01",
        "status": "S5",
        "scale_photo_url": "https://storage.saleng.app/scales/scale-rw01.jpg",
        "total_settled_amount": 200.0,
    }
    items_data = [
        {"category_code": "MAT-CARDBOARD", "actual_quantity": 40.0, "locked_unit_price": 5.0}
    ]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]

    # ผู้ขายส่งคำขอชั่งซ้ำ
    req_payload = {
        "seller_id": "usr-seller-rw01",
        "reason": "ตาชั่งน่าจะค้าง ขอให้ยกของลงแล้ววางชั่งใหม่อีกครั้งครับ",
    }
    resp = client.post(f"/api/v1/orders/{order_id}/request-reweigh", json=req_payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == order_id
    assert data["status"] == "S4"  # กลับสู่ S4 เพื่อชั่งใหม่
    assert "ชั่งน้ำหนักใหม่" in data["message"]

    # ตรวจสอบฐานข้อมูล
    updated = supabase_store.get_order(order_id)
    assert updated["status"] == "S4"
    assert updated["reweigh_requested"] is True
    assert updated["seller_confirmed_weight_at"] is None

    # ตรวจสอบ Audit Log
    logs = [l for l in supabase_store.audit_logs if l["entity_id"] == order_id and l["action"] == "SELLER_REQUESTED_REWEIGH"]
    assert len(logs) == 1
    assert logs[0]["actor_id"] == "usr-seller-rw01"
    assert logs[0]["details"]["new_status"] == "S4"


def test_seller_raises_dispute_successfully():
    """
    AC-S06-02: ผู้ขายกด 'ปฏิเสธผลชั่ง / แจ้งข้อพิพาท' (REQ-FN-006)
    ระบบเปลี่ยนสถานะเป็น S8 (Disputed) พร้อมล็อกภาพตาชั่งและราคาที่ล็อกไว้เพื่อส่งต่อให้ Admin
    """
    order_data = {
        "seller_id": "usr-seller-disp01",
        "buyer_id": "usr-saleng-disp01",
        "status": "S5",
        "scale_photo_url": "https://storage.saleng.app/scales/scale-disp01.jpg",
        "total_settled_amount": 150.0,
    }
    items_data = [
        {"category_code": "MAT-CARDBOARD", "actual_quantity": 30.0, "locked_unit_price": 5.0}
    ]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]

    dispute_payload = {
        "seller_id": "usr-seller-disp01",
        "dispute_reason": "ตาชั่งตัวเลขกระโดดผิดปกติ น้ำหนักหายไปกว่าครึ่ง ซาเล้งไม่ยอมชั่งใหม่",
    }
    resp = client.post(f"/api/v1/orders/{order_id}/dispute", json=dispute_payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == order_id
    assert data["status"] == "S8"  # S8: ข้อพิพาท
    assert data["dispute_reason"] == dispute_payload["dispute_reason"]
    assert "ส่งต่อให้ผู้ดูแลระบบ" in data["message"]

    # ตรวจสอบฐานข้อมูลว่า is_frozen = True (ล็อกหลักฐานตาม REQ-FN-006)
    updated = supabase_store.get_order(order_id)
    assert updated["status"] == "S8"
    assert updated["is_frozen"] is True
    assert updated["dispute_reason"] == dispute_payload["dispute_reason"]

    # ตรวจสอบ Audit Log
    logs = [l for l in supabase_store.audit_logs if l["entity_id"] == order_id and l["action"] == "ORDER_DISPUTED"]
    assert len(logs) == 1
    assert logs[0]["actor_id"] == "usr-seller-disp01"
    assert logs[0]["details"]["new_status"] == "S8"
    assert logs[0]["details"]["scale_photo_url"] == "https://storage.saleng.app/scales/scale-disp01.jpg"


def test_dispute_unauthorized_user():
    """AC-S06-02: บล็อกบุคคลอื่นที่ไม่ใช่ผู้ขายเจ้าของคำขอจากการแจ้งข้อพิพาท (HTTP 403)"""
    order_data = {
        "seller_id": "usr-owner-seller",
        "status": "S5",
    }
    created = supabase_store.create_order(order_data, [])
    order_id = created["order_id"]

    resp = client.post(
        f"/api/v1/orders/{order_id}/dispute",
        json={"seller_id": "usr-impostor", "dispute_reason": "ทดสอบข้อพิพาทจากบุคคลอื่น"}
    )
    assert resp.status_code == 403
    assert "ผู้ขายเจ้าของคำขอเท่านั้น" in resp.json()["detail"]


def test_dispute_invalid_status():
    """AC-S06-02: บล็อกการแจ้งข้อพิพาทหากงานปิดไปแล้ว (สถานะ S7)"""
    order_data = {
        "seller_id": "usr-seller-completed",
        "status": "S7",  # สำเร็จแล้ว
    }
    created = supabase_store.create_order(order_data, [])
    order_id = created["order_id"]

    resp = client.post(
        f"/api/v1/orders/{order_id}/dispute",
        json={"seller_id": "usr-seller-completed", "dispute_reason": "พยายามแจ้งข้อพิพาทหลังปิดงาน"}
    )
    assert resp.status_code == 400
    assert "ไม่สามารถแจ้งข้อพิพาทผลชั่งได้" in resp.json()["detail"]

