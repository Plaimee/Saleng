"""
API Endpoints สำหรับระบบหลังทำธุรกรรม (Post-Transaction API)
รองรับ UC-10, SC-05, REQ-FN-005, REQ-SEC-001, REQ-SEC-002, AC-S07-01..05, P-01..P-05
"""

from typing import List
from fastapi import APIRouter, status
from backend.app.models.post_transaction_models import (
    ReviewCreateRequest,
    ReviewResponse,
    FavoriteCollectorResponse,
    SalesHistoryResponse,
)
from backend.app.services.post_transaction_service import PostTransactionService

post_transaction_router = APIRouter(prefix="/api/v1", tags=["post-transaction"])


@post_transaction_router.post(
    "/orders/{order_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ส่งคะแนนและรีวิวบริการซาเล้ง (AC-S07-01, UC-10, Q-01, Q-02)"
)
def submit_order_review(order_id: str, payload: ReviewCreateRequest):
    """
    ผู้ขายให้คะแนนดาว 1-5 ดาว และเขียนรีวิวซาเล้งหลังจบงาน (สถานะ S7)
    จำกัด 1 รีวิว ต่อ 1 คำขอ
    """
    return PostTransactionService.submit_review(
        order_id=order_id,
        seller_id=payload.seller_id,
        rating=payload.rating,
        comment=payload.comment,
    )


@post_transaction_router.get(
    "/orders/{order_id}/review",
    response_model=ReviewResponse,
    summary="ดึงข้อมูลรีวิวของคำขอ (AC-S07-01, UC-10)"
)
def get_order_review(order_id: str):
    """ดึงข้อมูลรีวิวของคำขอที่ระบุ"""
    return PostTransactionService.get_review(order_id=order_id)


@post_transaction_router.post(
    "/sellers/{seller_id}/favorites/{collector_id}",
    response_model=FavoriteCollectorResponse,
    summary="สลับสถานะ (Toggle) บันทึก/ยกเลิกผู้รับซื้อประจำ (AC-S07-02, UC-10, Q-03)"
)
def toggle_favorite_collector(seller_id: str, collector_id: str):
    """
    ผู้ขายบันทึกหรือยกเลิกซาเล้งเป็นผู้รับซื้อประจำ (Toggle Bookmark)
    """
    return PostTransactionService.toggle_favorite(
        seller_id=seller_id,
        collector_id=collector_id,
    )


@post_transaction_router.delete(
    "/sellers/{seller_id}/favorites/{collector_id}",
    response_model=FavoriteCollectorResponse,
    summary="ยกเลิกผู้รับซื้อประจำ (AC-S07-02, UC-10)"
)
def remove_favorite_collector(seller_id: str, collector_id: str):
    """ยกเลิกซาเล้งออกจากรายการผู้รับซื้อประจำ"""
    # ถ้าเป็น favorite อยู่ ให้ toggle เพื่อยกเลิก
    return PostTransactionService.toggle_favorite(
        seller_id=seller_id,
        collector_id=collector_id,
    )


@post_transaction_router.get(
    "/sellers/{seller_id}/favorites",
    response_model=List[str],
    summary="ดึงรายชื่อรหัสซาเล้งที่เป็นผู้รับซื้อประจำ (AC-S07-02, UC-10)"
)
def get_favorite_collectors(seller_id: str):
    """ดึงรายชื่อรหัสซาเล้งที่เป็นผู้รับซื้อประจำของผู้ขายรายนี้"""
    return PostTransactionService.get_favorites(seller_id=seller_id)


@post_transaction_router.get(
    "/sellers/{seller_id}/sales-history",
    response_model=SalesHistoryResponse,
    summary="ดึงประวัติการขาย สรุปสถิติสะสม และ PII Masking (AC-S07-03, REQ-FN-005, REQ-SEC-002, Q-04)"
)
def get_sales_history(seller_id: str):
    """
    ดึงสรุปประวัติการขายที่ปิดงานสำเร็จ (S7) พร้อมยอดเงินสะสม น้ำหนักสะสม และรายการคำขอที่มี PII Masking
    """
    return PostTransactionService.get_sales_history(seller_id=seller_id)

