"""
Automated Test สำหรับ AC-S02-05: Lifting Help Request & Badge Alert
รองรับ REQ-FN-004, MD-DOM-04, Q-04, P-05
- ผู้ขายสามารถเลือกบริการเสริมขอคนช่วยยกของหนัก (needLiftingHelp: True)
- ระบุข้อจำกัดหน้างาน liftingHelpNotes (เช่น ชั้นอาคาร หรือขนาดสิ่งของ)
- มีป้ายสัญลักษณ์แจ้งเตือนบนคำขอ
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_AC_S02_05_lifting_help_update():
    """ทดสอบการขอคนช่วยยกของหนักและหมายเหตุหน้างาน (AC-S02-05)"""
    seller = supabase_store.create_seller({"phone": "0867778899", "display_name": "คุณนภา"})
    seller_id = seller["seller_id"]
    supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "sub_district": "วัฒนา",
        "address_text": "666 สุขุมวิท 39 คอนโด ชั้น 4",
        "geo_point": {"lat": 13.73, "lng": 100.57},
        "is_default": True,
    })

    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    order_id = draft_res.json()["order_id"]
    assert draft_res.json()["need_lifting_help"] is False

    # อัปเดตขอคนช่วยยก
    lift_res = client.patch(
        f"/api/v1/scrap-posting/drafts/{order_id}/lifting-help",
        json={
            "need_lifting_help": True,
            "lifting_help_notes": "อยู่ชั้น 4 ไม่มีลิฟต์ มีตู้เย็นขนาด 10 คิว ต้องใช้ 2 คนยก",
        },
    )
    assert lift_res.status_code == 200
    updated_order = lift_res.json()
    assert updated_order["need_lifting_help"] is True
    assert "ชั้น 4 ไม่มีลิฟต์" in updated_order["lifting_help_notes"]

    # ตรวจสอบการดึงข้อมูลคำขอ
    get_res = client.get(f"/api/v1/scrap-posting/drafts/{order_id}")
    assert get_res.json()["need_lifting_help"] is True

