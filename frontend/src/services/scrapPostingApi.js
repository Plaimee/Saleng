/**
 * Frontend API Client สำหรับระบบโพสต์ขายของเก่าของผู้ขาย (Scrap Posting API)
 * รองรับ UC-02, CC-01, CC-05, REQ-OP-001, REQ-UX-002, Card 03, AC-S02-01..05
 */

const API_BASE = '/api/v1/scrap-posting';

export const scrapPostingApi = {
  /**
   * ดึงรายการหมวดหมู่และคู่มือภาพทั้งหมด (AC-S02-01)
   */
  async getCategories() {
    try {
      const res = await fetch(`${API_BASE}/categories`);
      if (res.ok) {
        const data = await res.json();
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem('saleng_scrap_categories', JSON.stringify(data.categories || []));
        }
        return data;
      }
    } catch (e) {
      // Offline fallback
    }

    if (typeof window !== 'undefined' && window.localStorage) {
      const cached = localStorage.getItem('saleng_scrap_categories');
      if (cached) {
        return { categories: JSON.parse(cached), is_offline: true };
      }
    }
    return { categories: [] };
  },

  /**
   * สร้างคำขอโพสต์ขายของเก่าฉบับร่าง S1 Draft (P-06)
   */
  async createDraft(sellerId, pickupLocationId = null) {
    const res = await fetch(`${API_BASE}/drafts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        seller_id: sellerId,
        pickup_location_id: pickupLocationId,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'สร้างคำขอฉบับร่างไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_draft_order', JSON.stringify(data));
    }
    return data;
  },

  /**
   * ดึงข้อมูลคำขอฉบับร่าง พร้อม Offline Fallback (CC-05, REQ-OP-001)
   */
  async getDraft(orderId) {
    try {
      const res = await fetch(`${API_BASE}/drafts/${orderId}`);
      if (res.ok) {
        const data = await res.json();
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem('saleng_draft_order', JSON.stringify(data));
        }
        return data;
      }
    } catch (e) {
      // Offline fallback
    }

    if (typeof window !== 'undefined' && window.localStorage) {
      const cached = localStorage.getItem('saleng_draft_order');
      if (cached) {
        const draft = JSON.parse(cached);
        if (draft.order_id === orderId) {
          return { ...draft, is_offline: true };
        }
      }
    }
    throw new Error('ไม่พบข้อมูลคำขอฉบับร่าง');
  },

  /**
   * เพิ่มรายการของเก่าลงในฉบับร่าง พร้อม Guard ของชิ้นใหญ่ (AC-S02-01..03, Card 03)
   */
  async addItem(orderId, itemData) {
    const res = await fetch(`${API_BASE}/drafts/${orderId}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(itemData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'เพิ่มรายการของเก่าไม่สำเร็จ');
    }
    const item = await res.json();
    await this.getDraft(orderId);
    return item;
  },

  /**
   * ลบรายการของเก่าออกจากฉบับร่าง
   */
  async deleteItem(orderId, itemId) {
    const res = await fetch(`${API_BASE}/drafts/${orderId}/items/${itemId}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ลบรายการของเก่าไม่สำเร็จ');
    }
    const result = await res.json();
    await this.getDraft(orderId);
    return result;
  },

  /**
   * แนบรูปถ่ายของเก่าประกอบรายการ (AC-S02-04, P-04)
   */
  async attachPhoto(orderId, itemId, photoUrl) {
    const res = await fetch(`${API_BASE}/drafts/${orderId}/items/${itemId}/photos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ photo_url: photoUrl }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'แนบรูปถ่ายไม่สำเร็จ');
    }
    const item = await res.json();
    await this.getDraft(orderId);
    return item;
  },

  /**
   * ลบรูปถ่ายของเก่าออกจากรายการ (AC-S02-04)
   */
  async deletePhoto(orderId, itemId, photoIdx) {
    const res = await fetch(`${API_BASE}/drafts/${orderId}/items/${itemId}/photos/${photoIdx}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ลบรูปถ่ายไม่สำเร็จ');
    }
    const item = await res.json();
    await this.getDraft(orderId);
    return item;
  },

  /**
   * ปรับปรุงตัวเลือกขอคนช่วยยกของหนักและหมายเหตุ (AC-S02-05, P-05)
   */
  async updateLiftingHelp(orderId, { needLiftingHelp, liftingHelpNotes }) {
    const res = await fetch(`${API_BASE}/drafts/${orderId}/lifting-help`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        need_lifting_help: needLiftingHelp,
        lifting_help_notes: liftingHelpNotes,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ปรับปรุงตัวเลือกขอคนช่วยยกไม่สำเร็จ');
    }
    const draft = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_draft_order', JSON.stringify(draft));
    }
    return draft;
  },
};

