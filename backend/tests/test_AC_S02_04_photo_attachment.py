"""
Automated Test สำหรับ AC-S02-04: Multi-Photo Attachment & Limits
รองรับ REQ-FN-004, EV-03, EV-08, Q-03, P-04
- แนบรูปถ่ายของเก่าประกอบรายการ สูงสุด 5 รูป
- บล็อกเมื่อแนบเกิน 5 รูป
- ลบรูปถ่ายออกจากรายการ
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S02_04_photo_attachment_and_limit():
    """ทดสอบการแนบรูปถ่ายและการจำกัดไม่เกิน 5 รูป (AC-S02-04)"""
    seller = supabase_store.create_seller({"phone": "0856667788", "display_name": "ป้าสมใจ"})
    seller_id = seller["seller_id"]
    supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "sub_district": "ดอนเมือง",
        "address_text": "555 ถ.สรงประภา",
        "geo_point": {"lat": 13.92, "lng": 100.59},
        "is_default": True,
    })

    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    order_id = draft_res.json()["order_id"]

    # เพิ่มกระดาษลัง 10 กก.
    item_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={"category_code": "MAT-CARDBOARD", "quantity": 10.0},
    )
    item_id = item_res.json()["item_id"]

    # แนบรูปที่ 1 ถึง 5
    for i in range(1, 6):
        att_res = client.post(
            f"/api/v1/scrap-posting/drafts/{order_id}/items/{item_id}/photos",
            json={"photo_url": f"https://example.com/photo_{i}.jpg"},
        )
        assert att_res.status_code == 200
        assert len(att_res.json()["photo_urls"]) == i

    # แนบรูปที่ 6 -> ต้องติดข้อจำกัด 400
    att_res6 = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items/{item_id}/photos",
        json={"photo_url": "https://example.com/photo_6.jpg"},
    )
    assert att_res6.status_code == 400
    assert "ไม่เกิน 5 รูป" in att_res6.json()["detail"]

    # ลบรูปที่ 0
    del_res = client.delete(
        f"/api/v1/scrap-posting/drafts/{order_id}/items/{item_id}/photos/0"
    )
    assert del_res.status_code == 200
    assert len(del_res.json()["photo_urls"]) == 4

