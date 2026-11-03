/**
 * คอมโพเนนต์ตั้งค่าประเภทยานพาหนะและความจุน้ำหนักบรรทุก (VehicleConfigCard)
 * รองรับ REQ-FN-001, MD-DOM-04, BR-03, REQ-UX-001, CC-01, AC-B01-02, Q-04, P-02
 */

import React, { useState } from 'react';
import { collectorAccountApi } from '../services/collectorAccountApi';

const VEHICLE_OPTIONS = [
  {
    type: 'TRICYCLE',
    label: 'ซาเล้งสามล้อถีบ',
    defaultCapacity: 150.0,
    icon: '🚲',
    desc: 'เหมาะสำหรับซอยแคบ รับน้ำหนักได้คล่องตัว',
  },
  {
    type: 'SIDE_CAR_MOTORCYCLE',
    label: 'มอเตอร์ไซค์พ่วงข้าง',
    defaultCapacity: 300.0,
    icon: '🛵',
    desc: 'ระยะวิ่งปานกลาง บรรทุกได้ปริมาณพอเหมาะ',
  },
  {
    type: 'PICKUP_TRUCK',
    label: 'รถกระบะรับซื้อ',
    defaultCapacity: 1000.0,
    icon: '🛻',
    desc: 'รับของชิ้นใหญ่ เครื่องใช้ไฟฟ้า โลหะหนัก',
  },
];

export default function VehicleConfigCard({ profile, onVehicleUpdated }) {
  const [vehicleType, setVehicleType] = useState(profile?.vehicle_type || 'TRICYCLE');
  const [capacity, setCapacity] = useState(profile?.max_capacity_kg || 150.0);
  const [licensePlate, setLicensePlate] = useState(profile?.license_plate || '');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSelectVehicleType = (type, defaultCap) => {
    setVehicleType(type);
    setCapacity(defaultCap);
    setSuccessMsg('');
    setErrorMsg('');
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setErrorMsg('');

    const parsedCap = parseFloat(capacity);
    if (isNaN(parsedCap) || parsedCap <= 0) {
      setErrorMsg('กรุณาระบุน้ำหนักบรรทุกที่มากกว่า 0 กิโลกรัม');
      return;
    }

    setLoading(true);
    try {
      const updated = await collectorAccountApi.updateVehicle(profile.saleng_id, {
        vehicle_type: vehicleType,
        license_plate: licensePlate,
        max_capacity_kg: parsedCap,
      });
      setSuccessMsg('บันทึกข้อมูลยานพาหนะเรียบร้อยแล้ว');
      if (onVehicleUpdated) onVehicleUpdated(updated);
    } catch (err) {
      setErrorMsg(err.message || 'บันทึกข้อมูลไม่สำเร็จ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      data-req="REQ-FN-001"
      className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-md border border-gray-100 p-5 my-3"
    >
      <div className="flex items-center space-x-2.5 mb-4">
        <span className="text-2xl">🚛</span>
        <div>
          <h3 className="text-lg font-bold text-gray-900">ยานพาหนะและความจุ</h3>
          <p className="text-xs text-gray-500">ควบคุมโควตาน้ำหนักเที่ยววิ่งตามกฎ BR-03</p>
        </div>
      </div>

      {successMsg && (
        <div data-testid="vehicle-success-alert" className="mb-3 p-3 bg-green-50 border border-green-200 text-green-800 text-xs rounded-xl">
          ✓ {successMsg}
        </div>
      )}
      {errorMsg && (
        <div data-testid="vehicle-error-alert" className="mb-3 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl">
          ⚠️ {errorMsg}
        </div>
      )}

      <form onSubmit={handleSave} noValidate className="space-y-4">
        {/* เลือกประเภทยานพาหนะ 3 รูปแบบ */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-2">
            เลือกประเภทยานพาหนะมาตรฐาน (Q-04)
          </label>
          <div className="grid grid-cols-1 gap-2.5">
            {VEHICLE_OPTIONS.map((opt) => {
              const isSelected = vehicleType === opt.type;
              return (
                <button
                  key={opt.type}
                  type="button"
                  data-testid={`vehicle-option-${opt.type}`}
                  onClick={() => handleSelectVehicleType(opt.type, opt.defaultCapacity)}
                  className={`w-full min-h-[48px] p-3 rounded-xl border text-left transition flex items-center justify-between ${
                    isSelected
                      ? 'border-emerald-600 bg-emerald-50/70 ring-1 ring-emerald-500'
                      : 'border-gray-200 hover:border-gray-300 bg-white'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{opt.icon}</span>
                    <div>
                      <p className="text-sm font-bold text-gray-900">{opt.label}</p>
                      <p className="text-xs text-gray-500">{opt.desc}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold px-2 py-0.5 bg-gray-100 rounded-md text-gray-700">
                      ~{opt.defaultCapacity} กก.
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* ปรับแต่งความจุและเลขทะเบียน */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              ความจุจริง (กก.)
            </label>
            <input
              type="number"
              step="1"
              min="1"
              max="5000"
              data-testid="capacity-input"
              value={capacity}
              onChange={(e) => setCapacity(e.target.value)}
              className="w-full h-12 px-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm font-semibold text-gray-900"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              เลขทะเบียนรถ (ถ้ามี)
            </label>
            <input
              type="text"
              data-testid="license-plate-input"
              value={licensePlate}
              onChange={(e) => setLicensePlate(e.target.value)}
              placeholder="1กข-9999 กทม."
              className="w-full h-12 px-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-emerald-500 text-sm"
            />
          </div>
        </div>

        <button
          type="submit"
          data-testid="save-vehicle-btn"
          disabled={loading}
          className="w-full min-h-[48px] bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl shadow-md transition disabled:opacity-50 text-base flex items-center justify-center space-x-2"
        >
          {loading ? 'กำลังบันทึก...' : 'บันทึกการตั้งค่ายานพาหนะ'}
        </button>
      </form>
    </div>
  );
}
