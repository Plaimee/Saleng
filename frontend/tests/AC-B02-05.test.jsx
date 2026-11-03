/**
 * Component Tests for AC-B02-05: Multi-Criteria Job Filtering, View Switching & Unverified Gate
 * (Task T-08: UC-04, REQ-FN-002, REQ-UX-001, CC-01, D-00-01, Q-03, Q-04, Q-05)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import JobSearchPanel from '../src/components/JobSearchPanel';
import { jobSearchApi } from '../src/services/jobSearchApi';

describe('AC-B02-05: Multi-Criteria Filtering, View Switcher & Gate Modal Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('switches between List View and Map View and applies category and weight filters', async () => {
    const mockJobs = [
      {
        order_id: 'order-s2-01',
        status: 'S2',
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        approximate_lat: 13.7950,
        approximate_lng: 100.5810,
        road_distance_km: 0.8,
        estimated_price_min: 150,
        estimated_price_max: 220,
        estimated_weight_kg: 25,
        categories: ['MAT-CARDBOARD'],
        need_lifting_help: false,
      },
    ];

    const getNearbyMock = vi.spyOn(jobSearchApi, 'getNearbyJobs').mockResolvedValue({
      total_count: 1,
      radius_km: 5.0,
      jobs: mockJobs,
      active_filters: {},
    });

    render(<JobSearchPanel />);

    // 1. ตรวจสอบปุ่มสลับ Tab (Segmented Control)
    const tabList = screen.getByTestId('tab-list-view');
    const tabMap = screen.getByTestId('tab-map-view');
    expect(tabList).not.toBeNull();
    expect(tabMap).not.toBeNull();

    // 2. สลับไป Map View
    fireEvent.click(tabMap);
    await waitFor(() => {
      expect(screen.getByTestId('job-map-view')).not.toBeNull();
    });

    // 3. สลับกลับมา List View
    fireEvent.click(tabList);
    await waitFor(() => {
      expect(screen.getByTestId('job-card-list')).not.toBeNull();
    });

    // 4. ทดสอบกดตัวกรองหมวดหมู่
    const catCardboardBtn = screen.getByTestId('filter-cat-MAT-CARDBOARD');
    fireEvent.click(catCardboardBtn);

    await waitFor(() => {
      expect(getNearbyMock).toHaveBeenCalled();
      const lastCall = getNearbyMock.mock.calls[getNearbyMock.mock.calls.length - 1][0];
      expect(lastCall.category).toBe('MAT-CARDBOARD');
    });

    // 5. ทดสอบกดตัวกรองน้ำหนัก
    const weightSmallBtn = screen.getByTestId('filter-weight-SMALL');
    fireEvent.click(weightSmallBtn);

    await waitFor(() => {
      const lastCall = getNearbyMock.mock.calls[getNearbyMock.mock.calls.length - 1][0];
      expect(lastCall.weight_range).toBe('SMALL');
    });
  });

  it('blocks unverified collector from claiming job and displays informative gate modal (D-00-01, Q-05)', async () => {
    const mockJobs = [
      {
        order_id: 'order-s2-01',
        status: 'S2',
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        approximate_lat: 13.7950,
        approximate_lng: 100.5810,
        road_distance_km: 0.8,
        estimated_price_min: 150,
        estimated_price_max: 220,
        estimated_weight_kg: 25,
        categories: ['MAT-CARDBOARD'],
        need_lifting_help: false,
      },
    ];

    vi.spyOn(jobSearchApi, 'getNearbyJobs').mockResolvedValue({
      total_count: 1,
      radius_km: 5.0,
      jobs: mockJobs,
      active_filters: {},
    });

    const onNavigateToKycMock = vi.fn();

    // ซาเล้งที่ยังไม่ผ่าน KYC (verified: false)
    const unverifiedProfile = {
      saleng_id: 'saleng-unverified',
      verified: false,
      kyc_status: 'PENDING_REVIEW',
    };

    render(
      <JobSearchPanel
        collectorProfile={unverifiedProfile}
        onNavigateToKyc={onNavigateToKycMock}
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId('job-card-order-s2-01')).not.toBeNull();
    });

    // ปุ่มรับงานต้องมีไอคอนล็อก
    const claimBtn = screen.getByTestId('btn-claim-order-s2-01');
    expect(claimBtn.textContent).toContain('ยืนยันตัวตนเพื่อรับงาน');

    // เมื่อกดปุ่มรับงาน
    fireEvent.click(claimBtn);

    // ต้องแสดง Gate Modal
    await waitFor(() => {
      const modal = screen.getByTestId('unverified-gate-modal');
      expect(modal).not.toBeNull();
      expect(screen.getByTestId('gate-modal-title').textContent).toContain('ยืนยันตัวตนก่อนรับงาน');
      expect(screen.getByTestId('gate-modal-message').textContent).toContain('เฉพาะซาเล้งที่ยืนยันตัวตน (KYC) แล้วเท่านั้น');
    });

    // กดปุ่มไปหน้า KYC ใน modal
    const toKycBtn = screen.getByTestId('btn-gate-to-kyc');
    fireEvent.click(toKycBtn);
    expect(onNavigateToKycMock).toHaveBeenCalledTimes(1);
  });
});

