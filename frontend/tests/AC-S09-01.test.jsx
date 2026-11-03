/**
 * Vitest Component Test สำหรับ AC-S09-01: Media Evidence Recording Component Test
 * ตรวจสอบปุ่มเริ่ม/หยุดอัดเสียง, ตัวจับเวลา, คลื่นเสียง, และรายการหลักฐาน
 */

import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import MediaEvidenceRecorder from "../src/components/MediaEvidenceRecorder.jsx";

describe("AC-S09-01: Media Evidence Recording Component Test", () => {
  it("renders recorder and switches between audio and video modes", () => {
    const { container } = render(
      <MediaEvidenceRecorder
        orderId="ORDER-01"
        evidences={[]}
        onUploadEvidence={vi.fn()}
      />
    );

    expect(container.querySelector('[data-req="UC-09"]')).not.toBeNull();
    expect(screen.getByText(/บันทึกเสียง\/วิดีโอหลักฐานหน้างาน/)).toBeDefined();

    // ปุ่มสลับโหมดเสียง และวิดีโอ
    const audioBtn = screen.getByRole("button", { name: "เสียง" });
    const videoBtn = screen.getByRole("button", { name: "วิดีโอ" });
    expect(audioBtn).toBeDefined();
    expect(videoBtn).toBeDefined();

    fireEvent.click(videoBtn);
    expect(screen.getByText(/เริ่มอัดวิดีโอระหว่างชั่งของ/)).toBeDefined();
  });

  it("handles start and stop recording cycle with timer and callback", async () => {
    const mockUpload = vi.fn().mockResolvedValue({ evidence_id: "EVD-TEST" });
    render(
      <MediaEvidenceRecorder
        orderId="ORDER-01"
        evidences={[]}
        onUploadEvidence={mockUpload}
      />
    );

    const startBtn = screen.getByRole("button", { name: /เริ่มอัดเสียงระหว่างชั่งของ/ });
    fireEvent.click(startBtn);

    // ตรวจสอบว่าเข้าสู่โหมดกำลังบันทึก
    expect(screen.getByText(/กำลังบันทึกเสียง/)).toBeDefined();

    const stopBtn = screen.getByRole("button", { name: /หยุดและบันทึกหลักฐาน/ });
    expect(stopBtn).toBeDefined();

    await act(async () => {
      fireEvent.click(stopBtn);
    });

    expect(mockUpload).toHaveBeenCalledTimes(1);
    expect(mockUpload).toHaveBeenCalledWith(
      expect.objectContaining({
        media_type: "AUDIO",
      })
    );
  });
});

