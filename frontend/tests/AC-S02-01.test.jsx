/**
 * Vitest Component Test สำหรับ AC-S02-01: VisualScrapGuide
 * รองรับ UC-02, REQ-UX-002, AC-S02-01
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import VisualScrapGuide from '../src/components/VisualScrapGuide';

describe('AC-S02-01: VisualScrapGuide Component', () => {
  const mockCategories = [
    {
      category_code: 'MAT-CARDBOARD',
      category_group: 'GENERAL_WEIGHT',
      name: 'กระดาษลัง',
      icon: '📦',
      unit: 'kg',
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
    },
    {
      category_code: 'BOXED-GLASS',
      category_group: 'BOXED_CRATE_ITEMS',
      name: 'ขวดแก้วบรรจุลัง',
      icon: '🍾',
      unit: 'crate',
      min_price_per_unit: 15.0,
      max_price_per_unit: 25.0,
    },
  ];

  it('renders categories with icons, prices, and handles selection', () => {
    const handleSelect = vi.fn();
    render(
      <VisualScrapGuide
        categories={mockCategories}
        selectedCategory={mockCategories[0]}
        onSelectCategory={handleSelect}
      />
    );

    const card = screen.getByTestId('category-card-MAT-CARDBOARD');
    expect(card).not.toBeNull();
    expect(card.textContent).toContain('กระดาษลัง');
    expect(card.textContent).toContain('3–4 บ./กก.');

    fireEvent.click(card);
    expect(handleSelect).toHaveBeenCalledWith(mockCategories[0]);
  });

  it('switches tabs and displays items of that group', () => {
    const handleSelect = vi.fn();
    render(
      <VisualScrapGuide
        categories={mockCategories}
        selectedCategory={null}
        onSelectCategory={handleSelect}
      />
    );

    // Switch to BOXED_CRATE_ITEMS tab
    const tabBtn = screen.getByTestId('tab-BOXED_CRATE_ITEMS');
    fireEvent.click(tabBtn);

    const boxedCard = screen.getByTestId('category-card-BOXED-GLASS');
    expect(boxedCard).not.toBeNull();
    expect(boxedCard.textContent).toContain('ขวดแก้วบรรจุลัง');
    expect(boxedCard.textContent).toContain('15–25 บ./ลัง');
  });
});

