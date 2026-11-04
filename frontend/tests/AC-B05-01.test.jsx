/**
 * Component Tests สำหรับ AC-B05-01: In-App Direct Chat Messaging
 * (T-08: UC-08, REQ-UX-001, AC-B05-01, D-B05-01, D-B05-04)
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatView from '../src/components/ChatView.jsx';
import { communicationApi } from '../src/services/communicationApi.js';

describe('AC-B05-01: In-App Direct Chat Messaging Component Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders chat room, displays messages feed, and sends custom text message', async () => {
    const mockRoomData = {
      order_id: 'order-chat-01',
      order_status: 'S3',
      is_read_only: false,
      seller_info: {
        seller_id: 'seller-01',
        display_name: 'คุณวิภาดา',
        phone: '081-234-5678',
        phone_masked: false,
      },
      messages: [
        {
          message_id: 'm1',
          sender_id: 'seller-01',
          sender_role: 'SELLER',
          message_text: 'สวัสดีค่ะ',
          is_quick_reply: false,
          sent_at: '2026-11-04T10:00:00Z',
        },
      ],
    };

    vi.spyOn(communicationApi, 'getMessages').mockResolvedValue(mockRoomData);
    vi.spyOn(communicationApi, 'getQuickReplies').mockResolvedValue({
      quick_replies: [
        { id: 'qr-01', text: 'กำลังเดินทางไปครับ', emoji: '🚚' },
      ],
    });
    vi.spyOn(communicationApi, 'sendMessage').mockResolvedValue({
      status: 'success',
      message: {
        message_id: 'm2',
        sender_id: 'saleng-01',
        sender_role: 'COLLECTOR',
        message_text: 'สวัสดีครับ กำลังไปครับ',
        is_quick_reply: false,
        sent_at: '2026-11-04T10:01:00Z',
      },
    });

    render(<ChatView orderId="order-chat-01" salengId="saleng-01" />);

    // รอให้โหลดข้อมูลเสร็จ
    await waitFor(() => {
      expect(screen.getByTestId('chat-seller-name').textContent).toBe('คุณวิภาดา');
    });

    // ตรวจสอบข้อความเดิมจากผู้ขาย
    expect(screen.getByText('สวัสดีค่ะ')).not.toBeNull();

    // พิมพ์ข้อความใหม่ในช่อง input
    const input = screen.getByTestId('chat-input');
    const sendBtn = screen.getByTestId('send-message-btn');

    fireEvent.change(input, { target: { value: 'สวัสดีครับ กำลังไปครับ' } });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(communicationApi.sendMessage).toHaveBeenCalledWith('order-chat-01', {
        salengId: 'saleng-01',
        messageText: 'สวัสดีครับ กำลังไปครับ',
        isQuickReply: false,
      });
      expect(screen.getByText('สวัสดีครับ กำลังไปครับ')).not.toBeNull();
    });
  });
});

