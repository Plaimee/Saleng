/**
 * Component Tests สำหรับ AC-B05-05: Post-Transaction Privacy Guard in S7/S8
 * (T-08: MD-STM-04, REQ-SEC-002, AC-B05-05, D-B05-05)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ChatView from '../src/components/ChatView.jsx';
import { communicationApi } from '../src/services/communicationApi.js';

describe('AC-B05-05: Post-Transaction Privacy Guard Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('locks chat room to Read-only, displays PDPA banner, hides quick call, and disables input in S7', async () => {
    const mockRoomS7 = {
      order_id: 'order-s7-01',
      order_status: 'S7',
      is_read_only: true,
      read_only_reason: 'การทำธุรกรรมเสร็จสิ้นแล้ว ห้องแชตถูกปิดเพื่อความปลอดภัยของข้อมูลส่วนบุคคลตามกฎหมาย PDPA',
      seller_info: {
        seller_id: 'seller-01',
        display_name: 'คุณวิภาดา',
        phone: null,
        phone_masked: true,
      },
      messages: [
        {
          message_id: 'm1',
          sender_id: 'saleng-01',
          sender_role: 'COLLECTOR',
          message_text: 'ขอบคุณมากครับ',
          sent_at: '2026-11-04T11:00:00Z',
        },
      ],
    };

    vi.spyOn(communicationApi, 'getMessages').mockResolvedValue(mockRoomS7);
    vi.spyOn(communicationApi, 'getQuickReplies').mockResolvedValue({ quick_replies: [] });

    render(<ChatView orderId="order-s7-01" salengId="saleng-01" />);

    await waitFor(() => {
      // 1. ตรวจสอบแบนเนอร์แจ้งเตือน PDPA
      const banner = screen.getByTestId('read-only-banner');
      expect(banner).not.toBeNull();
      expect(banner.textContent).toContain('PDPA');

      // 2. ตรวจสอบว่าปุ่มโทรด่วนถูกซ่อน
      expect(screen.queryByTestId('quick-call-btn')).toBeNull();

      // 3. ตรวจสอบว่าแถบ Quick Replies ไม่ถูกแสดง
      expect(screen.queryByTestId('quick-replies-bar')).toBeNull();

      // 4. ตรวจสอบว่ากล่องพิมพ์ข้อความถูก disabled
      const input = screen.getByTestId('chat-input');
      expect(input.disabled).toBe(true);
      expect(input.getAttribute('placeholder')).toContain('ห้องแชตถูกปิด');

      const sendBtn = screen.getByTestId('send-message-btn');
      expect(sendBtn.disabled).toBe(true);
    });
  });
});
