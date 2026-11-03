"""
Automated Backend Tests สำหรับ AC-S09-03: Trusted Emergency Contact Management & Masking
รองรับ UC-09, REQ-SEC-002, REQ-SEC-001, AC-S09-03, P-03, Q-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_emergency_contact_crud_and_pii_masking():
    """
    AC-S09-03 / REQ-SEC-002:
    1. ดึงข้อมูลครั้งแรกเมื่อยังไม่ได้ตั้งค่า -> ได้รับค่า Default เป็น Saleng Hotline
    2. บันทึกข้อมูลผู้ติดต่อฉุกเฉินใหม่ -> เบอร์โทรศัพท์ถูก Mask เป็น 08X-XXX-XXXX
    3. ดึงข้อมูลอีกครั้ง -> ได้รับข้อมูลที่อัปเดตและเบอร์ถูก Mask PII
    4. ตรวจสอบ Audit Log SELLER_UPDATE_EMERGENCY_CONTACT
    """
    seller_id = "SELLER-CONTACT-AC03"

    # 1. ดึงครั้งแรกเมื่อยังไม่ได้ตั้งค่า
    resp1 = client.get(f"/api/v1/sellers/{seller_id}/safety/emergency-contact")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["is_default"] is True
    assert data1["contact_phone_masked"] == "02-123-4567"

    # 2. บันทึกข้อมูลผู้ติดต่อฉุกเฉินใหม่
    payload = {
        "contact_name": "นายสมพร สุขเกษม (สามี)",
        "relationship": "สามี",
        "contact_phone": "0812345678",
    }
    resp2 = client.put(f"/api/v1/sellers/{seller_id}/safety/emergency-contact", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()

    assert data2["contact_name"] == "นายสมพร สุขเกษม (สามี)"
    assert data2["relationship"] == "สามี"
    assert data2["is_default"] is False

    # REQ-SEC-002: ตรวจสอบ PII Masking
    assert data2["contact_phone_masked"] == "08X-XXX-5678"
    assert "0812345678" not in resp2.text

    # 3. ดึงข้อมูลอีกครั้ง
    resp3 = client.get(f"/api/v1/sellers/{seller_id}/safety/emergency-contact")
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["contact_name"] == "นายสมพร สุขเกษม (สามี)"
    assert data3["contact_phone_masked"] == "08X-XXX-5678"

    # 4. ตรวจสอบ Audit Log (REQ-SEC-001, AC-S09-05)
    logs = [
        l for l in supabase_store.audit_logs
        if l["action"] == "SELLER_UPDATE_EMERGENCY_CONTACT" and l["entity_id"] == seller_id
    ]
    assert len(logs) >= 1
    assert logs[-1]["details"]["masked_phone"] == "08X-XXX-5678"

