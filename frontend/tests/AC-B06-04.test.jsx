/**
 * Component Tests for AC-B06-04: Payment Method Selection UI
 * (Task T-08: UC-06, REQ-FN-004, D-B06-04)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PaymentMethodSelector from '../src/components/PaymentMethodSelector.jsx';

describe('AC-B06-04 Component Tests: PaymentMethodSelector', () => {
  it('allows selection of CASH and submits', () => {
    const onSelect = vi.fn();
    render(
      <PaymentMethodSelector
        orderId="order-01"
        totalAmount={500.0}
        onSelectPaymentMethod={onSelect}
      />
    );

    expect(screen.getByTestId('payment-method-selector')).toBeDefined();
    expect(screen.getByTestId('payment-total-amount').textContent).toContain('500.00');

    const confirmBtn = screen.getByTestId('confirm-payment-method-btn');
    fireEvent.click(confirmBtn);

    expect(onSelect).toHaveBeenCalledWith('CASH');
  });

  it('allows selection of PROMPTPAY and shows promptpay instructions', () => {
    const onSelect = vi.fn();
    render(
      <PaymentMethodSelector
        orderId="order-01"
        totalAmount={500.0}
        onSelectPaymentMethod={onSelect}
      />
    );

    const promptpayOption = screen.getByTestId('option-promptpay');
    fireEvent.click(promptpayOption);

    expect(screen.getByTestId('promptpay-instructions')).toBeDefined();

    const confirmBtn = screen.getByTestId('confirm-payment-method-btn');
    fireEvent.click(confirmBtn);

    expect(onSelect).toHaveBeenCalledWith('PROMPTPAY');
  });
});

