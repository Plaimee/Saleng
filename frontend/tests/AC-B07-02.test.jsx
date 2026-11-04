/**
 * Component Tests for AC-B07-02: Regular Customer List & Notes
 * (Task T-07: UC-10, REQ-SEC-002, CC-01, CC-06, D-B07-03)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import RegularCustomerList from '../src/components/RegularCustomerList.jsx';

describe('AC-B07-02 Component Tests: RegularCustomerList', () => {
  const mockCustomers = [
    {
      id: 'fav-1',
      seller_id: 'seller-01',
      seller_name: 'คุณวิภาดา ซอยอารีย์',
      seller_phone_masked: '08X-XXX-4567',
      latitude: 13.7563,
      longitude: 100.5018,
      notes: 'บ้านรั้วสีฟ้า สะดวกเสาร์-อาทิตย์ มีทองแดงบ่อย',
    },
  ];

  it('renders regular customer card with notes and map navigation link', () => {
    render(<RegularCustomerList customers={mockCustomers} />);

    expect(screen.getByTestId('customer-name').textContent).toContain('คุณวิภาดา ซอยอารีย์');
    expect(screen.getByTestId('customer-phone').textContent).toContain('08X-XXX-4567');
    expect(screen.getByTestId('customer-notes').textContent).toContain('บ้านรั้วสีฟ้า สะดวกเสาร์-อาทิตย์');

    const mapLink = screen.getByTestId('navigate-map-btn');
    expect(mapLink.getAttribute('href')).toContain('13.7563,100.5018');
  });

  it('triggers onRemoveCustomer callback when clicking remove button', () => {
    const onRemove = vi.fn();
    render(<RegularCustomerList customers={mockCustomers} onRemoveCustomer={onRemove} />);

    const removeBtn = screen.getByTestId('remove-customer-btn');
    fireEvent.click(removeBtn);
    expect(onRemove).toHaveBeenCalledWith('seller-01');
  });

  it('renders empty state when no regular customers', () => {
    render(<RegularCustomerList customers={[]} />);
    expect(screen.getByTestId('empty-regular-customers')).toBeDefined();
  });
});

