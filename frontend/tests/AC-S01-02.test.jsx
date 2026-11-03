/**
 * Vitest Component Test สำหรับ AC-S01-02: PickupLocationList & PickupLocationModal
 * รองรับ UC-01, UC-02, MD-DOM-04, Q-02, Q-03, AC-S01-02
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PickupLocationList from '../src/components/PickupLocationList';
import PickupLocationModal from '../src/components/PickupLocationModal';

describe('AC-S01-02: Pickup Locations UI Components', () => {
  const mockLocations = [
    {
      location_id: 'LOC-1',
      label: 'บ้าน',
      sub_district: 'บางซื่อ',
      address_text: '123 ซอย 5',
      geo_point: { lat: 13.75, lng: 100.5 },
      is_default: true,
    },
    {
      location_id: 'LOC-2',
      label: 'ร้านค้า',
      sub_district: 'จตุจักร',
      address_text: '456 ถ.พหลโยธิน',
      geo_point: { lat: 13.8, lng: 100.55 },
      is_default: false,
    },
  ];

  it('renders location list with default badge and action buttons', () => {
    const handleAddNew = vi.fn();
    const handleSetDefault = vi.fn();
    const handleDelete = vi.fn();

    render(
      <PickupLocationList
        locations={mockLocations}
        onAddNew={handleAddNew}
        onSetDefault={handleSetDefault}
        onDelete={handleDelete}
      />
    );

    const defaultBadge = screen.getByTestId('default-badge');
    expect(defaultBadge).not.toBeNull();
    expect(defaultBadge.textContent).toContain('ที่อยู่เริ่มต้น');

    // Click set default for second location
    const setDefBtn = screen.getByTestId('set-default-btn-LOC-2');
    fireEvent.click(setDefBtn);
    expect(handleSetDefault).toHaveBeenCalledWith('LOC-2');

    // Click delete
    const delBtn = screen.getByTestId('delete-btn-LOC-1');
    fireEvent.click(delBtn);
    expect(handleDelete).toHaveBeenCalledWith('LOC-1');
  });

  it('PickupLocationModal captures GPS pinning and submits form', () => {
    const handleSave = vi.fn();
    const handleClose = vi.fn();

    render(
      <PickupLocationModal
        isOpen={true}
        onClose={handleClose}
        onSave={handleSave}
      />
    );

    fireEvent.change(screen.getByTestId('sub-district-input'), {
      target: { value: 'ลาดพร้าว' },
    });
    fireEvent.change(screen.getByTestId('address-text-input'), {
      target: { value: '99/9 หมู่บ้านสุขใจ' },
    });

    // Click GPS pin button
    const gpsBtn = screen.getByTestId('gps-pin-btn');
    fireEvent.click(gpsBtn);

    // Toggle default checkbox
    const defaultCheckbox = screen.getByTestId('is-default-checkbox');
    fireEvent.click(defaultCheckbox);

    // Save
    const saveBtn = screen.getByTestId('save-location-btn');
    fireEvent.click(saveBtn);

    expect(handleSave).toHaveBeenCalledWith(
      expect.objectContaining({
        sub_district: 'ลาดพร้าว',
        address_text: '99/9 หมู่บ้านสุขใจ',
        is_default: true,
      })
    );
  });
});

