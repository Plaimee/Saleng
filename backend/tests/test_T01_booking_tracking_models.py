"""
Unit tests สำหรับ T-01: Data Models ของระบบนัดหมายและติดตามสถานะ
รองรับ UC-04, MD-STM-04, BR-03, REQ-DAT-001, CC-04, P-01
"""

import pytest
from backend.app.models.booking_tracking_models import (
    BookingSlotRequest,
    OrderCancellationRequest,
    OrderTrackingResponse,
    SimulateStatusRequest,
)


def test_T01_booking_slot_request_model():
    """ทดสอบ Schema และ Validation ของ BookingSlotRequest"""
    # แบบเรียกทันที
    req_immediate = BookingSlotRequest(booking_type="IMMEDIATE")
    assert req_immediate.booking_type == "IMMEDIATE"
    assert req_immediate.scheduled_date is None

    # แบบนัดล่วงหน้า
    req_scheduled = BookingSlotRequest(
        booking_type="SCHEDULED",
        scheduled_date="2026-11-10",
        scheduled_slot="MORNING_09_12",
        notes="กรุณากดกริ่งหน้าบ้าน",
    )
    assert req_scheduled.booking_type == "SCHEDULED"
    assert req_scheduled.scheduled_date == "2026-11-10"
    assert req_scheduled.scheduled_slot == "MORNING_09_12"
    assert req_scheduled.notes == "กรุณากดกริ่งหน้าบ้าน"


def test_T01_order_cancellation_request_model():
    """ทดสอบ OrderCancellationRequest"""
    req = OrderCancellationRequest(reason="เปลี่ยนใจ ไม่สะดวกส่งมอบวันนี้")
    assert req.reason == "เปลี่ยนใจ ไม่สะดวกส่งมอบวันนี้"

    with pytest.raises(Exception):
        OrderCancellationRequest(reason="ก")  # min_length = 2


def test_T01_order_tracking_response_model():
    """ทดสอบ OrderTrackingResponse และฟิลด์ can_cancel ตามกฎ BR-03"""
    resp_s3 = OrderTrackingResponse(
        order_id="order-01",
        seller_id="seller-01",
        status="S3",
        status_label="มีผู้รับงานแล้ว",
        stepper_step=2,
        can_cancel=True,
        updated_at="2026-11-04T12:00:00Z",
    )
    assert resp_s3.can_cancel is True
    assert resp_s3.stepper_step == 2

    resp_s4 = OrderTrackingResponse(
        order_id="order-01",
        seller_id="seller-01",
        status="S4",
        status_label="กำลังเดินทาง",
        stepper_step=3,
        can_cancel=False,  # BR-03: ล็อกปุ่มยกเลิก
        eta_minutes=8,
        distance_km=1.4,
        updated_at="2026-11-04T12:05:00Z",
    )
    assert resp_s4.can_cancel is False
    assert resp_s4.eta_minutes == 8
    assert resp_s4.distance_km == 1.4

