import React, { useState } from 'react';

// Seller Components & Pages
import AccountAccessPanel from './components/AccountAccessPanel';
import ScrapPostingPanel from './components/ScrapPostingPanel';
import PricingDecisionPage from './pages/PricingDecisionPage';
import BuyerSearchPanel from './components/BuyerSearchPanel';
import BookingTrackingPanel from './components/BookingTrackingPanel';
import PaymentVerificationPage from './pages/PaymentVerificationPage';
import SalesHistoryPage from './pages/SalesHistoryPage';
import TransactionSafetyPanel from './components/TransactionSafetyPanel';
import HelpCenterPage from './pages/HelpCenterPage';

// Collector (Buyer) Components
import CollectorAccountPanel from './components/CollectorAccountPanel';
import JobSearchPanel from './components/JobSearchPanel';
import JobEvaluationView from './components/JobEvaluationView';
import ActiveJobQueueView from './components/ActiveJobQueueView';
import ChatView from './components/ChatView';
import BillingReceiptView from './components/BillingReceiptView';
import PostJobCollectorView from './components/PostJobCollectorView';

// Admin Components
import AdminUserVerificationView from './components/admin/AdminUserVerificationView';
import AdminBenchmarkGradingView from './components/admin/AdminBenchmarkGradingView';
import AdminDispatchDisputeView from './components/admin/AdminDispatchDisputeView';
import AdminSecurityComplianceView from './components/admin/AdminSecurityComplianceView';
import AdminLoginPanel from './components/admin/AdminLoginPanel';

