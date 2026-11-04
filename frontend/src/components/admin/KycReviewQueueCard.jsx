import React, { useState } from 'react';

/**
 * คอมโพเนนต์การ์ดคำขอยืนยันตัวตน KYC สำหรับแอดมิน (AC-A01-01, AC-A01-02, REQ-UX-001, CC-01)
 * ทุกปุ่มกดทัชทาร์เก็ต >= 48px
 */
export default function KycReviewQueueCard({ submission, onApprove, onReject, isLoading = false }) {
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleApprove = () => {
    if (onApprove) {
      onApprove(submission.id);
    }
  };

  const handleConfirmReject = (e) => {
    e.preventDefault();
    if (!rejectionReason.trim()) {
      setErrorMsg('กรุณาระบุเหตุผลการปฏิเสธ');
      return;
    }
    setErrorMsg('');
    if (onReject) {
      onReject(submission.id, rejectionReason.trim());
    }
    setShowRejectModal(false);
  };

  return (
    <div
      className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow mb-4"
      data-testid={`kyc-card-${submission.id}`}
      data-req="UC-11"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3 mb-4">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 text-amber-700 rounded-full border border-amber-200">
            {submission.status === 'PENDING_REVIEW' ? 'รอตรวจสอบ' : submission.status}
          </span>
          <h3 className="text-lg font-bold text-gray-900 mt-1">{submission.full_name}</h3>
          <p className="text-xs text-gray-500">รหัสซาเล้ง: {submission.saleng_id}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">หมายเลขบัตรประชาชน (PDPA)</p>
          <p className="text-sm font-mono font-semibold text-gray-800" data-testid="masked-id-card">
            {submission.id_card_no_masked}
          </p>
        </div>
      </div>

      {/* รูปถ่ายหลักฐาน 3 ใบ */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div className="border border-gray-100 rounded-lg p-2 text-center bg-gray-50">
          <p className="text-xs font-medium text-gray-600 mb-1">หน้าบัตรประชาชน</p>
          <img
            src={submission.id_card_photo_url || 'https://via.placeholder.com/150'}
            alt="บัตรประชาชน"
            className="w-full h-32 object-cover rounded border border-gray-200"
            data-testid="kyc-img-id-card"
          />
        </div>
        <div className="border border-gray-100 rounded-lg p-2 text-center bg-gray-50">
          <p className="text-xs font-medium text-gray-600 mb-1">ภาพถ่ายเซลฟี่คู่บัตร</p>
          <img
            src={submission.selfie_with_id_photo_url || submission.selfie_photo_url || 'https://via.placeholder.com/150'}
            alt="เซลฟี่คู่บัตร"
            className="w-full h-32 object-cover rounded border border-gray-200"
            data-testid="kyc-img-selfie"
          />
        </div>
        <div className="border border-gray-100 rounded-lg p-2 text-center bg-gray-50">
          <p className="text-xs font-medium text-gray-600 mb-1">ยานพาหนะและทะเบียน</p>
          {submission.vehicle_photo_url ? (
            <img
              src={submission.vehicle_photo_url}
              alt="ยานพาหนะ"
              className="w-full h-32 object-cover rounded border border-gray-200"
              data-testid="kyc-img-vehicle"
            />
          ) : (
            <div className="w-full h-32 flex items-center justify-center bg-gray-100 text-gray-400 text-xs rounded">
              ไม่มีรูปยานพาหนะ
            </div>
          )}
          {submission.vehicle_plate && (
            <p className="text-xs text-gray-500 mt-1 font-mono">{submission.vehicle_plate}</p>
          )}
        </div>
      </div>

      {/* ปุ่มดำเนินการ อนุมัติ / ปฏิเสธ (ความสูง >= 48px) */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={handleApprove}
          disabled={isLoading}
          className="flex-1 min-h-[48px] px-4 py-3 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-semibold rounded-lg shadow-sm transition-colors text-sm flex items-center justify-center cursor-pointer disabled:opacity-50"
          data-testid="btn-approve-kyc"
        >
          อนุมัติ KYC
        </button>
        <button
          type="button"
          onClick={() => setShowRejectModal(true)}
          disabled={isLoading}
          className="flex-1 min-h-[48px] px-4 py-3 bg-rose-600 hover:bg-rose-700 active:bg-rose-800 text-white font-semibold rounded-lg shadow-sm transition-colors text-sm flex items-center justify-center cursor-pointer disabled:opacity-50"
          data-testid="btn-reject-kyc"
        >
          ปฏิเสธคำขอ
        </button>
      </div>

      {/* Modal ระบุเหตุผลการปฏิเสธ */}
      {showRejectModal && (
        <div
          className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
          data-testid="kyc-reject-modal"
        >
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-gray-200">
            <h4 className="text-base font-bold text-gray-900 mb-2">ระบุเหตุผลการปฏิเสธคำขอ KYC</h4>
            <p className="text-xs text-gray-500 mb-4">
              เหตุผลนี้จะส่งแจ้งเตือนไปยังซาเล้ง เพื่อให้แก้ไขและส่งเอกสารใหม่
            </p>

            {errorMsg && (
              <div className="p-3 mb-3 bg-rose-50 text-rose-700 text-xs rounded border border-rose-200" data-testid="reject-modal-error">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleConfirmReject}>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="เช่น ภาพถ่ายหน้าบัตรเบลอ ไม่สามารถอ่านเลขประจำตัวได้ชัดเจน"
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-rose-500 focus:outline-none mb-4"
                data-testid="rejection-reason-input"
              />

              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowRejectModal(false)}
                  className="min-h-[48px] px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 cursor-pointer"
                >
                  ยกเลิก
                </button>
                <button
                  type="submit"
                  className="min-h-[48px] px-5 py-2 bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-lg text-sm cursor-pointer"
                  data-testid="btn-confirm-reject"
                >
                  ยืนยันปฏิเสธ
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
