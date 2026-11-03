import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  fetchNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  fetchSortingGuides,
  fetchFaqs,
  submitSupportTicket,
  getCachedGuides,
  getCachedFaqs,
} from "../src/services/notificationHelpApi.js";

describe("notificationHelpApi client & offline cache (T-06)", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("fetchNotifications: fetches notifications and parses unread count", async () => {
    const mockData = {
      seller_id: "SELLER-01",
      unread_count: 2,
      notifications: [
        { id: "N1", type: "DRAFT_REMINDER", title: "ของค้าง", is_read: false },
        { id: "N2", type: "ORDER_STATUS_UPDATE", title: "รับงานแล้ว", is_read: false },
      ],
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockData,
    });

    const result = await fetchNotifications("SELLER-01");
    expect(result.unread_count).toBe(2);
    expect(result.notifications.length).toBe(2);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/sellers/SELLER-01/notifications"
    );
  });

  it("markNotificationAsRead: sends PATCH request", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ notification_id: "N1", is_read: true }),
    });

    const result = await markNotificationAsRead("N1");
    expect(result.is_read).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/notifications/N1/read",
      expect.objectContaining({ method: "PATCH" })
    );
  });

  it("fetchSortingGuides: caches response and supports offline fallback (CC-05, REQ-OP-001)", async () => {
    const mockGuides = {
      guides: [{ category_code: "MAT-CARDBOARD", category_name: "กระดาษลัง" }],
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockGuides,
    });

    const onlineData = await fetchSortingGuides();
    expect(onlineData.is_offline_cached).toBe(false);
    expect(getCachedGuides()).not.toBeNull();

    // Network drops
    global.fetch = vi.fn().mockRejectedValue(new Error("Network failed"));

    const offlineData = await fetchSortingGuides();
    expect(offlineData.is_offline_cached).toBe(true);
    expect(offlineData.guides[0].category_code).toBe("MAT-CARDBOARD");
  });

  it("fetchFaqs: caches faqs and supports offline search (CC-05, REQ-OP-001)", async () => {
    const mockFaqs = {
      categories: [
        {
          category_id: "MIN",
          category_name: "ขั้นต่ำ",
          faqs: [
            { id: "F1", question: "เกณฑ์ 500 บาทคืออะไร?", answer: "ต้องไม่ต่ำกว่า 500 บาท" },
            { id: "F2", question: "PromptPay รองรับไหม?", answer: "รองรับ QR Code" },
          ],
        },
      ],
      total_faqs: 2,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockFaqs,
    });

    await fetchFaqs();
    expect(getCachedFaqs()).not.toBeNull();

    // Network drops, perform offline search
    global.fetch = vi.fn().mockRejectedValue(new Error("Offline"));

    const searchResult = await fetchFaqs("500 บาท");
    expect(searchResult.is_offline_cached).toBe(true);
    expect(searchResult.total_faqs).toBe(1);
    expect(searchResult.categories[0].faqs[0].id).toBe("F1");
  });

  it("submitSupportTicket: sends POST and returns ticket response", async () => {
    const mockTicket = {
      id: "tck-01",
      ticket_no: "TCK-20261103-0001",
      seller_id: "SELLER-01",
      category: "BOOKING",
      subject: "มีปัญหาการนัดหมาย",
      contact_phone_masked: "08X-XXX-1234",
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockTicket,
    });

    const result = await submitSupportTicket("SELLER-01", {
      category: "BOOKING",
      subject: "มีปัญหาการนัดหมาย",
      description: "ซาเล้งยังไม่มาตามเวลานัด",
      contactPhone: "0819991234",
    });

    expect(result.ticket_no).toBe("TCK-20261103-0001");
    expect(result.contact_phone_masked).toBe("08X-XXX-1234");
  });
});

