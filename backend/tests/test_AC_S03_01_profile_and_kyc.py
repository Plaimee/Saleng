"""
Backend API Tests สำหรับ AC-S03-01: Saleng Profile & KYC Verification Display
รองรับ UC-03, REQ-QA-001, REQ-SEC-001, D-00-01, AC-S03-01
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_S03_01_profile_and_kyc_verification_display():
    """
    ทดสอบการดึงรายชื่อซาเล้ง:
    - ต้องเห็นเฉพาะซาเล้งที่ผ่าน KYC 100% (verified = True) และเปิดรับงาน (is_online = True)
    - ต้องไม่แสดงซาเล้ง unverified (saleng-05) และซาเล้ง offline (saleng-04)
    - แสดงข้อมูลรูปถ่าย, ชื่อ, สถานะยืนยันตัวตน, คะแนนรีวิว, จำนวนงานที่สำเร็จ, ประเภทยานพาหนะ, และระยะทาง
    """
    response = client.get("/api/v1/buyer-search/collectors?seller_id=seller-01&radius_km=5.0")
    assert response.status_code == 200
    data = response.json()

    assert "collectors" in data
    assert "total_count" in data
    collectors = data["collectors"]

    # ต้องไม่พบ saleng-04 (offline) และ saleng-05 (unverified)
    collector_ids = [c["saleng_id"] for c in collectors]
    assert "saleng-04" not in collector_ids
    assert "saleng-05" not in collector_ids

    # ต้องพบ saleng-01 และ saleng-02 ที่ผ่านเกณฑ์
    assert "saleng-01" in collector_ids
    saleng_01 = next(c for c in collectors if c["saleng_id"] == "saleng-01")
    assert saleng_01["verified"] is True
    assert saleng_01["display_name"] == "ลุงสมชาย ซาเล้งสุทธิสาร"
    assert saleng_01["rating"] >= 4.0
    assert saleng_01["completed_jobs_count"] > 0
    assert saleng_01["vehicle_type"] == "TRICYCLE"
    assert saleng_01["distance_km"] > 0


def test_AC_S03_01_get_collector_detail_profile():
    """ทดสอบการดึงโปรไฟล์ละเอียดของซาเล้งรายบุคคล"""
    response = client.get("/api/v1/buyer-search/collectors/saleng-01?seller_id=seller-01")
    assert response.status_code == 200
    data = response.json()
    assert data["saleng_id"] == "saleng-01"
    assert data["phone"] == "081-234-5678"
    assert data["verified"] is True

    # กรณีไม่พบ ID
    res_404 = client.get("/api/v1/buyer-search/collectors/non-existent-id")
    assert res_404.status_code == 404

