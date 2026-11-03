import React, { useState, useEffect } from "react";
import WasteSortingGuideView from "../components/WasteSortingGuideView";
import FaqAccordionView from "../components/FaqAccordionView";
import NotificationCenterModal from "../components/NotificationCenterModal";
import SupportTicketModal from "../components/SupportTicketModal";
import {
  fetchSortingGuides,
  fetchFaqs,
  fetchNotifications,
} from "../services/notificationHelpApi";

/**
 * HelpCenterPage Component (Main Mobile SPA Page)
 * ศูนย์รวมการช่วยเหลือ คำถามที่พบบ่อย คู่มือแยกขยะ และการแจ้งเตือน
 * รองรับ UC-08, UC-13, CC-01, CC-05, REQ-OP-001, AC-S08-01..04
 */
export default function HelpCenterPage({ sellerId = "SELLER-001", onBack }) {
  const [activeTab, setActiveTab] = useState("GUIDES"); // 'GUIDES', 'FAQS'
  const [guides, setGuides] = useState([]);
  const [faqsData, setFaqsData] = useState({ categories: [], total_faqs: 0 });
  const [searchQuery, setSearchQuery] = useState("");
  const [unreadNotifCount, setUnreadNotifCount] = useState(0);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [isTicketOpen, setIsTicketOpen] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [loading, setLoading] = useState(true);

  // โหลดข้อมูลคู่มือและ FAQ
  const loadData = async () => {
    setLoading(true);
    try {
      const [guideRes, faqRes, notifRes] = await Promise.all([
        fetchSortingGuides(),
        fetchFaqs(searchQuery),
        fetchNotifications(sellerId).catch(() => ({ unread_count: 0 })),
      ]);

      setGuides(guideRes.guides || []);
      setFaqsData(faqRes);
      setUnreadNotifCount(notifRes.unread_count || 0);
      setIsOffline(Boolean(guideRes.is_offline_cached || faqRes.is_offline_cached));
    } catch (e) {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [sellerId]);

  // ค้นหา FAQ เมื่อผู้ใช้พิมพ์คำค้นหา
  const handleFaqSearch = async (query) => {
    setSearchQuery(query);
    try {
      const res = await fetchFaqs(query);
      setFaqsData(res);
    } catch (e) {
      // ignore
    }
  };

  return (
    <div
      className="min-h-screen bg-gray-50 max-w-md mx-auto pb-16 font-sans text-gray-900 border-x border-gray-200"
      data-testid="help-center-page"
      data-req="UC-08"
    >
      {/* Header */}
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-gray-100 px-4 py-3 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-2">
          {onBack && (
            <button
              onClick={onBack}
              className="p-1.5 -ml-1.5 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 text-sm"
              data-testid="back-button"
            >
              ←
            </button>
          )}
          <h1 className="text-base font-bold text-gray-800">
            ศูนย์ช่วยเหลือและการแจ้งเตือน
          </h1>
        </div>

        {/* ปุ่มกระดิ่งแจ้งเตือน */}
        <button
          onClick={() => setIsNotifOpen(true)}
          data-testid="notif-bell-btn"
          data-req="UC-08"
          className="relative p-2 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <span className="text-lg">🔔</span>
          {unreadNotifCount > 0 && (
            <span
              className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center animate-pulse"
              data-testid="bell-unread-badge"
            >
              {unreadNotifCount}
            </span>
          )}
        </button>
      </header>

      {/* Main Container */}
      <main className="p-4">
        {/* ป้ายเตือนออฟไลน์แคช (CC-05, REQ-OP-001) */}
        {isOffline && (
          <div
            className="bg-amber-50 border border-amber-200 text-amber-800 px-3 py-2 rounded-xl text-xs mb-4 flex items-center justify-between"
            data-testid="offline-help-banner"
          >
            <span>📡 โหมดออฟไลน์: เปิดอ่านข้อมูลจากแคชในเครื่อง</span>
            <span className="text-[10px] text-amber-600">ออฟไลน์</span>
          </div>
        )}

        {/* Navigation Tabs (Guides vs FAQs) */}
        <div className="flex bg-gray-200/70 p-1 rounded-2xl mb-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab("GUIDES")}
            data-testid="tab-guides"
            className={`flex-1 py-2 rounded-xl transition-all ${
              activeTab === "GUIDES"
                ? "bg-white text-emerald-700 shadow-xs"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            💡 คู่มือคัดแยกขยะ
          </button>
          <button
            onClick={() => setActiveTab("FAQS")}
            data-testid="tab-faqs"
            className={`flex-1 py-2 rounded-xl transition-all ${
              activeTab === "FAQS"
                ? "bg-white text-emerald-700 shadow-xs"
                : "text-gray-500 hover:text-gray-800"
            }`}
          >
            ❓ คำถามที่พบบ่อย (FAQ)
          </button>
        </div>

        {/* Tab Contents */}
        {loading ? (
          <div className="text-center py-12 text-xs text-gray-400">
            กำลังโหลดข้อมูลศูนย์ช่วยเหลือ...
          </div>
        ) : activeTab === "GUIDES" ? (
          <WasteSortingGuideView guides={guides} isOffline={isOffline} />
        ) : (
          <FaqAccordionView
            categories={faqsData.categories || []}
            searchQuery={searchQuery}
            onSearchChange={handleFaqSearch}
          />
        )}

        {/* การ์ดติดต่อฝ่ายดูแลลูกค้าด่วน (AC-S08-04) */}
        <div className="bg-gradient-to-br from-emerald-600 to-teal-700 rounded-3xl p-5 text-white shadow-md mt-6">
          <h3 className="text-sm font-bold mb-1 flex items-center gap-1.5">
            <span>💬</span>
            <span>ยังต้องการความช่วยเหลือเพิ่มเติม?</span>
          </h3>
          <p className="text-xs opacity-90 mb-4 leading-relaxed">
            มีข้อสงสัยเกี่ยวกับการนัดหมายหรือพบปัญหาหน้างาน ส่งคำร้องขอความช่วยเหลือให้เจ้าหน้าที่ตรวจสอบได้ตลอดเวลา
          </p>
          <button
            type="button"
            onClick={() => setIsTicketOpen(true)}
            data-testid="open-support-ticket-btn"
            data-req="UC-13"
            className="w-full py-2.5 bg-white text-emerald-800 font-bold rounded-2xl text-xs hover:bg-emerald-50 transition-colors shadow-sm"
          >
            ส่งคำร้องขอความช่วยเหลือ (Support Ticket)
          </button>
        </div>
      </main>

      {/* Notification Center Modal */}
      <NotificationCenterModal
        isOpen={isNotifOpen}
        onClose={() => {
          setIsNotifOpen(false);
          loadData();
        }}
        sellerId={sellerId}
      />

      {/* Support Ticket Modal */}
      <SupportTicketModal
        isOpen={isTicketOpen}
        onClose={() => setIsTicketOpen(false)}
        sellerId={sellerId}
      />
    </div>
  );
}

