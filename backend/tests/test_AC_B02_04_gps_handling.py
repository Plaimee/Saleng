"""
Acceptance Tests for AC-B02-04: GPS Disabled or Denied Handling
(Task T-04: UC-04, REQ-OP-002, AC-04-09, CC-02, E1)
"""

from starlette.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_B02_04_missing_gps_coordinates_rejected():
    """
    Given: ซาเล้งปิด GPS หรือเบราว์เซอร์ปฏิเสธ Permission
    When: ซาเล้งเรียก GET /api/v1/collectors/jobs/nearby โดยไม่มีพิกัด saleng_lat / saleng_lng
    Then: ระบบต้องตอบกลับ HTTP 400 Bad Request
    And: มีข้อความเตือนชัดเจนให้เปิดใช้งาน GPS ไม่นำพิกัดเก่าหมดอายุมาใช้
    """
    # 1. ไม่ส่งพิกัดใด ๆ
    resp_no_gps = client.get("/api/v1/collectors/jobs/nearby")
    assert resp_no_gps.status_code == 400
    assert "กรุณาเปิด GPS เพื่อค้นหางานใกล้เคียง" in resp_no_gps.json()["detail"]

    # 2. ส่งเฉพาะ lat ไม่ส่ง lng
    resp_partial = client.get("/api/v1/collectors/jobs/nearby", params={"saleng_lat": 13.7900})
    assert resp_partial.status_code == 400
    assert "กรุณาเปิด GPS" in resp_partial.json()["detail"]


def test_AC_B02_04_invalid_gps_coordinates_rejected():
    """
    Given: พิกัด GPS ผิดพลาด หรือส่งค่าที่ไม่สมเหตุสมผล (เช่น ละติจูดเกิน 90 องศา หรือ 0.0, 0.0)
    When: ซาเล้งเรียก GET /api/v1/collectors/jobs/nearby
    Then: ระบบต้องปฏิเสธด้วย HTTP 400 Bad Request
    """
    # 1. พิกัด Lat นอกช่วง
    resp_out_of_bound = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": 150.0, "saleng_lng": 100.5750},
    )
    assert resp_out_of_bound.status_code == 400
    assert "พิกัด GPS ไม่อยู่ในช่วงที่ถูกต้อง" in resp_out_of_bound.json()["detail"]

    # 2. พิกัด Null Island (0.0, 0.0)
    resp_zero = client.get(
        "/api/v1/collectors/jobs/nearby",
        params={"saleng_lat": 0.0, "saleng_lng": 0.0},
    )
    assert resp_zero.status_code == 400
    assert "พิกัด GPS เป็น 0.0" in resp_zero.json()["detail"]

