"""
Integration E2E Lifecycle Test สำหรับระบบโพสต์ขายของเก่าของผู้ขาย (AC-S02-01..05)
รองรับ UC-02, REQ-UX-002, REQ-FN-003, REQ-FN-004, REQ-DAT-001, REQ-SEC-001, Card 03, P-01..P-06
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store


client = TestClient(app)


def test_e2e_scrap_posting_lifecycle():
    """
    ทดสอบครบวงจรระบบโพสต์ขายของเก่า (S1 Draft):
    1. ผู้ขายดึงคู่มือภาพ 3 หมวดหมู่ (AC-S02-01)
    2. สร้างคำขอฉบับร่าง S1 Draft พร้อมผูกที่อยู่นัดหมายเริ่มต้นอัตโนมัติ (P-06)
    3. เพิ่มรายการวัสดุชั่งกิโลกรัม: กระดาษลัง 15 กก. (AC-S02-01)
    4. ทดสอบ Guard เมื่อเลือกของชิ้นใหญ่เหมาจ่ายแต่ลืมเลือกประเภทย่อย -> บล็อก 422 (AC-S02-03)
    5. เพิ่มของชิ้นใหญ่เหมาจ่าย: ตู้เย็น 1 ชิ้น -> คิดราคา 200–300 บาท (AC-S02-02, Card 03)
    6. เพิ่มวัสดุบรรจุลัง: ขวดแก้วลัง 2 ลัง -> คิดราคา 30–50 บาท (AC-S02-02)
    7. แนบรูปถ่ายของเก่า 2 รูปประกอบรายการ (AC-S02-04)
    8. เลือกบริการเสริมขอคนช่วยยกของหนัก พร้อมระบุข้อจำกัดหน้างาน (AC-S02-05)
    9. ตรวจสอบยอดเงินประเมินรวม Min–Max ของคำขอฉบับร่าง
    10. ตรวจสอบ Audit Log บันทึกทุกเหตุการณ์ครบถ้วน (REQ-SEC-001)
    """
    # Step 1: ดึงคู่มือภาพ
    cats_res = client.get("/api/v1/scrap-posting/categories")
    assert cats_res.status_code == 200
    assert len(cats_res.json()["categories"]) >= 8

    # เตรียมผู้ขายและที่อยู่นัดหมาย
    seller = supabase_store.create_seller({"phone": "0878889900", "display_name": "คุณวิชัย"})
    seller_id = seller["seller_id"]
    loc = supabase_store.create_pickup_location({
        "seller_id": seller_id,
        "label": "บ้านสวน",
        "sub_district": "บางบอน",
        "address_text": "777 ถ.เอกชัย ซอย 10",
        "geo_point": {"lat": 13.65, "lng": 100.40},
        "is_default": True,
    })

    # Step 2: สร้างคำขอฉบับร่าง
    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    assert draft_res.status_code == 201
    draft = draft_res.json()
    order_id = draft["order_id"]
    assert draft["status"] == "S1"
    assert draft["pickup_location_id"] == loc["location_id"]

    # Step 3: เพิ่มกระดาษลัง 15 กก. (3–4 บ./กก.)
    item1_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={"category_code": "MAT-CARDBOARD", "quantity": 15.0},
    )
    assert item1_res.status_code == 201
    item1 = item1_res.json()
    assert item1["est_min_price"] == 45.0
    assert item1["est_max_price"] == 60.0

    # Step 4: ทดสอบ Guard หมวดของชิ้นใหญ่ (ลืมใส่ sub_category) -> ต้องบล็อก 422
    fail_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={"category_code": "BULKY-APPLIANCE", "quantity": 1.0},
    )
    assert fail_res.status_code == 422
    assert "กรุณาระบุประเภทของชิ้นใหญ่" in fail_res.json()["detail"]

    # Step 5: เพิ่มตู้เย็น 1 ชิ้น (200–300 บ./ชิ้น)
    item2_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={
            "category_code": "BULKY-APPLIANCE",
            "sub_category": "ตู้เย็น",
            "quantity": 1.0,
        },
    )
    assert item2_res.status_code == 201
    item2 = item2_res.json()
    assert item2["est_min_price"] == 200.0
    assert item2["est_max_price"] == 300.0

    # Step 6: เพิ่มขวดแก้ว 2 ลัง (15–25 บ./ลัง)
    item3_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={
            "category_code": "BOXED-GLASS",
            "sub_category": "ขวดเบียร์ลัง",
            "quantity": 2.0,
        },
    )
    assert item3_res.status_code == 201
    item3 = item3_res.json()
    assert item3["est_min_price"] == 30.0
    assert item3["est_max_price"] == 50.0

    # Step 7: แนบรูปถ่าย 2 รูปกับตู้เย็น
    client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items/{item2['item_id']}/photos",
        json={"photo_url": "https://example.com/fridge_front.jpg"},
    )
    client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items/{item2['item_id']}/photos",
        json={"photo_url": "https://example.com/fridge_side.jpg"},
    )

    # Step 8: ขอคนช่วยยกของหนัก
    lift_res = client.patch(
        f"/api/v1/scrap-posting/drafts/{order_id}/lifting-help",
        json={
            "need_lifting_help": True,
            "lifting_help_notes": "ตู้เย็น 12 คิว อยู่ในครัวหลังบ้าน ต้องยกผ่านทางเดินแคบ",
        },
    )
    assert lift_res.status_code == 200
    assert lift_res.json()["need_lifting_help"] is True

    # Step 9: ตรวจสอบยอดรวมทั้งหมดของฉบับร่าง
    # item1 (45-60) + item2 (200-300) + item3 (30-50) = 275 - 410
    final_draft = client.get(f"/api/v1/scrap-posting/drafts/{order_id}").json()
    assert final_draft["total_est_min_price"] == 275.0
    assert final_draft["total_est_max_price"] == 410.0
    assert len(final_draft["items"]) == 3

    # Step 10: ตรวจสอบ Audit Log
    actions = [log["action"] for log in supabase_store.audit_logs if log["actor_id"] == seller_id]
    assert "DRAFT_ORDER_CREATED" in actions
    assert "ITEM_ADDED_TO_DRAFT" in actions
    assert "ITEM_PHOTOS_UPDATED" in actions
    assert "LIFTING_HELP_UPDATED" in actions

