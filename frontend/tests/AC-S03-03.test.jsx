/**
 * Vitest Component Test สำหรับ AC-S03-03: Multi-Criteria Filter & Bulky Vehicle Match
 * รองรับ UC-03, REQ-FN-001, Card 03, AC-S03-03, P-03, Q-03
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CollectorFilterPanel from '../src/components/CollectorFilterPanel';

describe('AC-S03-03: CollectorFilterPanel Component Test', () => {
  it('renders filter chips and notifies parent on filter selection', () => {
    const handleRadius = vi.fn();
    const handleVehicle = vi.fn();
    const handleRating = vi.fn();

    render(
      <CollectorFilterPanel
        radiusKm={5.0}
        onChangeRadius={handleRadius}
        vehicleType={null}
        onChangeVehicleType={handleVehicle}
        minRating={null}
        onChangeMinRating={handleRating}
        hasBulkyItems={false}
      />
    );

    // เลือกรัศมี 3 กม.
    const chip3 = screen.getByTestId('radius-chip-3');
    expect(chip3).not.toBeNull();
    fireEvent.click(chip3);
    expect(handleRadius).toHaveBeenCalledWith(3.0);

    // เลือกรถกระบะ
    const pickupChip = screen.getByTestId('vehicle-chip-PICKUP_TRUCK');
    expect(pickupChip).not.toBeNull();
    fireEvent.click(pickupChip);
    expect(handleVehicle).toHaveBeenCalledWith('PICKUP_TRUCK');

    // เลือกรีวิว 4.8+
    const ratingChip = screen.getByTestId('rating-chip-45');
    expect(ratingChip).not.toBeNull();
    fireEvent.click(ratingChip);
    expect(handleRating).toHaveBeenCalledWith(4.8);
  });

  it('displays bulky warning banner when hasBulkyItems is true', () => {
    render(
      <CollectorFilterPanel
        radiusKm={5.0}
        hasBulkyItems={true}
        bulkyWarningMessage="คำขอของคุณมีตู้เย็น แนะนำรถกระบะ"
      />
    );

    const banner = screen.getByTestId('bulky-warning-banner');
    expect(banner).not.toBeNull();
    expect(banner.textContent).toContain('คำขอของคุณมีของชิ้นใหญ่');
    expect(banner.textContent).toContain('คำขอของคุณมีตู้เย็น แนะนำรถกระบะ');
  });
});

