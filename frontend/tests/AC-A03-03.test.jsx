import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AdminDispatchDisputeView from '../src/components/admin/AdminDispatchDisputeView';
import * as adminDispatchDisputeApi from '../src/services/adminDispatchDisputeApi';

describe('AC-A03-03 & AC-A03-04: Dispute Arbitration Modal Component Tests', () => {
  const mockDisputes = [
    {
      dispute_id: 'DISP-20261104-0001',
      order_id: 'order-dispute-01',
      seller_id: 'seller-02',
      buyer_id: 'saleng-01',
      dispute_reason: 'ผู้ขายไม่เห็นด้วยกับการหักสิ่งปนเปื้อน',
      status: 'PENDING_ADMIN',
      re_quoted_price: 210.0,
    },
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(adminDispatchDisputeApi, 'getStalledOrders').mockResolvedValue([]);
    vi.spyOn(adminDispatchDisputeApi, 'getDisputes').mockResolvedValue(mockDisputes);
    vi.spyOn(adminDispatchDisputeApi, 'resolveDispute').mockResolvedValue({
      success: true,
      dispute_id: 'DISP-20261104-0001',
      order_status: 'S7',
      dispute_status: 'RESOLVED_COMPLETED',
      arbitrated_amount: 220.0,
      receipt: { receipt_id: 'REC-1', total_amount: 220.0 },
    });
  });

  it('opens arbitration modal and submits RESOLVE_COMPLETE with arbitrated amount', async () => {
    render(<AdminDispatchDisputeView />);

    // ไปแท็บข้อพิพาท
    const tabDisputes = screen.getByTestId('tab-disputes');
    fireEvent.click(tabDisputes);

    await waitFor(() => {
      expect(screen.getByText('DISP-20261104-0001')).toBeTruthy();
    });

    // กดปุ่มตัดสินชี้ขาด
    const arbitrateBtn = screen.getByRole('button', { name: /ตัดสินชี้ขาด/i });
    expect(arbitrateBtn.className).toContain('min-h-[48px]');
    fireEvent.click(arbitrateBtn);

    // Modal ต้องปรากฏขึ้น
    await waitFor(() => {
      expect(screen.getByText(/ตัดสินชี้ขาดข้อพิพาทหน้างาน/)).toBeTruthy();
    });

    // ตรวจสอบช่องกรอกยอดเงินชี้ขาด
    const amountInput = screen.getByPlaceholderText(/เช่น 210\.00/i);
    fireEvent.change(amountInput, { target: { value: '220.00' } });

    // ปุ่มยืนยันคำตัดสิน
    const submitBtn = screen.getByRole('button', { name: /ยืนยันคำตัดสิน/i });
    expect(submitBtn.className).toContain('min-h-[48px]');
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(adminDispatchDisputeApi.resolveDispute).toHaveBeenCalledWith(
        'DISP-20261104-0001',
        expect.objectContaining({
          action: 'RESOLVE_COMPLETE',
          arbitrated_amount: 220.0,
        })
      );
    });
  });

  it('selects cancel choice and submits RESOLVE_CANCEL with reason (AC-A03-04)', async () => {
    vi.spyOn(adminDispatchDisputeApi, 'resolveDispute').mockResolvedValueOnce({
      success: true,
      dispute_id: 'DISP-20261104-0001',
      order_status: 'S9',
      dispute_status: 'RESOLVED_CANCELLED',
    });

    render(<AdminDispatchDisputeView />);

    const tabDisputes = screen.getByTestId('tab-disputes');
    fireEvent.click(tabDisputes);

    await waitFor(() => {
      expect(screen.getByText('DISP-20261104-0001')).toBeTruthy();
    });

    fireEvent.click(screen.getByRole('button', { name: /ตัดสินชี้ขาด/i }));

    await waitFor(() => {
      expect(screen.getByText(/ตัดสินชี้ขาดข้อพิพาทหน้างาน/)).toBeTruthy();
    });

    // กดเลือกสั่งยกเลิก (S9)
    const cancelOptionBtn = screen.getByRole('button', { name: /สั่งยกเลิก \(S9\)/i });
    fireEvent.click(cancelOptionBtn);

    // กรอกเหตุผล
    const reasonTextarea = screen.getByPlaceholderText(/ระบุเหตุผลการยกเลิก/i);
    fireEvent.change(reasonTextarea, { target: { value: 'สินค้าไม่ตรงตามที่ตกลงและยกเลิกรายการ' } });

    const submitBtn = screen.getByRole('button', { name: /ยืนยันคำตัดสิน/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(adminDispatchDisputeApi.resolveDispute).toHaveBeenCalledWith(
        'DISP-20261104-0001',
        expect.objectContaining({
          action: 'RESOLVE_CANCEL',
          arbitration_note: 'สินค้าไม่ตรงตามที่ตกลงและยกเลิกรายการ',
        })
      );
    });
  });
});

