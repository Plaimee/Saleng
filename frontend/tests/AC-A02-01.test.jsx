import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminBenchmarkGradingView from '../src/components/admin/AdminBenchmarkGradingView';
import * as adminBenchmarkApi from '../src/services/adminBenchmarkApi';

describe('AC-A02-01: Daily Benchmark Price Publishing Component Tests', () => {
  const mockPrices = [
    {
      category_code: 'MAT-CARDBOARD',
      category_name: 'กระดาษลัง',
      unit: 'kg',
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
      grading_condition: 'แห้ง สะอาด',
      updated_at: '2026-11-04T06:00:00Z',
    },
    {
      category_code: 'BULKY-FRIDGE',
      category_name: 'ตู้เย็น',
      unit: 'piece',
      min_price_per_unit: 200.0,
      max_price_per_unit: 300.0,
      grading_condition: 'คอมเพรสเซอร์ครบ',
      updated_at: '2026-11-04T06:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminBenchmarkApi, 'getBenchmarkPrices').mockResolvedValue(mockPrices);
  });

  it('renders AdminBenchmarkGradingView with data-req="UC-03" and touch targets >= 48px', async () => {
    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByTestId('admin-benchmark-grading-view')).toBeTruthy();
    });

    const mainContainer = screen.getByTestId('admin-benchmark-grading-view');
    expect(mainContainer.getAttribute('data-req')).toBe('UC-03');

    // ตรวจสอบปุ่มแท็บหลักมีขนาด >= 48px (min-h-[48px])
    const tabPrices = screen.getByTestId('tab-prices');
    const tabGrading = screen.getByTestId('tab-grading');
    expect(tabPrices.className).toContain('min-h-[48px]');
    expect(tabGrading.className).toContain('min-h-[48px]');
  });

  it('displays benchmark price table with min-max range', async () => {
    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByText('กระดาษลัง')).toBeTruthy();
    });

    expect(screen.getByText('3.00 – 4.00')).toBeTruthy();
  });

  it('allows clicking edit price, shows inline inputs, and updates price successfully', async () => {
    const updateSpy = vi.spyOn(adminBenchmarkApi, 'updateBenchmarkPrice').mockResolvedValue({
      success: true,
      category_code: 'MAT-CARDBOARD',
      min_price_per_unit: 3.5,
      max_price_per_unit: 4.5,
    });

    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByTestId('btn-edit-MAT-CARDBOARD')).toBeTruthy();
    });

    // กดปุ่มแก้ไขราคา
    fireEvent.click(screen.getByTestId('btn-edit-MAT-CARDBOARD'));

    const minInput = screen.getByTestId('input-min-price');
    const maxInput = screen.getByTestId('input-max-price');
    expect(minInput).toBeTruthy();
    expect(maxInput).toBeTruthy();

    fireEvent.change(minInput, { target: { value: '3.50' } });
    fireEvent.change(maxInput, { target: { value: '4.50' } });

    // กดบันทึก
    fireEvent.click(screen.getByTestId('btn-save-price'));

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        'MAT-CARDBOARD',
        expect.objectContaining({
          min_price_per_unit: 3.5,
          max_price_per_unit: 4.5,
        })
      );
    });
  });

  it('triggers confirmation warning modal when price shift exceeds 50%', async () => {
    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByTestId('btn-edit-MAT-CARDBOARD')).toBeTruthy();
    });

    fireEvent.click(screen.getByTestId('btn-edit-MAT-CARDBOARD'));

    // ปรับราคาเป็น 10 - 15 บาท (เดิม mid 3.5 -> ใหม่ mid 12.5 = shift > 200%)
    fireEvent.change(screen.getByTestId('input-min-price'), { target: { value: '10.00' } });
    fireEvent.change(screen.getByTestId('input-max-price'), { target: { value: '15.00' } });

    fireEvent.click(screen.getByTestId('btn-save-price'));

    // Modal เตือนยืนยันต้องแสดงผล
    await waitFor(() => {
      expect(screen.getByTestId('shift-warning-modal')).toBeTruthy();
    });
    expect(screen.getByText(/ยืนยันการเปลี่ยนแปลงราคาเกิน 50%/)).toBeTruthy();

    // ปุ่มใน Modal มีขนาด >= 48px
    const btnConfirm = screen.getByTestId('btn-modal-confirm');
    expect(btnConfirm.className).toContain('min-h-[48px]');
  });
});
