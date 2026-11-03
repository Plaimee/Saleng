import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  submitReview,
  getReview,
  toggleFavorite,
  getFavorites,
  fetchSalesHistory,
  fetchReceipt,
  setCachedSalesHistory,
  getCachedSalesHistory,
  setCachedReceipt,
  getCachedReceipt,
} from "../src/services/postTransactionApi.js";

describe("postTransactionApi client & offline cache (T-05, AC-S07-04)", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("submitReview: sends POST request to review endpoint and parses response", async () => {
    const mockResponse = {
      id: "REV-001",
      order_id: "ORD-001",
      seller_id: "SELLER-01",
      collector_id: "COL-01",
      rating: 5,
      comment: "ดีมาก",
      created_at: "2026-11-03T10:00:00Z",
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await submitReview("ORD-001", {
      sellerId: "SELLER-01",
      rating: 5,
      comment: "ดีมาก",
    });

    expect(result.id).toBe("REV-001");
    expect(result.rating).toBe(5);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/orders/ORD-001/review",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          seller_id: "SELLER-01",
          rating: 5,
          comment: "ดีมาก",
        }),
      })
    );
  });

  it("submitReview: throws formatted error on 409 conflict or bad request", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      json: async () => ({ detail: "คำขอนี้ได้รับการส่งรีวิวแล้ว" }),
    });

    await expect(
      submitReview("ORD-001", { sellerId: "SELLER-01", rating: 5 })
    ).rejects.toThrow("คำขอนี้ได้รับการส่งรีวิวแล้ว");
  });

  it("toggleFavorite: sends POST and returns favorite status", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        seller_id: "SELLER-01",
        collector_id: "COL-01",
        is_favorite: true,
        message: "บันทึกเป็นผู้รับซื้อประจำเรียบร้อยแล้ว",
      }),
    });

    const result = await toggleFavorite("SELLER-01", "COL-01");
    expect(result.is_favorite).toBe(true);
    expect(result.message).toContain("บันทึกเป็นผู้รับซื้อประจำ");
  });

  it("fetchSalesHistory: caches response and supports offline fallback (CC-05, REQ-OP-001)", async () => {
    const mockHistory = {
      seller_id: "SELLER-01",
      summary: {
        total_sales_amount: 500,
        total_weight_kg: 50,
        total_completed_orders: 2,
      },
      orders: [
        { order_id: "ORD-01", total_settled_amount: 300 },
        { order_id: "ORD-02", total_settled_amount: 200 },
      ],
    };

    // 1. Online fetch: caches data
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockHistory,
    });

    const onlineResult = await fetchSalesHistory("SELLER-01");
    expect(onlineResult.is_offline_cached).toBe(false);
    expect(onlineResult.summary.total_sales_amount).toBe(500);

    const cached = getCachedSalesHistory("SELLER-01");
    expect(cached).not.toBeNull();
    expect(cached.data.summary.total_sales_amount).toBe(500);

    // 2. Offline fetch: returns cached data with is_offline_cached: true
    global.fetch = vi.fn().mockRejectedValue(new Error("Network Error"));

    const offlineResult = await fetchSalesHistory("SELLER-01");
    expect(offlineResult.is_offline_cached).toBe(true);
    expect(offlineResult.summary.total_sales_amount).toBe(500);
    expect(offlineResult.orders.length).toBe(2);
  });

  it("fetchReceipt: caches receipt and returns offline fallback on network failure", async () => {
    const mockReceipt = {
      receipt_no: "REC-20261103-0001",
      order_id: "ORD-01",
      total_amount: 300,
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockReceipt,
    });

    const onlineReceipt = await fetchReceipt("ORD-01");
    expect(onlineReceipt.receipt_no).toBe("REC-20261103-0001");
    expect(onlineReceipt.is_offline_cached).toBe(false);

    // Network drops
    global.fetch = vi.fn().mockRejectedValue(new Error("Network disconnected"));

    const offlineReceipt = await fetchReceipt("ORD-01");
    expect(offlineReceipt.receipt_no).toBe("REC-20261103-0001");
    expect(offlineReceipt.is_offline_cached).toBe(true);
  });
});

