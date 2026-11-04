/**
 * Component Tests for AC-B06-01: Actual Weight Recording UI & Scale Photo Attachment
 * (Task T-08: UC-05, REQ-FN-002, D-B06-02)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import WeighingInputForm from '../src/components/WeighingInputForm.jsx';

describe('AC-B06-01 Component Tests: WeighingInputForm', () => {
  const mockItems = [
    {
      item_id: 'item-1',
      category_code: 'PAPER_BOX',
      category_name: 'กระดาษลัง',
      estimated_quantity: 20.0,
      locked_unit_price: 4.5,
      unit: 'กก.',
    },
    {
      item_id: 'item-2',
      category_code: 'GLASS_BOTTLE',
      category_name: 'ขวดแก้วใส',
      estimated_quantity: 10.0,
      locked_unit_price: 2.0,
      unit: 'กก.',
    },
  ];

  it('renders weighing form with locked prices and scale photo input', () => {
    render(<WeighingInputForm orderId="order-01" items={mockItems} />);

    expect(screen.getByTestId('weighing-input-form')).toBeDefined();
    expect(screen.getByText('กระดาษลัง')).toBeDefined();
    expect(screen.getByText('ขวดแก้วใส')).toBeDefined();
    expect(screen.getByTestId('input-scale-photo-url')).toBeDefined();
    expect(screen.getByTestId('submit-weighing-btn')).toBeDefined();
  });

  it('submits actual weights with scale photo url when valid', () => {
    const onSubmit = vi.fn();
    render(
      <WeighingInputForm
        orderId="order-01"
        items={mockItems}
        onSubmitWeighing={onSubmit}
      />
    );

    const inputWeight1 = screen.getByTestId('input-weight-item-1');
    const inputWeight2 = screen.getByTestId('input-weight-item-2');
    const photoInput = screen.getByTestId('input-scale-photo-url');
    const submitBtn = screen.getByTestId('submit-weighing-btn');

    fireEvent.change(inputWeight1, { target: { value: '25.0' } });
    fireEvent.change(inputWeight2, { target: { value: '12.0' } });
    fireEvent.change(photoInput, { target: { value: 'https://storage.saleng.app/photo.jpg' } });
    fireEvent.click(submitBtn);

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith({
      scalePhotoUrl: 'https://storage.saleng.app/photo.jpg',
      items: [
        { item_id: 'item-1', actual_quantity: 25.0 },
        { item_id: 'item-2', actual_quantity: 12.0 },
      ],
    });
  });

  it('shows error banner when scale photo is empty', () => {
    const onSubmit = vi.fn();
    render(
      <WeighingInputForm
        orderId="order-01"
        items={mockItems}
        initialScalePhotoUrl=""
        onSubmitWeighing={onSubmit}
      />
    );

    const inputWeight1 = screen.getByTestId('input-weight-item-1');
    fireEvent.change(inputWeight1, { target: { value: '20.0' } });

    const photoInput = screen.getByTestId('input-scale-photo-url');
    fireEvent.change(photoInput, { target: { value: '' } });

    const form = screen.getByTestId('weighing-input-form');
    fireEvent.submit(form);

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByTestId('weighing-error-banner')).toBeDefined();
  });
});
