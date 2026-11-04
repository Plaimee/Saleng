# แผนสถาปัตยกรรมและเทคโนโลยี: ระบบหลังจบงานฝั่งซาเล้ง (`specs/buyer/07-post-job/plan.md`)

- **Version:** `1.0` | **Status:** `ready-for-tasks` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิงสเปก:** [`specs/buyer/07-post-job/spec.md`](./spec.md) (v2.0)
- **Use Cases หลัก:** `UC-10: ให้คะแนนรีวิว สรุปยอดรายวัน และจัดการหลังจบงาน`, `UC-13: ตัดสินข้อพิพาทและงานตกค้าง` ([`docs/srs/use-cases.md`](../../../docs/srs/use-cases.md))
- **ข้อจำกัดกลาง:** [`specs/000-shared/constraints.md`](../../000-shared/constraints.md) (`CC-01..CC-06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)

---

## 1. เทคโนโลยีที่ใช้ (Technology Stack & Architecture)

> [!NOTE]
> **หมายเหตุด้านเทคโนโลยี:** เทคโนโลยีที่ใช้ในโมดูลนี้ **`"ทีมเลือกเอง ไม่ได้มาจาก spec"`** เพื่อให้สอดคล้องกับโครงสร้างและฐานโค้ดที่สร้างไว้แล้วใน Buyer Feature 01..06:

- **Backend Framework:** **Python 3.11 + FastAPI**
  - สถาปัตยกรรมแบบแยกส่วน: Router (`api/v1/post_job.py`), Service Layer (`services/post_job_service.py`), และ Data Models (`models/post_job_models.py`)
  - ตรวจสอบความถูกต้องของข้อมูลด้วย **Pydantic v2**
  - การจัดการ HTTP Status Code ตามมาตรฐาน REST (`200 OK`, `201 Created`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`)
- **Database & Storage:** **Supabase (PostgreSQL 15+)**
  - ตาราง `waste_pickup_orders` (สถานะ `S7: Completed`, `S8: Disputed`), `collector_favorite_sellers`, `dispute_reports`, `digital_receipts`, และ `audit_logs`
  - รองรับ Concurrency Control ด้วยคอลัมน์ `version` (Optimistic Locking ตาม `CC-04`)
- **Frontend Framework:** **React 18 + Vite + TailwindCSS**
  - ออกแบบเป็น Single-Page Application (SPA) แบบ Mobile-First ตามข้อกำหนด `CC-01`
  - ขนาดทัชทาร์เก็ตปุ่มกดและช่องป้อนข้อมูล `>= 48px` ทุกชิ้นตาม `REQ-UX-001`
  - รองรับการทำงานในจุดอับสัญญาณด้วย LocalStorage Caching (`CC-05`, `REQ-OP-001`)
- **Automated Testing:**
  - Backend: **Pytest** + `TestClient` (FastAPI)
  - Frontend: **Vitest + React Testing Library + JSDOM**

---

## 2. โครงสร้างไฟล์และโมดูล (File & Module Structure)

