import React from "react";

/**
 * หน้าต่างยืนยันการส่งสัญญาณฉุกเฉินและต่อสายตรง (AC-S09-02, P-02, Q-02, UC-09)
 */
export default function SosConfirmationModal({
  isOpen,
  onClose,
  sosData,
  onCallPhone,
}) {
  if (!isOpen || !sosData) return null;

  const phoneToCall = sosData.emergency_phone_to_call || "02-123-4567";
  const contactName = sosData.emergency_contact_name || "ศูนย์ช่วยเหลือ Saleng";
  const geoPoint = sosData.geo_point || { lat: 13.7563, lng: 100.5018 };

  const handleCall = () => {
    if (onCallPhone) {
      onCallPhone(phoneToCall);
    } else {
      window.location.href = `tel:${phoneToCall}`;
    }
  };

  const handleCallPolice = () => {
    if (onCallPhone) {
      onCallPhone("191");
    } else {
      window.location.href = "tel:191";
    }
  };

  return (
    <div
      data-req="UC-09"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 animate-fade-in"
    >
      <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl border-4 border-red-500">
        {/* Header แถบสีแดง */}
        <div className="bg-red-600 text-white p-4 text-center">
          <div className="text-3xl mb-1">🚨</div>
          <h2 className="text-xl font-bold">แจ้งเหตุฉุกเฉิน SOS สำเร็จ</h2>
          <p className="text-xs text-red-100 mt-1">
            รหัสแจ้งเหตุ: {sosData.sos_id || "SOS-ALERT"}
          </p>
        </div>

        {/* รายละเอียด */}
        <div className="p-4 space-y-4">
          <div className="bg-red-50 p-3 rounded-xl border border-red-200 text-sm text-red-900 space-y-1">
            <div className="font-semibold flex items-center gap-1.5">
              <span>📍</span>
              <span>ส่งพิกัดบ้านและข้อมูลซาเล้งไปยังศูนย์ Admin แล้ว</span>
            </div>
            <p className="text-xs text-gray-600">
              พิกัด: {geoPoint.lat.toFixed(4)}, {geoPoint.lng.toFixed(4)}
            </p>
            <p className="text-xs text-gray-600">
              สถานะ: ได้รับเรื่องแล้ว (ใช้เวลา {sosData.response_time_ms || 150} ms)
            </p>
          </div>

          <div className="bg-amber-50 p-3 rounded-xl border border-amber-200 text-xs text-amber-800">
            🔒 ระบบได้ทำการล็อกหลักฐานเสียง/วิดีโอของคำขอนี้เพื่อใช้ตรวจสอบแล้ว (ห้ามลบ/แก้ไข)
          </div>

          {/* ปุ่มโทรออกด่วน */}
          <div className="space-y-2 pt-1">
            <button
              type="button"
              onClick={handleCall}
              className="w-full min-h-[48px] py-3 px-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow flex items-center justify-center gap-2 active:scale-95 transition-all text-sm"
            >
              <span>📞</span>
              <span>โทรหาผู้ติดต่อฉุกเฉิน: {contactName}</span>
            </button>

            <button
              type="button"
              onClick={handleCallPolice}
              className="w-full min-h-[44px] py-2.5 px-4 bg-red-700 hover:bg-red-800 text-white font-semibold rounded-xl flex items-center justify-center gap-2 text-sm"
            >
              <span>👮</span>
              <span>โทรแจ้งเหตุด่วน 191</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-4 py-3 border-t flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-xl text-sm"
          >
            รับทราบและปิดหน้าต่าง
          </button>
        </div>
      </div>
    </div>
  );
}

