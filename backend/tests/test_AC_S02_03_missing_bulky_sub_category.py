"""
Automated Test สำหรับ AC-S02-03: Missing Bulky Sub-Category Guard
รองรับ REQ-FN-003, Card 03 (Exception Case), P-02, Q-02
- หากเลือกหมวด "ของชิ้นใหญ่แบบเหมาจ่าย" แต่ไม่ระบุประเภทย่อย (เช่น ตู้เย็น, เครื่องซักผ้า)
- ระบบต้องบล็อกด้วย HTTP 422
- แจ้งเตือน: "กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้"
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S02_03_missing_bulky_sub_category_guard():
    """
    ทดสอบ Card 03 Exception Case:
    เลือกหมวด "ของชิ้นใหญ่แบบเหมาจ่าย" แต่ไม่ระบุประเภทย่อย
    ระบบต้องปฏิเสธและส่งข้อความเตือนตรงตามสเปก
    """
    seller = supabase_store.create_seller({"phone": "0845556677", "display_name": "ลุงสมพงษ์"})
    seller_id = seller["seller_id"]
    loc = supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "sub_district": "ตลิ่งชัน",
        "address_text": "444 ถ.บรมราชชนนี",
        "geo_point": {"lat": 13.78, "lng": 100.45},
        "is_default": True,
    })

    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    order_id = draft_res.json()["order_id"]

    # 1. กรณีไม่ส่งฟิลด์ sub_category
    item_res1 = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={"category_code": "BULKY-APPLIANCE", "quantity": 1.0},
    )
    assert item_res1.status_code == 422
    assert "กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้" in item_res1.json()["detail"]

    # 2. กรณีส่ง sub_category เป็นสตริงว่าง
    item_res2 = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={"category_code": "BULKY-APPLIANCE", "sub_category": "   ", "quantity": 1.0},
    )
    assert item_res2.status_code == 422
    assert "กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้" in item_res2.json()["detail"]

