import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import SalesHistoryPage from "../src/pages/SalesHistoryPage";
import * as api from "../src/services/postTransactionApi";

describe("AC-S07-04: Digital Receipt Inspection & Offline Access Component Test", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("opens digital receipt modal on button click (REQ-FN-005)", async () => {
    const mockData = {
      seller_id: "SELLER-01",
      summary: { total_sales_amount: 300, total_weight_kg: 30, total_completed_orders: 1 },
      orders: [
        {
          order_id: "ORD-REC-TEST",
          completed_at: "2026-11-03T10:00:00Z",
          collector_id: "COL-01",
          collector_name: "นายสมคิด",
          collector_phone_masked: "08X-XXX-1122",
          total_settled_amount: 300,
          payment_method: "PROMPTPAY",
          items: [],
        },
      ],
      is_offline_cached: false,
    };

    const mockReceipt = {
      receipt_no: "REC-20261103-9999",
      order_id: "ORD-REC-TEST",
      seller_name: "ผู้ขาย",
      seller_phone_masked: "08X-XXX-3344",
      buyer_name: "นายสมคิด",
      buyer_phone_masked: "08X-XXX-1122",
      total_amount: 300,
      payment_method: "PROMPTPAY",
      items: [],
      is_offline_cached: false,
    };

    vi.spyOn(api, "fetchSalesHistory").mockResolvedValue(mockData);
    vi.spyOn(api, "fetchReceipt").mockResolvedValue(mockReceipt);

    render(<SalesHistoryPage sellerId="SELLER-01" />);

    await waitFor(() => {
      expect(screen.getByTestId("open-receipt-btn-ORD-REC-TEST")).toBeDefined();
    });

    // กดปุ่มดูใบเสร็จดิจิทัล
    fireEvent.click(screen.getByTestId("open-receipt-btn-ORD-REC-TEST"));

    await waitFor(() => {
      expect(screen.getByTestId("receipt-modal-backdrop")).toBeDefined();
      expect(screen.getByTestId("receipt-no").textContent).toContain("REC-20261103-9999");
    });

    // ปิด Modal
    fireEvent.click(screen.getByTestId("close-receipt-modal-btn"));
    expect(screen.queryByTestId("receipt-modal-backdrop")).toBeNull();
  });

  it("shows offline banner when data is loaded from offline cache (CC-05, REQ-OP-001)", async () => {
    const mockData = {
      seller_id: "SELLER-01",
      summary: { total_sales_amount: 300, total_weight_kg: 30, total_completed_orders: 1 },
      orders: [],
      is_offline_cached: true,
    };

    vi.spyOn(api, "fetchSalesHistory").mockResolvedValue(mockData);

    render(<SalesHistoryPage sellerId="SELLER-01" />);

    await waitFor(() => {
      expect(screen.getByTestId("offline-history-banner")).toBeDefined();
      expect(screen.getByText("📡 แสดงข้อมูลจากแคชออฟไลน์ในเครื่อง")).toBeDefined();
    });
  });
});
