"""
Acceptance Tests for AC-B06-05: Digital Receipt Summary & PII Masking
(Task T-05: UC-07, REQ-FN-005, REQ-SEC-002, CC-06)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_receipt_test_environment():
    """เตรียมข้อมูลคำขอขายสำหรับการทดสอบใบเสร็จดิจิทัล"""
    order_id = "order-b06-ac05"
    item_id = "item-b06-ac05-1"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S7",
        "seller_confirmed_weight": True,
        "payment_method": "PROMPTPAY",
        "total_settled_amount": 350.0,
        "seller_name": "สมศรี เจริญสุข",
        "seller_phone": "0891234567",
        "payment_confirmed_at": "2026-11-04T10:30:00Z",
        "receipt_id": "REC-20261104-AC05",
        "items": [
            {
                "item_id": item_id,
                "order_id": order_id,
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 70.0,
                "actual_quantity": 70.0,
                "locked_unit_price": 5.0,
                "settled_item_price": 350.0,
                "unit": "กก.",
            }
        ],
    }
    supabase_store.items[item_id] = dict(supabase_store.orders[order_id]["items"][0])

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "name": "สมชาย ซาเล้งสุพรรณ",
        "phone": "0819876543",
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.items.pop(item_id, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B06_05_get_digital_receipt_success():
    """ดึงใบเสร็จดิจิทัลในสถานะ S7 สำเร็จ พร้อมข้อมูลสรุปและ Mask เบอร์โทรศัพท์ (REQ-FN-005, REQ-SEC-002)"""
    order_id = "order-b06-ac05"
    resp = client.get(f"/api/v1/collectors/billing/{order_id}/receipt?saleng_id=saleng-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == order_id
    assert data["receipt_id"] == "REC-20261104-AC05"
    assert data["seller_name"] == "สมศรี เจริญสุข"
    # ตรวจสอบ Mask เบอร์โทรศัพท์ผู้ขาย: 0891234567 -> 08X-XXX-4567
    assert data["seller_phone_masked"] == "08X-XXX-4567"
    # ตรวจสอบ Mask เบอร์โทรศัพท์ซาเล้ง: 0819876543 -> 08X-XXX-6543
    assert data["collector_phone_masked"] == "08X-XXX-6543"
    assert data["payment_method"] == "PROMPTPAY"
    assert data["total_settled_amount"] == 350.0
    assert len(data["items"]) == 1
    assert data["items"][0]["category_name"] == "กระดาษลัง"
    assert data["items"][0]["actual_quantity"] == 70.0
    assert data["items"][0]["locked_unit_price"] == 5.0
    assert data["items"][0]["settled_item_price"] == 350.0


def test_AC_B06_05_receipt_blocked_if_order_not_completed():
    """หากคำขอขายยังไม่อยู่ในสถานะ S7 (เช่น ยังอยู่ S6 รอยืนยันเงิน) จะไม่สามารถดึงใบเสร็จได้"""
    order_id = "order-b06-ac05"
    supabase_store.orders[order_id]["status"] = "S6"

    resp = client.get(f"/api/v1/collectors/billing/{order_id}/receipt?saleng_id=saleng-01")
    assert resp.status_code == 400
    assert "S7" in resp.json()["detail"]

