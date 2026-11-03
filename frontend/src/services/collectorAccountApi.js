/**
 * Frontend API Client สำหรับระบบบัญชีและการยืนยันตัวตนซาเล้ง (Buyer Account & KYC)
 * รองรับ UC-01, CC-01, CC-05, REQ-OP-001, REQ-SEC-002, D-00-01, AC-B01-01..05
 */

const API_BASE = '/api/v1/collectors';

export const collectorAccountApi = {
  /**
   * ขอรับรหัส OTP 6 หลักสำหรับซาเล้ง (AC-B01-01)
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
   * ยืนยันรหัส OTP และบันทึก Session ลงใน LocalStorage (AC-B01-01, CC-05, REQ-OP-001)
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
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_collector_session', data.session_token);
      localStorage.setItem(
        'saleng_collector_profile',
        JSON.stringify({
          saleng_id: data.saleng_id,
          display_name: data.display_name,
          phone_masked: data.phone_masked,
          verified: data.verified,
          kyc_status: data.kyc_status,
          vehicle_type: data.vehicle_type,
          max_capacity_kg: data.max_capacity_kg,
        })
      );
    }
    return data;
  },

  /**
   * ดึงข้อมูลเซสชันและโปรไฟล์ที่แคชไว้ในเครื่อง (CC-05, REQ-OP-001)
   */
  getStoredSession() {
    if (typeof window === 'undefined' || !window.localStorage) return null;
    const token = localStorage.getItem('saleng_collector_session');
    const profileStr = localStorage.getItem('saleng_collector_profile');
    if (!token || !profileStr) return null;
    try {
      const profile = JSON.parse(profileStr);
      return { token, ...profile };
    } catch (e) {
      return null;
    }
  },

  /**
   * ออกจากระบบและล้างเซสชัน (AC-B01-01)
   */
  async logout() {
    const token = typeof window !== 'undefined' && window.localStorage
      ? localStorage.getItem('saleng_collector_session')
      : null;

    try {
      if (token) {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } finally {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.removeItem('saleng_collector_session');
        localStorage.removeItem('saleng_collector_profile');
      }
    }
    return { success: true };
  },

  /**
   * ดึงข้อมูลโปรไฟล์ของซาเล้ง พร้อม Offline Fallback (AC-B01-01..04, REQ-OP-001)
   */
  async getProfile(salengId) {
    try {
      const res = await fetch(`${API_BASE}/${salengId}/profile`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'ดึงข้อมูลโปรไฟล์ไม่สำเร็จ');
      }
      const data = await res.json();
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('saleng_collector_profile', JSON.stringify(data));
      }
      return data;
    } catch (err) {
      // Offline fallback
      if (typeof window !== 'undefined' && window.localStorage) {
        const cached = localStorage.getItem('saleng_collector_profile');
        if (cached) {
          try {
            return JSON.parse(cached);
          } catch (e) {}
        }
      }
      throw err;
    }
  },

  /**
   * อัปเดตชื่อโปรไฟล์ซาเล้ง (P-01)
   */
  async updateProfile(salengId, displayName) {
    const res = await fetch(`${API_BASE}/${salengId}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ display_name: displayName }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'อัปเดตโปรไฟล์ไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_collector_profile', JSON.stringify(data));
    }
    return data;
  },

  /**
   * อัปเดตประเภทยานพาหนะและความจุ (AC-B01-02, REQ-FN-001, BR-03)
   */
  async updateVehicle(salengId, { vehicle_type, license_plate, max_capacity_kg }) {
    const res = await fetch(`${API_BASE}/${salengId}/vehicle`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        vehicle_type,
        license_plate: license_plate || null,
        max_capacity_kg: parseFloat(max_capacity_kg),
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'อัปเดตข้อมูลยานพาหนะไม่สำเร็จ');
    }
    const data = await res.json();
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('saleng_collector_profile', JSON.stringify(data));
    }
    return data;
  },

  /**
   * ส่งเอกสารยืนยันตัวตน KYC (AC-B01-03, SC-04, Q-02)
   */
  async submitKyc(salengId, kycData) {
    const res = await fetch(`${API_BASE}/${salengId}/kyc/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(kycData),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ส่งเอกสาร KYC ไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * ตรวจสอบสถานะการยืนยันตัวตน KYC (AC-B01-03)
   */
  async getKycStatus(salengId) {
    const res = await fetch(`${API_BASE}/${salengId}/kyc/status`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ตรวจสอบสถานะ KYC ไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * ตรวจสอบสิทธิ์การกดรับงานตามกฎ Unverified Gate (AC-B01-04, D-00-01)
   */
  async checkJobClaimGate(salengId) {
    const res = await fetch(`${API_BASE}/${salengId}/job-claim-gate`);
    if (res.status === 403) {
      const err = await res.json().catch(() => ({}));
      return {
        can_claim_job: false,
        error_detail: err.detail || 'ซาเล้งต้องผ่านการยืนยันตัวตนก่อนรับงานตามกฎ D-00-01',
      };
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'ตรวจสอบสิทธิ์รับงานไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * จำลองการอนุมัติ KYC (Q-06, P-06)
   */
  async mockApproveKyc(salengId) {
    const res = await fetch(`${API_BASE}/${salengId}/mock-kyc-approval`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'จำลองการอนุมัติไม่สำเร็จ');
    }
    return await res.json();
  },

  /**
   * จำลองการปฏิเสธ KYC (Q-06, P-06)
   */
  async mockRejectKyc(salengId, reason) {
    const res = await fetch(`${API_BASE}/${salengId}/mock-kyc-rejection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rejection_reason: reason }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'จำลองการปฏิเสธไม่สำเร็จ');
    }
    return await res.json();
  },
};

