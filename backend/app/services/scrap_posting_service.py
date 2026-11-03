"""
Service Layer สำหรับระบบโพสต์ขายของเก่าของผู้ขาย (Scrap Posting Service)
รองรับ UC-02, REQ-UX-002, REQ-FN-003, REQ-FN-004, REQ-DAT-001, REQ-SEC-001, Card 03, MD-DOM-04, P-01..P-06
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict
import uuid
from fastapi import HTTPException, status

from backend.app.core.supabase import supabase_store
from backend.app.models.scrap_posting_models import (
    ScrapCategoryResponse,
    CategoryCatalogResponse,
    WasteItemCreateRequest,
    WasteItemResponse,
    LiftingHelpUpdateRequest,
    DraftOrderCreateRequest,
    DraftOrderResponse,
)

# ตารางราคารายการของชิ้นใหญ่เหมาจ่ายตาม Card 03 (หน้า 62)
BULKY_PRICE_MAP = {
    "ตู้เย็น": (200.0, 300.0),
    "เครื่องซักผ้า": (150.0, 250.0),
    "แอร์/คอมเพรสเซอร์": (300.0, 500.0),
    "โซฟา/เฟอร์นิเจอร์": (100.0, 200.0),
}


class ScrapPostingService:
    """
    บริการจัดการคู่มือภาพและสร้างคำขอโพสต์ขายของเก่าในสถานะ S1 Draft (UC-02)
    """

    @staticmethod
    def get_categories() -> CategoryCatalogResponse:
        """
        ดึงรายการหมวดหมู่และคู่มือภาพทั้งหมด (AC-S02-01, P-01)
        """
        cats = supabase_store.get_scrap_categories()
        items = [
            ScrapCategoryResponse(
                category_code=c["category_code"],
                category_group=c["category_group"],
                name=c["name"],
                icon=c["icon"],
                unit=c["unit"],
                min_price_per_unit=c["min_price_per_unit"],
                max_price_per_unit=c["max_price_per_unit"],
                sub_categories=c.get("sub_categories"),
            )
            for c in cats
        ]
        return CategoryCatalogResponse(categories=items)

    @staticmethod
    def create_draft_order(req: DraftOrderCreateRequest) -> DraftOrderResponse:
        """
        สร้างคำขอโพสต์ขายของเก่าฉบับร่าง (S1 Draft, P-06)
        ผูกกับที่อยู่นัดหมายเริ่มต้นจาก UC-01
        """
        seller = supabase_store.get_seller(req.seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบบัญชีผู้ขายรหัส {req.seller_id}",
            )

        loc_id = req.pickup_location_id
        if not loc_id:
            default_loc = supabase_store.get_default_pickup_location(req.seller_id)
            if not default_loc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ผู้ขายต้องระบุที่อยู่นัดหมายก่อนสร้างคำขอโพสต์ขายของเก่า (กรุณาเพิ่มที่อยู่ในระบบบัญชี)",
                )
            loc_id = default_loc["location_id"]

        order_data = {
            "seller_id": req.seller_id,
            "pickup_location_id": loc_id,
            "status": "S1",
            "need_lifting_help": False,
            "lifting_help_notes": None,
            "total_est_min_price": 0.0,
            "total_est_max_price": 0.0,
        }
        order = supabase_store.create_order(order_data, [])

        supabase_store.add_audit_log(
            action="DRAFT_ORDER_CREATED",
            entity_id=order["order_id"],
            actor_id=req.seller_id,
            details={"pickup_location_id": loc_id},
        )

        loc = supabase_store.get_pickup_location(loc_id)
        return DraftOrderResponse(
            order_id=order["order_id"],
            seller_id=order["seller_id"],
            pickup_location_id=loc_id,
            pickup_location=loc,
            status=order["status"],
            need_lifting_help=order["need_lifting_help"],
            lifting_help_notes=order["lifting_help_notes"],
            total_est_min_price=order["total_est_min_price"],
            total_est_max_price=order["total_est_max_price"],
            items=[],
            created_at=order["created_at"],
            updated_at=order["created_at"],
        )

    @staticmethod
    def get_draft_order(order_id: str) -> DraftOrderResponse:
        """
        ดึงข้อมูลคำขอฉบับร่างพร้อมรายการของเก่าในตะกร้า (AC-S02-01)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส {order_id}",
            )

        items = [
            WasteItemResponse(
                item_id=i["item_id"],
                order_id=i["order_id"],
                category_code=i["category_code"],
                category_name=i.get("category_name", ""),
                category_group=i.get("category_group", "GENERAL_WEIGHT"),
                sub_category=i.get("sub_category"),
                quantity=i["quantity"],
                unit=i.get("unit", "kg"),
                est_min_price=i["est_min_price"],
                est_max_price=i["est_max_price"],
                photo_urls=i.get("photo_urls", []),
            )
            for i in order.get("items", [])
        ]

        loc = supabase_store.get_pickup_location(order.get("pickup_location_id", ""))
        return DraftOrderResponse(
            order_id=order["order_id"],
            seller_id=order["seller_id"],
            pickup_location_id=order.get("pickup_location_id"),
            pickup_location=loc,
            status=order.get("status", "S1"),
            need_lifting_help=order.get("need_lifting_help", False),
            lifting_help_notes=order.get("lifting_help_notes"),
            total_est_min_price=order.get("total_est_min_price", 0.0),
            total_est_max_price=order.get("total_est_max_price", 0.0),
            items=items,
            created_at=order.get("created_at", ""),
            updated_at=order.get("updated_at", ""),
        )

    @staticmethod
    def add_item_to_draft(order_id: str, req: WasteItemCreateRequest) -> WasteItemResponse:
        """
        เพิ่มรายการของเก่าลงในฉบับร่าง (AC-S02-01, AC-S02-02, Card 03)
        พร้อม Missing Sub-Category Guard บล็อกเมื่อไม่ระบุประเภทย่อยของชิ้นใหญ่ (AC-S02-03)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส {order_id}",
            )

        cat = supabase_store.get_scrap_category(req.category_code)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ไม่พบหมวดหมู่ของเก่ารหัส {req.category_code}",
            )

        group = cat["category_group"]
        unit = cat["unit"]
        category_name = cat["name"]

        # -------------------------------------------------------------
        # Missing Sub-Category Guard สำหรับหมวดของชิ้นใหญ่ (Card 03 Exception Case)
        # -------------------------------------------------------------
        if group == "BULKY_FLAT_RATE":
            if not req.sub_category or not req.sub_category.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้",
                )
            sub_cat = req.sub_category.strip()
            # ใช้ช่วงราคาประเมินตามประเภทย่อย (Card 03 Pass Case)
            if sub_cat in BULKY_PRICE_MAP:
                min_p, max_p = BULKY_PRICE_MAP[sub_cat]
            else:
                min_p, max_p = cat["min_price_per_unit"], cat["max_price_per_unit"]
            category_name = f"{category_name} ({sub_cat})"
        else:
            sub_cat = req.sub_category.strip() if req.sub_category else None
            min_p = cat["min_price_per_unit"]
            max_p = cat["max_price_per_unit"]

        est_min = round(min_p * req.quantity, 2)
        est_max = round(max_p * req.quantity, 2)

        item_data = {
            "category_code": req.category_code,
            "category_name": category_name,
            "category_group": group,
            "sub_category": sub_cat,
            "quantity": req.quantity,
            "unit": unit,
            "est_min_price": est_min,
            "est_max_price": est_max,
            "photo_urls": req.photo_urls or [],
        }
        saved_item = supabase_store.add_item_to_order(order_id, item_data)

        supabase_store.add_audit_log(
            action="ITEM_ADDED_TO_DRAFT",
            entity_id=saved_item["item_id"],
            actor_id=order["seller_id"],
            details={
                "order_id": order_id,
                "category_code": req.category_code,
                "quantity": req.quantity,
                "est_min_price": est_min,
                "est_max_price": est_max,
            },
        )

        return WasteItemResponse(
            item_id=saved_item["item_id"],
            order_id=order_id,
            category_code=saved_item["category_code"],
            category_name=saved_item["category_name"],
            category_group=saved_item["category_group"],
            sub_category=saved_item.get("sub_category"),
            quantity=saved_item["quantity"],
            unit=saved_item["unit"],
            est_min_price=saved_item["est_min_price"],
            est_max_price=saved_item["est_max_price"],
            photo_urls=saved_item.get("photo_urls", []),
        )

    @staticmethod
    def delete_item_from_draft(order_id: str, item_id: str) -> dict:
        """
        ลบรายการของเก่าออกจากฉบับร่าง
        """
        success = supabase_store.delete_item_from_order(order_id, item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบรายการรหัส {item_id} ในคำขอนี้",
            )
        order = supabase_store.get_order(order_id)
        if order:
            supabase_store.add_audit_log(
                action="ITEM_DELETED_FROM_DRAFT",
                entity_id=item_id,
                actor_id=order["seller_id"],
                details={"order_id": order_id},
            )
        return {"success": True, "message": "ลบรายการของเก่าสำเร็จ"}

    @staticmethod
    def attach_photo_to_item(order_id: str, item_id: str, photo_url: str) -> WasteItemResponse:
        """
        แนบรูปถ่ายของเก่าประกอบรายการ (จำกัดไม่เกิน 5 รูป - AC-S02-04, P-04)
        """
        try:
            updated_item = supabase_store.attach_photo_to_item(item_id, photo_url)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        if not updated_item or updated_item.get("order_id") != order_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบรายการรหัส {item_id}",
            )

        order = supabase_store.get_order(order_id)
        if order:
            supabase_store.add_audit_log(
                action="ITEM_PHOTOS_UPDATED",
                entity_id=item_id,
                actor_id=order["seller_id"],
                details={"total_photos": len(updated_item["photo_urls"])},
            )

        return WasteItemResponse(
            item_id=updated_item["item_id"],
            order_id=order_id,
            category_code=updated_item["category_code"],
            category_name=updated_item["category_name"],
            category_group=updated_item["category_group"],
            sub_category=updated_item.get("sub_category"),
            quantity=updated_item["quantity"],
            unit=updated_item["unit"],
            est_min_price=updated_item["est_min_price"],
            est_max_price=updated_item["est_max_price"],
            photo_urls=updated_item.get("photo_urls", []),
        )

    @staticmethod
    def delete_photo_from_item(order_id: str, item_id: str, photo_idx: int) -> WasteItemResponse:
        """
        ลบรูปถ่ายของเก่าออกจากรายการ (AC-S02-04)
        """
        try:
            updated_item = supabase_store.delete_photo_from_item(item_id, photo_idx)
        except IndexError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        if not updated_item or updated_item.get("order_id") != order_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบรายการรหัส {item_id}",
            )

        return WasteItemResponse(
            item_id=updated_item["item_id"],
            order_id=order_id,
            category_code=updated_item["category_code"],
            category_name=updated_item["category_name"],
            category_group=updated_item["category_group"],
            sub_category=updated_item.get("sub_category"),
            quantity=updated_item["quantity"],
            unit=updated_item["unit"],
            est_min_price=updated_item["est_min_price"],
            est_max_price=updated_item["est_max_price"],
            photo_urls=updated_item.get("photo_urls", []),
        )

    @staticmethod
    def update_lifting_help(order_id: str, req: LiftingHelpUpdateRequest) -> DraftOrderResponse:
        """
        ปรับปรุงตัวเลือกขอคนช่วยยกของหนักและหมายเหตุหน้างาน (AC-S02-05, P-05)
        """
        order = supabase_store.get_order(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ไม่พบคำขอรหัส {order_id}",
            )

        updates = {
            "need_lifting_help": req.need_lifting_help,
            "lifting_help_notes": req.lifting_help_notes,
        }
        supabase_store.update_order(order_id, updates)

        supabase_store.add_audit_log(
            action="LIFTING_HELP_UPDATED",
            entity_id=order_id,
            actor_id=order["seller_id"],
            details=updates,
        )

        return ScrapPostingService.get_draft_order(order_id)

