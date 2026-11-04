/**
 * Component Tests สำหรับ AC-B05-04: Pre-Claim Privacy Guard in Status S2
 * (T-08: REQ-SEC-002, CC-06, AC-B05-04, D-B05-01)
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ChatHeader from '../src/components/ChatHeader.jsx';

describe('AC-B05-04: Pre-Claim Privacy Guard Component Tests', () => {
  it('disables and locks call button in status S2 when phone is masked', () => {
    render(
      <ChatHeader
        orderId="order-s2-test"
        orderStatus="S2"
        sellerName="คุณวิภาดา"
        sellerPhone={null}
        phoneMasked={true}
      />
    );

    // ตรวจสอบว่าไม่มีปุ่มโทรด่วนปกติ
    const activeCallBtn = screen.queryByTestId('quick-call-btn');
    expect(activeCallBtn).toBeNull();

    // มีปุ่มล็อกแจ้งเตือนว่ารับงานก่อนโทร
    const disabledBtn = screen.getByTestId('quick-call-btn-disabled');
    expect(disabledBtn).not.toBeNull();
    expect(disabledBtn.disabled).toBe(true);
    expect(disabledBtn.textContent).toContain('รับงานก่อนโทร');
  });
});
