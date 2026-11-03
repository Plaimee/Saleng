/**
 * Notification & Help Center API Client & Offline Cache Module
 * รองรับ UC-08, UC-13, REQ-OP-001, CC-01, CC-05, REQ-SEC-002, AC-S08-01..05
 */

const GUIDES_CACHE_KEY = "saleng_sorting_guides_cache";
const FAQS_CACHE_KEY = "saleng_faqs_cache";

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
 * ดึงคู่มือจากแคช (CC-05, REQ-OP-001)
 */
export function getCachedGuides() {
  try {
    const storage = getStorage();
    const raw = storage.getItem(GUIDES_CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

/**
 * บันทึกคู่มือลงแคช
 */
export function setCachedGuides(data) {
  try {
    const storage = getStorage();
    storage.setItem(GUIDES_CACHE_KEY, JSON.stringify({ data, cachedAt: new Date().toISOString() }));
  } catch (e) {
    // ignore
  }
}

/**
 * ดึง FAQ จากแคช
 */
export function getCachedFaqs() {
  try {
    const storage = getStorage();
    const raw = storage.getItem(FAQS_CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

/**
 * บันทึก FAQ ลงแคช
 */
export function setCachedFaqs(data) {
  try {
    const storage = getStorage();
    storage.setItem(FAQS_CACHE_KEY, JSON.stringify({ data, cachedAt: new Date().toISOString() }));
  } catch (e) {
    // ignore
  }
}

/**
 * ดึงรายการแจ้งเตือนทั้งหมดของผู้ขาย (AC-S08-01, UC-08, Q-01)
 */
export async function fetchNotifications(sellerId) {
  const url = `${API_BASE_URL}/api/v1/sellers/${sellerId}/notifications`;
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`ไม่สามารถโหลดการแจ้งเตือนได้ (HTTP ${resp.status})`);
  }
  return await resp.json();
}

/**
 * ทำเครื่องหมายแจ้งเตือนว่าอ่านแล้ว (AC-S08-01)
 */
export async function markNotificationAsRead(notificationId) {
  const url = `${API_BASE_URL}/api/v1/notifications/${notificationId}/read`;
  const resp = await fetch(url, { method: "PATCH" });
  if (!resp.ok) {
    throw new Error(`ไม่สามารถทำเครื่องหมายว่าอ่านแล้วได้ (HTTP ${resp.status})`);
  }
  return await resp.json();
}

/**
 * ทำเครื่องหมายแจ้งเตือนทั้งหมดว่าอ่านแล้ว (AC-S08-01)
 */
export async function markAllNotificationsAsRead(sellerId) {
  const url = `${API_BASE_URL}/api/v1/sellers/${sellerId}/notifications/mark-all-read`;
  const resp = await fetch(url, { method: "POST" });
  if (!resp.ok) {
    throw new Error(`ไม่สามารถล้างการแจ้งเตือนได้ (HTTP ${resp.status})`);
  }
  return await resp.json();
}

/**
 * ดึงคู่มือแนะนำการคัดแยกขยะ 4 หมวดหลัก พร้อมระบบ Offline Fallback (AC-S08-02, CC-05)
 */
export async function fetchSortingGuides() {
  const url = `${API_BASE_URL}/api/v1/help/sorting-guides`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP Error: ${resp.status}`);
    const data = await resp.json();
    setCachedGuides(data);
    return { ...data, is_offline_cached: false };
  } catch (err) {
    const cached = getCachedGuides();
    if (cached && cached.data) {
      return { ...cached.data, is_offline_cached: true, cached_at: cached.cachedAt };
    }
    throw err;
  }
}

/**
 * ดึงคำถามที่พบบ่อย (FAQ) พร้อมค้นหาและ Offline Fallback (AC-S08-03, CC-05)
 */
export async function fetchFaqs(query = "") {
  const queryParam = query ? `?query=${encodeURIComponent(query)}` : "";
  const url = `${API_BASE_URL}/api/v1/help/faqs${queryParam}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP Error: ${resp.status}`);
    const data = await resp.json();
    if (!query) {
      setCachedFaqs(data);
    }
    return { ...data, is_offline_cached: false };
  } catch (err) {
    const cached = getCachedFaqs();
    if (cached && cached.data) {
      let filtered = cached.data.categories || [];
      if (query) {
        const q = query.trim().toLowerCase();
        filtered = filtered
          .map((cat) => ({
            ...cat,
            faqs: cat.faqs.filter(
              (f) =>
                f.question.toLowerCase().includes(q) ||
                f.answer.toLowerCase().includes(q)
            ),
          }))
          .filter((cat) => cat.faqs.length > 0);
      }
      return {
        categories: filtered,
        total_faqs: filtered.reduce((acc, c) => acc + c.faqs.length, 0),
        is_offline_cached: true,
      };
    }
    throw err;
  }
}

/**
 * ส่งคำร้องขอความช่วยเหลือ (Support Ticket - AC-S08-04, UC-13, REQ-SEC-002)
 */
export async function submitSupportTicket(
  sellerId,
  { category, subject, description, contactPhone }
) {
  const url = `${API_BASE_URL}/api/v1/sellers/${sellerId}/support-tickets`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      category,
      subject,
      description,
      contact_phone: contactPhone,
    }),
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    const err = new Error(errorData.detail || "ไม่สามารถส่งคำร้องขอความช่วยเหลือได้");
    err.status = resp.status;
    throw err;
  }

  return await resp.json();
}

/**
 * ดึงข้อมูลติดต่อสายด่วน Call Center และ LINE Official (AC-S08-04)
 */
export async function fetchContactInfo() {
  const url = `${API_BASE_URL}/api/v1/help/contact-info`;
  const resp = await fetch(url);
  if (!resp.ok) {
    return {
      call_center_phone: "02-123-4567",
      operating_hours: "ทุกวัน 08:00 - 18:00 น.",
      line_official: "@saleng-help",
    };
  }
  return await resp.json();
}

