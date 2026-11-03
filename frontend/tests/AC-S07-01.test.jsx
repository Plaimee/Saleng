import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PostTransactionRatingModal from "../src/components/PostTransactionRatingModal";
import * as api from "../src/services/postTransactionApi";

describe("AC-S07-01: Post-Job Rating & Review Component Test", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders 5 star buttons and allows rating selection (1-5 stars)", async () => {
    render(
      <PostTransactionRatingModal
        isOpen={true}
        orderId="ORD-S7-TEST"
        sellerId="SELLER-01"
        collectorName="ลุงสมคิด (ซาเล้ง)"
      />
    );

    expect(screen.getByTestId("post-transaction-rating-modal")).toBeDefined();
    expect(screen.getByText("ให้คะแนนและรีวิวบริการ")).toBeDefined();
    expect(screen.getByText("ลุงสมคิด (ซาเล้ง)")).toBeDefined();

    // ปุ่มดาว 1 ถึง 5
    const star5 = screen.getByTestId("star-btn-5");
    fireEvent.click(star5);
    expect(screen.getByText("ประทับใจมาก ตาชั่งเที่ยงตรง")).toBeDefined();

    // ปุ่มส่งรีวิวปลดล็อก
    const submitBtn = screen.getByTestId("submit-review-btn");
    expect(submitBtn.disabled).toBe(false);
  });

  it("submits review successfully and triggers onSuccess callback", async () => {
    const mockSubmit = vi.spyOn(api, "submitReview").mockResolvedValue({
      id: "REV-123",
      order_id: "ORD-S7-TEST",
      rating: 5,
      comment: "บริการดีมาก",
    });

    const handleSuccess = vi.fn();

    render(
      <PostTransactionRatingModal
        isOpen={true}
        orderId="ORD-S7-TEST"
        sellerId="SELLER-01"
        onSuccess={handleSuccess}
      />
    );

    // เลือก 5 ดาว
    fireEvent.click(screen.getByTestId("star-btn-5"));

    // พิมพ์ความคิดเห็น
    const commentInput = screen.getByTestId("review-comment-input");
    fireEvent.change(commentInput, { target: { value: "บริการดีมาก" } });

    // กดส่งรีวิว
    fireEvent.click(screen.getByTestId("submit-review-btn"));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith("ORD-S7-TEST", {
        sellerId: "SELLER-01",
        rating: 5,
        comment: "บริการดีมาก",
      });
      expect(screen.getByText("ขอบคุณสำหรับคะแนนรีวิว!")).toBeDefined();
      expect(handleSuccess).toHaveBeenCalled();
    });
  });

  it("allows skipping rating without submitting (Q-01)", () => {
    const handleSkip = vi.fn();

    render(
      <PostTransactionRatingModal
        isOpen={true}
        orderId="ORD-S7-TEST"
        onSkip={handleSkip}
      />
    );

    const skipBtn = screen.getByTestId("skip-review-btn");
    fireEvent.click(skipBtn);
    expect(handleSkip).toHaveBeenCalledTimes(1);
  });
});
