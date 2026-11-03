"""
Automated Tests for AC-S06-03 (Payment Confirmation) & AC-S06-04 (Digital Receipt & PII Masking)
รองรับ UC-07, REQ-FN-005, REQ-SEC-001, REQ-SEC-002, AC-S06-03, AC-S06-04, P-04, P-05, Q-03, Q-04
"""

import re
import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store
from backend.app.services.payment_service import mask_phone

client = TestClient(app)


def _create_s6_order(seller_id: str, status: str = "S6") -> str:
    order_data = {
        "seller_id": seller_id,
        "buyer_id": "usr-saleng-pay",
        "seller_phone": "0812345678",
        "buyer_phone": "0898765432",
        "status": status,
        "total_settled_amount": 300.0,
    }
    items_data = [
        {
            "category_code": "MAT-CARDBOARD",
            "unit": "kg",
            "est_quantity": 50.0,
            "actual_quantity": 60.0,
            "locked_unit_price": 3.5,
            "settled_item_price": 210.0,
        },
        {
            "category_code": "MAT-GLASS-BOTTLE-BAG",
            "unit": "bag",
            "est_quantity": 2.0,
            "actual_quantity": 2.0,
            "locked_unit_price": 45.0,
            "settled_item_price": 90.0,
        },
    ]
    return supabase_store.create_order(order_data, items_data)["order_id"]


@pytest.mark.parametrize("method", ["CASH", "PROMPTPAY"])
def test_AC_S06_03_seller_confirms_payment(method):
    """AC-S06-03: ผู้ขายเลือกเงินสด/PromptPay และกดยืนยันรับเงิน -> S7 (Completed)"""
    seller_id = f"usr-seller-pay-{method.lower()}"
    order_id = _create_s6_order(seller_id)

    resp = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": seller_id, "payment_method": method},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "S7"
    assert data["payment_method"] == method
    assert data["total_amount"] == 300.0
    assert re.fullmatch(r"REC-\d{8}-\d{4}", data["receipt_no"])

    order = supabase_store.get_order(order_id)
    assert order["status"] == "S7"
    assert order["payment_method"] == method

    logs = [l for l in supabase_store.audit_logs if l["entity_id"] == order_id and l["action"] == "SELLER_PAYMENT_CONFIRMED"]
    assert len(logs) == 1
    assert logs[0]["details"]["new_status"] == "S7"


def test_AC_S06_03_block_non_seller():
    """AC-S06-03 / Q-03: ซาเล้งหรือบุคคลอื่นยืนยันรับเงินแทนผู้ขายไม่ได้ (HTTP 403)"""
    order_id = _create_s6_order("usr-seller-owner-pay")
    resp = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": "usr-saleng-pay", "payment_method": "CASH"},
    )
    assert resp.status_code == 403
    assert supabase_store.get_order(order_id)["status"] == "S6"


@pytest.mark.parametrize("status", ["S5", "S8"])
def test_AC_S06_03_block_when_not_s6(status):
    """AC-S06-03: บล็อกการยืนยันรับเงินหากยังไม่ผ่านการยืนยันน้ำหนัก (S5) หรืออยู่ระหว่างข้อพิพาท (S8)"""
    seller_id = f"usr-seller-block-{status}"
    order_id = _create_s6_order(seller_id, status=status)
    resp = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": seller_id, "payment_method": "CASH"},
    )
    assert resp.status_code == 400
    assert supabase_store.get_receipt_by_order(order_id) is None


def test_AC_S06_03_block_double_confirmation():
    """AC-S06-03: ยืนยันรับเงินซ้ำไม่ได้หลังปิดงาน (ป้องกันใบเสร็จซ้ำ)"""
    seller_id = "usr-seller-double"
    order_id = _create_s6_order(seller_id)
    payload = {"seller_id": seller_id, "payment_method": "CASH"}
    assert client.post(f"/api/v1/orders/{order_id}/confirm-payment", json=payload).status_code == 200
    second = client.post(f"/api/v1/orders/{order_id}/confirm-payment", json=payload)
    assert second.status_code == 400
    assert len([r for r in supabase_store.receipts.values() if r["order_id"] == order_id]) == 1


def test_AC_S06_04_digital_receipt_content_and_masking():
    """AC-S06-04: ใบเสร็จดิจิทัลมีรหัสไม่ซ้ำ รายการ น้ำหนักจริง ราคาล็อก ยอดสุทธิ วิธีชำระ และปกปิดเบอร์โทร"""
    seller_id = "usr-seller-receipt"
    order_id = _create_s6_order(seller_id)
    client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": seller_id, "payment_method": "PROMPTPAY"},
    )

    resp = client.get(f"/api/v1/receipts/{order_id}")
    assert resp.status_code == 200
    r = resp.json()

    assert re.fullmatch(r"REC-\d{8}-\d{4}", r["receipt_no"])
    assert r["order_id"] == order_id
    assert r["payment_method"] == "PROMPTPAY"
    assert r["total_amount"] == 300.0
    assert r["issued_at"]

    # REQ-SEC-002: ปกปิดเบอร์โทร และต้องไม่มีเบอร์เต็มหลุดในใบเสร็จ
    assert r["seller_phone_masked"] == "08X-XXX-5678"
    assert r["buyer_phone_masked"] == "08X-XXX-5432"
    assert "0812345678" not in resp.text
    assert "0898765432" not in resp.text

    cardboard = next(i for i in r["items"] if i["category_code"] == "MAT-CARDBOARD")
    assert cardboard["actual_quantity"] == 60.0
    assert cardboard["locked_unit_price"] == 3.5
    assert cardboard["settled_item_price"] == 210.0


def test_AC_S06_04_receipt_numbers_unique():
    """AC-S06-04: รหัสใบเสร็จต้องไม่ซ้ำกัน"""
    numbers = set()
    for i in range(3):
        seller_id = f"usr-seller-uniq-{i}"
        order_id = _create_s6_order(seller_id)
        data = client.post(
            f"/api/v1/orders/{order_id}/confirm-payment",
            json={"seller_id": seller_id, "payment_method": "CASH"},
        ).json()
        numbers.add(data["receipt_no"])
    assert len(numbers) == 3


def test_AC_S06_04_receipt_not_found():
    """AC-S06-04: ใบงานที่ยังไม่ปิดงานต้องไม่มีใบเสร็จ (HTTP 404)"""
    order_id = _create_s6_order("usr-seller-noreceipt")
    assert client.get(f"/api/v1/receipts/{order_id}").status_code == 404


def test_AC_S06_04_mask_phone_helper():
    """REQ-SEC-002: ฟังก์ชันปกปิดเบอร์โทรรองรับรูปแบบต่าง ๆ และไม่เดาค่าเมื่อไม่มีข้อมูล"""
    assert mask_phone("0812345678") == "08X-XXX-5678"
    assert mask_phone("081-234-5678") == "08X-XXX-5678"
    assert mask_phone(None) == "XXX-XXX-XXXX"
    assert mask_phone("123") == "XXX-XXX-XXXX"

