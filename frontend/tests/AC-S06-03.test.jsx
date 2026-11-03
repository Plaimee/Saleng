import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import PaymentConfirmationCard from "../src/components/PaymentConfirmationCard.jsx";

/**
 * AC-S06-03: Payment Method Selection & Seller Cash/PromptPay Confirmation
 * รองรับ UC-07, AC-S06-03, P-04, Q-03
 */
describe("AC-S06-03: Payment Confirmation Card Component", () => {
  const mockOrder = {
    order_id: "ORD-PAY-001",
    status: "S6",
    total_settled_amount: 450.0,
  };

  it("แสดงยอดสุทธิ และสลับระหว่าง PromptPay และ เงินสด ได้ถูกต้อง (AC-S06-03)", () => {
    render(
      <PaymentConfirmationCard
        order={mockOrder}
        onConfirmPayment={vi.fn()}
      />
    );

    // ตรวจสอบ data-req="UC-07"
    const card = screen.getByTestId("payment-confirmation-card");
    expect(card.getAttribute("data-req")).toBe("UC-07");

    // ตรวจสอบยอดสุทธิ 450.00 บาท
    expect(screen.getByTestId("payment-amount-display").textContent).toContain("450.00");

    // ค่าเริ่มต้นเป็น PromptPay -> แสดง PromptPay box
    expect(screen.getByTestId("promptpay-box")).toBeDefined();

    // กดสลับเป็นเงินสด
    const cashBtn = screen.getByTestId("pay-method-cash");
    fireEvent.click(cashBtn);

    // แสดงคำแนะนำการรับเงินสด
    expect(screen.getByTestId("cash-box")).toBeDefined();
  });

  it("กดยืนยันรับเงินส่งวิธีชำระเงินที่เลือกไปยัง callback (AC-S06-03, Q-03)", () => {
    const handleConfirm = vi.fn();
    render(
      <PaymentConfirmationCard
        order={mockOrder}
        onConfirmPayment={handleConfirm}
      />
    );

    // สลับเป็นเงินสด
    fireEvent.click(screen.getByTestId("pay-method-cash"));

    // กดยืนยันรับเงิน
    const confirmBtn = screen.getByTestId("confirm-payment-btn");
    fireEvent.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledWith("CASH");
  });
});

