import React from 'react';

/**
 * ReadOnlyNoticeBanner Component
 * แบนเนอร์แจ้งเตือนห้องแชตล็อกเป็น Read-only เมื่อคำขอเข้าสู่สถานะ S7 (สำเร็จ) หรือ S8 (ยกเลิก)
 * คุ้มครองสิทธิความเป็นส่วนตัวตามกฎหมาย PDPA (MD-STM-04, REQ-SEC-002, AC-B05-05, D-B05-05)
 */
export default function ReadOnlyNoticeBanner({
  reason = 'การทำธุรกรรมเสร็จสิ้นแล้ว ห้องแชตถูกปิดเพื่อความปลอดภัยของข้อมูลส่วนบุคคลตามกฎหมาย PDPA',
}) {
  return (
    <div
      data-testid="read-only-banner"
      className="bg-amber-50 border-t border-b border-amber-200 px-4 py-3 flex items-start gap-2.5 text-amber-900 text-xs shadow-inner"
    >
      <span className="text-base leading-none">🔒</span>
      <div className="flex-1 leading-relaxed">
        <p className="font-semibold">ห้องแชตนี้อยู่ในโหมดอ่านอย่างเดียว (Read-only)</p>
        <p className="text-amber-700 mt-0.5">{reason}</p>
      </div>
    </div>
  );
}

