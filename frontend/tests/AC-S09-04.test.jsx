/**
 * Vitest Component Test สำหรับ AC-S09-04: Evidence Immutability Badge & Panel Test
 * ตรวจสอบป้ายล็อกหลักฐานห้ามแก้ไขเมื่อเกิดข้อพิพาท/SOS
 */

import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import MediaEvidenceRecorder from "../src/components/MediaEvidenceRecorder.jsx";

describe("AC-S09-04: Evidence Immutability Badge Test", () => {
  it("renders locked badge for immutable evidences in dispute or SOS", () => {
    const evidences = [
      {
        evidence_id: "EVD-20261103-0001",
        media_type: "AUDIO",
        duration_seconds: 35,
        is_locked: true,
      },
      {
        evidence_id: "EVD-20261103-0002",
        media_type: "VIDEO",
        duration_seconds: 60,
        is_locked: false,
      },
    ];

    render(
      <MediaEvidenceRecorder
        orderId="ORDER-LOCKED-01"
        evidences={evidences}
        onUploadEvidence={() => {}}
      />
    );

    expect(screen.getByText("EVD-20261103-0001")).toBeDefined();
    expect(screen.getByText("EVD-20261103-0002")).toBeDefined();

    // มีป้ายล็อกแล้วสำหรับรายการแรก
    expect(screen.getByText(/🔒 ล็อกแล้ว/)).toBeDefined();
    expect(screen.getByText("บันทึกแล้ว")).toBeDefined();
  });
});

