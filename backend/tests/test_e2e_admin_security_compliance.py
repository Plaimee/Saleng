"""
End-to-End (E2E) Test Suite for Admin Feature 04: Audit Trail, Community Waste Reporting & PDPA Compliance
รองรับ UC-13, REQ-SEC-001, REQ-SEC-002, CT-01, P-07, D-A04-01..06, CC-01, CC-03, CC-04, CC-05, CC-06
"""

import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_e2e_admin_security_compliance_lifecycle():
    """
    ทดสอบวงจรชีวิตแบบครบวงจร (End-to-End) ของ Admin Feature 04:
    1. ตรวจสอบ Audit Log และ Integrity Check
    2. ส่งออก Audit Log (CSV, JSON)
    3. ตรวจสอบรายงานขยะชุมชนรายเขต ปลอด PII 100%
    4. ส่งออกรายงานขยะชุมชน CSV
    5. ตรวจสอบสถานะการเก็บรักษา PDPA Retention
    6. สั่ง Purge ข้อมูลหมดอายุ และตรวจสอบผลลัพธ์
    7. ตรวจสอบการบันทึก Audit Log การ Purge และ Integrity อีกครั้ง
    8. ตรวจสอบการบังคับใช้ RBAC ทุกบทบาท
    """
    # -------------------------------------------------------------
    # Step 1: ตรวจสอบและดึง Audit Log ในฐานะ ADMIN
    # -------------------------------------------------------------
    resp_logs = client.get(
        "/api/v1/admin/compliance/audit-logs?limit=20&offset=0",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert resp_logs.status_code == 200
    logs_data = resp_logs.json()
    assert logs_data["total_records"] >= 1
    assert len(logs_data["logs"]) >= 1
    assert "log_hash" in logs_data["logs"][0]

    # -------------------------------------------------------------
    # Step 2: ตรวจสอบความสมบูรณ์ SHA-256 Integrity Check ในฐานะ AUDITOR
    # -------------------------------------------------------------
    resp_integrity = client.post(
        "/api/v1/admin/compliance/audit-logs/verify-integrity",
        headers={"X-Admin-Role": "AUDITOR"},
    )
    assert resp_integrity.status_code == 200
    integrity_data = resp_integrity.json()
    assert integrity_data["is_valid"] is True
    assert len(integrity_data["corrupted_log_ids"]) == 0

    # -------------------------------------------------------------
    # Step 3: ส่งออก Audit Log เป็น CSV และ JSON
    # -------------------------------------------------------------
    resp_export_csv = client.get(
        "/api/v1/admin/compliance/audit-logs/export?format=csv",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert resp_export_csv.status_code == 200
    assert "text/csv" in resp_export_csv.headers.get("content-type", "")
    assert "log_id,timestamp,actor_id" in resp_export_csv.text

    resp_export_json = client.get(
        "/api/v1/admin/compliance/audit-logs/export?format=json",
        headers={"X-Admin-Role": "AUDITOR"},
    )
    assert resp_export_json.status_code == 200
    assert isinstance(resp_export_json.json(), list)

    # -------------------------------------------------------------
    # Step 4: ตรวจสอบรายงานขยะชุมชน (Community Waste Report) - No PII
    # -------------------------------------------------------------
    resp_report = client.get(
        "/api/v1/admin/compliance/reports/community-waste",
        headers={"X-Admin-Role": "AUDITOR"},
    )
    assert resp_report.status_code == 200
    report_data = resp_report.json()
    assert report_data["is_anonymized"] is True
    assert report_data["grand_total_weight_kg"] > 0
    assert report_data["grand_total_amount_thb"] > 0
    assert len(report_data["summary_items"]) >= 1

    for row in report_data["summary_items"]:
        # ยืนยันว่าไม่มี PII เด็ดขาด
        assert "seller" not in row
        assert "collector" not in row
        assert "phone" not in row
        assert "address" not in row
        assert "district" in row
        assert "subdistrict" in row

    # ส่งออก CSV รายงานขยะชุมชนสำหรับ กทม.
    resp_report_csv = client.get(
        "/api/v1/admin/compliance/reports/community-waste/export",
        headers={"X-Admin-Role": "DPO"},
    )
    assert resp_report_csv.status_code == 200
    assert "text/csv" in resp_report_csv.headers.get("content-type", "")

    # -------------------------------------------------------------
    # Step 5: ตรวจสอบสถานะการเก็บรักษาข้อมูล PDPA ในฐานะ DPO
    # -------------------------------------------------------------
    now = datetime.now(timezone.utc)
    # เพิ่ม GPS และ Order เก่าเพื่อให้มั่นใจว่ามีข้อมูลที่ครบกำหนด Purge
    supabase_store.collector_gps_history.append({
        "gps_id": "gps-e2e-expired",
        "collector_id": "saleng-e2e",
        "latitude": 13.75,
        "longitude": 100.50,
        "recorded_at": (now - timedelta(days=100)).isoformat(),
    })

    resp_retention = client.get(
        "/api/v1/admin/compliance/retention-status",
        headers={"X-Admin-Role": "DPO"},
    )
    assert resp_retention.status_code == 200
    retention_data = resp_retention.json()
    assert retention_data["gps_retention_days"] == 90
    assert retention_data["expired_gps_coordinates_count"] >= 1

    # -------------------------------------------------------------
    # Step 6: ดำเนินการ Purge ข้อมูลหมดอายุตามนโยบาย PDPA
    # -------------------------------------------------------------
    resp_purge = client.post(
        "/api/v1/admin/compliance/purge-expired",
        headers={"X-Admin-Role": "DPO"},
        json={"admin_id": "dpo-e2e-officer", "confirm_purge": True},
    )
    assert resp_purge.status_code == 200
    purge_data = resp_purge.json()
    assert purge_data["success"] is True
    assert purge_data["purged_gps_points_count"] >= 1
    assert purge_data["purged_by"] == "dpo-e2e-officer"

    # ตรวจสอบสถานะหลัง Purge
    resp_retention_after = client.get(
        "/api/v1/admin/compliance/retention-status",
        headers={"X-Admin-Role": "DPO"},
    )
    assert resp_retention_after.status_code == 200
    assert resp_retention_after.json()["expired_gps_coordinates_count"] == 0

    # -------------------------------------------------------------
    # Step 7: ตรวจสอบ Audit Log รายการ Purge และความสมบูรณ์อีกครั้ง
    # -------------------------------------------------------------
    resp_purge_log = client.get(
        "/api/v1/admin/compliance/audit-logs?action=ADMIN_PURGED_EXPIRED_DATA",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert resp_purge_log.status_code == 200
    purge_logs = resp_purge_log.json()
    assert len(purge_logs["logs"]) >= 1
    assert purge_logs["logs"][0]["actor_role"] == "DPO"

    # Integrity ยังคงต้อง 100% Intact
    resp_integrity_final = client.post(
        "/api/v1/admin/compliance/audit-logs/verify-integrity",
        headers={"X-Admin-Role": "ADMIN"},
    )
    assert resp_integrity_final.status_code == 200
    assert resp_integrity_final.json()["is_valid"] is True

    # -------------------------------------------------------------
    # Step 8: ตรวจสอบ RBAC Enforcement
    # -------------------------------------------------------------
    # SUPPORT ต้องถูกบล็อกทุก Endpoint
    resp_blocked = client.get(
        "/api/v1/admin/compliance/audit-logs",
        headers={"X-Admin-Role": "SUPPORT"},
    )
    assert resp_blocked.status_code == 403

    # DPO ห้ามดู Audit Trail
    resp_dpo_blocked = client.get(
        "/api/v1/admin/compliance/audit-logs",
        headers={"X-Admin-Role": "DPO"},
    )
    assert resp_dpo_blocked.status_code == 403

    # AUDITOR ห้ามสั่ง Purge
    resp_auditor_blocked = client.post(
        "/api/v1/admin/compliance/purge-expired",
        headers={"X-Admin-Role": "AUDITOR"},
        json={"admin_id": "auditor-01", "confirm_purge": True},
    )
    assert resp_auditor_blocked.status_code == 403

