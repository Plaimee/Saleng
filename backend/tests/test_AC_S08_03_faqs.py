"""
Automated Backend Tests สำหรับ AC-S08-03: Categorized FAQ Knowledge Base with Search
รองรับ UC-08, CC-05, REQ-OP-001, AC-S08-03, P-03, Q-03
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_get_faqs_categorized():
    """
    AC-S08-03 / Q-03: ตรวจสอบการดึงข้อมูลคำถามที่พบบ่อย (FAQ) แยกตาม 3 หมวดหมู่หลัก
    """
    response = client.get("/api/v1/help/faqs")
    assert response.status_code == 200
    data = response.json()

    assert data["total_faqs"] >= 8
    categories = data["categories"]
    assert len(categories) == 3

    cat_ids = [c["category_id"] for c in categories]
    assert "MINIMUM_AND_BOOKING" in cat_ids
    assert "WEIGHING_AND_PRICING" in cat_ids
    assert "PAYMENT_AND_RECEIPT" in cat_ids


def test_search_faqs_with_keyword():
    """
    AC-S08-03: ตรวจสอบการค้นหา FAQ ด้วยคำสำคัญ (Search Query)
    """
    # 1. ค้นหาคำว่า "500 บาท"
    resp1 = client.get("/api/v1/help/faqs?query=500 บาท")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["total_faqs"] >= 1
    all_faqs1 = [f for c in data1["categories"] for f in c["faqs"]]
    assert any("500 บาท" in f["question"] or "500 บาท" in f["answer"] for f in all_faqs1)

    # 2. ค้นหาคำว่า "ตาชั่ง"
    resp2 = client.get("/api/v1/help/faqs?query=ตาชั่ง")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["total_faqs"] >= 1

    # 3. ค้นหาคำที่ไม่พบ
    resp3 = client.get("/api/v1/help/faqs?query=คำที่ไม่มีอยู่ในระบบแน่นอน12345")
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["total_faqs"] == 0
    assert data3["categories"] == []

