"""
Acceptance Tests for AC-B06-02: Price Calculation with Locked Rates and ±15% Re-quote Threshold
(Task T-03: REQ-BR-002, D-B06-03, MD-STM-04)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_price_calc_test_environment():
    """เตรียมข้อมูลสำหรับการทดสอบการคำนวณราคาด้วยราคาล็อกและเกณฑ์ ±15%"""
    order_id = "order-b06-ac02"
    item_id = "item-b06-ac02-1"

    orig_benchmark = dict(supabase_store.benchmark_prices["PAPER_BOX"]) if "PAPER_BOX" in supabase_store.benchmark_prices else None
    supabase_store.benchmark_prices["PAPER_BOX"] = {
        "category_code": "PAPER_BOX",
        "category_name": "กระดาษลัง",
        "unit": "kg",
        "min_price_per_unit": 2.5,
        "max_price_per_unit": 3.5,
        "price_per_unit": 3.0,
    }

    # แต่คำขอนี้ล็อกราคาไว้ที่ 5.0 บาทตอนนัดหมาย
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-01",
        "saleng_id": "saleng-01",
        "buyer_id": "saleng-01",
        "status": "S4",
        "items": [
            {
                "item_id": item_id,
                "order_id": order_id,
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 100.0,
                "locked_unit_price": 5.0,  # ราคาล็อก
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
    if orig_benchmark:
        supabase_store.benchmark_prices["PAPER_BOX"] = orig_benchmark
    else:
        supabase_store.benchmark_prices.pop("PAPER_BOX", None)


def test_AC_B06_02_calculation_uses_locked_rate_not_benchmark():
    """คำนวณยอดเงินสุทธิด้วยราคาล็อก (5.0 บาท) ไม่ใช่ราคากลางปัจจุบัน (3.0 บาท) (REQ-BR-002)"""
    order_id = "order-b06-ac02"
    payload = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "https://storage.saleng.app/scales/order-b06-ac02.jpg",
        "items": [
            {"item_id": "item-b06-ac02-1", "actual_quantity": 100.0},
        ],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # 100.0 * 5.0 = 500.0 บาท (ถ้าผิดไปใช้ราคากลางจะเป็น 300.0)
    assert data["total_settled_amount"] == 500.0
    # ส่วนต่าง 0% ไม่เกิน ±15% -> is_re_quote = False
    assert data["is_re_quote"] is False


def test_AC_B06_02_difference_exceeds_15_percent_triggers_re_quote():
    """เมื่อปริมาณชั่งจริงต่างจากประเมินเกิน ±15% ให้ตั้งค่า is_re_quote = True (MD-STM-04)"""
    order_id = "order-b06-ac02"
    # เดิมประเมิน 100.0 กก. ชั่งจริงได้ 125.0 กก. (+25% เกิน 15%)
    payload = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "https://storage.saleng.app/scales/order-b06-ac02.jpg",
        "items": [
            {"item_id": "item-b06-ac02-1", "actual_quantity": 125.0},
        ],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # 125.0 * 5.0 = 625.0 บาท
    assert data["total_settled_amount"] == 625.0
    assert data["is_re_quote"] is True


def test_AC_B06_02_difference_under_15_percent_no_re_quote():
    """เมื่อปริมาณชั่งจริงต่างจากประเมินไม่เกิน ±15% จะไม่ติด re_quote"""
    order_id = "order-b06-ac02"
    # เดิมประเมิน 100.0 กก. ชั่งจริงได้ 90.0 กก. (-10% ไม่เกิน 15%)
    payload = {
        "saleng_id": "saleng-01",
        "scale_photo_url": "https://storage.saleng.app/scales/order-b06-ac02.jpg",
        "items": [
            {"item_id": "item-b06-ac02-1", "actual_quantity": 90.0},
        ],
    }
    resp = client.post(f"/api/v1/collectors/billing/{order_id}/weighing", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # 90.0 * 5.0 = 450.0 บาท
    assert data["total_settled_amount"] == 450.0
    assert data["is_re_quote"] is False
