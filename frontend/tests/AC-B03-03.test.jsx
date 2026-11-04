/**
 * Component Tests สำหรับ AC-B03-03: Online/Offline Toggle & Capacity Guard
 * (T-08: BR-03, REQ-CON-003, CC-02, D-B03-03, D-B03-04, D-B03-05)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import JobEvaluationView from '../src/components/JobEvaluationView';
import { jobEvaluationApi } from '../src/services/jobEvaluationApi';

describe('AC-B03-03: Online/Offline Toggle & Capacity Guard Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders overload alert and disables claim button when projected load exceeds 200 kg (BR-03)', async () => {
    const mockOverloadEval = {
      order_id: 'order-s2-overload',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.0,
      estimated_fuel_cost: 2.5,
      is_fallback_distance: false,
      total_est_weight_kg: 80.0,
      total_min_price: 400.0,
      total_max_price: 600.0,
      current_load_kg: 140.0, // 140 + 80 = 220 kg > 200 kg
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 60.0,
      projected_total_load_kg: 220.0,
      is_capacity_exceeded: true,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: false,
      claim_block_reason: 'CAPACITY_EXCEEDED',
      items: [
        {
          item_id: 'item-heavy',
          category_id: 'MAT-STEEL',
          category_name_th: 'เหล็กหนา/โครงสร้าง',
          est_weight_kg: 80.0,
          est_min_price: 400.0,
          est_max_price: 600.0,
          photo_urls: [],
          is_bulky: true,
        },
      ],
      location_summary: { subdistrict_name: 'แขวงสามเสนนอก', district_name: 'เขตห้วยขวาง' },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockOverloadEval);

    render(<JobEvaluationView orderId="order-s2-overload" salengId="saleng-01" />);

    await waitFor(() => {
      const alertEl = screen.getByTestId('capacity-overload-alert');
      expect(alertEl).not.toBeNull();
      expect(alertEl.textContent).toContain('น้ำหนักเกินความจุรถ');
    });

    // ตรวจสอบว่าปุ่มรับงานถูก Disable พร้อมแสดงข้อความเตือน
    const disabledBtn = screen.getByTestId('capacity-disabled-claim-button');
    expect(disabledBtn).not.toBeNull();
    expect(disabledBtn.textContent).toContain('น้ำหนักเกินความจุรถ');
    expect(disabledBtn.getAttribute('disabled')).not.toBeNull();
  });

  it('renders offline warning and disables claim button when collector is offline (CC-02, D-B03-05)', async () => {
    const mockOfflineEval = {
      order_id: 'order-s2-offline',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.0,
      estimated_fuel_cost: 2.5,
      is_fallback_distance: false,
      total_est_weight_kg: 20.0,
      total_min_price: 100.0,
      total_max_price: 150.0,
      current_load_kg: 30.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 170.0,
      projected_total_load_kg: 50.0,
      is_capacity_exceeded: false,
      collector_is_online: false, // ออฟไลน์
      collector_is_verified: true,
      can_claim_job: false,
      claim_block_reason: 'OFFLINE',
      items: [],
      location_summary: { subdistrict_name: 'แขวงสามเสนนอก', district_name: 'เขตห้วยขวาง' },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockOfflineEval);

    render(<JobEvaluationView orderId="order-s2-offline" salengId="saleng-01" />);

    await waitFor(() => {
      const offlineWarning = screen.getByTestId('offline-warning-badge');
      expect(offlineWarning).not.toBeNull();
    });

    const offlineBtn = screen.getByTestId('offline-disabled-claim-button');
    expect(offlineBtn).not.toBeNull();
    expect(offlineBtn.textContent).toContain('กรุณาเปิดสถานะ Online เพื่อรับงาน');
    expect(offlineBtn.getAttribute('disabled')).not.toBeNull();
  });

  it('triggers toggleOnlineStatus when online toggle button is clicked', async () => {
    const mockEval = {
      order_id: 'order-s2-online',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.0,
      estimated_fuel_cost: 2.5,
      is_fallback_distance: false,
      total_est_weight_kg: 20.0,
      total_min_price: 100.0,
      total_max_price: 150.0,
      current_load_kg: 30.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 170.0,
      projected_total_load_kg: 50.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: true,
      claim_block_reason: null,
      items: [],
      location_summary: { subdistrict_name: 'แขวงสามเสนนอก', district_name: 'เขตห้วยขวาง' },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockEval);
    const toggleSpy = vi.spyOn(jobEvaluationApi, 'toggleOnlineStatus').mockResolvedValue({
      saleng_id: 'saleng-01',
      is_online: false,
    });

    render(<JobEvaluationView orderId="order-s2-online" salengId="saleng-01" />);

    await waitFor(() => {
      const toggleBtn = screen.getByTestId('online-status-toggle');
      expect(toggleBtn).not.toBeNull();
    });

    const toggleBtn = screen.getByTestId('online-status-toggle');
    await act(async () => {
      fireEvent.click(toggleBtn);
    });

    expect(toggleSpy).toHaveBeenCalledWith('saleng-01', false);
  });
});
