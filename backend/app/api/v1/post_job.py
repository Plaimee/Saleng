"""
FastAPI Router for Buyer Post-Job Management System (ระบบหลังจบงานฝั่งซาเล้ง)
รองรับ UC-10, UC-13, REQ-FN-005, REQ-FN-006, REQ-SEC-001, REQ-SEC-002, CC-01, CC-04, CC-06, D-B07-01..06
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from backend.app.models.post_job_models import (
    PurchaseHistoryResponse,
    RegularCustomerItem,
    ToggleRegularCustomerRequest,
    ToggleRegularCustomerResponse,
    ReportSellerMismatchRequest,
    ReportSellerMismatchResponse,
)
from backend.app.services.post_job_service import post_job_service

router = APIRouter(prefix="/post-job", tags=["buyer-post-job"])


@router.get("/history", response_model=PurchaseHistoryResponse)
def get_purchase_history(
    saleng_id: str = Query(..., description="รหัสซาเล้งผู้เข้าใช้งาน"),
    period: str = Query("all", description="ช่วงเวลาตัวกรอง (all, today, month)"),
):
    """
    ดึงประวัติการรับซื้อของเก่าที่เสร็จสิ้นแล้ว (S7) พร้อมสรุปสถิติสะสม 3 มิติ (UC-10, REQ-FN-005, D-B07-05)
    """
    try:
        return post_job_service.get_purchase_history(saleng_id, period)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/regular-customers", response_model=List[RegularCustomerItem])
def get_regular_customers(
    saleng_id: str = Query(..., description="รหัสซาเล้งผู้เข้าใช้งาน"),
):
    """
    ดึงรายชื่อลูกค้าประจำที่ซาเล้งปักหมุดไว้ พร้อมพิกัดและบันทึกย่อ (UC-10, AC-B07-02, D-B07-03)
    """
    try:
        return post_job_service.get_regular_customers(saleng_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/regular-customers", response_model=ToggleRegularCustomerResponse)
def toggle_regular_customer(
    request: ToggleRegularCustomerRequest,
):
    """
    สลับสถานะ (Toggle Bookmark) ปักหมุดหรือยกเลิกผู้ขายเป็นลูกค้าประจำ (AC-B07-02, REQ-SEC-001)
    """
    try:
        return post_job_service.toggle_regular_customer(request.saleng_id, request)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/report-mismatch", response_model=ReportSellerMismatchResponse)
def report_seller_mismatch(
    request: ReportSellerMismatchRequest,
):
    """
    รายงานข้อพิพาทหน้างานกรณี No-show หรือของไม่ตรงสเปก (S3/S4 -> S8: Disputed)
    รองรับ UC-13, REQ-FN-006, REQ-SEC-001, AC-B07-03, D-B07-01, D-B07-02
    """
    try:
        return post_job_service.report_seller_mismatch(request.order_id, request)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