```
Saleng/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── post_job.py                  # [NEW] FastAPI Router สำหรับระบบหลังจบงานซาเล้ง
│   │   │   └── pricing.py                   # [UPDATE] เมานต์ post_job_router เข้ากับแอปหลัก
│   │   ├── core/
│   │   │   └── supabase.py                  # [UPDATE] ขยาย store เพิ่ม favorite_sellers และ disputes
│   │   ├── models/
│   │   │   └── post_job_models.py           # [NEW] Pydantic Schemas สำหรับประวัติ, ลูกค้าประจำ, และข้อพิพาท
│   │   └── services/
│   │       └── post_job_service.py          # [NEW] Service จัดการประวัติรับซื้อ, ลูกค้าประจำ, และรายงานข้อพิพาท
│   └── tests/
│       ├── test_T01_post_job_models.py      # [NEW] ทดสอบ Data Models & Supabase Store
│       ├── test_AC_B07_01_history_log.py    # [NEW] ทดสอบประวัติการรับซื้อและสถิติสะสม
│       ├── test_AC_B07_02_regular_customer.py# [NEW] ทดสอบปักหมุดลูกค้าประจำและบันทึกย่อ
│       ├── test_AC_B07_03_seller_mismatch.py# [NEW] ทดสอบรายงานผู้ขายกรณี No-show / ของไม่ตรง (S3/S4 -> S8)
│       └── test_e2e_buyer_post_job.py       # [NEW] ทดสอบ Integration E2E ครบวงจร
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PurchaseHistoryCard.jsx      # [NEW] การ์ดแสดงประวัติคำขอย้อนหลัง + PII Masking
│   │   │   ├── RegularCustomerList.jsx      # [NEW] หน้ารายการลูกค้าประจำพร้อมปุ่มนำทางและบันทึกย่อ
│   │   │   ├── SellerMismatchReportModal.jsx# [NEW] โมดอลส่งรายงานปัญหาหน้างาน / No-show (ปุ่ม >= 48px)
│   │   │   └── PostJobCollectorView.jsx     # [NEW] หน้าจอหลักรวบรวมประวัติและลูกค้าประจำ (data-req="UC-10")
│   │   └── services/
│   │       └── postJobApi.js                # [NEW] Frontend API Client พร้อมระบบ Offline Cache
│   └── tests/
│       ├── postJobApi.test.mjs              # [NEW] ทดสอบ Vitest สำหรับ postJobApi
│       ├── AC-B07-01.test.jsx               # [NEW] ทดสอบหน้ารวมประวัติการรับซื้อ
│       ├── AC-B07-02.test.jsx               # [NEW] ทดสอบปักหมุดลูกค้าประจำ
│       └── AC-B07-03.test.jsx               # [NEW] ทดสอบโมดอลรายงานข้อพิพาทหน้างาน
```

---

## 3. แบบจำลองข้อมูลและฐานข้อมูล (Data Models & Database Schema)

### 3.1 ตาราง `collector_favorite_sellers` (ลูกค้าประจำ)
| ฟิลด์ | ชนิดข้อมูล | เงื่อนไข | คำอธิบาย |
|---|---|---|---|
| `id` | `VARCHAR(64)` | `PRIMARY KEY` | รหัสอ้างอิงรายการบันทึก |
| `collector_id` | `VARCHAR(64)` | `NOT NULL, INDEX` | รหัสซาเล้งผู้บันทึก |
| `seller_id` | `VARCHAR(64)` | `NOT NULL, INDEX` | รหัสผู้ขายลูกค้าประจำ |
| `seller_name` | `VARCHAR(128)` | `NOT NULL` | ชื่อผู้ขาย / ป้ายกำกับที่ซาเล้งเรียก |
| `seller_phone_masked` | `VARCHAR(20)` | `NOT NULL` | เบอร์โทรศัพท์ที่ Mask แล้ว (`08X-XXX-XXXX`) ตาม PDPA |
| `latitude` | `FLOAT` | `NOT NULL` | ละติจูดจุดนัดรับเพื่อการวางแผนเส้นทาง |
| `longitude` | `FLOAT` | `NOT NULL` | ลองจิจูดจุดนัดรับเพื่อการวางแผนเส้นทาง |
| `notes` | `VARCHAR(200)` | `NULLABLE` | บันทึกย่อส่วนตัวของซาเล้ง (เช่น "บ้านรั้วสีฟ้า สะดวกเสาร์-อาทิตย์") |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | วันที่บันทึกลูกค้าประจำ |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | วันที่แก้ไขบันทึกย่อล่าสุด |

