/**
 * Component Tests สำหรับ AC-B03-02: Dual-Engine Routing Fallback & Timeout Handling
 * (T-08: CC-03, REQ-OP-002, AC-04-10, E3, D-B03-02)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import JobEvaluationView from '../src/components/JobEvaluationView';
import { jobEvaluationApi } from '../src/services/jobEvaluationApi';

describe('AC-B03-02: Dual-Engine Routing Fallback Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders fallback badge "⚡ ระยะทางประเมินสำรอง" when is_fallback_distance is true', async () => {
    const mockFallbackEval = {
      order_id: 'order-s2-fallback',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.89, // Haversine * 1.35
      estimated_fuel_cost: 4.73,
      is_fallback_distance: true,
      total_est_weight_kg: 25.0,
      total_min_price: 150.0,
      total_max_price: 220.0,
      current_load_kg: 20.0,
      max_capacity_kg: 200.0,
      remaining_capacity_kg: 180.0,
      projected_total_load_kg: 45.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: true,
      claim_block_reason: null,
      items: [],
      location_summary: {
        subdistrict_name: 'แขวงสามเสนนอก',
        district_name: 'เขตห้วยขวาง',
        fuzzed_lat: 13.795,
        fuzzed_lng: 100.581,
      },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockFallbackEval);

    render(<JobEvaluationView orderId="order-s2-fallback" salengId="saleng-01" />);

    await waitFor(() => {
      const badge = screen.getByTestId('routing-fallback-badge');
      expect(badge).not.toBeNull();
      expect(badge.textContent).toContain('ระยะทางประเมินสำรอง');
    });

    const distEl = screen.getByTestId('road-distance-value');
    expect(distEl.textContent).toContain('1.9');
  });

  it('does NOT render fallback badge when primary routing engine succeeds', async () => {
    const mockNormalEval = {
      order_id: 'order-s2-normal',
      collector_id: 'saleng-01',
      vehicle_type: 'MOTORCYCLE',
      road_distance_km: 1.4,
      estimated_fuel_cost: 3.5,
      is_fallback_distance: false,
      total_est_weight_kg: 15.0,
      current_load_kg: 0.0,
      max_capacity_kg: 200.0,
      projected_total_load_kg: 15.0,
      is_capacity_exceeded: false,
      collector_is_online: true,
      collector_is_verified: true,
      can_claim_job: true,
      items: [],
      location_summary: { subdistrict_name: 'แขวงสามเสนนอก', district_name: 'เขตห้วยขวาง' },
    };

    vi.spyOn(jobEvaluationApi, 'evaluateJob').mockResolvedValue(mockNormalEval);

    render(<JobEvaluationView orderId="order-s2-normal" salengId="saleng-01" />);

    await waitFor(() => {
      const distEl = screen.getByTestId('road-distance-value');
      expect(distEl).not.toBeNull();
    });

    const badge = screen.queryByTestId('routing-fallback-badge');
    expect(badge).toBeNull();
  });
});

