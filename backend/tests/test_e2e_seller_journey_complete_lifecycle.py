"""
Comprehensive End-to-End Integration Test สำหรับวงจรการขายฝั่งผู้ขายครบทั้ง 9 ฟีเจอร์ (Seller Journey S01..S09)
ทดสอบความสอดคล้องและการเชื่อมโยงข้อมูลอย่างไร้รอยต่อ:
- S01: ยืนยันตัวตน OTP และระบุสถานที่รับของ
- S02: สร้างโพสต์ของเก่า แนบรูป และขอคนช่วยยก
- S04: คำนวณราคากลาง ตรวจสอบ Minimum Threshold
- S03: ค้นหาซาเล้ง KYC 100% และบันทึกคนโปรด
- S05: เลือกสล็อตเวลานัดหมาย ติดตาม 9 สถานะ MD-STM-04 และบังคับใช้กฎเหล็ก BR-03
- S09: บันทึกข้อมูลผู้ติดต่อฉุกเฉิน
- S06: บันทึกผลชั่งน้ำหนัก ยืนยันผลชั่ง ชำระเงิน และออกใบเสร็จดิจิทัล
- S07: ให้คะแนนรีวิว บันทึกผู้ซื้อประจำ และดูประวัติการขาย
- S08: ตรวจสอบการแจ้งเตือนความคืบหน้า และคู่มือแยกขยะ
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_complete_seller_customer_journey_s01_to_s09():
    # =========================================================================
    # STEP 1 (Seller 01): การลงทะเบียน ยืนยันตัวตน OTP และระบุสถานที่รับของ
    # =========================================================================
    phone = "0819876543"
    otp_req = client.post("/api/v1/sellers/auth/request-otp", json={"phone": phone})
    assert otp_req.status_code == 200
    otp_code = otp_req.json().get("mock_otp") or "123456"

    verify_res = client.post("/api/v1/sellers/auth/verify-otp", json={"phone": phone, "otp_code": otp_code})
    assert verify_res.status_code == 200
    seller_id = verify_res.json()["seller_id"]

    # เพิ่มสถานที่รับของเก่า
    loc_res = client.post(
        f"/api/v1/sellers/{seller_id}/locations",
        json={
            "label": "บ้านพักประชาชื่น",
            "address_text": "99/12 ซอยประชาชื่น 14 เขตบางซื่อ กทม.",
            "sub_district": "บางซื่อ",
            "geo_point": {"lat": 13.8245, "lng": 100.5378},
            "is_default": True,
        },
    )
    assert loc_res.status_code == 201

    # =========================================================================
    # STEP 2 (Seller 02): โพสต์ของเก่า แนบรูปภาพ และระบุการขอคนช่วยยก (Lifting Help)
    # =========================================================================
    draft_res = client.post("/api/v1/scrap-posting/drafts", json={"seller_id": seller_id})
    assert draft_res.status_code == 201
    draft_data = draft_res.json()
    order_id = draft_data["order_id"]

    # เพิ่มรายการของเก่า 1: กระดาษลัง 30 กก.
    item1_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={
            "category_code": "MAT-CARDBOARD",
            "quantity": 30.0,
        },
    )
    assert item1_res.status_code == 201
    item1_id = item1_res.json()["item_id"]

    # เพิ่มรายการของเก่า 2: ตู้เย็นเก่า (Bulky item พร้อมขอคนช่วยยก)
    item2_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items",
        json={
            "category_code": "BULKY-APPLIANCE",
            "sub_category": "ตู้เย็น",
            "quantity": 1.0,
        },
    )
    assert item2_res.status_code == 201
    item2_id = item2_res.json()["item_id"]

    # แนบรูปถ่ายของเก่า
    photo_res = client.post(
        f"/api/v1/scrap-posting/drafts/{order_id}/items/{item2_id}/photos",
        json={"photo_url": "https://example.com/fridge_photo.jpg"},
    )
    assert photo_res.status_code == 200

    # ขอคนช่วยยกของหนัก
    lift_res = client.patch(
        f"/api/v1/scrap-posting/drafts/{order_id}/lifting-help",
        json={
            "need_lifting_help": True,
            "lifting_help_notes": "ตู้เย็น 2 ประตูอยู่ชั้น 1 ต้องช่วยยก 2 คน",
        },
    )
    assert lift_res.status_code == 200

    # =========================================================================
    # STEP 3 (Seller 04): ตรวจสอบราคากลาง และคำนวณราคาประเมิน
    # =========================================================================
    bench_res = client.get("/api/v1/pricing/benchmark-prices")
    assert bench_res.status_code == 200
    bench_data = bench_res.json()
    assert len(bench_data["prices"]) >= 5

    # =========================================================================
    # STEP 4 (Seller 03): ค้นหาซาเล้งในพื้นที่ และบันทึกเป็นผู้รับซื้อประจำ
    # =========================================================================
    search_res = client.get(
        f"/api/v1/buyer-search/collectors?seller_id={seller_id}&lat=13.8245&lng=100.5378&radius_km=5.0"
    )
    assert search_res.status_code == 200
    collectors = search_res.json()["collectors"]
    assert len(collectors) >= 1
    target_saleng = collectors[0]
    saleng_id = target_saleng["saleng_id"]

    # บุ๊กมาร์กเป็นผู้ซื้อประจำ
    fav_res = client.post(
        f"/api/v1/buyer-search/favorites/{saleng_id}/toggle?seller_id={seller_id}"
    )
    assert fav_res.status_code == 200
    assert fav_res.json()["is_favorite"] is True

    # =========================================================================
    # STEP 5 (Seller 05): เลือกเวลานัดหมาย ส่งคำขอ (S1 -> S2) และติดตามสถานะ (MD-STM-04)
    # =========================================================================
    book_res = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/book?seller_id={seller_id}",
        json={
            "booking_type": "SCHEDULED",
            "scheduled_date": "2026-11-10",
            "scheduled_slot": "MORNING_09_12",
            "notes": "รั้วสีขาว ติดร้านขายยา",
        },
    )
    assert book_res.status_code == 200
    assert book_res.json()["status"] == "S2"

    # ซาเล้งกดรับงาน (S2 -> S3)
    sim_s3 = client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status?seller_id={seller_id}",
        json={"target_status": "S3", "saleng_id": saleng_id},
    )
    assert sim_s3.status_code == 200
    assert sim_s3.json()["status"] == "S3"
    assert sim_s3.json()["can_cancel"] is True  # ใน S3 ยังยกเลิกได้ตาม BR-03

    # ซาเล้งออกเดินทาง (S3 -> S4 In-Transit)
    sim_s4 = client.patch(
        f"/api/v1/booking-tracking/orders/{order_id}/simulate-status?seller_id={seller_id}",
        json={"target_status": "S4", "saleng_id": saleng_id},
    )
    assert sim_s4.status_code == 200
    assert sim_s4.json()["status"] == "S4"
    assert sim_s4.json()["can_cancel"] is False  # ใน S4 ล็อกปุ่มยกเลิกตาม BR-03
    assert sim_s4.json()["eta_minutes"] is not None
    assert sim_s4.json()["distance_km"] is not None

    # ทดสอบกฎเหล็ก BR-03: ผู้ขายพยายามกดยกเลิกใน S4 ระบบต้องบล็อกและตอบ 400
    blocked_cancel = client.post(
        f"/api/v1/booking-tracking/orders/{order_id}/cancel?seller_id={seller_id}",
        json={"reason": "ขอยกเลิกกระทันหันครับ"},
    )
    assert blocked_cancel.status_code == 400
    assert "BR-03" in blocked_cancel.json()["detail"]

    # =========================================================================
    # STEP 6 (Seller 09): ตั้งค่าผู้ติดต่อฉุกเฉิน (Transaction Safety)
    # =========================================================================
    contact_res = client.put(
        f"/api/v1/sellers/{seller_id}/safety/emergency-contact",
        json={
            "contact_name": "นายสมพงษ์ ปลอดภัย",
            "relationship": "พี่ชาย",
            "contact_phone": "0891234567",
        },
    )
    assert contact_res.status_code == 200
    assert contact_res.json()["contact_phone_masked"] == "08X-XXX-4567"

    # =========================================================================
    # STEP 7 (Seller 06): บันทึกผลชั่งจริงหน้างาน (S4 -> S5) ยืนยันน้ำหนัก (S6) และชำระเงิน (S7)
    # =========================================================================
    weigh_payload = {
        "scale_photo_url": "https://storage.saleng.app/weigh/scale_photo_01.jpg",
        "items": [
            {
                "item_id": item1_id,
                "actual_quantity": 30.0,
            },
            {
                "item_id": item2_id,
                "actual_quantity": 1.0,
            },
        ],
    }
    weigh_res = client.post(
        f"/api/v1/orders/{order_id}/record-weighing",
        json=weigh_payload,
    )
    assert weigh_res.status_code == 200, weigh_res.text
    assert weigh_res.json()["status"] == "S5"

    # ผู้ขายกดยืนยันตัวเลขน้ำหนัก (S5 -> S6)
    conf_res = client.post(
        f"/api/v1/orders/{order_id}/confirm-weights",
        json={"seller_id": seller_id},
    )
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] == "S6"

    # ผู้ขายกดยืนยันรับเงิน (S6 -> S7) พร้อมออกใบเสร็จดิจิทัล
    pay_res = client.post(
        f"/api/v1/orders/{order_id}/confirm-payment",
        json={"seller_id": seller_id, "payment_method": "PROMPTPAY"},
    )
    assert pay_res.status_code == 200
    pay_data = pay_res.json()
    assert pay_data["status"] == "S7"
    assert "REC-" in pay_data["receipt_no"]

    # =========================================================================
    # STEP 8 (Seller 07): ให้คะแนนรีวิวซาเล้ง และตรวจสอบประวัติการขาย (Sales History)
    # =========================================================================
    review_res = client.post(
        f"/api/v1/orders/{order_id}/review",
        json={
            "seller_id": seller_id,
            "rating": 5,
            "comment": "บริการสุภาพ ตาชั่งเที่ยงตรงมากครับ",
        },
    )
    assert review_res.status_code == 201

    # ดูประวัติการขาย
    history_res = client.get(f"/api/v1/sellers/{seller_id}/sales-history")
    assert history_res.status_code == 200
    orders_list = history_res.json()["orders"]
    assert any(o["order_id"] == order_id for o in orders_list)

    # =========================================================================
    # STEP 9 (Seller 08): ตรวจสอบการแจ้งเตือนความคืบหน้า และคู่มือการแยกขยะ
    # =========================================================================
    notif_res = client.get(f"/api/v1/sellers/{seller_id}/notifications")
    assert notif_res.status_code == 200

    guides_res = client.get("/api/v1/help/sorting-guides")
    assert guides_res.status_code == 200
    assert len(guides_res.json()["guides"]) >= 1

    # =========================================================================
    # ตรวจสอบความสมบูรณ์ของ Audit Trail (CC-04, REQ-SEC-001)
    # =========================================================================
    audit_actions = [l["action"] for l in supabase_store.audit_logs if l.get("entity_id") == order_id]
    assert "ORDER_SUBMITTED" in audit_actions
    assert "SELLER_PAYMENT_CONFIRMED" in audit_actions
