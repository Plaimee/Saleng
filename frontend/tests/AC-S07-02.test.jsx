import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import PostTransactionRatingModal from "../src/components/PostTransactionRatingModal";
import SalesOrderCard from "../src/components/SalesOrderCard";
import * as api from "../src/services/postTransactionApi";

describe("AC-S07-02: Favorite Collector Bookmark Component Test", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("toggles favorite collector button in rating modal (Q-03)", async () => {
    const mockToggle = vi.spyOn(api, "toggleFavorite").mockResolvedValue({
      seller_id: "SELLER-01",
      collector_id: "COLLECTOR-01",
      is_favorite: true,
      message: "บันทึกเป็นผู้รับซื้อประจำเรียบร้อยแล้ว",
    });

    render(
      <PostTransactionRatingModal
        isOpen={true}
        orderId="ORD-01"
        sellerId="SELLER-01"
        collectorId="COLLECTOR-01"
        initialIsFavorite={false}
      />
    );

    const favBtn = screen.getByTestId("favorite-toggle-btn");
    expect(favBtn.textContent).toContain("บันทึกเป็นผู้รับซื้อประจำ");

    fireEvent.click(favBtn);

    await waitFor(() => {
      expect(mockToggle).toHaveBeenCalledWith("SELLER-01", "COLLECTOR-01");
      expect(favBtn.textContent).toContain("เป็นผู้รับซื้อประจำแล้ว");
    });
  });

  it("displays favorite badge and triggers toggle callback in SalesOrderCard", () => {
    const mockOrder = {
      order_id: "ORD-S7-99",
      completed_at: "2026-11-03T12:00:00Z",
      collector_id: "COL-01",
      collector_name: "นายสมคิด",
      collector_phone_masked: "08X-XXX-4455",
      is_favorite_collector: true,
      total_settled_amount: 500,
      payment_method: "PROMPTPAY",
      items: [{ category_name: "กระดาษลัง", actual_quantity: 50, unit: "kg", settled_item_price: 500 }],
    };

    const handleToggle = vi.fn();

    render(
      <SalesOrderCard
        order={mockOrder}
        onToggleFavorite={handleToggle}
        onOpenReceipt={() => {}}
      />
    );

    expect(screen.getByTestId("favorite-collector-badge").textContent).toContain("⭐ ขาประจำ");

    const toggleBtn = screen.getByTestId("toggle-fav-btn-ORD-S7-99");
    fireEvent.click(toggleBtn);
    expect(handleToggle).toHaveBeenCalledWith("COL-01");
  });
});
