/**
 * Transaction Safety & SOS API Client & Offline Cache Module
 * รองรับ UC-09, UC-13, REQ-SEC-001, REQ-SEC-002, REQ-QA-001, REQ-UX-001, REQ-FN-006, CC-01, CC-05, REQ-OP-001, AC-S09-01..05
 */

const EMERGENCY_CONTACT_CACHE_KEY = "saleng_emergency_contact_cache";
const SAFETY_EVIDENCE_CACHE_PREFIX = "saleng_safety_evidence_cache_";

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

// -----------------------------------------------------------------------------
// 1. Local Cache Functions (CC-05, REQ-OP-001)
// -----------------------------------------------------------------------------
export function getCachedEmergencyContact(sellerId) {
  try {
    const storage = getStorage();
    const raw = storage.getItem(`${EMERGENCY_CONTACT_CACHE_KEY}_${sellerId}`);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function setCachedEmergencyContact(sellerId, contactData) {
  try {
    const storage = getStorage();
    storage.setItem(
      `${EMERGENCY_CONTACT_CACHE_KEY}_${sellerId}`,
      JSON.stringify({ ...contactData, cachedAt: new Date().toISOString() })
    );
  } catch (e) {
    // ignore
  }
}

export function getCachedEvidences(orderId) {
  try {
    const storage = getStorage();
    const raw = storage.getItem(`${SAFETY_EVIDENCE_CACHE_PREFIX}${orderId}`);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

export function setCachedEvidences(orderId, evidences) {
  try {
    const storage = getStorage();
    storage.setItem(
      `${SAFETY_EVIDENCE_CACHE_PREFIX}${orderId}`,
      JSON.stringify(evidences)
    );
  } catch (e) {
    // ignore
  }
}

// -----------------------------------------------------------------------------
// 2. API Functions
// -----------------------------------------------------------------------------

/**
 * ดึงข้อมูลผู้ติดต่อฉุกเฉิน (AC-S09-03, REQ-SEC-002)
 */
export async function fetchEmergencyContact(sellerId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/sellers/${sellerId}/safety/emergency-contact`);
    if (!res.ok) throw new Error("Failed to fetch contact");
    const data = await res.json();
    setCachedEmergencyContact(sellerId, data);
    return data;
  } catch (err) {
    const cached = getCachedEmergencyContact(sellerId);
    if (cached) return cached;
    return {
      seller_id: sellerId,
      contact_name: "ศูนย์ช่วยเหลือและสายด่วน Saleng Hotline",
      relationship: "ศูนย์ดูแลระบบส่วนกลาง",
      contact_phone_masked: "02-123-4567",
      is_default: true,
      updated_at: new Date().toISOString(),
      offline: true,
    };
  }
}

/**
 * บันทึกหรือแก้ไขผู้ติดต่อฉุกเฉิน (AC-S09-03, P-03)
 */
export async function saveEmergencyContact(sellerId, { contact_name, relationship, contact_phone }) {
  const res = await fetch(`${API_BASE_URL}/api/v1/sellers/${sellerId}/safety/emergency-contact`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contact_name, relationship, contact_phone }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "บันทึกข้อมูลผู้ติดต่อฉุกเฉินไม่สำเร็จ");
  }
  const data = await res.json();
  setCachedEmergencyContact(sellerId, data);
  return data;
}

/**
 * ส่งสัญญาณฉุกเฉิน SOS One-Tap Trigger (AC-S09-02, REQ-QA-001, P-02)
 */
export async function triggerEmergencySos(orderId, sellerId, { current_lat, current_lng, notes } = {}) {
  const url = `${API_BASE_URL}/api/v1/orders/${orderId}/safety/sos?seller_id=${sellerId}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ current_lat, current_lng, notes }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "ส่งสัญญาณฉุกเฉินไม่สำเร็จ");
  }
  return await res.json();
}

/**
 * อัปโหลด/บันทึกไฟล์หลักฐานเสียงหรือวิดีโอ (AC-S09-01, P-01)
 */
export async function uploadSafetyEvidence(orderId, sellerId, { media_type, duration_seconds, file_size_bytes, file_url }) {
  const url = `${API_BASE_URL}/api/v1/orders/${orderId}/safety/evidence?seller_id=${sellerId}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ media_type, duration_seconds, file_size_bytes, file_url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "บันทึกหลักฐานไม่สำเร็จ");
  }
  const data = await res.json();
  const cachedList = getCachedEvidences(orderId);
  setCachedEvidences(orderId, [...cachedList, data]);
  return data;
}

/**
 * ดึงรายการหลักฐานของคำขอ (AC-S09-01, AC-S09-04)
 */
export async function fetchSafetyEvidences(orderId, sellerId) {
  try {
    const url = `${API_BASE_URL}/api/v1/orders/${orderId}/safety/evidence?seller_id=${sellerId}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch evidences");
    const data = await res.json();
    setCachedEvidences(orderId, data.evidences);
    return data;
  } catch (err) {
    const cached = getCachedEvidences(orderId);
    return {
      order_id: orderId,
      total_evidences: cached.length,
      evidences: cached,
      offline: true,
    };
  }
}

/**
 * สั่งล็อกหลักฐานเมื่อมีข้อพิพาท (AC-S09-04, P-04)
 */
export async function lockSafetyEvidences(orderId, actorId) {
  const url = `${API_BASE_URL}/api/v1/orders/${orderId}/safety/lock-evidence?actor_id=${actorId}`;
  const res = await fetch(url, {
    method: "PATCH",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "ล็อกหลักฐานไม่สำเร็จ");
  }
  const data = await res.json();
  // อัปเดตแคช
  const cached = getCachedEvidences(orderId);
  const updated = cached.map((e) => ({ ...e, is_locked: true }));
  setCachedEvidences(orderId, updated);
  return data;
}

