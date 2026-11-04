/**
 * Component Tests for AC-B07-01: Purchase History Log & PII Masking
 * (Task T-07: UC-10, REQ-FN-005, REQ-SEC-002, CC-06, D-B07-05)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PurchaseHistoryCard from '../src/components/PurchaseHistoryCard.jsx';

describe('AC-B07-01 Component Tests: PurchaseHistoryCard', () => {
  const mockItem = {
    order_id: 'order-b07-01',
    completed_at: '2026-11-04T10:30:00Z',
    seller_name: 'คุณวิภาดา รักษ์โลก',
    seller_phone_masked: '08X-XXX-4567',
    total_settled_amount: 350.0,
    total_weight_kg: 70.0,
    payment_method: 'PROMPTPAY',
    status: 'S7',
    is_regular_customer: false,
    items_summary: 'กระดาษลัง (50 กก.), ขวดแก้วใส (20 กก.)',
  };

  it('renders completed order with masked phone and settled amount', () => {
    render(<PurchaseHistoryCard item={mockItem} />);

    expect(screen.getByTestId('order-id').textContent).toContain('order-b07-01');
    expect(screen.getByTestId('seller-name').textContent).toContain('คุณวิภาดา รักษ์โลก');
    expect(screen.getByTestId('seller-phone-masked').textContent).toBe('08X-XXX-4567');
    expect(screen.getByTestId('total-amount').textContent).toContain('350.00');
    expect(screen.getByTestId('status-badge').textContent).toContain('S7 สำเร็จ');
  });

  it('triggers onViewReceipt and onToggleRegularCustomer callbacks', () => {
    const onViewReceipt = vi.fn();
    const onToggle = vi.fn();

    render(
      <PurchaseHistoryCard
        item={mockItem}
        onViewReceipt={onViewReceipt}
        onToggleRegularCustomer={onToggle}
      />
    );

    const receiptBtn = screen.getByTestId('view-receipt-btn');
    fireEvent.click(receiptBtn);
    expect(onViewReceipt).toHaveBeenCalledWith('order-b07-01');

    const toggleBtn = screen.getByTestId('toggle-regular-customer-btn');
    fireEvent.click(toggleBtn);
    expect(onToggle).toHaveBeenCalledWith(mockItem);
  });
});

