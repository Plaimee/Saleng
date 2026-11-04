/**
 * Frontend API Client สำหรับระบบหลังจบงานซาเล้ง (Buyer Post-Job Management)
 * รองรับ UC-10, UC-13, REQ-FN-005, REQ-FN-006, REQ-SEC-001, REQ-SEC-002, CC-01, CC-05, REQ-OP-001, D-B07-01..06
 */

const API_BASE = '/api/v1/collectors/post-job';
const HISTORY_CACHE_KEY = 'saleng_purchase_history_cache';
const REGULAR_CUSTOMERS_CACHE_KEY = 'saleng_regular_customers_cache';

export const postJobApi = {
  /**
   * ดึงประวัติการรับซื้อของเก่าที่เสร็จสิ้นแล้ว (S7) พร้อมสรุปสถิติสะสม (UC-10, REQ-FN-005, D-B07-05)
   */
  async getPurchaseHistory(salengId = 'saleng-01', period = 'all') {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    // ถ้าออฟไลน์ ให้ดึงจากแคชใน localStorage
    if (!isOnline && typeof localStorage !== 'undefined') {
      const cached = localStorage.getItem(`${HISTORY_CACHE_KEY}_${period}`);
      if (cached) {
        try {
          return { ...JSON.parse(cached), from_cache: true, is_offline: true };
        } catch {
          // ignore
        }
      }
    }

    try {
      const res = await fetch(
        `${API_BASE}/history?saleng_id=${encodeURIComponent(salengId)}&period=${encodeURIComponent(period)}`
      );
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const error = new Error(err.detail || 'ไม่สามารถดึงประวัติการรับซื้อได้');
        error.status = res.status;
        throw error;
      }

      const data = await res.json();
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(`${HISTORY_CACHE_KEY}_${period}`, JSON.stringify(data));
      }
      return { ...data, from_cache: false, is_offline: false };
    } catch (err) {
      if (typeof localStorage !== 'undefined') {
        const cached = localStorage.getItem(`${HISTORY_CACHE_KEY}_${period}`);
        if (cached) {
          try {
            return { ...JSON.parse(cached), from_cache: true, is_offline: true };
          } catch {
            // ignore
          }
        }
      }
      throw err;
    }
  },

  /**
   * ดึงรายชื่อลูกค้าประจำที่ซาเล้งปักหมุดไว้ (UC-10, AC-B07-02, D-B07-03)
   */
  async getRegularCustomers(salengId = 'saleng-01') {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    if (!isOnline && typeof localStorage !== 'undefined') {
      const cached = localStorage.getItem(REGULAR_CUSTOMERS_CACHE_KEY);
      if (cached) {
        try {
          return JSON.parse(cached);
        } catch {
          // ignore
        }
      }
    }

    try {
      const res = await fetch(`${API_BASE}/regular-customers?saleng_id=${encodeURIComponent(salengId)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const error = new Error(err.detail || 'ไม่สามารถดึงรายชื่อลูกค้าประจำได้');
        error.status = res.status;
        throw error;
      }

      const data = await res.json();
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(REGULAR_CUSTOMERS_CACHE_KEY, JSON.stringify(data));
      }
      return data;
    } catch (err) {
      if (typeof localStorage !== 'undefined') {
        const cached = localStorage.getItem(REGULAR_CUSTOMERS_CACHE_KEY);
        if (cached) {
          try {
            return JSON.parse(cached);
          } catch {
            // ignore
          }
        }
      }
      throw err;
    }
  },

  /**
   * สลับสถานะปักหมุดหรือยกเลิกผู้ขายเป็นลูกค้าประจำ (AC-B07-02)
   */
  async toggleRegularCustomer(salengId = 'saleng-01', payload = {}) {
    const res = await fetch(`${API_BASE}/regular-customers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id: salengId,
        ...payload,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'ไม่สามารถบันทึกลูกค้าประจำได้');
      error.status = res.status;
      throw error;
    }

    return await res.json();
  },

  /**
   * รายงานข้อพิพาทหน้างานกรณี No-show หรือของไม่ตรงสเปก (S3/S4 -> S8)
   * รองรับ UC-13, REQ-FN-006, AC-B07-03, D-B07-01, D-B07-02
   */
  async reportSellerMismatch(payload = {}) {
    const res = await fetch(`${API_BASE}/report-mismatch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'ไม่สามารถส่งรายงานข้อพิพาทได้');
      error.status = res.status;
      throw error;
    }

    return await res.json();
  },
};

