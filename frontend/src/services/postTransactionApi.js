/**
 * Post-Transaction API Client & Offline Cache Module
 * รองรับ UC-10, SC-05, REQ-FN-005, REQ-SEC-002, CC-01, CC-05, REQ-OP-001, AC-S07-01..05
 */

const HISTORY_CACHE_KEY_PREFIX = "saleng_sales_history_";
const RECEIPT_CACHE_KEY_PREFIX = "saleng_receipt_cache_";

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
 * ดึงประวัติการขายที่แคชไว้ใน Local Storage (CC-05, REQ-OP-001)
 */
export function getCachedSalesHistory(sellerId) {
  try {
    const storage = getStorage();
    const raw = storage.getItem(`${HISTORY_CACHE_KEY_PREFIX}${sellerId}`);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

/**
 * บันทึกประวัติการขายลง Local Storage Cache (CC-05)
 */
export function setCachedSalesHistory(sellerId, data) {
  try {
    const storage = getStorage();
    const payload = {
      data,
      cachedAt: new Date().toISOString(),
    };
    storage.setItem(`${HISTORY_CACHE_KEY_PREFIX}${sellerId}`, JSON.stringify(payload));
  } catch (e) {
    // ignore storage quota errors
  }
}

/**
 * ดึงใบเสร็จดิจิทัลจาก Local Storage Cache
 */
export function getCachedReceipt(orderId) {
  try {
    const storage = getStorage();
    const raw = storage.getItem(`${RECEIPT_CACHE_KEY_PREFIX}${orderId}`);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed.data || parsed;
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
  } catch (e) {
    // ignore
  }
}

/**
 * ส่งคะแนนและรีวิวซาเล้ง (AC-S07-01, UC-10, Q-01, Q-02)
 */
export async function submitReview(orderId, { sellerId, rating, comment = null }) {
  const url = `${API_BASE_URL}/api/v1/orders/${orderId}/review`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      seller_id: sellerId,
      rating: Number(rating),
      comment: comment || null,
    }),
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    const err = new Error(errorData.detail || "ไม่สามารถส่งรีวิวได้");
    err.status = resp.status;
    err.data = errorData;
    throw err;
  }

  return await resp.json();
}

/**
 * ดึงข้อมูลรีวิวของคำขอ (AC-S07-01)
 */
export async function getReview(orderId) {
  const url = `${API_BASE_URL}/api/v1/orders/${orderId}/review`;
  const resp = await fetch(url);
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    const err = new Error(errorData.detail || "ไม่พบรีวิว");
    err.status = resp.status;
    throw err;
  }
  return await resp.json();
}

/**
 * บันทึกหรือยกเลิกซาเล้งเป็นผู้รับซื้อประจำ (Toggle Bookmark) (AC-S07-02, UC-10, Q-03)
 */
export async function toggleFavorite(sellerId, collectorId) {
  const url = `${API_BASE_URL}/api/v1/sellers/${sellerId}/favorites/${collectorId}`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    const err = new Error(errorData.detail || "ไม่สามารถจัดการผู้รับซื้อประจำได้");
    err.status = resp.status;
    throw err;
  }

  return await resp.json();
}

/**
 * ดึงรายการผู้รับซื้อประจำของผู้ขาย (AC-S07-02)
 */
export async function getFavorites(sellerId) {
  const url = `${API_BASE_URL}/api/v1/sellers/${sellerId}/favorites`;
  const resp = await fetch(url);
  if (!resp.ok) {
    return [];
  }
  return await resp.json();
}

/**
 * ดึงประวัติการขายที่ปิดงานสำเร็จทั้งหมดของผู้ขาย (AC-S07-03, REQ-FN-005, REQ-SEC-002, CC-05)
 */
export async function fetchSalesHistory(sellerId) {
  const url = `${API_BASE_URL}/api/v1/sellers/${sellerId}/sales-history`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`HTTP Error: ${resp.status}`);
    }
    const data = await resp.json();
    setCachedSalesHistory(sellerId, data);
    return { ...data, is_offline_cached: false };
  } catch (err) {
    // Offline Fallback (CC-05, REQ-OP-001)
    const cached = getCachedSalesHistory(sellerId);
    if (cached && cached.data) {
      return {
        ...cached.data,
        is_offline_cached: true,
        cached_at: cached.cachedAt,
      };
    }
    throw err;
  }
}

/**
 * ดึงข้อมูลใบเสร็จดิจิทัล พร้อมระบบ Offline Fallback (AC-S07-04, REQ-FN-005, CC-05)
 */
export async function fetchReceipt(orderId) {
  const url = `${API_BASE_URL}/api/v1/receipts/${orderId}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`HTTP Error: ${resp.status}`);
    }
    const data = await resp.json();
    setCachedReceipt(orderId, data);
    return { ...data, is_offline_cached: false };
  } catch (err) {
    // Offline Fallback (CC-05, REQ-OP-001)
    const cached = getCachedReceipt(orderId);
    if (cached) {
      return { ...cached, is_offline_cached: true };
    }
    throw err;
  }
}

