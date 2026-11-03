import React, { useState } from "react";
import { submitSupportTicket } from "../services/notificationHelpApi";

/**
 * SupportTicketModal Component
 * แบบฟอร์มส่งคำร้องขอความช่วยเหลือ และการ์ดข้อมูลสายด่วน Call Center / LINE Official
 * รองรับ UC-08, UC-13, REQ-SEC-002, AC-S08-04, P-04, Q-04
 */
export default function SupportTicketModal({
  isOpen = true,
  onClose,
  sellerId = "SELLER-001",
  onTicketSubmitted,
}) {
  const [category, setCategory] = useState("BOOKING");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [submittedTicket, setSubmittedTicket] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (subject.length < 3) {
      setErrorMsg("กรุณากรอกหัวข้อปัญหาอย่างน้อย 3 ตัวอักษร");
      return;
    }
    if (description.length < 10) {
      setErrorMsg("กรุณากรอกรายละเอียดปัญหาอย่างน้อย 10 ตัวอักษร");
      return;
    }
    if (contactPhone.length < 9) {
      setErrorMsg("กรุณากรอกเบอร์โทรศัพท์สำหรับติดต่อกลับ");
      return;
    }

    setSubmitting(true);
    setErrorMsg("");

    try {
      const ticket = await submitSupportTicket(sellerId, {
        category,
        subject,
        description,
        contactPhone,
      });
      setSubmittedTicket(ticket);
      if (onTicketSubmitted) onTicketSubmitted(ticket);
    } catch (err) {
      setErrorMsg(err.message || "เกิดข้อผิดพลาดในการส่งคำร้อง");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      data-testid="support-ticket-modal"
      data-req="UC-13"
    >
      <div className="bg-white w-full max-w-sm rounded-3xl p-5 shadow-2xl border border-gray-100 max-h-[90vh] overflow-y-auto">
        {submittedTicket ? (
          <div className="py-6 text-center">
            <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-3 text-3xl">
              ✓
            </div>
            <h3 className="text-base font-bold text-gray-800 mb-1">
              ส่งคำร้องขอความช่วยเหลือเรียบร้อย
            </h3>
            <span
              className="text-xs font-mono font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200 inline-block mb-3"
              data-testid="ticket-no-badge"
            >
              {submittedTicket.ticket_no}
            </span>
            <p className="text-xs text-gray-500 mb-4 px-2">
              เจ้าหน้าที่ศูนย์ดูแลระบบจะติดต่อกลับไปยังเบอร์{" "}
              <span className="font-mono font-semibold" data-testid="ticket-masked-phone">
                {submittedTicket.contact_phone_masked}
              </span>{" "}
              ภายในเวลาทำการ
            </p>
            <button
              onClick={onClose}
              data-testid="close-ticket-success-btn"
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-2xl shadow-md text-xs transition-all"
            >
              ตกลง / ปิดหน้าต่าง
            </button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="flex justify-between items-center pb-2.5 border-b border-gray-100 mb-3">
              <h2 className="text-base font-bold text-gray-800">
                ติดต่อฝ่ายดูแลลูกค้า (Support)
              </h2>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-lg leading-none p-1"
                data-testid="close-ticket-modal-btn"
              >
                ✕
              </button>
            </div>

            {/* Hotline Contact Info Card (Q-04) */}
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-3 border border-emerald-100 mb-4 text-xs">
              <div className="font-bold text-emerald-900 mb-1 flex items-center gap-1.5">
                <span>📞</span>
                <span>สายด่วนช่วยเหลือทันใจ:</span>
              </div>
              <div className="text-emerald-800 space-y-0.5">
                <div>เบอร์โทร: <span className="font-bold font-mono">02-123-4567</span></div>
                <div className="text-[11px] text-emerald-700">เวลาทำการ: ทุกวัน 08:00 - 18:00 น.</div>
                <div>LINE Official: <span className="font-bold font-mono">@saleng-help</span></div>
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  หมวดหมู่ปัญหา
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  data-testid="ticket-category-select"
                  className="w-full text-xs p-2.5 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="BOOKING">การนัดหมายและเวลารถรับซื้อ</option>
                  <option value="WEIGHING">การชั่งน้ำหนักและข้อพิพาทตาชั่ง</option>
                  <option value="PAYMENT">การชำระเงินและใบเสร็จดิจิทัล</option>
                  <option value="APP_ISSUE">ปัญหาการใช้งานแอปพลิเคชัน</option>
                  <option value="OTHER">ข้อเสนอแนะหรือปัญหาอื่น ๆ</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  หัวข้อเรื่อง
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="เช่น ซาเล้งยังไม่มาตามนัดหมาย"
                  data-testid="ticket-subject-input"
                  maxLength={150}
                  className="w-full text-xs p-2.5 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  รายละเอียดปัญหา
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="อธิบายรายละเอียดปัญหาที่พบอย่างน้อย 10 ตัวอักษร..."
                  data-testid="ticket-description-input"
                  rows={3}
                  maxLength={1000}
                  className="w-full text-xs p-2.5 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  เบอร์โทรติดต่อกลับ
                </label>
                <input
                  type="tel"
                  value={contactPhone}
                  onChange={(e) => setContactPhone(e.target.value)}
                  placeholder="08X-XXX-XXXX"
                  data-testid="ticket-phone-input"
                  maxLength={15}
                  className="w-full text-xs p-2.5 rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono"
                />
                <span className="text-[10px] text-gray-400 mt-0.5 block">
                  * ข้อมูลเบอร์โทรจะถูกปกปิดตามมาตรฐาน PDPA (REQ-SEC-002)
                </span>
              </div>

              {errorMsg && (
                <div
                  className="bg-red-50 text-red-600 text-xs p-2.5 rounded-xl border border-red-200"
                  data-testid="ticket-error-msg"
                >
                  {errorMsg}
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                data-testid="submit-ticket-btn"
                data-req="UC-13"
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-semibold rounded-2xl shadow-md text-xs transition-all"
              >
                {submitting ? "กำลังส่งคำร้อง..." : "ส่งคำร้องขอความช่วยเหลือ"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

