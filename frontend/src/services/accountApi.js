/**
 * Frontend API Client สำหรับระบบบัญชีและการเข้าใช้งานของผู้ขาย (Seller Account & Access)
 * รองรับ UC-01, UC-02, CC-01, CC-05, REQ-OP-001, REQ-SEC-002, AC-S01-01..04
 */

const API_BASE = '/api/v1/sellers';

export const accountApi = {
  /**
   * ขอรับรหัส OTP 6 หลักสำหรับเบอร์โทรศัพท์ (AC-S01-01)
   */
  async requestOtp(phone) {
    const res = await fetch(`${API_BASE}/auth/request-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ขอรับรหัส OTP ไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * ยืนยันรหัส OTP และออก Session Token (AC-S01-01, AC-S01-04)
   */
  async verifyOtp(phone, otpCode) {
    const res = await fetch(`${API_BASE}/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, otp_code: otpCode }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ยืนยันรหัส OTP ไม่สำเร็จ');
    }
    const data = await res.json();
    // บันทึก Session ลงใน localStorage (CC-05, REQ-OP-001)
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_seller_token', data.session_token);
      localStorage.setItem(
        'saleng_seller_profile',
        JSON.stringify({
          seller_id: data.seller_id,
          phone_masked: data.phone_masked,
          display_name: data.display_name,
        })
      );
    }
    return data;
  },

  /**
   * ดึงข้อมูลเซสชันที่แคชไว้ในเครื่อง (CC-05)
   */
  getStoredSession() {
    if (typeof window === 'undefined' || !window.localStorage) return null;
    const token = localStorage.getItem('saleng_seller_token');
    const profileStr = localStorage.getItem('saleng_seller_profile');
    if (!token || !profileStr) return null;
    try {
      const profile = JSON.parse(profileStr);
      return { token, ...profile };
    } catch (e) {
      return null;
    }
  },

  /**
   * ออกจากระบบและล้างเซสชัน (AC-S01-05)
   */
  async logout() {
    const token = typeof window !== 'undefined' && window.localStorage
      ? localStorage.getItem('saleng_seller_token')
      : null;

    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
    } catch (e) {
      // แม้ API มีปัญหา ก็ล้างแคชในเครื่องออก
    } finally {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.removeItem('saleng_seller_token');
        localStorage.removeItem('saleng_seller_profile');
        localStorage.removeItem('saleng_seller_locations');
      }
    }
    return { success: true };
  },

  /**
   * ดึงข้อมูลโปรไฟล์ผู้ขาย (AC-S01-03)
   */
  async getProfile(sellerId) {
    const res = await fetch(`${API_BASE}/${sellerId}/profile`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ดึงข้อมูลโปรไฟล์ไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_seller_profile', JSON.stringify(data));
    }
    return data;
  },

  /**
   * แก้ไขชื่อที่แสดง (AC-S01-01)
   */
  async updateProfile(sellerId, displayName) {
    const res = await fetch(`${API_BASE}/${sellerId}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ display_name: displayName }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'แก้ไขโปรไฟล์ไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_seller_profile', JSON.stringify(data));
    }
    return data;
  },

  /**
   * ดึงรายการที่อยู่นัดหมาย พร้อม Offline Fallback (AC-S01-02, CC-05, REQ-OP-001)
   */
  async listLocations(sellerId) {
    try {
      const res = await fetch(`${API_BASE}/${sellerId}/locations`);
      if (res.ok) {
        const data = await res.json();
        if (typeof window !== 'undefined' && window.localStorage) {
          localStorage.setItem('saleng_seller_locations', JSON.stringify(data.locations || []));
        }
        return data;
      }
    } catch (e) {
      // ออฟไลน์: โหลดจากแคช
    }

    if (typeof window !== 'undefined' && window.localStorage) {
      const cached = localStorage.getItem('saleng_seller_locations');
      if (cached) {
        const locations = JSON.parse(cached);
        return {
          seller_id: sellerId,
          total_locations: locations.length,
          locations,
          is_offline: true,
        };
      }
    }

    return { seller_id: sellerId, total_locations: 0, locations: [] };
  },

  /**
   * เพิ่มที่อยู่นัดหมายใหม่ (AC-S01-02)
   */
  async createLocation(sellerId, locationData) {
    const res = await fetch(`${API_BASE}/${sellerId}/locations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locationData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'เพิ่มที่อยู่นัดหมายไม่สำเร็จ');
    }
    const created = await res.json();
    // อัปเดตแคช
    await this.listLocations(sellerId);
    return created;
  },

  /**
   * แก้ไขที่อยู่นัดหมาย (AC-S01-02)
   */
  async updateLocation(sellerId, locationId, updateData) {
    const res = await fetch(`${API_BASE}/${sellerId}/locations/${locationId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'แก้ไขที่อยู่นัดหมายไม่สำเร็จ');
    }
    const updated = await res.json();
    await this.listLocations(sellerId);
    return updated;
  },

  /**
   * ลบที่อยู่นัดหมาย (AC-S01-02)
   */
  async deleteLocation(sellerId, locationId) {
    const res = await fetch(`${API_BASE}/${sellerId}/locations/${locationId}`, {
      method: 'DELETE',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ลบที่อยู่นัดหมายไม่สำเร็จ');
    }
    const result = await res.json();
    await this.listLocations(sellerId);
    return result;
  },

  /**
   * ตั้งเป็นที่อยู่เริ่มต้น (AC-S01-02, Q-03)
   */
  async setDefaultLocation(sellerId, locationId) {
    const res = await fetch(`${API_BASE}/${sellerId}/locations/${locationId}/default`, {
      method: 'PATCH',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ตั้งค่าที่อยู่เริ่มต้นไม่สำเร็จ');
    }
    const updated = await res.json();
    await this.listLocations(sellerId);
    return updated;
  },

  /**
   * ดึงที่อยู่นัดหมายเริ่มต้น (P-06)
   */
  async getDefaultLocation(sellerId) {
    const res = await fetch(`${API_BASE}/${sellerId}/locations/default`);
    if (!res.ok) return null;
    return await res.json();
  },
};

