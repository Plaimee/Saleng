import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import WeightVerificationCard from "../src/components/WeightVerificationCard.jsx";

/**
 * AC-S06-01: 100% Seller Weight Confirmation Gate
 * รองรับ REQ-FN-004, AC-S06-01, P-01, Q-01
 */
describe("AC-S06-01: Weight Verification Card Component", () => {
  const mockOrder = {
    order_id: "ORD-WEIGHT-001",
    status: "S5",
    scale_photo_url: "https://storage.saleng.app/scales/scale-ac01.jpg",
    total_settled_amount: 300.0,
    items: [
      {
        item_id: "itm-01",
        category_code: "MAT-CARDBOARD",
        category_name: "กระดาษลัง",
        unit: "kg",
        est_quantity: 50.0,
        actual_quantity: 60.0,
        locked_unit_price: 3.5,
        settled_item_price: 210.0,
      },
      {
        item_id: "itm-02",
        category_code: "MAT-GLASS-BOTTLE-BAG",
        category_name: "ขวดแก้ว (กระสอบ)",
        unit: "bag",
        est_quantity: 2.0,
        actual_quantity: 2.0,
        locked_unit_price: 45.0,
        settled_item_price: 90.0,
      },
    ],
  };

  it("แสดงผลชั่งจริงหน้างาน รูปตาชั่ง และยอดเงินสุทธิคำนวณจากราคาล็อก (AC-S06-01)", () => {
    render(
      <WeightVerificationCard
        order={mockOrder}
        onConfirmWeights={vi.fn()}
        onRequestReweigh={vi.fn()}
        onRaiseDispute={vi.fn()}
      />
    );

    // ตรวจสอบ data-req="REQ-FN-004"
    const card = screen.getByTestId("weight-verification-card");
    expect(card.getAttribute("data-req")).toBe("REQ-FN-004");

    // ตรวจสอบสถานะ S5
    expect(screen.getByText(/สถานะ S5: รอผู้ขายยืนยันน้ำหนัก/i)).toBeDefined();

    // ตรวจสอบการแสดงรูปตาชั่ง
    const img = screen.getByTestId("scale-photo");
    expect(img.getAttribute("src")).toBe("https://storage.saleng.app/scales/scale-ac01.jpg");

    // ตรวจสอบน้ำหนักชั่งจริง: 60 kg และ 2 bag
    expect(screen.getByTestId("actual-qty-0").textContent).toContain("60 kg");
    expect(screen.getByTestId("actual-qty-1").textContent).toContain("2 bag");

    // ตรวจสอบยอดสุทธิ: 300.00 บาท
    expect(screen.getByTestId("total-settled-amount").textContent).toBe("300.00");
  });

  it("กดยืนยันตัวเลขน้ำหนักจริงเรียก callback สำเร็จ (100% Confirmation Gate)", () => {
    const handleConfirm = vi.fn();
    render(
      <WeightVerificationCard
        order={mockOrder}
        onConfirmWeights={handleConfirm}
        onRequestReweigh={vi.fn()}
        onRaiseDispute={vi.fn()}
      />
    );

    const confirmBtn = screen.getByTestId("confirm-weights-btn");
    fireEvent.click(confirmBtn);

    expect(handleConfirm).toHaveBeenCalledTimes(1);
  });
});

