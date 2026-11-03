"""
Payment & Verification API Endpoints
รองรับ REQ-FN-004, REQ-FN-005, REQ-FN-006, REQ-BR-002, AC-S06-01..05
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.payment_models import (
    RecordWeighingRequest,
    WeighingRecordResponse,
    WeightConfirmationRequest,
    WeightConfirmationResponse,
    RequestReweighRequest,
    RequestReweighResponse,
    DisputeRequest,
    DisputeResponse,
    PaymentConfirmationRequest,
    PaymentConfirmationResponse,
    DigitalReceiptResponse,
)
from backend.app.services.payment_service import payment_service

payment_router = APIRouter(prefix="/api/v1/orders", tags=["payment"])


@payment_router.post("/{order_id}/record-weighing", response_model=WeighingRecordResponse)
def record_weighing(order_id: str, request: RecordWeighingRequest):
    """
    บันทึกผลชั่งจริงหน้างานโดยซาเล้ง (S4 -> S5)
    รองรับ REQ-FN-004, REQ-BR-002, P-03
    """
    try:
        return payment_service.record_weighing(order_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@payment_router.post("/{order_id}/confirm-weights", response_model=WeightConfirmationResponse)
def confirm_weights(order_id: str, request: WeightConfirmationRequest):
    """
    ผู้ขายตรวจสอบและกดยืนยันตัวเลขน้ำหนักชั่งจริง (100% Confirmation Gate: S5 -> S6)
    รองรับ REQ-FN-004, REQ-SEC-001, AC-S06-01, P-01, Q-01
    """
    try:
        return payment_service.confirm_weights(order_id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@payment_router.post("/{order_id}/request-reweigh", response_model=RequestReweighResponse)
def request_reweigh(order_id: str, request: RequestReweighRequest):
    """
    ผู้ขายส่งคำขอให้ซาเล้งตรวจสอบตาชั่งและชั่งน้ำหนักซ้ำ
    รองรับ AC-S06-02, Q-02
    """
    try:
        return payment_service.request_reweigh(order_id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@payment_router.post("/{order_id}/dispute", response_model=DisputeResponse)
def raise_dispute(order_id: str, request: DisputeRequest):
    """
    ผู้ขายปฏิเสธผลชั่งและแจ้งข้อพิพาท (S8: Disputed)
    พร้อมล็อกหลักฐานภาพตาชั่งและพิกัด GPS ส่งต่อให้ Admin ตรวจสอบ
    รองรับ REQ-FN-006, REQ-SEC-001, AC-S06-02, P-02, Q-02
    """
    try:
        return payment_service.raise_dispute(order_id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@payment_router.post("/{order_id}/confirm-payment", response_model=PaymentConfirmationResponse)
def confirm_payment(order_id: str, request: PaymentConfirmationRequest):
    """
    ผู้ขายกดยืนยันรับเงิน (เงินสด / PromptPay) บนหน้าจอของตนเอง (S6 -> S7) และออกใบเสร็จดิจิทัล
    รองรับ UC-07, REQ-FN-005, REQ-SEC-001, AC-S06-03, P-04, Q-03
    """
    try:
        return payment_service.confirm_payment(order_id, request)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


receipt_router = APIRouter(prefix="/api/v1/receipts", tags=["receipts"])


@receipt_router.get("/{order_id}", response_model=DigitalReceiptResponse)
def get_receipt(order_id: str):
    """
    ดึงใบเสร็จดิจิทัลของคำขอ พร้อมเบอร์โทรที่ปกปิดแล้ว (08X-XXX-XXXX)
    รองรับ REQ-FN-005, REQ-SEC-002, AC-S06-04, P-05, Q-04
    """
    try:
        return payment_service.get_receipt(order_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
