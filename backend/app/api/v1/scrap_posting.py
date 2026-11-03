"""
FastAPI Router สำหรับระบบโพสต์ขายของเก่าของผู้ขาย (Scrap Posting API)
รองรับ UC-02, REQ-UX-002, REQ-FN-003, REQ-FN-004, Card 03, CC-01, CC-04, P-01..P-06
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from backend.app.models.scrap_posting_models import (
    CategoryCatalogResponse,
    DraftOrderCreateRequest,
    DraftOrderResponse,
    WasteItemCreateRequest,
    WasteItemResponse,
    LiftingHelpUpdateRequest,
)
from backend.app.services.scrap_posting_service import ScrapPostingService

scrap_posting_router = APIRouter(prefix="/scrap-posting", tags=["Scrap Posting"])


class PhotoAttachRequest(BaseModel):
    photo_url: str = Field(..., min_length=1, description="URL หรือ Base64 ของรูปถ่าย")


@scrap_posting_router.get(
    "/categories",
    response_model=CategoryCatalogResponse,
    summary="ดึงรายการหมวดหมู่และคู่มือภาพทั้งหมด (AC-S02-01, P-01)",
)
def get_categories():
    return ScrapPostingService.get_categories()


@scrap_posting_router.post(
    "/drafts",
    response_model=DraftOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="สร้างคำขอโพสต์ขายของเก่าฉบับร่าง S1 Draft (P-06)",
)
def create_draft(req: DraftOrderCreateRequest):
    return ScrapPostingService.create_draft_order(req)


@scrap_posting_router.get(
    "/drafts/{order_id}",
    response_model=DraftOrderResponse,
    summary="ดึงข้อมูลคำขอฉบับร่างและรายการของเก่า (AC-S02-01)",
)
def get_draft(order_id: str):
    return ScrapPostingService.get_draft_order(order_id)


@scrap_posting_router.post(
    "/drafts/{order_id}/items",
    response_model=WasteItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="เพิ่มรายการของเก่าลงในฉบับร่าง พร้อม Bulky Guard (AC-S02-01..03, Card 03)",
)
def add_item_to_draft(order_id: str, req: WasteItemCreateRequest):
    return ScrapPostingService.add_item_to_draft(order_id, req)


@scrap_posting_router.delete(
    "/drafts/{order_id}/items/{item_id}",
    summary="ลบรายการของเก่าออกจากฉบับร่าง",
)
def delete_item_from_draft(order_id: str, item_id: str):
    return ScrapPostingService.delete_item_from_draft(order_id, item_id)


@scrap_posting_router.post(
    "/drafts/{order_id}/items/{item_id}/photos",
    response_model=WasteItemResponse,
    summary="แนบรูปถ่ายของเก่าประกอบรายการ สูงสุด 5 รูป (AC-S02-04, P-04)",
)
def attach_photo(order_id: str, item_id: str, req: PhotoAttachRequest):
    return ScrapPostingService.attach_photo_to_item(order_id, item_id, req.photo_url)


@scrap_posting_router.delete(
    "/drafts/{order_id}/items/{item_id}/photos/{photo_idx}",
    response_model=WasteItemResponse,
    summary="ลบรูปถ่ายของเก่าออกจากรายการ (AC-S02-04)",
)
def delete_photo(order_id: str, item_id: str, photo_idx: int):
    return ScrapPostingService.delete_photo_from_item(order_id, item_id, photo_idx)


@scrap_posting_router.patch(
    "/drafts/{order_id}/lifting-help",
    response_model=DraftOrderResponse,
    summary="ปรับปรุงบริการเสริมขอคนช่วยยกของหนักและหมายเหตุ (AC-S02-05, P-05)",
)
def update_lifting_help(order_id: str, req: LiftingHelpUpdateRequest):
    return ScrapPostingService.update_lifting_help(order_id, req)

