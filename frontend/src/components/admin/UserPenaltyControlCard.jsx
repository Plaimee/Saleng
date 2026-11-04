import React, { useState } from 'react';

/**
 * คอมโพเนนต์การ์ดควบคุมบทลงโทษผู้ใช้งาน (AC-A01-03, AC-A01-04, REQ-UX-001, CC-01)
 * รองรับทั้งซาเล้ง (COLLECTOR) และผู้ขาย (SELLER)
 * ทุกปุ่มกดมีทัชทาร์เก็ต >= 48px
 */
export default function UserPenaltyControlCard({ user, onPenalize, onReactivate, isLoading = false }) {
  const [showPenaltyModal, setShowPenaltyModal] = useState(false);
  const [selectedPenaltyType, setSelectedPenaltyType] = useState('SUSPENDED_TEMPORARY');
  const [penaltyReason, setPenaltyReason] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const isSuspended = user.account_status === 'SUSPENDED_TEMPORARY';
  const isBanned = user.account_status === 'BANNED';
  const isActive = user.account_status === 'ACTIVE' || !user.account_status;

  const handleOpenPenaltyModal = (type) => {
    setSelectedPenaltyType(type);
    setPenaltyReason('');
    setErrorMsg('');
    setShowPenaltyModal(true);
  };

  const handleConfirmPenalty = (e) => {
    e.preventDefault();
    if (!penaltyReason.trim()) {
      setErrorMsg('กรุณาระบุเหตุผลการลงโทษ');
      return;
    }
    setErrorMsg('');
    if (onPenalize) {
      onPenalize(user.user_id, user.role, selectedPenaltyType, penaltyReason.trim());
    }
    setShowPenaltyModal(false);
  };

  const handleReactivate = () => {
    if (onReactivate) {
      onReactivate(user.user_id, user.role);
    }
  };

  return (
    <div
      className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow mb-4"
      data-testid={`user-card-${user.user_id}`}
      data-req="UC-11"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span
              className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
                user.role === 'COLLECTOR'
                  ? 'bg-blue-50 text-blue-700 border-blue-200'
                  : 'bg-purple-50 text-purple-700 border-purple-200'
              }`}
            >
              {user.role === 'COLLECTOR' ? 'ซาเล้ง (COLLECTOR)' : 'ผู้ขาย (SELLER)'}
            </span>
            <span
              className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
                isActive
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : isSuspended
                  ? 'bg-amber-50 text-amber-700 border-amber-200'
                  : 'bg-rose-50 text-rose-700 border-rose-200'
              }`}
              data-testid="account-status-badge"
            >
              {isActive ? 'ใช้งานปกติ (ACTIVE)' : isSuspended ? 'ระงับชั่วคราว (SUSPENDED)' : 'แบนถาวร (BANNED)'}
            </span>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-2">{user.display_name || user.name || user.user_id}</h3>
          <p className="text-xs text-gray-500">รหัสผู้ใช้: {user.user_id}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">เบอร์โทรศัพท์ (PDPA)</p>
          <p className="text-sm font-mono font-semibold text-gray-800" data-testid="masked-phone">
            {user.phone_masked || user.phone || '-'}
          </p>
        </div>
      </div>

      {user.penalty_reason && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 text-xs text-red-700" data-testid="penalty-reason-box">
          <span className="font-bold">สาเหตุการลงโทษ:</span> {user.penalty_reason}
        </div>
      )}

      {/* Action Buttons: Touch targets >= 48px */}
      <div className="flex flex-wrap items-center gap-3 pt-2">
        {isActive && (
          <>
            <button
              type="button"
              onClick={() => handleOpenPenaltyModal('SUSPENDED_TEMPORARY')}
              disabled={isLoading}
              data-testid="btn-suspend-user"
              className="flex-1 min-h-[48px] px-4 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-lg text-sm transition-colors focus:ring-4 focus:ring-amber-200 disabled:opacity-50"
            >
              ระงับชั่วคราว
            </button>
            <button
              type="button"
              onClick={() => handleOpenPenaltyModal('BANNED')}
              disabled={isLoading}
              data-testid="btn-ban-user"
              className="flex-1 min-h-[48px] px-4 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-medium rounded-lg text-sm transition-colors focus:ring-4 focus:ring-rose-200 disabled:opacity-50"
            >
              แบนถาวร
            </button>
          </>
        )}

        {(isSuspended || isBanned) && (
          <>
            <button
              type="button"
              onClick={handleReactivate}
              disabled={isLoading}
              data-testid="btn-reactivate-user"
              className="flex-1 min-h-[48px] px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg text-sm transition-colors focus:ring-4 focus:ring-emerald-200 disabled:opacity-50"
            >
              ปลดระงับบัญชี (คืนสถานะ ACTIVE)
            </button>
            {isSuspended && (
              <button
                type="button"
                onClick={() => handleOpenPenaltyModal('BANNED')}
                disabled={isLoading}
                data-testid="btn-upgrade-ban-user"
                className="min-h-[48px] px-4 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-medium rounded-lg text-sm transition-colors focus:ring-4 focus:ring-rose-200 disabled:opacity-50"
              >
                ยกระดับเป็นแบนถาวร
              </button>
            )}
          </>
        )}
      </div>

      {/* Modal ระบุเหตุผลการลงโทษ */}
      {showPenaltyModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
          data-testid="penalty-modal"
        >
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl">
            <h4 className="text-lg font-bold text-gray-900 mb-2">
              {selectedPenaltyType === 'BANNED' ? 'ยืนยันแบนถาวร' : 'ยืนยันระงับบัญชีชั่วคราว'}
            </h4>
            <p className="text-xs text-gray-600 mb-4">
              ผู้ใช้: {user.display_name || user.user_id} ({user.role})
            </p>

            <form onSubmit={handleConfirmPenalty}>
              <div className="mb-4">
                <label htmlFor="penalty-reason-input" className="block text-xs font-semibold text-gray-700 mb-1">
                  เหตุผลการลงโทษ <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="penalty-reason-input"
                  data-testid="penalty-reason-input"
                  rows={3}
                  value={penaltyReason}
                  onChange={(e) => {
                    setPenaltyReason(e.target.value);
                    if (errorMsg) setErrorMsg('');
                  }}
                  placeholder="เช่น โกงตาชั่ง, No-show ซ้ำซาก, มีการร้องเรียนเรื่องพฤติกรรม"
                  className="w-full text-sm border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none"
                />
                {errorMsg && (
                  <p className="text-xs text-red-600 mt-1" data-testid="penalty-modal-error">
                    {errorMsg}
                  </p>
                )}
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowPenaltyModal(false)}
                  className="min-h-[48px] px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  data-testid="btn-cancel-penalty"
                >
                  ยกเลิก
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="min-h-[48px] px-5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  data-testid="btn-confirm-penalty"
                >
                  ยืนยันลงโทษ
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

