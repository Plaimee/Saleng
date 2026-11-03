"""
Backend API Tests สำหรับ AC-S03-02: Top Pinning for Previous Collectors
รองรับ UC-03, REQ-UX-001, AC-S03-02, Q-02, P-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_AC_S03_02_top_pinning_for_previous_collectors():
    """
    ทดสอบว่าซาเล้งที่เป็น 'คนโปรด / เคยใช้บริการ' จะถูกตรึง (Pinned) ไว้บนสุดเสมอ
    แม้จะมีคนอื่นอยู่ใกล้กว่า
    """
    # ตรวจสอบว่า seller-01 มี saleng-01 เป็น Favorite อยู่แล้ว
    response = client.get("/api/v1/buyer-search/collectors?seller_id=seller-01")
    assert response.status_code == 200
    collectors = response.json()["collectors"]

    assert len(collectors) >= 2
    # คนแรกสุดต้องเป็น saleng-01 ซึ่งมี is_favorite = True
    assert collectors[0]["saleng_id"] == "saleng-01"
    assert collectors[0]["is_favorite"] is True


def test_AC_S03_02_favorites_toggle_and_list():
    """
    ทดสอบการดึงรายการโปรด และการเปิด/ปิดบันทึกคนโปรด
    """
    seller_id = "seller-test-fav"
    # ตอนแรกยังไม่มีคนโปรด
    res_list = client.get(f"/api/v1/buyer-search/favorites?seller_id={seller_id}")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 0

    # บันทึก saleng-02 เป็นคนโปรด
    res_toggle_on = client.post(
        f"/api/v1/buyer-search/favorites/saleng-02/toggle?seller_id={seller_id}"
    )
    assert res_toggle_on.status_code == 200
    assert res_toggle_on.json()["is_favorite"] is True

    # ตรวจสอบรายการโปรดอีกครั้ง
    res_list2 = client.get(f"/api/v1/buyer-search/favorites?seller_id={seller_id}")
    assert len(res_list2.json()) == 1
    assert res_list2.json()[0]["saleng_id"] == "saleng-02"

    # กดยกเลิกคนโปรด
    res_toggle_off = client.post(
        f"/api/v1/buyer-search/favorites/saleng-02/toggle?seller_id={seller_id}"
    )
    assert res_toggle_off.status_code == 200
    assert res_toggle_off.json()["is_favorite"] is False

