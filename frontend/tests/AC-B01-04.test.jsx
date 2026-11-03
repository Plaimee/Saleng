/**
 * Vitest Component Test สำหรับ AC-B01-04: Unverified Collector Job Claim Block Gate
 * รองรับ D-00-01, REQ-UX-001, CC-01, AC-B01-04, Q-05, P-05
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CollectorAccountPanel from '../src/components/CollectorAccountPanel';
import { collectorAccountApi } from '../src/services/collectorAccountApi';

describe('AC-B01-04: Unverified Collector Job Claim Gate (D-00-01)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('blocks unverified collector from claiming job and shows informative gate modal (D-00-01, Q-05)', async () => {
    const unverifiedProfile = {
      saleng_id: 'saleng-05',
      display_name: 'เอกชัย ยังไม่ยืนยัน',
      phone_masked: '08X-XXX-4444',
      verified: false,
      kyc_status: 'UNVERIFIED',
      vehicle_type: 'TRICYCLE',
      max_capacity_kg: 150.0,
      rating: 4.0,
      completed_jobs_count: 0,
    };

    vi.spyOn(collectorAccountApi, 'getStoredSession').mockReturnValue({
      token: 'saleng_tok_05',
      ...unverifiedProfile,
    });
    vi.spyOn(collectorAccountApi, 'getProfile').mockResolvedValue(unverifiedProfile);
    vi.spyOn(collectorAccountApi, 'checkJobClaimGate').mockResolvedValue({
      can_claim_job: false,
      error_detail: 'ท่านยังไม่ได้ยื่นเอกสารยืนยันตัวตน (KYC) กรุณาส่งเอกสารก่อนกดรับงาน',
    });

    render(<CollectorAccountPanel />);

    await waitFor(() => {
      expect(screen.getByTestId('test-claim-job-btn')).not.toBeNull();
    });

    // ซาเล้งกดปุ่มรับงาน
    const claimBtn = screen.getByTestId('test-claim-job-btn');
    fireEvent.click(claimBtn);

    // ต้องปรากฏ Gate Modal บล็อกการรับงาน
    await waitFor(() => {
      const modal = screen.getByTestId('unverified-gate-modal');
      expect(modal).not.toBeNull();
      expect(modal.textContent).toContain('ไม่สามารถรับงานได้');
      expect(modal.textContent).toContain('ท่านยังไม่ได้ยื่นเอกสารยืนยันตัวตน (KYC)');
      expect(screen.getByTestId('modal-goto-kyc-btn')).not.toBeNull();
    });
  });

  it('permits verified collector to claim job (D-00-01)', async () => {
    const verifiedProfile = {
      saleng_id: 'saleng-01',
      display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
      phone_masked: '08X-XXX-5678',
      verified: true,
      kyc_status: 'VERIFIED',
      vehicle_type: 'TRICYCLE',
      max_capacity_kg: 200.0,
      rating: 4.9,
      completed_jobs_count: 142,
    };

    vi.spyOn(collectorAccountApi, 'getStoredSession').mockReturnValue({
      token: 'saleng_tok_01',
      ...verifiedProfile,
    });
    vi.spyOn(collectorAccountApi, 'getProfile').mockResolvedValue(verifiedProfile);
    vi.spyOn(collectorAccountApi, 'checkJobClaimGate').mockResolvedValue({
      can_claim_job: true,
      verified: true,
      kyc_status: 'VERIFIED',
    });

    render(<CollectorAccountPanel />);

    await waitFor(() => {
      expect(screen.getByTestId('test-claim-job-btn')).not.toBeNull();
    });

    const claimBtn = screen.getByTestId('test-claim-job-btn');
    fireEvent.click(claimBtn);

    await waitFor(() => {
      const modal = screen.getByTestId('unverified-gate-modal');
      expect(modal).not.toBeNull();
      expect(modal.textContent).toContain('สามารถรับงานได้');
    });
  });
});

