import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminBenchmarkGradingView from '../src/components/admin/AdminBenchmarkGradingView';
import * as adminBenchmarkApi from '../src/services/adminBenchmarkApi';

describe('AC-A02-02: Quality Grading & Contamination Rules Component Tests', () => {
  const mockPrices = [
    {
      category_code: 'MAT-CARDBOARD',
      category_name: 'กระดาษลัง',
      unit: 'kg',
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
    },
  ];

  const mockRules = [
    {
      rule_id: 'r-1',
      category_code: 'MAT-CARDBOARD',
      grade_level: 'GRADE_A',
      grade_name: 'เกรด A (สะอาด/แห้ง/สมบูรณ์)',
      description: 'สะอาด แห้งสนิท',
      contamination_deduction_percent: 0.0,
      price_target: 'MAX',
    },
    {
      rule_id: 'r-2',
      category_code: 'MAT-CARDBOARD',
      grade_level: 'GRADE_B',
      grade_name: 'เกรด B (ปนเปื้อนเล็กน้อย)',
      description: 'มีความชื้นเล็กน้อย',
      contamination_deduction_percent: 5.0,
      price_target: 'MID',
    },
    {
      rule_id: 'r-3',
      category_code: 'MAT-CARDBOARD',
      grade_level: 'GRADE_C',
      grade_name: 'เกรด C (ปนเปื้อนมาก)',
      description: 'เปียกน้ำ คละเกรด',
      contamination_deduction_percent: 10.0,
      price_target: 'MIN',
    },
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminBenchmarkApi, 'getBenchmarkPrices').mockResolvedValue(mockPrices);
    vi.spyOn(adminBenchmarkApi, 'getGradingRules').mockResolvedValue(mockRules);
  });

  it('switches to grading tab and renders 3 tiers with 0%, 5%, 10% deductions', async () => {
    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      expect(screen.getByTestId('tab-grading')).toBeTruthy();
    });

    // คลิกแท็บเกณฑ์คุณภาพ
    fireEvent.click(screen.getByTestId('tab-grading'));

    await waitFor(() => {
      expect(screen.getByTestId('quality-grading-card')).toBeTruthy();
    });

    expect(screen.getByTestId('grading-tier-GRADE_A')).toBeTruthy();
    expect(screen.getByTestId('grading-tier-GRADE_B')).toBeTruthy();
    expect(screen.getByTestId('grading-tier-GRADE_C')).toBeTruthy();

    // ตรวจสอบค่าเริ่มต้น 0%, 5%, 10%
    expect(Number(screen.getByTestId('input-deduction-GRADE_A').value)).toBe(0);
    expect(Number(screen.getByTestId('input-deduction-GRADE_B').value)).toBe(5);
    expect(Number(screen.getByTestId('input-deduction-GRADE_C').value)).toBe(10);
  });

  it('allows updating grading description and saves successfully', async () => {
    const updateSpy = vi.spyOn(adminBenchmarkApi, 'updateGradingRules').mockResolvedValue({
      success: true,
      category_code: 'MAT-CARDBOARD',
      rules: mockRules,
    });

    render(<AdminBenchmarkGradingView />);

    await waitFor(() => {
      fireEvent.click(screen.getByTestId('tab-grading'));
    });

    await waitFor(() => {
      expect(screen.getByTestId('textarea-desc-GRADE_B')).toBeTruthy();
    });

    const descB = screen.getByTestId('textarea-desc-GRADE_B');
    fireEvent.change(descB, { target: { value: 'มีความชื้นไม่เกิน 5% หรือมีสิ่งเจือปนเล็กน้อย' } });

    // กดปุ่มบันทึก
    const saveBtn = screen.getByTestId('btn-save-grading-rules');
    expect(saveBtn.className).toContain('min-h-[48px]');
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        'MAT-CARDBOARD',
        expect.objectContaining({
          rules: expect.arrayContaining([
            expect.objectContaining({
              grade_level: 'GRADE_B',
              description: 'มีความชื้นไม่เกิน 5% หรือมีสิ่งเจือปนเล็กน้อย',
            }),
          ]),
        })
      );
    });
  });
});
