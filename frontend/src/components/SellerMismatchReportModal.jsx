import React, { useState } from 'react';

/**
 * SellerMismatchReportModal Component
 * โมดอลรายงานข้อพิพาทหน้างานกรณี No-show หรือของไม่ตรงสเปก (S3/S4 -> S8)
 * รองรับ UC-13, REQ-FN-006, CC-01, D-B07-01, D-B07-02
 */
export default function SellerMismatchReportModal({
  orderId,
  isOpen = false,
  onClose,
  onSubmitReport,
  isSubmitting = false,
}) {
  const [reason, setReason] = useState('SELLER_NO_SHOW');
  const [evidencePhotoUrl, setEvidencePhotoUrl] = useState('https://storage.saleng.app/disputes/evidence.jpg');
  const [notes, setNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!evidencePhotoUrl || !evidencePhotoUrl.trim()) {
      setErrorMsg('จำเป็นต้องแนบภาพถ่ายหน้างานเป็นหลักฐาน (REQ-FN-006)');
      return;
    }

    if (onSubmitReport) {
      onSubmitReport({
        orderId,
        mismatchReason: reason,
        evidencePhotoUrl: evidencePhotoUrl.trim(),
        notes: notes.trim(),
      });
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
      data-req="UC-13"
      data-testid="seller-mismatch-modal"
    >
      <div className="bg-white rounded-3xl max-w-sm w-full p-5 space-y-4 shadow-xl border border-red-100 max-h-[90vh] overflow-y-auto">
        {/* ส่วนหัวโมดอล */}
        <div className="text-center space-y-1 border-b border-gray-100 pb-3">
          <div className="w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto text-2xl">
            ⚠️
          </div>
          <h3 className="text-base font-bold text-gray-800">
            รายงานปัญหาหน้างาน / แจ้งข้อพิพาท
          </h3>
          <p className="text-xs text-gray-500">
            คำขอ #{orderId} (ระบบจะปรับสถานะเป็น S8 และส่งเรื่องให้ Admin ตรวจสอบ)
          </p>
        </div>

        {errorMsg && (
          <div
            className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-700"
            data-testid="modal-error-banner"
          >
            ⚠️ {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {/* เลือกสาเหตุ */}
          <div>
            <label className="text-xs font-bold text-gray-700 block mb-1">
              สาเหตุของปัญหา <span className="text-red-500">*</span>:
            </label>
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full min-h-[48px] px-3 border border-gray-300 rounded-xl text-xs bg-white focus:outline-none focus:ring-2 focus:ring-red-500"
              data-testid="mismatch-reason-select"
            >
              <option value="SELLER_NO_SHOW">ผู้ขายไม่อยู่บ้านตามนัด / ติดต่อไม่ได้ (No-Show)</option>
              <option value="CONTAMINATED_WASTE">ของเก่าปนเปื้อนสารอันตราย / ขยะเน่าเสีย</option>
              <option value="QUANTITY_MISMATCH">ปริมาณของจริงไม่ตรงกับที่แจ้งไว้มาก</option>
              <option value="OTHER">สาเหตุอื่น ๆ</option>
            </select>
          </div>

          {/* ภาพถ่ายหน้างานเป็นหลักฐาน (REQ-FN-006) */}
          <div className="p-3 bg-red-50/50 rounded-xl border border-red-100 space-y-1.5">
            <label className="text-xs font-bold text-red-900 block">
              📸 ภาพถ่ายหน้างานเป็นหลักฐาน (บังคับ) <span className="text-red-500">*</span>:
            </label>
            <input
              type="url"
              required
              value={evidencePhotoUrl}
              onChange={(e) => {
                setEvidencePhotoUrl(e.target.value);
                setErrorMsg('');
              }}
              placeholder="https://storage.saleng.app/disputes/photo.jpg"
              className="w-full min-h-[48px] px-3 border border-red-200 rounded-xl text-xs bg-white focus:outline-none focus:ring-2 focus:ring-red-500"
              data-testid="evidence-photo-input"
            />
            <p className="text-[11px] text-red-700">
              ถ่ายภาพหน้าบ้านที่ปิดเงียบ หรือสภาพของเก่าที่ไม่ตรง เพื่อให้ Admin พิจารณา
            </p>
          </div>

          {/* คำอธิบายเพิ่มเติม */}
          <div>
            <label className="text-xs font-medium text-gray-700 block mb-1">
              รายละเอียดเหตุการณ์เพิ่มเติม:
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="ระบุรายละเอียดเพิ่มเติม เช่น โทรติดต่อ 3 ครั้งแล้วไม่มีผู้รับสาย..."
              className="w-full p-2.5 border border-gray-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-red-500"
              data-testid="notes-textarea"
            />
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-xl p-2.5 text-[11px] text-amber-800">
            <span>ℹ️ เมื่อส่งรายงาน ระบบจะปลดล็อกงานนี้ออกจากคิวของคุณทันที เพื่อให้คุณเดินทางไปรับงานถัดไปได้</span>
          </div>

          {/* ปุ่มกดดำเนินการ (ทัชทาร์เก็ต >= 48px ตาม REQ-UX-001, CC-01) */}
          <div className="space-y-2 pt-1">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full min-h-[48px] bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-60"
              data-testid="submit-mismatch-btn"
            >
              {isSubmitting ? 'กำลังส่งรายงาน...' : '🚨 ยืนยันส่งรายงานข้อพิพาท (S8)'}
            </button>

            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="w-full min-h-[48px] bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl text-xs transition text-center"
              data-testid="cancel-modal-btn"
            >
              ยกเลิก
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

