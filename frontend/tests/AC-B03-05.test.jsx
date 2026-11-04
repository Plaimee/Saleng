/**
 * Component Tests สำหรับ AC-B03-05: Unverified Collector Claim Gate Integration
 * (T-08: D-00-01, AC-B03-05, D-B03-06)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import JobEvaluationView from '../src/components/JobEvaluationView';
import { jobEvaluationApi } from '../src/services/jobEvaluationApi';

describe('AC-B03-05: Unverified Collector Claim Gate Integration Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders locked claim button 🔒 and opens KYC gate modal when clicked by unverified collector', async () => {
    const mockUnverifiedEval = {
      order_id: 'order-s2-kyc-gate',
      collector_id: 'saleng-unverified',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.5,
      estimated_fuel_cost: 3.75,
      is_fallback_distance: false,
      total_est_weight_kg: 20.0,
      total_min_price: 100.0,
      total_max_price: 150.0,
      current_load_kg: 0.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 200.0,
      projected_total_load_kg: 20.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: false, // ยังไม่ผ่าน KYC
      can_claim_job: false,
      claim_block_reason: 'UNVERIFIED_KYC',
      items: [],
      location_summary: { subdistrict_name: 'แขวงสามเสนนอก', district_name: 'เขตห้วยขวาง' },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockUnverifiedEval);

    const onKycSpy = vi.fn();

    render(
      <JobEvaluationView
        orderId="order-s2-kyc-gate"
        salengId="saleng-unverified"
        onNavigateKyc={onKycSpy}
      />
    );

    // ตรวจสอบว่ามีปุ่มล็อกรูปกุญแจ 🔒
    await waitFor(() => {
      const lockBtn = screen.getByTestId('unverified-claim-button');
      expect(lockBtn).not.toBeNull();
      expect(lockBtn.textContent).toContain('ยืนยันตัวตนเพื่อรับงาน');
    });

    // คลิกที่ปุ่มล็อก
    const lockBtn = screen.getByTestId('unverified-claim-button');
    fireEvent.click(lockBtn);

    // ตรวจสอบว่า Gate Modal ปรากฏขึ้น
    const modal = screen.getByTestId('kyc-gate-modal');
    expect(modal).not.toBeNull();
    expect(modal.textContent).toContain('ต้องยืนยันตัวตน (KYC) ก่อนรับงาน');

    // คลิกปุ่ม "ไปหน้ายืนยันตัวตน (KYC)"
    const kycBtn = screen.getByTestId('go-to-kyc-button');
    expect(kycBtn).not.toBeNull();
    fireEvent.click(kycBtn);

    expect(onKycSpy).toHaveBeenCalled();
  });
});

