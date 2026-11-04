/**
 * Unit Test for adminSecurityComplianceApi.js
 * รองรับ UC-13, AC-A04-01..05, CC-03, CC-05
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getAdminHeaders,
  getAuditLogs,
  exportAuditLogs,
  verifyAuditIntegrity,
  getCommunityWasteReport,
  exportCommunityWasteCsv,
  getPdpaRetentionStatus,
  purgeExpiredPdpaData,
} from '../src/services/adminSecurityComplianceApi.js';

describe('adminSecurityComplianceApi Service', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getAdminHeaders generates expected headers with role and content-type', () => {
    const headers = getAdminHeaders('admin-auditor-01', 'AUDITOR');
    expect(headers['X-Admin-Role']).toBe('AUDITOR');
    expect(headers['X-Admin-Id']).toBe('admin-auditor-01');
    expect(headers['Content-Type']).toBe('application/json');
  });

  it('getAuditLogs sends GET request with filters and receives data', async () => {
    const mockData = { total_records: 2, limit: 10, offset: 0, logs: [{ log_id: 'l1', action: 'KYC_APPROVED' }] };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const res = await getAuditLogs({ action: 'KYC_APPROVED', limit: 10 }, { customRole: 'ADMIN' });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/admin/compliance/audit-logs?action=KYC_APPROVED&limit=10'),
      expect.objectContaining({ method: 'GET' })
    );
    expect(res.total_records).toBe(2);
    expect(res.logs[0].action).toBe('KYC_APPROVED');
  });

  it('verifyAuditIntegrity sends POST request to verify endpoint', async () => {
    const mockData = { total_checked: 10, is_valid: true, corrupted_log_ids: [], message: 'Intact' };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const res = await verifyAuditIntegrity({ customRole: 'AUDITOR' });
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/admin/compliance/audit-logs/verify-integrity',
      expect.objectContaining({ method: 'POST' })
    );
    expect(res.is_valid).toBe(true);
  });

  it('getCommunityWasteReport sends GET request and receives anonymized report', async () => {
    const mockData = {
      period: '2026-11',
      summary_items: [{ district: 'ปทุมวัน', total_weight_kg: 50.0 }],
      grand_total_weight_kg: 50.0,
      is_anonymized: true,
    };
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const res = await getCommunityWasteReport({ district: 'ปทุมวัน' }, { customRole: 'DPO' });
    expect(res.is_anonymized).toBe(true);
    expect(res.summary_items[0].district).toBe('ปทุมวัน');
  });

  it('getPdpaRetentionStatus and purgeExpiredPdpaData work properly', async () => {
    // 1. Status
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ gps_retention_days: 90, expired_gps_coordinates_count: 5 }),
    });
    const status = await getPdpaRetentionStatus({ customRole: 'DPO' });
    expect(status.gps_retention_days).toBe(90);

    // 2. Purge
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, purged_gps_points_count: 5 }),
    });
    const purgeRes = await purgeExpiredPdpaData({ admin_id: 'dpo-01', confirm_purge: true }, { customRole: 'DPO' });
    expect(purgeRes.success).toBe(true);
    expect(purgeRes.purged_gps_points_count).toBe(5);
  });
});

