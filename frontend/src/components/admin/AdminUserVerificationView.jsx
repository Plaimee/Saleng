import React, { useState, useEffect, useCallback } from 'react';
import KycReviewQueueCard from './KycReviewQueueCard';
import UserPenaltyControlCard from './UserPenaltyControlCard';
import {
  getKycSubmissions,
  reviewKyc,
  getUsers,
  penalizeUser,
  reactivateUser,
} from '../../services/adminUserApi';

/**
 * หน้าจอหลักระบบตรวจสอบอนุมัติผู้ใช้งานและจัดการบทลงโทษ (Admin SPA)
 * รองรับ UC-11, REQ-UX-001, CC-01, CC-03, CC-05, CC-06
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 */
export default function AdminUserVerificationView() {
  const [activeTab, setActiveTab] = useState('kyc'); // 'kyc' | 'penalty'

  // State: KYC Submissions
  const [kycSubmissions, setKycSubmissions] = useState([]);
  const [kycStatusFilter, setKycStatusFilter] = useState('PENDING_REVIEW');
  const [isKycLoading, setIsKycLoading] = useState(false);
  const [kycError, setKycError] = useState('');
  const [kycSuccessMsg, setKycSuccessMsg] = useState('');

  // State: Users & Penalties
  const [users, setUsers] = useState([]);
  const [userRoleFilter, setUserRoleFilter] = useState('');
  const [userStatusFilter, setUserStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isUsersLoading, setIsUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState('');
  const [usersSuccessMsg, setUsersSuccessMsg] = useState('');

  // Load KYC data
  const fetchKycList = useCallback(async () => {
    setIsKycLoading(true);
    setKycError('');
    try {
      const data = await getKycSubmissions(kycStatusFilter ? { status: kycStatusFilter } : {});
      setKycSubmissions(data || []);
    } catch (err) {
      setKycError(err.message || 'ไม่สามารถโหลดรายการคำขอ KYC ได้');
    } finally {
      setIsKycLoading(false);
    }
  }, [kycStatusFilter]);

  // Load Users data
  const fetchUsersList = useCallback(async () => {
    setIsUsersLoading(true);
    setUsersError('');
    try {
      const params = {};
      if (userRoleFilter) params.role = userRoleFilter;
      if (userStatusFilter) params.status = userStatusFilter;
      if (searchQuery.trim()) params.q = searchQuery.trim();
      const data = await getUsers(params);
      setUsers(data || []);
    } catch (err) {
      setUsersError(err.message || 'ไม่สามารถโหลดรายชื่อผู้ใช้ได้');
    } finally {
      setIsUsersLoading(false);
    }
  }, [userRoleFilter, userStatusFilter, searchQuery]);

  useEffect(() => {
    if (activeTab === 'kyc') {
      fetchKycList();
    } else {
      fetchUsersList();
    }
  }, [activeTab, fetchKycList, fetchUsersList]);

  // Action: Approve KYC
  const handleApproveKyc = async (submissionId) => {
    setIsKycLoading(true);
    setKycError('');
    setKycSuccessMsg('');
    try {
      await reviewKyc({
        submission_id: submissionId,
        action: 'APPROVE',
      });
      setKycSuccessMsg('อนุมัติยืนยันตัวตนเรียบร้อยแล้ว (เปิดสิทธิ์รับงาน UC-04)');
      await fetchKycList();
    } catch (err) {
      setKycError(err.message || 'เกิดข้อผิดพลาดในการอนุมัติ');
    } finally {
      setIsKycLoading(false);
    }
  };

  // Action: Reject KYC
  const handleRejectKyc = async (submissionId, rejectionReason) => {
    setIsKycLoading(true);
    setKycError('');
    setKycSuccessMsg('');
    try {
      await reviewKyc({
        submission_id: submissionId,
        action: 'REJECT',
        rejection_reason: rejectionReason,
      });
      setKycSuccessMsg('ปฏิเสธคำขอยืนยันตัวตนเรียบร้อยแล้ว');
      await fetchKycList();
    } catch (err) {
      setKycError(err.message || 'เกิดข้อผิดพลาดในการปฏิเสธ');
    } finally {
      setIsKycLoading(false);
    }
  };

  // Action: Penalize User
  const handlePenalizeUser = async (userId, role, penaltyType, reason) => {
    setIsUsersLoading(true);
    setUsersError('');
    setUsersSuccessMsg('');
    try {
      await penalizeUser({
        user_id: userId,
        role: role,
        penalty_type: penaltyType,
        penalty_reason: reason,
      });
      setUsersSuccessMsg(`บันทึกบทลงโทษ (${penaltyType === 'BANNED' ? 'แบนถาวร' : 'ระงับชั่วคราว'}) สำเร็จ`);
      await fetchUsersList();
    } catch (err) {
      setUsersError(err.message || 'เกิดข้อผิดพลาดในการลงโทษผู้ใช้');
    } finally {
      setIsUsersLoading(false);
    }
  };

  // Action: Reactivate User
  const handleReactivateUser = async (userId, role) => {
    setIsUsersLoading(true);
    setUsersError('');
    setUsersSuccessMsg('');
    try {
      await reactivateUser({
        user_id: userId,
        role: role,
      });
      setUsersSuccessMsg('ปลดระงับและคืนสถานะ ACTIVE เรียบร้อยแล้ว');
      await fetchUsersList();
    } catch (err) {
      setUsersError(err.message || 'เกิดข้อผิดพลาดในการปลดระงับบัญชี');
    } finally {
      setIsUsersLoading(false);
    }
  };

  return (
    <div
      className="max-w-5xl mx-auto px-4 py-6 font-sans text-gray-800"
      data-testid="admin-user-verification-view"
      data-req="UC-11"
    >
      {/* Header */}
      <header className="mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-200 pb-4">
          <div>
            <h1 className="text-2xl font-black text-gray-900 tracking-tight">
              ระบบตรวจสอบและจัดการบัญชีผู้ใช้งาน (Admin Panel)
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              ตรวจสอบอนุมัติ KYC ซาเล้ง และจัดการบทลงโทษบัญชีผู้ใช้ตามข้อกำหนด UC-11
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-semibold border border-emerald-300">
              Online Only (CC-05)
            </span>
            <span className="text-xs bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-semibold border border-blue-300">
              Admin RBAC (CC-03)
            </span>
          </div>
        </div>

        {/* Tab Buttons: Touch targets >= 48px */}
        <div className="flex gap-2 mt-4" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'kyc'}
            onClick={() => setActiveTab('kyc')}
            data-testid="tab-kyc"
            className={`min-h-[48px] px-6 py-2.5 rounded-xl font-bold text-sm transition-all focus:outline-none focus:ring-4 ${
              activeTab === 'kyc'
                ? 'bg-emerald-600 text-white shadow-md focus:ring-emerald-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-300'
            }`}
          >
            คิวคำขอยืนยันตัวตน KYC
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'penalty'}
            onClick={() => setActiveTab('penalty')}
            data-testid="tab-penalty"
            className={`min-h-[48px] px-6 py-2.5 rounded-xl font-bold text-sm transition-all focus:outline-none focus:ring-4 ${
              activeTab === 'penalty'
                ? 'bg-emerald-600 text-white shadow-md focus:ring-emerald-200'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-300'
            }`}
          >
            จัดการบทลงโทษผู้ใช้
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {/* TAB 1: KYC REVIEW QUEUE */}
        {activeTab === 'kyc' && (
          <section aria-labelledby="kyc-section-heading" data-testid="kyc-tab-content">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4 bg-gray-50 p-4 rounded-xl border border-gray-200">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-600">สถานะคำขอ:</span>
                <button
                  type="button"
                  onClick={() => setKycStatusFilter('PENDING_REVIEW')}
                  className={`min-h-[48px] px-4 py-2 rounded-lg text-xs font-medium border transition-colors ${
                    kycStatusFilter === 'PENDING_REVIEW'
                      ? 'bg-amber-600 text-white border-amber-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                  data-testid="filter-kyc-pending"
                >
                  รอตรวจสอบ (PENDING)
                </button>
                <button
                  type="button"
                  onClick={() => setKycStatusFilter('')}
                  className={`min-h-[48px] px-4 py-2 rounded-lg text-xs font-medium border transition-colors ${
                    kycStatusFilter === ''
                      ? 'bg-gray-800 text-white border-gray-800'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                  data-testid="filter-kyc-all"
                >
                  ทั้งหมด
                </button>
              </div>

              <button
                type="button"
                onClick={fetchKycList}
                disabled={isKycLoading}
                className="min-h-[48px] px-4 py-2 bg-white border border-gray-300 hover:bg-gray-100 rounded-lg text-xs font-semibold text-gray-700 transition-colors disabled:opacity-50"
                data-testid="btn-refresh-kyc"
              >
                {isKycLoading ? 'กำลังโหลด...' : 'รีเฟรชข้อมูล'}
              </button>
            </div>

            {/* Notification banners */}
            {kycError && (
              <div className="p-4 mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm" role="alert" data-testid="kyc-error-banner">
                {kycError}
              </div>
            )}
            {kycSuccessMsg && (
              <div className="p-4 mb-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-sm" role="status" data-testid="kyc-success-banner">
                {kycSuccessMsg}
              </div>
            )}

            {/* List */}
            {isKycLoading && kycSubmissions.length === 0 ? (
              <div className="text-center py-12 text-gray-500 text-sm">กำลังโหลดรายการคำขอ...</div>
            ) : kycSubmissions.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-2xl border border-dashed border-gray-300 text-gray-500 text-sm" data-testid="kyc-empty-state">
                ไม่พบรายการคำขอยืนยันตัวตนในขณะนี้
              </div>
            ) : (
              <div className="space-y-4">
                {kycSubmissions.map((sub) => (
                  <KycReviewQueueCard
                    key={sub.id}
                    submission={sub}
                    onApprove={handleApproveKyc}
                    onReject={handleRejectKyc}
                    isLoading={isKycLoading}
                  />
                ))}
              </div>
            )}
          </section>
        )}

        {/* TAB 2: USER PENALTY MANAGEMENT */}
        {activeTab === 'penalty' && (
          <section aria-labelledby="penalty-section-heading" data-testid="penalty-tab-content">
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-4 space-y-3">
              <div className="flex flex-wrap gap-2 items-center">
                <input
                  type="text"
                  placeholder="ค้นหาชื่อ, รหัสผู้ใช้ หรือเบอร์โทร..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 min-h-[48px] px-4 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-emerald-500"
                  data-testid="user-search-input"
                />
                <button
                  type="button"
                  onClick={fetchUsersList}
                  disabled={isUsersLoading}
                  className="min-h-[48px] px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                  data-testid="btn-search-users"
                >
                  {isUsersLoading ? 'ค้นหา...' : 'ค้นหา'}
                </button>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-gray-200">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-semibold text-gray-600">ประเภทผู้ใช้:</span>
                  <button
                    type="button"
                    onClick={() => setUserRoleFilter('')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userRoleFilter === ''
                        ? 'bg-gray-800 text-white border-gray-800'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-role-all"
                  >
                    ทั้งหมด
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserRoleFilter('COLLECTOR')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userRoleFilter === 'COLLECTOR'
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-role-collector"
                  >
                    ซาเล้ง (COLLECTOR)
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserRoleFilter('SELLER')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userRoleFilter === 'SELLER'
                        ? 'bg-purple-600 text-white border-purple-600'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-role-seller"
                  >
                    ผู้ขาย (SELLER)
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-semibold text-gray-600">สถานะ:</span>
                  <button
                    type="button"
                    onClick={() => setUserStatusFilter('')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userStatusFilter === ''
                        ? 'bg-gray-800 text-white border-gray-800'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-status-all"
                  >
                    ทั้งหมด
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserStatusFilter('ACTIVE')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userStatusFilter === 'ACTIVE'
                        ? 'bg-emerald-600 text-white border-emerald-600'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-status-active"
                  >
                    ปกติ
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserStatusFilter('SUSPENDED_TEMPORARY')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userStatusFilter === 'SUSPENDED_TEMPORARY'
                        ? 'bg-amber-600 text-white border-amber-600'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-status-suspended"
                  >
                    ระงับชั่วคราว
                  </button>
                  <button
                    type="button"
                    onClick={() => setUserStatusFilter('BANNED')}
                    className={`min-h-[48px] px-3 py-1.5 rounded-lg text-xs font-medium border ${
                      userStatusFilter === 'BANNED'
                        ? 'bg-rose-600 text-white border-rose-600'
                        : 'bg-white text-gray-700 border-gray-300'
                    }`}
                    data-testid="filter-status-banned"
                  >
                    แบนถาวร
                  </button>
                </div>
              </div>
            </div>

            {/* Notification banners */}
            {usersError && (
              <div className="p-4 mb-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm" role="alert" data-testid="users-error-banner">
                {usersError}
              </div>
            )}
            {usersSuccessMsg && (
              <div className="p-4 mb-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-sm" role="status" data-testid="users-success-banner">
                {usersSuccessMsg}
              </div>
            )}

            {/* List */}
            {isUsersLoading && users.length === 0 ? (
              <div className="text-center py-12 text-gray-500 text-sm">กำลังโหลดรายชื่อผู้ใช้...</div>
            ) : users.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-2xl border border-dashed border-gray-300 text-gray-500 text-sm" data-testid="users-empty-state">
                ไม่พบรายชื่อผู้ใช้ตามเงื่อนไขที่กำหนด
              </div>
            ) : (
              <div className="space-y-4">
                {users.map((u) => (
                  <UserPenaltyControlCard
                    key={`${u.role}-${u.user_id}`}
                    user={u}
                    onPenalize={handlePenalizeUser}
                    onReactivate={handleReactivateUser}
                    isLoading={isUsersLoading}
                  />
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

