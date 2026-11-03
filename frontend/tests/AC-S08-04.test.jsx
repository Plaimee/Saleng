import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import SupportTicketModal from "../src/components/SupportTicketModal";
import * as api from "../src/services/notificationHelpApi";

describe("AC-S08-04: Customer Support Ticket Submission Component Test", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("submits support ticket and displays masked phone and ticket number (REQ-SEC-002, Q-04)", async () => {
    const mockTicket = {
      id: "tck-001",
      ticket_no: "TCK-20261103-8899",
      seller_id: "SELLER-01",
      category: "WEIGHING",
      subject: "มีปัญหาเรื่องตาชั่ง",
      description: "ตัวเลขตาชั่งไม่ตรงกับที่ตกลงกัน",
      contact_phone_masked: "08X-XXX-4455",
      status: "OPEN",
    };

    const mockSubmit = vi.spyOn(api, "submitSupportTicket").mockResolvedValue(mockTicket);

    render(
      <SupportTicketModal
        isOpen={true}
        onClose={() => {}}
        sellerId="SELLER-01"
      />
    );

    // ตรวจสอบข้อมูลติดต่อสายด่วน
    expect(screen.getByText("02-123-4567")).toBeDefined();
    expect(screen.getByText("@saleng-help")).toBeDefined();

    // กรอกฟอร์ม
    fireEvent.change(screen.getByTestId("ticket-subject-input"), {
      target: { value: "มีปัญหาเรื่องตาชั่ง" },
    });
    fireEvent.change(screen.getByTestId("ticket-description-input"), {
      target: { value: "ตัวเลขตาชั่งไม่ตรงกับที่ตกลงกันไว้หน้างาน" },
    });
    fireEvent.change(screen.getByTestId("ticket-phone-input"), {
      target: { value: "0811224455" },
    });

    // ส่งฟอร์ม
    fireEvent.click(screen.getByTestId("submit-ticket-btn"));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith("SELLER-01", {
        category: "BOOKING",
        subject: "มีปัญหาเรื่องตาชั่ง",
        description: "ตัวเลขตาชั่งไม่ตรงกับที่ตกลงกันไว้หน้างาน",
        contactPhone: "0811224455",
      });
      expect(screen.getByTestId("ticket-no-badge").textContent).toContain("TCK-20261103-8899");
      expect(screen.getByTestId("ticket-masked-phone").textContent).toContain("08X-XXX-4455");
    });
  });
});

