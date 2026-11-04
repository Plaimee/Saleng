"""
Acceptance Tests for AC-B06-04: Payment Method Selection (Cash vs PromptPay)
(Task T-05: UC-06, REQ-FN-004, D-B06-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_payment_method_test_environment():
    """เตรียมข้อมูลคำขอขายในสถานะ S6 สำหรับการทดสอบเลือกวิธีชำระเงิน"""
    order_id = "order-b06-ac04"
    item_id = "item-b06-ac04-1"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S6",
        "seller_confirmed_weight": True,
        "total_settled_amount": 500.0,
        "payment_method": None,
        "items": [
            {
                "item_id": item_id,
                "order_id": order_id,
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 100.0,
                "actual_quantity": 100.0,
                "locked_unit_price": 5.0,
                "settled_item_price": 500.0,
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


def test_AC_B06_04_select_cash_payment():
    """ซาเล้งเลือกชำระเงินสด (CASH) สำเร็จ"""
    order_id = "order-b06-ac04"
    payload = {
        "saleng_id": "saleng-01",
        "payment_method": "CASH",
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/payment-method", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["payment_method"] == "CASH"

    order = supabase_store.get_order(order_id)
    assert order["payment_method"] == "CASH"


def test_AC_B06_04_select_promptpay_payment():
    """ซาเล้งเลือกชำระผ่าน PromptPay QR สำเร็จ"""
    order_id = "order-b06-ac04"
    payload = {
        "saleng_id": "saleng-01",
        "payment_method": "PROMPTPAY",
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/payment-method", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["payment_method"] == "PROMPTPAY"

    order = supabase_store.get_order(order_id)
    assert order["payment_method"] == "PROMPTPAY"


def test_AC_B06_04_reject_invalid_payment_method():
    """ปฏิเสธช่องทางชำระเงินนอกเหนือจาก CASH หรือ PROMPTPAY (เช่น บัตรเครดิต/Wallet ที่เป็น Non-goals)"""
    order_id = "order-b06-ac04"
    payload = {
        "saleng_id": "saleng-01",
        "payment_method": "CREDIT_CARD",
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/payment-method", json=payload)
    assert resp.status_code == 400

