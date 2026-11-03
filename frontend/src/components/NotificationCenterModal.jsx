import React, { useState, useEffect } from "react";
import {
  fetchNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
} from "../services/notificationHelpApi";

/**
 * NotificationCenterModal Component
 * แสดงศูนย์แจ้งเตือน In-App แจ้งเตือนของค้าง S1 และการเปลี่ยนสถานะ
 * รองรับ UC-08, AC-S08-01, P-01, Q-01
 */
export default function NotificationCenterModal({
  isOpen = true,
  onClose,
  sellerId = "SELLER-001",
}) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const data = await fetchNotifications(sellerId);
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen, sellerId]);

  if (!isOpen) return null;

  const handleMarkOne = async (id) => {
    try {
      await markNotificationAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (e) {
      // ignore
    }
  };

  const handleMarkAll = async () => {
    try {
      await markAllNotificationsAsRead(sellerId);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (e) {
      // ignore
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      data-testid="notification-center-modal"
      data-req="UC-08"
    >
      <div className="bg-white w-full max-w-sm rounded-3xl p-5 shadow-2xl border border-gray-100 max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center pb-3 border-b border-gray-100 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-base font-bold text-gray-800">ศูนย์แจ้งเตือน</span>
            {unreadCount > 0 && (
              <span
                className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full"
                data-testid="unread-badge"
              >
                {unreadCount} ใหม่
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-lg leading-none p-1"
            data-testid="close-notif-btn"
          >
            ✕
          </button>
        </div>

        {/* Action bar */}
        {unreadCount > 0 && (
          <div className="flex justify-end mb-2.5">
            <button
              onClick={handleMarkAll}
              className="text-xs text-emerald-600 hover:text-emerald-700 font-semibold"
              data-testid="mark-all-read-btn"
              data-req="UC-08"
            >
              ✓ อ่านแล้วทั้งหมด
            </button>
          </div>
        )}

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
          {loading ? (
            <div className="text-center py-10 text-xs text-gray-400">
              กำลังโหลดการแจ้งเตือน...
            </div>
          ) : notifications.length === 0 ? (
            <div className="text-center py-10 text-xs text-gray-400">
              ไม่มีการแจ้งเตือนใหม่ในขณะนี้
            </div>
          ) : (
            notifications.map((item) => {
              const isDraft = item.type === "DRAFT_REMINDER";
              return (
                <div
                  key={item.id}
                  onClick={() => !item.is_read && handleMarkOne(item.id)}
                  data-testid={`notification-item-${item.id}`}
                  className={`p-3 rounded-2xl border transition-all cursor-pointer ${
                    item.is_read
                      ? "bg-gray-50/70 border-gray-100 text-gray-500 opacity-80"
                      : isDraft
                      ? "bg-amber-50/50 border-amber-200 text-gray-800 shadow-xs"
                      : "bg-emerald-50/50 border-emerald-200 text-gray-800 shadow-xs"
                  }`}
                >
                  <div className="flex items-start justify-between gap-1 mb-1">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                        isDraft
                          ? "bg-amber-100 text-amber-800"
                          : "bg-emerald-100 text-emerald-800"
                      }`}
                    >
                      {isDraft ? "⏰ เตือนของค้าง" : "🚚 อัปเดตสถานะ"}
                    </span>
                    {!item.is_read && (
                      <span className="w-2 h-2 rounded-full bg-emerald-500 mt-1"></span>
                    )}
                  </div>
                  <h4 className="text-xs font-bold mb-1 leading-snug">{item.title}</h4>
                  <p className="text-[11px] leading-relaxed text-gray-600">{item.message}</p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

