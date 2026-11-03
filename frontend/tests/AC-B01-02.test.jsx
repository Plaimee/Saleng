/**
 * Vitest Component Test สำหรับ AC-B01-02: Vehicle Profile & Capacity Setup
 * รองรับ REQ-FN-001, MD-DOM-04, BR-03, REQ-UX-001, CC-01, AC-B01-02, Q-04, P-02
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import VehicleConfigCard from '../src/components/VehicleConfigCard';
import { collectorAccountApi } from '../src/services/collectorAccountApi';

describe('AC-B01-02: Vehicle Profile & Capacity Setup', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const baseProfile = {
    saleng_id: 'saleng-01',
    vehicle_type: 'TRICYCLE',
    max_capacity_kg: 150.0,
    license_plate: '',
  };

  it('renders 3 standard vehicle options and auto-fills default capacities (Q-04)', () => {
    render(<VehicleConfigCard profile={baseProfile} />);

    expect(screen.getByTestId('vehicle-option-TRICYCLE')).not.toBeNull();
    expect(screen.getByTestId('vehicle-option-SIDE_CAR_MOTORCYCLE')).not.toBeNull();
    expect(screen.getByTestId('vehicle-option-PICKUP_TRUCK')).not.toBeNull();

    const capacityInput = screen.getByTestId('capacity-input');
    expect(capacityInput.value).toBe('150');

    // คลิกเลือก SIDE_CAR_MOTORCYCLE -> ความจุเปลี่ยนเป็น 300
    fireEvent.click(screen.getByTestId('vehicle-option-SIDE_CAR_MOTORCYCLE'));
    expect(capacityInput.value).toBe('300');

    // คลิกเลือก PICKUP_TRUCK -> ความจุเปลี่ยนเป็น 1000
    fireEvent.click(screen.getByTestId('vehicle-option-PICKUP_TRUCK'));
    expect(capacityInput.value).toBe('1000');
  });

  it('allows custom capacity and submits update to API (REQ-FN-001, BR-03)', async () => {
    vi.spyOn(collectorAccountApi, 'updateVehicle').mockResolvedValue({
      ...baseProfile,
      vehicle_type: 'SIDE_CAR_MOTORCYCLE',
      max_capacity_kg: 350.5,
      license_plate: '1กข-9999',
    });

    const onUpdated = vi.fn();
    render(<VehicleConfigCard profile={baseProfile} onVehicleUpdated={onUpdated} />);

    // เลือก SIDE_CAR_MOTORCYCLE
    fireEvent.click(screen.getByTestId('vehicle-option-SIDE_CAR_MOTORCYCLE'));

    // แก้ไขค่าน้ำหนักเป็น 350.5 และทะเบียนรถ
    const capacityInput = screen.getByTestId('capacity-input');
    fireEvent.change(capacityInput, { target: { value: '350.5' } });

    const plateInput = screen.getByTestId('license-plate-input');
    fireEvent.change(plateInput, { target: { value: '1กข-9999' } });

    // กดปุ่มบันทึก
    const saveBtn = screen.getByTestId('save-vehicle-btn');
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(collectorAccountApi.updateVehicle).toHaveBeenCalledWith('saleng-01', {
        vehicle_type: 'SIDE_CAR_MOTORCYCLE',
        license_plate: '1กข-9999',
        max_capacity_kg: 350.5,
      });
      expect(screen.getByTestId('vehicle-success-alert')).not.toBeNull();
    });
  });

  it('validates that max_capacity_kg must be greater than zero', async () => {
    render(<VehicleConfigCard profile={baseProfile} />);

    const capacityInput = screen.getByTestId('capacity-input');
    fireEvent.change(capacityInput, { target: { value: '0' } });

    const saveBtn = screen.getByTestId('save-vehicle-btn');
    fireEvent.click(saveBtn);

    await waitFor(() => {
      const errorAlert = screen.getByTestId('vehicle-error-alert');
      expect(errorAlert).not.toBeNull();
      expect(errorAlert.textContent).toContain('มากกว่า 0 กิโลกรัม');
    });
  });
});

