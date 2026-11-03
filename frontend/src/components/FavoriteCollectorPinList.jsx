/**
 * แถบตรึงซาเล้งที่เคยใช้บริการไว้บนสุด (FavoriteCollectorPinList)
 * รองรับ UC-03, REQ-UX-001, AC-S03-02, Q-02
 */

import React from 'react';

export default function FavoriteCollectorPinList({ favorites = [], onSelect }) {
  if (!favorites || favorites.length === 0) {
    return null;
  }

  return (
    <div
      data-req="UC-03"
      data-testid="favorite-pin-list"
      className="p-3 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-2xl space-y-2"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5 text-xs font-bold text-amber-900">
          <span>⭐</span>
          <span>ซาเล้งที่เคยใช้บริการ ({favorites.length})</span>
        </div>
        <span className="text-[10px] text-amber-700 font-medium">นัดซ้ำง่ายใน 1 คลิก</span>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        {favorites.map((fav) => (
          <button
            key={fav.saleng_id}
            type="button"
            data-testid={`fav-pin-card-${fav.saleng_id}`}
            onClick={() => onSelect && onSelect(fav)}
            className="flex-shrink-0 flex items-center space-x-2.5 p-2 bg-white rounded-xl border border-amber-300 shadow-2xs hover:border-amber-500 text-left transition-all"
          >
            <div className="w-8 h-8 rounded-full overflow-hidden bg-amber-100 flex items-center justify-center text-sm flex-shrink-0">
              {fav.avatar_url ? (
                <img src={fav.avatar_url} alt={fav.display_name} className="w-full h-full object-cover" />
              ) : (
                '👨‍🔧'
              )}
            </div>
            <div>
              <div className="text-[11px] font-bold text-gray-800 line-clamp-1">
                {fav.display_name}
              </div>
              <div className="text-[9px] text-amber-700 font-medium">
                ★ {fav.rating.toFixed(1)} • {fav.vehicle_type === 'PICKUP_TRUCK' ? 'รถกระบะ' : 'ซาเล้ง'}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

