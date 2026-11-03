import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import SalesHistoryPage from "../src/pages/SalesHistoryPage";
import * as api from "../src/services/postTransactionApi";

describe("AC-S07-03: Sales History & PII Masking Component Test", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders summary statistics cards and masked phone numbers correctly (REQ-SEC-002, Q-04)", async () => {
    const mockData = {
      seller_id: "SELLER-01",
      summary: {
        total_sales_amount: 1250,
        total_weight_kg: 120.5,
        total_completed_orders: 3,
      },
      orders: [
        {
          order_id: "ORD-001",
          completed_at: "2026-11-03T10:00:00Z",
          collector_id: "COL-01",
          collector_name: "นายสมชาย",
          collector_phone_masked: "08X-XXX-8899",
          is_favorite_collector: true,
          total_settled_amount: 500,
          payment_method: "PROMPTPAY",
          items: [{ category_name: "กระดาษลัง", actual_quantity: 50, unit: "kg", settled_item_price: 500 }],
        },
      ],
      is_offline_cached: false,
    };

    vi.spyOn(api, "fetchSalesHistory").mockResolvedValue(mockData);

    render(<SalesHistoryPage sellerId="SELLER-01" />);

    // ตรวจสอบตัวเลขสรุป 3 ช่อง
    await waitFor(() => {
      expect(screen.getByTestId("total-sales-amount").textContent).toContain("1,250");
      expect(screen.getByTestId("total-weight-kg").textContent).toContain("120.5 กก.");
      expect(screen.getByTestId("total-completed-orders").textContent).toContain("3 ครั้ง");
    });

    // ตรวจสอบ PII Masking: เบอร์โทรต้องถูก Masking ตาม REQ-SEC-002
    expect(screen.getByTestId("collector-phone-masked").textContent).toContain("08X-XXX-8899");
  });
});
