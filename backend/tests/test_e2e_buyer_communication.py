"""
Integration E2E Lifecycle Test Suite for Buyer Communication System
(Task T-08: UC-08, REQ-SEC-001, REQ-SEC-002, REQ-UX-001, CC-01..06, AC-B05-01..06, D-B05-01..06)
"""

import pytest
from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_e2e_environment():
    """เตรียมข้อมูลสภาพแวดล้อม E2E สำหรับคำขอขายตลอด Lifecycle S2 -> S3 -> S4 -> S7"""
    order_id = "order-e2e-comm"
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": "seller-e2e",
        "collector_id": None,
        "assigned_saleng_id": None,
        "status": "S2",
        "location_id": "loc-01",
        "version": 1,
    }

    supabase_store.sellers["seller-e2e"] = {
        "seller_id": "seller-e2e",
        "display_name": "คุณวิภาดา รัชดา",
        "phone": "081-888-9999",
    }

    orig_profile = dict(supabase_store.saleng_profiles.get("saleng-01", {}))
    supabase_store.saleng_profiles["saleng-01"].update({
        "verified": True,
        "kyc_status": "VERIFIED",
        "is_online": True,
    })

    supabase_store.saleng_profiles["saleng-unverified"] = {
        "saleng_id": "saleng-unverified",
        "display_name": "ซาเล้งใหม่ยังไม่ยืนยัน",
        "phone": "089-000-0000",
        "verified": False,
        "kyc_status": "PENDING",
        "vehicle_type": "TRICYCLE",
        "current_lat": 13.7900,
        "current_lng": 100.5750,
        "is_online": True,
    }

    # ล้างข้อความเก่า
    supabase_store.chat_messages = [
        m for m in supabase_store.chat_messages if m.get("order_id") != order_id
    ]

    yield

    supabase_store.orders.pop(order_id, None)
    supabase_store.sellers.pop("seller-e2e", None)
    supabase_store.saleng_profiles.pop("saleng-unverified", None)
    if orig_profile:
        supabase_store.saleng_profiles["saleng-01"] = orig_profile
    supabase_store.chat_messages = [
        m for m in supabase_store.chat_messages if m.get("order_id") != order_id
    ]


