"""
Automated Test for AC-A04-01: Audit Trail Query, Filtering & Export
รองรับ UC-13, REQ-SEC-001, D-A04-01, CC-03, CC-05
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app

client = TestClient(app)


def test_get_audit_logs_success():
    """ทดสอบการดึงรายการ Audit Log พร้อมตรวจสอบโครงสร้างข้อมูลและการทำ Pagination"""
    response = client.get(
        "/api/v1/admin/compliance/audit-logs?limit=10&offset=0",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "logs" in data
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert len(data["logs"]) >= 1

    first_item = data["logs"][0]
    assert "log_id" in first_item
    assert "action" in first_item
    assert "actor_id" in first_item
    assert "actor_role" in first_item
    assert "log_hash" in first_item
    assert "timestamp" in first_item


def test_get_audit_logs_with_filter():
    """ทดสอบการกรอง Audit Log ตาม action หรือ actor_role"""
    response = client.get(
        "/api/v1/admin/compliance/audit-logs?actor_role=ADMIN",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["logs"]:
        assert item["actor_role"] == "ADMIN"


def test_export_audit_logs_csv():
    """ทดสอบการส่งออก Audit Log เป็นไฟล์ CSV (D-A04-01, AC-A04-01)"""
    response = client.get(
        "/api/v1/admin/compliance/audit-logs/export?format=csv",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert "attachment; filename=audit_trail_export.csv" in response.headers.get("content-disposition", "")
    content = response.text
    assert "log_id,timestamp,actor_id,actor_role,action,entity_id,log_hash,details" in content


def test_export_audit_logs_json():
    """ทดสอบการส่งออก Audit Log เป็น JSON"""
    response = client.get(
        "/api/v1/admin/compliance/audit-logs/export?format=json",
        headers={"X-Admin-Role": "AUDITOR"},
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    data = response.json()
    assert isinstance(data, list)


def test_export_audit_logs_invalid_format():
    """ทดสอบกรณีระบุ format ไม่ถูกต้อง ให้ส่งกลับ HTTP 400"""
    response = client.get(
        "/api/v1/admin/compliance/audit-logs/export?format=xml",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert response.status_code == 400
