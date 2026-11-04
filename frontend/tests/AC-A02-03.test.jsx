import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminBenchmarkGradingView from '../src/components/admin/AdminBenchmarkGradingView';
import * as adminBenchmarkApi from '../src/services/adminBenchmarkApi';

describe('AC-A02-03: Bulky Waste Lump-sum Price Management Component Tests', () => {
  const mockPrices = [
    {
      category_code: 'MAT-CARDBOARD',
      category_name: 'กระดาษลัง',
      unit: 'kg',
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
    },
    {
      category_code: 'BULKY-FRIDGE',
      category_name: 'ตู้เย็น',
      unit: 'piece',
      min_price_per_unit: 200.0,
      max_price_per_unit: 300.0,
      grading_condition: 'คอมเพรสเซอร์ครบ',
    },
    {
      category_code: 'BULKY-TV',
      category_name: 'โทรทัศน์/จอภาพ',
      unit: 'piece',
      min_price_per_unit: 50.0,
      max_price_per_unit: 150.0,
      grading_condition: 'จอไม่แตก',
    },
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminBenchmarkApi, 'getBenchmarkPrices').mockResolvedValue(mockPrices);
  });

  it('renders bulky item price table with piece units and flat rate badges', async () => {
    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByTestId('bulky-item-table-container')).toBeTruthy();
    });

    expect(screen.getByText('ตู้เย็น')).toBeTruthy();
    expect(screen.getByText('โทรทัศน์/จอภาพ')).toBeTruthy();
    expect(screen.getByText('200 – 300 บ.')).toBeTruthy();
    expect(screen.getByText('50 – 150 บ.')).toBeTruthy();
  });

  it('allows editing bulky item price and saving successfully', async () => {
    const updateSpy = vi.spyOn(adminBenchmarkApi, 'updateBenchmarkPrice').mockResolvedValue({
      success: true,
      category_code: 'BULKY-FRIDGE',
      min_price_per_unit: 250.0,
      max_price_per_unit: 350.0,
    });

    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByTestId('btn-edit-bulky-BULKY-FRIDGE')).toBeTruthy();
    });

    // ปุ่มแก้ไขมีขนาด >= 48px
    const editBtn = screen.getByTestId('btn-edit-bulky-BULKY-FRIDGE');
    expect(editBtn.className).toContain('min-h-[48px]');
    fireEvent.click(editBtn);

    const minInput = screen.getByTestId('input-bulky-min-price');
    const maxInput = screen.getByTestId('input-bulky-max-price');
    fireEvent.change(minInput, { target: { value: '250' } });
    fireEvent.change(maxInput, { target: { value: '350' } });

    const saveBtn = screen.getByTestId('btn-save-bulky-price');
    expect(saveBtn.className).toContain('min-h-[48px]');
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        'BULKY-FRIDGE',
        expect.objectContaining({
          min_price_per_unit: 250,
          max_price_per_unit: 350,
        })
      );
    });
  });
});
