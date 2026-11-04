/**
 * Frontend API Client สำหรับระบบผู้ดูแลระบบ (Admin Feature 01)
 * รองรับ UC-11, AC-A01-01..05, CC-03, CC-05, REQ-SEC-001, REQ-SEC-002
 */

const API_BASE_URL = '/api/v1/admin';

/**
 * Helper สำหรับสร้าง Header แอดมิน (CC-03, D-A01-05)
 */
export function getAdminHeaders(adminId = 'admin-01', customRole = 'ADMIN') {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Role': customRole,
    'X-Admin-Id': adminId,
  };
}

/**
 * เรียกดูคิวคำขอยืนยันตัวตน KYC (AC-A01-01)
 */
export async function getKycSubmissions(statusOrOptions = 'PENDING_REVIEW', adminId = 'admin-01', customRole = 'ADMIN') {
  let status = statusOrOptions;
  if (typeof statusOrOptions === 'object' && statusOrOptions !== null) {
    status = statusOrOptions.status !== undefined ? statusOrOptions.status : 'PENDING_REVIEW';
    if (statusOrOptions.adminId) adminId = statusOrOptions.adminId;
    if (statusOrOptions.customRole) customRole = statusOrOptions.customRole;
  }
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  const url = `${API_BASE_URL}/kyc/submissions${query}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถเรียกดูคิว KYC ได้' }));
    throw new Error(errorData.detail || `Error ${response.status}`);
  }

  return await response.json();
}

/**
 * พิจารณาอนุมัติหรือปฏิเสธคำขอ KYC (AC-A01-02)
 */
export async function reviewKyc(submissionIdOrOptions, action, rejectionReason = null, adminId = 'admin-01', customRole = 'ADMIN') {
  let submissionId = submissionIdOrOptions;
  if (typeof submissionIdOrOptions === 'object' && submissionIdOrOptions !== null) {
    submissionId = submissionIdOrOptions.submission_id || submissionIdOrOptions.submissionId;
    action = submissionIdOrOptions.action;
    rejectionReason = submissionIdOrOptions.rejection_reason || submissionIdOrOptions.rejectionReason;
    if (submissionIdOrOptions.adminId) adminId = submissionIdOrOptions.adminId;
    if (submissionIdOrOptions.customRole) customRole = submissionIdOrOptions.customRole;
  }

  const url = `${API_BASE_URL}/kyc/review`;
  const body = {
    submission_id: submissionId,
    action: action,
  };
  if (rejectionReason) {
    body.rejection_reason = rejectionReason;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถบันทึกผลการพิจารณาได้' }));
    throw new Error(errorData.detail || `Error ${response.status}`);
  }

  return await response.json();
}

/**
 * ดึงรายชื่อผู้ใช้งานทั้งหมด พร้อมสถานะบัญชี (AC-A01-03)
 */
export async function getUsers(roleOrOptions = null, status = null, search = null, adminId = 'admin-01', customRole = 'ADMIN') {
  let role = roleOrOptions;
  if (typeof roleOrOptions === 'object' && roleOrOptions !== null) {
    role = roleOrOptions.role;
    status = roleOrOptions.status;
    search = roleOrOptions.search || roleOrOptions.q;
    if (roleOrOptions.adminId) adminId = roleOrOptions.adminId;
    if (roleOrOptions.customRole) customRole = roleOrOptions.customRole;
  }

  const params = new URLSearchParams();
  if (role) params.append('role', role);
  if (status) params.append('status', status);
  if (search) params.append('search', search);

  const queryStr = params.toString() ? `?${params.toString()}` : '';
  const url = `${API_BASE_URL}/users${queryStr}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: getAdminHeaders(adminId, customRole),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถดึงรายชื่อผู้ใช้ได้' }));
    throw new Error(errorData.detail || `Error ${response.status}`);
  }

  return await response.json();
}

/**
 * สั่งระงับสิทธิ์บัญชีผู้ใช้ชั่วคราวหรือถาวร (AC-A01-03)
 */
export async function penalizeUser(userIdOrOptions, role, action, penaltyReason, durationDays = null, adminId = 'admin-01', customRole = 'ADMIN') {
  let userId = userIdOrOptions;
  if (typeof userIdOrOptions === 'object' && userIdOrOptions !== null) {
    userId = userIdOrOptions.user_id || userIdOrOptions.userId;
    role = userIdOrOptions.role;
    action = userIdOrOptions.action || (userIdOrOptions.penalty_type === 'BANNED' ? 'BAN' : 'SUSPEND_TEMPORARY');
    penaltyReason = userIdOrOptions.penalty_reason || userIdOrOptions.penaltyReason;
    durationDays = userIdOrOptions.duration_days || userIdOrOptions.durationDays;
    if (userIdOrOptions.adminId) adminId = userIdOrOptions.adminId;
    if (userIdOrOptions.customRole) customRole = userIdOrOptions.customRole;
  }

  const url = `${API_BASE_URL}/users/penalty`;
  const body = {
    user_id: userId,
    role: role,
    action: action === 'SUSPENDED_TEMPORARY' ? 'SUSPEND_TEMPORARY' : action,
    penalty_reason: penaltyReason,
  };
  if (durationDays) {
    body.duration_days = durationDays;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถบันทึกบทลงโทษได้' }));
    throw new Error(errorData.detail || `Error ${response.status}`);
  }

  return await response.json();
}

/**
 * ปลดระงับสิทธิ์บัญชีผู้ใช้ คืนสถานะ ACTIVE (AC-A01-04)
 */
export async function reactivateUser(userIdOrOptions, role, reason = 'ADMIN_REINSTATED', adminId = 'admin-01', customRole = 'ADMIN') {
  let userId = userIdOrOptions;
  if (typeof userIdOrOptions === 'object' && userIdOrOptions !== null) {
    userId = userIdOrOptions.user_id || userIdOrOptions.userId;
    role = userIdOrOptions.role;
    reason = userIdOrOptions.reason || 'ADMIN_REINSTATED';
    if (userIdOrOptions.adminId) adminId = userIdOrOptions.adminId;
    if (userIdOrOptions.customRole) customRole = userIdOrOptions.customRole;
  }

  const url = `${API_BASE_URL}/users/reactivate`;
  const body = {
    user_id: userId,
    role: role,
    reason: reason,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: getAdminHeaders(adminId, customRole),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'ไม่สามารถปลดระงับสิทธิ์ได้' }));
    throw new Error(errorData.detail || `Error ${response.status}`);
  }

  return await response.json();
}
