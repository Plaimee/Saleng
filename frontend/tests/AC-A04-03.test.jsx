import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminSecurityComplianceView from '../src/components/admin/AdminSecurityComplianceView';
import * as adminSecurityComplianceApi from '../src/services/adminSecurityComplianceApi';

describe('AC-A04-03: PDPA Retention & Purge Panel Component Tests', () => {
  const mockRetentionStatus = {
    gps_retention_days: 90,
    expired_gps_coordinates_count: 3,
    unmasked_completed_orders_count: 2,
    total_audit_logs_count: 15,
    checked_at: '2026-11-04T12:00:00Z',
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminSecurityComplianceApi, 'getAuditLogs').mockResolvedValue({ total_records: 0, limit: 10, offset: 0, logs: [] });
    vi.spyOn(adminSecurityComplianceApi, 'getPdpaRetentionStatus').mockResolvedValue(mockRetentionStatus);
    vi.spyOn(adminSecurityComplianceApi, 'purgeExpiredPdpaData').mockResolvedValue({
      success: true,
      purged_gps_points_count: 3,
      masked_orders_count: 2,
      purged_by: 'dpo-compliance-01',
      message: 'Purge completed successfully: 3 GPS records purged, 2 orders masked.',
    });
  });

  it('renders PDPA retention policies and handles purge flow', async () => {
    render(<AdminSecurityComplianceView />);

    // สลับไปยังแท็บ PDPA
    const pdpaTabBtn = screen.getByText(/การปฏิบัติตาม PDPA/i);
    fireEvent.click(pdpaTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/Collector GPS/i)).toBeTruthy();
      expect(screen.getByText(/เกณฑ์ไม่เกิน 90 วัน/i)).toBeTruthy();
      expect(screen.getByText(/Mask หลังจบงาน 24 ชม./i)).toBeTruthy();
    });

    const purgeBtn = screen.getByText(/ดำเนินการล้างข้อมูลตามนโยบาย PDPA ทันที/i);
    expect(purgeBtn.disabled).toBe(true);

    // ติ๊กยืนยัน
    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);
    expect(checkbox.checked).toBe(true);
    expect(purgeBtn.disabled).toBe(false);

    // กดปุ่ม Purge
    fireEvent.click(purgeBtn);

    await waitFor(() => {
      expect(screen.getAllByText(/Purge completed successfully/i).length).toBeGreaterThanOrEqual(1);
    });
  });
});
