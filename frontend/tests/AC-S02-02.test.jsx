/**
 * Vitest Component Test สำหรับ AC-S02-02 และ AC-S02-03: BulkyItemSelector
 * รองรับ UC-02, REQ-FN-003, Card 03, AC-S02-02, AC-S02-03
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import BulkyItemSelector from '../src/components/BulkyItemSelector';

describe('AC-S02-02 & AC-S02-03: BulkyItemSelector Component', () => {
  it('renders bulky options with prices and handles item selection (AC-S02-02)', () => {
    const handleSelect = vi.fn();
    render(
      <BulkyItemSelector
        selectedSubCategory="ตู้เย็น"
        onSelectSubCategory={handleSelect}
        errorMessage=""
      />
    );

    // ตรวจสอบตัวเลือกตู้เย็นและราคา 200–300 บ./ชิ้น
    const fridgeOption = screen.getByTestId('bulky-option-ตู้เย็น');
    expect(fridgeOption).not.toBeNull();
    expect(fridgeOption.textContent).toContain('ตู้เย็น');
    expect(fridgeOption.textContent).toContain('200–300 บ./ชิ้น');

    // คลิกเลือกเครื่องซักผ้า
    const washerOption = screen.getByTestId('bulky-option-เครื่องซักผ้า');
    expect(washerOption).not.toBeNull();
    expect(washerOption.textContent).toContain('150–250 บ./ชิ้น');
    fireEvent.click(washerOption);

    expect(handleSelect).toHaveBeenCalledWith('เครื่องซักผ้า');
  });

  it('renders bulky-guard-error when errorMessage is provided (AC-S02-03)', () => {
    const errorText = 'กรุณาระบุประเภทของชิ้นใหญ่ เพื่อให้ผู้รับซื้อจัดสรรพื้นที่รถบรรทุกได้';
    render(
      <BulkyItemSelector
        selectedSubCategory=""
        onSelectSubCategory={vi.fn()}
        errorMessage={errorText}
      />
    );

    const errorBanner = screen.getByTestId('bulky-guard-error');
    expect(errorBanner).not.toBeNull();
    expect(errorBanner.textContent).toContain(errorText);
  });
});

