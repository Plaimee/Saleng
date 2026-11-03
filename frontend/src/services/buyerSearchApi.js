/**
 * Frontend API Client สำหรับระบบค้นหาและเลือกผู้รับซื้อ (Buyer Search & Selection API)
 * รองรับ UC-03, CC-01, CC-05, REQ-OP-001, REQ-UX-001, REQ-QA-001, AC-S03-01..05
 */

const API_BASE = '/api/v1/buyer-search';

export const buyerSearchApi = {
  /**
   * ค้นหารายชื่อซาเล้งในพื้นที่ พร้อมตัวกรองและระบบตรึงคนโปรด (AC-S03-01..03)
   */
  async searchCollectors({
    sellerId = 'seller-01',
    orderId = null,
    radiusKm = 5.0,
    vehicleType = null,
    minRating = null,
    category = null,
  } = {}) {
    const params = new URLSearchParams({ seller_id: sellerId, radius_km: radiusKm.toString() });
    if (orderId) params.append('order_id', orderId);
    if (vehicleType) params.append('vehicle_type', vehicleType);
    if (minRating) params.append('min_rating', minRating.toString());
    if (category) params.append('category', category);

    try {
      const res = await fetch(`${API_BASE}/collectors?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem('saleng_cached_collectors', JSON.stringify(data.collectors || []));
        }
        return data;
      }
    } catch (e) {
      // Offline fallback
    }

    if (typeof window !== 'undefined' && window.localStorage) {
      const cached = localStorage.getItem('saleng_cached_collectors');
      if (cached) {
        const parsed = JSON.parse(cached);
        return {
          collectors: parsed,
          total_count: parsed.length,
          has_bulky_items: false,
          is_offline: true,
        };
      }
    }
    return { collectors: [], total_count: 0, has_bulky_items: false, is_offline: true };
  },

  /**
   * ดึงข้อมูลโปรไฟล์ละเอียดของซาเล้ง (AC-S03-01)
   */
  async getCollectorProfile(salengId, sellerId = 'seller-01') {
    const res = await fetch(`${API_BASE}/collectors/${salengId}?seller_id=${sellerId}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ไม่สามารถดึงข้อมูลโปรไฟล์ผู้รับซื้อได้');
    }
    return res.json();
  },

  /**
   * ดึงรายชื่อซาเล้งที่เคยใช้บริการ (AC-S03-02)
   */
  async getFavorites(sellerId = 'seller-01') {
    try {
      const res = await fetch(`${API_BASE}/favorites?seller_id=${sellerId}`);
      if (res.ok) {
        return res.json();
      }
    } catch (e) {
      // Offline fallback
    }
    return [];
  },

  /**
   * สลับสถานะเปิด/ปิดบันทึกเป็นซาเล้งที่เคยใช้บริการ (AC-S03-02)
   */
  async toggleFavorite(salengId, sellerId = 'seller-01') {
    const res = await fetch(`${API_BASE}/favorites/${salengId}/toggle?seller_id=${sellerId}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ไม่สามารถสลับสถานะคนโปรดได้');
    }
    return res.json();
  },

  /**
   * ส่งคำขอนัดหมายเจาะจงบุคคล (Direct Request) และเปลี่ยนสถานะเป็น S2 (AC-S03-05)
   */
  async sendDirectRequest(orderId, salengId, sellerId = 'seller-01', notes = '') {
    const res = await fetch(`${API_BASE}/orders/${orderId}/direct-request?seller_id=${sellerId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        saleng_id: salengId,
        notes: notes,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ส่งคำขอนัดหมายไม่สำเร็จ');
    }
    return res.json();
  },
};

