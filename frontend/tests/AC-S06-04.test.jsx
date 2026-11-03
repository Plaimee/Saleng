import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import DigitalReceiptCard from "../src/components/DigitalReceiptCard.jsx";

/**
 * AC-S06-04: Digital Receipt Generation & PII Masking
 * รองรับ REQ-FN-005, REQ-SEC-002, SC-03, AC-S06-04, P-05, Q-04
 */
describe("AC-S06-04: Digital Receipt Card Component", () => {
  const mockReceipt = {
    receipt_no: "REC-20261103-0001",
    issued_at: "2026-11-03T12:30:00Z",
    seller_phone_masked: "08X-XXX-1234",
    buyer_phone_masked: "08X-XXX-5678",
    total_amount: 520.0,
    payment_method: "PROMPTPAY",
    items: [
      {
        category_code: "MAT-CARDBOARD",
        category_name: "กระดาษลัง",
        unit: "kg",
        actual_quantity: 120.0,
        locked_unit_price: 3.5,
        settled_item_price: 420.0,
      },
      {
        category_code: "MAT-GLASS-BOTTLE-BAG",
        category_name: "ขวดแก้ว (กระสอบ)",
        unit: "bag",
        actual_quantity: 2.0,
        locked_unit_price: 50.0,
        settled_item_price: 100.0,
      },
    ],
  };

  it("แสดงข้อมูลใบเสร็จครบถ้วน ยอดสุทธิ และปกปิดเบอร์โทรศัพท์ (AC-S06-04, REQ-SEC-002)", () => {
    render(<DigitalReceiptCard receipt={mockReceipt} />);

    // ตรวจสอบ data-req="REQ-FN-005"
    const card = screen.getByTestId("digital-receipt-card");
    expect(card.getAttribute("data-req")).toBe("REQ-FN-005");

    // ตรวจสอบเลขที่ใบเสร็จ
    expect(screen.getByTestId("receipt-no").textContent).toContain("REC-20261103-0001");

    // ตรวจสอบ PII Masking (08X-XXX-XXXX)
    const phoneBox = screen.getByTestId("receipt-phones");
    expect(phoneBox.textContent).toContain("08X-XXX-1234");
    expect(phoneBox.textContent).toContain("08X-XXX-5678");

    // ตรวจสอบวิธีชำระเงิน
    expect(screen.getByTestId("receipt-method").textContent).toContain("PromptPay");

    // ตรวจสอบยอดสุทธิ
    expect(screen.getByTestId("receipt-total").textContent).toContain("520.00");
  });

  it("แสดงป้ายแจ้งเตือนโหมดออฟไลน์เมื่อเปิดดูใบเสร็จจากแคช (CC-05, REQ-OP-001)", () => {
    render(
      <DigitalReceiptCard
        receipt={mockReceipt}
        isOffline={true}
        offlineNotice="โหมดออฟไลน์: กำลังแสดงใบเสร็จที่บันทึกไว้ในเครื่อง"
      />
    );

    const badge = screen.getByTestId("offline-receipt-badge");
    expect(badge).toBeDefined();
    expect(badge.textContent).toContain("โหมดออฟไลน์");
  });
});

