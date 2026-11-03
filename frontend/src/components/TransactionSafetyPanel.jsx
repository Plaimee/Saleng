import React, { useState, useEffect } from "react";
import EmergencySosButton from "./EmergencySosButton.jsx";
import SosConfirmationModal from "./SosConfirmationModal.jsx";
import MediaEvidenceRecorder from "./MediaEvidenceRecorder.jsx";
import EmergencyContactModal from "./EmergencyContactModal.jsx";
import {
  fetchEmergencyContact,
  saveEmergencyContact,
  triggerEmergencySos,
  uploadSafetyEvidence,
  fetchSafetyEvidences,
} from "../services/safetyApi.js";

/**
 * แผงควบคุมความปลอดภัยขณะทำธุรกรรม (Transaction Safety Panel - UC-09, AC-S09-01..05)
 */
export default function TransactionSafetyPanel({
  orderId,
  sellerId,
  orderStatus = "S5",
}) {
  const [contact, setContact] = useState(null);
  const [evidences, setEvidences] = useState([]);
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [isSosModalOpen, setIsSosModalOpen] = useState(false);
  const [sosResult, setSosResult] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");

  // โหลดข้อมูลเบอร์ติดต่อและหลักฐาน
  useEffect(() => {
    if (sellerId) {
      fetchEmergencyContact(sellerId).then(setContact).catch(() => {});
    }
    if (orderId && sellerId) {
      fetchSafetyEvidences(orderId, sellerId)
        .then((res) => setEvidences(res.evidences || []))
        .catch(() => {});
    }
  }, [orderId, sellerId]);

  // จัดการกด SOS
  const handleTriggerSos = async () => {
    try {
      setStatusMessage("กำลังส่งสัญญาณแจ้งเหตุฉุกเฉิน SOS...");
      const res = await triggerEmergencySos(orderId, sellerId);
      setSosResult(res);
      setIsSosModalOpen(true);
      setStatusMessage("");
      // รีเฟรชหลักฐานที่ถูกล็อก
      fetchSafetyEvidences(orderId, sellerId).then((r) => setEvidences(r.evidences || []));
    } catch (err) {
      setStatusMessage(`แจ้งเหตุฉุกเฉินล้มเหลว: ${err.message}`);
    }
  };

  // จัดการอัปโหลดหลักฐาน
  const handleUploadEvidence = async ({ media_type, duration_seconds, file_size_bytes }) => {
    try {
      const created = await uploadSafetyEvidence(orderId, sellerId, {
        media_type,
        duration_seconds,
        file_size_bytes,
      });
      setEvidences((prev) => [...prev, created]);
    } catch (err) {
      alert(`บันทึกหลักฐานไม่สำเร็จ: ${err.message}`);
    }
  };

  // จัดการบันทึกเบอร์ติดต่อฉุกเฉิน
  const handleSaveContact = async (contactPayload) => {
    const updated = await saveEmergencyContact(sellerId, contactPayload);
    setContact(updated);
  };

  // ปิดปุ่มหากสถานะไม่อยู่ใน S3..S6
  const isSosEnabled = ["S3", "S4", "S5", "S6"].includes(orderStatus);
  const isEvidenceEnabled = ["S4", "S5", "S6"].includes(orderStatus);

  return (
    <div
      data-req="UC-09"
      className="bg-red-50/50 rounded-2xl border-2 border-red-200 p-4 space-y-4 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-red-900 font-bold text-sm">
          <span>🛡️</span>
          <span>ความปลอดภัยขณะทำธุรกรรม (UC-09)</span>
        </div>
        <button
          type="button"
          onClick={() => setIsContactModalOpen(true)}
          className="text-xs text-emerald-700 bg-white border border-emerald-300 hover:bg-emerald-50 px-2 py-1 rounded-lg font-medium shadow-xs"
        >
          ⚙️ เบอร์ฉุกเฉิน ({contact ? contact.contact_phone_masked : "ค่าเริ่มต้น"})
        </button>
      </div>

      {statusMessage && (
        <div className="text-xs p-2 bg-amber-100 text-amber-900 rounded-lg">
          {statusMessage}
        </div>
      )}

      {/* ปุ่ม SOS ฉุกเฉิน */}
      <EmergencySosButton
        onTriggerSos={handleTriggerSos}
        disabled={!isSosEnabled}
      />

      {/* แผงอัดเสียง/วิดีโอหลักฐาน */}
      {isEvidenceEnabled && (
        <MediaEvidenceRecorder
          orderId={orderId}
          evidences={evidences}
          onUploadEvidence={handleUploadEvidence}
        />
      )}

      {/* Modals */}
      <SosConfirmationModal
        isOpen={isSosModalOpen}
        onClose={() => setIsSosModalOpen(false)}
        sosData={sosResult}
      />

      <EmergencyContactModal
        isOpen={isContactModalOpen}
        onClose={() => setIsContactModalOpen(false)}
        currentContact={contact}
        onSaveContact={handleSaveContact}
      />
    </div>
  );
}

