/**
 * Component Tests for AC-B06-02: Price Calculation Preview & ±15% Re-quote Threshold
 * (Task T-08: REQ-BR-002, D-B06-03, MD-STM-04)
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import WeighingInputForm from '../src/components/WeighingInputForm.jsx';

describe('AC-B06-02 Component Tests: Price Calculation & Re-quote Warning', () => {
  const mockItems = [
    {
      item_id: 'item-1',
      category_code: 'PAPER_BOX',
      category_name: 'กระดาษลัง',
      estimated_quantity: 100.0,
      locked_unit_price: 5.0,
      unit: 'กก.',
    },
  ];

  it('calculates live total using locked rate (100 kg * 5.0 = 500.00)', () => {
    render(<WeighingInputForm orderId="order-01" items={mockItems} />);

    const inputWeight = screen.getByTestId('input-weight-item-1');
    fireEvent.change(inputWeight, { target: { value: '100.0' } });

    const totalPreview = screen.getByTestId('total-settled-preview');
    expect(totalPreview.textContent).toContain('500.00');
    // Difference is 0%, no re-quote warning
    expect(screen.queryByTestId('re-quote-warning')).toBeNull();
  });

  it('displays re-quote warning banner when difference exceeds 15% (e.g. 130 kg vs 100 kg)', () => {
    render(<WeighingInputForm orderId="order-01" items={mockItems} />);

    const inputWeight = screen.getByTestId('input-weight-item-1');
    fireEvent.change(inputWeight, { target: { value: '130.0' } }); // +30% diff

    const totalPreview = screen.getByTestId('total-settled-preview');
    expect(totalPreview.textContent).toContain('650.00');

    const warning = screen.getByTestId('re-quote-warning');
    expect(warning).toBeDefined();
    expect(warning.textContent).toContain('±15%');
  });
});

