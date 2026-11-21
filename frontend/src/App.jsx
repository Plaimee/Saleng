import React, { useState } from 'react';

// Auth Gate (หน้าแรกบังคับ Login / Register ของทั้ง 3 พอร์ทัล)
import ShopeeAuthGate from './components/ShopeeAuthGate';
import { accountApi } from './services/accountApi';
import { collectorAccountApi } from './services/collectorAccountApi';
import { jobRouteApi } from './services/jobRouteApi';

// Seller Components & Pages
import AccountAccessPanel from './components/AccountAccessPanel';
import PickupLocationModal from './components/PickupLocationModal';
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
import IncomingDirectOrdersCard from './components/IncomingDirectOrdersCard';
import CollectorGpsNavigationView from './components/CollectorGpsNavigationView';
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

// โครงสร้าง User Journey หลัก 4 หมวดต่อพอร์ทัล (สอดคล้องกับ UC-01..UC-13 และ State Machine S1..S9)
const PRIMARY_NAV = {
  seller: [
    {
      id: 'sell-flow',
      label: 'ลงขายของเก่า',
      shortLabel: 'ลงขาย',
      icon: '📦',
      subtitle: 'สร้างคำขอขายแบบทีละขั้นตอน (* → S1 → S2)',
    },
    {
      id: 'my-orders',
      label: 'รายการขายของฉัน',
      shortLabel: 'รายการขาย',
      icon: '🧾',
      subtitle: 'ติดตามซาเล้ง ตรวจรับ ชำระเงิน SOS และประวัติ (S2 → S7)',
    },
    {
      id: 'market-check',
      label: 'เช็กราคากลาง',
      shortLabel: 'ราคากลาง',
      icon: '💰',
      subtitle: 'ตรวจสอบตารางราคากลางประจำวันและลองคำนวณราคาก่อนลงขาย',
    },
    {
      id: 'me',
      label: 'บัญชีของฉัน',
      shortLabel: 'ฉัน',
      icon: '👤',
      subtitle: 'จัดการโปรไฟล์ ที่อยู่นัดรับ และศูนย์ช่วยเหลือ',
    },
  ],
  collector: [
    {
      id: 'discover',
      label: 'หางานใกล้ฉัน',
      shortLabel: 'หางาน',
      icon: '🗺️',
      subtitle: 'ค้นหางานจากแผนที่และประเมินค่าน้ำมันก่อนกดรับ (S1 → S2)',
    },
    {
      id: 'active-route',
      label: 'คิวงานวันนี้',
      shortLabel: 'คิวงาน',
      icon: '🛵',
      subtitle: 'เส้นทางรับซื้อ แชตผู้ขาย ชั่งน้ำหนัก และออกใบเสร็จ (S2 → S7)',
    },
    {
      id: 'history',
      label: 'ประวัติ & ลูกค้าประจำ',
      shortLabel: 'ประวัติ',
      icon: '🤝',
      subtitle: 'สรุปยอดรับซื้อรายวันและรายชื่อลูกค้าประจำ (S7)',
    },
    {
      id: 'account',
      label: 'บัญชี & KYC',
      shortLabel: 'บัญชี',
      icon: '🪪',
      subtitle: 'ข้อมูลผู้ขับขี่ ความจุรถ และสถานะยืนยันตัวตน KYC (D-00-01)',
    },
  ],
  admin: [
    {
      id: 'admin-users',
      label: 'อนุมัติ KYC & บทลงโทษ',
      shortLabel: 'KYC',
      icon: '🪪',
      subtitle: 'ตรวจสอบเอกสารซาเล้งและจัดการบทลงโทษ (UC-11)',
    },
    {
      id: 'admin-pricing',
      label: 'ราคากลาง & เกณฑ์คัดแยก',
      shortLabel: 'ราคากลาง',
      icon: '📊',
      subtitle: 'ประกาศราคากลางประจำวันและเกณฑ์คัดเกรดวัสดุ (UC-12)',
    },
    {
      id: 'admin-dispatch',
      label: 'คิวงานตกค้าง & ข้อพิพาท',
      shortLabel: 'ข้อพิพาท',
      icon: '🚨',
      subtitle: 'จ่ายงานตกค้างและตัดสินข้อพิพาท S8 (UC-13)',
    },
    {
      id: 'admin-compliance',
      label: 'Audit Trail & PDPA',
      shortLabel: 'PDPA',
      icon: '🔒',
      subtitle: 'ตรวจสอบบันทึกความปลอดภัยและนโยบายเก็บข้อมูล (UC-13)',
    },
  ],
};