### 3.2 ตาราง `dispute_reports` (รายงานข้อพิพาทหน้างาน)
| ฟิลด์ | ชนิดข้อมูล | เงื่อนไข | คำอธิบาย |
|---|---|---|---|
| `dispute_id` | `VARCHAR(64)` | `PRIMARY KEY` | รหัสข้อพิพาท (`DISP-YYYYMMDD-XXXX`) |
| `order_id` | `VARCHAR(64)` | `NOT NULL, INDEX` | รหัสคำขอขายที่เกิดปัญหา |
| `reporter_id` | `VARCHAR(64)` | `NOT NULL` | รหัสซาเล้งผู้รายงาน |
| `reporter_role` | `VARCHAR(32)` | `DEFAULT 'COLLECTOR'` | บทบาทผู้รายงาน |
| `mismatch_reason` | `VARCHAR(64)` | `NOT NULL` | สาเหตุ: `SELLER_NO_SHOW`, `CONTAMINATED_WASTE`, `QUANTITY_MISMATCH`, `OTHER` |
| `evidence_photo_url` | `TEXT` | `NOT NULL` | URL รูปถ่ายหลักฐานหน้างาน (บังคับตาม `REQ-FN-006`) |
| `notes` | `TEXT` | `NULLABLE` | คำอธิบายรายละเอียดเหตุการณ์ |
| `gps_lat` | `FLOAT` | `NULLABLE` | ละติจูดขณะกดรายงานเพื่อยืนยันว่าถึงหน้างานจริง |
| `gps_lng` | `FLOAT` | `NULLABLE` | ลองจิจูดขณะกดรายงาน |
| `status` | `VARCHAR(32)` | `DEFAULT 'PENDING_ADMIN'` | สถานะข้อพิพาทรอ Admin ตัดสิน (`UC-13`) |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | วันและเวลาที่ส่งรายงาน |

---

## 4. ข้อกำหนดการเชื่อมต่อ API (API Specification & Contracts)

### 4.1 `GET /api/v1/collectors/post-job/history`
- **คำอธิบาย:** ดึงประวัติการรับซื้อของเก่าที่เสร็จสิ้นแล้ว (`S7: Completed`) พร้อมสถิติสะสม 3 มิติ และตัวกรองช่วงเวลา
- **Query Parameters:**
  - `saleng_id` (string, required): รหัสซาเล้งผู้เข้าใช้งาน
  - `period` (string, optional): ช่วงเวลาที่ต้องการสรุป (`all`, `today`, `month`) ค่าเริ่มต้น `all`
- **Response Model:** `PurchaseHistoryResponse`
  ```json
  {
    "period": "all",
    "summary": {
      "total_expense_baht": 1450.0,
      "total_weight_kg": 320.5,
      "total_completed_jobs": 6
    },
    "items": [
      {
        "order_id": "order-101",
        "completed_at": "2026-11-04T10:30:00Z",
        "seller_name": "คุณวิภาดา",
        "seller_phone_masked": "08X-XXX-4567",
        "total_settled_amount": 350.0,
        "total_weight_kg": 70.0,
        "payment_method": "PROMPTPAY",
        "status": "S7",
        "is_regular_customer": true,
        "items_summary": "กระดาษลัง (50 กก.), ขวดแก้วใส (20 กก.)"
      }
    ]
  }
  ```

### 4.2 `GET /api/v1/collectors/post-job/regular-customers`
- **คำอธิบาย:** ดึงรายชื่อลูกค้าประจำที่ซาเล้งปักหมุดไว้ พร้อมพิกัดและบันทึกย่อ
- **Query Parameters:**
  - `saleng_id` (string, required): รหัสซาเล้งผู้เข้าใช้งาน
- **Response Model:** `List[RegularCustomerItem]`

### 4.3 `POST /api/v1/collectors/post-job/regular-customers`
- **คำอธิบาย:** สลับสถานะ (Toggle Bookmark) เพิ่มหรือลบผู้ขายออกจากรายการลูกค้าประจำ
- **Request Body:**
  ```json
  {
    "saleng_id": "saleng-01",
    "seller_id": "seller-01",
    "notes": "บ้านรั้วสีฟ้า สะดวกช่วงบ่ายเสาร์-อาทิตย์",
    "latitude": 13.7563,
    "longitude": 100.5018
  }
  ```
