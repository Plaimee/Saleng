/**
 * Frontend API Client สำหรับระบบค้นหาและแสดงงานรับซื้อตามพิกัด (Buyer Job Search & Map)
 * รองรับ UC-04, CC-01, CC-03, CC-05, REQ-OP-001, REQ-SEC-002, D-00-02, AC-B02-01..05
 */

const API_BASE = '/api/v1/collectors/jobs';
const CACHE_KEY = 'saleng_active_job_search_cache';

export const jobSearchApi = {
  /**
   * ค้นหาคำขอขายใกล้เคียงในรัศมี 5.0 หรือ 10.0 กม. พร้อม Offline Cache (CC-05, REQ-OP-001)
   */
  async getNearbyJobs({
    saleng_lat,
    saleng_lng,
    radius_km = 5.0,
    category,
    weight_range = 'ALL',
    sort_by = 'DISTANCE',
    force_fallback = false,
  } = {}) {
    // ตรวจสอบสถานะ Online/Offline
    const isOnline = typeof navigator !== 'undefined' ? (navigator.onLine !== false) : true;

    if (!isOnline) {
      return this.getCachedJobs();
    }

    const queryParams = new URLSearchParams();
    if (saleng_lat !== undefined && saleng_lat !== null) queryParams.append('saleng_lat', saleng_lat);
    if (saleng_lng !== undefined && saleng_lng !== null) queryParams.append('saleng_lng', saleng_lng);
    if (radius_km) queryParams.append('radius_km', radius_km);
    if (category) queryParams.append('category', category);
    if (weight_range) queryParams.append('weight_range', weight_range);
    if (sort_by) queryParams.append('sort_by', sort_by);
    if (force_fallback) queryParams.append('force_fallback', 'true');

    try {
      const res = await fetch(`${API_BASE}/nearby?${queryParams.toString()}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'ค้นหาคำขอขายใกล้เคียงไม่สำเร็จ');
      }
      const data = await res.json();

      // บันทึกลง LocalStorage Cache (CC-05, REQ-OP-001)
      if (typeof window !== 'undefined' && window.localStorage) {
        try {
          const cachePayload = {
            cached_at: new Date().toISOString(),
            data,
          };
          localStorage.setItem(CACHE_KEY, JSON.stringify(cachePayload));
        } catch {
          // ละเว้นหาก LocalStorage เต็ม
        }
      }

      return data;
    } catch (err) {
      // เมื่อเกิดข้อผิดพลาดในการเชื่อมต่อเครือข่าย พยายามอ่านข้อมูลแคชล่าสุด
      const cached = this.getCachedJobs();
      if (cached && cached.jobs && cached.jobs.length > 0) {
        return {
          ...cached,
          is_offline_cached: true,
          message: 'แสดงข้อมูลงานล่าสุดจากแคชออฟไลน์',
        };
      }
      throw err;
    }
  },

  /**
   * ดึงข้อมูลสรุปของคำขอขายก่อนรับงาน (AC-B02-03)
   */
  async getJobSummary(orderId, { saleng_lat, saleng_lng, force_fallback = false } = {}) {
    const queryParams = new URLSearchParams();
    if (saleng_lat !== undefined && saleng_lat !== null) queryParams.append('saleng_lat', saleng_lat);
    if (saleng_lng !== undefined && saleng_lng !== null) queryParams.append('saleng_lng', saleng_lng);
    if (force_fallback) queryParams.append('force_fallback', 'true');

    const qs = queryParams.toString() ? `?${queryParams.toString()}` : '';
    const res = await fetch(`${API_BASE}/${orderId}/summary${qs}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ดึงข้อมูลคำขอขายไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * จำลองคำขอขายใหม่สถานะ S2 เพื่อทดสอบ Polling & Live Alert (Q-02)
   */
  async simulateNewOrder(payload) {
    const res = await fetch(`${API_BASE}/simulate-new-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'จำลองคำขอขายไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * อ่านข้อมูลแคชล่าสุดจาก LocalStorage (CC-05, REQ-OP-001)
   */
  getCachedJobs() {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed.data || null;
    } catch {
      return null;
    }
  },

  /**
   * ล้างแคชการค้นหางาน
   */
  clearCachedJobs() {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem(CACHE_KEY);
    }
  },
};

