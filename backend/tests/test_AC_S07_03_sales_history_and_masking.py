"""
Automated Backend Tests สำหรับ AC-S07-03: Sales History & PII Masking
รองรับ REQ-FN-005, REQ-SEC-002, AC-S07-03, P-03, Q-04
"""

import uuid
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_sales_history_summary_and_masking():
    """
    AC-S07-03 / REQ-SEC-002:
    1. สรุปยอดเงินรวม น้ำหนักรวม และจำนวนครั้งสำเร็จ
    2. ปกปิดเบอร์โทรศัพท์เป็น 08X-XXX-XXXX (PDPA Masking)
    3. กรองเฉพาะสถานะ S7 เท่านั้น
    """
    seller_id = "SELLER-HIST-01"
    collector_id = "COLLECTOR-HIST-01"

    # บันทึกเป็นผู้รับซื้อประจำไว้ก่อน
    supabase_store.add_favorite(seller_id, collector_id)

    # 1. คำขอที่ 1 (S7: สำเร็จ, 300 บาท, น้ำหนัก 30 กก.)
    order_id_1 = "ORDER-HIST-S7-01"
    supabase_store.orders[order_id_1] = {
        "order_id": order_id_1,
        "seller_id": seller_id,
        "collector_id": collector_id,
        "collector_name": "พี่สมชาย",
        "buyer_phone": "0812345678",
        "status": "S7",
        "total_settled_amount": 300.0,
        "payment_method": "PROMPTPAY",
        "payment_confirmed_at": "2026-11-03T10:00:00Z",
    }
    supabase_store.items[str(uuid.uuid4())] = {
        "order_id": order_id_1,
        "category_code": "MAT-CARDBOARD",
        "category_name": "กระดาษลัง",
        "actual_quantity": 30.0,
        "unit": "kg",
        "locked_unit_price": 10.0,
        "settled_item_price": 300.0,
    }

    # 2. คำขอที่ 2 (S7: สำเร็จ, 200 บาท, น้ำหนัก 20 กก.)
    order_id_2 = "ORDER-HIST-S7-02"
    supabase_store.orders[order_id_2] = {
        "order_id": order_id_2,
        "seller_id": seller_id,
        "collector_id": "COLLECTOR-OTHER",
        "collector_name": "นายวิชัย",
        "buyer_phone": "0898765432",
        "status": "S7",
        "total_settled_amount": 200.0,
        "payment_method": "CASH",
        "payment_confirmed_at": "2026-11-02T15:00:00Z",
    }
    supabase_store.items[str(uuid.uuid4())] = {
        "order_id": order_id_2,
        "category_code": "MAT-WHITE-PAPER",
        "category_name": "กระดาษขาวดำ",
        "actual_quantity": 20.0,
        "unit": "kg",
        "locked_unit_price": 10.0,
        "settled_item_price": 200.0,
    }

    # 3. คำขอที่ 3 (S5: ยังไม่จบงาน ต้องไม่รวมในประวัติการขายสำเร็จ)
    order_id_3 = "ORDER-HIST-S5-IGNORE"
    supabase_store.orders[order_id_3] = {
        "order_id": order_id_3,
        "seller_id": seller_id,
        "status": "S5",
        "total_settled_amount": 1000.0,
    }

    # ยิง API ดึงประวัติการขาย
    response = client.get(f"/api/v1/sellers/{seller_id}/sales-history")
    assert response.status_code == 200
    data = response.json()

    # ตรวจสอบภาพรวมสรุปสะสม
    summary = data["summary"]
    assert summary["total_sales_amount"] == 500.0  # 300 + 200
    assert summary["total_weight_kg"] == 50.0      # 30 + 20
    assert summary["total_completed_orders"] == 2  # เฉพาะ 2 คำขอ S7

    # ตรวจสอบรายการคำขอ
    orders = data["orders"]
    assert len(orders) == 2

    order1 = next(o for o in orders if o["order_id"] == order_id_1)
    assert order1["collector_phone_masked"] == "08X-XXX-5678"
    assert order1["is_favorite_collector"] is True

    order2 = next(o for o in orders if o["order_id"] == order_id_2)
    assert order2["collector_phone_masked"] == "08X-XXX-5432"
    assert order2["is_favorite_collector"] is False

    # REQ-SEC-002: ตรวจสอบว่าไม่มีเบอร์จริงรั่วไหลใน Payload
    assert "0812345678" not in response.text
    assert "0898765432" not in response.text

