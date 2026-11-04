import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminDispatchDisputeView from '../src/components/admin/AdminDispatchDisputeView';
import * as adminDispatchDisputeApi from '../src/services/adminDispatchDisputeApi';

describe('AC-A03-02: Dispute Inspection Dossier Display Component Tests', () => {
  const mockDisputes = [
    {
      dispute_id: 'DISP-20261104-0001',
      order_id: 'order-dispute-01',
      seller_id: 'seller-02',
      buyer_id: 'saleng-01',
      seller_name: 'คุณสมศรี ผู้ขาย',
      buyer_name: 'ลุงสมชาย ซาเล้งสุทธิสาร',
      dispute_reason: 'น้ำหนักขวดพลาสติกชั่งได้น้อยกว่าที่ประเมินมาก ซาเล้งแจ้งว่าหักสิ่งปนเปื้อนเกินจริง',
      status: 'PENDING_ADMIN',
      re_quoted_price: 210.0,
      created_at: '2026-11-04T15:30:00Z',
    },
  ];

  const mockDossier = {
    dispute_id: 'DISP-20261104-0001',
    order_id: 'order-dispute-01',
    seller_id: 'seller-02',
    buyer_id: 'saleng-01',
    status: 'PENDING_ADMIN',
    created_at: '2026-11-04T15:30:00Z',
    dispute_reason: 'น้ำหนักขวดพลาสติกชั่งได้น้อยกว่าที่ประเมินมาก ซาเล้งแจ้งว่าหักสิ่งปนเปื้อนเกินจริง',
    original_order: {
      order_id: 'order-dispute-01',
      total_est_min_price: 300.0,
      total_est_max_price: 450.0,
      total_est_weight_kg: 60.0,
      price_snapshot: {
        'MAT-PET-BOTTLE': { min_price: 5.0, max_price: 7.5 },
      },
    },
    saleng_verification: {
      scale_photo_url: 'https://storage.saleng.app/disputes/scale_photo_01.jpg',
      actual_weights: { 'MAT-PET-BOTTLE': 42.0 },
      re_quoted_price: 210.0,
    },
    seller_dispute: {
      dispute_reason: 'น้ำหนักขวดพลาสติกชั่งได้น้อยกว่าที่ประเมินมาก ซาเล้งแจ้งว่าหักสิ่งปนเปื้อนเกินจริง',
      seller_photo_urls: [],
    },
    parties_contact: {
      seller: { name: 'คุณสมศรี ผู้ขาย', phone_masked: '081-XXX-4567' },
      buyer: { name: 'ลุงสมชาย ซาเล้งสุทธิสาร', phone_masked: '089-XXX-1234' },
    },
  };

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminDispatchDisputeApi, 'getStalledOrders').mockResolvedValue([]);
    vi.spyOn(adminDispatchDisputeApi, 'getDisputes').mockResolvedValue(mockDisputes);
    vi.spyOn(adminDispatchDisputeApi, 'getDisputeDossier').mockResolvedValue(mockDossier);
  });

  it('switches to disputes tab and renders dispute card with 4-dimension dossier', async () => {
    render(<AdminDispatchDisputeView />);

    // สลับไปยังแท็บศูนย์ตัดสินข้อพิพาท
    const tabDisputes = screen.getByTestId('tab-disputes');
    fireEvent.click(tabDisputes);

    await waitFor(() => {
      expect(screen.getByText('DISP-20261104-0001')).toBeTruthy();
    });

    expect(screen.getByText(/หักสิ่งปนเปื้อนเกินจริง/)).toBeTruthy();

    // กดปุ่มดูสำนวนหลักฐาน
    const expandBtn = screen.getByRole('button', { name: /ดูสำนวนหลักฐาน/i });
    expect(expandBtn.className).toContain('min-h-[48px]');
    fireEvent.click(expandBtn);

    await waitFor(() => {
      expect(adminDispatchDisputeApi.getDisputeDossier).toHaveBeenCalledWith('DISP-20261104-0001');
      expect(screen.getByText(/มิติ 1: คำขอเดิม & Price Snapshot/)).toBeTruthy();
      expect(screen.getByText(/มิติ 2: ข้อมูลหน้างานจากซาเล้ง/)).toBeTruthy();
      expect(screen.getByText(/มิติ 3: ข้อโต้แย้งจากผู้ขาย/)).toBeTruthy();
      expect(screen.getByText(/มิติ 4: ข้อมูลติดต่อคู่กรณี/)).toBeTruthy();
    });

    // ตรวจสอบภาพตาชั่งและเบอร์ติดต่อ Masking
    const scaleImg = screen.getByAltText('ภาพหน้าตาชั่งดิจิทัล');
    expect(scaleImg).toBeTruthy();
    expect(screen.getByText('081-XXX-4567')).toBeTruthy();
  });
});

