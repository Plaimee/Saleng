"""
Test Suite for T-01: Data Models and Storage Helpers for Admin Security, Audit Trail & PDPA Compliance
รองรับ UC-13, REQ-SEC-001, REQ-SEC-002, CT-01, P-07, D-A04-01..05
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.app.models.security_compliance_models import (
    compute_audit_log_hash,
    AuditLogQueryFilter,
    AuditLogItem,
    AuditLogListResponse,
    AuditLogExportResponse,
    VerifyIntegrityResponse,
    CommunityWasteSummaryItem,
    CommunityWasteReportResponse,
    DataRetentionStatusResponse,
    PurgeExpiredDataRequest,
    PurgeExpiredDataResponse,
)
from backend.app.core.supabase import supabase_store


def test_compute_audit_log_hash_determinism():
    """ทดสอบว่า compute_audit_log_hash คำนวณค่าแฮช SHA-256 ได้คงที่และเปลี่ยนเมื่อเนื้อหาเปลี่ยน"""
    log_data = {
        "actor_id": "admin-001",
        "actor_role": "ADMIN",
        "action": "PRICE_BENCHMARK_UPDATED",
        "entity_id": "bench-01",
        "timestamp": "2026-11-04T10:00:00Z",
        "details": {"price": 5.0, "category": "MAT-CARDBOARD"},
    }
    hash1 = compute_audit_log_hash(log_data)
    hash2 = compute_audit_log_hash(log_data)
    assert len(hash1) == 64
    assert hash1 == hash2

    # เปลี่ยนแปลงข้อมูล เล็กน้อย แฮชต้องเปลี่ยน
    tampered_data = dict(log_data)
    tampered_data["action"] = "TAMPERED_ACTION"
    hash_tampered = compute_audit_log_hash(tampered_data)
    assert hash1 != hash_tampered


def test_pydantic_models_validation():
    """ทดสอบ Pydantic Schemas สำหรับ Security & Compliance"""
    filter_model = AuditLogQueryFilter(action="DISPATCH_OVERRIDE", limit=20, offset=0)
    assert filter_model.limit == 20
    assert filter_model.action == "DISPATCH_OVERRIDE"

    retention_req = PurgeExpiredDataRequest(admin_id="admin-dpo-01", reason="รอบการล้างข้อมูลประจำสัปดาห์")
    assert retention_req.admin_id == "admin-dpo-01"


def test_supabase_store_query_and_integrity():
    """ทดสอบการสืบค้น Audit Log และการตรวจ Integrity Check ของ SupabaseStore"""
    # 1. Query Logs
    total, logs = supabase_store.query_audit_logs(limit=10)
    assert total >= 1
    assert len(logs) <= 10
    first_log = logs[0]
    assert "log_hash" in first_log
    assert "action" in first_log

    # 2. Verify Integrity
    count, is_valid, corrupted = supabase_store.verify_audit_logs_integrity()
    assert count >= 1
    assert is_valid is True
    assert len(corrupted) == 0

    # 3. Simulate Tampering
    tampered_entry = {
        "log_id": "tampered-log-id",
        "action": "FAKE_ACTION",
        "actor_id": "attacker",
        "actor_role": "SELLER",
        "entity_id": "victim",
        "timestamp": "2026-11-04T12:00:00Z",
        "details": {},
        "log_hash": "invalid_hash_string_12345",
    }
    supabase_store.audit_logs.append(tampered_entry)
    count2, is_valid2, corrupted2 = supabase_store.verify_audit_logs_integrity()
    assert is_valid2 is False
    assert "tampered-log-id" in corrupted2

    # Clean up tampered entry
    supabase_store.audit_logs = [l for l in supabase_store.audit_logs if l.get("log_id") != "tampered-log-id"]


def test_supabase_store_community_report_and_pdpa_retention():
    """ทดสอบการสร้างรายงานชุมชน และกระบวนการ Retention/Purge ของ SupabaseStore"""
    now = datetime.now(timezone.utc)
    # เพิ่ม GPS และ Order เก่าเพื่อให้มั่นใจว่ามีข้อมูลสำหรับทดสอบ purge เสมอ
    supabase_store.collector_gps_history.append({
        "gps_id": "gps-test-t01-expired",
        "collector_id": "saleng-001",
        "latitude": 13.73,
        "longitude": 100.52,
        "recorded_at": (now - timedelta(days=95)).isoformat(),
    })
    supabase_store.orders["order-comp-comm-01"] = {
        "id": "order-comp-comm-01",
        "order_id": "order-comp-comm-01",
        "status": "S7",
        "district": "ปทุมวัน",
        "subdistrict": "ลุมพินี",
        "seller_address": "99/1 ซอยร่วมฤดี",
        "seller_address_masked": "*** ซอยร่วมฤดี",
        "is_address_masked": False,
        "completed_at": (now - timedelta(days=3)).isoformat(),
    }
    supabase_store.items["item-comm-01"] = {
        "id": "item-comm-01",
        "order_id": "order-comp-comm-01",
        "category_code": "MAT-CARDBOARD",
        "category_name": "กระดาษลัง",
        "weight_kg": 25.0,
        "total_price": 87.5,
    }

    # 1. Community report
    report = supabase_store.get_community_waste_report(district_filter="ปทุมวัน")
    assert len(report) >= 1
    item = report[0]
    assert item["district"] == "ปทุมวัน"
    assert item["total_weight_kg"] > 0
    # ตรวจสอบว่าไม่มี PII ใดๆ หลุดออกมา
    for k in item.keys():
        assert "seller" not in k
        assert "collector" not in k
        assert "phone" not in k
        assert "address" not in k

    # 2. PDPA Retention Status
    status = supabase_store.get_pdpa_retention_status()
    assert status["retention_policy_gps_days"] == 90
    assert status["retention_policy_address_hours"] == 24
    assert status["expired_gps_records"] >= 1
    assert status["unmasked_completed_orders_gt_24h"] >= 1

    # 3. Purge Expired Data
    purged_gps, masked_orders = supabase_store.purge_expired_pdpa_data(admin_id="admin-dpo-test")
    assert purged_gps >= 1
    assert masked_orders >= 1

    # Check status after purge
    status_after = supabase_store.get_pdpa_retention_status()
    assert status_after["expired_gps_records"] == 0
    assert status_after["unmasked_completed_orders_gt_24h"] == 0
