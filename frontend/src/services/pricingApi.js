/**
 * Pricing API Client & Offline Cache Module
 * รองรับ CC-01 (Mobile-First SPA), CC-05 (Offline Cache), REQ-OP-001, AC-S04-01..05
 */

const CACHE_KEY = "saleng_benchmark_prices_cache";
const API_BASE_URL = typeof process !== "undefined" && process.env?.VITE_API_BASE_URL
  ? process.env.VITE_API_BASE_URL
  : "http://localhost:8000";

// Simple in-memory fallback if localStorage is unavailable
let memoryCache = null;

function getStorage() {
  if (typeof window !== "undefined" && window.localStorage) {
    return window.localStorage;
  }
  return {
    getItem: (key) => memoryCache?.[key] || null,
    setItem: (key, val) => {
      memoryCache = memoryCache || {};
      memoryCache[key] = val;
    },
    removeItem: (key) => {
      if (memoryCache) delete memoryCache[key];
    },
  };
}

/**
 * ดึงราคากลางล่าสุดจาก Cache
 * รองรับ CC-05, REQ-OP-001
 */
export function getCachedBenchmarkPrices() {
  try {
    const storage = getStorage();
    const raw = storage.getItem(CACHE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

/**
 * บันทึกราคากลางลง Cache
 */
export function setCachedBenchmarkPrices(data) {
  try {
    const storage = getStorage();
    const payload = {
      data,
      cachedAt: new Date().toISOString(),
    };
    storage.setItem(CACHE_KEY, JSON.stringify(payload));
  } catch (e) {
    // ignore cache write error
  }
}

/**
 * ดึงตารางเรตราคากลางรับซื้อรายวัน
 * รองรับ REQ-DAT-001, AC-S04-01, CC-05, REQ-OP-001
 * - หากมีสัญญาณ: ดึงจาก API และแคชลง Storage
 * - หากออฟไลน์: คืนค่าจากแคชล่าสุดพร้อม flag isOffline: true และแจ้งเตือน
 */
export async function fetchBenchmarkPrices(fetchFn = fetch, baseUrl = API_BASE_URL) {
  try {
    const res = await fetchFn(`${baseUrl}/api/v1/pricing/benchmark-prices`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ไม่สามารถดึงราคากลางได้`);
    }
    const data = await res.json();
    setCachedBenchmarkPrices(data);
    return {
      ...data,
      isOffline: false,
    };
  } catch (err) {
    // พยายามอ่านจาก Cache เมื่อเกิดข้อผิดพลาดเครือข่ายหรือออฟไลน์ (CC-05, REQ-OP-001)
    const cached = getCachedBenchmarkPrices();
    if (cached && cached.data) {
      return {
        ...cached.data,
        isOffline: true,
        offlineNotice: "ข้อมูลอาจไม่อัปเดต (เปิดจากแคชออฟไลน์)",
        cachedAt: cached.cachedAt,
      };
    }
    throw err;
  }
}

/**
 * คำนวณช่วงราคาประเมินเบื้องต้น
 * รองรับ Card 01, BR-01, AC-S04-02, AC-S04-04, AC-S04-05, D-02, D-06
 * - ตรวจสอบปริมาณ > 0 หากไม่ถูกต้องแจ้งเตือนทันที
 * - เรียก API เพื่อคำนวณและคืนผลลัพธ์
 */
export async function calculateEstimate(items, fetchFn = fetch, baseUrl = API_BASE_URL) {
  if (!items || items.length === 0) {
    throw new Error("กรุณาระบุรายการของเก่าอย่างน้อย 1 รายการ");
  }

  // Client-side validation: ตรวจสอบปริมาณ > 0 (AC-S04-04)
  for (const item of items) {
    if (typeof item.quantity !== "number" || item.quantity <= 0) {
      throw new Error("กรุณากรอกปริมาณมากกว่า 0");
    }
  }

  const res = await fetchFn(`${baseUrl}/api/v1/pricing/calculate-estimate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail || "เกิดข้อผิดพลาดในการคำนวณราคา";
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return await res.json();
}

/**
 * ส่งคำขอนัดหมาย (เดี่ยว, ฝากรวมทางผ่าน, จุดรับรวมอาคาร)
 * รองรับ REQ-FN-001, REQ-FN-006, AC-S04-03, D-01, D-03
 * - หากไม่ผ่านเกณฑ์ขั้นต่ำ 500 บาท สำหรับนัดหมายเดี่ยว คืน error พร้อมรายการทางเลือก
 */
export async function submitOrder(orderPayload, fetchFn = fetch, baseUrl = API_BASE_URL) {
  const res = await fetchFn(`${baseUrl}/api/v1/orders/validate-and-submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(orderPayload),
  });

  const data = await res.json().catch(() => ({}));

  if (res.status === 201) {
    return {
      ok: true,
      data,
    };
  }

  if (res.status === 400 && data.error === "MINIMUM_THRESHOLD_NOT_MET") {
    return {
      ok: false,
      error: "MINIMUM_THRESHOLD_NOT_MET",
      message: data.message,
      total_est_min_price: data.total_est_min_price,
      total_bags: data.total_bags,
      allowed_alternatives: data.allowed_alternatives || ["ROUTE_DROP_IN", "BUILDING_GROUP"],
    };
  }

  throw new Error(data.detail || data.message || `เกิดข้อผิดพลาดในการส่งคำขอ (HTTP ${res.status})`);
}

