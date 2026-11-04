"""
Automated Test for AC-A02-02: Quality Grading & Contamination Rules
รองรับ UC-03, REQ-FN-003, AC-A02-02, D-A02-03, REQ-SEC-001, CC-03
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_grading_rules():
    """บันทึกและคืนค่าเกณฑ์คุณภาพก่อนและหลังทดสอบ"""
    original = list(supabase_store.get_quality_grading_rules("MAT-CARDBOARD"))
    yield
    if original:
        supabase_store.quality_grading_rules["MAT-CARDBOARD"] = original


def test_AC_A02_02_get_grading_rules_success():
    """
    ทดสอบการดึงเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อนมาตรฐาน
    รองรับ AC-A02-02, REQ-FN-003, D-A02-03
    - GRADE_A: หัก 0%, price_target = MAX
    - GRADE_B: หัก 5%, price_target = MID
    - GRADE_C: หัก 10%, price_target = MIN
    """
    response = client.get(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    grades = {r["grade_level"]: r for r in data}
    assert "GRADE_A" in grades
    assert "GRADE_B" in grades
    assert "GRADE_C" in grades

    # ตรวจสอบเปอร์เซ็นต์หักสิ่งปนเปื้อน 0%/5%/10% ตาม D-A02-03
    assert grades["GRADE_A"]["contamination_deduction_percent"] == 0.0
    assert grades["GRADE_A"]["price_target"] == "MAX"

    assert grades["GRADE_B"]["contamination_deduction_percent"] == 5.0
    assert grades["GRADE_B"]["price_target"] == "MID"

    assert grades["GRADE_C"]["contamination_deduction_percent"] == 10.0
    assert grades["GRADE_C"]["price_target"] == "MIN"


def test_AC_A02_02_update_grading_rules_success():
    """
    ทดสอบการปรับปรุงคำอธิบายสภาพวัสดุ และเปอร์เซ็นต์หักสิ่งปนเปื้อน
    รองรับ AC-A02-02, REQ-FN-003, REQ-SEC-001
    """
    current_rules = client.get(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        headers={"X-Admin-Role": "ADMIN"},
    ).json()

    # แก้ไขคำอธิบายเกรด B
    current_rules[1]["description"] = "มีคราบเปื้อนเล็กน้อย หรือมีเศษกระดาษสีปนไม่เกิน 5%"
    current_rules[1]["contamination_deduction_percent"] = 5.0

    payload = {
        "rules": current_rules,
        "updated_by": "admin-01",
    }
    response = client.put(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        json=payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["category_code"] == "MAT-CARDBOARD"
    assert res_data["rules"][1]["description"] == "มีคราบเปื้อนเล็กน้อย หรือมีเศษกระดาษสีปนไม่เกิน 5%"

    # ตรวจสอบ Audit Log (REQ-SEC-001)
    audits = [a for a in supabase_store.audit_logs if a["action"] == "ADMIN_UPDATED_GRADING_RULES"]
    assert len(audits) >= 1
    last_audit = audits[-1]
    assert last_audit["entity_id"] == "MAT-CARDBOARD"
    assert last_audit["details"]["actor_role"] == "ADMIN"


def test_AC_A02_02_grading_rules_not_found():
    """
    ทดสอบกรณีหมวดหมู่วัสดุไม่มีอยู่ในระบบ (404 Not Found)
    """
    response = client.get(
        "/api/v1/admin/benchmark-prices/grading/MAT-UNKNOWN-XYZ",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 404


def test_AC_A02_02_grading_rules_invalid_percent():
    """
    ทดสอบกรณีส่งค่า % หักสิ่งปนเปื้อนติดลบหรือเกิน 100%
    """
    bad_payload = {
        "rules": [
            {
                "rule_id": "r-1",
                "category_code": "MAT-CARDBOARD",
                "grade_level": "GRADE_A",
                "grade_name": "เกรด A",
                "description": "ผิดพลาด",
                "contamination_deduction_percent": 120.0,
                "price_target": "MAX",
                "updated_at": "2026-11-04T00:00:00Z",
                "updated_by": "admin-01",
            }
        ],
        "updated_by": "admin-01",
    }
    response = client.put(
        "/api/v1/admin/benchmark-prices/grading/MAT-CARDBOARD",
        json=bad_payload,
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 422