const PORTAL_LABELS = {
  seller: { name: 'ผู้ขาย (Seller)', badge: 'Seller', icon: '🛒' },
  collector: { name: 'ซาเล้ง (Buyer)', badge: 'Collector', icon: '🛺' },
  admin: { name: 'แอดมิน (Admin)', badge: 'Admin', icon: '🛡️' },
};

function readAdminSession() {
  if (window.localStorage.getItem('saleng_admin_session') !== 'authenticated') {
    return null;
  }
  try {
    const raw = window.localStorage.getItem('saleng_admin_profile');
    return raw ? JSON.parse(raw) : { username: 'admin', display_name: 'ผู้ดูแลระบบ' };
  } catch {
    return { username: 'admin', display_name: 'ผู้ดูแลระบบ' };
  }
}

export default function App() {
  const getRoleFromPath = () => {
    if (window.location.pathname.startsWith('/buyer')) return 'collector';
    if (window.location.pathname.startsWith('/admin')) return 'admin';
    return 'seller';
  };

  const initialRole = getRoleFromPath();
  const [activeRole, setActiveRole] = useState(initialRole);
  const [activeSection, setActiveSection] = useState(PRIMARY_NAV[initialRole][0].id);

  // Journey Sub-States (แยกตาม Flow จริงของแต่ละหมวด)
  const [sellStep, setSellStep] = useState(1); // 1: โพสต์, 2: ประเมินราคา, 3: เลือกซาเล้ง
  const [sellDraftItems, setSellDraftItems] = useState([]);
  const [activeOrderId, setActiveOrderId] = useState(null);
  const [matchedCollectorOrder, setMatchedCollectorOrder] = useState(null);
  const [liveOrderStatus, setLiveOrderStatus] = useState(null);
  const [liveSalengId, setLiveSalengId] = useState(null);
  const [autoJumpedOrderId, setAutoJumpedOrderId] = useState(null);
  const [selectedPickupLocation, setSelectedPickupLocation] = useState(null);
  const [pickupModalOpen, setPickupModalOpen] = useState(false);
  const [orderTab, setOrderTab] = useState('tracking'); // 'tracking' | 'payment' | 'history'
  const [showSosDrawer, setShowSosDrawer] = useState(false); // SOS ฝังในหน้าติดตามงาน (S3..S6)
  const [sellerMeTab, setSellerMeTab] = useState('profile'); // 'profile' | 'help'

  const [selectedEvalOrderId, setSelectedEvalOrderId] = useState(null);
  const [routeSubView, setRouteSubView] = useState('queue'); // 'queue' | 'gps' | 'chat' | 'billing'
  const [selectedQueueOrderId, setSelectedQueueOrderId] = useState(null);
  const [navigatingJob, setNavigatingJob] = useState(null);

  // Independent Auth Sessions for all 3 portals
  const [sellerSession, setSellerSession] = useState(() => accountApi.getStoredSession());
  const [collectorSession, setCollectorSession] = useState(() =>
    collectorAccountApi.getStoredSession()
  );
  const [adminSession, setAdminSession] = useState(() => readAdminSession());

  const currentSession =
    activeRole === 'seller'
      ? sellerSession
      : activeRole === 'collector'
      ? collectorSession
      : adminSession;

  const navigateToRole = (role) => {
    const path = role === 'collector' ? '/buyer' : `/${role}`;
    window.history.pushState({}, '', path);
    setActiveRole(role);
    setActiveSection(PRIMARY_NAV[role][0].id);
    setShowSosDrawer(false);
  };

  const handleAuthenticated = (role, sessionData) => {
    if (role === 'seller') setSellerSession(sessionData);
    if (role === 'collector') setCollectorSession(sessionData);
    if (role === 'admin') setAdminSession(sessionData);
    setActiveSection(PRIMARY_NAV[role][0].id);
  };

  const handleLogout = async () => {
    if (activeRole === 'seller') {
      await accountApi.logout().catch(() => {});
      window.localStorage.removeItem('saleng_seller_token');
      window.localStorage.removeItem('saleng_seller_profile');
      setSellerSession(null);
    } else if (activeRole === 'collector') {
      await collectorAccountApi.logout().catch(() => {});
      window.localStorage.removeItem('saleng_collector_session');
      window.localStorage.removeItem('saleng_collector_profile');
      setCollectorSession(null);
    } else {
      window.localStorage.removeItem('saleng_admin_session');
      window.localStorage.removeItem('saleng_admin_profile');
      setAdminSession(null);
    }
  };

  // บังคับหน้า Login / Register เป็นหน้าแรกเสมอของทั้ง 3 พอร์ทัล
  if (!currentSession) {
    return (
      <ShopeeAuthGate
        activeRole={activeRole}
        onSwitchRole={navigateToRole}
        onAuthenticated={handleAuthenticated}
      />
    );
  }

  const navItems = PRIMARY_NAV[activeRole];
  const currentNav = navItems.find((item) => item.id === activeSection) || navItems[0];
  const portalInfo = PORTAL_LABELS[activeRole];
  const displayName =
    currentSession.display_name || currentSession.username || 'ผู้ใช้งาน Saleng';

  return (
    <div className="min-h-screen flex flex-col sp-page-bg pb-20 md:pb-0">
      {/* Header: Slim Black Utility Bar + Clean Golden Yellow Main Nav */}
      <header className="sp-header-gradient sticky top-0 z-40">
        {/* Top Utility Bar (Jet Black) */}
        <div className="sp-topbar">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-2 flex flex-wrap items-center justify-between gap-2 text-xs">
            {/* 3-Portal Switcher */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              {['seller', 'collector', 'admin'].map((role) => {
                const isCurrent = activeRole === role;
                const isLoggedIn =
                  role === 'seller'
                    ? Boolean(sellerSession)
                    : role === 'collector'
                    ? Boolean(collectorSession)
                    : Boolean(adminSession);
                return (
                  <button
                    key={role}
                    type="button"
                    onClick={() => navigateToRole(role)}
                    className={`px-2.5 py-1 rounded-full transition flex items-center gap-1 ${
                      isCurrent
                        ? 'bg-yellow-400 text-black font-bold'
                        : 'text-zinc-300 hover:text-yellow-300'
                    }`}
                  >
                    <span>{PORTAL_LABELS[role].icon}</span>
                    <span>{PORTAL_LABELS[role].name}</span>
                    {!isLoggedIn && !isCurrent && <span className="opacity-70 text-[10px]">🔒</span>}
                  </button>
                );
              })}
            </div>

            {/* User & Logout */}
            <div className="flex items-center gap-3">
              <span className="font-medium text-yellow-300 flex items-center gap-1">
                <span>👤</span> {displayName}
              </span>
              <button
                type="button"
                onClick={handleLogout}
                className="px-3 py-1 sp-logout-btn text-xs"
              >
                ออกจากระบบ
              </button>
            </div>
          </div>
        </div>

        {/* Main Bar: Logo + 4 Primary Journey Tabs (Desktop) */}
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => setActiveSection(navItems[0].id)}
            className="flex items-center gap-2.5 text-left flex-shrink-0"
          >
            <span className="w-10 h-10 rounded-xl bg-black flex items-center justify-center text-2xl shadow">
              🛺
            </span>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight text-black">Saleng</span>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-black text-yellow-400">
                  {portalInfo.badge}
                </span>
              </div>
              <p className="text-[11px] text-black/75 font-medium hidden sm:block">
                แพลตฟอร์มรับซื้อของเก่าดิจิทัล
              </p>
            </div>
          </button>

          {/* Desktop 4 Primary Journey Navigation Pills */}
          <nav className="hidden md:flex items-center gap-2 overflow-x-auto sp-no-scrollbar">
            {navItems.map((item) => {
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveSection(item.id)}
                  className={`sp-nav-pill ${isActive ? 'sp-nav-pill-active' : ''}`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 space-y-5">
        {/* Clean Section Title Header */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-black flex items-center gap-2">
              <span>{currentNav.icon}</span>
              <span>{currentNav.label}</span>
            </h1>
            <p className="text-xs sm:text-sm text-zinc-600 mt-0.5">{currentNav.subtitle}</p>
          </div>
          {activeRole === 'seller' && activeSection === 'my-orders' && orderTab === 'tracking' && (
            <button
              type="button"
              onClick={() => setShowSosDrawer((prev) => !prev)}
              className={`px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition shadow-sm flex items-center gap-1.5 ${
                showSosDrawer
                  ? 'bg-red-600 text-white'
                  : 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100'
              }`}
            >
              <span>🚨</span>
              <span>{showSosDrawer ? 'ซ่อนแผงความปลอดภัย SOS' : 'ความปลอดภัย & ฉุกเฉิน SOS'}</span>
            </button>
          )}
        </div>

        {/* =======================================================
            SELLER PORTAL — JOURNEY BASED VIEWS
           ======================================================= */}
        {activeRole === 'seller' && activeSection === 'sell-flow' && (
          <div className="sp-workspace-card overflow-hidden">
            {/* 3-Step Visual Stepper (* -> S1 -> S2) */}
            <div className="p-4 sm:p-5 bg-zinc-50/70 border-b border-zinc-200">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                {[
                  { step: 1, title: 'โพสต์รายการของเก่า', desc: 'ถ่ายรูป & ระบุประเภท (S1)' },
                  { step: 2, title: 'ประเมินราคากลาง', desc: 'เช็กช่วงราคา & เกณฑ์ขั้นต่ำ' },
                  { step: 3, title: 'เลือกซาเล้งนัดรับ', desc: 'จับคู่ & ยืนยันเวลานัด (S2)' },
                ].map((s) => (
                  <button
                    key={s.step}
                    type="button"
                    onClick={() => setSellStep(s.step)}
                    className={`sp-step-btn ${sellStep === s.step ? 'sp-step-btn-active' : ''}`}
                  >
                    <span className="sp-step-num">{s.step}</span>
                    <div>
                      <div className="leading-tight">{s.title}</div>
                      <div className="text-[11px] font-normal text-zinc-500 mt-0.5">{s.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="p-5 sm:p-6">
              {sellStep === 1 && (
                <div>
                  <ScrapPostingPanel
                    sellerId={sellerSession?.seller_id || 'SEL-DEMO-01'}
                    pickupLocation={selectedPickupLocation}
                    onOpenLocationPicker={() => setPickupModalOpen(true)}
                    onItemsChange={setSellDraftItems}
                    onPostConfirmed={() => setSellStep(2)}
                  />

                  <PickupLocationModal
                    isOpen={pickupModalOpen}
                    location={selectedPickupLocation}
                    onClose={() => setPickupModalOpen(false)}
                    onSave={async (locData) => {
                      const sellerId = sellerSession?.seller_id || 'SEL-DEMO-01';
                      try {
                        const created = await accountApi.createLocation(sellerId, locData);
                        setSelectedPickupLocation(created);
                      } catch {
                        setSelectedPickupLocation({
                          location_id: `LOC-${Date.now()}`,
                          ...locData,
                        });
                      }
                      setPickupModalOpen(false);
                    }}
                  />
                </div>
              )}
              {sellStep === 2 && (
                <PricingDecisionPage
                  sellerId={sellerSession?.seller_id || 'SEL-DEMO-01'}
                  pickupLocationId={selectedPickupLocation?.location_id || 'LOC-DEMO-01'}
                  initialBasket={sellDraftItems}
                  showCalculator={false}
                  onOrderSubmitted={(orderData) => {
                    setActiveOrderId(orderData?.order_id || `ORD-${Date.now()}`);
                    setMatchedCollectorOrder(null);
                    setSellStep(3);
                  }}
                />
              )}
              {sellStep === 3 && (
                <BuyerSearchPanel
                  sellerId={sellerSession?.seller_id || 'SEL-DEMO-01'}
                  orderId={activeOrderId || 'ORD-DEMO-001'}
                  onOrderMatched={(matched) => {
                    setMatchedCollectorOrder(matched);
                    setSellStep(1);
                    setActiveSection('my-orders');
                    setOrderTab('tracking');
                  }}
                />
              )}

              {/* Stepper Footer Controls */}
              {sellStep > 1 && (
                <div className="mt-6 pt-4 border-t border-zinc-100 flex items-center justify-between">
                  <button
                    type="button"
                    onClick={() => setSellStep((s) => Math.max(1, s - 1))}
                    className="px-4 py-2 rounded-full text-xs sm:text-sm font-semibold border border-zinc-300 text-zinc-700 hover:bg-zinc-50"
                  >
                    ← ย้อนกลับขั้นก่อนหน้า
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeRole === 'seller' && activeSection === 'my-orders' && (
          <div className="space-y-4">
            {/* แถบแจ้งเตือนยืนยันหลังเลือกซาเล้งสำเร็จ */}
            {matchedCollectorOrder && (
              <div className="rounded-2xl p-4 bg-yellow-400 border-2 border-black shadow-sm flex items-start justify-between gap-3">
                <div>
                  <div className="text-sm font-extrabold text-black flex items-center gap-1.5">
                    <span>🎉</span>
                    <span>ส่งคำขอนัดหมายไปยังซาเล้งเรียบร้อยแล้ว (สถานะ: S2)</span>
                  </div>
                  <p className="text-xs text-black/85 mt-0.5">
                    {matchedCollectorOrder.message}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setMatchedCollectorOrder(null)}
                  className="text-xs font-bold px-2.5 py-1 rounded-full bg-black text-yellow-400 hover:bg-zinc-800 flex-shrink-0"
                >
                  ปิด
                </button>
              </div>
            )}

            {/* แถบแจ้งเตือนด่วนเมื่อซาเล้งถึงหน้างานและส่งผลชั่งน้ำหนักแล้ว (S5 / S6) */}
            {(liveOrderStatus === 'S5' || liveOrderStatus === 'S6') && orderTab !== 'payment' && (
              <div className="rounded-2xl p-4 bg-black text-white border-2 border-yellow-400 shadow-lg flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl animate-bounce">⚖️</span>
                  <div>
                    <div className="text-sm font-extrabold text-yellow-400">
                      ซาเล้งถึงหน้างานและส่งผลชั่งน้ำหนักแล้ว! (สถานะ: {liveOrderStatus})
                    </div>
                    <p className="text-xs text-zinc-300 mt-0.5">
                      กรุณาตรวจสอบภาพถ่ายตาชั่งและกดยืนยันตัวเลขน้ำหนักเพื่อดำเนินการชำระเงิน
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setOrderTab('payment');
                    setShowSosDrawer(false);
                  }}
                  className="px-4 py-2.5 rounded-full bg-yellow-400 hover:bg-yellow-300 text-black text-xs font-extrabold transition shadow"
                >
                  ตรวจสอบและยืนยันน้ำหนัก →
                </button>
              </div>
            )}

            {/* Inline SOS Safety Panel (เฉพาะตอนติดตามออเดอร์กำลังดำเนินการ S3..S6) */}
            {orderTab === 'tracking' && showSosDrawer && (
              <div className="sp-workspace-card p-5 border-2 border-red-200 bg-red-50/30">
                <TransactionSafetyPanel />
              </div>
            )}

            <div className="sp-workspace-card overflow-hidden">
              {/* Shopee-Style Order Status Tabs */}
              <div className="flex border-b border-zinc-200 overflow-x-auto sp-no-scrollbar bg-white px-2">
                <button
                  type="button"
                  onClick={() => setOrderTab('tracking')}
                  className={`sp-subtab ${orderTab === 'tracking' ? 'sp-subtab-active' : ''}`}
                >
                  📍 กำลังดำเนินการ (S2–S4)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setOrderTab('payment');
                    setShowSosDrawer(false);
                  }}
                  className={`sp-subtab ${orderTab === 'payment' ? 'sp-subtab-active' : ''}`}
                >
                  🧾 ตรวจรับ & ชำระเงิน (S5–S6)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setOrderTab('history');
                    setShowSosDrawer(false);
                  }}
                  className={`sp-subtab ${orderTab === 'history' ? 'sp-subtab-active' : ''}`}
                >
                  ⭐ สำเร็จแล้ว & รีวิว (S7)
                </button>
              </div>

              <div className="p-5 sm:p-6">
                {orderTab === 'tracking' &&
                  (activeOrderId || matchedCollectorOrder ? (
                    <BookingTrackingPanel
                      orderId={activeOrderId || 'ORD-ACTIVE-01'}
                      sellerId={sellerSession?.seller_id || 'SEL-DEMO-01'}
                      showSimulator={false}
                      onOrderUpdated={(updated) => {
                        if (updated?.status) setLiveOrderStatus(updated.status);
                        if (updated?.assigned_saleng?.saleng_id) {
                          setLiveSalengId(updated.assigned_saleng.saleng_id);
                        }
                        // เด้งไปหน้า "ตรวจรับ & ชำระเงิน" อัตโนมัติทันทีเมื่อซาเล้งถึงหน้างาน/ส่งผลชั่ง (S5/S6)
                        if (
                          (updated?.status === 'S5' || updated?.status === 'S6') &&
                          autoJumpedOrderId !== updated.order_id
                        ) {
                          setAutoJumpedOrderId(updated.order_id);
                          setOrderTab('payment');
                          setShowSosDrawer(false);
                        }
                      }}
                      initialOrder={{
                        order_id: activeOrderId || 'ORD-ACTIVE-01',
                        status: 'S2',
                        status_label: 'รอซาเล้งยืนยันและออกเดินทาง',
                        stepper_step: 2,
                        items_count: sellDraftItems.length,
                        total_estimated_price: {
                          min_price: sellDraftItems.reduce(
                            (sum, it) => sum + (Number(it.est_min_price) || 0),
                            0
                          ),
                          max_price: sellDraftItems.reduce(
                            (sum, it) => sum + (Number(it.est_max_price) || 0),
                            0
                          ),
                        },
                        scheduled_time_display: 'นัดหมายรับซื้อวันนี้ (รอซาเล้งตอบรับภายใน 15 นาที)',
                        assigned_saleng: matchedCollectorOrder
                          ? {
                              display_name: matchedCollectorOrder.saleng_name || 'ซาเล้งที่คุณเลือก',
                              vehicle_type: 'ซาเล้งสามล้อ',
                              rating: 4.9,
                              phone_masked: '08X-XXX-XXXX',
                            }
                          : null,
                        distance_km: 1.2,
                        eta_minutes: 12,
                        can_cancel: true,
                      }}
                    />
                  ) : (
                    <div className="bg-yellow-50 border-2 border-dashed border-yellow-400 rounded-2xl p-8 text-center space-y-3">
                      <div className="text-4xl">📦</div>
                      <h3 className="text-base font-extrabold text-black">
                        ยังไม่มีรายการขายที่กำลังดำเนินการ
                      </h3>
                      <p className="text-xs text-zinc-600">
                        เริ่มโพสต์รายการของเก่า ประเมินราคากลาง และเลือกซาเล้งเพื่อนัดรับได้เลย
                      </p>
                      <button
                        type="button"
                        onClick={() => {
                          setActiveSection('sell-flow');
                          setSellStep(1);
                        }}
                        className="px-6 py-2.5 sp-btn-primary text-xs sm:text-sm"
                      >
                        📦 เริ่มลงขายของเก่าเลย
                      </button>
                    </div>
                  ))}
                {orderTab === 'payment' && (
                  <PaymentVerificationPage
                    orderId={activeOrderId || 'ORD-TEST-001'}
                    sellerId={sellerSession?.seller_id || 'SEL-DEMO-01'}
                    salengId={
                      liveSalengId ||
                      matchedCollectorOrder?.assigned_saleng?.saleng_id ||
                      'saleng-01'
                    }
                  />
                )}
                {orderTab === 'history' && <SalesHistoryPage />}
              </div>
            </div>
          </div>
        )}

        {activeRole === 'seller' && activeSection === 'market-check' && (
          <div className="sp-workspace-card p-5 sm:p-6">
            <PricingDecisionPage />
          </div>
        )}

        {activeRole === 'seller' && activeSection === 'me' && (
          <div className="sp-workspace-card overflow-hidden">
            <div className="flex border-b border-zinc-200 bg-white px-2">
              <button
                type="button"
                onClick={() => setSellerMeTab('profile')}
                className={`sp-subtab ${sellerMeTab === 'profile' ? 'sp-subtab-active' : ''}`}
              >
                👤 โปรไฟล์ & ที่อยู่นัดรับ
              </button>
              <button
                type="button"
                onClick={() => setSellerMeTab('help')}
                className={`sp-subtab ${sellerMeTab === 'help' ? 'sp-subtab-active' : ''}`}
              >
                💡 ศูนย์ช่วยเหลือ & FAQ
              </button>
            </div>
            <div className="p-5 sm:p-6">
              {sellerMeTab === 'profile' && <AccountAccessPanel />}
              {sellerMeTab === 'help' && <HelpCenterPage />}
            </div>
          </div>
        )}

        {/* =======================================================
            COLLECTOR (BUYER) PORTAL — REAL END-TO-END JOURNEY
           ======================================================= */}
        {activeRole === 'collector' && activeSection === 'discover' && (
          <div className="sp-workspace-card p-5 sm:p-6">
            <IncomingDirectOrdersCard
              salengId={collectorSession?.saleng_id || 'saleng-01'}
              onAccepted={async (req) => {
                const sid = collectorSession?.saleng_id || 'saleng-01';
                try {
                  await jobRouteApi.startTransit(req.order_id, {
                    saleng_id: sid,
                    current_lat: 13.790,
                    current_lng: 100.575,
                  });
                } catch {
                  // continue to GPS simulation even if already S4
                }
                setSelectedEvalOrderId(null);
                setSelectedQueueOrderId(req.order_id);
                setNavigatingJob({
                  order_id: req.order_id,
                  total_est_weight_kg: req.total_est_weight_kg,
                  total_est_price_min: req.total_est_min_price,
                  total_est_price_max: req.total_est_max_price,
                  distance_km: 1.2,
                  dest_lat: 13.7955,
                  dest_lng: 100.5815,
                });
                setRouteSubView('gps');
                setActiveSection('active-route');
              }}
            />
            {selectedEvalOrderId ? (
              <JobEvaluationView
                orderId={selectedEvalOrderId}
                salengId={collectorSession?.saleng_id || 'saleng-01'}
                onNavigateBack={() => setSelectedEvalOrderId(null)}
                onNavigateKyc={() => {
                  setSelectedEvalOrderId(null);
                  setActiveSection('account');
                }}
                onClaimSuccess={async (evalData) => {
                  const sid = collectorSession?.saleng_id || 'saleng-01';
                  try {
                    await jobRouteApi.claimJob(selectedEvalOrderId, {
                      saleng_id: sid,
                      expected_version: evalData?.order_version || 1,
                    });
                    await jobRouteApi.startTransit(selectedEvalOrderId, {
                      saleng_id: sid,
                      current_lat: 13.790,
                      current_lng: 100.575,
                    });
                  } catch {
                    // continue to GPS simulation
                  }
                  setSelectedQueueOrderId(selectedEvalOrderId);
                  setNavigatingJob({
                    order_id: selectedEvalOrderId,
                    total_est_weight_kg: evalData?.total_est_weight_kg || 20,
                    total_est_price_min: evalData?.total_min_price || 500,
                    total_est_price_max: evalData?.total_max_price || 800,
                    distance_km: evalData?.road_distance_km || 1.2,
                    dest_lat: 13.7955,
                    dest_lng: 100.5815,
                  });
                  setSelectedEvalOrderId(null);
                  setRouteSubView('gps');
                  setActiveSection('active-route');
                }}
              />
            ) : (
              <JobSearchPanel
                collectorProfile={collectorSession}
                onNavigateToKyc={() => setActiveSection('account')}
                onJobAccepted={(job) => {
                  setSelectedEvalOrderId(job?.order_id || null);
                }}
              />
            )}
          </div>
        )}

        {activeRole === 'collector' && activeSection === 'active-route' && (
          <div className="sp-workspace-card p-5 sm:p-6">
            {routeSubView === 'queue' && (
              <IncomingDirectOrdersCard
                salengId={collectorSession?.saleng_id || 'saleng-01'}
                onAccepted={async (req) => {
                  const sid = collectorSession?.saleng_id || 'saleng-01';
                  try {
                    await jobRouteApi.startTransit(req.order_id, {
                      saleng_id: sid,
                      current_lat: 13.790,
                      current_lng: 100.575,
                    });
                  } catch {
                    // ignore
                  }
                  setSelectedQueueOrderId(req.order_id);
                  setNavigatingJob({
                    order_id: req.order_id,
                    total_est_weight_kg: req.total_est_weight_kg,
                    total_est_price_min: req.total_est_min_price,
                    total_est_price_max: req.total_est_max_price,
                    distance_km: 1.2,
                    dest_lat: 13.7955,
                    dest_lng: 100.5815,
                  });
                  setRouteSubView('gps');
                }}
              />
            )}
            {routeSubView === 'queue' && (
              <ActiveJobQueueView
                salengId={collectorSession?.saleng_id || 'saleng-01'}
                onStartNavigation={(job) => {
                  setSelectedQueueOrderId(job.order_id);
                  setNavigatingJob(job);
                  setRouteSubView('gps');
                }}
                onOpenChat={(job) => {
                  setSelectedQueueOrderId(job.order_id);
                  setRouteSubView('chat');
                }}
                onOpenBilling={(job) => {
                  setSelectedQueueOrderId(job.order_id);
                  setRouteSubView('billing');
                }}
              />
            )}
            {routeSubView === 'gps' && (
              <CollectorGpsNavigationView
                job={navigatingJob}
                salengId={collectorSession?.saleng_id || 'saleng-01'}
                durationSeconds={10}
                onBack={() => setRouteSubView('queue')}
                onOpenChat={(job) => {
                  setSelectedQueueOrderId(job?.order_id || selectedQueueOrderId);
                  setRouteSubView('chat');
                }}
                onArrivedOpenBilling={(job) => {
                  setSelectedQueueOrderId(job?.order_id || selectedQueueOrderId);
                  setRouteSubView('billing');
                }}
              />
            )}
            {routeSubView === 'chat' && (
              <ChatView
                orderId={selectedQueueOrderId || activeOrderId || 'order-s2-01'}
                salengId={collectorSession?.saleng_id || 'saleng-01'}
                onBack={() => setRouteSubView('queue')}
              />
            )}
            {routeSubView === 'billing' && (
              <BillingReceiptView
                orderId={selectedQueueOrderId || activeOrderId || 'order-01'}
                salengId={collectorSession?.saleng_id || 'saleng-01'}
                onBack={() => setRouteSubView('queue')}
              />
            )}
          </div>
        )}

        {activeRole === 'collector' && activeSection === 'history' && (
          <div className="sp-workspace-card p-5 sm:p-6">
            <PostJobCollectorView salengId={collectorSession?.saleng_id || 'saleng-01'} />
          </div>
        )}

        {activeRole === 'collector' && activeSection === 'account' && (
          <div className="sp-workspace-card p-5 sm:p-6">
            <CollectorAccountPanel showDevTools={false} />
          </div>
        )}

        {/* =======================================================
            ADMIN PORTAL — 4 BACK-OFFICE MODULES
           ======================================================= */}
        {activeRole === 'admin' && (
          <div className="sp-workspace-card p-5 sm:p-6">
            {activeSection === 'admin-users' && <AdminUserVerificationView />}
            {activeSection === 'admin-pricing' && <AdminBenchmarkGradingView />}
            {activeSection === 'admin-dispatch' && <AdminDispatchDisputeView />}
            {activeSection === 'admin-compliance' && <AdminSecurityComplianceView />}
          </div>
        )}
      </main>

      {/* Mobile Bottom Tab Bar (ตรงกับ 4 หมวดหลักของแต่ละพอร์ทัลแบบ 1:1) */}
      <nav className="sp-bottom-nav md:hidden">
        <div className="grid grid-cols-4 py-1.5">
          {navItems.map((item) => {
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveSection(item.id)}
                className={`flex flex-col items-center justify-center py-1 text-[11px] font-medium ${
                  isActive ? 'text-yellow-400 font-bold' : 'text-zinc-400'
                }`}
              >
                <span className="text-lg leading-none mb-0.5">{item.icon}</span>
                <span>{item.shortLabel}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <footer className="bg-black border-t-2 border-yellow-400 py-4 text-center text-xs text-yellow-300 mt-auto">
        Saleng Digital Scrap Platform &copy; 2026 รายวิชา 517 511 Requirements Engineering (กลุ่ม 2)
      </footer>
    </div>
  );
}
