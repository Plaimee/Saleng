/**
 * Frontend API Client สำหรับระบบนัดหมายและติดตามสถานะ (Booking & Status Tracking API)
 * รองรับ UC-04, CC-01, CC-05, REQ-OP-001, BR-03, MD-STM-04, AC-S05-01..05
 */

const API_BASE = '/api/v1/booking-tracking';

export const bookingTrackingApi = {
  /**
   * เลือกช่วงเวลานัดหมายและยืนยันส่งคำขอ (AC-S05-01)
   */
  async bookSlot(orderId, bookingData, sellerId = 'seller-01') {
    const res = await fetch(`${API_BASE}/orders/${orderId}/book?seller_id=${sellerId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookingData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ส่งคำขอนัดหมายไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_active_order_tracking', JSON.stringify(data));
    }
    return data;
  },

  /**
   * ดึงสถานะความคืบหน้าคำขอ Stepper Timeline และ ETA (AC-S05-02, AC-S05-04)
   */
  async getStatus(orderId, sellerId = 'seller-01') {
    try {
      const res = await fetch(`${API_BASE}/orders/${orderId}/status?seller_id=${sellerId}`);
      if (res.ok) {
        const data = await res.json();
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem('saleng_active_order_tracking', JSON.stringify(data));
        }
        return data;
      }
    } catch (e) {
      // Offline fallback
    }

    if (typeof window !== 'undefined' && window.localStorage) {
      const cached = localStorage.getItem('saleng_active_order_tracking');
      if (cached) {
        return { ...JSON.parse(cached), is_offline: true };
      }
    }
    throw new Error('ไม่สามารถดึงข้อมูลสถานะคำขอได้');
  },

  /**
   * ยกเลิกนัดหมายของผู้ขายตามกฎ BR-03 (AC-S05-03)
   */
  async cancelOrder(orderId, reason, sellerId = 'seller-01') {
    const res = await fetch(`${API_BASE}/orders/${orderId}/cancel?seller_id=${sellerId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ยกเลิกคำขอไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_active_order_tracking', JSON.stringify(data));
    }
    return data;
  },

  /**
   * จำลองการเปลี่ยนสถานะสำหรับทดสอบ (S2 -> S3 -> S4 -> S5)
   */
  async simulateStatus(orderId, targetStatus, salengId = 'saleng-01', sellerId = 'seller-01') {
    const res = await fetch(`${API_BASE}/orders/${orderId}/simulate-status?seller_id=${sellerId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_status: targetStatus, saleng_id: salengId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'จำลองสถานะไม่สำเร็จ');
    }
    return res.json();
  },
};

