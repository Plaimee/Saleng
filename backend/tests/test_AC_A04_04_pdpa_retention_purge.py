"""
Automated Test for AC-A04-04: PDPA Data Retention & Purge API
รองรับ UC-13, REQ-SEC-002, CT-01, D-A04-04, CC-03, CC-05
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_pdpa_retention_status_and_purge_flow():
    """ทดสอบกระบวนการตรวจสอบสถานะ Retention และการสั่ง Purge ข้อมูลหมดอายุตามกฎหมาย PDPA"""
    # ตรวจสอบให้มีข้อมูล expired สำหรับทดสอบ
    now = datetime.now(timezone.utc)
    supabase_store.collector_gps_history.append({
        "gps_id": "gps-test-expired",
        "collector_id": "saleng-001",
        "latitude": 13.73,
        "longitude": 100.52,
        "recorded_at": (now - timedelta(days=95)).isoformat(),
    })

    # 1. ตรวจสอบสถานะก่อน Purge
    status_resp = client.get(
        "/api/v1/admin/compliance/retention-status",
        headers={"X-Admin-Role": "DPO"},
    )
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["gps_retention_days"] == 90
    assert status_data["expired_gps_coordinates_count"] >= 1

    # 2. สั่งดำเนินการ Purge Expired Data
    purge_resp = client.post(
        "/api/v1/admin/compliance/purge-expired",
        headers={"X-Admin-Role": "DPO"},
        json={"admin_id": "dpo-somchai-01", "confirm_purge": True},
    )
    assert purge_resp.status_code == 200
    purge_data = purge_resp.json()
    assert purge_data["success"] is True
    assert purge_data["purged_gps_points_count"] >= 1
    assert purge_data["purged_by"] == "dpo-somchai-01"

    # 3. ตรวจสอบสถานะหลัง Purge ข้อมูล expired ต้องเป็น 0
    status_resp2 = client.get(
        "/api/v1/admin/compliance/retention-status",
        headers={"X-Admin-Role": "DPO"},
    )
    assert status_resp2.status_code == 200
    status_data2 = status_resp2.json()
    assert status_data2["expired_gps_coordinates_count"] == 0
    assert status_data2["unmasked_completed_orders_count"] == 0

    # 4. ตรวจสอบว่ามีบันทึก Audit Log กิจกรรม ADMIN_PURGED_EXPIRED_DATA
    log_resp = client.get(
        "/api/v1/admin/compliance/audit-logs?action=ADMIN_PURGED_EXPIRED_DATA",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert log_resp.status_code == 200
    log_data = log_resp.json()
    assert len(log_data["logs"]) >= 1
    latest_purge_log = log_data["logs"][0]
    assert latest_purge_log["action"] == "ADMIN_PURGED_EXPIRED_DATA"
    assert latest_purge_log["actor_role"] == "DPO"


def test_pdpa_purge_unconfirmed_validation_error():
    """กรณี confirm_purge เป็น False ต้องปฏิเสธคำขอ (HTTP 422 Unprocessable Entity)"""
    resp = client.post(
        "/api/v1/admin/compliance/purge-expired",
        headers={"X-Admin-Role": "DPO"},
        json={"admin_id": "dpo-01", "confirm_purge": False},
    )
    assert resp.status_code == 422

