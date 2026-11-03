"""
End-to-End Integration Test สำหรับ Seller Feature 09: ระบบความปลอดภัยขณะทำธุรกรรม (Transaction Safety & SOS)
รองรับ Use Case UC-09, UC-13, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-001, REQ-FN-006, CC-01, AC-S09-01..05, P-01..P-06
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_transaction_safety_lifecycle():
    """
    ทดสอบครบวงจรระบบความปลอดภัยขณะทำธุรกรรม (End-to-End):
    1. ผู้ขายตั้งค่าเบอร์ผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (AC-S09-03, REQ-SEC-002)
    2. มีคำขอที่ซาเล้งเดินทางมาถึงหน้างาน (สถานะ S4) และเข้าสู่ช่วงชั่งของ (สถานะ S5)
    3. ผู้ขายกดเริ่มและหยุดบันทึกเสียงหลักฐานหน้างาน (AC-S09-01, P-01)
    4. ผู้ขายกดปุ่ม SOS ฉุกเฉิน One-Tap Trigger -> ระบบส่งสัญญาณและพิกัดเข้าศูนย์ Admin ใน < 2 วินาที (AC-S09-02, REQ-QA-001)
    5. ตรวจสอบว่าหลักฐานในคำขอนั้นถูกล็อกสถานะเป็น Read-only ทันที (AC-S09-04, REQ-FN-006)
    6. ทดสอบการสั่งล็อกหลักฐานผ่าน API ล็อกข้อพิพาทโดยตรง (AC-S09-04)
    7. ตรวจสอบความครบถ้วนของ Audit Logs ทุกเหตุการณ์ด้านความปลอดภัย (AC-S09-05, REQ-SEC-001)
    """
    seller_id = "SELLER-E2E-S09"
    collector_id = "COLLECTOR-E2E-BOONMEE"
    order_id = "ORDER-E2E-SAFETY-01"

    # -------------------------------------------------------------------------
    # 1. ผู้ขายตั้งค่าเบอร์ผู้ติดต่อฉุกเฉิน (AC-S09-03, REQ-SEC-002)
    # -------------------------------------------------------------------------
    contact_payload = {
        "contact_name": "นายสมเกียรติ มั่นคง (บุตรชาย)",
        "relationship": "บุตรชาย",
        "contact_phone": "0819876543",
    }
    res_contact = client.put(f"/api/v1/sellers/{seller_id}/safety/emergency-contact", json=contact_payload)
    assert res_contact.status_code == 200
    contact_data = res_contact.json()
    assert contact_data["contact_name"] == "นายสมเกียรติ มั่นคง (บุตรชาย)"
    assert contact_data["contact_phone_masked"] == "08X-XXX-6543"
    assert "0819876543" not in res_contact.text

    # -------------------------------------------------------------------------
    # 2. จำลองคำขอในสถานะ S5 (ซาเล้งกำลังชั่งของหน้างาน)
    # -------------------------------------------------------------------------
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "collector_id": collector_id,
        "status": "S5",
        "created_at": "2026-11-03T20:00:00Z",
    }

    # -------------------------------------------------------------------------
    # 3. ผู้ขายบันทึกเสียงหลักฐานหน้างาน (AC-S09-01, P-01)
    # -------------------------------------------------------------------------
    evidence_payload = {
        "media_type": "AUDIO",
        "duration_seconds": 55,
        "file_size_bytes": 1024 * 1024 * 1,  # 1 MB
        "file_url": "https://storage.saleng.app/evidences/order-safety-01.webm",
    }
    res_ev = client.post(
        f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}",
        json=evidence_payload
    )
    assert res_ev.status_code == 201
    ev_data = res_ev.json()
    assert ev_data["evidence_id"].startswith("EVD-")
    assert ev_data["media_type"] == "AUDIO"
    assert ev_data["duration_seconds"] == 55
    assert ev_data["is_locked"] is False

    # -------------------------------------------------------------------------
    # 4. ผู้ขายกดปุ่ม SOS ฉุกเฉิน (AC-S09-02, REQ-QA-001, P-02)
    # -------------------------------------------------------------------------
    sos_payload = {
        "current_lat": 13.7563,
        "current_lng": 100.5018,
        "notes": "แจ้งเหตุฉุกเฉินขณะชั่งของ",
    }
    res_sos = client.post(
        f"/api/v1/orders/{order_id}/safety/sos?seller_id={seller_id}",
        json=sos_payload
    )
    assert res_sos.status_code == 200
    sos_data = res_sos.json()
    assert sos_data["sos_id"].startswith("SOS-")
    assert sos_data["order_id"] == order_id
    assert sos_data["saleng_id"] == collector_id
    assert sos_data["status"] == "TRIGGERED"
    assert sos_data["response_time_ms"] < 2000.0  # REQ-QA-001
    assert sos_data["emergency_phone_to_call"] == "0819876543"  # เบอร์โทรออกด่วน
    assert sos_data["emergency_contact_name"] == "นายสมเกียรติ มั่นคง (บุตรชาย)"

    # -------------------------------------------------------------------------
    # 5. ตรวจสอบว่าหลักฐานถูกล็อกอัตโนมัติเมื่อกด SOS (AC-S09-04, REQ-FN-006)
    # -------------------------------------------------------------------------
    res_list_after_sos = client.get(f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}")
    assert res_list_after_sos.status_code == 200
    list_data = res_list_after_sos.json()
    assert len(list_data["evidences"]) >= 1
    assert all(e["is_locked"] is True for e in list_data["evidences"])

    # -------------------------------------------------------------------------
    # 6. ทดสอบการสั่งล็อกหลักฐานผ่าน API lock-evidence (AC-S09-04)
    # -------------------------------------------------------------------------
    res_lock = client.patch(f"/api/v1/orders/{order_id}/safety/lock-evidence?actor_id={seller_id}")
    assert res_lock.status_code == 200
    lock_data = res_lock.json()
    assert lock_data["is_locked"] is True
    assert lock_data["locked_count"] >= 1

    # -------------------------------------------------------------------------
    # 7. ตรวจสอบความครบถ้วนของ Audit Logs (AC-S09-05, REQ-SEC-001)
    # -------------------------------------------------------------------------
    actions_recorded = [
        l["action"] for l in supabase_store.audit_logs
        if l.get("actor_id") == seller_id
    ]
    assert "SELLER_UPDATE_EMERGENCY_CONTACT" in actions_recorded
    assert "SELLER_STOP_EVIDENCE_RECORDING" in actions_recorded
    assert "SELLER_TRIGGER_SOS" in actions_recorded
    assert "SYSTEM_LOCK_EVIDENCE" in actions_recorded

