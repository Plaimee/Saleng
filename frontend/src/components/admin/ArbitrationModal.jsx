import React, { useState } from 'react';

/**
 * Modal สำหรับแอดมินตัดสินชี้ขาดข้อพิพาทหน้างาน (UC-13, D-A03-01, D-A03-05)
 * - RESOLVE_COMPLETE: ตัดสินให้จบงาน (S7) พร้อมยอดเงินชี้ขาดสุทธิ (บาท) และออกใบเสร็จ
 * - RESOLVE_CANCEL: ตัดสินให้ยกเลิกคำขอ (S9) ไม่มีการชำระเงิน
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม (REQ-UX-001, CC-01)
 */
export default function ArbitrationModal({
  dispute,
  isOpen = false,
  onClose,
  onSubmit,
  isLoading = false,
}) {
  const [action, setAction] = useState('RESOLVE_COMPLETE');
  const [arbitratedAmount, setArbitratedAmount] = useState(
    dispute?.re_quoted_price || dispute?.saleng_verification?.re_quoted_price || ''
  );
  const [arbitrationNote, setArbitrationNote] = useState('');
  const [error, setError] = useState('');

  if (!isOpen || !dispute) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (action === 'RESOLVE_COMPLETE') {
      const amount = Number(arbitratedAmount);
      if (!arbitratedAmount || isNaN(amount) || amount <= 0) {
        setError('กรุณากรอกยอดเงินชี้ขาดสุทธิที่ถูกต้อง (มากกว่า 0 บาท)');
        return;
      }
      onSubmit({
        action: 'RESOLVE_COMPLETE',
        arbitrated_amount: amount,
        arbitration_note: arbitrationNote || 'ตัดสินชี้ขาดให้ปิดงานตามยอดที่ระบุ',
      });
    } else {
      if (!arbitrationNote || !arbitrationNote.trim()) {
        setError('กรุณากรอกเหตุผลการยกเลิกคำขอ');
        return;
      }
      onSubmit({
        action: 'RESOLVE_CANCEL',
        arbitrated_amount: null,
        arbitration_note: arbitrationNote.trim(),
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 max-w-lg w-full overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/80">
          <div>
            <h3 className="text-base font-bold text-gray-800">ตัดสินชี้ขาดข้อพิพาทหน้างาน</h3>
            <p className="text-xs text-gray-500 font-mono mt-0.5">{dispute.dispute_id}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="min-h-[48px] min-w-[48px] flex items-center justify-center text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition"
            aria-label="ปิดหน้าต่าง"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 font-medium">
              {error}
            </div>
          )}

          {/* สรุปข้อพิพาท */}
          <div className="p-3.5 bg-amber-50/70 border border-amber-200/80 rounded-xl text-xs space-y-1">
            <div className="font-semibold text-amber-900">เหตุผลข้อโต้แย้งของผู้ขาย:</div>
            <div className="text-amber-800">{dispute.dispute_reason}</div>
          </div>

          {/* ทางเลือกคำตัดสิน */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2">เลือกแนวทางการตัดสินชี้ขาด</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setAction('RESOLVE_COMPLETE')}
                className={`min-h-[48px] px-3 py-2.5 rounded-xl border text-xs font-medium transition flex flex-col items-center justify-center gap-1 ${
                  action === 'RESOLVE_COMPLETE'
                    ? 'border-emerald-600 bg-emerald-50/60 text-emerald-800 font-semibold ring-2 ring-emerald-500/20'
                    : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <span>ปิดงาน (จบงาน S7)</span>
                <span className="text-[10px] text-emerald-600 font-normal">ออกใบเสร็จดิจิทัล</span>
              </button>

              <button
                type="button"
                onClick={() => setAction('RESOLVE_CANCEL')}
                className={`min-h-[48px] px-3 py-2.5 rounded-xl border text-xs font-medium transition flex flex-col items-center justify-center gap-1 ${
                  action === 'RESOLVE_CANCEL'
                    ? 'border-red-600 bg-red-50/60 text-red-800 font-semibold ring-2 ring-red-500/20'
                    : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <span>สั่งยกเลิก (S9)</span>
                <span className="text-[10px] text-red-600 font-normal">ไม่มีการจ่ายเงิน</span>
              </button>
            </div>
          </div>

          {/* ฟิลด์ตาม Action */}
          {action === 'RESOLVE_COMPLETE' ? (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  ยอดเงินสุทธิที่ตัดสินชี้ขาด (บาท) <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 font-mono text-sm">฿</span>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    value={arbitratedAmount}
                    onChange={(e) => setArbitratedAmount(e.target.value)}
                    placeholder="เช่น 210.00"
                    className="w-full pl-8 pr-3 py-2.5 min-h-[48px] border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    required
                  />
                </div>
                <p className="text-[11px] text-gray-400 mt-1">
                  ระบบจะบันทึกเป็นยอดเงินชำระสุทธิ และออกใบเสร็จดิจิทัลตามยอดนี้ทันที
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">หมายเหตุคำตัดสิน</label>
                <textarea
                  rows="2"
                  value={arbitrationNote}
                  onChange={(e) => setArbitrationNote(e.target.value)}
                  placeholder="เช่น ตัดสินตามราคาชั่งจริงหน้างาน หรือ ยอดประนีประนอม"
                  className="w-full p-2.5 text-xs border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">
                เหตุผลการสั่งยกเลิกคำขอ <span className="text-red-500">*</span>
              </label>
              <textarea
                rows="3"
                value={arbitrationNote}
                onChange={(e) => setArbitrationNote(e.target.value)}
                placeholder="ระบุเหตุผลการยกเลิก เช่น สินค้าปนเปื้อนสารเคมีอันตราย หรือ คู่กรณีตกลงยกเลิกการซื้อขาย"
                className="w-full p-2.5 text-xs border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500"
                required
              />
              <p className="text-[11px] text-gray-400 mt-1">
                คำขอจะถูกเปลี่ยนสถานะเป็น S9 (Cancelled) โดยไม่มีการทำธุรกรรมการเงิน
              </p>
            </div>
          )}

          {/* ปุ่มยืนยัน / ยกเลิก */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="min-h-[48px] px-5 py-2.5 border border-gray-300 text-gray-600 rounded-xl text-xs font-medium hover:bg-gray-50 transition"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className={`min-h-[48px] px-6 py-2.5 rounded-xl text-white text-xs font-semibold shadow-sm transition active:scale-95 disabled:opacity-50 ${
                action === 'RESOLVE_COMPLETE'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-red-600 hover:bg-red-700'
              }`}
            >
              {isLoading ? 'กำลังบันทึก...' : 'ยืนยันคำตัดสิน'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

