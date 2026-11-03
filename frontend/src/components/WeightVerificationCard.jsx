import React, { useState } from "react";

/**
 * WeightVerificationCard Component
 * ตรวจสอบและกดยืนยันตัวเลขน้ำหนักชั่งจริงหน้างาน (100% Confirmation Gate)
 * รองรับ REQ-FN-004, REQ-FN-006, AC-S06-01, AC-S06-02, P-01, P-02, Q-01, Q-02
 */
export default function WeightVerificationCard({
  order,
  onConfirmWeights,
  onRequestReweigh,
  onRaiseDispute,
  isLoading = false,
}) {
  const [showReweighModal, setShowReweighModal] = useState(false);
  const [reweighReason, setReweighReason] = useState("");
  const [showDisputeModal, setShowDisputeModal] = useState(false);
  const [disputeReason, setDisputeReason] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const items = order?.items || [];
  const totalAmount = order?.total_settled_amount || 0;

  const handleReweighSubmit = (e) => {
    e.preventDefault();
    if (!reweighReason.trim()) {
      setErrorMsg("กรุณาระบุเหตุผลที่ขอให้ชั่งซ้ำ");
      return;
    }
    setErrorMsg("");
    onRequestReweigh(reweighReason);
    setShowReweighModal(false);
  };

  const handleDisputeSubmit = (e) => {
    e.preventDefault();
    if (!disputeReason.trim() || disputeReason.trim().length < 5) {
      setErrorMsg("กรุณาระบุเหตุผลข้อพิพาทอย่างน้อย 5 ตัวอักษร");
      return;
    }
    setErrorMsg("");
    onRaiseDispute(disputeReason);
    setShowDisputeModal(false);
  };

  return (
    <div
      className="bg-white rounded-2xl shadow-sm border border-emerald-100 p-5 mb-4"
      data-req="REQ-FN-004"
      data-testid="weight-verification-card"
    >
      {/* ส่วนหัวแสดงสถานะ S5 */}
      <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
        <div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 text-amber-700 rounded-full border border-amber-200">
            สถานะ S5: รอผู้ขายยืนยันน้ำหนัก
          </span>
          <h2 className="text-sm font-bold text-gray-800 mt-1.5">
            ⚖️ ตรวจสอบผลชั่งจริงหน้างาน
          </h2>
        </div>
        <div className="text-right">
          <span className="text-[11px] text-gray-400 block">รหัสคำขอ</span>
          <span className="text-xs font-mono font-medium text-gray-600">
            {order?.order_id?.slice(0, 8)}...
          </span>
        </div>
      </div>

      {/* รูปถ่ายหน้าตาชั่งดิจิทัล (REQ-FN-002) */}
      {order?.scale_photo_url && (
        <div className="mb-4 bg-gray-50 p-2.5 rounded-xl border border-gray-200">
          <span className="text-xs font-medium text-gray-600 block mb-1.5 flex items-center gap-1">
            📸 รูปถ่ายหน้าตาชั่งดิจิทัลจากซาเล้ง
          </span>
          <div className="relative rounded-lg overflow-hidden border border-gray-200 bg-black/5 aspect-video flex items-center justify-center">
            <img
              src={order.scale_photo_url}
              alt="ภาพหน้าตาชั่งดิจิทัล"
              className="object-cover w-full h-full"
              data-testid="scale-photo"
              onError={(e) => {
                e.target.style.display = "none";
                e.target.nextSibling.style.display = "block";
              }}
            />
            <div className="hidden text-xs text-gray-400 p-4 text-center">
              (รูปถ่ายหน้าตาชั่งดิจิทัล)
            </div>
          </div>
        </div>
      )}

      {/* ตารางเปรียบเทียบน้ำหนักประเมิน vs ชั่งจริง */}
      <div className="space-y-2 mb-4">
        <span className="text-xs font-semibold text-gray-700 block">
          รายการวัสดุและน้ำหนักที่ชั่งได้:
        </span>
        <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden">
          {items.map((item, idx) => (
            <div key={item.item_id || idx} className="p-3 bg-gray-50/50 flex justify-between items-center text-xs">
              <div>
                <span className="font-bold text-gray-800 block">
                  {item.category_name || item.category_code}
                </span>
                <span className="text-gray-500 text-[11px]">
                  ประเมินไว้: {item.est_quantity || "-"} {item.unit} | ราคาล็อก: {item.locked_unit_price} บ./{item.unit}
                </span>
              </div>
              <div className="text-right">
                <span className="font-extrabold text-emerald-700 text-sm block" data-testid={`actual-qty-${idx}`}>
                  {item.actual_quantity} {item.unit}
                </span>
                <span className="text-gray-500 font-medium text-[11px]">
                  = {(item.settled_item_price || item.actual_quantity * (item.locked_unit_price || 0)).toFixed(2)} บาท
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ยอดเงินสุทธิรวม */}
      <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3.5 mb-5 flex justify-between items-center">
        <div>
          <span className="text-xs text-emerald-900 block font-medium">ยอดเงินสุทธิคำนวณจากน้ำหนักจริง</span>
          <span className="text-[11px] text-emerald-700">อิงราคาที่ล็อกไว้ ณ เวลานัดหมาย (REQ-BR-002)</span>
        </div>
        <div className="text-right">
          <span className="text-lg font-black text-emerald-700" data-testid="total-settled-amount">
            {totalAmount.toFixed(2)}
          </span>
          <span className="text-xs font-bold text-emerald-800 ml-1">บาท</span>
        </div>
      </div>

      {/* ข้อความแจ้งเตือน Confirmation Gate 100% */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-2.5 mb-4 text-[11px] text-amber-800 flex items-start gap-1.5">
        <span className="text-amber-600 font-bold">⚠️</span>
        <span>
          <strong>กฎความโปร่งใส (REQ-FN-004):</strong> ระบบจะบล็อกการชำระเงินไว้ 100% จนกว่าผู้ขายจะตรวจสอบและกดยืนยันตัวเลขน้ำหนักจริงด้านล่าง
        </span>
      </div>

      {/* ปุ่มดำเนินการหลักและรอง */}
      <div className="space-y-2">
        <button
          type="button"
          onClick={onConfirmWeights}
          disabled={isLoading}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-4 rounded-xl text-xs transition duration-150 flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-50"
          data-testid="confirm-weights-btn"
        >
          <span>✅</span> กดยืนยันตัวเลขน้ำหนัก (เข้าสู่การชำระเงิน)
        </button>

        <div className="grid grid-cols-2 gap-2 pt-1" data-req="REQ-FN-006">
          <button
            type="button"
            onClick={() => setShowReweighModal(true)}
            disabled={isLoading}
            className="w-full bg-white hover:bg-gray-50 border border-gray-300 text-gray-700 font-medium py-2 px-3 rounded-xl text-xs transition duration-150 text-center"
            data-testid="request-reweigh-btn"
          >
            🔄 ขอให้ชั่งซ้ำ
          </button>
          <button
            type="button"
            onClick={() => setShowDisputeModal(true)}
            disabled={isLoading}
            className="w-full bg-white hover:bg-rose-50 border border-rose-200 text-rose-700 font-medium py-2 px-3 rounded-xl text-xs transition duration-150 text-center"
            data-testid="raise-dispute-btn"
          >
            🚫 ปฏิเสธ / แจ้งข้อพิพาท
          </button>
        </div>
      </div>

      {/* Modal ขอให้ชั่งซ้ำ */}
      {showReweighModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-xl border border-gray-100">
            <h3 className="text-sm font-bold text-gray-800 mb-2">🔄 ขอให้ซาเล้งตรวจสอบและชั่งใหม่</h3>
            <p className="text-xs text-gray-500 mb-3">
              ระบบจะส่งสัญญาณให้ซาเล้งตรวจสอบตาชั่งและแก้ไขค่าน้ำหนักจริงในระบบใหม่อีกครั้ง
            </p>
            {errorMsg && <p className="text-xs text-rose-600 mb-2">{errorMsg}</p>}
            <textarea
              value={reweighReason}
              onChange={(e) => setReweighReason(e.target.value)}
              placeholder="เช่น ตาชั่งน่าจะค้าง ขอยกของลงวางใหม่"
              rows={3}
              className="w-full text-xs border border-gray-200 rounded-xl p-2.5 mb-3 focus:outline-none focus:border-emerald-500"
              data-testid="reweigh-reason-input"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowReweighModal(false)}
                className="px-3 py-1.5 text-xs text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                ยกเลิก
              </button>
              <button
                type="button"
                onClick={handleReweighSubmit}
                className="px-3.5 py-1.5 text-xs bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium"
                data-testid="submit-reweigh-btn"
              >
                ยืนยันขอชั่งใหม่
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal แจ้งข้อพิพาท */}
      {showDisputeModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-sm w-full p-5 shadow-xl border border-rose-100">
            <h3 className="text-sm font-bold text-rose-700 mb-2">🚫 ปฏิเสธผลชั่ง / ส่งข้อพิพาท (REQ-FN-006)</h3>
            <p className="text-xs text-gray-500 mb-3">
              ระบบจะล็อกข้อมูลภาพถ่ายตาชั่ง พิกัด GPS และราคาที่ล็อกไว้ เพื่อส่งให้ผู้ดูแลระบบตรวจสอบข้อพิพาท
            </p>
            {errorMsg && <p className="text-xs text-rose-600 mb-2">{errorMsg}</p>}
            <textarea
              value={disputeReason}
              onChange={(e) => setDisputeReason(e.target.value)}
              placeholder="ระบุเหตุผลในการปฏิเสธผลชั่งจริง..."
              rows={3}
              className="w-full text-xs border border-gray-200 rounded-xl p-2.5 mb-3 focus:outline-none focus:border-rose-500"
              data-testid="dispute-reason-input"
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowDisputeModal(false)}
                className="px-3 py-1.5 text-xs text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                ยกเลิก
              </button>
              <button
                type="button"
                onClick={handleDisputeSubmit}
                className="px-3.5 py-1.5 text-xs bg-rose-600 text-white rounded-lg hover:bg-rose-700 font-medium"
                data-testid="submit-dispute-btn"
              >
                ส่งข้อพิพาทให้ Admin
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

