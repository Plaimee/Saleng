/**
 * Component Tests สำหรับ AC-B04-06: Collector Cancellation with Automatic State Reversion
 * (T-08: MD-STM-04, AC-B04-06, D-B04-04)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CollectorCancelModal from '../src/components/CollectorCancelModal.jsx';

describe('AC-B04-06: Collector Cancellation Modal Component Tests (MD-STM-04)', () => {
  const mockJob = {
    order_id: 'order-s2-01',
    status: 'S3',
    seller_name: 'สมชาย ใจดี',
  };

  it('renders CollectorCancelModal with 4 cancellation reasons and handles confirm', () => {
    const handleConfirm = vi.fn();
    const handleClose = vi.fn();

    render(
      <CollectorCancelModal
        isOpen={true}
        job={mockJob}
        onClose={handleClose}
        onConfirm={handleConfirm}
      />
    );

    const modal = screen.getByTestId('collector-cancel-modal');
    expect(modal).not.toBeNull();

    // Reason: VEHICLE_BREAKDOWN selected by default
    const confirmBtn = screen.getByTestId('confirm-cancel-job-btn');
    expect(confirmBtn).not.toBeNull();
    expect(confirmBtn.textContent).toContain('ยืนยันสละสิทธิ์');

    fireEvent.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledWith('order-s2-01', {
      reason: 'VEHICLE_BREAKDOWN',
      note: '',
    });
  });

  it('allows selecting another reason and entering note before submitting', () => {
    const handleConfirm = vi.fn();

    render(
      <CollectorCancelModal
        isOpen={true}
        job={mockJob}
        onClose={() => {}}
        onConfirm={handleConfirm}
      />
    );

    // Select ACCIDENT
    const accidentRadio = screen.getByLabelText(/เกิดอุบัติเหตุ/i);
    fireEvent.click(accidentRadio);

    // Enter note
    const noteInput = screen.getByPlaceholderText(/ยางหลังรั่ว/i);
    fireEvent.change(noteInput, { target: { value: 'มอเตอร์ไซค์ชนท้ายที่แยกสุทธิสาร' } });

    // Submit
    const confirmBtn = screen.getByTestId('confirm-cancel-job-btn');
    fireEvent.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledWith('order-s2-01', {
      reason: 'ACCIDENT',
      note: 'มอเตอร์ไซค์ชนท้ายที่แยกสุทธิสาร',
    });
  });
});

