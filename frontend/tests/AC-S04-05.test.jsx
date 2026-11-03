import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ItemPriceCalculator from "../src/components/ItemPriceCalculator.jsx";

/**
 * AC-S04-05: การคำนวณราคาแบบเหมาเป็น 'กระสอบ' (Bag Unit Pricing for Bottles)
 * รองรับ REQ-FN-001, AC-S04-05, D-02
 */
describe("AC-S04-05: Bag Unit Pricing for Bottles Component", () => {
  const mockBenchmarkPrices = [
    {
      category_code: "MAT-GLASS-BOTTLE",
      category_name: "ขวดแก้ว",
      unit: "kg",
      min_price_per_unit: 1.0,
      max_price_per_unit: 2.0,
      grading_condition: "ขวดสมบูรณ์ ไม่แตก",
    },
    {
      category_code: "MAT-GLASS-BOTTLE-BAG",
      category_name: "ขวดแก้ว (กระสอบ)",
      unit: "bag",
      min_price_per_unit: 40.0,
      max_price_per_unit: 60.0,
      grading_condition: "บรรจุกระสอบมาตรฐาน",
    },
    {
      category_code: "MAT-PLASTIC-BOTTLE",
      category_name: "ขวดพลาสติก",
      unit: "kg",
      min_price_per_unit: 8.0,
      max_price_per_unit: 10.0,
      grading_condition: "ขวด PET ใส",
    },
    {
      category_code: "MAT-PLASTIC-BOTTLE-BAG",
      category_name: "ขวดพลาสติก (กระสอบ)",
      unit: "bag",
      min_price_per_unit: 50.0,
      max_price_per_unit: 70.0,
      grading_condition: "บรรจุกระสอบมาตรฐาน",
    },
    {
      category_code: "MAT-CARDBOARD",
      category_name: "กระดาษลัง",
      unit: "kg",
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
      grading_condition: "แห้ง สะอาด",
    },
  ];

  it("แสดงตัวเลือกหน่วย 'กระสอบ' เมื่อเลือกประเภทขวดแก้ว และคำนวณราคาเหมาต่อกระสอบถูกต้อง (AC-S04-05)", () => {
    const handleAddItem = vi.fn();
    render(
      <ItemPriceCalculator
        benchmarkPrices={mockBenchmarkPrices}
        onAddItem={handleAddItem}
      />
    );

    // เลือกประเภทเป็นขวดแก้ว
    const categorySelect = screen.getByTestId("category-select");
    fireEvent.change(categorySelect, { target: { value: "MAT-GLASS-BOTTLE" } });

    // ตรวจสอบว่ามีตัวเลือกหน่วย 'กระสอบ' ปรากฏขึ้น
    const bagUnitBtn = screen.getByTestId("unit-bag-btn");
    expect(bagUnitBtn).toBeDefined();

    // กดเลือกหน่วย 'กระสอบ'
    fireEvent.click(bagUnitBtn);

    // ระบุจำนวน 2 กระสอบ
    const qtyInput = screen.getByTestId("quantity-input");
    fireEvent.change(qtyInput, { target: { value: "2" } });

    // ตรวจสอบราคาประเมินเบื้องต้น: 2 * (40 - 60) = 80 - 120 บาท
    const estimatePreview = screen.getByTestId("live-estimate-preview");
    expect(estimatePreview.textContent).toContain("80");
    expect(estimatePreview.textContent).toContain("120");

    // กดเพิ่มรายการลงตะกร้า
    const submitBtn = screen.getByTestId("add-item-btn");
    fireEvent.click(submitBtn);

    // ตรวจสอบว่า callback ถูกเรียกพร้อม unit: 'bag'
    expect(handleAddItem).toHaveBeenCalledTimes(1);
    expect(handleAddItem).toHaveBeenCalledWith(
      expect.objectContaining({
        category_code: "MAT-GLASS-BOTTLE",
        unit: "bag",
        quantity: 2,
        est_min_price: 80,
        est_max_price: 120,
      })
    );
  });

  it("ไม่แสดงตัวเลือกหน่วย 'กระสอบ' สำหรับวัสดุประเภทกระดาษลัง (AC-S04-05, D-02)", () => {
    render(
      <ItemPriceCalculator
        benchmarkPrices={mockBenchmarkPrices}
        onAddItem={vi.fn()}
      />
    );

    // ค่าเริ่มต้นเป็นกระดาษลัง MAT-CARDBOARD
    const bagUnitBtn = screen.queryByTestId("unit-bag-btn");
    expect(bagUnitBtn).toBeNull();
  });
});
