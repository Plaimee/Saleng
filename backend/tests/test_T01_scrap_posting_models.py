"""
Unit tests สำหรับ Data Models และ Supabase Store ของระบบโพสต์ขายของเก่า (T-01)
รองรับ UC-02, REQ-UX-002, REQ-FN-003, REQ-FN-004, Card 03, MD-DOM-04, P-01..P-03
"""

import pytest
from pydantic import ValidationError
from backend.app.models.scrap_posting_models import (
    WasteItemCreateRequest,
    LiftingHelpUpdateRequest,
    DraftOrderCreateRequest,
)
from backend.app.core.supabase import supabase_store


def test_scrap_posting_models_validation():
    """ทดสอบ Pydantic Validation สำหรับ WasteItemCreateRequest (AC-S02-01, AC-S02-04)"""
    # ปริมาณปกติ
    req = WasteItemCreateRequest(category_code="MAT-CARDBOARD", quantity=10.5)
    assert req.quantity == 10.5
    assert req.photo_urls == []

    # ปริมาณ <= 0 ต้องติด validation
    with pytest.raises(ValidationError):
        WasteItemCreateRequest(category_code="MAT-CARDBOARD", quantity=0)

    # แนบรูปเกิน 5 รูป ต้องติด validation (AC-S02-04)
    with pytest.raises(ValidationError):
        WasteItemCreateRequest(
            category_code="MAT-CARDBOARD",
            quantity=5.0,
            photo_urls=["url1", "url2", "url3", "url4", "url5", "url6"],
        )


def test_scrap_categories_seed_and_store():
    """ทดสอบการ Seeding หมวดหมู่ของเก่า 3 หมวดหลักใน Supabase Store (AC-S02-01, Card 03)"""
    categories = supabase_store.get_scrap_categories()
    assert len(categories) >= 8

    # ตรวจสอบว่ามีครบทั้ง 3 กลุ่มหลัก
    groups = {c["category_group"] for c in categories}
    assert "GENERAL_WEIGHT" in groups
    assert "BOXED_CRATE_ITEMS" in groups
    assert "BULKY_FLAT_RATE" in groups

    # ตรวจสอบหมวดของชิ้นใหญ่ (Card 03)
    bulky = supabase_store.get_scrap_category("BULKY-APPLIANCE")
    assert bulky is not None
    assert bulky["unit"] == "piece"
    assert "ตู้เย็น" in bulky["sub_categories"]
    assert "เครื่องซักผ้า" in bulky["sub_categories"]


def test_draft_order_and_items_store():
    """ทดสอบ Store CRUD สำหรับคำขอฉบับร่างและการคำนวณยอดรวม Min-Max (MD-DOM-04, P-06)"""
    order_data = {
        "seller_id": "SEL-TEST-01",
        "pickup_location_id": "LOC-TEST-01",
        "status": "S1",
        "need_lifting_help": False,
        "total_est_min_price": 0.0,
        "total_est_max_price": 0.0,
    }
    order = supabase_store.create_order(order_data, [])
    order_id = order["order_id"]

    # เพิ่มของเก่าชิ้นที่ 1: กระดาษลัง 10 กก. (3–4 บ./กก.)
    item1 = {
        "category_code": "MAT-CARDBOARD",
        "category_group": "GENERAL_WEIGHT",
        "quantity": 10.0,
        "unit": "kg",
        "est_min_price": 30.0,
        "est_max_price": 40.0,
    }
    supabase_store.add_item_to_order(order_id, item1)

    # เพิ่มของเก่าชิ้นที่ 2: ตู้เย็น 1 ชิ้น (200–300 บ./ชิ้น)
    item2 = {
        "category_code": "BULKY-APPLIANCE",
        "category_group": "BULKY_FLAT_RATE",
        "sub_category": "ตู้เย็น",
        "quantity": 1.0,
        "unit": "piece",
        "est_min_price": 200.0,
        "est_max_price": 300.0,
    }
    supabase_store.add_item_to_order(order_id, item2)

    # ตรวจสอบยอดรวมที่คำนวณอัตโนมัติ
    updated_order = supabase_store.get_order(order_id)
    assert updated_order["total_est_min_price"] == 230.0
    assert updated_order["total_est_max_price"] == 340.0
    assert len(updated_order["items"]) == 2

