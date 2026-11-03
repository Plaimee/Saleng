/**
 * แผงจัดการอัปโหลดรูปถ่ายของเก่า (PhotoUploadManager)
 * รองรับ REQ-FN-004, EV-03, EV-08, AC-S02-04
 */

import React from 'react';

export default function PhotoUploadManager({ photos = [], onAddPhoto, onRemovePhoto }) {
  const maxPhotos = 5;

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      alert('ขนาดไฟล์ต้องไม่เกิน 5 MB');
      return;
    }

    if (photos.length >= maxPhotos) {
      alert('สามารถแนบรูปถ่ายได้สูงสุดไม่เกิน 5 รูปต่อรายการ');
      return;
    }

    // สร้าง data url จำลอง
    const reader = new FileReader();
    reader.onload = (event) => {
      onAddPhoto(event.target.result);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  return (
    <div data-req="UC-02" className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
          📷 รูปถ่ายของเก่าประกอบรายการ
          <span className="text-[11px] font-normal text-gray-400">
            ({photos.length}/{maxPhotos} รูป)
          </span>
        </label>
        <span className="text-[10px] text-gray-400">ขนาดไม่เกิน 5 MB/รูป</span>
      </div>

      <div className="flex flex-wrap gap-2 items-center">
        {/* รายการรูปที่อัปโหลดแล้ว */}
        {photos.map((url, idx) => (
          <div
            key={idx}
            data-testid={`photo-thumbnail-${idx}`}
            className="relative w-16 h-16 rounded-xl overflow-hidden border border-gray-200 bg-gray-50 shadow-2xs group"
          >
            <img src={url} alt={`Scrap ${idx + 1}`} className="w-full h-full object-cover" />
            <button
              type="button"
              data-testid={`remove-photo-btn-${idx}`}
              onClick={() => onRemovePhoto(idx)}
              className="absolute top-1 right-1 w-5 h-5 bg-black/60 text-white rounded-full flex items-center justify-center text-[10px] hover:bg-black/80 transition-colors"
            >
              ✕
            </button>
          </div>
        ))}

        {/* ปุ่มถ่ายรูป / เลือกไฟล์ */}
        {photos.length < maxPhotos && (
          <label
            data-testid="upload-photo-label"
            className="w-16 h-16 rounded-xl border-2 border-dashed border-gray-300 hover:border-emerald-500 hover:bg-emerald-50/50 flex flex-col items-center justify-center cursor-pointer text-gray-400 hover:text-emerald-600 transition-all"
          >
            <span className="text-lg">+</span>
            <span className="text-[9px] font-medium">เพิ่มรูป</span>
            <input
              type="file"
              accept="image/*"
              data-testid="photo-file-input"
              className="hidden"
              onChange={handleFileChange}
            />
          </label>
        )}
      </div>
    </div>
  );
}

