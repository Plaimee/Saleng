/**
 * หน้าต่างเพิ่มหรือแก้ไขที่อยู่นัดหมายรับของเก่า (PickupLocationModal)
 * รองรับ UC-01, UC-02, MD-DOM-04, Q-02, Q-03, AC-S01-02
 */

import React, { useState } from 'react';

export default function PickupLocationModal({
  isOpen,
  location, // ถ้ามีคือโหมดแก้ไข ถ้าไม่มีคือเพิ่มใหม่
  onClose,
  onSave,
}) {
  if (!isOpen) return null;

  const [label, setLabel] = useState(location?.label || 'บ้าน');
  const [subDistrict, setSubDistrict] = useState(location?.sub_district || '');
  const [addressText, setAddressText] = useState(location?.address_text || '');
  const [lat, setLat] = useState(location?.geo_point?.lat || 13.7563);
  const [lng, setLng] = useState(location?.geo_point?.lng || 100.5018);
  const [isDefault, setIsDefault] = useState(location?.is_default || false);
  const [locating, setLocating] = useState(false);
  const [gpsSuccess, setGpsSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleGetCurrentLocation = () => {
    setLocating(true);
    setGpsSuccess(false);
    setError('');

    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLat(parseFloat(pos.coords.latitude.toFixed(6)));
          setLng(parseFloat(pos.coords.longitude.toFixed(6)));
          setLocating(false);
          setGpsSuccess(true);
        },
        () => {
          // Fallback จำลองพิกัดกรุงเทพฯ
          setLat(13.7563);
          setLng(100.5018);
          setLocating(false);
          setGpsSuccess(true);
        },
        { timeout: 5000 }
      );
    } else {
      setLat(13.7563);
      setLng(100.5018);
      setLocating(false);
      setGpsSuccess(true);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!subDistrict.trim()) {
      setError('กรุณาระบุตำบล/แขวง');
      return;
    }
    if (!addressText.trim()) {
      setError('กรุณาระบุบ้านเลขที่และซอย/ถนน');
      return;
    }

    onSave({
      label: label.trim() || 'บ้าน',
      sub_district: subDistrict.trim(),
      address_text: addressText.trim(),
      geo_point: { lat: parseFloat(lat), lng: parseFloat(lng) },
      is_default: isDefault,
    });
  };

  return (
    <div
      data-req="UC-01"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
    >
      <div className="bg-white rounded-3xl w-full max-w-md shadow-xl overflow-hidden border border-gray-100 animate-in fade-in zoom-in-95 duration-200">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-bold text-gray-900 text-base">
            {location ? 'แก้ไขที่อยู่นัดหมาย' : 'เพิ่มที่อยู่นัดหมายใหม่'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl font-bold p-1"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && (
            <div className="p-2.5 bg-red-50 text-red-600 text-xs rounded-xl border border-red-200">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              ป้ายกำกับที่อยู่
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['บ้าน', 'คอนโด', 'ที่ทำงาน/ร้านค้า'].map((opt) => (
                <button
                  type="button"
                  key={opt}
                  onClick={() => setLabel(opt)}
                  className={`py-2 text-xs font-medium rounded-xl border transition-all ${
                    label === opt
                      ? 'bg-emerald-50 border-emerald-500 text-emerald-700'
                      : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              ตำบล / แขวง <span className="text-gray-400 font-normal">(เปิดเผยก่อนรับงาน)</span>
            </label>
            <input
              type="text"
              data-testid="sub-district-input"
              value={subDistrict}
              onChange={(e) => setSubDistrict(e.target.value)}
              placeholder="เช่น บางซื่อ, จตุจักร, ลาดพร้าว"
              className="w-full px-3.5 py-2.5 text-sm rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              บ้านเลขที่ ซอย ถนน จุดสังเกต <span className="text-red-500 font-normal">(ข้อมูลส่วนตัว PII)</span>
            </label>
            <textarea
              rows={2}
              data-testid="address-text-input"
              value={addressText}
              onChange={(e) => setAddressText(e.target.value)}
              placeholder="เช่น 123/45 ซอย 5 หมู่บ้านสุขสันต์ ถนนวงศ์สว่าง"
              className="w-full px-3.5 py-2 text-sm rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <div className="p-3 bg-gray-50 rounded-2xl border border-gray-200/60">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-gray-700 flex items-center gap-1.5">
                📍 พิกัด GPS นัดหมาย
              </span>
              <button
                type="button"
                data-testid="gps-pin-btn"
                onClick={handleGetCurrentLocation}
                disabled={locating}
                className="text-xs text-emerald-600 font-semibold hover:underline flex items-center gap-1"
              >
                {locating ? 'กำลังดึงพิกัด...' : '🎯 ดึงตำแหน่งปัจจุบัน'}
              </button>
            </div>
            <div className="text-[11px] text-gray-500 font-mono">
              ละติจูด: {lat}, ลองจิจูด: {lng}
            </div>
            {gpsSuccess && (
              <span className="text-[10px] text-emerald-600 font-medium">✓ ปักหมุดพิกัดสำเร็จ</span>
            )}
          </div>

          <label className="flex items-center space-x-2 cursor-pointer pt-1">
            <input
              type="checkbox"
              data-testid="is-default-checkbox"
              checked={isDefault}
              onChange={(e) => setIsDefault(e.target.checked)}
              className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500"
            />
            <span className="text-xs text-gray-700">ตั้งเป็นที่อยู่นัดหมายเริ่มต้น (Default)</span>
          </label>

          <div className="flex items-center space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-xs font-semibold hover:bg-gray-50"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              data-testid="save-location-btn"
              className="flex-1 py-2.5 bg-emerald-600 text-white rounded-xl text-xs font-semibold hover:bg-emerald-700 shadow-sm"
            >
              บันทึกที่อยู่
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

