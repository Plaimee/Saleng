/**
 * Component Tests สำหรับ AC-B03-01: Distance & Fuel Cost Estimation
 * (T-08: UC-04, Card 02, REQ-FN-002, REQ-QA-002, AC-04-11, D-B03-01)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import JobEvaluationView from '../src/components/JobEvaluationView';
import { jobEvaluationApi } from '../src/services/jobEvaluationApi';

describe('AC-B03-01: Distance & Fuel Cost Estimation Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders fuel cost and distance according to vehicle type (MOTORCYCLE rate = 2.50 THB/km)', async () => {
    const mockEval = {
      order_id: 'order-s2-01',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 2.0,
      estimated_fuel_cost: 5.0,
      is_fallback_distance: false,
      total_est_weight_kg: 30.0,
      total_min_price: 180.0,
      total_max_price: 260.0,
      current_load_kg: 50.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 150.0,
      projected_total_load_kg: 80.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: true,
      claim_block_reason: null,
      items: [
        {
          item_id: 'item-01',
          category_id: 'MAT-CARDBOARD',
          category_name_th: 'ลังกระดาษ/กระดาษลูกฟูก',
          est_weight_kg: 30.0,
          est_min_price: 180.0,
          est_max_price: 260.0,
          photo_urls: ['https://example.com/cardboard.jpg'],
          is_bulky: false,
        },
      ],
      location_summary: {
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        fuzzed_lat: 13.795,
        fuzzed_lng: 100.581,
      },
      need_lifting_help: true,
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockEval);

    render(<JobEvaluationView orderId="order-s2-01" salengId="saleng-01" />);

    // รอให้โหลดเสร็จ
    await waitFor(() => {
      const distEl = screen.getByTestId('road-distance-value');
      expect(distEl).not.toBeNull();
      expect(distEl.textContent).toContain('2.0');
    });

    // ตรวจสอบค่าน้ำมัน
    const costEl = screen.getByTestId('fuel-cost-value');
    expect(costEl.textContent).toContain('5.00');

    // ตรวจสอบป้ายประเภทยานพาหนะ
    const vTypeEl = screen.getByTestId('vehicle-type-badge');
    expect(vTypeEl.textContent).toContain('มอเตอร์ไซค์พ่วงข้าง');

    // ตรวจสอบป้ายขอคนช่วยยก
    const helpBadge = screen.getByTestId('need-lifting-help-badge');
    expect(helpBadge).not.toBeNull();
    expect(helpBadge.textContent).toContain('ขอคนช่วยยก');

    // ตรวจสอบปุ่มรับงานแบบ Active
    const claimBtn = screen.getByTestId('claim-job-button');
    expect(claimBtn).not.toBeNull();
    expect(claimBtn.textContent).toContain('กดรับงานนี้');
  });

  it('renders fuel cost 0.00 THB for TRICYCLE vehicle type', async () => {
    const mockEvalTricycle = {
      order_id: 'order-s2-02',
      collector_id: 'saleng-01',
      vehicle_type: 'TRICYCLE',
      road_distance_km: 1.5,
      estimated_fuel_cost: 0.0,
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
      collector_is_verified: true,
      can_claim_job: true,
      items: [],
      location_summary: { subdistrict_name: 'แขวงจันทรเกษม', district_name: 'เขตจตุจักร' },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockEvalTricycle);

    render(<JobEvaluationView orderId="order-s2-02" salengId="saleng-01" />);

    await waitFor(() => {
      const costEl = screen.getByTestId('fuel-cost-value');
      expect(costEl.textContent).toContain('0.00');
    });

    const vTypeEl = screen.getByTestId('vehicle-type-badge');
    expect(vTypeEl.textContent).toContain('รถซาเล้งถีบ');
  });
});

