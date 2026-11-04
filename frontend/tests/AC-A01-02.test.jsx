/**
 * Vitest Component Test สำหรับ AC-A01-02: Driver KYC Approval & Rejection
 * รองรับ UC-11, D-00-01, REQ-SEC-001, REQ-UX-001, AC-A01-02
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import KycReviewQueueCard from '../src/components/admin/KycReviewQueueCard';

describe('AC-A01-02: Driver KYC Approval & Rejection', () => {
  const mockSubmission = {
    id: 'kyc-sub-002',
    saleng_id: 'saleng-02',
    full_name: 'นายประสิทธิ์ มั่นคง',
    id_card_no_masked: '1-1002-XXXXX-XX-X',
    id_card_photo_url: 'https://storage.saleng.app/kyc/saleng-02-id.jpg',
    selfie_with_id_photo_url: 'https://storage.saleng.app/kyc/saleng-02-selfie.jpg',
    vehicle_photo_url: 'https://storage.saleng.app/kyc/saleng-02-vehicle.jpg',
    vehicle_plate: '2กค-1234 กทม.',
    status: 'PENDING_REVIEW',
    submitted_at: '2026-11-04T10:00:00Z',
  };

  it('triggers onApprove callback with submission_id when approve button is clicked (D-00-01)', () => {
    const handleApprove = vi.fn();
    render(
      <KycReviewQueueCard
        submission={mockSubmission}
        onApprove={handleApprove}
        onReject={vi.fn()}
      />
    );

    const approveBtn = screen.getByTestId('btn-approve-kyc');
    fireEvent.click(approveBtn);

    expect(handleApprove).toHaveBeenCalledTimes(1);
    expect(handleApprove).toHaveBeenCalledWith('kyc-sub-002');
  });

  it('opens rejection modal, enforces mandatory rejection reason, and calls onReject (AC-A01-02)', () => {
    const handleReject = vi.fn();
    render(
      <KycReviewQueueCard
        submission={mockSubmission}
        onApprove={vi.fn()}
        onReject={handleReject}
      />
    );

    // Click reject button
    const rejectBtn = screen.getByTestId('btn-reject-kyc');
    fireEvent.click(rejectBtn);

    // Modal opens
    const modal = screen.getByTestId('kyc-reject-modal');
    expect(modal).not.toBeNull();

    // Submit empty reason -> validation error
    const confirmBtn = screen.getByTestId('btn-confirm-reject');
    fireEvent.click(confirmBtn);

    const errorMsg = screen.getByTestId('reject-modal-error');
    expect(errorMsg.textContent).toContain('กรุณาระบุเหตุผลการปฏิเสธ');
    expect(handleReject).not.toHaveBeenCalled();

    // Fill valid reason
    const textarea = screen.getByTestId('rejection-reason-input');
    fireEvent.change(textarea, { target: { value: 'ภาพถ่ายบัตรประชาชนไม่ชัดเจน ไม่สามารถอ่านตัวหนังสือได้' } });

    // Confirm reject
    fireEvent.click(confirmBtn);

    expect(handleReject).toHaveBeenCalledTimes(1);
    expect(handleReject).toHaveBeenCalledWith(
      'kyc-sub-002',
      'ภาพถ่ายบัตรประชาชนไม่ชัดเจน ไม่สามารถอ่านตัวหนังสือได้'
    );
  });
});

