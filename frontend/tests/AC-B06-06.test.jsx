/**
 * Component Tests for AC-B06-06: BillingReceiptView Main Orchestrator & Offline Queue
 * (Task T-08: CC-05, REQ-OP-001, D-B06-05)
 */

import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import BillingReceiptView from '../src/components/BillingReceiptView.jsx';
import { billingReceiptApi } from '../src/services/billingReceiptApi.js';

describe('AC-B06-06 Component Tests: BillingReceiptView Orchestrator', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('renders weighing form when order is in S4 status', async () => {
    vi.spyOn(billingReceiptApi, 'getWeighingSheet').mockResolvedValue({
      order_id: 'order-101',
      order_status: 'S4',
      seller_name: 'คุณสมศรี',
      seller_phone_masked: '08X-XXX-4567',
      seller_confirmed_weight: false,
      items: [
        {
          item_id: 'it-1',
          category_code: 'PAPER_BOX',
          category_name: 'กระดาษลัง',
          estimated_quantity: 20.0,
          locked_unit_price: 4.5,
          unit: 'กก.',
        },
      ],
    });

    render(<BillingReceiptView orderId="order-101" salengId="saleng-01" />);

    await waitFor(() => {
      expect(screen.getByTestId('billing-receipt-view')).toBeDefined();
      expect(screen.getByTestId('weighing-input-form')).toBeDefined();
    });
  });

  it('renders confirmation gate when order is in S5 status awaiting seller', async () => {
    vi.spyOn(billingReceiptApi, 'getWeighingSheet').mockResolvedValue({
      order_id: 'order-102',
      order_status: 'S5',
      seller_name: 'คุณวิภาดา',
      seller_phone_masked: '08X-XXX-1234',
      seller_confirmed_weight: false,
      total_settled_amount: 300.0,
      items: [],
    });

    render(<BillingReceiptView orderId="order-102" salengId="saleng-01" />);

    await waitFor(() => {
      expect(screen.getByTestId('seller-confirmation-gate')).toBeDefined();
      expect(screen.queryByTestId('weighing-input-form')).toBeNull();
    });
  });

  it('renders payment method selector when order is in S6 status', async () => {
    vi.spyOn(billingReceiptApi, 'getWeighingSheet').mockResolvedValue({
      order_id: 'order-103',
      order_status: 'S6',
      seller_name: 'คุณวิภาดา',
      seller_phone_masked: '08X-XXX-1234',
      seller_confirmed_weight: true,
      total_settled_amount: 300.0,
      items: [],
    });

    render(<BillingReceiptView orderId="order-103" salengId="saleng-01" />);

    await waitFor(() => {
      expect(screen.getByTestId('payment-method-selector')).toBeDefined();
    });
  });
});

