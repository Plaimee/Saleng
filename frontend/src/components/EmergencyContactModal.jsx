import React, { useState, useEffect } from "react";

/**
 * หน้าต่างตั้งค่าเบอร์ผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (AC-S09-03, REQ-SEC-002, P-03, Q-03, UC-09)
 */
export default function EmergencyContactModal({
  isOpen,
  onClose,
  currentContact,
  onSaveContact,
}) {
  const [contactName, setContactName] = useState("");
  const [relationship, setRelationship] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (currentContact) {
      setContactName(currentContact.contact_name || "");
      setRelationship(currentContact.relationship || "");
      setContactPhone("");
    }
  }, [currentContact, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!contactName.trim() || !relationship.trim() || !contactPhone.trim()) {
      setErrorMsg("กรุณากรอกข้อมูลให้ครบทุกช่อง");
      return;
    }
    if (!/^0\d{8,9}$/.test(contactPhone.trim())) {
      setErrorMsg("เบอร์โทรศัพท์ต้องขึ้นต้นด้วย 0 และยาว 9-10 หลัก");
      return;
    }

    setErrorMsg("");
    setIsSubmitting(true);
    try {
      await onSaveContact({
        contact_name: contactName.trim(),
        relationship: relationship.trim(),
        contact_phone: contactPhone.trim(),
      });
      onClose();
    } catch (err) {
      setErrorMsg(err.message || "บันทึกข้อมูลไม่สำเร็จ");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      data-req="UC-09"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 animate-fade-in"
    >
      <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl">
        <div className="bg-emerald-600 text-white p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🛡️</span>
            <h2 className="font-bold text-base">ตั้งค่าเบอร์ติดต่อฉุกเฉิน</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white/80 hover:text-white text-xl font-bold p-1"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          {/* ข้อมูลปัจจุบัน */}
          {currentContact && (
            <div className="bg-gray-50 p-2.5 rounded-xl border text-xs space-y-1">
              <span className="text-gray-500 font-medium">เบอร์ฉุกเฉินปัจจุบัน:</span>
              <div className="flex justify-between items-center text-gray-800 font-semibold">
                <span>{currentContact.contact_name}</span>
                <span className="font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  {currentContact.contact_phone_masked}
                </span>
              </div>
            </div>
          )}

          {errorMsg && (
            <div className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl">
              ⚠️ {errorMsg}
            </div>
          )}

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-700">ชื่อผู้ติดต่อที่ไว้ใจได้</label>
            <input
              type="text"
              value={contactName}
              onChange={(e) => setContactName(e.target.value)}
              placeholder="เช่น นายสมบูรณ์ มีสุข"
              className="w-full px-3 py-2 border rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-700">ความสัมพันธ์</label>
            <input
              type="text"
              value={relationship}
              onChange={(e) => setRelationship(e.target.value)}
              placeholder="เช่น บุตร, ญาติ, เพื่อนบ้าน"
              className="w-full px-3 py-2 border rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-700">เบอร์โทรศัพท์ติดต่อ (10 หลัก)</label>
            <input
              type="tel"
              value={contactPhone}
              onChange={(e) => setContactPhone(e.target.value)}
              placeholder="08xxxxxxxx"
              className="w-full px-3 py-2 border rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none font-mono"
            />
            <p className="text-[11px] text-gray-400">
              * ข้อมูลเบอร์โทรจะถูกปกปิด (PDPA Masking) ตามมาตรฐานความปลอดภัย
            </p>
          </div>

          <div className="pt-2 flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl text-sm"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-sm shadow disabled:opacity-50"
            >
              {isSubmitting ? "กำลังบันทึก..." : "บันทึกข้อมูล"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

