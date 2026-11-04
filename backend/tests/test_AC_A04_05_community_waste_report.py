"""
Automated Test for AC-A04-05: Anonymized Community Waste Report API
รองรับ UC-13, D-A04-03, REQ-SEC-002, CC-03, CC-05, CC-06
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_get_community_waste_report_success():
    """ทดสอบการดึงรายงานสถิติขยะชุมชนแบบไม่ระบุตัวตน (No PII)"""
    response = client.get(
        "/api/v1/admin/compliance/reports/community-waste",
        headers={"X-Admin-Role": "AUDITOR"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_anonymized"] is True
    assert data["grand_total_weight_kg"] > 0
    assert data["grand_total_amount_thb"] > 0
    assert len(data["summary_items"]) >= 1

    # ตรวจสอบว่าไม่มี PII ใดๆ ปรากฏในแต่ละแถวข้อมูล
    for item in data["summary_items"]:
        assert "district" in item
        assert "subdistrict" in item
        assert "category_name" in item
        assert "total_weight_kg" in item
        assert "total_amount_thb" in item
        # ตรวจสอบการไม่มี PII
        item_keys = set(item.keys())
        assert "seller_name" not in item_keys
        assert "collector_name" not in item_keys
        assert "phone" not in item_keys
        assert "address" not in item_keys


def test_get_community_waste_report_filter_district():
    """ทดสอบการกรองรายงานเฉพาะเขตที่กำหนด"""
    response = client.get(
        "/api/v1/admin/compliance/reports/community-waste?district=ปทุมวัน",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["summary_items"]:
        assert item["district"] == "ปทุมวัน"


def test_export_community_waste_report_csv():
    """ทดสอบการส่งออกรายงานขยะชุมชนเป็นไฟล์ CSV สำหรับส่งต่อ กทม."""
    response = client.get(
        "/api/v1/admin/compliance/reports/community-waste/export",
        headers={"X-Admin-Role": "DPO"},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert "attachment; filename=community_waste_report.csv" in response.headers.get("content-disposition", "")
    csv_text = response.text
    assert "district,subdistrict,category_code,category_name,total_weight_kg,total_amount_thb,completed_trips_count,period_month" in csv_text
    assert "ปทุมวัน" in csv_text or "คลองเตย" in csv_text

