/**
 * Vitest Component Test สำหรับ AC-A01-01: Driver KYC Queue & Inspection
 * รองรับ UC-11, REQ-QA-001, REQ-SEC-002, REQ-UX-001, CC-01, CC-06, D-00-01
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import KycReviewQueueCard from '../src/components/admin/KycReviewQueueCard';

describe('AC-A01-01: Driver KYC Queue & Inspection', () => {
  const mockSubmission = {
    id: 'kyc-sub-001',
    saleng_id: 'saleng-01',
    full_name: 'นายสมชาย ใจดี',
    id_card_no_masked: '1-1002-XXXXX-XX-X',
    id_card_photo_url: 'https://storage.saleng.app/kyc/saleng-01-id.jpg',
    selfie_with_id_photo_url: 'https://storage.saleng.app/kyc/saleng-01-selfie.jpg',
    vehicle_photo_url: 'https://storage.saleng.app/kyc/saleng-01-vehicle.jpg',
    vehicle_plate: '1กข-9999 กทม.',
    status: 'PENDING_REVIEW',
    submitted_at: '2026-11-04T10:00:00Z',
  };

  it('renders driver KYC card with PII-masked Thai ID card (REQ-SEC-002, CC-06)', () => {
    render(
      <KycReviewQueueCard
        submission={mockSubmission}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />
    );

    // Displays name and saleng ID
    expect(screen.getByText('นายสมชาย ใจดี')).not.toBeNull();
    expect(screen.getByText(/saleng-01/)).not.toBeNull();

    // Masked Thai ID card according to REQ-SEC-002
    const maskedIdEl = screen.getByTestId('masked-id-card');
    expect(maskedIdEl.textContent).toBe('1-1002-XXXXX-XX-X');
    expect(maskedIdEl.textContent).not.toContain('12345');
  });

  it('renders 3 evidence photos: id card, selfie with id, and vehicle photo (AC-A01-01)', () => {
    render(
      <KycReviewQueueCard
        submission={mockSubmission}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />
    );

    const idCardImg = screen.getByTestId('kyc-img-id-card');
    const selfieImg = screen.getByTestId('kyc-img-selfie');
    const vehicleImg = screen.getByTestId('kyc-img-vehicle');

    expect(idCardImg.getAttribute('src')).toBe(mockSubmission.id_card_photo_url);
    expect(selfieImg.getAttribute('src')).toBe(mockSubmission.selfie_with_id_photo_url);
    expect(vehicleImg.getAttribute('src')).toBe(mockSubmission.vehicle_photo_url);

    // Vehicle plate
    expect(screen.getByText(/1กข-9999 กทม\./)).not.toBeNull();
  });

  it('has approve and reject buttons with touch targets >= 48px (REQ-UX-001, CC-01)', () => {
    render(
      <KycReviewQueueCard
        submission={mockSubmission}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />
    );

    const approveBtn = screen.getByTestId('btn-approve-kyc');
    const rejectBtn = screen.getByTestId('btn-reject-kyc');

    expect(approveBtn.className).toContain('min-h-[48px]');
    expect(rejectBtn.className).toContain('min-h-[48px]');
  });
});

