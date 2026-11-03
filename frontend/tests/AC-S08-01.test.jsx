import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import NotificationCenterModal from "../src/components/NotificationCenterModal";
import * as api from "../src/services/notificationHelpApi";

describe("AC-S08-01: In-App Notifications & Draft Reminders Component Test", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders notifications list and shows unread badge (UC-08, Q-01)", async () => {
    const mockData = {
      seller_id: "SELLER-01",
      unread_count: 2,
      notifications: [
        {
          id: "N-DRAFT-01",
          seller_id: "SELLER-01",
          type: "DRAFT_REMINDER",
          title: "แจ้งเตือน: รายการของเก่าค้างในฉบับร่าง",
          message: "มีรายการคำขอนัดหมายค้างในระบบเกิน 3 วัน",
          order_id: "ORD-01",
          is_read: false,
          created_at: "2026-11-03T10:00:00Z",
        },
        {
          id: "N-STATUS-02",
          seller_id: "SELLER-01",
          type: "ORDER_STATUS_UPDATE",
          title: "ซาเล้งรับงานแล้ว",
          message: "ซาเล้งตอบรับคำขอนัดหมายแล้ว",
          is_read: false,
          created_at: "2026-11-03T11:00:00Z",
        },
      ],
    };

    vi.spyOn(api, "fetchNotifications").mockResolvedValue(mockData);

    render(
      <NotificationCenterModal
        isOpen={true}
        onClose={() => {}}
        sellerId="SELLER-01"
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId("notification-center-modal")).toBeDefined();
      expect(screen.getByTestId("unread-badge").textContent).toContain("2 ใหม่");
      expect(screen.getByText("แจ้งเตือน: รายการของเก่าค้างในฉบับร่าง")).toBeDefined();
      expect(screen.getByText("⏰ เตือนของค้าง")).toBeDefined();
      expect(screen.getByText("🚚 อัปเดตสถานะ")).toBeDefined();
    });
  });

  it("marks all notifications as read when clicking mark-all button", async () => {
    const mockData = {
      seller_id: "SELLER-01",
      unread_count: 1,
      notifications: [
        {
          id: "N-01",
          type: "DRAFT_REMINDER",
          title: "เตือนของค้าง",
          message: "ค้าง 3 วัน",
          is_read: false,
        },
      ],
    };

    vi.spyOn(api, "fetchNotifications").mockResolvedValue(mockData);
    const mockMarkAll = vi.spyOn(api, "markAllNotificationsAsRead").mockResolvedValue({
      cleared_count: 1,
    });

    render(
      <NotificationCenterModal
        isOpen={true}
        onClose={() => {}}
        sellerId="SELLER-01"
      />
    );

    await waitFor(() => {
      expect(screen.getByTestId("mark-all-read-btn")).toBeDefined();
    });

    fireEvent.click(screen.getByTestId("mark-all-read-btn"));

    await waitFor(() => {
      expect(mockMarkAll).toHaveBeenCalledWith("SELLER-01");
      expect(screen.queryByTestId("unread-badge")).toBeNull();
    });
  });
});

