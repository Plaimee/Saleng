"""
Automated Test สำหรับ AC-S02-01: Visual Scrap Guide & Category Selection
รองรับ UC-02, REQ-UX-002, Q-01, P-01, P-06
- ผู้ขายสามารถดึงคู่มือภาพ 3 หมวดหลัก
- สร้างฉบับร่าง S1 Draft ผูกกับที่อยู่นัดหมาย
- เพิ่มรายการวัสดุชั่งกิโลกรัมทั่วไป คำนวณช่วงราคาประเมินถูกต้อง
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S02_01_categories_catalog_and_selection():
    """ทดสอบการดึงคู่มือภาพ 3 หมวดหลัก (AC-S02-01, REQ-UX-002)"""
    res = client.get("/api/v1/scrap-posting/categories")
    assert res.status_code == 200
    data = res.json()
    cats = data["categories"]
    assert len(cats) >= 8

    groups = {c["category_group"] for c in cats}
    assert "GENERAL_WEIGHT" in groups
    assert "BOXED_CRATE_ITEMS" in groups
    assert "BULKY_FLAT_RATE" in groups

    # ตรวจสอบว่าทุกรายการมีไอคอนและช่วงราคา
    for c in cats:
        assert c["icon"] is not None
        assert c["min_price_per_unit"] > 0
        assert c["max_price_per_unit"] >= c["min_price_per_unit"]


def test_AC_S02_01_draft_order_and_general_weight_item():
    """ทดสอบการสร้างฉบับร่าง S1 และเพิ่มวัสดุชั่งกิโลกรัม (AC-S02-01, P-06)"""
    # 1. สร้างผู้ขายและที่อยู่นัดหมายเริ่มต้น
    seller = supabase_store.create_seller({
        "phone": "0812223344",
        "display_name": "ผู้ขาย ทดสอบโพสต์",
    })
    seller_id = seller["seller_id"]
    loc = supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "label": "บ้าน",
        "sub_district": "บางพลัด",
        "address_text": "100 ซอยจรัญสนิทวงศ์ 75",
        "geo_point": {"lat": 13.78, "lng": 100.50},
        "is_default": True,
    })

    # 2. สร้างฉบับร่าง (ดึง default pickup location อัตโนมัติ)
    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    assert draft_res.status_code == 201
    draft = draft_res.json()
    order_id = draft["order_id"]
    assert draft["status"] == "S1"
    assert draft["pickup_location_id"] == loc["location_id"]
    assert draft["total_est_min_price"] == 0.0

    # 3. เพิ่มกระดาษลัง 20 กก. (3–4 บ./กก.)
    item_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={"category_code": "MAT-CARDBOARD", "quantity": 20.0},
    )
    assert item_res.status_code == 201
    item = item_res.json()
    assert item["quantity"] == 20.0
    assert item["est_min_price"] == 60.0
    assert item["est_max_price"] == 80.0

    # 4. ตรวจสอบยอดรวมของคำขอฉบับร่าง
    get_draft = client.get(f"/api/v1/scrap-posting/drafts/{order_id}")
    assert get_draft.status_code == 200
    d_data = get_draft.json()
    assert d_data["total_est_min_price"] == 60.0
    assert d_data["total_est_max_price"] == 80.0
    assert len(d_data["items"]) == 1

