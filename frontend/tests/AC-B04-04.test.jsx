/**
 * Component Tests สำหรับ AC-B04-04: Active Queue & Route Ordering
 * (T-08: BR-03, REQ-CON-003, AC-B04-04, D-B04-02)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ActiveJobQueueView from '../src/components/ActiveJobQueueView.jsx';
import RouteOptimizationBar from '../src/components/RouteOptimizationBar.jsx';
import { jobRouteApi } from '../src/services/jobRouteApi.js';

describe('AC-B04-04: Active Queue & Route Ordering Component Tests', () => {
  const mockQueueData = {
    collector_id: 'saleng-01',
    total_active_jobs: 2,
    current_load_kg: 65.0,
    max_capacity_kg: 200.0,
    remaining_capacity_kg: 135.0,
    total_route_distance_km: 4.8,
    total_estimated_duration_min: 30,
    jobs: [
      {
        order_id: 'order-s2-01',
        status: 'S4',
        seller_name: 'คุณสมชาย',
        address_text: '123/45 ซอยรัชดา 18',
        seller_phone: '081-999-8888',
        est_weight_kg: 25.0,
        appointment_slot: '10:00 - 12:00 น.',
        sequence_order: 1,
        distance_from_prev_km: 1.2,
        navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
      },
      {
        order_id: 'order-s2-02',
        status: 'S3',
        seller_name: 'คุณสมหญิง',
        address_text: '456/78 ซอยลาดพร้าว 48',
        seller_phone: '089-111-2222',
        est_weight_kg: 40.0,
        appointment_slot: '13:00 - 15:00 น.',
        sequence_order: 2,
        distance_from_prev_km: 3.6,
        navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.798000,100.585000&travelmode=driving',
      },
    ],
  };

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders RouteOptimizationBar with waypoint chips in sequence and distance/duration summary (AC-B04-04)', () => {
    render(
      <RouteOptimizationBar
        jobs={mockQueueData.jobs}
        total_route_distance_km={mockQueueData.total_route_distance_km}
        total_estimated_duration_min={mockQueueData.total_estimated_duration_min}
      />
    );

    const bar = screen.getByTestId('route-optimization-bar');
    expect(bar).not.toBeNull();

    const distEl = screen.getByTestId('total-route-distance');
    expect(distEl.textContent).toContain('4.8 กม.');

    const durEl = screen.getByTestId('total-route-duration');
    expect(durEl.textContent).toContain('30 นาที');

    const chip1 = screen.getByTestId('waypoint-chip-1');
    expect(chip1.textContent).toContain('คุณสมชาย');

    const chip2 = screen.getByTestId('waypoint-chip-2');
    expect(chip2.textContent).toContain('คุณสมหญิง');
  });

  it('renders ActiveJobQueueView showing accumulated capacity and list of active jobs (BR-03)', async () => {
    vi.spyOn(jobRouteApi, 'getActiveQueue').mockResolvedValue(mockQueueData);

    render(<ActiveJobQueueView salengId="saleng-01" initialData={mockQueueData} />);

    // Capacity bar text
    const capText = screen.getByTestId('capacity-text-projected');
    expect(capText.textContent).toContain('65.0 / 200 กก.');

    // 2 Job cards
    const cards = screen.getAllByTestId('active-job-card');
    expect(cards.length).toBe(2);
  });
});

