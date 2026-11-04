"""
Acceptance Tests for AC-B06-01: Actual Weight Recording & Scale Photo Attachment
(Task T-02: UC-05, REQ-FN-002, D-B06-02)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_billing_test_environment():
    """เตรียมข้อมูลคำขอขายและโปรไฟล์ซาเล้งสำหรับการทดสอบการชั่งน้ำหนัก"""
    order_id = "order-b06-ac01"
    item_id_1 = "item-b06-ac01-1"
    item_id_2 = "item-b06-ac01-2"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S4",
        "scale_photo_url": None,
        "seller_confirmed_weight": False,
        "items": [
            {
                "item_id": item_id_1,
                "order_id": order_id,
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 20.0,
                "locked_unit_price": 4.5,
                "unit": "กก.",
            },
            {
                "item_id": item_id_2,
                "order_id": order_id,
                "category_code": "GLASS_CLEAR",
                "category_name": "ขวดแก้วใส",
                "estimated_quantity": 10.0,
                "locked_unit_price": 2.5,
                "unit": "กก.",
            },
        ],
    }

    supabase_store.items[item_id_1] = dict(supabase_store.orders[order_id]["items"][0])
    supabase_store.items[item_id_2] = dict(supabase_store.orders[order_id]["items"][1])

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
    })

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.items.pop(item_id_1, None)
    supabase_store.items.pop(item_id_2, None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile


def test_AC_B06_01_get_weighing_sheet():
    """ซาเล้งสามารถดึงใบชั่งน้ำหนักที่มีรายการและราคาล็อกของคำขอขายได้"""
    order_id = "order-b06-ac01"
    resp = client.get(f"/api/v1/collectors/billing/{order_id}/weighing-sheet?saleng_id=saleng-01")
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == order_id
    assert data["order_status"] == "S4"
    assert len(data["items"]) == 2
    assert data["items"][0]["locked_unit_price"] == 4.5
    assert data["seller_phone_masked"] != ""


def test_AC_B06_01_record_actual_weight_success():
    """ซาเล้งบันทึกผลชั่งจริงพร้อมแนบรูปถ่ายตาชั่งสำเร็จ (S4 -> S5)"""
    order_id = "order-b06-ac01"
    payload = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "https://storage.saleng.app/scales/order-b06-ac01.jpg",
        "items": [
            {"item_id": "item-b06-ac01-1", "actual_quantity": 21.0},
            {"item_id": "item-b06-ac01-2", "actual_quantity": 9.5},
        ],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["order_id"] == order_id
    assert data["new_status"] == "S5"
    assert data["scale_photo_url"] == payload["scale_photo_url"]
    assert data["seller_confirmed_weight"] is False
    # ตรวจสอบยอดเงินสุทธิ: (21 * 4.5) + (9.5 * 2.5) = 94.5 + 23.75 = 118.25
    assert data["total_settled_amount"] == 118.25

    # ตรวจสอบว่า order ใน database ถูกอัปเดตเป็น S5
    order = supabase_store.get_order(order_id)
    assert order["status"] == "S5"
    assert order["scale_photo_url"] == payload["scale_photo_url"]


def test_AC_B06_01_reject_without_scale_photo():
    """ปฏิเสธหากไม่มีภาพถ่ายหน้าตาชั่งดิจิทัล (REQ-FN-002, D-B06-02)"""
    order_id = "order-b06-ac01"
    payload = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "",  # Empty photo URL
        "items": [
            {"item_id": "item-b06-ac01-1", "actual_quantity": 20.0},
        ],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code in [400, 422]


def test_AC_B06_01_reject_invalid_quantity():
    """ปฏิเสธหากน้ำหนักชั่งจริง <= 0 กก."""
    order_id = "order-b06-ac01"
    payload = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "https://storage.saleng.app/scales/order-b06-ac01.jpg",
        "items": [
            {"item_id": "item-b06-ac01-1", "actual_quantity": 0.0},
        ],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code in [400, 422]


def test_AC_B06_01_kyc_unverified_blocked():
    """ซาเล้งที่ยังไม่ผ่าน KYC ไม่สามารถเข้าใช้งานระบบคิดเงินได้ (D-00-01)"""
    order_id = "order-b06-ac01"
    supabase_store.saleng_profiles["saleng-unverified"] = {
        "id": "saleng-unverified",
        "verified": False,
        "kyc_status": "PENDING",
    }
    payload = {
        "saleng_id": "saleng-unverified",
        "scale_photo_url": "https://storage.saleng.app/scales/order-b06-ac01.jpg",
        "items": [{"item_id": "item-b06-ac01-1", "actual_quantity": 10.0}],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code == 403
    del supabase_store.saleng_profiles["saleng-unverified"]

