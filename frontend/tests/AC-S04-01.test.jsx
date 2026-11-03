import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import BenchmarkPriceTable from "../src/components/BenchmarkPriceTable.jsx";

/**
 * AC-S04-01: Benchmark Price Table Daily Refresh
 * รองรับ REQ-DAT-001, AC-S04-01, CC-05, REQ-OP-001, D-04
 */
describe("AC-S04-01: Benchmark Price Table Component", () => {
  const mockPrices = [
    {
      category_code: "MAT-CARDBOARD",
      category_name: "กระดาษลัง",
      unit: "kg",
      min_price_per_unit: 3.0,
      max_price_per_unit: 4.0,
      grading_condition: "แห้ง สะอาด ไม่เปียกน้ำ",
    },
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
  ];

  it("แสดงตารางช่วงราคากลางจำแนกตามประเภทและหน่วยนับถูกต้อง (AC-S04-01)", () => {
    render(
      <BenchmarkPriceTable
        prices={mockPrices}
        lastUpdatedAt="2026-11-03T06:00:00Z"
      />
    );

    // ตรวจสอบตารางมีอยู่และแสดง data-req="REQ-DAT-001"
    const tableContainer = screen.getByTestId("benchmark-price-table");
    expect(tableContainer).toBeDefined();

    // ตรวจสอบการแสดงผลกระดาษลัง 3–4 บาท
    expect(screen.getByText("กระดาษลัง")).toBeDefined();
    expect(screen.getByText("3–4 บาท")).toBeDefined();

    // ตรวจสอบการแสดงผลขวดแก้วกระสอบ 40–60 บาท
    expect(screen.getByText("ขวดแก้ว (กระสอบ)")).toBeDefined();
    expect(screen.getByText("40–60 บาท")).toBeDefined();

    // ตรวจสอบป้ายอัปเดต 06:00 น.
    const badge = screen.getByTestId("last-updated-badge");
    expect(badge.textContent).toContain("06:00 น.");
  });

  it("แสดงป้ายแจ้งเตือนเมื่ออยู่ในโหมดออฟไลน์ (CC-05, REQ-OP-001)", () => {
    render(
      <BenchmarkPriceTable
        prices={mockPrices}
        lastUpdatedAt="2026-11-03T06:00:00Z"
        isOffline={true}
        offlineNotice="ข้อมูลอาจไม่อัปเดต (เปิดจากแคชออฟไลน์)"
      />
    );

    const alert = screen.getByTestId("offline-alert");
    expect(alert).toBeDefined();
    expect(alert.textContent).toContain("ข้อมูลอาจไม่อัปเดต (เปิดจากแคชออฟไลน์)");
  });
});

