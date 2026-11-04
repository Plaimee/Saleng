"""
Automated Test for AC-A02-04: Price Snapshot Integrity on Ongoing Orders
รองรับ REQ-BR-002, D-00-02, D-A02-05, AC-A02-04
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_store():
    orig_cardboard = dict(supabase_store.benchmark_prices.get("MAT-CARDBOARD", {}))
    created_orders = []
    yield created_orders
    if orig_cardboard:
        supabase_store.benchmark_prices["MAT-CARDBOARD"] = orig_cardboard
    for oid in created_orders:
        supabase_store.orders.pop(oid, None)


def test_AC_A02_04_price_update_affects_S1_S2_but_locks_S3_to_S7(cleanup_store):
    """
    ทดสอบว่าการปรับราคากลางใหม่:
    1. ออเดอร์สถานะ S1/S2 จะได้รับการคำนวณราคาประเมินใหม่ตามเรตล่าสุดทันที
    2. ออเดอร์สถานะ S3 ถึง S7 จะถูกล็อกราคาเดิมตาม Price Snapshot ณ เวลาที่กดรับงานอย่างเคร่งครัด
    รองรับ AC-A02-04, REQ-BR-002, D-00-02, D-A02-05
    """
    # 1. ตั้งค่าราคาเริ่มต้นสำหรับ MAT-CARDBOARD: 3.0 - 4.0 บาท/กก.
    supabase_store.update_benchmark_price(
        category_code="MAT-CARDBOARD",
        min_price=3.0,
        max_price=4.0,
        updated_by="admin-01",
    )

    # 2. สร้างออเดอร์ S2 (รอซาเล้งรับงาน) ปริมาณ 100 กก.
    order_id_s2 = f"order-test-s2-{uuid.uuid4().hex[:6]}"
    cleanup_store.append(order_id_s2)
    item_id_s2 = f"item-test-s2-{uuid.uuid4().hex[:6]}"
    order_s2 = {
        "order_id": order_id_s2,
        "seller_id": "seller-01",
        "status": "S2",
        "total_est_min_price": 300.0,
        "total_est_max_price": 400.0,
        "items": [
            {
                "item_id": item_id_s2,
                "order_id": order_id_s2,
                "category_code": "MAT-CARDBOARD",
                "quantity": 100.0,
                "unit": "kg",
                "est_min_price": 300.0,
                "est_max_price": 400.0,
            }
        ],
    }
    supabase_store.orders[order_id_s2] = order_s2
    supabase_store.items[item_id_s2] = order_s2["items"][0]

    # 3. สร้างออเดอร์ S3 (ซาเล้งกดรับงานแล้ว ล็อก Price Snapshot) ปริมาณ 100 กก.
    order_id_s3 = f"order-test-s3-{uuid.uuid4().hex[:6]}"
    cleanup_store.append(order_id_s3)
    item_id_s3 = f"item-test-s3-{uuid.uuid4().hex[:6]}"
    order_s3 = {
        "order_id": order_id_s3,
        "seller_id": "seller-02",
        "buyer_id": "saleng-01",
        "status": "S3",
        "total_est_min_price": 300.0,
        "total_est_max_price": 400.0,
        "items": [
            {
                "item_id": item_id_s3,
                "order_id": order_id_s3,
                "category_code": "MAT-CARDBOARD",
                "quantity": 100.0,
                "unit": "kg",
                "est_min_price": 300.0,
                "est_max_price": 400.0,
                "locked_unit_price": 3.0,
            }
        ],
    }
    supabase_store.orders[order_id_s3] = order_s3
    supabase_store.items[item_id_s3] = order_s3["items"][0]

    # 4. แอดมินปรับราคากลาง MAT-CARDBOARD ขึ้นเป็น 4.0 - 5.0 บาท/กก. (เปลี่ยนจาก mid 3.5 -> 4.5 = +28.5% <= 50%)
    update_res = client.put(
        "/api/v1/admin/benchmark-prices/MAT-CARDBOARD",
        json={
            "min_price_per_unit": 4.0,
            "max_price_per_unit": 5.0,
            "confirm_shift": False,
            "updated_by": "admin-01",
        },
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert update_res.status_code == 200

    # 5. ตรวจสอบออเดอร์ S2: ต้องได้รับการคำนวณราคาใหม่ (100 * 4.0 = 400, 100 * 5.0 = 500)
    updated_order_s2 = supabase_store.get_order(order_id_s2)
    assert updated_order_s2["total_est_min_price"] == 400.0
    assert updated_order_s2["total_est_max_price"] == 500.0
    assert updated_order_s2["items"][0]["est_min_price"] == 400.0
    assert updated_order_s2["items"][0]["est_max_price"] == 500.0

    # 6. ตรวจสอบออเดอร์ S3: ต้องล็อกราคาเดิมตาม Price Snapshot ไม่เปลี่ยนแปลง (ยังคงเป็น 300 - 400)
    updated_order_s3 = supabase_store.get_order(order_id_s3)
    assert updated_order_s3["total_est_min_price"] == 300.0
    assert updated_order_s3["total_est_max_price"] == 400.0
    assert updated_order_s3["items"][0]["locked_unit_price"] == 3.0
    assert updated_order_s3["items"][0]["est_min_price"] == 300.0
    assert updated_order_s3["items"][0]["est_max_price"] == 400.0
