import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ItemPriceCalculator from "../src/components/ItemPriceCalculator.jsx";
import MultiItemBasketSummary from "../src/components/MultiItemBasketSummary.jsx";

/**
 * AC-S04-02: Instant Min-Max Calculation & Multi-Item Basket
 * รองรับ Card 01, BR-01, AC-S04-02, D-06
 */
describe("AC-S04-02: Instant Min-Max Calculation & Multi-Item Basket", () => {
  const mockPrices = [
    {
      category_code: "MAT-CARDBOARD",
      category_name: "กระดาษลัง",
      unit: "kg",
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
    },
    {
      category_code: "MAT-WHITE-PAPER",
      category_name: "กระดาษขาวดำ",
      unit: "kg",
      min_price_per_unit: 6.0,
      max_price_per_unit: 7.0,
    },
  ];

  it("คำนวณและแสดงช่วงราคาประเมินเบื้องต้นทันทีเมื่อกรอกปริมาณ (Card 01, AC-S04-02)", () => {
    const onAddItem = vi.fn();
    render(<ItemPriceCalculator benchmarkPrices={mockPrices} onAddItem={onAddItem} />);

    const qtyInput = screen.getByTestId("quantity-input");
    fireEvent.change(qtyInput, { target: { value: "10" } });

    // ตรวจสอบช่วงราคาเรียลไทม์ (10 กก. x 3–4 บ. -> 30–40 บาท)
    const preview = screen.getByTestId("live-estimate-preview");
    expect(preview.textContent).toContain("30–40 บาท");

    // กดเพิ่มลงตะกร้า
    const addBtn = screen.getByTestId("add-item-btn");
    fireEvent.click(addBtn);

    expect(onAddItem).toHaveBeenCalledTimes(1);
    expect(onAddItem).toHaveBeenCalledWith(
      expect.objectContaining({
        category_code: "MAT-CARDBOARD",
        quantity: 10,
        est_min_price: 30,
        est_max_price: 40,
      })
    );
  });

  it("แสดงสรุปตะกร้าหลายรายการและยอดรวม Min-Max พร้อมข้อความกำกับตาม BR-01 (D-06)", () => {
    const mockBasket = [
      {
        category_code: "MAT-CARDBOARD",
        category_name: "กระดาษลัง",
        unit: "kg",
        quantity: 10,
        est_min_price: 30,
        est_max_price: 40,
      },
      {
        category_code: "MAT-WHITE-PAPER",
        category_name: "กระดาษขาวดำ",
        unit: "kg",
        quantity: 5,
        est_min_price: 30,
        est_max_price: 35,
      },
    ];

    render(
      <MultiItemBasketSummary
        basket={mockBasket}
        totalMin={60}
        totalMax={75}
        disclaimer="ราคาจริงขึ้นกับสภาพของหน้างาน"
        onRemoveItem={vi.fn()}
        onSubmitOrder={vi.fn()}
      />
    );

    // ตรวจสอบมีรายการแยกบรรทัดทั้ง 2 รายการ
    expect(screen.getByText("กระดาษลัง")).toBeDefined();
    expect(screen.getByText("30–40 บ.")).toBeDefined();
    expect(screen.getByText("กระดาษขาวดำ")).toBeDefined();
    expect(screen.getByText("30–35 บ.")).toBeDefined();

    // ตรวจสอบยอดรวม Min-Max 60–75 บาท
    const totalRange = screen.getByTestId("total-price-range");
    expect(totalRange.textContent).toContain("60–75 บาท");

    // ตรวจสอบข้อความกำกับตาม BR-01
    const disclaimer = screen.getByTestId("disclaimer-text");
    expect(disclaimer.textContent).toContain("ราคาจริงขึ้นกับสภาพของหน้างาน");
  });
});

