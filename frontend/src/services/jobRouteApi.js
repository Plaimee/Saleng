/**
 * Frontend API Client สำหรับระบบจัดการงานและเส้นทางของซาเล้ง (Job & Route Management API)
 * รองรับ UC-04, UC-09, UC-12, BR-02, BR-03, CC-01, CC-04, CC-05, REQ-OP-001, AC-B04-01..07, D-B04-01..06
 */

const API_BASE = '/api/v1/collectors';
const SCHEDULE_CACHE_PREFIX = 'saleng_active_schedule_cache_';
const OFFLINE_TRANSIT_QUEUE_KEY = 'saleng_offline_transit_queue';

export const jobRouteApi = {
  /**
   * กดรับงานแบบ Single Collector Atomic Claim (BR-02, CC-04, AC-B04-01)
   */
  async claimJob(orderId, { saleng_id = 'saleng-01', expected_version = 1 } = {}) {
    const res = await fetch(`${API_BASE}/jobs/${orderId}/claim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id,
        expected_version,
      }),
    });

    if (res.status === 409) {
      const err = await res.json().catch(() => ({}));
      const conflictError = new Error(err.detail || 'มีผู้รับงานนี้แล้ว');
      conflictError.status = 409;
      throw conflictError;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const error = new Error(err.detail || 'ไม่สามารถรับงานได้');
      error.status = res.status;
      throw error;
    }

    return await res.json();
  },

  /**
   * ข้ามงาน คงสถานะรอผู้รับงาน S2 (Extension A2, AC-B04-02)
   */
  async skipJob(orderId, { saleng_id = 'saleng-01' } = {}) {
    const res = await fetch(`${API_BASE}/jobs/${orderId}/skip?saleng_id=${encodeURIComponent(saleng_id)}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ข้ามงานไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * ดึงรายการคิวงานและตารางนัดหมายสะสม (BR-03, AC-B04-04, CC-05)
   */
  async getActiveQueue({ saleng_id = 'saleng-01', saleng_lat, saleng_lng } = {}) {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    if (!isOnline) {
      const cached = this.getCachedQueue(saleng_id);
      if (cached) {
        return {
          ...cached,
          is_offline_cached: true,
          message: 'แสดงข้อมูลตารางนัดหมายจากแคชในเครื่อง (โหมดออฟไลน์)',
        };
      }
    }

    const queryParams = new URLSearchParams();
    if (saleng_lat !== undefined && saleng_lat !== null) queryParams.append('saleng_lat', saleng_lat);
    if (saleng_lng !== undefined && saleng_lng !== null) queryParams.append('saleng_lng', saleng_lng);

    try {
      const url = `${API_BASE}/${saleng_id}/active-jobs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      const res = await fetch(url);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'ดึงรายการคิวงานไม่สำเร็จ');
      }
      const data = await res.json();

      // บันทึกลง LocalStorage Cache (CC-05, REQ-OP-001)
      if (typeof window !== 'undefined' && window.localStorage) {
        try {
          const cachePayload = {
            cached_at: new Date().toISOString(),
            data,
          };
          localStorage.setItem(`${SCHEDULE_CACHE_PREFIX}${saleng_id}`, JSON.stringify(cachePayload));
        } catch {
          // ละเว้นหาก LocalStorage เต็ม
        }
      }

      return data;
    } catch (err) {
      const cached = this.getCachedQueue(saleng_id);
      if (cached) {
        return {
          ...cached,
          is_offline_cached: true,
          message: 'แสดงข้อมูลตารางนัดหมายจากแคชในเครื่อง (โหมดออฟไลน์)',
        };
      }
      throw err;
    }
  },

  /**
   * ยืนยันออกเดินทาง S3 -> S4 และล็อกปุ่มยกเลิกผู้ขาย (UC-09, BR-03, AC-B04-05)
   */
  async startTransit(orderId, { saleng_id = 'saleng-01', current_lat, current_lng } = {}) {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    if (!isOnline) {
      // โหมดออฟไลน์: บันทึกลง Offline Transit Queue พร้อม idempotency_key (REQ-OP-001, CC-05)
      this.enqueueOfflineTransit({ orderId, saleng_id, current_lat, current_lng });
      return {
        order_id: orderId,
        status: 'S4',
        started_at: new Date().toISOString(),
        is_offline_queued: true,
        seller_cancel_locked: true,
        navigation_url: `https://www.google.com/maps/dir/?api=1&destination=${current_lat || 13.7950},${current_lng || 100.5810}`,
        message: 'บันทึกคำสั่งเริ่มออกเดินทางในคิวออฟไลน์แล้ว จะซิงก์อัตโนมัติเมื่อมีสัญญาณ',
      };
    }

    const res = await fetch(`${API_BASE}/jobs/${orderId}/start-transit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id,
        current_lat,
        current_lng,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'เริ่มออกเดินทางไม่สำเร็จ');
    }

    return await res.json();
  },

  /**
   * สละสิทธิ์/ยกเลิกงาน คืนสถานะคำขอกลับเป็น S2 (D-B04-04, AC-B04-06)
   */
  async cancelJob(orderId, { saleng_id = 'saleng-01', reason = 'VEHICLE_BREAKDOWN', note = '' } = {}) {
    const res = await fetch(`${API_BASE}/jobs/${orderId}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id,
        reason,
        note,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ยกเลิกงานไม่สำเร็จ');
    }

    return await res.json();
  },

  /**
   * อ่านข้อมูลแคชตารางงานจาก LocalStorage
   */
  getCachedQueue(saleng_id = 'saleng-01') {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    try {
      const raw = localStorage.getItem(`${SCHEDULE_CACHE_PREFIX}${saleng_id}`);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed.data || null;
    } catch {
      return null;
    }
  },

  /**
   * ล้างแคชตารางงาน
   */
  clearCachedQueue(saleng_id = 'saleng-01') {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(`${SCHEDULE_CACHE_PREFIX}${saleng_id}`);
    }
  },

  /**
   * เพิ่มคำสั่งออกเดินทางลงใน Offline Queue
   */
  enqueueOfflineTransit({ orderId, saleng_id, current_lat, current_lng }) {
    if (typeof window === 'undefined' || !window.localStorage) return;
    try {
      const existing = this.getOfflineTransitQueue();
      const payload = {
        orderId,
        saleng_id,
        current_lat,
        current_lng,
        idempotency_key: `transit_${orderId}_${Date.now()}`,
        enqueued_at: new Date().toISOString(),
      };
      existing.push(payload);
      localStorage.setItem(OFFLINE_TRANSIT_QUEUE_KEY, JSON.stringify(existing));
    } catch {
      // Ignored
    }
  },

  /**
   * ดึงรายการใน Offline Transit Queue
   */
  getOfflineTransitQueue() {
    if (typeof window === 'undefined' || !window.localStorage) return [];
    try {
      const raw = localStorage.getItem(OFFLINE_TRANSIT_QUEUE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  /**
   * ล้าง Offline Transit Queue
   */
  clearOfflineTransitQueue() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(OFFLINE_TRANSIT_QUEUE_KEY);
    }
  },
};

