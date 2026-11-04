/**
 * Frontend API Client สำหรับศูนย์ควบคุมการจับคู่งานและข้อพิพาท (Admin Feature 03)
 * รองรับ UC-13, AC-A03-01..05, CC-03, CC-05, REQ-SEC-001, REQ-FN-005, D-A03-01..06
 */

const API_BASE_URL = '/api/v1/admin';

/**
 * Helper สำหรับสร้าง Header แอดมิน (CC-03, D-A03-06)
 */
export function getAdminHeaders(adminId = 'admin-01', customRole = 'ADMIN') {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Role': customRole,
    'X-Admin-Id': adminId,
  };
}

/**
 * ดึงรายการคำขอนัดหมายสถานะ S2 ที่ตกค้างเกินเกณฑ์เวลา (AC-A03-01, D-A03-02)
 * @param {Object} options - { min_wait_minutes, adminId, customRole }
 */
export async function getStalledOrders(options = {}) {
  const { min_wait_minutes = 30, adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/dispatch/stalled-orders?min_wait_minutes=${encodeURIComponent(min_wait_minutes)}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูคิวงานตกค้างได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการดึงข้อมูลงานตกค้าง';
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * แอดมินมอบหมายงานตรงให้ซาเล้งเฉพาะราย (Direct Assign -> S3) (AC-A03-01, D-A03-03, D-00-01)
 * @param {Object} data - { order_id, saleng_id, notes, admin_id }
 * @param {Object} options - { adminId, customRole }
 */
export async function manualDispatchOrder(data, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/dispatch/assign`;

  const body = {
    order_id: data.order_id,
    saleng_id: data.saleng_id,
    admin_id: data.admin_id || adminId,
    notes: data.notes || null,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถมอบหมายงานตรงได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการมอบหมายงานตรง';
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * แอดมินขยายรัศมีการค้นหาของคำขอเป็น 10.0 กม. (Expand Radius Broadcast) (AC-A03-01, D-A03-03)
 * @param {Object} data - { order_id, new_radius_km, admin_id }
 * @param {Object} options - { adminId, customRole }
 */
export async function expandSearchRadius(data, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/dispatch/expand-radius`;

  const body = {
    order_id: data.order_id,
    new_radius_km: Number(data.new_radius_km || 10.0),
    admin_id: data.admin_id || adminId,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถขยายรัศมีการค้นหาได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการขยายรัศมี';
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * ดึงรายการข้อพิพาทรอดำเนินการ (AC-A03-02, D-A03-01)
 * @param {Object} options - { status, adminId, customRole }
 */
export async function getDisputes(options = {}) {
  const { status = 'PENDING_ADMIN', adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/disputes?status=${encodeURIComponent(status)}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูรายการข้อพิพาทได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการดึงข้อมูลข้อพิพาท';
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * ดึงสำนวนหลักฐานข้อพิพาท 4 มิติฉบับสมบูรณ์ (AC-A03-02, D-A03-04)
 * @param {string} disputeId
 * @param {Object} options - { adminId, customRole }
 */
export async function getDisputeDossier(disputeId, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/disputes/${encodeURIComponent(disputeId)}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูสำนวนข้อพิพาทได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการดึงสำนวนหลักฐาน';
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * แอดมินตัดสินชี้ขาดข้อพิพาท (AC-A03-03, AC-A03-04, D-A03-05)
 * @param {string} disputeId
 * @param {Object} data - { action, arbitrated_amount, arbitration_note, admin_id }
 * @param {Object} options - { adminId, customRole }
 */
export async function resolveDispute(disputeId, data, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/disputes/${encodeURIComponent(disputeId)}/resolve`;

  const body = {
    action: data.action,
    arbitrated_amount: data.arbitrated_amount != null ? Number(data.arbitrated_amount) : null,
    arbitration_note: data.arbitration_note || null,
    admin_id: data.admin_id || adminId,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถตัดสินชี้ขาดข้อพิพาทได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการตัดสินชี้ขาด';
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

