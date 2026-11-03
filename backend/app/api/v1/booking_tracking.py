"""
FastAPI Router สำหรับระบบนัดหมายและติดตามสถานะ (Booking & Status Tracking Endpoints)
รองรับ UC-04, MD-STM-04, BR-03, REQ-FN-003, REQ-SEC-001, AC-S05-01..05
"""

from fastapi import APIRouter, Query, status
from backend.app.models.booking_tracking_models import (
    BookingSlotRequest,
    OrderCancellationRequest,
    OrderTrackingResponse,
    SimulateStatusRequest,
)
from backend.app.services.booking_tracking_service import BookingTrackingService

router = APIRouter(prefix="/booking-tracking", tags=["Booking & Status Tracking"])


@router.post(
    "/orders/{order_id}/book",
    response_model=OrderTrackingResponse,
    summary="เลือกช่วงเวลานัดหมายและยืนยันส่งคำขอ S1 -> S2 (AC-S05-01)",
)
def book_order_slot(
    order_id: str,
    req: BookingSlotRequest,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    เลือกสล็อตเวลานัดหมาย (เรียกทันที หรือนัดหมายล่วงหน้า) และเปลี่ยนสถานะคำขอสู่ S2
    """
    return BookingTrackingService.book_order_slot(
        order_id=order_id, req=req, seller_id=seller_id
    )


@router.get(
    "/orders/{order_id}/status",
    response_model=OrderTrackingResponse,
    summary="ดึงสถานะคำขอ Stepper Timeline และ ETA (AC-S05-02, AC-S05-04)",
)
def get_order_status(
    order_id: str,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    ดึงสถานะความคืบหน้าของคำขอ พร้อมสิทธิ์การยกเลิกตามกฎ BR-03
    """
    return BookingTrackingService.get_order_status(order_id=order_id, seller_id=seller_id)


@router.post(
    "/orders/{order_id}/cancel",
    response_model=OrderTrackingResponse,
    summary="ยกเลิกนัดหมายพร้อมบังคับใช้กฎเหล็ก BR-03 (AC-S05-03)",
)
def cancel_order(
    order_id: str,
    req: OrderCancellationRequest,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    ยกเลิกนัดหมายในสถานะ S1..S3 และบล็อกห้ามยกเลิกเมื่อเข้าสู่ S4 In-Transit
    """
    return BookingTrackingService.cancel_order(
        order_id=order_id, req=req, seller_id=seller_id
    )


@router.patch(
    "/orders/{order_id}/simulate-status",
    response_model=OrderTrackingResponse,
    summary="จำลองการเปลี่ยนสถานะสำหรับชุดทดสอบ (S2->S3->S4->S5)",
)
def simulate_status_change(
    order_id: str,
    req: SimulateStatusRequest,
    seller_id: str = Query("seller-01", description="รหัสผู้ขาย"),
):
    """
    จำลองการอัปเดตสถานะใบงานสำหรับทดสอบ Stepper และกฎ BR-03
    """
    return BookingTrackingService.simulate_status_change(
        order_id=order_id, req=req, seller_id=seller_id
    )

