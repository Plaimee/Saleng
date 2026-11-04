/**
 * Component Tests for AC-B06-03: 100% Confirmation Gate UI
 * (Task T-08: REQ-FN-004, AC-B06-03, D-B06-01)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SellerConfirmationGate from '../src/components/SellerConfirmationGate.jsx';

describe('AC-B06-03 Component Tests: SellerConfirmationGate', () => {
  it('displays waiting state when seller has not confirmed weight yet', () => {
    const onCheck = vi.fn();
    render(
      <SellerConfirmationGate
        orderId="order-01"
        sellerConfirmed={false}
        orderStatus="S5"
        totalAmount={250.0}
        onCheckStatus={onCheck}
      />
    );

    expect(screen.getByTestId('seller-confirmation-gate')).toBeDefined();
    expect(screen.getByTestId('gate-status-badge').textContent).toContain('S5');
    expect(screen.getByText(/รอผู้ขายตรวจสอบและยืนยันน้ำหนัก/)).toBeDefined();

    const checkBtn = screen.getByTestId('check-confirmation-btn');
    expect(checkBtn).toBeDefined();
    fireEvent.click(checkBtn);
    expect(onCheck).toHaveBeenCalledTimes(1);

    // Proceed to payment button should NOT be rendered when unconfirmed
    expect(screen.queryByTestId('proceed-to-payment-btn')).toBeNull();
  });

  it('displays confirmed state and proceed button when seller confirmed', () => {
    const onProceed = vi.fn();
    render(
      <SellerConfirmationGate
        orderId="order-01"
        sellerConfirmed={true}
        orderStatus="S6"
        totalAmount={250.0}
        onProceedToPayment={onProceed}
      />
    );

    expect(screen.getByTestId('gate-status-badge').textContent).toContain('S6');
    expect(screen.getByText(/ผู้ขายยืนยันน้ำหนักเรียบร้อยแล้ว/)).toBeDefined();

    const proceedBtn = screen.getByTestId('proceed-to-payment-btn');
    expect(proceedBtn).toBeDefined();
    fireEvent.click(proceedBtn);
    expect(onProceed).toHaveBeenCalledTimes(1);
  });
});