- **Response:** `ToggleRegularCustomerResponse` (`status="success"`, `is_favorite=true/false`)

### 4.4 `POST /api/v1/collectors/post-job/report-mismatch`
- **คำอธิบาย:** ซาเล้งรายงานผู้ขายกรณี No-show หรือของไม่ตรงสเปก (S3/S4 -> S8)
- **Request Body:**
  ```json
  {
    "saleng_id": "saleng-01",
    "order_id": "order-102",
    "mismatch_reason": "SELLER_NO_SHOW",
    "evidence_photo_url": "https://storage.saleng.app/disputes/no-show-102.jpg",
    "notes": "เดินทางไปถึงหน้าบ้านตามเวลานัดแล้ว โทรติดต่อผู้ขาย 3 ครั้งไม่มีผู้รับสาย",
    "current_lat": 13.7563,
    "current_lng": 100.5018
  }
  ```
- **Response:** `ReportSellerMismatchResponse` (`status="success"`, `new_status="S8"`, `dispute_id="DISP-..."`)

---

## 5. แผนการเชื่อมต่อระบบภายนอกและการจำลอง (External Integrations & Fallbacks)

1. **ระบบเก็บรูปภาพหลักฐานข้อพิพาท (Cloud Object Storage):**
   - รูปภาพหลักฐานหน้างาน (`evidence_photo_url`) จำลอง URL ที่จัดเก็บบน Cloud Storage มีการตรวจสอบความถูกต้องของ URL และบังคับไม่ให้เป็นค่าว่างตาม `REQ-FN-006`
2. **ระบบแผนที่นำทางไปยังพิกัดลูกค้าประจำ (Native Map Launch):**
   - ปุ่ม "นำทางไปยังบ้านลูกค้าประจำ" ใช้ Deep Link `geo:lat,lng` หรือ `https://maps.google.com/?q=lat,lng` สำหรับเปิดแอปแผนที่นำทางบนอุปกรณ์
3. **ระบบออฟไลน์แคช (Offline Local Storage):**
   - เมื่อไม่มีสัญญาณเน็ต หน้ารวมประวัติการรับซื้อและรายการลูกค้าประจำจะเปิดอ่านข้อมูลที่แคชไว้ใน `localStorage` (`saleng_purchase_history_cache`, `saleng_regular_customers_cache`) ทันทีตาม `CC-05` และ `REQ-OP-001`

---

## 6. การออกแบบหน้าจอและประสบการณ์ผู้ใช้ (UI/UX Design & Component Hierarchy)

```
[PostJobCollectorView (data-req="UC-10")]
├── Header Bar (ชื่อหน้าจอ, ยอดรวมสะสม, ปุ่มสลับแท็บ)
├── Tab Navigation:
│   ├── Tab 1: "ประวัติการรับซื้อ" (Purchase History)
│   │   ├── Period Filter Bar (ทั้งหมด | วันนี้ | เดือนนี้)
│   │   ├── Summary Cards (ยอดจ่าย ฿ | น้ำหนักรวม กก. | จำนวนงาน)
│   │   └── PurchaseHistoryCard List:
│   │       ├── วันที่, รหัสคำขอ, ชื่อผู้ขาย, เบอร์ Mask (08X-XXX-XXXX)
│   │       ├── รายการของเก่าและยอดเงินสุทธิ
│   │       ├── ปุ่ม "ดูใบเสร็จดิจิทัล" (DigitalReceiptModal)
│   │       └── ปุ่ม "ลูกค้าประจำ" (ปักหมุด/สลับสถานะ)
│   └── Tab 2: "ลูกค้าประจำ" (Regular Customers)
│       ├── Search / Filter Bar
│       └── RegularCustomerList:
│           ├── ชื่อลูกค้า, เบอร์ Mask, บันทึกย่อช่วยจำ (Notes)
│           ├── ปุ่ม "นำทางบนแผนที่" (>= 48px)
│           └── ปุ่ม "แก้ไขบันทึก / ลบออก" (>= 48px)
└── Global Modal:
    └── [SellerMismatchReportModal] (เปิดจากหน้างาน S3 หรือ S4)
        ├── ตัวเลือกสาเหตุ (No-show, ของปนเปื้อน, ปริมาณไม่ตรง)
        ├── ช่องแนบรูปหลักฐานหน้าตาชั่งหรือหน้าบ้าน
        ├── ช่องระบุบันทึกข้อความเหตุการณ์
        └── ปุ่ม "ส่งรายงานข้อพิพาท (S8)" (>= 48px, สีแดง/ส้ม)
```

