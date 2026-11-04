"""
Acceptance Tests for AC-B06-03: 100% Confirmation Gate
(Task T-04: REQ-FN-004, AC-B06-03, D-B06-01, D-B06-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_seller_gate_test_environment():
    """เตรียมข้อมูลคำขอขายสำหรับการทดสอบประตูกั้นยืนยันน้ำหนัก 100%"""
    order_id = "order-b06-ac03"
    item_id = "item-b06-ac03-1"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S5",
        "seller_confirmed_weight": False,
        "total_settled_amount": 250.0,
        "items": [
            {
                "item_id": item_id,
                "order_id": order_id,
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 50.0,
                "actual_quantity": 50.0,
                "locked_unit_price": 5.0,
                "settled_item_price": 250.0,
                "unit": "กก.",
            }
        ],
    }
    supabase_store.items[item_id] = dict(supabase_store.orders[order_id]["items"][0])

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.items.pop(item_id, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B06_03_payment_method_blocked_when_seller_not_confirmed():
    """ซาเล้งถูกบล็อกไม่ให้เลือกชำระเงินจนกว่าผู้ขายจะยืนยันน้ำหนัก (HTTP 403 Forbidden)"""
    order_id = "order-b06-ac03"
    payload = {
        "saleng_id": "saleng-01",
        "payment_method": "CASH",
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/payment-method", json=payload)
    assert resp.status_code == 403
    assert "ผู้ขายยังไม่ได้ยืนยันผลการชั่งน้ำหนัก" in resp.json()["detail"]


def test_AC_B06_03_payment_method_allowed_after_seller_confirmed():
    """เมื่อผู้ขายยืนยันน้ำหนักแล้ว (S6, seller_confirmed_weight = True) ซาเล้งเลือกชำระเงินได้"""
    order_id = "order-b06-ac03"

    # ผู้ขายกดยืนยันน้ำหนัก (จำลองการยืนยันผ่าน seller endpoint หรืออัปเดต store)
    seller_confirm_resp = client.post(
        f"/api/v1/orders/{order_id}/confirm-weights",
        json={"seller_id": "seller-01"}
    )
    assert seller_confirm_resp.status_code == 200

    # ตอนนี้คำขออยู่ในสถานะ S6 และ seller_confirmed_weight = True
    payload = {
        "saleng_id": "saleng-01",
        "payment_method": "CASH",
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/payment-method", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["payment_method"] == "CASH"
    assert data["order_status"] == "S6"


def test_AC_B06_03_saleng_cannot_confirm_weights_on_behalf_of_seller():
    """ซาเล้งไม่สามารถใช้ saleng_id ไปเรียก confirm-weights แทนผู้ขายได้ (Two-Party Rule)"""
    order_id = "order-b06-ac03"
    resp = client.post(
        f"/api/v1/orders/{order_id}/confirm-weights",
        json={"seller_id": "saleng-01"}  # ซาเล้งพยายามยืนยันแทนผู้ขาย
    )
    assert resp.status_code == 403

