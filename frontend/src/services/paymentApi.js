/**
 * Payment & Verification API Client & Offline Cache Module
 * รองรับ CC-01 (Mobile-First SPA), CC-05 (Offline Cache), REQ-OP-001, AC-S06-01..05
 */

const RECEIPT_CACHE_KEY_PREFIX = "saleng_receipt_cache_";
const ALL_RECEIPTS_INDEX_KEY = "saleng_cached_receipt_ids";

const API_BASE_URL =
  typeof process !== "undefined" && process.env?.VITE_API_BASE_URL
    ? process.env.VITE_API_BASE_URL
    : "http://localhost:8000";

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
 * ดึงใบเสร็จดิจิทัลจาก Local Storage Cache
 * รองรับ CC-05, REQ-OP-001
 */
export function getCachedReceipt(orderId) {
  try {
    const storage = getStorage();
    const raw = storage.getItem(`${RECEIPT_CACHE_KEY_PREFIX}${orderId}`);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

/**
 * บันทึกใบเสร็จดิจิทัลลงใน Local Storage Cache
 */
export function setCachedReceipt(orderId, data) {
  try {
    const storage = getStorage();
    const payload = {
      data,
      cachedAt: new Date().toISOString(),
    };
    storage.setItem(`${RECEIPT_CACHE_KEY_PREFIX}${orderId}`, JSON.stringify(payload));

    // อัปเดต index ของใบเสร็จทั้งหมด
    const rawIds = storage.getItem(ALL_RECEIPTS_INDEX_KEY);
    const ids = rawIds ? JSON.parse(rawIds) : [];
    if (!ids.includes(orderId)) {
      ids.push(orderId);
      storage.setItem(ALL_RECEIPTS_INDEX_KEY, JSON.stringify(ids));
    }
  } catch (e) {
    // ignore cache write error
  }
}

/**
 * 1. บันทึกผลชั่งจริงหน้างาน (Record Weighing - โดยซาเล้ง)
 * รองรับ REQ-BR-002, P-03
 */
export async function recordWeighing(orderId, scalePhotoUrl, items, customFetch = null) {
  const fetchFn = customFetch || (typeof fetch !== "undefined" ? fetch : null);
  if (!fetchFn) throw new Error("Fetch is not available");

  const res = await fetchFn(`${API_BASE_URL}/api/v1/orders/${orderId}/record-weighing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scale_photo_url: scalePhotoUrl,
      items,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.message || "เกิดข้อผิดพลาดในการบันทึกผลชั่งจริง");
  }
  return data;
}

/**
 * 2. ผู้ขายตรวจสอบและกดยืนยันตัวเลขน้ำหนักจริง (100% Confirmation Gate: S5 -> S6)
 * รองรับ REQ-FN-004, AC-S06-01, P-01, Q-01
 */
export async function confirmWeights(orderId, sellerId, customFetch = null) {
  const fetchFn = customFetch || (typeof fetch !== "undefined" ? fetch : null);
  if (!fetchFn) throw new Error("Fetch is not available");

  const res = await fetchFn(`${API_BASE_URL}/api/v1/orders/${orderId}/confirm-weights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seller_id: sellerId }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.message || "เกิดข้อผิดพลาดในการยืนยันน้ำหนัก");
  }
  return data;
}

/**
 * 3. ผู้ขายขอให้ซาเล้งชั่งน้ำหนักซ้ำ
 * รองรับ AC-S06-02, P-02, Q-02
 */
export async function requestReweigh(orderId, sellerId, reason, customFetch = null) {
  const fetchFn = customFetch || (typeof fetch !== "undefined" ? fetch : null);
  if (!fetchFn) throw new Error("Fetch is not available");

  const res = await fetchFn(`${API_BASE_URL}/api/v1/orders/${orderId}/request-reweigh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seller_id: sellerId,
      reason: reason || "ผู้ขายขอให้ตรวจสอบและชั่งน้ำหนักซ้ำ",
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.message || "เกิดข้อผิดพลาดในการขอชั่งซ้ำ");
  }
  return data;
}

/**
 * 4. ผู้ขายปฏิเสธผลชั่งและส่งข้อพิพาท (S8: Disputed)
 * รองรับ REQ-FN-006, AC-S06-02, P-02, Q-02
 */
export async function raiseDispute(orderId, sellerId, disputeReason, customFetch = null) {
  const fetchFn = customFetch || (typeof fetch !== "undefined" ? fetch : null);
  if (!fetchFn) throw new Error("Fetch is not available");

  const res = await fetchFn(`${API_BASE_URL}/api/v1/orders/${orderId}/dispute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seller_id: sellerId,
      dispute_reason: disputeReason,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.message || "เกิดข้อผิดพลาดในการแจ้งข้อพิพาท");
  }
  return data;
}

/**
 * 5. ผู้ขายยืนยันการรับเงิน (CASH / PROMPTPAY: S6 -> S7)
 * รองรับ UC-07, REQ-FN-005, AC-S06-03, P-04, Q-03
 */
export async function confirmPayment(orderId, sellerId, paymentMethod, customFetch = null) {
  const fetchFn = customFetch || (typeof fetch !== "undefined" ? fetch : null);
  if (!fetchFn) throw new Error("Fetch is not available");

  const res = await fetchFn(`${API_BASE_URL}/api/v1/orders/${orderId}/confirm-payment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seller_id: sellerId,
      payment_method: paymentMethod,
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.message || "เกิดข้อผิดพลาดในการยืนยันรับเงิน");
  }

  return data;
}

/**
 * 6. ดึงใบเสร็จดิจิทัล พร้อมรองรับ Offline Cache Fallback
 * รองรับ REQ-FN-005, REQ-SEC-002, CC-05, REQ-OP-001, AC-S06-04
 */
export async function fetchReceipt(orderId, customFetch = null) {
  const fetchFn = customFetch || (typeof fetch !== "undefined" ? fetch : null);

  if (fetchFn) {
    try {
      const res = await fetchFn(`${API_BASE_URL}/api/v1/receipts/${orderId}`);
      if (res.ok) {
        const data = await res.json();
        // บันทึกลงแคชเพื่อเปิดดูออฟไลน์ได้
        setCachedReceipt(orderId, data);
        return {
          isOffline: false,
          receipt: data,
        };
      }
    } catch (err) {
      // เมื่อเกิด network error (เช่น ออฟไลน์) ให้ข้ามไปอ่านจากแคช
    }
  }

  // Fallback: ดึงจาก Offline Cache
  const cached = getCachedReceipt(orderId);
  if (cached && cached.data) {
    return {
      isOffline: true,
      offlineNotice: `โหมดออฟไลน์: กำลังแสดงใบเสร็จดิจิทัลที่บันทึกไว้เมื่อ ${cached.cachedAt}`,
      receipt: cached.data,
    };
  }

  throw new Error("ไม่สามารถเปิดใบเสร็จได้ขณะออฟไลน์เนื่องจากไม่มีข้อมูลที่บันทึกไว้");
}

