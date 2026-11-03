import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ItemPriceCalculator from "../src/components/ItemPriceCalculator.jsx";

/**
 * AC-S04-04: Invalid Quantity Guard
 * รองรับ Card 01 Exception Case, AC-S04-04
 */
describe("AC-S04-04: Invalid Quantity Guard", () => {
  const mockPrices = [
    {
      category_code: "MAT-CARDBOARD",
      category_name: "กระดาษลัง",
      unit: "kg",
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
    },
  ];

  it("บล็อกและแจ้งเตือน 'กรุณากรอกปริมาณมากกว่า 0' เมื่อกรอก 0 (AC-S04-04)", () => {
    const onAddItem = vi.fn();
    render(<ItemPriceCalculator benchmarkPrices={mockPrices} onAddItem={onAddItem} />);

    const qtyInput = screen.getByTestId("quantity-input");
    const addBtn = screen.getByTestId("add-item-btn");

    fireEvent.change(qtyInput, { target: { value: "0" } });
    fireEvent.click(addBtn);

    const error = screen.getByTestId("quantity-error");
    expect(error.textContent).toContain("กรุณากรอกปริมาณมากกว่า 0");
    expect(onAddItem).not.toHaveBeenCalled();
  });

  it("บล็อกและแจ้งเตือน 'กรุณากรอกปริมาณมากกว่า 0' เมื่อกรอกค่าติดลบ (AC-S04-04)", () => {
    const onAddItem = vi.fn();
    render(<ItemPriceCalculator benchmarkPrices={mockPrices} onAddItem={onAddItem} />);

    const qtyInput = screen.getByTestId("quantity-input");
    const addBtn = screen.getByTestId("add-item-btn");

    fireEvent.change(qtyInput, { target: { value: "-5" } });
    fireEvent.click(addBtn);

    const error = screen.getByTestId("quantity-error");
    expect(error.textContent).toContain("กรุณากรอกปริมาณมากกว่า 0");
    expect(onAddItem).not.toHaveBeenCalled();
  });
});