---

## 7. การจัดการคำถามเปิดและสมมติฐาน (Decisions, Assumptions & Constraints)

| รหัส | หัวข้อการตัดสินใจ / สมมติฐาน | รายละเอียดและที่มา |
|:---:|:---|:---|
| **`D-B07-01`** | สถานะปลายทางของการรายงานข้อพิพาทคือ `S8: Disputed` | เมื่อซาเล้งกดรายงานปัญหาหน้างาน คำขอจะเปลี่ยนเป็น `S8` เพื่อส่งเข้าศูนย์ควบคุมข้อพิพาทของ Admin (`UC-13`) และปลดล็อกซาเล้งออกจากงานทันที (จาก `Q-01`) |
| **`D-B07-02`** | จุดที่รายงานผู้ขายได้ครอบคลุมทั้ง `S3` และ `S4` | อนุญาตให้รายงานได้จาก `S3: En Route` (กรณี No-show) และ `S4: Weighing` (กรณีของปนเปื้อน/ไม่ตรงสเปก) (จาก `Q-02`) |
| **`D-B07-03`** | โครงสร้างตารางลูกค้าประจำตามหลัก PDPA | จัดเก็บพิกัดเพื่อการวางแผนเส้นทางและบันทึกย่อช่วยจำ แต่ Mask เบอร์โทรศัพท์เป็น `08X-XXX-XXXX` และไม่เปิดเผยบ้านเลขที่เกิน 24 ชม. ตาม `REQ-SEC-002` (จาก `Q-03`) |
| **`D-B07-04`** | ซาเล้งไม่มีการให้คะแนนดาว 1–5 ดาวแก่ผู้ขาย | รักษาความเรียบง่ายและไม่เพิ่มสเปกที่อยู่นอก SRS โดยซาเล้งใช้ระบบ Bookmark และ Dispute Report เท่านั้น (จาก `Q-04`) |
| **`D-B07-05`** | สถิติสรุปสะสม 3 มิติในหน้าประวัติ | คำนวณยอดจ่ายรวม (บาท), น้ำหนักรวม (กก.), และจำนวนงานสำเร็จ (ครั้ง) พร้อมตัวกรองรายวัน/รายเดือน (จาก `Q-05`) |
| **`D-B07-06`** | ขอบเขตสิ่งที่ไม่ทำ (Non-goals) ชัดเจน | ไม่ทำแชทคุยต่อหลังจบงาน, ไม่จ่ายเงินชดเชยค่าเดินทางอัตโนมัติ, ไม่เปิดเผย PII ที่ไม่ Mask เกิน 24 ชม., และไม่ทำระบบรีวิวดาวผู้ขาย (จาก `Q-06`) |

---

## 8. ตารางตรวจสอบข้อจำกัดกลาง (Constraints Traceability Table)

