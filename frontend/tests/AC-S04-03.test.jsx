import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ThresholdGuardModal from "../src/components/ThresholdGuardModal.jsx";

/**
 * AC-S04-03: Minimum Threshold Guard & Alternative Selection
 * รองรับ REQ-FN-001, REQ-FN-006, AC-S04-03, D-01, D-03
 */
describe("AC-S04-03: Minimum Threshold Guard Modal", () => {
  it("แสดง Modal แจ้งเตือนเมื่อไม่ถึงเกณฑ์ขั้นต่ำ 500 บาท และมี 2 ทางเลือก (AC-S04-03)", () => {
    const onSelectAlt = vi.fn();
    const onClose = vi.fn();

    render(
      <ThresholdGuardModal
        isOpen={true}
        totalMin={350}
        totalBags={1}
        onSelectAlternative={onSelectAlt}
        onClose={onClose}
      />
    );

    // ตรวจสอบหัวข้อและยอดประเมิน
    expect(screen.getByText("ยอดประเมินไม่ถึงเกณฑ์ขั้นต่ำ")).toBeDefined();
    expect(screen.getByText("350 บาท")).toBeDefined();

    // 1. ตรวจสอบปุ่มทางเลือก: ฝากรวมกับจุดรับทางผ่าน (REQ-FN-001, D-03)
    const routeDropBtn = screen.getByTestId("alt-route-drop-btn");
    expect(routeDropBtn).toBeDefined();
    fireEvent.click(routeDropBtn);
    expect(onSelectAlt).toHaveBeenCalledWith("ROUTE_DROP_IN");

    // 2. ตรวจสอบปุ่มทางเลือก: จุดรับรวมประจำอาคาร/หอพัก (REQ-FN-006, D-03)
    const buildingGroupBtn = screen.getByTestId("alt-building-group-btn");
    expect(buildingGroupBtn).toBeDefined();
    fireEvent.click(buildingGroupBtn);
    expect(onSelectAlt).toHaveBeenCalledWith("BUILDING_GROUP");

    // 3. ตรวจสอบปุ่มปิด / กลับไปแก้ไข
    const cancelBtn = screen.getByTestId("cancel-guard-modal-btn");
    fireEvent.click(cancelBtn);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("ไม่แสดงผลเมื่อ isOpen เป็น false", () => {
    const { container } = render(
      <ThresholdGuardModal
        isOpen={false}
        totalMin={600}
        totalBags={2}
        onSelectAlternative={vi.fn()}
        onClose={vi.fn()}
      />
    );
    expect(container.firstChild).toBeNull();
  });
});

