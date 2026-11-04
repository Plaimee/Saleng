import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminDispatchDisputeView from '../src/components/admin/AdminDispatchDisputeView';
import * as adminDispatchDisputeApi from '../src/services/adminDispatchDisputeApi';

describe('AC-A03-01: Stalled Orders Queue & Manual Dispatch Component Tests', () => {
  const mockStalledOrders = [
    {
      order_id: 'order-s2-stalled-01',
      seller_id: 'seller-01',
      status: 'S2',
      created_at: '2026-11-04T15:00:00Z',
      waiting_minutes: 45.0,
      subdistrict: 'แขวงห้วยขวาง',
      district: 'เขตห้วยขวาง',
      total_est_min_price: 200.0,
      total_est_max_price: 350.0,
      total_est_weight_kg: 40.0,
      search_radius_km: 5.0,
      is_manual_dispatched: false,
    },
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminDispatchDisputeApi, 'getStalledOrders').mockResolvedValue(mockStalledOrders);
    vi.spyOn(adminDispatchDisputeApi, 'manualDispatchOrder').mockResolvedValue({
      success: true,
      order_id: 'order-s2-stalled-01',
      status: 'S3',
      assigned_saleng_id: 'saleng-01',
    });
    vi.spyOn(adminDispatchDisputeApi, 'expandSearchRadius').mockResolvedValue({
      success: true,
      order_id: 'order-s2-stalled-01',
      old_radius_km: 5.0,
      new_radius_km: 10.0,
    });
  });

  it('renders AdminDispatchDisputeView with data-req="UC-13" and touch targets >= 48px', async () => {
    render(<AdminDispatchDisputeView />);

    await waitFor(() => {
      expect(screen.getByTestId('admin-dispatch-dispute-view')).toBeTruthy();
    });

    const mainContainer = screen.getByTestId('admin-dispatch-dispute-view');
    expect(mainContainer.getAttribute('data-req')).toBe('UC-13');

    // ตรวจสอบปุ่มแท็บหลักมีขนาด >= 48px (min-h-[48px])
    const tabDispatch = screen.getByTestId('tab-dispatch');
    const tabDisputes = screen.getByTestId('tab-disputes');
    expect(tabDispatch.className).toContain('min-h-[48px]');
    expect(tabDisputes.className).toContain('min-h-[48px]');
  });

  it('displays stalled orders queue and triggers direct assign (S2 -> S3)', async () => {
    render(<AdminDispatchDisputeView />);

    await waitFor(() => {
      expect(screen.getByText('order-s2-stalled-01')).toBeTruthy();
    });

    expect(screen.getByText(/รอ 45 นาที/)).toBeTruthy();
    expect(screen.getByText('แขวงห้วยขวาง')).toBeTruthy();

    // กดปุ่มมอบหมายตรง
    const assignBtn = screen.getByRole('button', { name: /มอบหมายตรง/i });
    expect(assignBtn.className).toContain('min-h-[48px]');
    fireEvent.click(assignBtn);

    await waitFor(() => {
      expect(adminDispatchDisputeApi.manualDispatchOrder).toHaveBeenCalledWith(
        expect.objectContaining({
          order_id: 'order-s2-stalled-01',
          saleng_id: 'saleng-01',
        })
      );
    });
  });

  it('triggers expand radius to 10.0 km', async () => {
    render(<AdminDispatchDisputeView />);

    await waitFor(() => {
      expect(screen.getByText('order-s2-stalled-01')).toBeTruthy();
    });

    const expandBtn = screen.getByRole('button', { name: /ขยาย 10 กม\./i });
    expect(expandBtn.className).toContain('min-h-[48px]');
    fireEvent.click(expandBtn);

    await waitFor(() => {
      expect(adminDispatchDisputeApi.expandSearchRadius).toHaveBeenCalledWith(
        expect.objectContaining({
          order_id: 'order-s2-stalled-01',
          new_radius_km: 10.0,
        })
      );
    });
  });
});

