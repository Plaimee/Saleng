/**
 * Component Tests สำหรับ AC-B04-03: Address Unmasking & GPS Navigation Launch
 * (T-08: REQ-SEC-002, UC-09, AC-B04-03, D-B04-03)
 */

import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ActiveJobCard from '../src/components/ActiveJobCard.jsx';

describe('AC-B04-03: Address Unmasking & GPS Navigation Launch Component Tests', () => {
  const mockJob = {
    order_id: 'order-s2-01',
    status: 'S3',
    seller_name: 'สมชาย ใจดี',
    address_text: '123/45 ซอยรัชดาภิเษก 18 แขวงสามเสนนอก เขตห้วยขวาง กทม.',
    dest_lat: 13.7930,
    dest_lng: 100.5780,
    seller_phone: '081-999-8888',
    est_weight_kg: 25.0,
    appointment_slot: '10:00 - 12:00 น.',
    sequence_order: 1,
    distance_from_prev_km: 1.2,
    navigation_url: 'https://www.google.com/maps/dir/?api=1&destination=13.793000,100.578000&travelmode=driving',
    items: [
      { category_name_th: 'กระดาษลูกฟูก', est_weight_kg: 25.0 },
    ],
  };

  it('renders unmasked address and seller phone when job is in S3 (REQ-SEC-002, AC-B04-03)', () => {
    render(<ActiveJobCard job={mockJob} />);

    // Unmasked Address
    const addressEl = screen.getByTestId('seller-address-text');
    expect(addressEl).not.toBeNull();
    expect(addressEl.textContent).toContain('123/45 ซอยรัชดาภิเษก 18');

    // Seller Phone
    const phoneEl = screen.getByTestId('seller-phone-text');
    expect(phoneEl).not.toBeNull();
    expect(phoneEl.textContent).toContain('081-999-8888');

    // Phone Link tel:
    const phoneLink = screen.getByTestId('seller-phone-link');
    expect(phoneLink.getAttribute('href')).toBe('tel:081-999-8888');
  });

  it('renders GPS navigation button with correct Google Maps URL and triggers navigation (UC-09, D-B04-03)', () => {
    const handleNavigate = vi.fn();

    render(<ActiveJobCard job={mockJob} onNavigate={handleNavigate} />);

    const navBtn = screen.getByTestId('nav-gps-btn');
    expect(navBtn).not.toBeNull();
    expect(navBtn.getAttribute('href')).toBe(mockJob.navigation_url);

    fireEvent.click(navBtn);
    expect(handleNavigate).toHaveBeenCalledWith(mockJob);
  });
});

