"""
FastAPI Router for Buyer Billing & Receipt System (ระบบคิดเงินและออกใบเสร็จฝั่งซาเล้ง)
รองรับ UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B06-01..06
"""

from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.billing_models import (
    SubmitWeighingRequest,
    WeighingSheetResponse,
    WeighingResultResponse,
    SelectPaymentMethodRequest,
    PaymentMethodSelectionResponse,
    DigitalReceiptSummaryResponse,
)
from backend.app.services.billing_service import billing_service

router = APIRouter(prefix="/billing", tags=["buyer-billing"])


@router.get("/{order_id}/weighing-sheet", response_model=WeighingSheetResponse)
def get_weighing_sheet(
    order_id: str,
    saleng_id: str = Query(..., description="รหัสซาเล้งผู้เข้าใช้งาน"),
):
    """
    ดึงข้อมูลใบชั่งน้ำหนักหน้างานและราคาต่อหน่วยที่ล็อกไว้ (UC-05, REQ-FN-002, REQ-BR-002)
    """
    try:
        return billing_service.get_weighing_sheet(order_id, saleng_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/weighing", response_model=WeighingResultResponse)
def submit_weighing(
    order_id: str,
    request: SubmitWeighingRequest,
):
    """
    บันทึกผลชั่งจริงหน้างานโดยซาเล้ง พร้อมภาพถ่ายตาชั่ง (REQ-FN-002, D-B06-02, D-B06-03)
    คำนวณยอดเงินสุทธิด้วยราคาล็อก (REQ-BR-002) และตรวจสอบเกณฑ์ ±15% (MD-STM-04)
    """
    try:
        return billing_service.submit_weighing(order_id, request)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/payment-method", response_model=PaymentMethodSelectionResponse)
def select_payment_method(
    order_id: str,
    request: SelectPaymentMethodRequest,
):
    """
    เลือกช่องทางการชำระเงินหน้างาน (CASH หรือ PROMPTPAY)
    100% Confirmation Gate: บล็อกจนกว่าผู้ขายจะกดยืนยันน้ำหนัก (REQ-FN-004, AC-B06-03, D-B06-01, D-B06-04)
    """
    try:
        return billing_service.select_payment_method(order_id, request)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{order_id}/receipt", response_model=DigitalReceiptSummaryResponse)
def get_receipt(
    order_id: str,
    saleng_id: str = Query(..., description="รหัสซาเล้งผู้เข้าใช้งาน"),
):
    """
    ดึงข้อมูลใบเสร็จสรุปรายการดิจิทัลเมื่อจบงาน (S7) พร้อม Mask เบอร์โทรศัพท์ (REQ-FN-005, REQ-SEC-002, CC-06)
    """
    try:
        return billing_service.get_receipt(order_id, saleng_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

