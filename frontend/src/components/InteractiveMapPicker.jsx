/**
 * Interactive OpenStreetMap Pin Picker (Leaflet)
 * ใช้สำหรับเลือกพิกัดจุดนัดรับของเก่าบนแผนที่จริง (คลิกหรือลากหมุด + ค้นหาสถานที่)
 * รองรับ UC-01, UC-02, AC-S01-02 (ปลอดภัยในโหมด Vitest/jsdom เมื่อไม่มี window.L)
 */

import React, { useEffect, useRef, useState } from 'react';

export default function InteractiveMapPicker({
  lat = 13.7563,
  lng = 100.5018,
  onChange,
  onAddressFound,
  height = '220px',
}) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);

  const [searchText, setSearchText] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  // Initialize Leaflet map once
  useEffect(() => {
    const L = typeof window !== 'undefined' ? window.L : null;
    if (!L || !containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [lat, lng],
      zoom: 15,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 19,
    }).addTo(map);

    const marker = L.marker([lat, lng], { draggable: true }).addTo(map);

    const emitPosition = (newLat, newLng) => {
      const fixedLat = parseFloat(Number(newLat).toFixed(6));
      const fixedLng = parseFloat(Number(newLng).toFixed(6));
      if (onChange) onChange(fixedLat, fixedLng);
    };

    marker.on('dragend', () => {
      const pos = marker.getLatLng();
      emitPosition(pos.lat, pos.lng);
    });

    map.on('click', (e) => {
      marker.setLatLng(e.latlng);
      emitPosition(e.latlng.lat, e.latlng.lng);
    });

    mapRef.current = map;
    markerRef.current = marker;

    // Ensure proper tile layout when rendered inside a modal
    setTimeout(() => {
      map.invalidateSize();
    }, 150);

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  // Sync external lat/lng updates (e.g., GPS button or search result)
  useEffect(() => {
    if (!mapRef.current || !markerRef.current) return;
    const current = markerRef.current.getLatLng();
    if (
      Math.abs(current.lat - lat) > 0.00001 ||
      Math.abs(current.lng - lng) > 0.00001
    ) {
      markerRef.current.setLatLng([lat, lng]);
      mapRef.current.setView([lat, lng], Math.max(mapRef.current.getZoom(), 15), {
        animate: true,
      });
    }
  }, [lat, lng]);

  const handleSearchPlace = async () => {
    const q = searchText.trim();
    if (!q) return;
    setSearching(true);
    setSearchError('');
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&countrycodes=th&limit=1&q=${encodeURIComponent(
          q
        )}`
      );
      const results = await res.json();
      if (!results || results.length === 0) {
        setSearchError('ไม่พบสถานที่นี้ ลองพิมพ์ชื่อเขต/แขวง หรือคลิกปักหมุดบนแผนที่โดยตรง');
      } else {
        const hit = results[0];
        const newLat = parseFloat(parseFloat(hit.lat).toFixed(6));
        const newLng = parseFloat(parseFloat(hit.lon).toFixed(6));
        if (onChange) onChange(newLat, newLng);
        if (onAddressFound && hit.address) {
          const subDistrict =
            hit.address.suburb ||
            hit.address.quarter ||
            hit.address.city_district ||
            hit.address.town ||
            '';
          onAddressFound({
            subDistrict,
            displayName: hit.display_name || '',
          });
        }
      }
    } catch {
      setSearchError('ค้นหาสถานที่ไม่ได้ชั่วคราว กรุณาคลิกหรือลากหมุดบนแผนที่โดยตรง');
    } finally {
      setSearching(false);
    }
  };

  const hasLeaflet = typeof window !== 'undefined' && Boolean(window.L);

  return (
    <div className="space-y-2">
      {/* Search Place Input */}
      <div className="flex gap-1.5">
        <input
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleSearchPlace();
            }
          }}
          placeholder="ค้นหาสถานที่ เช่น จตุจักร, ม.เกษตร, ลาดพร้าว..."
          className="flex-1 px-3 py-1.5 text-xs rounded-lg border border-gray-300 bg-white focus:outline-none focus:border-black"
        />
        <button
          type="button"
          onClick={handleSearchPlace}
          disabled={searching}
          className="px-3 py-1.5 rounded-lg bg-black text-yellow-400 text-xs font-bold hover:bg-zinc-800 disabled:opacity-50"
        >
          {searching ? '...' : '🔍 ค้นหา'}
        </button>
      </div>

      {searchError && (
        <p className="text-[11px] text-amber-700 bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200">
          {searchError}
        </p>
      )}

      {/* Map Canvas */}
      {hasLeaflet ? (
        <div
          ref={containerRef}
          data-testid="interactive-map-picker"
          style={{ height, width: '100%' }}
          className="rounded-xl overflow-hidden border border-gray-300 z-0"
        />
      ) : (
        <div
          data-testid="interactive-map-picker"
          className="rounded-xl border border-dashed border-gray-300 bg-white p-4 text-center text-xs text-gray-500"
        >
          🗺️ แผนที่ปักหมุดพิกัด ({lat}, {lng})
        </div>
      )}

      <p className="text-[11px] text-gray-500">
        💡 คลิกบนแผนที่ หรือลากหมุดสีน้ำเงิน เพื่อเลือกจุดนัดรับของเก่าที่แม่นยำ
      </p>
    </div>
  );
}
