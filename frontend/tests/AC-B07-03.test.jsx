/**
 * Component Tests for AC-B07-03: Seller Mismatch Report Modal
 * (Task T-07: UC-13, REQ-FN-006, CC-01, D-B07-01, D-B07-02)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SellerMismatchReportModal from '../src/components/SellerMismatchReportModal.jsx';

describe('AC-B07-03 Component Tests: SellerMismatchReportModal', () => {
  it('renders modal when open and submits dispute report', () => {
    const onSubmit = vi.fn();
    const onClose = vi.fn();

    render(
      <SellerMismatchReportModal
        orderId="order-101"
        isOpen={true}
        onClose={onClose}
        onSubmitReport={onSubmit}
      />
    );

    expect(screen.getByTestId('seller-mismatch-modal')).toBeDefined();
    expect(screen.getByTestId('mismatch-reason-select')).toBeDefined();
    expect(screen.getByTestId('evidence-photo-input')).toBeDefined();

    // เลือกสาเหตุและกรอกข้อมูล
    const reasonSelect = screen.getByTestId('mismatch-reason-select');
    fireEvent.change(reasonSelect, { target: { value: 'CONTAMINATED_WASTE' } });

    const photoInput = screen.getByTestId('evidence-photo-input');
    fireEvent.change(photoInput, { target: { value: 'https://storage.saleng.app/disp-1.jpg' } });

    const notesTextarea = screen.getByTestId('notes-textarea');
    fireEvent.change(notesTextarea, { target: { value: 'พบขยะเปียกและสารเคมีปนเปื้อน' } });

    const submitBtn = screen.getByTestId('submit-mismatch-btn');
    fireEvent.click(submitBtn);

    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit).toHaveBeenCalledWith({
      orderId: 'order-101',
      mismatchReason: 'CONTAMINATED_WASTE',
      evidencePhotoUrl: 'https://storage.saleng.app/disp-1.jpg',
      notes: 'พบขยะเปียกและสารเคมีปนเปื้อน',
    });
  });

  it('shows error banner when evidence photo is empty', () => {
    const onSubmit = vi.fn();

    render(
      <SellerMismatchReportModal
        orderId="order-101"
        isOpen={true}
        onSubmitReport={onSubmit}
      />
    );

    const photoInput = screen.getByTestId('evidence-photo-input');
    fireEvent.change(photoInput, { target: { value: '' } });

    const form = screen.getByTestId('seller-mismatch-modal').querySelector('form');
    fireEvent.submit(form);

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByTestId('modal-error-banner')).toBeDefined();
  });
});
