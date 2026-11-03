"""
Unit & Integration Tests for T-02: Weighing Recording & Settlement Calculation
รองรับ REQ-BR-002, P-03, D-04
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_record_weighing_and_settlement_calculation():
    """
    ทดสอบการบันทึกผลชั่งจริงหน้างานโดยซาเล้ง และคำนวณยอดเงินสุทธิ
    รองรับ REQ-BR-002, P-03
    สูตร: ยอดสุทธิ = actual_quantity * locked_unit_price
    """
    # 1. จัดเตรียมคำขอนัดหมายในสถานะ S4 (ซาเล้งถึงหน้างาน) พร้อมราคาที่ล็อกไว้ (locked_unit_price)
    order_data = {
        "seller_id": "usr-seller-02",
        "buyer_id": "usr-saleng-02",
        "pickup_location_id": "loc-02",
        "status": "S4",
        "total_est_min_price": 500.0,
        "total_est_max_price": 650.0,
    }
    items_data = [
        {
            "category_code": "MAT-CARDBOARD",
            "unit": "kg",
            "est_quantity": 50.0,
            "est_min_price": 150.0,
            "est_max_price": 200.0,
            "locked_unit_price": 3.5,  # ล็อกไว้ 3.50 บาท/กก.
        },
        {
            "category_code": "MAT-GLASS-BOTTLE-BAG",
            "unit": "bag",
            "est_quantity": 2.0,
            "est_min_price": 80.0,
            "est_max_price": 120.0,
            "locked_unit_price": 45.0,  # ล็อกไว้ 45.00 บาท/กระสอบ
        },
    ]
    created_order = supabase_store.create_order(order_data, items_data)
    order_id = created_order["order_id"]
    item_cardboard_id = created_order["items"][0]["item_id"]
    item_bottle_id = created_order["items"][1]["item_id"]

    # 2. ซาเล้งส่งค่าน้ำหนักชั่งจริง: กระดาษลัง 60 กก. (ชั่งได้มากกว่าเดิม), ขวดแก้ว 2 กระสอบ
    # ยอดคำนวณที่คาดหวัง: (60 * 3.5) + (2 * 45) = 210.0 + 90.0 = 300.0 บาท
    weighing_payload = {
        "scale_photo_url": "https://storage.saleng.app/scales/scale-02.jpg",
        "items": [
            {"item_id": item_cardboard_id, "actual_quantity": 60.0},
            {"item_id": item_bottle_id, "actual_quantity": 2.0},
        ],
    }

    resp = client.post(f"/api/v1/orders/{order_id}/record-weighing", json=weighing_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["order_id"] == order_id
    assert data["status"] == "S5"  # เปลี่ยนเป็น S5 (Re-Quote / Weight Confirmed Gate)
    assert data["total_settled_amount"] == 300.0
    assert data["scale_photo_url"] == "https://storage.saleng.app/scales/scale-02.jpg"
    assert data["seller_confirmed_weight"] is False
    assert len(data["items"]) == 2

    cardboard_out = next(i for i in data["items"] if i["item_id"] == item_cardboard_id)
    assert cardboard_out["actual_quantity"] == 60.0
    assert cardboard_out["locked_unit_price"] == 3.5
    assert cardboard_out["settled_item_price"] == 210.0

    bottle_out = next(i for i in data["items"] if i["item_id"] == item_bottle_id)
    assert bottle_out["actual_quantity"] == 2.0
    assert bottle_out["locked_unit_price"] == 45.0
    assert bottle_out["settled_item_price"] == 90.0

    # 3. ตรวจสอบ Audit Log ว่าบันทึกสถานะ S5
    audit = [l for l in supabase_store.audit_logs if l["entity_id"] == order_id and l["action"] == "ORDER_WEIGHING_RECORDED"]
    assert len(audit) == 1
    assert audit[0]["details"]["total_settled_amount"] == 300.0


def test_record_weighing_invalid_order_status():
    """ทดสอบบล็อกการบันทึกผลชั่งหากสถานะใบงานไม่ถูกต้อง (เช่น อยู่ใน S1 หรือ S7 แล้ว)"""
    order_data = {
        "seller_id": "usr-seller-03",
        "pickup_location_id": "loc-03",
        "status": "S1",  # ฉบับร่าง ซาเล้งยังไม่ได้รับงาน
    }
    items_data = [
        {
            "category_code": "MAT-CARDBOARD",
            "est_quantity": 20.0,
            "locked_unit_price": 3.0,
        }
    ]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]
    item_id = created["items"][0]["item_id"]

    resp = client.post(
        f"/api/v1/orders/{order_id}/record-weighing",
        json={
            "scale_photo_url": "https://scale.jpg",
            "items": [{"item_id": item_id, "actual_quantity": 25.0}],
        },
    )
    assert resp.status_code == 400
    assert "ไม่สามารถบันทึกผลชั่งจริงได้" in resp.json()["detail"]


def test_record_weighing_item_not_found():
    """ทดสอบกรณี item_id ที่ส่งมาไม่มีอยู่ในใบงาน"""
    order_data = {
        "seller_id": "usr-seller-04",
        "status": "S4",
    }
    created = supabase_store.create_order(order_data, [])
    order_id = created["order_id"]

    resp = client.post(
        f"/api/v1/orders/{order_id}/record-weighing",
        json={
            "scale_photo_url": "https://scale.jpg",
            "items": [{"item_id": "non-existent-item", "actual_quantity": 10.0}],
        },
    )
    assert resp.status_code == 400
    assert "ไม่พบรายการรหัส" in resp.json()["detail"]

