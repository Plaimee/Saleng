import React, { useState, useEffect } from "react";

/**
 * แผงบันทึกเสียงและวิดีโอหลักฐานหน้างาน (AC-S09-01, P-01, Q-01, UC-09)
 */
export default function MediaEvidenceRecorder({
  orderId,
  evidences = [],
  onUploadEvidence,
  disabled = false,
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [mediaType, setMediaType] = useState("AUDIO"); // 'AUDIO' or 'VIDEO'
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ตัวจับเวลาขณะบันทึก
  useEffect(() => {
    let interval = null;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordSeconds(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const formatTimer = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleStartRecording = () => {
    setIsRecording(true);
  };

  const handleStopAndSave = async () => {
    setIsRecording(false);
    const duration = recordSeconds || 5; // fallback อย่างน้อย 5 วิ
    setIsSubmitting(true);
    try {
      const simulatedBytes = duration * 32000; // จำลองขนาดไฟล์
      await onUploadEvidence({
        media_type: mediaType,
        duration_seconds: duration,
        file_size_bytes: simulatedBytes,
      });
    } catch (e) {
      // handled by parent
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      data-req="UC-09"
      className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 space-y-3"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-gray-800 text-sm flex items-center gap-1.5">
          <span>🎙️</span>
          <span>บันทึกเสียง/วิดีโอหลักฐานหน้างาน</span>
        </h3>
        <div className="flex gap-1 text-xs">
          <button
            type="button"
            onClick={() => setMediaType("AUDIO")}
            disabled={isRecording || disabled}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              mediaType === "AUDIO"
                ? "bg-emerald-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            เสียง
          </button>
          <button
            type="button"
            onClick={() => setMediaType("VIDEO")}
            disabled={isRecording || disabled}
            className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
              mediaType === "VIDEO"
                ? "bg-emerald-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            วิดีโอ
          </button>
        </div>
      </div>

      {/* หน้าต่างสถานะการบันทึก */}
      {isRecording ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-center space-y-2 animate-pulse">
          <div className="flex items-center justify-center gap-2 text-red-600 font-bold text-base">
            <span className="w-3 h-3 rounded-full bg-red-600 animate-ping" />
            <span>กำลังบันทึก{mediaType === "AUDIO" ? "เสียง" : "วิดีโอ"}...</span>
            <span className="font-mono text-lg">{formatTimer(recordSeconds)}</span>
          </div>

          {/* Waveform indicator จำลอง */}
          <div className="flex items-center justify-center gap-1 h-6">
            <span className="w-1 bg-red-500 rounded h-3 animate-bounce" />
            <span className="w-1 bg-red-500 rounded h-6 animate-pulse" />
            <span className="w-1 bg-red-500 rounded h-4 animate-bounce" />
            <span className="w-1 bg-red-500 rounded h-5 animate-pulse" />
            <span className="w-1 bg-red-500 rounded h-2 animate-bounce" />
          </div>

          <button
            type="button"
            onClick={handleStopAndSave}
            disabled={isSubmitting}
            className="w-full py-2.5 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg text-sm shadow transition-all active:scale-95"
          >
            {isSubmitting ? "กำลังประมวลผล..." : "⏹️ หยุดและบันทึกหลักฐาน"}
          </button>
        </div>
      ) : (
        <div>
          <button
            type="button"
            onClick={handleStartRecording}
            disabled={disabled || isSubmitting}
            className="w-full py-2.5 bg-gray-100 hover:bg-gray-200 active:bg-gray-300 text-gray-700 font-semibold rounded-xl text-sm flex items-center justify-center gap-2 border border-gray-300 transition-all disabled:opacity-50"
          >
            <span>⏺️</span>
            <span>เริ่มอัด{mediaType === "AUDIO" ? "เสียง" : "วิดีโอ"}ระหว่างชั่งของ</span>
          </button>
        </div>
      )}

      {/* รายการหลักฐานที่บันทึกไว้ในคำขอนี้ */}
      {evidences && evidences.length > 0 && (
        <div className="space-y-1.5 pt-2 border-t">
          <div className="text-xs text-gray-500 font-medium">
            หลักฐานที่แนบไว้ในคำขอนี้ ({evidences.length} รายการ):
          </div>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {evidences.map((ev, idx) => (
              <div
                key={ev.evidence_id || idx}
                className="flex items-center justify-between bg-gray-50 p-2 rounded-lg text-xs border"
              >
                <div className="flex items-center gap-1.5 text-gray-700">
                  <span>{ev.media_type === "AUDIO" ? "🎵" : "📹"}</span>
                  <span className="font-mono font-medium">{ev.evidence_id}</span>
                  <span className="text-gray-400">({ev.duration_seconds}s)</span>
                </div>
                {ev.is_locked ? (
                  <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-medium">
                    🔒 ล็อกแล้ว
                  </span>
                ) : (
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                    บันทึกแล้ว
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

