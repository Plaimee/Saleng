/**
 * Vitest Component Test สำหรับ AC-S09-03: Emergency Contact Modal & Masking
 * ตรวจสอบแบบฟอร์มบันทึกเบอร์ฉุกเฉิน และการแสดงผล PII Masking 08X-XXX-XXXX
 */

import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import EmergencyContactModal from "../src/components/EmergencyContactModal.jsx";

describe("AC-S09-03: Emergency Contact Modal & Masking", () => {
  it("displays masked phone and submits valid contact update", async () => {
    const handleSave = vi.fn().mockResolvedValue({});
    const handleClose = vi.fn();

    const currentContact = {
      contact_name: "นายสมพร สุขเกษม",
      relationship: "สามี",
      contact_phone_masked: "08X-XXX-5678",
    };

    render(
      <EmergencyContactModal
        isOpen={true}
        onClose={handleClose}
        currentContact={currentContact}
        onSaveContact={handleSave}
      />
    );

    // ตรวจสอบการแสดงผล masked phone
    expect(screen.getByText("08X-XXX-5678")).toBeDefined();

    const phoneInput = screen.getByPlaceholderText("08xxxxxxxx");
    fireEvent.change(phoneInput, { target: { value: "0899998888" } });

    const submitBtn = screen.getByRole("button", { name: "บันทึกข้อมูล" });
    await act(async () => {
      fireEvent.click(submitBtn);
    });

    expect(handleSave).toHaveBeenCalledWith({
      contact_name: "นายสมพร สุขเกษม",
      relationship: "สามี",
      contact_phone: "0899998888",
    });
    expect(handleClose).toHaveBeenCalled();
  });
});

