import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import WasteSortingGuideView from "../src/components/WasteSortingGuideView";

describe("AC-S08-02: Waste Sorting & Value-Add Guide Component Test", () => {
  const mockGuides = [
    {
      category_code: "MAT-CARDBOARD",
      category_name: "กระดาษลัง / กล่องลูกฟูก",
      icon: "📦",
      value_add_tips: ["แกะเทปกาวออก", "พับกล่องให้แบนเป็นระเบียบ"],
      price_impact_description: "ได้ราคาสูงสุด 3-4 บาท/กก.",
      precautions: ["ห้ามเปียกน้ำ"],
    },
    {
      category_code: "MAT-WHITE-PAPER",
      category_name: "กระดาษขาวดำ",
      icon: "📄",
      value_add_tips: ["แยกกระดาษขาวล้วน"],
      price_impact_description: "ได้ราคาเพิ่มขึ้นเป็น 6–7 บาท/กก.",
      precautions: ["ไม่ปนกระดาษคาร์บอน"],
    },
  ];

  it("renders guide category tabs and displays value-add tips (UC-08, Q-02)", () => {
    render(<WasteSortingGuideView guides={mockGuides} isOffline={false} />);

    expect(screen.getByTestId("waste-sorting-guide-view")).toBeDefined();
    expect(screen.getByTestId("guide-tab-MAT-CARDBOARD")).toBeDefined();
    expect(screen.getByTestId("guide-tab-MAT-WHITE-PAPER")).toBeDefined();

    // Default: กระดาษลัง
    expect(screen.getByText("พับกล่องให้แบนเป็นระเบียบ")).toBeDefined();
    expect(screen.getByText("ได้ราคาสูงสุด 3-4 บาท/กก.")).toBeDefined();

    // เปลี่ยนไปแท็บกระดาษขาวดำ
    fireEvent.click(screen.getByTestId("guide-tab-MAT-WHITE-PAPER"));
    expect(screen.getByText("แยกกระดาษขาวล้วน")).toBeDefined();
    expect(screen.getByText("ได้ราคาเพิ่มขึ้นเป็น 6–7 บาท/กก.")).toBeDefined();
  });
});