export default function App() {
  const getRoleFromPath = () => {
    if (window.location.pathname.startsWith('/buyer')) return 'collector';
    if (window.location.pathname.startsWith('/admin')) return 'admin';
    return 'seller';
  };

  const [activeRole, setActiveRole] = useState(getRoleFromPath);
  const [activeSubView, setActiveSubView] = useState(() => {
    if (window.location.pathname.startsWith('/buyer')) return 'collector-account';
    if (window.location.pathname.startsWith('/admin')) {
      return window.localStorage.getItem('saleng_admin_session') === 'authenticated'
        ? 'admin-users'
        : 'admin-login';
    }
    return 'seller-account';
  });
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(
    () => window.localStorage.getItem('saleng_admin_session') === 'authenticated'
  );

  const navigateToRole = (role) => {
    const path = role === 'collector' ? '/buyer' : `/${role}`;
    window.history.pushState({}, '', path);
    setActiveRole(role);
    if (role === 'seller') setActiveSubView('seller-account');
    if (role === 'collector') setActiveSubView('collector-account');
    if (role === 'admin') setActiveSubView('admin-login');
  };

  const sellerMenu = [
    { id: 'seller-account', label: '👤 บัญชี & เข้าสู่ระบบ', icon: '🔐' },
    { id: 'seller-posting', label: '📦 โพสต์ขายของเก่า', icon: '📝' },
    { id: 'seller-pricing', label: '💰 ราคากลางและประเมิน', icon: '⚖️' },
    { id: 'seller-search', label: '🔍 ค้นหาซาเล้งใกล้ฉัน', icon: '🛺' },
    { id: 'seller-tracking', label: '📍 ติดตามสถานะคำขอ', icon: '⏱️' },
    { id: 'seller-payment', label: '💳 ชำระเงินและใบเสร็จ', icon: '🧾' },
    { id: 'seller-history', label: '⭐ ประวัติและคะแนนรีวิว', icon: '📊' },
    { id: 'seller-safety', label: '🛡️ ความปลอดภัย & SOS', icon: '🚨' },
    { id: 'seller-help', label: '❓ คู่มือและศูนย์ช่วยเหลือ', icon: '💡' },
  ];

  const collectorMenu = [
    { id: 'collector-account', label: '👤 บัญชี & ยืนยันตัวตน KYC', icon: '🪪' },
    { id: 'collector-search', label: '🗺️ ค้นหางาน & เรดาร์แผนที่', icon: '📡' },
    { id: 'collector-eval', label: '⛽ ประเมินงาน & ค่าน้ำมัน', icon: '📈' },
    { id: 'collector-queue', label: '📋 คิวงาน & เส้นทางรับซื้อ', icon: '🛵' },
    { id: 'collector-chat', label: '💬 แชต & โทรติดต่อผู้ขาย', icon: '📞' },
    { id: 'collector-billing', label: '⚖️ ชั่งน้ำหนัก & ออกใบเสร็จ', icon: '🧾' },
    { id: 'collector-postjob', label: '⭐ ลูกค้าประจำ & รับซื้อ', icon: '🤝' },
  ];

  const adminMenu = [
    { id: 'admin-users', label: '🪪 อนุมัติ KYC & จัดการบทลงโทษ', icon: '⚖️' },
    { id: 'admin-pricing', label: '📊 ราคากลาง & เกณฑ์คัดแยก', icon: '🏷️' },
    { id: 'admin-dispatch', label: '🚨 คิวงานตกค้าง & ระงับข้อพิพาท', icon: '⚡' },
    { id: 'admin-compliance', label: '🛡️ ร่องรอยตรวจสอบ & PDPA', icon: '🔒' },
  ];

  const handleRoleChange = (role) => {
    navigateToRole(role);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      {/* Top Navbar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 py-3">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🛺</span>
            <div>
              <h1 className="text-xl font-black text-emerald-800 tracking-tight">
                Saleng (ซาเล้ง)
              </h1>
              <p className="text-xs text-gray-500 font-medium">
                แพลตฟอร์มรับซื้อของเก่าดิจิทัล (517 511 RE — กลุ่ม 2)
              </p>
            </div>
          </div>

          {/* Separate Portal Switcher */}
          <div className="flex items-center bg-gray-100 p-1 rounded-xl border border-gray-200">
            <button
              type="button"
              onClick={() => handleRoleChange('seller')}
              className={`min-h-[44px] px-4 py-1.5 rounded-lg font-bold text-xs sm:text-sm transition flex items-center gap-1.5 ${
                activeRole === 'seller'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>🛒</span> ผู้ขาย (Seller)
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('collector')}
              className={`min-h-[44px] px-4 py-1.5 rounded-lg font-bold text-xs sm:text-sm transition flex items-center gap-1.5 ${
                activeRole === 'collector'
                  ? 'bg-amber-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>🛺</span> ซาเล้ง (Buyer)
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('admin')}
              className={`min-h-[44px] px-4 py-1.5 rounded-lg font-bold text-xs sm:text-sm transition flex items-center gap-1.5 ${
                activeRole === 'admin'
                  ? 'bg-indigo-700 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span>🛡️</span> แอดมิน (Admin)
            </button>
          </div>

          {/* Quick API Docs Link */}
          <div className="hidden lg:flex items-center gap-2">
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-xs font-semibold px-3 py-1.5 bg-gray-100 hover:bg-gray-200 border rounded-lg text-gray-700 flex items-center gap-1.5 transition"
            >
              <span>📖</span> Swagger API Docs
            </a>
          </div>
        </div>

        {/* Sub Navigation Bar */}
        <div className="bg-gray-50 border-t border-gray-200 overflow-x-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center gap-2 py-2 whitespace-nowrap">
            {activeRole === 'seller' &&
              sellerMenu.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveSubView(item.id)}
                  className={`min-h-[44px] px-3.5 py-1.5 rounded-lg font-medium text-xs sm:text-sm transition flex items-center gap-1.5 ${
                    activeSubView === item.id
                      ? 'bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold'
                      : 'text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span>{item.icon}</span> {item.label}
                </button>
              ))}

            {activeRole === 'collector' &&
              collectorMenu.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveSubView(item.id)}
                  className={`min-h-[44px] px-3.5 py-1.5 rounded-lg font-medium text-xs sm:text-sm transition flex items-center gap-1.5 ${
                    activeSubView === item.id
                      ? 'bg-amber-100 text-amber-900 border border-amber-300 font-bold'
                      : 'text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span>{item.icon}</span> {item.label}
                </button>
              ))}

            {activeRole === 'admin' &&
              adminMenu.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveSubView(item.id)}
                  className={`min-h-[44px] px-3.5 py-1.5 rounded-lg font-medium text-xs sm:text-sm transition flex items-center gap-1.5 ${
                    activeSubView === item.id
                      ? 'bg-indigo-100 text-indigo-900 border border-indigo-300 font-bold'
                      : 'text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span>{item.icon}</span> {item.label}
                </button>
              ))}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6">
        {/* Seller Sub Views */}
        {activeRole === 'seller' && (
          <div>
            {activeSubView === 'seller-account' && <AccountAccessPanel />}
            {activeSubView === 'seller-posting' && <ScrapPostingPanel />}
            {activeSubView === 'seller-pricing' && <PricingDecisionPage />}
            {activeSubView === 'seller-search' && <BuyerSearchPanel />}
            {activeSubView === 'seller-tracking' && <BookingTrackingPanel />}
            {activeSubView === 'seller-payment' && <PaymentVerificationPage />}
            {activeSubView === 'seller-history' && <SalesHistoryPage />}
            {activeSubView === 'seller-safety' && <TransactionSafetyPanel />}
            {activeSubView === 'seller-help' && <HelpCenterPage />}
          </div>
        )}

        {/* Collector Sub Views */}
        {activeRole === 'collector' && (
          <div>
            {activeSubView === 'collector-account' && <CollectorAccountPanel />}
            {activeSubView === 'collector-search' && <JobSearchPanel />}
            {activeSubView === 'collector-eval' && <JobEvaluationView />}
            {activeSubView === 'collector-queue' && <ActiveJobQueueView />}
            {activeSubView === 'collector-chat' && <ChatView />}
            {activeSubView === 'collector-billing' && <BillingReceiptView />}
            {activeSubView === 'collector-postjob' && <PostJobCollectorView />}
          </div>
        )}

        {/* Admin Sub Views */}
        {activeRole === 'admin' && (
          <div>
            {!isAdminLoggedIn ? (
              <AdminLoginPanel
                onLoginSuccess={() => {
                  window.localStorage.setItem('saleng_admin_session', 'authenticated');
                  setIsAdminLoggedIn(true);
                  setActiveSubView('admin-users');
                }}
              />
            ) : (
              <>
                {activeSubView === 'admin-users' && <AdminUserVerificationView />}
                {activeSubView === 'admin-pricing' && <AdminBenchmarkGradingView />}
                {activeSubView === 'admin-dispatch' && <AdminDispatchDisputeView />}
                {activeSubView === 'admin-compliance' && <AdminSecurityComplianceView />}
              </>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4 text-center text-xs text-gray-500">
        Saleng Digital Scrap Platform &copy; 2026 รายวิชา 517 511 Requirements Engineering (กลุ่ม 2)
      </footer>
    </div>
  );
}

