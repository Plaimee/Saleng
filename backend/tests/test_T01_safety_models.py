"""
Unit Tests สำหรับ T-01: Data Models & Supabase Store ระบบความปลอดภัยและ SOS
รองรับ UC-09, UC-13, REQ-SEC-002, CC-04, P-01..P-04
"""

import pytest
from pydantic import ValidationError
from backend.app.models.safety_models import (
    EvidenceUploadRequest,
    EvidenceItemResponse,
    EvidenceListResponse,
    EmergencyContactUpdateRequest,
    EmergencyContactResponse,
    SosTriggerRequest,
    SosAlertResponse,
    LockEvidenceResponse,
)
from backend.app.core.supabase import supabase_store


def test_evidence_models_validation():
    """ตรวจสอบการทำงานของ Evidence Models และเกณฑ์ขนาดไฟล์ <= 25MB (CC-01)"""
    valid_req = EvidenceUploadRequest(
        media_type="AUDIO",
        duration_seconds=120,
        file_size_bytes=5 * 1024 * 1024,
        file_url="data:audio/webm;base64,GkXfo59ChoEBQveBAULygQ8USAElBA=="
    )
    assert valid_req.media_type == "AUDIO"
    assert valid_req.duration_seconds == 120

    # ตรวจสอบขนาดไฟล์เกิน 25 MB ต้องยกเลิกด้วย ValidationError
    with pytest.raises(ValidationError):
        EvidenceUploadRequest(
            media_type="VIDEO",
            duration_seconds=60,
            file_size_bytes=26 * 1024 * 1024,  # เกิน 25 MB
        )

    # ตรวจสอบความยาวเกิน 15 นาที (900 วินาที)
    with pytest.raises(ValidationError):
        EvidenceUploadRequest(
            media_type="AUDIO",
            duration_seconds=901,
            file_size_bytes=1024,
        )


def test_emergency_contact_models_validation():
    """ตรวจสอบ Emergency Contact Models และการตรวจสอบรูปแบบเบอร์โทรศัพท์"""
    valid_contact = EmergencyContactUpdateRequest(
        contact_name="นายสมศักดิ์ มีสุข (บุตรชาย)",
        relationship="บุตร",
        contact_phone="0819998877",
    )
    assert valid_contact.contact_phone == "0819998877"

    # เบอร์โทรศัพท์ผิดรูปแบบ (ต้องขึ้นต้นด้วย 0 และยาว 9-10 หลัก)
    with pytest.raises(ValidationError):
        EmergencyContactUpdateRequest(
            contact_name="ญาติ",
            relationship="ญาติ",
            contact_phone="12345",
        )


def test_supabase_store_safety_operations():
    """ตรวจสอบ Store Operations สำหรับ Evidence, Contact, และ SOS"""
    order_id = "ORDER-TEST-T01-SAFETY"
    seller_id = "SELLER-TEST-T01"

    # 1. Evidence Store
    ev = supabase_store.add_safety_evidence({
        "evidence_id": "EVD-20261103-T001",
        "order_id": order_id,
        "seller_id": seller_id,
        "media_type": "AUDIO",
        "file_url": "https://example.com/audio1.webm",
        "file_size_bytes": 10240,
        "duration_seconds": 30,
        "is_locked": False,
    })
    assert ev["evidence_id"] == "EVD-20261103-T001"
    assert ev["is_locked"] is False

    ev_list = supabase_store.get_safety_evidences_by_order(order_id)
    assert len(ev_list) >= 1

    # 2. Lock Evidence
    locked_count = supabase_store.lock_safety_evidences_for_order(order_id)
    assert locked_count >= 1
    ev_locked = supabase_store.get_safety_evidences_by_order(order_id)
    assert ev_locked[0]["is_locked"] is True

    # 3. Emergency Contact Store
    contact = supabase_store.upsert_emergency_contact({
        "seller_id": seller_id,
        "contact_name": "นางสมพร (ภรรยา)",
        "relationship": "ภรรยา",
        "contact_phone": "0898887766",
    })
    assert contact["seller_id"] == seller_id

    fetched_contact = supabase_store.get_emergency_contact(seller_id)
    assert fetched_contact is not None
    assert fetched_contact["contact_name"] == "นางสมพร (ภรรยา)"

    # 4. SOS Alert Store
    alert = supabase_store.create_sos_alert({
        "sos_id": "SOS-20261103-T001",
        "order_id": order_id,
        "seller_id": seller_id,
        "saleng_id": "SALENG-T01",
        "geo_point": {"lat": 13.7563, "lng": 100.5018},
        "status": "TRIGGERED",
    })
    assert alert["sos_id"] == "SOS-20261103-T001"
    alerts = supabase_store.get_sos_alerts_by_order(order_id)
    assert len(alerts) >= 1

