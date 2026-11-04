/**
 * Frontend API Client สำหรับระบบคิดเงินและออกใบเสร็จ (Buyer Billing & Receipt)
 * รองรับ UC-05, UC-06, UC-07, REQ-FN-002, REQ-FN-004, REQ-FN-005, REQ-BR-002, REQ-SEC-002, CC-01, CC-05, CC-06, REQ-OP-001, D-B06-01..06
 */

const API_BASE = '/api/v1/collectors/billing';
const SHEET_CACHE_PREFIX = 'saleng_weighing_sheet_';
const RECEIPT_CACHE_PREFIX = 'saleng_receipt_';
export const OFFLINE_QUEUE_KEY = 'saleng_weighing_offline_queue';

export const billingReceiptApi = {
  /**
   * ดึงข้อมูลใบชั่งน้ำหนักหน้างานและราคาต่อหน่วยที่ล็อกไว้ (UC-05, REQ-FN-002, REQ-BR-002)
   */
  async getWeighingSheet(orderId, salengId = 'saleng-01') {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    // ถ้าออฟไลน์ ให้ดึงจากแคชใน localStorage
    if (!isOnline && typeof localStorage !== 'undefined') {
      const cached = localStorage.getItem(`${SHEET_CACHE_PREFIX}${orderId}`);
      if (cached) {
        try {
          return { ...JSON.parse(cached), from_cache: true, is_offline: true };
        } catch {
          // ignore corrupted json
        }
      }
    }

    try {
      const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/weighing-sheet?saleng_id=${encodeURIComponent(salengId)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const error = new Error(err.detail || 'ไม่สามารถดึงใบชั่งน้ำหนักได้');
        error.status = res.status;
        throw error;
      }

      const data = await res.json();
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(`${SHEET_CACHE_PREFIX}${orderId}`, JSON.stringify(data));
      }
      return { ...data, from_cache: false, is_offline: false };
    } catch (err) {
      if (typeof localStorage !== 'undefined') {
        const cached = localStorage.getItem(`${SHEET_CACHE_PREFIX}${orderId}`);
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
   * บันทึกผลชั่งจริงหน้างานโดยซาเล้ง พร้อมภาพถ่ายตาชั่ง (REQ-FN-002, D-B06-02, D-B06-03)
   * รองรับ Offline Queue เมื่อไม่มีสัญญาณเน็ตหน้างาน (CC-05, REQ-OP-001, D-B06-05)
   */
  async submitWeighing(orderId, { salengId = 'saleng-01', scalePhotoUrl, items, idempotencyKey } = {}) {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;
    const finalKey = idempotencyKey || `idemp-${orderId}-${Date.now()}`;

    const payload = {
      saleng_id: salengId,
      scale_photo_url: scalePhotoUrl,
      items: items || [],
      idempotency_key: finalKey,
    };

    if (!isOnline) {
      // จัดเก็บลง Offline Queue ใน localStorage
      this.enqueueOfflineWeighing(orderId, payload);
      return {
        status: 'queued',
        is_offline: true,
        order_id: orderId,
        idempotency_key: finalKey,
        message: 'บันทึกข้อมูลการชั่งลงคิวออฟไลน์แล้ว จะซิงก์เมื่อเชื่อมต่ออินเทอร์เน็ต',
      };
    }

    const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/weighing`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'บันทึกผลการชั่งน้ำหนักไม่สำเร็จ');
      error.status = res.status;
      throw error;
    }

    return await res.json();
  },

  /**
   * บันทึกรายการลงคิวออฟไลน์
   */
  enqueueOfflineWeighing(orderId, payload) {
    if (typeof localStorage === 'undefined') return;
    try {
      const currentQueue = JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]');
      currentQueue.push({
        order_id: orderId,
        payload,
        queued_at: new Date().toISOString(),
      });
      localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(currentQueue));
    } catch {
      // ignore storage error
    }
  },

  /**
   * ซิงก์ข้อมูลการชั่งน้ำหนักจาก Offline Queue ไปยังเซิร์ฟเวอร์ (REQ-OP-001)
   */
  async syncOfflineWeighingQueue() {
    if (typeof localStorage === 'undefined') return { syncedCount: 0, failedCount: 0 };
    let currentQueue = [];
    try {
      currentQueue = JSON.parse(localStorage.getItem(OFFLINE_QUEUE_KEY) || '[]');
    } catch {
      currentQueue = [];
    }

    if (currentQueue.length === 0) {
      return { syncedCount: 0, failedCount: 0 };
    }

    const remaining = [];
    let syncedCount = 0;
    let failedCount = 0;

    for (const item of currentQueue) {
      try {
        const res = await fetch(`${API_BASE}/${encodeURIComponent(item.order_id)}/weighing`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(item.payload),
        });
        if (res.ok) {
          syncedCount++;
        } else {
          remaining.push(item);
          failedCount++;
        }
      } catch {
        remaining.push(item);
        failedCount++;
      }
    }

    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(remaining));
    return { syncedCount, failedCount };
  },

  /**
   * เลือกช่องทางการชำระเงินหน้างาน (CASH หรือ PROMPTPAY) (D-B06-04)
   * 100% Confirmation Gate: เซิร์ฟเวอร์จะปฏิเสธ (403) หากผู้ขายยังไม่ยืนยันน้ำหนัก (REQ-FN-004, AC-B06-03)
   */
  async selectPaymentMethod(orderId, { salengId = 'saleng-01', paymentMethod } = {}) {
    const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/payment-method`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id: salengId,
        payment_method: paymentMethod,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'ไม่สามารถบันทึกช่องทางชำระเงินได้');
      error.status = res.status;
      throw error;
    }

    return await res.json();
  },

  /**
   * ดึงใบเสร็จสรุปรายการดิจิทัลเมื่อจบงาน (S7) พร้อม Mask เบอร์โทรศัพท์ (REQ-FN-005, REQ-SEC-002, CC-06)
   */
  async getReceipt(orderId, salengId = 'saleng-01') {
    try {
      const res = await fetch(`${API_BASE}/${encodeURIComponent(orderId)}/receipt?saleng_id=${encodeURIComponent(salengId)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const error = new Error(err.detail || 'ไม่สามารถดึงใบเสร็จดิจิทัลได้');
        error.status = res.status;
        throw error;
      }

      const data = await res.json();
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(`${RECEIPT_CACHE_PREFIX}${orderId}`, JSON.stringify(data));
      }
      return data;
    } catch (err) {
      if (typeof localStorage !== 'undefined') {
        const cached = localStorage.getItem(`${RECEIPT_CACHE_PREFIX}${orderId}`);
        if (cached) {
          try {
            return { ...JSON.parse(cached), from_cache: true };
          } catch {
            // ignore
          }
        }
      }
      throw err;
    }
  },
};

