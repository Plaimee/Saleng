"""
Automated Backend Tests สำหรับ AC-S08-02: Waste Sorting & Value-Add Guide
รองรับ UC-08, CC-05, REQ-OP-001, AC-S08-02, P-02, Q-02
"""

from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_get_sorting_guides():
    """
    AC-S08-02 / Q-02: ตรวจสอบการดึงข้อมูลคู่มือแนะนำการคัดแยกขยะ 4 หมวดหลัก
    พร้อมคำแนะนำการเตรียมเพื่อเพิ่มมูลค่าราคา
    """
    response = client.get("/api/v1/help/sorting-guides")
    assert response.status_code == 200
    data = response.json()

    guides = data["guides"]
    assert len(guides) == 4

    # 1. ตรวจสอบกระดาษลัง
    cardboard = next(g for g in guides if g["category_code"] == "MAT-CARDBOARD")
    assert "กล่องลูกฟูก" in cardboard["category_name"]
    assert any("พับให้แบน" in tip for tip in cardboard["value_add_tips"])

    # 2. ตรวจสอบกระดาษขาวดำ
    white_paper = next(g for g in guides if g["category_code"] == "MAT-WHITE-PAPER")
    assert "6–7 บาท/กก." in white_paper["price_impact_description"]

    # 3. ตรวจสอบขวดแก้ว
    glass = next(g for g in guides if g["category_code"] == "MAT-GLASS-BOTTLE")
    assert any("แยกสี" in tip for tip in glass["value_add_tips"])

    # 4. ตรวจสอบขวดพลาสติก PET
    pet = next(g for g in guides if g["category_code"] == "MAT-PLASTIC-PET")
    assert any("บีบหรือเหยียบ" in tip for tip in pet["value_add_tips"])

