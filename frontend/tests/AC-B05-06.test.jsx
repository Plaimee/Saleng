/**
 * Component Tests สำหรับ AC-B05-06: Offline Chat History Cache
 * (T-08: REQ-OP-001, CC-05, AC-B05-06, D-B05-06)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ChatView from '../src/components/ChatView.jsx';
import { communicationApi } from '../src/services/communicationApi.js';

describe('AC-B05-06: Offline Chat History Cache Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('displays offline banner and cached messages when offline, while disabling inputs', async () => {
    const mockOfflineRoom = {
      order_id: 'order-offline-01',
      order_status: 'S3',
      is_read_only: false,
      from_cache: true,
      is_offline: true,
      seller_info: {
        seller_id: 'seller-01',
        display_name: 'คุณวิภาดา',
        phone: '081-234-5678',
        phone_masked: false,
      },
      messages: [
        {
          message_id: 'm-cached-1',
          sender_id: 'seller-01',
          sender_role: 'SELLER',
          message_text: 'จุดสังเกต: รั้วสีเขียว ติดต้นมะม่วงค่ะ',
          sent_at: '2026-11-04T09:30:00Z',
        },
      ],
    };

    vi.spyOn(communicationApi, 'getMessages').mockResolvedValue(mockOfflineRoom);
    vi.spyOn(communicationApi, 'getQuickReplies').mockResolvedValue({
      quick_replies: [
        { id: 'qr-01', text: 'กำลังเดินทางไปครับ', emoji: '🚚' },
      ],
    });

    render(<ChatView orderId="order-offline-01" salengId="saleng-01" />);

    await waitFor(() => {
      // 1. ตรวจสอบแบนเนอร์แจ้งเตือนโหมดออฟไลน์
      const banner = screen.getByTestId('offline-chat-banner');
      expect(banner).not.toBeNull();
      expect(banner.textContent).toContain('โหมดออฟไลน์');

      // 2. ตรวจสอบว่าแสดงข้อความจุดสังเกตจากแคช
      expect(screen.getByText('จุดสังเกต: รั้วสีเขียว ติดต้นมะม่วงค่ะ')).not.toBeNull();

      // 3. ตรวจสอบว่ากล่องพิมพ์ข้อความถูก disabled ในโหมดออฟไลน์
      const input = screen.getByTestId('chat-input');
      expect(input.disabled).toBe(true);
      expect(input.getAttribute('placeholder')).toContain('โหมดออฟไลน์');

      // 4. ปุ่มข้อความด่วนถูก disabled
      const qrBtn = screen.getByTestId('quick-reply-btn');
      expect(qrBtn.disabled).toBe(true);
    });
  });
});
