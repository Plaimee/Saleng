/**
 * Vitest Component Test สำหรับ AC-A01-04: Reactivate & Penalty Revocation
 * รองรับ UC-11, D-A01-03, D-A01-04, REQ-SEC-001, REQ-UX-001, AC-A01-04
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import UserPenaltyControlCard from '../src/components/admin/UserPenaltyControlCard';

describe('AC-A01-04: Reactivate & Penalty Revocation', () => {
  const mockSuspendedSaleng = {
    user_id: 'saleng-02',
    role: 'COLLECTOR',
    display_name: 'นายสมบัติ ซาเล้งลาดพร้าว',
    phone_masked: '08X-XXX-8888',
    account_status: 'SUSPENDED_TEMPORARY',
    penalty_reason: 'อยู่ระหว่างตรวจสอบการไม่ไปรับของตามนัด',
  };

  const mockBannedSeller = {
    user_id: 'seller-03',
    role: 'SELLER',
    display_name: 'ร้านค้าที่ถูกแบน',
    phone_masked: '08X-XXX-9999',
    account_status: 'BANNED',
    penalty_reason: 'ละเมิดข้อกำหนดร้ายแรง',
  };

  it('renders suspended status, displays penalty reason box, and shows reactivate button', () => {
    render(
      <UserPenaltyControlCard
        user={mockSuspendedSaleng}
        onPenalize={vi.fn()}
        onReactivate={vi.fn()}
      />
    );

    const statusBadge = screen.getByTestId('account-status-badge');
    expect(statusBadge.textContent).toContain('SUSPENDED');

    const reasonBox = screen.getByTestId('penalty-reason-box');
    expect(reasonBox.textContent).toContain('อยู่ระหว่างตรวจสอบการไม่ไปรับของตามนัด');

    const reactivateBtn = screen.getByTestId('btn-reactivate-user');
    expect(reactivateBtn).not.toBeNull();
    expect(reactivateBtn.className).toContain('min-h-[48px]');
  });

  it('triggers onReactivate callback when reactivate button is clicked (AC-A01-04)', () => {
    const handleReactivate = vi.fn();
    render(
      <UserPenaltyControlCard
        user={mockSuspendedSaleng}
        onPenalize={vi.fn()}
        onReactivate={handleReactivate}
      />
    );

    const reactivateBtn = screen.getByTestId('btn-reactivate-user');
    fireEvent.click(reactivateBtn);

    expect(handleReactivate).toHaveBeenCalledTimes(1);
    expect(handleReactivate).toHaveBeenCalledWith('saleng-02', 'COLLECTOR');
  });

  it('triggers onReactivate callback for banned user when reactivate button is clicked', () => {
    const handleReactivate = vi.fn();
    render(
      <UserPenaltyControlCard
        user={mockBannedSeller}
        onPenalize={vi.fn()}
        onReactivate={handleReactivate}
      />
    );

    const reactivateBtn = screen.getByTestId('btn-reactivate-user');
    fireEvent.click(reactivateBtn);

    expect(handleReactivate).toHaveBeenCalledTimes(1);
    expect(handleReactivate).toHaveBeenCalledWith('seller-03', 'SELLER');
  });
});

