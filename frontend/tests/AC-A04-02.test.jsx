import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminSecurityComplianceView from '../src/components/admin/AdminSecurityComplianceView';
import * as adminSecurityComplianceApi from '../src/services/adminSecurityComplianceApi';

describe('AC-A04-02: Community Waste Report View Component Tests', () => {
  const mockReport = {
    period: '2026-11',
    district: 'ปทุมวัน',
    is_anonymized: true,
    grand_total_weight_kg: 85.0,
    grand_total_amount_thb: 347.5,
    total_completed_trips: 2,
    summary_items: [
      {
        subdistrict: 'ลุมพินี',
        district: 'ปทุมวัน',
        category_code: 'MAT-CARDBOARD',
        category_name: 'กระดาษลัง',
        total_weight_kg: 25.0,
        total_amount_thb: 87.5,
        completed_trips_count: 1,
        period_month: '2026-11',
      },
    ],
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminSecurityComplianceApi, 'getAuditLogs').mockResolvedValue({ total_records: 0, limit: 10, offset: 0, logs: [] });
    vi.spyOn(adminSecurityComplianceApi, 'getCommunityWasteReport').mockResolvedValue(mockReport);
    vi.spyOn(adminSecurityComplianceApi, 'exportCommunityWasteCsv').mockResolvedValue('district,subdistrict,total_weight\nปทุมวัน,ลุมพินี,25.0');
  });

  it('renders Community Waste Report with No PII indicator and KPIs', async () => {
    render(<AdminSecurityComplianceView />);

    // สลับไปยังแท็บรายงานขยะชุมชน
    const reportTabBtn = screen.getByText(/รายงานสถิติขยะชุมชน/i);
    fireEvent.click(reportTabBtn);

    await waitFor(() => {
      expect(screen.getByText(/No PII \(ปลอดข้อมูลส่วนบุคคล 100%\)/i)).toBeTruthy();
      expect(screen.getByText(/85/)).toBeTruthy(); // Grand total weight
      expect(screen.getByText(/กระดาษลัง/i)).toBeTruthy();
      expect(screen.getByText('ลุมพินี')).toBeTruthy();
    });
  });
});

