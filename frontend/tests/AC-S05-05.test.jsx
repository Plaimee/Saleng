/**
 * Vitest Component Test สำหรับ AC-S05-05: CancelBookingModal & Reason Submission
 * รองรับ UC-04, BR-03, REQ-SEC-001, AC-S05-05, P-03, P-05
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CancelBookingModal from '../src/components/CancelBookingModal';

describe('AC-S05-05: CancelBookingModal Component Test', () => {
  it('does not render when isOpen is false', () => {
    render(<CancelBookingModal isOpen={false} />);
    expect(screen.queryByTestId('cancel-modal')).toBeNull();
  });

  it('renders and selects preset reason to confirm cancellation', () => {
    const handleConfirm = vi.fn();
    const handleClose = vi.fn();
    render(
      <CancelBookingModal
        isOpen={true}
        onClose={handleClose}
        onConfirmCancel={handleConfirm}
      />
    );

    expect(screen.getByTestId('cancel-modal')).not.toBeNull();

    // กดยืนยันด้วยเหตุผลแรก
    const confirmBtn = screen.getByTestId('confirm-cancel-btn');
    fireEvent.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledWith('ติดธุระด่วน ไม่สะดวกอยู่บ้านในเวลาดังกล่าว');
  });

  it('allows custom reason input and calls onClose when clicking close button', () => {
    const handleConfirm = vi.fn();
    const handleClose = vi.fn();
    render(
      <CancelBookingModal
        isOpen={true}
        onClose={handleClose}
        onConfirmCancel={handleConfirm}
      />
    );

    // เลือกเหตุผลอื่นๆ
    const customRadio = screen.getByLabelText('ระบุเหตุผลอื่นๆ');
    fireEvent.click(customRadio);

    // พิมพ์เหตุผล
    const textarea = screen.getByTestId('cancel-reason-input');
    expect(textarea).not.toBeNull();
    fireEvent.change(textarea, { target: { value: 'ฝนตกหนักน้ำท่วมซอยเข้าบ้านไม่ได้' } });

    // ยืนยัน
    const confirmBtn = screen.getByTestId('confirm-cancel-btn');
    fireEvent.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledWith('ฝนตกหนักน้ำท่วมซอยเข้าบ้านไม่ได้');

    // กดปุ่มปิด
    const closeBtn = screen.getByTestId('btn-close-cancel-modal');
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

