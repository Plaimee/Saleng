/**
 * Frontend API Client สำหรับระบบความปลอดภัย ตรวจสอบร่องรอย และ PDPA (Admin Feature 04)
 * รองรับ UC-13, AC-A04-01..05, CC-03, CC-05, REQ-SEC-001, REQ-SEC-002, CT-01, D-A04-01..06
 */

const API_BASE_URL = '/api/v1/admin/compliance';

/**
 * Helper สำหรับสร้าง Header แอดมิน (CC-03, D-A04-02)
 */
export function getAdminHeaders(adminId = 'admin-01', customRole = 'ADMIN') {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Role': customRole,
    'X-Admin-Id': adminId,
  };
}

/**
 * ดึงรายการบันทึกประวัติ Audit Trail กรองตามเงื่อนไข (AC-A04-01, D-A04-01)
 */
export async function getAuditLogs(params = {}, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const query = new URLSearchParams();
  if (params.action) query.append('action', params.action);
  if (params.actor_role) query.append('actor_role', params.actor_role);
  if (params.actor_id) query.append('actor_id', params.actor_id);
  if (params.start_date) query.append('start_date', params.start_date);
  if (params.end_date) query.append('end_date', params.end_date);
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);

  const url = `${API_BASE_URL}/audit-logs?${query.toString()}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดู Audit Trail ได้' }));
    const errorMsg = typeof errorData.detail === 'string' ? errorData.detail : 'ข้อผิดพลาดในการดึง Audit Trail';
    const err = new Error(errorMsg);
    err.status = response.status;
    throw err;
  }

  return await response.json();
}

/**
 * ส่งออกบันทึก Audit Trail เป็นไฟล์ CSV หรือ JSON (AC-A04-01, D-A04-01)
 */
export async function exportAuditLogs(params = {}, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const query = new URLSearchParams();
  query.append('format', params.format || 'csv');
  if (params.action) query.append('action', params.action);
  if (params.actor_role) query.append('actor_role', params.actor_role);

  const url = `${API_BASE_URL}/audit-logs/export?${query.toString()}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const err = new Error('ไม่สามารถส่งออก Audit Trail ได้');
    err.status = response.status;
    throw err;
  }

  if (params.format === 'json') {
    return await response.json();
  }
  return await response.text();
}

/**
 * ตรวจสอบความถูกต้องสมบูรณ์ของบันทึก Audit Trail ด้วย SHA-256 (AC-A04-02, D-A04-05)
 */
export async function verifyAuditIntegrity(options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const url = `${API_BASE_URL}/audit-logs/verify-integrity`;

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถตรวจสอบ Integrity ได้' }));
    const err = new Error(errorData.detail || 'ข้อผิดพลาดในการตรวจสอบ Integrity');
    err.status = response.status;
    throw err;
  }

  return await response.json();
}

/**
 * ดึงรายงานสถิติปริมาณขยะรีไซเคิลชุมชนรายเขต/แขวง แบบ No PII (AC-A04-05, D-A04-03)
 */
export async function getCommunityWasteReport(params = {}, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const query = new URLSearchParams();
  if (params.period) query.append('period', params.period);
  if (params.district) query.append('district', params.district);

  const url = `${API_BASE_URL}/reports/community-waste?${query.toString()}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถดึงรายงานขยะชุมชนได้' }));
    const err = new Error(errorData.detail || 'ข้อผิดพลาดในการดึงรายงานขยะชุมชน');
    err.status = response.status;
    throw err;
  }

  return await response.json();
}

/**
 * ส่งออกรายงานขยะชุมชนเป็นไฟล์ CSV (AC-A04-05)
 */
export async function exportCommunityWasteCsv(params = {}, options = {}) {
  const { adminId = 'admin-01', customRole = 'ADMIN' } = options;
  const query = new URLSearchParams();
  if (params.period) query.append('period', params.period);
  if (params.district) query.append('district', params.district);

  const url = `${API_BASE_URL}/reports/community-waste/export?${query.toString()}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const err = new Error('ไม่สามารถส่งออก CSV รายงานขยะชุมชนได้');
    err.status = response.status;
    throw err;
  }

  return await response.text();
}

/**
 * ตรวจสอบสถานะการเก็บรักษาข้อมูลและรายการหมดอายุตามนโยบาย PDPA (AC-A04-04, D-A04-04)
 */
export async function getPdpaRetentionStatus(options = {}) {
  const { adminId = 'admin-01', customRole = 'DPO' } = options;
  const url = `${API_BASE_URL}/retention-status`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถดึงสถานะ Retention ได้' }));
    const err = new Error(errorData.detail || 'ข้อผิดพลาดในการดึงสถานะ Retention');
    err.status = response.status;
    throw err;
  }

  return await response.json();
}

/**
 * ดำเนินการล้างข้อมูลหมดอายุตามนโยบาย PDPA (AC-A04-04, D-A04-04)
 */
export async function purgeExpiredPdpaData(data = {}, options = {}) {
  const { adminId = 'admin-01', customRole = 'DPO' } = options;
  const url = `${API_BASE_URL}/purge-expired`;

  const payload = {
    admin_id: data.admin_id || adminId,
    confirm_purge: data.confirm_purge !== undefined ? data.confirm_purge : true,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถดำเนินการล้างข้อมูลได้' }));
    const err = new Error(errorData.detail || 'ข้อผิดพลาดในการล้างข้อมูล');
    err.status = response.status;
    throw err;
  }

  return await response.json();
}

