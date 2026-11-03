import { describe, it, expect, beforeEach } from "vitest";
import {
  recordWeighing,
  confirmWeights,
  requestReweigh,
  raiseDispute,
  confirmPayment,
  fetchReceipt,
  getCachedReceipt,
  setCachedReceipt,
} from "../src/services/paymentApi.js";

/**
 * T-06: Payment API Client & Offline Cache Unit Tests
 * รองรับ CC-01, CC-05, REQ-OP-001, AC-S06-01..05
 */
describe("T-06: Payment API Client & Offline Cache Tests", () => {
  const mockOrderId = "ORD-TEST-PAY-01";
  const mockSellerId = "USR-SELLER-01";

  it("recordWeighing sends actual quantity and returns S5", async () => {
    const mockResponse = {
      order_id: mockOrderId,
      status: "S5",
      scale_photo_url: "https://scale.jpg",
      total_settled_amount: 350.0,
      seller_confirmed_weight: false,
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain(`/api/v1/orders/${mockOrderId}/record-weighing`);
      expect(options.method).toBe("POST");
      const body = JSON.parse(options.body);
      expect(body.items.length).toBe(1);
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const res = await recordWeighing(
      mockOrderId,
      "https://scale.jpg",
      [{ item_id: "itm-01", actual_quantity: 50.0 }],
      mockFetch
    );
    expect(res.status).toBe("S5");
    expect(res.total_settled_amount).toBe(350.0);
  });

  it("confirmWeights sends sellerId and returns S6 (AC-S06-01)", async () => {
    const mockResponse = {
      order_id: mockOrderId,
      status: "S6",
      seller_confirmed_weight_at: "2026-11-03T12:00:00Z",
      total_settled_amount: 350.0,
      message: "ผู้ขายยืนยันตัวเลขน้ำหนักเรียบร้อยแล้ว",
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain(`/api/v1/orders/${mockOrderId}/confirm-weights`);
      const body = JSON.parse(options.body);
      expect(body.seller_id).toBe(mockSellerId);
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const res = await confirmWeights(mockOrderId, mockSellerId, mockFetch);
    expect(res.status).toBe("S6");
    expect(res.seller_confirmed_weight_at).toBeDefined();
  });

  it("confirmWeights throws error on 403 Forbidden (not owner)", async () => {
    const mockFetch = async () => ({
      ok: false,
      status: 403,
      json: async () => ({ detail: "ผู้ขายเจ้าของคำขอเท่านั้น" }),
    });

    await expect(confirmWeights(mockOrderId, "wrong-seller", mockFetch)).rejects.toThrow(
      "ผู้ขายเจ้าของคำขอเท่านั้น"
    );
  });

  it("requestReweigh sends reason and returns S4 (AC-S06-02)", async () => {
    const mockResponse = {
      order_id: mockOrderId,
      status: "S4",
      message: "ส่งคำขอชั่งซ้ำแล้ว",
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain(`/api/v1/orders/${mockOrderId}/request-reweigh`);
      const body = JSON.parse(options.body);
      expect(body.reason).toContain("ตาชั่งค้าง");
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const res = await requestReweigh(mockOrderId, mockSellerId, "ตาชั่งค้าง ขอชั่งใหม่", mockFetch);
    expect(res.status).toBe("S4");
  });

  it("raiseDispute sends disputeReason and returns S8 (AC-S06-02)", async () => {
    const mockResponse = {
      order_id: mockOrderId,
      status: "S8",
      dispute_reason: "น้ำหนักหายไปครึ่งหนึ่ง",
      message: "ส่งข้อพิพาทเรียบร้อยแล้ว",
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain(`/api/v1/orders/${mockOrderId}/dispute`);
      const body = JSON.parse(options.body);
      expect(body.dispute_reason).toBe("น้ำหนักหายไปครึ่งหนึ่ง");
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const res = await raiseDispute(mockOrderId, mockSellerId, "น้ำหนักหายไปครึ่งหนึ่ง", mockFetch);
    expect(res.status).toBe("S8");
  });

  it("confirmPayment confirms cash or promptpay and returns S7 (AC-S06-03)", async () => {
    const mockResponse = {
      order_id: mockOrderId,
      status: "S7",
      payment_method: "PROMPTPAY",
      receipt_id: "rec-01",
      receipt_no: "REC-20261103-0001",
      total_amount: 350.0,
    };

    const mockFetch = async (url, options) => {
      expect(url).toContain(`/api/v1/orders/${mockOrderId}/confirm-payment`);
      const body = JSON.parse(options.body);
      expect(body.payment_method).toBe("PROMPTPAY");
      return {
        ok: true,
        status: 200,
        json: async () => mockResponse,
      };
    };

    const res = await confirmPayment(mockOrderId, mockSellerId, "PROMPTPAY", mockFetch);
    expect(res.status).toBe("S7");
    expect(res.receipt_no).toBe("REC-20261103-0001");
  });

  it("fetchReceipt online caches data and returns receipt (AC-S06-04)", async () => {
    const mockReceipt = {
      receipt_id: "rec-01",
      receipt_no: "REC-20261103-0001",
      order_id: mockOrderId,
      total_amount: 350.0,
      payment_method: "CASH",
      seller_phone_masked: "08X-XXX-1234",
      items: [],
      issued_at: "2026-11-03T12:00:00Z",
    };

    const mockFetch = async (url) => {
      expect(url).toContain(`/api/v1/receipts/${mockOrderId}`);
      return {
        ok: true,
        status: 200,
        json: async () => mockReceipt,
      };
    };

    const res = await fetchReceipt(mockOrderId, mockFetch);
    expect(res.isOffline).toBe(false);
    expect(res.receipt.receipt_no).toBe("REC-20261103-0001");

    // ตรวจสอบว่าถูกบันทึกลงแคช
    const cached = getCachedReceipt(mockOrderId);
    expect(cached).toBeDefined();
    expect(cached.data.receipt_no).toBe("REC-20261103-0001");
  });

  it("fetchReceipt offline falls back to cached receipt (CC-05, REQ-OP-001)", async () => {
    // เซฟแคชจำลอง
    setCachedReceipt("ORD-OFFLINE-01", {
      receipt_no: "REC-20261103-9999",
      total_amount: 400.0,
    });

    const mockFailingFetch = async () => {
      throw new Error("Network offline");
    };

    const res = await fetchReceipt("ORD-OFFLINE-01", mockFailingFetch);
    expect(res.isOffline).toBe(true);
    expect(res.offlineNotice).toContain("โหมดออฟไลน์");
    expect(res.receipt.receipt_no).toBe("REC-20261103-9999");
  });

  it("fetchReceipt offline throws error if no cache exists", async () => {
    const mockFailingFetch = async () => {
      throw new Error("Network offline");
    };

    await expect(fetchReceipt("ORD-NEVER-CACHED", mockFailingFetch)).rejects.toThrow(
      "ไม่สามารถเปิดใบเสร็จได้ขณะออฟไลน์"
    );
  });
});

