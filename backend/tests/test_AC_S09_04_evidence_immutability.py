"""
Automated Backend Tests สำหรับ AC-S09-04: Evidence Immutability on Dispute / SOS
รองรับ REQ-FN-006, UC-13, AC-S09-04, P-04, REQ-SEC-001, Q-04
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_lock_evidence_on_dispute_or_sos():
    """
    AC-S09-04 / REQ-FN-006:
    1. สร้างคำขอและเพิ่มหลักฐาน 2 รายการ (is_locked=False)
    2. เรียก API lock-evidence (จำลองการเกิดข้อพิพาท S8 หรือกด SOS)
    3. ตรวจสอบหลักฐานทั้งหมดถูกเปลี่ยนเป็น is_locked=True
    4. ตรวจสอบ Audit Log SYSTEM_LOCK_EVIDENCE
    """
    seller_id = "SELLER-LOCK-AC04"
    order_id = "ORDER-LOCK-DISPUTE-01"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S5",
    }

    # เพิ่มหลักฐาน 2 รายการ
    supabase_store.add_safety_evidence({
        "evidence_id": "EVD-20261103-L001",
        "order_id": order_id,
        "seller_id": seller_id,
        "media_type": "AUDIO",
        "file_url": "https://storage.saleng.app/evidences/audio1.webm",
        "file_size_bytes": 1024,
        "duration_seconds": 15,
        "is_locked": False,
    })
    supabase_store.add_safety_evidence({
        "evidence_id": "EVD-20261103-L002",
        "order_id": order_id,
        "seller_id": seller_id,
        "media_type": "VIDEO",
        "file_url": "https://storage.saleng.app/evidences/video1.webm",
        "file_size_bytes": 2048,
        "duration_seconds": 30,
        "is_locked": False,
    })

    # ก่อนล็อก
    ev_before = client.get(f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}").json()
    assert all(e["is_locked"] is False for e in ev_before["evidences"])

    # สั่งล็อกหลักฐาน
    lock_resp = client.patch(f"/api/v1/orders/{order_id}/safety/lock-evidence?actor_id={seller_id}")
    assert lock_resp.status_code == 200
    lock_data = lock_resp.json()
    assert lock_data["locked_count"] == 2
    assert lock_data["is_locked"] is True

    # หลังล็อก
    ev_after = client.get(f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}").json()
    assert all(e["is_locked"] is True for e in ev_after["evidences"])

    # ตรวจสอบ Audit Log (REQ-SEC-001, AC-S09-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SYSTEM_LOCK_EVIDENCE" and l["entity_id"] == order_id
    ]
    assert len(logs) >= 1
    assert logs[-1]["details"]["locked_count"] == 2

