"""
Unit Tests for Task T-01: Billing Models and Supabase Store Extensions
รองรับ UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-002
"""

import pytest
from pydantic import ValidationError
from backend.app.models.billing_models import (
    WeighingItemInput,
    SubmitWeighingRequest,
    WeighingSheetItem,
    WeighingSheetResponse,
    WeighingResultResponse,
    SelectPaymentMethodRequest,
    PaymentMethodSelectionResponse,
    DigitalReceiptItem,
    DigitalReceiptSummaryResponse,
)
from backend.app.core.supabase import supabase_store


def test_weighing_item_input_validation():
    """น้ำหนักชั่งจริงต้องมากกว่า 0 เท่านั้น"""
    valid = WeighingItemInput(item_id="item-1", actual_quantity=15.5)
    assert valid.item_id == "item-1"
    assert valid.actual_quantity == 15.5

    # Test invalid: actual_quantity <= 0
    with pytest.raises(ValidationError):
        WeighingItemInput(item_id="item-1", actual_quantity=0)

    with pytest.raises(ValidationError):
        WeighingItemInput(item_id="item-1", actual_quantity=-2.5)


def test_submit_weighing_request_validation():
    """คำขอบันทึกผลชั่งจริงต้องมี scale_photo_url และ items อย่างน้อย 1 รายการ"""
    valid = SubmitWeighingRequest(
        saleng_id="saleng-01",
        scale_photo_url="https://example.com/scale1.jpg",
        items=[WeighingItemInput(item_id="item-1", actual_quantity=10.0)],
        idempotency_key="idemp-12345"
    )
    assert valid.saleng_id == "saleng-01"
    assert valid.scale_photo_url == "https://example.com/scale1.jpg"
    assert len(valid.items) == 1

    # Empty photo URL
    with pytest.raises(ValidationError):
        SubmitWeighingRequest(
            saleng_id="saleng-01",
            scale_photo_url="",
            items=[WeighingItemInput(item_id="item-1", actual_quantity=10.0)]
        )

    # Empty items list
    with pytest.raises(ValidationError):
        SubmitWeighingRequest(
            saleng_id="saleng-01",
            scale_photo_url="https://example.com/scale1.jpg",
            items=[]
        )


def test_select_payment_method_request():
    """ทดสอบ SelectPaymentMethodRequest"""
    req = SelectPaymentMethodRequest(saleng_id="saleng-01", payment_method="CASH")
    assert req.saleng_id == "saleng-01"
    assert req.payment_method == "CASH"

    with pytest.raises(ValidationError):
        SelectPaymentMethodRequest(saleng_id="", payment_method="CASH")


def test_digital_receipt_summary_response():
    """ทดสอบโครงสร้างข้อมูลใบเสร็จดิจิทัล DigitalReceiptSummaryResponse"""
    receipt = DigitalReceiptSummaryResponse(
        receipt_id="REC-20261104-0001",
        order_id="order-01",
        issued_at="2026-11-04T10:00:00Z",
        seller_name="สมศรี มีสุข",
        seller_phone_masked="08X-XXX-4567",
        collector_name="สมชาย ซาเล้ง",
        collector_phone_masked="08X-XXX-8901",
        payment_method="PROMPTPAY",
        total_settled_amount=350.0,
        items=[
            DigitalReceiptItem(
                category_name="กระดาษลัง",
                actual_quantity=50.0,
                unit="กก.",
                locked_unit_price=4.0,
                settled_item_price=200.0
            ),
            DigitalReceiptItem(
                category_name="ขวดแก้วใส",
                actual_quantity=50.0,
                unit="กก.",
                locked_unit_price=3.0,
                settled_item_price=150.0
            )
        ]
    )
    assert receipt.receipt_id == "REC-20261104-0001"
    assert receipt.total_settled_amount == 350.0
    assert len(receipt.items) == 2


def test_supabase_store_billing_methods():
    """ทดสอบฟังก์ชัน get_order_weighing_sheet และ update_order_payment_method ใน SupabaseStore"""
    # Seed mock order
    order_id = "test-order-b06-t01"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "saleng_id": "saleng-01",
        "seller_name": "ยายแก้ว",
        "seller_phone": "0812345678",
        "status": "S4",
        "seller_confirmed_weight": False,
        "items": [
            {
                "item_id": "item-1",
                "category_code": "PAPER_BOX",
                "category_name": "กระดาษลัง",
                "estimated_quantity": 20.0,
                "locked_unit_price": 4.5,
                "unit": "กก."
            }
        ]
    }

    sheet = supabase_store.get_order_weighing_sheet(order_id)
    assert sheet is not None
    assert sheet["order_id"] == order_id
    assert sheet["seller_name"] == "ยายแก้ว"
    assert sheet["seller_phone_masked"] == "08X-XXX-5678"
    assert len(sheet["items"]) == 1
    assert sheet["items"][0]["locked_unit_price"] == 4.5

    updated = supabase_store.update_order_payment_method(order_id, "PROMPTPAY")
    assert updated["payment_method"] == "PROMPTPAY"

    # Cleanup
    if order_id in supabase_store.orders:
        del supabase_store.orders[order_id]

