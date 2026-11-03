/**
 * Component Tests for AC-B02-01: Job Discovery in 5.0 km Radius within 3.0s
 * (Task T-08: UC-04, REQ-FN-002, REQ-QA-002, CC-03, P-01)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import JobSearchPanel from '../src/components/JobSearchPanel';
import { jobSearchApi } from '../src/services/jobSearchApi';

describe('AC-B02-01: Job Discovery in 5.0 km Radius Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders nearby jobs list within 5.0 km radius with subdistrict, distance, and price', async () => {
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
        categories: ['MAT-CARDBOARD', 'MAT-ALU-CAN'],
        need_lifting_help: false,
        is_fallback_distance: false,
        created_at: '2026-11-04T02:30:00Z',
      },
      {
        order_id: 'order-s2-02',
        status: 'S2',
        subdistrict_name: 'แขวงจันทรเกษม',
        district_name: 'เขตจตุจักร',
        approximate_lat: 13.8030,
        approximate_lng: 100.5740,
        road_distance_km: 1.4,
        estimated_price_min: 300,
        estimated_price_max: 450,
        estimated_weight_kg: 60,
        categories: ['MAT-PET-BOTTLE'],
        need_lifting_help: true,
        is_fallback_distance: false,
        created_at: '2026-11-04T02:40:00Z',
      },
    ];

    vi.spyOn(jobSearchApi, 'getNearbyJobs').mockResolvedValue({
      total_count: 2,
      radius_km: 5.0,
      jobs: mockJobs,
      active_filters: {},
    });

    render(<JobSearchPanel />);

    // รอให้โหลดรายการงาน
    await waitFor(() => {
      const card1 = screen.getByTestId('job-card-order-s2-01');
      expect(card1).not.toBeNull();
    });

    // ตรวจสอบการแสดงผลข้อมูลสำคัญบนการ์ด
    const loc1 = screen.getByTestId('job-location-order-s2-01');
    expect(loc1.textContent).toContain('แขวงสามเสนนอก เขตห้วยขวาง');

    const dist1 = screen.getByTestId('job-distance-order-s2-01');
    expect(dist1.textContent).toContain('0.8 กม.');

    const price1 = screen.getByTestId('job-price-order-s2-01');
    expect(price1.textContent).toContain('150 - 220 บาท');

    const card2 = screen.getByTestId('job-card-order-s2-02');
    expect(card2).not.toBeNull();
    expect(screen.getByText('💪 ขอคนช่วยยก')).not.toBeNull();
  });
});

