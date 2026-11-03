/**
 * Vitest Component Test สำหรับ AC-S09-02: Emergency SOS Button & Confirmation Modal
 * ตรวจสอบความสูง >= 48px (REQ-UX-001), การแสดงพิกัด และปุ่มโทรด่วน tel:
 */

import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import EmergencySosButton from "../src/components/EmergencySosButton.jsx";
import SosConfirmationModal from "../src/components/SosConfirmationModal.jsx";

describe("AC-S09-02: Emergency SOS Button & Confirmation Modal", () => {
  it("renders big SOS button with min-h-[48px] and triggers action (REQ-UX-001)", () => {
    const handleTrigger = vi.fn();
    const { container } = render(
      <EmergencySosButton onTriggerSos={handleTrigger} />
    );

    const button = container.querySelector('[data-req="UC-09"]');
    expect(button).not.toBeNull();
    expect(button.className).toContain("min-h-[48px]");
    expect(button.className).toContain("bg-red-600");

    fireEvent.click(button);
    expect(handleTrigger).toHaveBeenCalledTimes(1);
  });

  it("renders SOS confirmation modal with dispatch details and call button", () => {
    const handleClose = vi.fn();
    const handleCall = vi.fn();

    const sosData = {
      sos_id: "SOS-20261103-TEST",
      emergency_phone_to_call: "0891234567",
      emergency_contact_name: "นายสมศักดิ์ (พี่ชาย)",
      geo_point: { lat: 13.7563, lng: 100.5018 },
      response_time_ms: 85.0,
    };

    render(
      <SosConfirmationModal
        isOpen={true}
        onClose={handleClose}
        sosData={sosData}
        onCallPhone={handleCall}
      />
    );

    expect(screen.getByText(/แจ้งเหตุฉุกเฉิน SOS สำเร็จ/)).toBeDefined();
    expect(screen.getByText(/SOS-20261103-TEST/)).toBeDefined();
    expect(screen.getByText(/13.7563, 100.5018/)).toBeDefined();

    const callContactBtn = screen.getByRole("button", { name: /โทรหาผู้ติดต่อฉุกเฉิน/ });
    expect(callContactBtn).toBeDefined();

    fireEvent.click(callContactBtn);
    expect(handleCall).toHaveBeenCalledWith("0891234567");

    const callPoliceBtn = screen.getByRole("button", { name: /โทรแจ้งเหตุด่วน 191/ });
    fireEvent.click(callPoliceBtn);
    expect(handleCall).toHaveBeenCalledWith("191");
  });
});

