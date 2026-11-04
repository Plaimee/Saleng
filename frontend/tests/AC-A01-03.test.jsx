/**
 * Vitest Component Test สำหรับ AC-A01-03: User Penalty Enforcement for Saleng & Seller
 * รองรับ UC-11, D-A01-03, D-A01-04, REQ-SEC-001, REQ-UX-001, AC-A01-03
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import UserPenaltyControlCard from '../src/components/admin/UserPenaltyControlCard';

describe('AC-A01-03: User Penalty Enforcement for Saleng & Seller', () => {
  const mockActiveSaleng = {
    user_id: 'saleng-01',
    role: 'COLLECTOR',
    display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
    phone_masked: '08X-XXX-5678',
    account_status: 'ACTIVE',
    penalty_reason: null,
  };

  const mockActiveSeller = {
    user_id: 'seller-01',
    role: 'SELLER',
    display_name: 'สมศรี ร้านกาแฟสุขุมวิท',
    phone_masked: '08X-XXX-1111',
    account_status: 'ACTIVE',
    penalty_reason: null,
  };

  it('renders active user card with role and active status badge', () => {
    render(
      <UserPenaltyControlCard
        user={mockActiveSaleng}
        onPenalize={vi.fn()}
        onReactivate={vi.fn()}
      />
    );

    expect(screen.getByText('ลุงสมชาย ซาเล้งสุทธิสาร')).not.toBeNull();
    expect(screen.getByText('ซาเล้ง (COLLECTOR)')).not.toBeNull();
    const statusBadge = screen.getByTestId('account-status-badge');
    expect(statusBadge.textContent).toContain('ACTIVE');
    expect(screen.getByTestId('masked-phone').textContent).toBe('08X-XXX-5678');
  });

  it('opens modal and penalizes user with SUSPENDED_TEMPORARY when suspend button is clicked', () => {
    const handlePenalize = vi.fn();
    render(
      <UserPenaltyControlCard
        user={mockActiveSaleng}
        onPenalize={handlePenalize}
        onReactivate={vi.fn()}
      />
    );

    // Click Suspend button
    const suspendBtn = screen.getByTestId('btn-suspend-user');
    expect(suspendBtn.className).toContain('min-h-[48px]');
    fireEvent.click(suspendBtn);

    // Modal opens
    const modal = screen.getByTestId('penalty-modal');
    expect(modal).not.toBeNull();
    expect(screen.getByText(/ยืนยันระงับบัญชีชั่วคราว/)).not.toBeNull();

    // Click confirm with empty reason -> validation error
    const confirmBtn = screen.getByTestId('btn-confirm-penalty');
    fireEvent.click(confirmBtn);
    expect(screen.getByTestId('penalty-modal-error').textContent).toContain('กรุณาระบุเหตุผลการลงโทษ');
    expect(handlePenalize).not.toHaveBeenCalled();

    // Enter reason and submit
    const textarea = screen.getByTestId('penalty-reason-input');
    fireEvent.change(textarea, { target: { value: 'รายงานการโกงตาชั่งขวดแก้ว' } });
    fireEvent.click(confirmBtn);

    expect(handlePenalize).toHaveBeenCalledTimes(1);
    expect(handlePenalize).toHaveBeenCalledWith(
      'saleng-01',
      'COLLECTOR',
      'SUSPENDED_TEMPORARY',
      'รายงานการโกงตาชั่งขวดแก้ว'
    );
  });

  it('opens modal and penalizes seller with BANNED when ban button is clicked', () => {
    const handlePenalize = vi.fn();
    render(
      <UserPenaltyControlCard
        user={mockActiveSeller}
        onPenalize={handlePenalize}
        onReactivate={vi.fn()}
      />
    );

    const banBtn = screen.getByTestId('btn-ban-user');
    expect(banBtn.className).toContain('min-h-[48px]');
    fireEvent.click(banBtn);

    expect(screen.getByText(/ยืนยันแบนถาวร/)).not.toBeNull();

    const textarea = screen.getByTestId('penalty-reason-input');
    fireEvent.change(textarea, { target: { value: 'เจตนาทิ้งขยะอันตรายและพฤติกรรมก้าวร้าว' } });

    const confirmBtn = screen.getByTestId('btn-confirm-penalty');
    fireEvent.click(confirmBtn);

    expect(handlePenalize).toHaveBeenCalledWith(
      'seller-01',
      'SELLER',
      'BANNED',
      'เจตนาทิ้งขยะอันตรายและพฤติกรรมก้าวร้าว'
    );
  });
});

