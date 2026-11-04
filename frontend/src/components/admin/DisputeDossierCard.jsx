import React, { useState } from 'react';

/**
 * การ์ดแสดงรายการข้อพิพาทและชุดสำนวนหลักฐาน 4 มิติ (Dispute Dossier)
 * รองรับ UC-13, REQ-FN-005, REQ-FN-004, D-A03-04, REQ-UX-001, CC-01, CC-06
 * ทัชทาร์เก็ตปุ่มกด >= 48px ทุกปุ่ม
 */
export default function DisputeDossierCard({
  dispute,
  dossier,
  onOpenArbitration,
  onFetchDossier,
  isLoading = false,
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    if (!isExpanded && !dossier && onFetchDossier) {
      onFetchDossier(dispute.dispute_id);
    }
    setIsExpanded(!isExpanded);
  };

  const isResolved = dispute.status === 'RESOLVED_COMPLETED' || dispute.status === 'RESOLVED_CANCELLED';
  const effectiveDossier = dossier || dispute;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition hover:shadow-md">
      {/* ส่วนหัวการ์ดข้อพิพาท */}
      <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gray-50/50">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-sm font-bold text-gray-900">{dispute.dispute_id}</span>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                dispute.status === 'PENDING_ADMIN'
                  ? 'bg-amber-100 text-amber-800'
                  : dispute.status === 'RESOLVED_COMPLETED'
                  ? 'bg-emerald-100 text-emerald-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {dispute.status === 'PENDING_ADMIN'
                ? 'รอดำเนินการ (S8)'
                : dispute.status === 'RESOLVED_COMPLETED'
                ? 'ปิดงานแล้ว (S7)'
                : 'ยกเลิกแล้ว (S9)'}
            </span>
            <span className="text-xs text-gray-400 font-mono">คำขอ: {dispute.order_id}</span>
          </div>

          <p className="text-sm text-gray-700 font-medium line-clamp-2">
            <span className="font-semibold text-gray-900">ข้อโต้แย้ง: </span>
            {dispute.dispute_reason}
          </p>

          <div className="flex items-center gap-4 text-xs text-gray-500 pt-1">
            <span>ผู้ขาย: <strong className="text-gray-700">{dispute.seller_name || dispute.seller_id}</strong></span>
            <span>ซาเล้ง: <strong className="text-gray-700">{dispute.buyer_name || dispute.buyer_id}</strong></span>
            {dispute.re_quoted_price && (
              <span className="text-emerald-700 font-medium">
                ราคาเสนอใหม่: ฿{dispute.re_quoted_price}
              </span>
            )}
          </div>
        </div>

        {/* ปุ่มแอ็กชัน */}
        <div className="flex items-center gap-2 self-start md:self-center">
          <button
            type="button"
            onClick={toggleExpand}
            className="min-h-[48px] px-4 py-2 border border-gray-300 rounded-lg text-xs font-medium text-gray-700 hover:bg-gray-100 active:scale-95 transition"
          >
            {isExpanded ? 'ย่อสำนวน' : 'ดูสำนวนหลักฐาน'}
          </button>

          {!isResolved && (
            <button
              type="button"
              onClick={() => onOpenArbitration && onOpenArbitration(effectiveDossier)}
              disabled={isLoading}
              className="min-h-[48px] px-5 py-2 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-semibold rounded-lg shadow-sm transition disabled:opacity-50"
            >
              ตัดสินชี้ขาด
            </button>
          )}
        </div>
      </div>

      {/* ส่วนขยายแสดงสำนวนหลักฐาน 4 มิติ */}
      {isExpanded && (
        <div className="p-5 border-t border-gray-100 bg-white space-y-5 animate-in fade-in duration-150">
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">
            ชุดสำนวนหลักฐานประกอบการตัดสิน 4 มิติ (Dispute Dossier)
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* มิติ 1: ข้อมูลคำขอเดิม & Price Snapshot */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200/80 space-y-2 text-xs">
              <div className="font-bold text-gray-800 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                มิติ 1: คำขอเดิม & Price Snapshot
              </div>
              <div className="space-y-1 text-gray-600">
                <div>ช่วงราคาประเมินเดิม: <strong className="text-gray-800">฿{effectiveDossier.original_order?.total_est_min_price || 0} – ฿{effectiveDossier.original_order?.total_est_max_price || 0}</strong></div>
                <div>น้ำหนักประเมินรวม: <strong className="text-gray-800">{effectiveDossier.original_order?.total_est_weight_kg || 0} กก.</strong></div>
                {effectiveDossier.original_order?.price_snapshot && (
                  <div className="mt-2 p-2 bg-white rounded border border-gray-200">
                    <span className="font-semibold text-gray-700">Price Snapshot ที่ล็อกไว้:</span>
                    <pre className="text-[10px] text-gray-500 mt-1 overflow-x-auto">
                      {JSON.stringify(effectiveDossier.original_order.price_snapshot, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {/* มิติ 2: ข้อมูลหน้างานจากซาเล้ง (ภาพตาชั่ง REQ-FN-005) */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200/80 space-y-2 text-xs">
              <div className="font-bold text-gray-800 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                มิติ 2: ข้อมูลหน้างานจากซาเล้ง
              </div>
              <div className="space-y-1 text-gray-600">
                <div>ยอดเสนอใหม่: <strong className="text-emerald-700">฿{effectiveDossier.saleng_verification?.re_quoted_price || effectiveDossier.re_quoted_price || 'ไม่มี'}</strong></div>
                {effectiveDossier.saleng_verification?.scale_photo_url && (
                  <div className="mt-2">
                    <span className="font-semibold text-gray-700 block mb-1">ภาพถ่ายหน้าตาชั่งดิจิทัล:</span>
                    <div className="relative rounded-lg overflow-hidden border border-gray-200 bg-gray-100 max-h-36 flex items-center justify-center">
                      <img
                        src={effectiveDossier.saleng_verification.scale_photo_url}
                        alt="ภาพหน้าตาชั่งดิจิทัล"
                        className="object-cover h-36 w-full"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <span className="text-[10px] text-gray-400 p-2">หลักฐานภาพถ่ายหน้าตาชั่งดิจิทัล</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* มิติ 3: ข้อมูลข้อโต้แย้งจากผู้ขาย */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200/80 space-y-2 text-xs">
              <div className="font-bold text-gray-800 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                มิติ 3: ข้อโต้แย้งจากผู้ขาย
              </div>
              <div className="space-y-1 text-gray-600">
                <div className="p-2 bg-amber-50 rounded border border-amber-200/60 text-amber-900">
                  {effectiveDossier.seller_dispute?.dispute_reason || effectiveDossier.dispute_reason}
                </div>
              </div>
            </div>

            {/* มิติ 4: ข้อมูลคู่กรณี (PDPA Masked CC-06) */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200/80 space-y-2 text-xs">
              <div className="font-bold text-gray-800 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                มิติ 4: ข้อมูลติดต่อคู่กรณี (PDPA Masking)
              </div>
              <div className="space-y-2 text-gray-600">
                <div className="flex justify-between items-center p-2 bg-white rounded border border-gray-200">
                  <span>ผู้ขาย: <strong className="text-gray-800">{effectiveDossier.parties_contact?.seller?.name || 'ผู้ขาย'}</strong></span>
                  <span className="font-mono text-gray-500">{effectiveDossier.parties_contact?.seller?.phone_masked || '08X-XXX-XXXX'}</span>
                </div>
                <div className="flex justify-between items-center p-2 bg-white rounded border border-gray-200">
                  <span>ซาเล้ง: <strong className="text-gray-800">{effectiveDossier.parties_contact?.buyer?.name || 'ซาเล้ง'}</strong></span>
                  <span className="font-mono text-gray-500">{effectiveDossier.parties_contact?.buyer?.phone_masked || '08X-XXX-XXXX'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* แถบผลการตัดสินกรณีตัดสินไปแล้ว */}
          {isResolved && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-1">
              <div className="font-bold text-emerald-900">บันทึกคำตัดสินชี้ขาดของแอดมิน:</div>
              <div className="text-emerald-800">
                ผลการตัดสิน: <strong>{dispute.status === 'RESOLVED_COMPLETED' ? 'ปิดงานสำเร็จ (S7)' : 'ยกเลิกคำขอ (S9)'}</strong>
                {dispute.arbitrated_amount && <span> | ยอดเงินชี้ขาดสุทธิ: ฿{dispute.arbitrated_amount}</span>}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

