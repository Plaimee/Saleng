import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminSecurityComplianceView from '../src/components/admin/AdminSecurityComplianceView';
import * as adminSecurityComplianceApi from '../src/services/adminSecurityComplianceApi';

describe('AC-A04-01: Audit Trail Viewer & Integrity Check Component Tests', () => {
  const mockAuditLogs = {
    total_records: 2,
    limit: 10,
    offset: 0,
    logs: [
      {
        log_id: 'log-001',
        action: 'PRICE_BENCHMARK_UPDATED',
        actor_id: 'admin-001',
        actor_role: 'ADMIN',
        entity_id: 'bench-01',
        details: { category: 'MAT-CARDBOARD' },
        timestamp: '2026-11-04T10:00:00Z',
        log_hash: 'a1b2c3d4e5f678901234567890abcdef',
      },
      {
        log_id: 'log-002',
        action: 'KYC_APPROVED',
        actor_id: 'admin-001',
        actor_role: 'ADMIN',
        entity_id: 'kyc-01',
        details: { collector_id: 'saleng-001' },
        timestamp: '2026-11-04T11:00:00Z',
        log_hash: 'f6e5d4c3b2a109876543210987fedcba',
      },
    ],
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminSecurityComplianceApi, 'getAuditLogs').mockResolvedValue(mockAuditLogs);
    vi.spyOn(adminSecurityComplianceApi, 'verifyAuditIntegrity').mockResolvedValue({
      total_checked: 2,
      is_valid: true,
      corrupted_log_ids: [],
      message: 'Audit Trail Verified - 100% Integrity Intact',
      verified_at: '2026-11-04T12:00:00Z',
    });
  });

  it('renders AdminSecurityComplianceView with data-req="UC-13" and touch targets >= 48px', async () => {
    render(<AdminSecurityComplianceView />);

    await waitFor(() => {
      expect(screen.getByTestId('admin-security-compliance-view')).toBeTruthy();
    });

    const mainContainer = screen.getByTestId('admin-security-compliance-view');
    expect(mainContainer.getAttribute('data-req')).toBe('UC-13');

    // ตรวจสอบว่าปุ่มกดมีคลาสความสูงอย่างน้อย min-h-[48px]
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
    buttons.forEach((btn) => {
      expect(btn.className).toContain('min-h-[48px]');
    });
  });

  it('displays audit logs and performs SHA-256 integrity check', async () => {
    render(<AdminSecurityComplianceView />);

    await waitFor(() => {
      expect(screen.getByText('PRICE_BENCHMARK_UPDATED')).toBeTruthy();
      expect(screen.getByText('KYC_APPROVED')).toBeTruthy();
    });

    // กดปุ่มตรวจสอบความสมบูรณ์ SHA-256
    const verifyBtn = screen.getByText(/ตรวจสอบความสมบูรณ์/i);
    fireEvent.click(verifyBtn);

    await waitFor(() => {
      expect(screen.getAllByText(/Audit Trail Verified - 100% Integrity Intact/i).length).toBeGreaterThanOrEqual(1);
    });
  });
});
