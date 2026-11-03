"""
End-to-End Lifecycle Integration Test: Payment & Verification Feature
รองรับ REQ-FN-004, REQ-FN-005, REQ-FN-006, REQ-BR-002, REQ-SEC-001, REQ-SEC-002, AC-S06-01..05, P-01..P-06
"""

import re
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_payment_and_verification_complete_lifecycle():
    """
    ทดสอบครบวงจรตั้งแต่ซาเล้งกรอกน้ำหนัก -> บล็อกหากผู้ขายยังไม่ยืนยัน
    -> ผู้ขายกดยืนยันน้ำหนัก -> เลือกวิธีรับเงิน -> ผู้ขายกดยืนยันรับเงิน
    -> เปลี่ยนเป็น S7 ออกใบเสร็จดิจิทัล พร้อมตรวจสอบประวัติ Audit Log ครบทุกขั้นตอน (AC-S06-05)
    """
    # -------------------------------------------------------------------------
    # 1. จัดเตรียมคำขอในสถานะ S4 พร้อมราคาล็อก ณ เวลานัดหมาย (REQ-BR-002)
    # -------------------------------------------------------------------------
    seller_id = "usr-seller-e2e-pay"
    buyer_id = "usr-saleng-e2e-pay"

    order_data = {
        "seller_id": seller_id,
        "buyer_id": buyer_id,
        "seller_phone": "0811223344",
        "buyer_phone": "0899887766",
        "pickup_location_id": "loc-e2e-pay",
        "status": "S4",
        "total_est_min_price": 400.0,
        "total_est_max_price": 550.0,
    }
    items_data = [
        {
            "category_code": "MAT-CARDBOARD",
            "unit": "kg",
            "est_quantity": 50.0,
            "est_min_price": 150.0,
            "est_max_price": 200.0,
            "locked_unit_price": 3.5,  # ล็อกราคา 3.50 บ./กก.
        },
        {
            "category_code": "MAT-GLASS-BOTTLE-BAG",
            "unit": "bag",
            "est_quantity": 2.0,
            "est_min_price": 80.0,
            "est_max_price": 120.0,
            "locked_unit_price": 45.0,  # ล็อกราคา 45.00 บ./กระสอบ
        },
    ]
    created = supabase_store.create_order(order_data, items_data)
    order_id = created["order_id"]
    item_cardboard_id = created["items"][0]["item_id"]
    item_bottle_id = created["items"][1]["item_id"]

    # -------------------------------------------------------------------------
    # 2. ซาเล้งบันทึกผลชั่งจริงหน้างาน (POST /api/v1/orders/{order_id}/record-weighing)
    # -------------------------------------------------------------------------
    weighing_payload = {
        "scale_photo_url": "https://storage.saleng.app/scales/e2e-scale.jpg",
        "items": [
            {"item_id": item_cardboard_id, "actual_quantity": 60.0},
            {"item_id": item_bottle_id, "actual_quantity": 2.0},
        ],
    }
    resp_weigh = client.post(f"/api/v1/orders/{order_id}/record-weighing", json=weighing_payload)
    assert resp_weigh.status_code == 200
    weigh_data = resp_weigh.json()

    assert weigh_data["status"] == "S5"  # เปลี่ยนเป็น S5 รอผู้ขายยืนยัน
    assert weigh_data["total_settled_amount"] == 300.0  # (60 * 3.5) + (2 * 45) = 300.0

    # -------------------------------------------------------------------------
    # 3. ทดสอบกฎเหล็ก 100% Confirmation Gate (REQ-FN-004, AC-S06-01):
    # หากผู้ขายยังไม่กดยืนยันน้ำหนัก จะไม่สามารถข้ามไปยืนยันรับเงินได้ (HTTP 400)
    # -------------------------------------------------------------------------
    resp_premature_pay = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": seller_id, "payment_method": "PROMPTPAY"},
    )
    assert resp_premature_pay.status_code == 400
    assert "ผู้ขายต้องยืนยันตัวเลขน้ำหนักก่อน" in resp_premature_pay.json()["detail"]

    # -------------------------------------------------------------------------
    # 4. ผู้ขายตรวจสอบและกดยืนยันตัวเลขน้ำหนัก (POST /api/v1/orders/{order_id}/confirm-weights)
    # -------------------------------------------------------------------------
    resp_confirm_weight = client.post(
        f"/api/v1/orders/{order_id}/confirm-weights",
        json={"seller_id": seller_id},
    )
    assert resp_confirm_weight.status_code == 200
    weight_conf_data = resp_confirm_weight.json()

    assert weight_conf_data["status"] == "S6"  # ปลดล็อกเข้าสู่ S6 (รอยืนยันชำระเงิน)
    assert weight_conf_data["total_settled_amount"] == 300.0

    # -------------------------------------------------------------------------
    # 5. ผู้ขายกดยืนยันรับเงิน PromptPay บนหน้าจอ (POST /api/v1/orders/{order_id}/confirm-payment)
    # -------------------------------------------------------------------------
    resp_pay = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": seller_id, "payment_method": "PROMPTPAY"},
    )
    assert resp_pay.status_code == 200
    pay_data = resp_pay.json()

    assert pay_data["status"] == "S7"  # S7: สำเร็จ / ปิดงาน
    assert pay_data["payment_method"] == "PROMPTPAY"
    assert pay_data["total_amount"] == 300.0
    receipt_no = pay_data["receipt_no"]
    assert re.fullmatch(r"REC-\d{8}-\d{4}", receipt_no)

    # -------------------------------------------------------------------------
    # 6. ดึงใบเสร็จดิจิทัล (GET /api/v1/receipts/{order_id})
    # -------------------------------------------------------------------------
    resp_receipt = client.get(f"/api/v1/receipts/{order_id}")
    assert resp_receipt.status_code == 200
    receipt = resp_receipt.json()

    assert receipt["receipt_no"] == receipt_no
    assert receipt["total_amount"] == 300.0
    assert receipt["payment_method"] == "PROMPTPAY"

    # REQ-SEC-002: ตรวจสอบ PII Masking
    assert receipt["seller_phone_masked"] == "08X-XXX-3344"
    assert receipt["buyer_phone_masked"] == "08X-XXX-7766"
    assert "0811223344" not in resp_receipt.text
    assert "0899887766" not in resp_receipt.text

    # -------------------------------------------------------------------------
    # 7. ตรวจสอบความสมบูรณ์ของ Audit Log ทุกขั้นตอน (AC-S06-05, REQ-SEC-001)
    # -------------------------------------------------------------------------
    order_logs = [l for l in supabase_store.audit_logs if l["entity_id"] == order_id]
    actions = [l["action"] for l in order_logs]

    # ต้องมี Log ครบทั้ง 3 ลำดับขั้น
    assert "ORDER_WEIGHING_RECORDED" in actions
    assert "SELLER_WEIGHT_CONFIRMED" in actions
    assert "SELLER_PAYMENT_CONFIRMED" in actions

    # -------------------------------------------------------------------------
    # 8. ตรวจสอบ Price Snapshot Integrity: แม้ราคากลางวันถัดไปเปลี่ยน ยอดในใบเสร็จต้องคงเดิม
    # -------------------------------------------------------------------------
    supabase_store.upsert_benchmark_price({
        "category_code": "MAT-CARDBOARD",
        "category_name": "กระดาษลัง",
        "unit": "kg",
        "min_price_per_unit": 10.0,  # ราคากระโดดเป็น 10 บาท
        "max_price_per_unit": 12.0,
    })

    # ดึงใบเสร็จเดิมอีกครั้ง ยอดเงินต้องคงเป็น 300.00 เท่าเดิม
    receipt_again = client.get(f"/api/v1/receipts/{order_id}").json()
    assert receipt_again["total_amount"] == 300.0
    cardboard_item = next(i for i in receipt_again["items"] if i["category_code"] == "MAT-CARDBOARD")
    assert cardboard_item["locked_unit_price"] == 3.5
    assert cardboard_item["settled_item_price"] == 210.0

    # คืนค่าราคา Benchmark เดิม ป้องกัน test state pollution ไปยัง suite อื่น
    supabase_store.upsert_benchmark_price({
        "category_code": "MAT-CARDBOARD",
        "category_name": "กระดาษลัง",
        "unit": "kg",
        "min_price_per_unit": 3.0,
        "max_price_per_unit": 4.0,
        "grading_condition": "แห้ง สะอาด ไม่เปียกน้ำ",
    })
