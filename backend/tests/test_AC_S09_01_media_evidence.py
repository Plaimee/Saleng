"""
Automated Backend Tests สำหรับ AC-S09-01: In-Transaction Audio/Video Evidence Recording
รองรับ UC-09, AC-S09-01, P-01, REQ-SEC-001, CC-01, Q-01
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_upload_evidence_success_in_valid_status():
    """
    AC-S09-01:
    1. ผู้ขายสามารถบันทึก/อัปโหลดไฟล์หลักฐานเสียงในสถานะ S5
    2. ได้รับรหัสหลักฐาน EVD-YYYYMMDD-XXXX
    3. ตรวจสอบการบันทึก Audit Log SELLER_STOP_EVIDENCE_RECORDING
    4. สามารถเรียกดูรายการหลักฐานของคำขอได้
    """
    seller_id = "SELLER-AC09-01"
    order_id = "ORDER-AC09-S5-VALID"

    # จำลองคำขอในสถานะ S5 (กำลังชั่งของหน้างาน)
    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S5",
    }

    payload = {
        "media_type": "AUDIO",
        "duration_seconds": 65,
        "file_size_bytes": 1024 * 1024 * 2,  # 2 MB
        "file_url": "https://storage.saleng.app/evidences/audio-rec-01.webm",
    }

    response = client.post(
        f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}",
        json=payload
    )
    assert response.status_code == 201
    data = response.json()

    assert data["order_id"] == order_id
    assert data["seller_id"] == seller_id
    assert data["media_type"] == "AUDIO"
    assert data["evidence_id"].startswith("EVD-")
    assert data["duration_seconds"] == 65
    assert data["is_locked"] is False

    # ดึงรายการหลักฐานของคำขอ
    list_resp = client.get(f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total_evidences"] >= 1
    assert any(e["evidence_id"] == data["evidence_id"] for e in list_data["evidences"])

    # ตรวจสอบ Audit Log (REQ-SEC-001, AC-S09-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_STOP_EVIDENCE_RECORDING" and l["entity_id"] == data["evidence_id"]
    ]
    assert len(logs) >= 1
    assert logs[-1]["details"]["duration_seconds"] == 65


def test_upload_evidence_blocked_in_invalid_status():
    """
    AC-S09-01: ไม่อนุญาตให้อัดเสียง/วิดีโอในสถานะที่ไม่ใช่หน้างาน (เช่น S1 หรือ S7)
    """
    seller_id = "SELLER-AC09-INVALID"
    order_id = "ORDER-AC09-S1-POSTED"

    supabase_store.orders[order_id] = {
        "order_id": order_id,
        "seller_id": seller_id,
        "status": "S1",  # ยังไม่มีซาเล้งรับงาน
    }

    payload = {
        "media_type": "AUDIO",
        "duration_seconds": 30,
        "file_size_bytes": 1024 * 500,
    }

    response = client.post(
        f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}",
        json=payload
    )
    assert response.status_code == 400
    assert "สามารถบันทึกหลักฐานได้เฉพาะขณะซาเล้งปฏิบัติงานหน้างาน" in response.json()["detail"]


def test_upload_evidence_file_size_exceeded():
    """
    CC-01: ขนาดไฟล์หลักฐานต้องไม่เกิน 25 MB
    """
    seller_id = "SELLER-AC09-01"
    order_id = "ORDER-AC09-S5-VALID"

    payload = {
        "media_type": "VIDEO",
        "duration_seconds": 120,
        "file_size_bytes": 30 * 1024 * 1024,  # 30 MB
    }

    response = client.post(
        f"/api/v1/orders/{order_id}/safety/evidence?seller_id={seller_id}",
        json=payload
    )
    # Validation error จาก Pydantic
    assert response.status_code in [400, 422]

