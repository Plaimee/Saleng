import React, { useState } from "react";
import { submitReview, toggleFavorite } from "../services/postTransactionApi";

/**
 * PostTransactionRatingModal Component
 * หน้าต่างสำหรับให้คะแนนดาว 1-5 ดาว, เขียนรีวิว, บันทึกผู้รับซื้อประจำ, และปุ่มข้าม
 * รองรับ UC-10, SC-05, AC-S07-01, AC-S07-02, P-01, P-02, Q-01, Q-02
 */
export default function PostTransactionRatingModal({
  isOpen = true,
  orderId,
  sellerId = "SELLER-001",
  collectorId = "COLLECTOR-001",
  collectorName = "ลุงสมคิด (ซาเล้ง)",
  initialIsFavorite = false,
  onClose,
  onSuccess,
  onSkip,
}) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite);
  const [favLoading, setFavLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [submitted, setSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleToggleFavorite = async () => {
    setFavLoading(true);
    try {
      const res = await toggleFavorite(sellerId, collectorId);
      setIsFavorite(res.is_favorite);
    } catch (e) {
      // ignore
    } finally {
      setFavLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating < 1 || rating > 5) {
      setErrorMsg("กรุณาเลือกคะแนนดาว 1 ถึง 5 ดาว");
      return;
    }

    setSubmitting(true);
    setErrorMsg("");

    try {
      const result = await submitReview(orderId, {
        sellerId,
        rating,
        comment,
      });
      setSubmitted(true);
      if (onSuccess) onSuccess(result);
    } catch (err) {
      setErrorMsg(err.message || "เกิดข้อผิดพลาดในการส่งรีวิว");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      data-testid="post-transaction-rating-modal"
      data-req="UC-10"
    >
      <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-gray-100 text-center animate-in fade-in zoom-in duration-200">
        {submitted ? (
          <div className="py-6">
            <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-3 text-3xl">
              ✓
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-1">
              ขอบคุณสำหรับคะแนนรีวิว!
            </h3>
            <p className="text-xs text-gray-500 mb-6">
              ความคิดเห็นของคุณช่วยยกระดับคุณภาพบริการของซาเล้งในชุมชน
            </p>
            <button
              onClick={onClose}
              data-testid="modal-close-btn"
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-2xl shadow-md text-sm transition-all"
            >
              ปิดหน้าต่าง / ดูใบเสร็จ
            </button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="mb-4">
              <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 text-amber-700 rounded-full border border-amber-200 inline-block mb-2">
                🌟 สรุปงานเสร็จสมบูรณ์
              </span>
              <h2 className="text-base font-bold text-gray-800">
                ให้คะแนนและรีวิวบริการ
              </h2>
              <p className="text-xs text-gray-500 mt-1">
                ผู้รับซื้อ: <span className="font-semibold text-gray-700">{collectorName}</span>
              </p>
            </div>

            {/* ปุ่มทางลัด: บันทึกเป็นผู้รับซื้อประจำ (AC-S07-02, Q-03) */}
            <div className="mb-4 flex justify-center">
              <button
                type="button"
                onClick={handleToggleFavorite}
                disabled={favLoading}
                data-testid="favorite-toggle-btn"
                data-req="UC-10"
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all ${
                  isFavorite
                    ? "bg-amber-500 text-white border-amber-600 shadow-sm"
                    : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                }`}
              >
                <span>{isFavorite ? "⭐" : "☆"}</span>
                <span>{isFavorite ? "เป็นผู้รับซื้อประจำแล้ว" : "บันทึกเป็นผู้รับซื้อประจำ"}</span>
              </button>
            </div>

            {/* แถบเลือกดาว 1-5 ดาว (Interactive Stars - Q-02) */}
            <div className="flex justify-center items-center gap-2 mb-4" data-testid="star-rating-container">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  data-testid={`star-btn-${star}`}
                  className="text-3xl transition-transform hover:scale-125 focus:outline-none p-1"
                >
                  <span
                    className={
                      star <= (hoverRating || rating)
                        ? "text-amber-400 drop-shadow-sm"
                        : "text-gray-200"
                    }
                  >
                    ★
                  </span>
                </button>
              ))}
            </div>
            <div className="text-xs font-semibold text-amber-600 mb-4 h-4">
              {rating === 1 && "ควรปรับปรุง"}
              {rating === 2 && "พอใช้"}
              {rating === 3 && "ปานกลาง"}
              {rating === 4 && "ดีมาก"}
              {rating === 5 && "ประทับใจมาก ตาชั่งเที่ยงตรง"}
            </div>

            {/* กล่องข้อความรีวิว */}
            <div className="mb-4 text-left">
              <label className="block text-xs font-medium text-gray-600 mb-1">
                ความคิดเห็นเพิ่มเติม (ไม่บังคับ)
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value.slice(0, 500))}
                maxLength={500}
                placeholder="เช่น ตรงต่อเวลา ตาชั่งได้มาตรฐาน มีมารยาท..."
                data-testid="review-comment-input"
                rows={3}
                className="w-full text-xs p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none resize-none bg-gray-50"
              />
              <div className="text-[10px] text-gray-400 text-right mt-0.5">
                {comment.length}/500 ตัวอักษร
              </div>
            </div>

            {errorMsg && (
              <div
                className="bg-red-50 text-red-600 text-xs p-2.5 rounded-xl border border-red-200 mb-4"
                data-testid="review-error-message"
              >
                {errorMsg}
              </div>
            )}

            {/* ปุ่มดำเนินการ */}
            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={submitting || rating === 0}
                data-testid="submit-review-btn"
                data-req="UC-10"
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-semibold rounded-2xl shadow-md text-xs transition-all flex items-center justify-center gap-1"
              >
                {submitting ? "กำลังส่งรีวิว..." : "ส่งคะแนนรีวิว"}
              </button>

              {/* ปุ่มทางเลือกข้าม (Q-01) */}
              <button
                type="button"
                onClick={onSkip || onClose}
                data-testid="skip-review-btn"
                data-req="UC-10"
                className="w-full py-2.5 text-gray-500 hover:text-gray-700 text-xs font-medium transition-colors"
              >
                ข้าม / ดูใบเสร็จ
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

