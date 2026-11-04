/**
 * Frontend API Client สำหรับระบบประเมินงานและค่าน้ำมันก่อนรับ (Buyer Job Evaluation & Fuel Cost)
 * รองรับ UC-04, Card 02, CC-01, CC-03, CC-05, REQ-OP-001, REQ-CON-003, AC-B03-01..05
 */

const API_BASE = '/api/v1/collectors';
const CACHE_PREFIX = 'saleng_active_job_eval_cache_';

export const jobEvaluationApi = {
  /**
   * ดึงข้อมูลประเมินคำขอขาย คำนวณระยะทาง ค่าน้ำมัน และความจุรถ (Card 02, AC-B03-01)
   */
  async evaluateJob(orderId, { saleng_id = 'saleng-01', saleng_lat, saleng_lng, force_fallback = false } = {}) {
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    if (!isOnline) {
      return this.getCachedEvaluation(orderId);
    }

    const queryParams = new URLSearchParams();
    if (saleng_id) queryParams.append('saleng_id', saleng_id);
    if (saleng_lat !== undefined && saleng_lat !== null) queryParams.append('saleng_lat', saleng_lat);
    if (saleng_lng !== undefined && saleng_lng !== null) queryParams.append('saleng_lng', saleng_lng);
    if (force_fallback) queryParams.append('force_fallback', 'true');

    try {
      const res = await fetch(`${API_BASE}/jobs/${orderId}/evaluate?${queryParams.toString()}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'ประเมินคำขอขายไม่สำเร็จ');
      }
      const data = await res.json();

      // บันทึกลง LocalStorage Cache (CC-05, REQ-OP-001)
      if (typeof window !== 'undefined' && window.localStorage) {
        try {
          const cachePayload = {
            cached_at: new Date().toISOString(),
            data,
          };
          localStorage.setItem(`${CACHE_PREFIX}${orderId}`, JSON.stringify(cachePayload));
        } catch {
          // ละเว้นหาก LocalStorage เต็ม
        }
      }

      return data;
    } catch (err) {
      const cached = this.getCachedEvaluation(orderId);
      if (cached) {
        return {
          ...cached,
          is_offline_cached: true,
          message: 'แสดงผลการประเมินจากแคชออฟไลน์',
        };
      }
      throw err;
    }
  },

  /**
   * สลับสถานะ Online / Offline (CC-02, AC-B03-03)
   */
  async toggleOnlineStatus(salengId, isOnline, { current_lat, current_lng } = {}) {
    const res = await fetch(`${API_BASE}/${salengId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id: salengId,
        is_online: isOnline,
        current_lat,
        current_lng,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'สลับสถานะไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * ดึงข้อมูลความจุรถและน้ำหนักสะสมของซาเล้ง (BR-03, REQ-CON-003)
   */
  async getCollectorCapacity(salengId) {
    const res = await fetch(`${API_BASE}/${salengId}/capacity`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ดึงข้อมูลความจุรถไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * อ่านข้อมูลแคชล่าสุดจาก LocalStorage (CC-05, REQ-OP-001)
   */
  getCachedEvaluation(orderId) {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    try {
      const raw = localStorage.getItem(`${CACHE_PREFIX}${orderId}`);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed.data || null;
    } catch {
      return null;
    }
  },

  /**
   * ล้างแคชการประเมิน
   */
  clearCachedEvaluation(orderId) {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(`${CACHE_PREFIX}${orderId}`);
    }
  },
};