| รหัส Constraint | ข้อกำหนดใน Constraint กลาง (`specs/000-shared/constraints.md`) | การปฏิบัติตามในโมดูล Buyer 07 (แผนงานนี้) |
|:---:|:---|:---|
| **`CC-01`** | Mobile-First Web SPA (`RAM >= 2 GB`, ปุ่มกด `>= 48px`) | หน้าจอทุกคอมโพเนนต์พัฒนาด้วย React 18 + TailwindCSS ปุ่มกดทุกปุ่ม (ปุ่มเปิดใบเสร็จ, ปุ่มปักหมุดลูกค้าประจำ, ปุ่มส่งรายงานข้อพิพาท) มีความสูงไม่น้อยกว่า `48px` |
| **`CC-02`** | GPS Sync Interval ทุก 60 วินาทีขณะ Online | บันทึกพิกัด GPS ขณะกดรายงานข้อพิพาทหน้างาน เพื่อพิสูจน์ว่าซาเล้งเดินทางไปถึงจุดนัดหมายจริง |
| **`CC-03`** | Road Distance API รัศมี <= 5.0 กม. พร้อม Haversine Fallback | ไม่เกี่ยวข้องโดยตรงกับการแสดงประวัติ แต่พิกัดลูกค้าประจำที่บันทึกไว้จะถูกส่งต่อให้ระบบจัดเส้นทาง (Buyer 03, 04) ในรอบถัดไป |
| **`CC-04`** | PostgreSQL + Concurrency Control / Optimistic Locking | ใช้ Optimistic Locking ผ่านฟิลด์ `version` ในตารางคำขอ ป้องกันการส่งรายงานซ้ำซ้อน |
| **`CC-05`** | Offline Cache ใน IndexedDB / Local Storage | แคชรายการประวัติการรับซื้อและรายชื่อลูกค้าประจำลงใน `localStorage` เพื่อให้เปิดดูได้ในจุดอับสัญญาณ |
| **`CC-06`** | PDPA & PII Masking ซ่อนบ้านเลขที่และพิกัดละเอียด | ปกปิดเบอร์โทรศัพท์ของผู้ขายบนหน้าประวัติและรายการลูกค้าประจำให้เป็น `08X-XXX-XXXX` เสมอ และซ่อนบ้านเลขที่หลังจบงานเกิน 24 ชม. |
| **`REQ-SEC-001`** | บันทึกประวัติลงตาราง Audit Log | บันทึกประวัติการส่งรายงานข้อพิพาท (`COLLECTOR_REPORTED_MISMATCH`) และการปักหมุดลูกค้าประจำ (`COLLECTOR_BOOKMARKED_CUSTOMER`) ลงใน `audit_logs` |
| **`REQ-SEC-002`** | ปกปิดข้อมูลส่วนบุคคล (PII) ของผู้ขาย | ปกปิดข้อมูลเบอร์โทรศัพท์และที่อยู่ละเอียดของผู้ขายในทุกจุดแสดงผลของโมดูลนี้ |
| **`REQ-OP-001`** | โหมด Offline Cache สำหรับดูข้อมูลที่แคชไว้ | รองรับการเปิดดูประวัติการรับซื้อและใบเสร็จดิจิทัลย้อนหลังที่เคยแคชไว้ได้แม้อุปกรณ์ออฟไลน์ |
| **`REQ-OP-002`** | Haversine Fallback สำหรับการคำนวณระยะทาง | ไม่เกี่ยวข้องโดยตรงกับระบบประวัติและลูกค้าประจำ |
| **`D-00-01`** | KYC เป็น Precondition ของระบบผู้ซื้อ | ตรวจสอบสถานะ KYC Verified ของซาเล้งก่อนอนุญาตให้เข้าถึงหน้าประวัติการรับซื้อและรายการลูกค้าประจำ |
| **`D-00-02`** | ซ่อนพิกัดผู้ขายจนกว่าจะรับงาน | ในหน้าประวัติการรับซื้อย้อนหลัง ซ่อนพิกัดละเอียดของผู้ขายตามกฎหมาย PDPA |
| **`D-00-03`** | ขอบเขตหยุดที่สถานะมีผู้รับงานแล้ว | ครอบคลุมงานหลังจบงาน `S7: Completed` และการเปลี่ยนสถานะเป็น `S8: Disputed` เมื่อเกิดปัญหาหน้างาน |

