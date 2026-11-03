"""
Unit Tests for T-01: Payment & Settlement Data Models and Storage
รองรับ MD-DOM-04, REQ-FN-005, CC-04, P-03, P-05
"""

import pytest
from pydantic import ValidationError
from backend.app.models.payment_models import (
    ActualWeightItemInput,
    RecordWeighingRequest,
    WeightConfirmationRequest,
    WeightConfirmationResponse,
    DisputeRequest,
    PaymentConfirmationRequest,
    DigitalReceiptResponse,
    DigitalReceiptItem,
)
from backend.app.core.supabase import supabase_store


def test_actual_weight_item_validation():
    """ทดสอบ Validation ค่าน้ำหนักชั่งจริงต้องมากกว่า 0 (T-01, REQ-FN-004)"""
    # ผ่าน: น้ำหนัก 15.5 กก.
    valid_item = ActualWeightItemInput(item_id="itm-01", actual_quantity=15.5)
    assert valid_item.actual_quantity == 15.5

    # ตก: น้ำหนักเป็น 0 หรือติดลบ
    with pytest.raises(ValidationError):
        ActualWeightItemInput(item_id="itm-01", actual_quantity=0.0)

    with pytest.raises(ValidationError):
        ActualWeightItemInput(item_id="itm-01", actual_quantity=-2.5)


def test_record_weighing_request_validation():
    """ทดสอบ RecordWeighingRequest ต้องมีรูปตาชั่งและมีรายการอย่างน้อย 1 รายการ"""
    valid_req = RecordWeighingRequest(
        scale_photo_url="https://storage.saleng.app/scales/scale-001.jpg",
        items=[ActualWeightItemInput(item_id="itm-01", actual_quantity=20.0)],
    )
    assert len(valid_req.items) == 1
    assert "scales/scale-001.jpg" in valid_req.scale_photo_url

    # ตก: ไม่มีรายการ
    with pytest.raises(ValidationError):
        RecordWeighingRequest(scale_photo_url="https://scale.jpg", items=[])


def test_dispute_and_payment_method_validation():
    """ทดสอบ Dispute reason และ Payment method ต้องเป็น CASH หรือ PROMPTPAY (T-01, UC-07)"""
    # Dispute ต้องมีเหตุผลอย่างน้อย 5 ตัวอักษร
    valid_dispute = DisputeRequest(seller_id="usr-seller-01", dispute_reason="ตาชั่งไม่ได้มาตรฐาน น้ำหนักน้อยเกินจริง")
    assert valid_dispute.seller_id == "usr-seller-01"

    with pytest.raises(ValidationError):
        DisputeRequest(seller_id="usr-seller-01", dispute_reason="สั้น")

    # Payment Confirmation รับเฉพาะ CASH หรือ PROMPTPAY
    pay_cash = PaymentConfirmationRequest(seller_id="usr-seller-01", payment_method="CASH")
    assert pay_cash.payment_method == "CASH"

    pay_qr = PaymentConfirmationRequest(seller_id="usr-seller-01", payment_method="PROMPTPAY")
    assert pay_qr.payment_method == "PROMPTPAY"

    with pytest.raises(ValidationError):
        PaymentConfirmationRequest(seller_id="usr-seller-01", payment_method="CREDIT_CARD")


def test_digital_receipt_model_and_supabase_store():
    """ทดสอบการสร้างและบันทึก Digital Receipt ลงใน Supabase Store (T-01, REQ-FN-005, P-05)"""
    order_data = {
        "seller_id": "usr-seller-99",
        "pickup_location_id": "loc-99",
        "status": "S6",
        "total_est_min_price": 500.0,
        "total_est_max_price": 600.0,
        "total_settled_amount": 550.0,
    }
    items_data = [
        {
            "category_code": "MAT-CARDBOARD",
            "unit": "kg",
            "est_quantity": 100.0,
            "actual_quantity": 110.0,
            "est_min_price": 300.0,
            "est_max_price": 400.0,
            "locked_unit_price": 3.5,
            "settled_item_price": 385.0,
        }
    ]
    created_order = supabase_store.create_order(order_data, items_data)
    order_id = created_order["order_id"]

    # อัปเดตคำขอใน Store
    updated = supabase_store.update_order(order_id, {"status": "S7", "payment_method": "PROMPTPAY"})
    assert updated["status"] == "S7"
    assert updated["version"] == 2

    # สร้างและบันทึกใบเสร็จ
    receipt_dict = {
        "receipt_id": "rec-uuid-001",
        "receipt_no": "REC-20261103-0001",
        "order_id": order_id,
        "seller_id": "usr-seller-99",
        "buyer_id": "usr-buyer-01",
        "seller_phone_masked": "08X-XXX-1234",
        "buyer_phone_masked": "08X-XXX-5678",
        "total_amount": 385.0,
        "payment_method": "PROMPTPAY",
        "items": [
            {
                "category_code": "MAT-CARDBOARD",
                "category_name": "กระดาษลัง",
                "unit": "kg",
                "actual_quantity": 110.0,
                "locked_unit_price": 3.5,
                "settled_item_price": 385.0,
            }
        ],
    }

    saved_receipt = supabase_store.create_digital_receipt(receipt_dict)
    assert saved_receipt["receipt_no"] == "REC-20261103-0001"

    # ดึงใบเสร็จตาม order_id
    retrieved = supabase_store.get_receipt_by_order(order_id)
    assert retrieved is not None
    assert retrieved["receipt_no"] == "REC-20261103-0001"
    assert retrieved["total_amount"] == 385.0

    # ตรวจสอบ Pydantic Response Model
    receipt_obj = DigitalReceiptResponse(**retrieved)
    assert receipt_obj.seller_phone_masked == "08X-XXX-1234"
    assert receipt_obj.buyer_phone_masked == "08X-XXX-5678"
    assert len(receipt_obj.items) == 1

