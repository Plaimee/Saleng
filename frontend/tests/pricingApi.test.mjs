import { describe, it, expect } from "vitest";
import {
  fetchBenchmarkPrices,
  calculateEstimate,
  submitOrder,
  getCachedBenchmarkPrices,
  setCachedBenchmarkPrices,
} from "../src/services/pricingApi.js";

/**
 * T-05: Pricing API Client & Offline Cache Unit Tests
 * รองรับ CC-05, REQ-OP-001, AC-S04-04
 */
describe("T-05: Pricing API Client & Offline Cache Tests", () => {
  it("fetchBenchmarkPrices online succeeds and writes cache", async () => {
    const mockPrices = {
      prices: [
        { category_code: "MAT-CARDBOARD", min_price_per_unit: 3, max_price_per_unit: 4 }
      ],
      last_updated_at: "2026-11-03T06:00:00Z"
    };

    const mockFetch = async () => ({
      ok: true,
      status: 200,
      json: async () => mockPrices,
    });

    const result = await fetchBenchmarkPrices(mockFetch);
    expect(result.isOffline).toBe(false);
    expect(result.prices.length).toBe(1);

    // Check cache was written
    const cached = getCachedBenchmarkPrices();
    expect(cached).toBeDefined();
    expect(cached.data.prices[0].category_code).toBe("MAT-CARDBOARD");
  });

  it("fetchBenchmarkPrices offline falls back to cached data (CC-05, REQ-OP-001)", async () => {
    // Mock failing network (fetch throws)
    const mockFetchFailing = async () => {
      throw new Error("Network request failed: Offline");
    };

    const result = await fetchBenchmarkPrices(mockFetchFailing);
    expect(result.isOffline).toBe(true);
    expect(result.offlineNotice).toContain("ข้อมูลอาจไม่อัปเดต");
    expect(result.prices[0].category_code).toBe("MAT-CARDBOARD");
  });

  it("calculateEstimate validates positive quantity (AC-S04-04)", async () => {
    // Test quantity <= 0
    await expect(
      calculateEstimate([{ category_code: "MAT-CARDBOARD", unit: "kg", quantity: 0 }])
    ).rejects.toThrow("กรุณากรอกปริมาณมากกว่า 0");

    await expect(
      calculateEstimate([{ category_code: "MAT-CARDBOARD", unit: "kg", quantity: -5 }])
    ).rejects.toThrow("กรุณากรอกปริมาณมากกว่า 0");
  });

  it("calculateEstimate sends items and returns min-max estimate (AC-S04-02)", async () => {
    const mockResponse = {
      total_min_price: 150.0,
      total_max_price: 200.0,
      items: [
        {
          category_code: "MAT-CARDBOARD",
          category_name: "กระดาษลัง",
          unit: "kg",
          quantity: 50.0,
          est_min_price: 150.0,
          est_max_price: 200.0,
        }
      ],
      disclaimer: "ราคาประเมินเบื้องต้น อาจมีการปรับเปลี่ยนตามคุณภาพจริงหน้างาน"
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain("/api/v1/pricing/calculate-estimate");
      expect(options.method).toBe("POST");
      const body = JSON.parse(options.body);
      expect(body.items.length).toBe(1);
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const result = await calculateEstimate(
      [{ category_code: "MAT-CARDBOARD", unit: "kg", quantity: 50 }],
      mockFetch
    );
    expect(result.total_min_price).toBe(150.0);
    expect(result.total_max_price).toBe(200.0);
    expect(result.disclaimer).toContain("ราคาประเมินเบื้องต้น");
  });

  it("submitOrder submits order and receives status (AC-S04-03)", async () => {
    const mockOrderResponse = {
      order_id: "ORD-TEST-001",
      seller_id: "USR-SELLER-01",
      status: "S2",
      total_min_price: 600.0,
      total_max_price: 800.0,
      is_route_drop_in: false,
      is_building_group_drop: false,
      threshold_met: true,
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain("/api/v1/orders/validate-and-submit");
      return {
        ok: true,
        status: 201,
        json: async () => mockOrderResponse,
      };
    };

    const orderPayload = {
      seller_id: "USR-SELLER-01",
      items: [{ category_code: "MAT-CARDBOARD", unit: "kg", quantity: 200 }],
      selected_option: "NORMAL",
    };

    const result = await submitOrder(orderPayload, mockFetch);
    expect(result.ok).toBe(true);
    expect(result.data.order_id).toBe("ORD-TEST-001");
    expect(result.data.status).toBe("S2");
    expect(result.data.threshold_met).toBe(true);
  });
});
