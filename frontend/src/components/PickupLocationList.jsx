/**
 * คอมโพเนนต์แสดงรายการที่อยู่นัดหมายของผู้ขาย (PickupLocationList)
 * รองรับ UC-01, UC-02, MD-DOM-04, AC-S01-02, Q-03
 */

import React from 'react';

export default function PickupLocationList({
  locations,
  onAddNew,
  onEdit,
  onDelete,
  onSetDefault,
}) {
  return (
    <div data-req="UC-01" className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-gray-900">ที่อยู่นัดหมายรับของเก่า</h3>
          <p className="text-xs text-gray-500">เลือกที่อยู่สำหรับให้ซาเล้งไปรับของ</p>
        </div>
        <button
          type="button"
          data-testid="add-new-location-btn"
          onClick={onAddNew}
          className="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-xl text-xs font-semibold flex items-center gap-1 transition-colors"
        >
          <span>+</span> เพิ่มที่อยู่
        </button>
      </div>

      {(!locations || locations.length === 0) ? (
        <div
          data-testid="empty-locations-notice"
          className="p-6 bg-gray-50 rounded-2xl border border-dashed border-gray-200 text-center"
        >
          <div className="text-2xl mb-1">🏡</div>
          <p className="text-xs text-gray-500 mb-3">ยังไม่มีที่อยู่นัดหมาย</p>
          <button
            type="button"
            onClick={onAddNew}
            className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-semibold hover:bg-emerald-700"
          >
            เพิ่มที่อยู่นัดหมายแรก
          </button>
        </div>
      ) : (
        <div className="space-y-2.5">
          {locations.map((loc) => (
            <div
              key={loc.location_id}
              data-testid={`location-card-${loc.location_id}`}
              className={`p-4 rounded-2xl border transition-all ${
                loc.is_default
                  ? 'bg-emerald-50/50 border-emerald-300 shadow-xs'
                  : 'bg-white border-gray-100 hover:border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-gray-800 bg-gray-100 px-2.5 py-0.5 rounded-md">
                    {loc.label || 'บ้าน'}
                  </span>
                  {loc.is_default && (
                    <span
                      data-testid="default-badge"
                      className="text-[11px] bg-emerald-600 text-white px-2 py-0.5 rounded-full font-semibold shadow-xs"
                    >
                      ★ ที่อยู่เริ่มต้น
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-1">
                  {!loc.is_default && onSetDefault && (
                    <button
                      type="button"
                      data-testid={`set-default-btn-${loc.location_id}`}
                      onClick={() => onSetDefault(loc.location_id)}
                      className="text-[11px] text-gray-500 hover:text-emerald-600 px-2 py-1 rounded hover:bg-gray-100"
                    >
                      ตั้งเป็นค่าเริ่มต้น
                    </button>
                  )}
                  <button
                    type="button"
                    data-testid={`edit-btn-${loc.location_id}`}
                    onClick={() => onEdit(loc)}
                    className="text-[11px] text-emerald-600 hover:underline px-1.5 py-1"
                  >
                    แก้ไข
                  </button>
                  <button
                    type="button"
                    data-testid={`delete-btn-${loc.location_id}`}
                    onClick={() => onDelete(loc.location_id)}
                    className="text-[11px] text-red-500 hover:text-red-700 px-1.5 py-1"
                  >
                    ลบ
                  </button>
                </div>
              </div>

              <div className="text-xs text-gray-800 font-medium mb-1">
                ตำบล/แขวง: <span className="font-bold text-gray-900">{loc.sub_district}</span>
              </div>
              <div className="text-xs text-gray-600 line-clamp-2">
                {loc.address_text}
              </div>

              {loc.geo_point && (
                <div className="text-[10px] text-gray-400 mt-2 font-mono flex items-center gap-1">
                  📍 {loc.geo_point.lat.toFixed(4)}, {loc.geo_point.lng.toFixed(4)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