def test_e2e_communication_full_lifecycle():
    """
    ทดสอบครบวงจร E2E ระบบสื่อสาร:
    1. สถานะ S2: แชตสอบถามได้, เบอร์โทรศัพท์ถูก Mask, บล็อกการโทร
    2. สถานะ S3: เปิดเผยเบอร์โทรศัพท์จริง, ส่งข้อความด่วนได้, โทรด่วนพร้อมบันทึก Audit Log
    3. สถานะ S4: ซาเล้งส่งข้อความแจ้งเตือนกำลังถึง
    4. สถานะ S7: ใบงานเสร็จสิ้น ห้องแชตล็อก Read-only, บล็อกการส่งข้อความ, บล็อกการโทร, ซ่อนเบอร์โทรศัพท์
    """
    order_id = "order-e2e-comm"

    # ========================================================
    # ขั้นที่ 1: สถานะ S2 (Direct Request / รอรับงาน)
    # ========================================================
    # 1.1 ตรวจสอบห้องแชตใน S2
    room_resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert room_resp.status_code == 200
    room_data = room_resp.json()
    assert room_data["order_status"] == "S2"
    assert room_data["is_read_only"] is False
    assert room_data["seller_info"]["phone"] is None
    assert room_data["seller_info"]["phone_masked"] is True

    # 1.2 โทรด่วนใน S2 ต้องถูกบล็อกด้วย 403 (AC-B05-04)
    call_blocked_resp = client.post(
        f"/api/v1/collectors/chat/{order_id}/call-log",
        json={"saleng_id": "saleng-01", "dialed_phone": "081-888-9999"},
    )
    assert call_blocked_resp.status_code == 403

    # 1.3 ส่งข้อความสอบถามใน S2 ได้ (D-B05-01)
    msg_s2_resp = client.post(
        f"/api/v1/collectors/chat/{order_id}/messages",
        json={
            "saleng_id": "saleng-01",
            "message_text": "สวัสดีครับคุณวิภาดา สะดวกช่วงบ่ายไหมครับ",
            "is_quick_reply": False,
        },
    )
    assert msg_s2_resp.status_code == 201

    # ========================================================
    # ขั้นที่ 2: เปลี่ยนสถานะเป็น S3 (รับงานแล้ว)
    # ========================================================
    supabase_store.orders[order_id]["status"] = "S3"
    supabase_store.orders[order_id]["collector_id"] = "saleng-01"

    # 2.1 ตรวจสอบห้องแชตใน S3: เบอร์โทรศัพท์เปิดเผยแล้ว (AC-B05-03)
    room_s3_resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert room_s3_resp.status_code == 200
    room_s3_data = room_s3_resp.json()
    assert room_s3_data["order_status"] == "S3"
    assert room_s3_data["seller_info"]["phone"] == "081-888-9999"
    assert room_s3_data["seller_info"]["phone_masked"] is False

    # 2.2 ส่ง Quick Reply (AC-B05-02)
    qr_resp = client.post(
        f"/api/v1/collectors/chat/{order_id}/messages",
        json={
            "saleng_id": "saleng-01",
            "message_text": "กำลังเดินทางไปครับ",
            "is_quick_reply": True,
        },
    )
    assert qr_resp.status_code == 201
    assert qr_resp.json()["message"]["is_quick_reply"] is True

    # 2.3 กดโทรด่วนใน S3 สำเร็จ และบันทึก Audit Log (AC-B05-03, REQ-SEC-001)
    call_resp = client.post(
        f"/api/v1/collectors/chat/{order_id}/call-log",
        json={"saleng_id": "saleng-01", "dialed_phone": "081-888-9999"},
    )
    assert call_resp.status_code == 200
    assert call_resp.json()["action"] == "COLLECTOR_INITIATED_CALL"

    # ========================================================
    # ขั้นที่ 3: เปลี่ยนสถานะเป็น S4 (กำลังเดินทาง)
    # ========================================================
    supabase_store.orders[order_id]["status"] = "S4"

    # ส่งข้อความถึงหน้าบ้านแล้ว
    arrive_resp = client.post(
        f"/api/v1/collectors/chat/{order_id}/messages",
        json={
            "saleng_id": "saleng-01",
            "message_text": "ถึงหน้าบ้านแล้วครับ",
            "is_quick_reply": True,
        },
    )
    assert arrive_resp.status_code == 201

    # ========================================================
    # ขั้นที่ 4: เปลี่ยนสถานะเป็น S7 (เสร็จสิ้น / ปิดงาน)
    # ========================================================
    supabase_store.orders[order_id]["status"] = "S7"

    # 4.1 ห้องแชตล็อก Read-only และซ่อนเบอร์โทรศัพท์ (AC-B05-05, D-B05-05)
    room_s7_resp = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id=saleng-01")
    assert room_s7_resp.status_code == 200
    room_s7_data = room_s7_resp.json()
    assert room_s7_data["is_read_only"] is True
    assert "PDPA" in room_s7_data["read_only_reason"]
    assert room_s7_data["seller_info"]["phone"] is None
    assert room_s7_data["seller_info"]["phone_masked"] is True

    # 4.2 พยายามส่งข้อความใหม่ใน S7 ต้องถูกบล็อกด้วย 403
    blocked_msg = client.post(
        f"/api/v1/collectors/chat/{order_id}/messages",
        json={
            "saleng_id": "saleng-01",
            "message_text": "ขอบคุณครับ",
            "is_quick_reply": False,
        },
    )
    assert blocked_msg.status_code == 403

    # 4.3 พยายามโทรออกใน S7 ต้องถูกบล็อกด้วย 403
    blocked_call = client.post(
        f"/api/v1/collectors/chat/{order_id}/call-log",
        json={"saleng_id": "saleng-01", "dialed_phone": "081-888-9999"},
    )
    assert blocked_call.status_code == 403


def test_e2e_kyc_security_guard():
    """
    ทดสอบว่าผู้ที่ยังไม่ผ่าน KYC ไม่สามารถเข้าถึงหรือส่งข้อความในระบบสื่อสารได้ (D-00-01)
    """
    order_id = "order-e2e-comm"
    unverified_id = "saleng-unverified"

    # เข้าห้องแชตโดน 403
    resp_room = client.get(f"/api/v1/collectors/chat/{order_id}/messages?saleng_id={unverified_id}")
    assert resp_room.status_code == 403
    assert "KYC" in resp_room.json()["detail"]

    # ส่งข้อความโดน 403
    resp_send = client.post(
        f"/api/v1/collectors/chat/{order_id}/messages",
        json={
            "saleng_id": unverified_id,
            "message_text": "ฮัลโหล",
        },
    )
    assert resp_send.status_code == 403
    assert "KYC" in resp_send.json()["detail"]
