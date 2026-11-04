/**
 * Frontend API Client สำหรับระบบจัดการราคากลางและเกณฑ์คุณภาพ (Admin Feature 02)
 * รองรับ UC-03, UC-05, AC-A02-01..05, CC-03, CC-05, REQ-DAT-001, REQ-FN-003, REQ-SEC-001
 */

const API_BASE_URL = '/api/v1/admin/benchmark-prices';

/**
 * Helper สำหรับสร้าง Header แอดมิน (CC-03, D-A02-06)
 */
export function getAdminHeaders(adminId = 'admin-01', customRole = 'ADMIN') {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Role': customRole,
    'X-Admin-Id': adminId,
  };
}

/**
 * ดึงรายการราคากลางประจำวันทั้งหมดสำหรับแอดมิน (AC-A02-01)
 * @param {Object} options - { unit, q, adminId, customRole }
 */
export async function getBenchmarkPrices(options = {}) {
  const { unit, q, adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const params = new URLSearchParams();
  if (unit && unit !== 'all') params.append('unit', unit);
  if (q) params.append('q', q);

  const queryStr = params.toString() ? `?${params.toString()}` : '';
  const url = `${API_BASE_URL}${queryStr}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูตารางราคากลางได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : (errorData.detail?.message || 'ข้อผิดพลาดในการดึงข้อมูลราคา');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * แก้ไขช่วงราคากลางรายวัน (Min-Max) ของหมวดหมู่วัสดุ (AC-A02-01, D-A02-02)
 * @param {string} categoryCode
 * @param {Object} data - { min_price_per_unit, max_price_per_unit, grading_condition, confirm_shift, change_reason }
 * @param {Object} options - { adminId, customRole }
 */
export async function updateBenchmarkPrice(categoryCode, data, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/${encodeURIComponent(categoryCode)}`;

  const body = {
    min_price_per_unit: Number(data.min_price_per_unit),
    max_price_per_unit: Number(data.max_price_per_unit),
    grading_condition: data.grading_condition || null,
    confirm_shift: Boolean(data.confirm_shift),
    updated_by: adminId,
    change_reason: data.change_reason || null,
  };

  const response = await fetch(url, {
    method: 'PUT',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถอัปเดตราคากลางได้' }));
    const errorMsg = typeof errorData.detail === 'string'
      ? errorData.detail
      : (errorData.detail?.message || 'ข้อผิดพลาดในการอัปเดตราคา');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * อัปเดตราคากลางแบบกลุ่มประจำวัน (Batch Update — AC-A02-03)
 * @param {Object} data - { items, effective_date, change_reason }
 * @param {Object} options - { adminId, customRole }
 */
export async function batchUpdatePrices(data, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/batch-update`;

  const body = {
    items: data.items.map(it => ({
      category_code: it.category_code,
      min_price_per_unit: Number(it.min_price_per_unit),
      max_price_per_unit: Number(it.max_price_per_unit),
      grading_condition: it.grading_condition || null,
      confirm_shift: Boolean(it.confirm_shift),
    })),
    effective_date: data.effective_date || null,
    updated_by: adminId,
    change_reason: data.change_reason || null,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถอัปเดตราคาแบบกลุ่มได้' }));
    const errorMsg = typeof errorData.detail === 'string'
      ? errorData.detail
      : (errorData.detail?.message || 'ข้อผิดพลาดในการอัปเดตราคาแบบกลุ่ม');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * ดึงเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน (AC-A02-02)
 * @param {string} categoryCode
 * @param {Object} options - { adminId, customRole }
 */
export async function getGradingRules(categoryCode, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/grading/${encodeURIComponent(categoryCode)}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูเกณฑ์คุณภาพได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : (errorData.detail?.message || 'ข้อผิดพลาดในการดึงเกณฑ์คุณภาพ');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * ปรับปรุงเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน (AC-A02-02)
 * @param {string} categoryCode
 * @param {Object} data - { rules }
 * @param {Object} options - { adminId, customRole }
 */
export async function updateGradingRules(categoryCode, data, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/grading/${encodeURIComponent(categoryCode)}`;

  const body = {
    rules: data.rules,
    updated_by: adminId,
  };

  const response = await fetch(url, {
    method: 'PUT',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถอัปเดตเกณฑ์คุณภาพได้' }));
    const errorMsg = typeof errorData.detail === 'string'
      ? errorData.detail
      : (errorData.detail?.message || 'ข้อผิดพลาดในการอัปเดตเกณฑ์คุณภาพ');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

/**
 * ดึงประวัติการปรับปรุงราคาของหมวดหมู่ (AC-A02-05)
 * @param {string} categoryCode
 * @param {number} limit
 * @param {Object} options - { adminId, customRole }
 */
export async function getPriceHistory(categoryCode, limit = 20, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/history/${encodeURIComponent(categoryCode)}?limit=${limit}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูประวัติราคาได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : (errorData.detail?.message || 'ข้อผิดพลาดในการดึงประวัติราคา');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = errorData;
    throw err;
  }

  return await response.json();
}

