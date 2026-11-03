/**
 * Vitest Component Test สำหรับ AC-S03-02: Top Pinning for Previous Collectors
 * รองรับ UC-03, REQ-UX-001, AC-S03-02, Q-02
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FavoriteCollectorPinList from '../src/components/FavoriteCollectorPinList';
import SalengProfileCard from '../src/components/SalengProfileCard';

describe('AC-S03-02: Top Pinning for Previous Collectors Test', () => {
  const mockFavorites = [
    {
      saleng_id: 'saleng-01',
      display_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
      rating: 4.9,
      vehicle_type: 'TRICYCLE',
      distance_km: 1.2,
      is_favorite: true,
      verified: true,
    },
  ];

  it('renders pinned previous collectors strip at top with star badge', () => {
    const handleSelect = vi.fn();
    render(
      <FavoriteCollectorPinList
        favorites={mockFavorites}
        onSelect={handleSelect}
      />
    );

    const pinList = screen.getByTestId('favorite-pin-list');
    expect(pinList).not.toBeNull();
    expect(pinList.textContent).toContain('ซาเล้งที่เคยใช้บริการ');

    const favCard = screen.getByTestId('fav-pin-card-saleng-01');
    expect(favCard).not.toBeNull();
    expect(favCard.textContent).toContain('ลุงสมชาย');

    fireEvent.click(favCard);
    expect(handleSelect).toHaveBeenCalledWith(mockFavorites[0]);
  });

  it('displays favorite badge in SalengProfileCard when is_favorite is true', () => {
    render(
      <SalengProfileCard
        collector={mockFavorites[0]}
        onSelect={vi.fn()}
        onToggleFavorite={vi.fn()}
        onStartChat={vi.fn()}
      />
    );

    const favBadge = screen.getByTestId('favorite-badge');
    expect(favBadge).not.toBeNull();
    expect(favBadge.textContent).toContain('ซาเล้งที่เคยใช้บริการ');
  });
});

