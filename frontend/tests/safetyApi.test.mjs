/**
 * Vitest Unit Tests สำหรับ safetyApi.js
 * ทดสอบการเรียก API, Offline Cache (CC-05, REQ-OP-001), และ Error Handling
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  getCachedEmergencyContact,
  setCachedEmergencyContact,
  getCachedEvidences,
  setCachedEvidences,
  fetchEmergencyContact,
  saveEmergencyContact,
  triggerEmergencySos,
  uploadSafetyEvidence,
  fetchSafetyEvidences,
  lockSafetyEvidences,
} from "../src/services/safetyApi.js";

describe("safetyApi Client & Offline Cache Tests", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("sets and gets cached emergency contact (CC-05, REQ-OP-001)", () => {
    const sellerId = "SELLER-CACHE-01";
    const contactData = {
      seller_id: sellerId,
      contact_name: "นายสมชาย (บุตร)",
      contact_phone_masked: "08X-XXX-1234",
    };
    setCachedEmergencyContact(sellerId, contactData);
    const cached = getCachedEmergencyContact(sellerId);
    expect(cached).not.toBeNull();
    expect(cached.contact_name).toBe("นายสมชาย (บุตร)");
    expect(cached.contact_phone_masked).toBe("08X-XXX-1234");
  });

  it("fetches emergency contact online and falls back to cache or default on failure", async () => {
    const sellerId = "SELLER-FETCH-01";

    // 1. Mock Online Fetch
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        seller_id: sellerId,
        contact_name: "พี่สาว",
        relationship: "พี่สาว",
        contact_phone_masked: "08X-XXX-9999",
        is_default: false,
      }),
    });

    const onlineRes = await fetchEmergencyContact(sellerId);
    expect(onlineRes.contact_name).toBe("พี่สาว");
    expect(onlineRes.contact_phone_masked).toBe("08X-XXX-9999");

    // 2. Mock Offline/Network Error -> Fallback to Cache
    global.fetch = vi.fn().mockRejectedValueOnce(new Error("Network Error"));
    const offlineRes = await fetchEmergencyContact(sellerId);
    expect(offlineRes.contact_name).toBe("พี่สาว");
    expect(offlineRes.contact_phone_masked).toBe("08X-XXX-9999");
  });

  it("triggers emergency SOS successfully (AC-S09-02, REQ-QA-001)", async () => {
    const orderId = "ORDER-SOS-VITEST";
    const sellerId = "SELLER-VITEST";

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        sos_id: "SOS-20261103-9999",
        order_id: orderId,
        emergency_phone_to_call: "0812345678",
        status: "TRIGGERED",
        response_time_ms: 120.5,
      }),
    });

    const res = await triggerEmergencySos(orderId, sellerId, { current_lat: 13.7, current_lng: 100.5 });
    expect(res.sos_id).toBe("SOS-20261103-9999");
    expect(res.emergency_phone_to_call).toBe("0812345678");
    expect(res.response_time_ms).toBeLessThan(2000);
  });

  it("uploads evidence and caches it locally (AC-S09-01, CC-05)", async () => {
    const orderId = "ORDER-EVID-VITEST";
    const sellerId = "SELLER-VITEST";

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        evidence_id: "EVD-20261103-8888",
        order_id: orderId,
        media_type: "AUDIO",
        file_size_bytes: 5000,
        duration_seconds: 45,
        is_locked: false,
      }),
    });

    const uploaded = await uploadSafetyEvidence(orderId, sellerId, {
      media_type: "AUDIO",
      duration_seconds: 45,
      file_size_bytes: 5000,
    });
    expect(uploaded.evidence_id).toBe("EVD-20261103-8888");

    const cachedList = getCachedEvidences(orderId);
    expect(cachedList.length).toBe(1);
    expect(cachedList[0].evidence_id).toBe("EVD-20261103-8888");
  });

  it("locks safety evidences and updates local cache (AC-S09-04, REQ-FN-006)", async () => {
    const orderId = "ORDER-LOCK-VITEST";
    setCachedEvidences(orderId, [
      { evidence_id: "EVD-01", is_locked: false },
      { evidence_id: "EVD-02", is_locked: false },
    ]);

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        order_id: orderId,
        locked_count: 2,
        is_locked: true,
      }),
    });

    const res = await lockSafetyEvidences(orderId, "SELLER-1");
    expect(res.is_locked).toBe(true);

    const cached = getCachedEvidences(orderId);
    expect(cached.every((e) => e.is_locked === true)).toBe(true);
  });
});

