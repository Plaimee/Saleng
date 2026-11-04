"""
Automated Test for AC-A04-02: Immutable Audit Integrity & SHA-256 Hash Verification
รองรับ UC-13, REQ-SEC-001, P-07, D-A04-05, CC-03, CC-05
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.api.v1.pricing import app
from backend.app.core.supabase import supabase_store

client = TestClient(app)


def test_verify_audit_integrity_intact():
    """ทดสอบการตรวจสอบ Integrity ของ Audit Trail ในสภาวะปกติ (100% Intact)"""
    response = client.post(
        "/api/v1/admin/compliance/audit-logs/verify-integrity",
        headers={"X-Admin-Role": "AUDITOR"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_checked"] >= 1
    assert data["is_valid"] is True
    assert len(data["corrupted_log_ids"]) == 0
    assert "Intact" in data["message"]


def test_verify_audit_integrity_tampering_detected():
    """ทดสอบกรณีบันทึก Audit Log ถูกแก้ไขหรือปลอมแปลง (Tamper-evident Detection)"""
    tampered_entry = {
        "log_id": "tampered-log-test-999",
        "action": "UNAUTHORIZED_DELETE",
        "actor_id": "bad-actor",
        "actor_role": "ADMIN",
        "entity_id": "target-001",
        "timestamp": "2026-11-04T12:00:00Z",
        "details": {"reason": "hacked"},
        "log_hash": "corrupted_hash_value_abcdef1234567890",
    }
    supabase_store.audit_logs.append(tampered_entry)

    try:
        response = client.post(
            "/api/v1/admin/compliance/audit-logs/verify-integrity",
            headers={"X-Admin-Role": "ADMIN"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "tampered-log-test-999" in data["corrupted_log_ids"]
        assert "Tampering Detected" in data["message"]
    finally:
        # Clean up
        supabase_store.audit_logs = [
            l for l in supabase_store.audit_logs if l.get("log_id") != "tampered-log-test-999"
        ]

