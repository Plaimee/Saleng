"""
Automated Test สำหรับ AC-S02-02: Bulky Flat-Rate & Boxed Crate Estimation
รองรับ REQ-FN-003, Card 03 (Pass & Alt Cases), P-02, P-03
- หมวดของชิ้นใหญ่เหมาจ่าย (ตู้เย็น 200–300 บาท/ชิ้น)
- หมวดวัสดุบรรจุลัง (ขวดแก้วลัง, ขวดพลาสติกกระสอบ)
- ส่งต่อข้อมูลขนาดและประเภทย่อยไปยังผู้รับซื้อครบถ้วน 100%
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S02_02_bulky_fridge_pass_case():
    """
    ทดสอบ Card 03 Pass Case:
    เลือกหมวด "ของชิ้นใหญ่แบบเหมาจ่าย" และเลือกประเภท "ตู้เย็น" 1 ชิ้น
    ระบบต้องแสดงช่วงราคาเหมาอ้างอิง 200–300 บาท (Card 03)
    """
    seller = supabase_store.create_seller({"phone": "0823334455", "display_name": "เจ๊หมวย"})
    seller_id = seller["seller_id"]
    loc = supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "sub_district": "ห้วยขวาง",
        "address_text": "222 ถ.ประชาสงเคราะห์",
        "geo_point": {"lat": 13.77, "lng": 100.57},
        "is_default": True,
    })

    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    order_id = draft_res.json()["order_id"]

    # เพิ่มตู้เย็น 1 ชิ้น
    item_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={
            "category_code": "BULKY-APPLIANCE",
            "sub_category": "ตู้เย็น",
            "quantity": 1.0,
        },
    )
    assert item_res.status_code == 201
    item = item_res.json()
    assert item["category_group"] == "BULKY_FLAT_RATE"
    assert item["sub_category"] == "ตู้เย็น"
    assert item["quantity"] == 1.0
    assert item["unit"] == "piece"
    assert item["est_min_price"] == 200.0
    assert item["est_max_price"] == 300.0


def test_AC_S02_02_boxed_items_alt_case():
    """
    ทดสอบ Card 03 Alt Case:
    เลือกหมวด "วัสดุบรรจุลังแยกเฉพาะ" เช่น ขวดแก้วบรรจุลัง 3 ลัง
    ระบบต้องคำนวณตามเรตกล่อง/ลัง (15–25 บ./ลัง)
    """
    seller = supabase_store.create_seller({"phone": "0834445566", "display_name": "เสี่ยอ๋า"})
    seller_id = seller["seller_id"]
    loc = supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "sub_district": "มีนบุรี",
        "address_text": "333 ถ.สุวินทวงศ์",
        "geo_point": {"lat": 13.81, "lng": 100.72},
        "is_default": True,
    })

    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    order_id = draft_res.json()["order_id"]

    # เพิ่มขวดแก้ว 3 ลัง
    item_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={
            "category_code": "BOXED-GLASS",
            "sub_category": "ขวดเบียร์ลัง",
            "quantity": 3.0,
        },
    )
    assert item_res.status_code == 201
    item = item_res.json()
    assert item["category_group"] == "BOXED_CRATE_ITEMS"
    assert item["unit"] == "crate"
    assert item["quantity"] == 3.0
    assert item["est_min_price"] == 45.0  # 15 * 3
    assert item["est_max_price"] == 75.0  # 25 * 3

