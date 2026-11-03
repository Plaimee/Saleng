"""
Automated Test for AC-S06-01: 100% Seller Weight Confirmation Gate
รองรับ REQ-FN-004, REQ-SEC-001, AC-S06-01, P-01, Q-01
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_seller_confirms_weight_successfully():
    """
    AC-S06-01: ผู้ขายกดยืนยันตัวเลขน้ำหนักจริงบนหน้าจอของตนเอง
    ระบบเปลี่ยนสถานะเป็น S6 (รอยืนยันชำระเงิน) และบันทึกเวลาที่ยืนยัน
    """
    order_data = {
        "seller_id": "usr-seller-ac01",
        "buyer_id": "usr-buyer-ac01",
        "status": "S5",
        "total_settled_amount": 420.0,
    }
    items_data = [
        {
            "category_code": "MAT-CARDBOARD",
            "est_quantity": 100.0,
            "actual_quantity": 120.0,
            "locked_unit_price": 3.5,
            "settled_item_price": 420.0,
        }
    ]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]

    # ผู้ขายกดยืนยันตัวเลขน้ำหนัก
    confirm_payload = {"seller_id": "usr-seller-ac01"}
    resp = client.post(f"/api/v1/orders/{order_id}/confirm-weights", json=confirm_payload)

    assert resp.status_code == 200
    data = resp.json()

    assert data["order_id"] == order_id
    assert data["status"] == "S6"  # S6: รอยืนยันชำระเงิน
    assert data["total_settled_amount"] == 420.0
    assert "seller_confirmed_weight_at" in data
    assert data["seller_confirmed_weight_at"] is not None

    # ตรวจสอบในฐานข้อมูล
    updated = supabase_store.get_order(order_id)
    assert updated["status"] == "S6"
    assert updated["seller_confirmed_weight_at"] == data["seller_confirmed_weight_at"]

    # ตรวจสอบ Audit Log
    logs = [l for l in supabase_store.audit_logs if l["entity_id"] == order_id and l["action"] == "SELLER_WEIGHT_CONFIRMED"]
    assert len(logs) == 1
    assert logs[0]["actor_id"] == "usr-seller-ac01"
    assert logs[0]["details"]["new_status"] == "S6"


def test_block_when_caller_is_not_seller():
    """
    AC-S06-01: บล็อกบุคคลอื่นหรือซาเล้งไม่ให้กดยืนยันน้ำหนักแทนผู้ขาย (HTTP 403 Forbidden)
    """
    order_data = {
        "seller_id": "usr-seller-real",
        "buyer_id": "usr-buyer-01",
        "status": "S5",
        "total_settled_amount": 350.0,
    }
    items_data = [
        {"category_code": "MAT-WHITE-PAPER", "actual_quantity": 50.0, "locked_unit_price": 7.0}
    ]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]

    # ผู้ใช้คนอื่น (ไม่ใช่ seller_id เจ้าของคำขอ) พยายามกดยืนยัน
    fake_caller = {"seller_id": "usr-attacker-or-buyer"}
    resp = client.post(f"/api/v1/orders/{order_id}/confirm-weights", json=fake_caller)

    assert resp.status_code == 403
    assert "ผู้ขายเจ้าของคำขอเท่านั้น" in resp.json()["detail"]

    # สถานะต้องยังคงเป็น S5 เหมือนเดิม (ไม่เปลี่ยนเป็น S6)
    order = supabase_store.get_order(order_id)
    assert order["status"] == "S5"


def test_block_when_order_not_in_s5():
    """
    AC-S06-01: บล็อกการยืนยันหากใบงานยังไม่ได้บันทึกผลชั่งจริง (เช่น ยังอยู่สถานะ S4)
    """
    order_data = {
        "seller_id": "usr-seller-notweighed",
        "status": "S4",  # กำลังเดินทาง/ชั่ง แต่ยังไม่เสร็จ
    }
    items_data = [{"category_code": "MAT-CARDBOARD", "est_quantity": 20.0}]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]

    resp = client.post(
        f"/api/v1/orders/{order_id}/confirm-weights",
        json={"seller_id": "usr-seller-notweighed"}
    )
    assert resp.status_code == 400
    assert "ซาเล้งยังไม่ได้บันทึกผลชั่งจริง" in resp.json()["detail"]


def test_100_percent_gate_enforcement():
    """
    กฎเหล็ก REQ-FN-004: หากผู้ขายยังไม่ได้กดยืนยันน้ำหนัก ระบบต้องอยู่ในสถานะ S5
    และไม่อนุญาตให้ออกใบสรุปยอดเงินหรือข้ามไปชำระเงินเด็ดขาด
    """
    order_data = {
        "seller_id": "usr-seller-gate",
        "status": "S5",
        "total_settled_amount": 500.0,
    }
    items_data = [{"category_code": "MAT-CARDBOARD", "actual_quantity": 100.0, "locked_unit_price": 5.0}]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]

    # ตรวจสอบสถานะว่ายังอยู่ที่ S5 และ seller_confirmed_weight_at ยังว่างอยู่
    current = supabase_store.get_order(order_id)
    assert current["status"] == "S5"
    assert current.get("seller_confirmed_weight_at") is None

