/**
 * Vitest Component Test สำหรับ AC-B01-03: Thai-ID / DBD-ID KYC Submission & Lifecycle Status
 * รองรับ SC-04, D-00-01, REQ-UX-001, CC-01, AC-B01-03, Q-02, Q-03, P-03
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import KycStatusBanner from '../src/components/KycStatusBanner';
import KycSubmissionModal from '../src/components/KycSubmissionModal';
import { collectorAccountApi } from '../src/services/collectorAccountApi';

describe('AC-B01-03: KYC Submission & Status Lifecycle', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('displays appropriate banners across all 4 KYC lifecycle states (Q-03)', () => {
    // 1. UNVERIFIED
    const { rerender } = render(
      <KycStatusBanner profile={{ kyc_status: 'UNVERIFIED' }} onOpenKycModal={vi.fn()} />
    );
    expect(screen.getByTestId('kyc-banner-unverified')).not.toBeNull();
    expect(screen.getByTestId('start-kyc-btn')).not.toBeNull();

    // 2. PENDING_REVIEW
    rerender(
      <KycStatusBanner profile={{ kyc_status: 'PENDING_REVIEW' }} onOpenKycModal={vi.fn()} />
    );
    expect(screen.getByTestId('kyc-banner-pending')).not.toBeNull();
    expect(screen.getByTestId('kyc-banner-pending').textContent).toContain('อยู่ระหว่างการตรวจสอบ');

    // 3. REJECTED
    rerender(
      <KycStatusBanner
        profile={{ kyc_status: 'REJECTED', rejection_reason: 'รูปบัตรไม่ชัดเจน' }}
        onOpenKycModal={vi.fn()}
      />
    );
    expect(screen.getByTestId('kyc-banner-rejected')).not.toBeNull();
    expect(screen.getByTestId('kyc-banner-rejected').textContent).toContain('รูปบัตรไม่ชัดเจน');
    expect(screen.getByTestId('retry-kyc-btn')).not.toBeNull();

    // 4. VERIFIED
    rerender(
      <KycStatusBanner profile={{ kyc_status: 'VERIFIED' }} onOpenKycModal={vi.fn()} />
    );
    expect(screen.getByTestId('kyc-banner-verified')).not.toBeNull();
    expect(screen.getByTestId('kyc-banner-verified').textContent).toContain('ผ่านการยืนยันตัวตนแล้ว');
  });

  it('submits KYC documents with 13-digit Thai-ID and photo evidence (Q-02)', async () => {
    vi.spyOn(collectorAccountApi, 'submitKyc').mockResolvedValue({
      saleng_id: 'saleng-01',
      kyc_status: 'PENDING_REVIEW',
      verified: false,
      id_card_masked: '1-XXXX-XXXXX-61',
      full_name: 'นายสมชาย มั่นคง',
    });

    const onSubmitted = vi.fn();
    const onClose = vi.fn();

    render(
      <KycSubmissionModal
        salengId="saleng-01"
        isOpen={true}
        onClose={onClose}
        onKycSubmitted={onSubmitted}
      />
    );

    const idInput = screen.getByTestId('id-card-input');
    const nameInput = screen.getByTestId('full-name-input');
    const submitBtn = screen.getByTestId('submit-kyc-btn');

    fireEvent.change(idInput, { target: { value: '1100701234561' } });
    fireEvent.change(nameInput, { target: { value: 'นายสมชาย มั่นคง' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(collectorAccountApi.submitKyc).toHaveBeenCalledWith(
        'saleng-01',
        expect.objectContaining({
          id_card_no: '1100701234561',
          full_name: 'นายสมชาย มั่นคง',
        })
      );
      expect(onSubmitted).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });
});

