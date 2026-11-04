/**
 * Component Tests for AC-B06-05: Digital Receipt Display & PII Masking
 * (Task T-08: UC-07, REQ-FN-005, REQ-SEC-002, CC-06)
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import DigitalReceiptCard from '../src/components/DigitalReceiptCard.jsx';

describe('AC-B06-05 Component Tests: DigitalReceiptCard', () => {
  const mockReceipt = {
    receipt_id: 'REC-20261104-AC05',
    issued_at: '2026-11-04T10:00:00Z',
    seller_name: 'คุณสมศรี',
    seller_phone_masked: '08X-XXX-4567',
    collector_name: 'สมชาย ซาเล้ง',
    collector_phone_masked: '08X-XXX-8901',
    payment_method: 'PROMPTPAY',
    total_settled_amount: 350.0,
    items: [
      {
        category_name: 'กระดาษลัง',
        actual_quantity: 70.0,
        unit: 'กก.',
        locked_unit_price: 5.0,
        settled_item_price: 350.0,
      },
    ],
  };

  it('renders digital receipt with masked phone numbers and settled amount', () => {
    render(<DigitalReceiptCard receipt={mockReceipt} />);

    expect(screen.getByTestId('digital-receipt-card')).toBeDefined();
    expect(screen.getByTestId('receipt-no').textContent).toContain('REC-20261104-AC05');
    expect(screen.getByTestId('receipt-phones').textContent).toContain('08X-XXX-4567');
    expect(screen.getByTestId('collector-phone').textContent).toContain('08X-XXX-8901');
    expect(screen.getByTestId('receipt-total').textContent).toContain('350.00');
    expect(screen.getByText('กระดาษลัง')).toBeDefined();
  });
});

