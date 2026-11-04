import React from 'react';

/**
 * ChatHeader Component
 * ส่วนหัวห้องแชต แสดงชื่อผู้ขาย ป้ายสถานะคำขอ และปุ่มโทรด่วน (Native Quick Call tel:)
 * ทัชทาร์เก็ตปุ่มกดขนาดใหญ่ >= 48px ตาม REQ-UX-001, CC-01
 * ควบคุม PDPA ตาม REQ-SEC-002, D-B05-01, D-B05-02, D-B05-05
 */
export default function ChatHeader({
  orderId,
  orderStatus = 'S3',
  sellerName = 'ผู้ขาย',
  sellerPhone = null,
  phoneMasked = true,
  onBack,
  onCallClick,
}) {
  const isPostTransaction = orderStatus === 'S7' || orderStatus === 'S8';
  const isPreClaimS2 = orderStatus === 'S2';
  const canCall = !isPostTransaction && !isPreClaimS2 && sellerPhone && !phoneMasked;

  const handleCall = (e) => {
    if (onCallClick && sellerPhone) {
      onCallClick(sellerPhone);
    }
  };

  const getStatusBadge = () => {
    switch (orderStatus) {
      case 'S2':
        return <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-medium">S2: สอบถามก่อนรับงาน</span>;
      case 'S3':
        return <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-medium">S3: รับงานแล้ว</span>;
      case 'S4':
        return <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium">S4: กำลังเดินทาง</span>;
      case 'S5':
        return <span className="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full font-medium">S5: กำลังชั่งของ</span>;
      case 'S6':
        return <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-full font-medium">S6: ชำระเงิน</span>;
      case 'S7':
        return <span className="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full font-medium">S7: สำเร็จ/ปิดงาน</span>;
      case 'S8':
        return <span className="text-xs bg-rose-100 text-rose-700 px-2 py-0.5 rounded-full font-medium">S8: ยกเลิก</span>;
      default:
        return <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">{orderStatus}</span>;
    }
  };

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-slate-200 px-3 py-2.5 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-2">
        {onBack && (
          <button
            type="button"
            onClick={onBack}
            data-testid="chat-back-btn"
            aria-label="ย้อนกลับ"
            className="min-h-[48px] min-w-[48px] flex items-center justify-center rounded-xl text-slate-600 hover:bg-slate-100 active:scale-95 transition-transform"
          >
            <span className="text-xl">←</span>
          </button>
        )}
        <div>
          <div className="flex items-center gap-1.5">
            <h1 className="text-base font-bold text-slate-800 leading-tight" data-testid="chat-seller-name">
              {sellerName}
            </h1>
            {getStatusBadge()}
          </div>
          <p className="text-xs text-slate-500 mt-0.5" data-testid="chat-order-id">
            ใบงาน: {orderId}
          </p>
        </div>
      </div>

      {/* ปุ่มโทรด่วน Native Quick Call */}
      {!isPostTransaction && (
        <div className="flex items-center">
          {canCall ? (
            <a
              href={`tel:${sellerPhone}`}
              onClick={handleCall}
              data-testid="quick-call-btn"
              className="min-h-[48px] px-3.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl flex items-center gap-1.5 font-semibold text-sm shadow-sm active:scale-95 transition-all"
            >
              <span className="text-base">📞</span>
              <span>โทรหาผู้ขาย</span>
            </a>
          ) : isPreClaimS2 ? (
            <button
              type="button"
              disabled
              data-testid="quick-call-btn-disabled"
              title="รับงานก่อนจึงจะสามารถโทรหาผู้ขายได้"
              className="min-h-[48px] px-3 bg-slate-100 text-slate-400 rounded-xl flex items-center gap-1 text-xs font-medium cursor-not-allowed border border-slate-200"
            >
              <span>🔒</span>
              <span>รับงานก่อนโทร</span>
            </button>
          ) : null}
        </div>
      )}
    </header>
  );
}

