"""
Backend API Tests สำหรับ AC-S03-04: Direct Contact with PDPA Masking
รองรับ UC-03, REQ-SEC-002, CC-06, AC-S03-04, P-04, Q-04
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_S03_04_direct_contact_phone_and_pdpa_protection():
    """
    ทดสอบว่ามีเบอร์โทรซาเล้งสำหรับ Native Dialer
    และตรวจสอบว่า API ไม่เปิดเผยบ้านเลขที่จริงและพิกัดละเอียดของผู้ขาย
    """
    response = client.get("/api/v1/buyer-search/collectors?seller_id=seller-01")
    assert response.status_code == 200
    collectors = response.json()["collectors"]

    for c in collectors:
        # มีเบอร์โทรของซาเล้งสำหรับโทรด่วน
        assert "phone" in c
        assert len(c["phone"]) > 0

        # ห้ามมีฟิลด์ข้อมูลส่วนบุคคลของผู้ขายหลุดออกมาในผลการค้นหาซาเล้ง
        assert "seller_address_text" not in c
        assert "seller_exact_coords" not in c
        assert "seller_phone" not in c

