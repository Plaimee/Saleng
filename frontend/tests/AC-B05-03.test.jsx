/**
 * Component Tests สำหรับ AC-B05-03: Native Quick Call Launch
 * (T-08: UC-08, REQ-SEC-001, CC-01, AC-B05-03, D-B05-02)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatHeader from '../src/components/ChatHeader.jsx';

describe('AC-B05-03: Native Quick Call Launch Component Tests', () => {
  it('renders quick call button with tel: protocol and touch target >= 48px in status S3', () => {
    const handleCall = vi.fn();

    render(
      <ChatHeader
        orderId="order-call-test"
        orderStatus="S3"
        sellerName="คุณวิภาดา"
        sellerPhone="081-234-5678"
        phoneMasked={false}
        onCallClick={handleCall}
      />
    );

    const callBtn = screen.getByTestId('quick-call-btn');
    expect(callBtn).not.toBeNull();
    expect(callBtn.getAttribute('href')).toBe('tel:081-234-5678');
    expect(callBtn.className).toContain('min-h-[48px]');

    fireEvent.click(callBtn);
    expect(handleCall).toHaveBeenCalledWith('081-234-5678');
  });

  it('renders quick call button in S4 (In-Transit) status as active', () => {
    render(
      <ChatHeader
        orderId="order-call-s4"
        orderStatus="S4"
        sellerName="คุณวิภาดา"
        sellerPhone="081-234-5678"
        phoneMasked={false}
      />
    );

    const callBtn = screen.getByTestId('quick-call-btn');
    expect(callBtn).not.toBeNull();
    expect(callBtn.getAttribute('href')).toBe('tel:081-234-5678');
  });
});

