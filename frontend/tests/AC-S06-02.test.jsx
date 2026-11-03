import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import WeightVerificationCard from "../src/components/WeightVerificationCard.jsx";

/**
 * AC-S06-02: Dispute & Re-Weigh Option Component Tests
 * รองรับ REQ-FN-006, AC-S06-02, P-02, Q-02
 */
describe("AC-S06-02: Dispute & Re-Weigh Options", () => {
  const mockOrder = {
    order_id: "ORD-DISPUTE-001",
    status: "S5",
    total_settled_amount: 150.0,
    items: [
      {
        item_id: "itm-01",
        category_code: "MAT-CARDBOARD",
        category_name: "กระดาษลัง",
        unit: "kg",
        actual_quantity: 30.0,
        locked_unit_price: 5.0,
      },
    ],
  };

  it("เปิด Modal ขอให้ชั่งซ้ำและส่งเหตุผลสำเร็จ (AC-S06-02)", () => {
    const handleReweigh = vi.fn();
    render(
      <WeightVerificationCard
        order={mockOrder}
        onConfirmWeights={vi.fn()}
        onRequestReweigh={handleReweigh}
        onRaiseDispute={vi.fn()}
      />
    );

    // กดปุ่มขอให้ชั่งซ้ำ
    const reweighBtn = screen.getByTestId("request-reweigh-btn");
    fireEvent.click(reweighBtn);

    // กรอกเหตุผล
    const input = screen.getByTestId("reweigh-reason-input");
    fireEvent.change(input, { target: { value: "ตาชั่งค้าง ขอยกของลงวางใหม่" } });

    // กดยืนยันส่ง
    const submitBtn = screen.getByTestId("submit-reweigh-btn");
    fireEvent.click(submitBtn);

    expect(handleReweigh).toHaveBeenCalledWith("ตาชั่งค้าง ขอยกของลงวางใหม่");
  });

  it("เปิด Modal แจ้งข้อพิพาทและส่งเหตุผลสำเร็จ (AC-S06-02, REQ-FN-006)", () => {
    const handleDispute = vi.fn();
    render(
      <WeightVerificationCard
        order={mockOrder}
        onConfirmWeights={vi.fn()}
        onRequestReweigh={vi.fn()}
        onRaiseDispute={handleDispute}
      />
    );

    // กดปุ่มปฏิเสธ / แจ้งข้อพิพาท
    const disputeBtn = screen.getByTestId("raise-dispute-btn");
    fireEvent.click(disputeBtn);

    // กรอกเหตุผลข้อพิพาท (> 5 ตัวอักษร)
    const input = screen.getByTestId("dispute-reason-input");
    fireEvent.change(input, {
      target: { value: "น้ำหนักที่ชั่งได้น้อยกว่าปกติมาก ไม่ตรงกับที่ตกลงกัน" },
    });

    // กดยืนยันส่งข้อพิพาท
    const submitBtn = screen.getByTestId("submit-dispute-btn");
    fireEvent.click(submitBtn);

    expect(handleDispute).toHaveBeenCalledWith(
      "น้ำหนักที่ชั่งได้น้อยกว่าปกติมาก ไม่ตรงกับที่ตกลงกัน"
    );
  });
});

