# แผนสถาปัตยกรรมและเทคโนโลยี: ศูนย์ควบคุมการจับคู่งานและข้อพิพาท (`specs/admin/03-dispatch-and-dispute-center/plan.md`)

- **Version:** `1.0` | **Status:** `ready-for-tasks` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิงสเปก:** [`specs/admin/03-dispatch-and-dispute-center/spec.md`](./spec.md) (v2.0)
- **Use Case หลัก:** **`UC-13: จัดการข้อพิพาทและงานตกค้าง`** ([`docs/srs/use-cases.md`](../../../docs/srs/use-cases.md))
- **ข้อจำกัดกลาง:** [`specs/000-shared/constraints.md`](../../000-shared/constraints.md) (`CC-01..CC-06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)

---

## 1. เทคโนโลยีที่ใช้ (Technology Stack & Architecture)

> [!NOTE]
> **หมายเหตุด้านเทคโนโลยี:** เทคโนโลยีที่ใช้ในโมดูลนี้ **`"ทีมเลือกเอง ไม่ได้มาจาก spec"`** เพื่อให้สอดคล้องกับโครงสร้างและฐานโค้ดหลักของระบบ Saleng:

- **Backend Framework:** **Python 3.11 + FastAPI**
  - สถาปัตยกรรมแบบแยกส่วน: Router (`api/v1/dispatch_dispute.py`), Service Layer (`services/dispatch_dispute_service.py`), และ Data Models (`models/dispatch_dispute_models.py`)
  - ตรวจสอบความถูกต้องของข้อมูลและ Schema ด้วย **Pydantic v2**
  - ควบคุมการเข้าถึงด้วย Role-based Header (`X-Admin-Role: ADMIN`) ส่งกลับ `HTTP 403 Forbidden` หากไม่ใช่แอดมินตาม `CC-03` และ `D-A03-06`
  - มาตรฐานรหัสตอบกลับ HTTP: `200 OK`, `201 Created`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`
- **Database & State Store:** **Supabase (PostgreSQL 15+)**
  - ตาราง `orders`: คัดกรองคำขอตกค้างสถานะ `S2 (Pending)` ที่ค้างเกิน 30 นาที, บันทึกการขยายรัศมี `search_radius_km` และการมอบหมายงาน `buyer_id`
  - ตาราง `dispute_reports`: บันทึกข้อมูลข้อพิพาท (`dispute_id`, `order_id`, `status: PENDING_ADMIN / RESOLVED_COMPLETED / RESOLVED_CANCELLED`, `arbitrated_amount`, `arbitration_note`)
  - ตาราง `audit_logs`: บันทึกประวัติการตัดสินและกระจายงานสำรองแบบ Append-only ตาม `REQ-SEC-001`
- **Frontend Framework:** **React 18 + Vite + TailwindCSS**
  - ออกแบบเป็น Single-Page Application (SPA) รองรับทั้งจอมือถือและเดสก์ท็อปของแอดมินตาม `CC-01`
  - ทัชทาร์เก็ตปุ่มกดและฟังก์ชันสำคัญขนาดไม่ต่ำกว่า `48px` ทุกปุ่มตาม `REQ-UX-001`
  - มี Modal ยืนยันการชี้ขาดข้อพิพาท พร้อมช่องกรอกยอดเงินสุทธิที่ตัดสินชี้ขาด (`Arbitrated Amount`)
  - แอดมินทำงานแบบ **Online-only** ตาม `CC-05` และ `D-A03-06` เพื่อความถูกต้องของคิวงานและคำตัดสินแบบเรียลไทม์
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
│   │   │   ├── dispatch_dispute.py             # [NEW] FastAPI Router สำหรับคิวกระจายงานสำรองและระงับข้อพิพาท
│   │   │   └── pricing.py                      # [UPDATE] เมานต์ dispatch_dispute.router เข้ากับแอปหลัก
│   │   ├── core/
│   │   │   └── supabase.py                     # [UPDATE] เพิ่ม helper methods สำหรับ stalled orders & dispute arbitration
│   │   ├── models/
│   │   │   └── dispatch_dispute_models.py      # [NEW] Pydantic Schemas สำหรับงานตกค้าง, มอบหมายงาน, สำนวนข้อพิพาท, และคำตัดสิน
│   │   └── services/
│   │       └── dispatch_dispute_service.py     # [NEW] Service ตรรกะธุรกิจ การคัดกรองงานตกค้าง, กระจายงาน, ขยายรัศมี, และตัดสินชี้ขาด
│   └── tests/
│       ├── test_T01_dispatch_dispute_models.py # [NEW] ทดสอบ Pydantic Models & Store methods
│       ├── test_AC_A03_01_manual_dispatch.py   # [NEW] ทดสอบดึงงานตกค้าง, มอบหมายตรง, และขยายรัศมี
│       ├── test_AC_A03_02_dispute_dossier.py   # [NEW] ทดสอบการเรียกดูคิวข้อพิพาทและสำนวนหลักฐาน
│       ├── test_AC_A03_03_resolve_complete.py  # [NEW] ทดสอบการตัดสินชี้ขาดให้จบงาน (S8 -> S7) พร้อมยอดเงินชี้ขาด
│       ├── test_AC_A03_04_resolve_cancel.py    # [NEW] ทดสอบการตัดสินสั่งยกเลิกคำขอ (S8 -> S9)
│       ├── test_AC_A03_05_admin_dispute_rbac_audit.py # [NEW] ทดสอบ RBAC (403) และ Audit Logs
│       └── test_e2e_admin_dispatch_dispute.py  # [NEW] ทดสอบ Integration E2E เต็มวงจร
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── admin/
│   │   │       ├── StalledOrdersTable.jsx      # [NEW] ตารางคิวนัดหมายตกค้าง + ปุ่มมอบหมายตรง + ขยายรัศมี
│   │   │       ├── DisputeDossierCard.jsx      # [NEW] การ์ดแสดงรายการข้อพิพาทและสำนวนหลักฐาน 4 มิติ
│   │   │       ├── ArbitrationModal.jsx        # [NEW] Modal สำหรับตัดสินชี้ขาด (จบงาน / ยกเลิก)
│   │   │       └── AdminDispatchDisputeView.jsx # [NEW] หน้าจอหลักแอดมินแท็บคู่ (data-req="UC-13")
│   │   └── services/
│   │       └── adminDispatchDisputeApi.js      # [NEW] Frontend API Client สำหรับติดต่อ Dispatch & Dispute Endpoints
│   └── tests/
│       ├── adminDispatchDisputeApi.test.mjs    # [NEW] ทดสอบ Vitest สำหรับ adminDispatchDisputeApi
│       ├── AC-A03-01.test.jsx                  # [NEW] ทดสอบ UI งานตกค้างและการกระจายงานสำรอง
│       ├── AC-A03-02.test.jsx                  # [NEW] ทดสอบ UI แสดงสำนวนหลักฐานข้อพิพาท
│       └── AC-A03-03.test.jsx                  # [NEW] ทดสอบ UI การตัดสินชี้ขาดข้อพิพาท
```

---

## 3. การออกแบบฐานข้อมูล / Data Models (Database & Schema Design)

### 3.1 ตาราง `orders` (ส่วนขยายสำหรับงานตกค้างและการกระจายงาน — `D-A03-02`, `D-A03-03`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `order_id` | `UUID / String` | รหัสคำขอนัดหมาย (Primary Key) |
| `status` | `String` | สถานะใบงาน: `S2 (Pending)`, `S3 (Assigned)`, `S8 (Disputed)`, `S7 (Completed)`, `S9 (Cancelled)` |
| `created_at` | `String (ISO 8601)` | เวลาสร้างคำขอ (ใช้คำนวณระยะเวลาตกค้าง `> 30 นาที`) |
| `pickup_time` | `Optional[String]` | ช่วงเวลานัดหมาย |
| `search_radius_km` | `Float` | รัศมีการค้นหาปัจจุบัน (เริ่มต้น `5.0 กม.`, ขยายเป็น `10.0 กม.`) |
| `is_manual_dispatched` | `Boolean` | สถานะระบุว่าได้รับการกระจายงานโดยแอดมินหรือไม่ |
| `dispatched_by` | `Optional[String]` | รหัสแอดมินผู้กระจายงาน |
| `dispatched_at` | `Optional[String]` | เวลาที่กระจายงาน |

### 3.2 ตาราง `dispute_reports` (สำนวนข้อพิพาท — `REQ-FN-005`, `D-A03-01`, `D-A03-04`, `D-A03-05`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `dispute_id` | `String` | รหัสข้อพิพาท (`DISP-YYYYMMDD-XXXX`, Primary Key) |
| `order_id` | `String` | รหัสคำขอที่เกี่ยวข้อง (Foreign Key อ้างอิง `orders`) |
| `seller_id` | `String` | รหัสผู้ขาย |
| `buyer_id` | `String` | รหัสซาเล้งผู้รับงาน |
| `dispute_reason` | `String` | เหตุผลการโต้แย้ง/ปฏิเสธผลชั่งของผู้ขาย |
| `status` | `String` | สถานะข้อพิพาท: `PENDING_ADMIN`, `RESOLVED_COMPLETED`, `RESOLVED_CANCELLED` |
| `re_quoted_price` | `Optional[Float]` | ยอดเงินใหม่ที่ซาเล้งเสนอหน้างาน |
| `scale_photo_url` | `Optional[String]` | ลิงก์รูปถ่ายหน้าตาชั่งดิจิทัลของซาเล้ง (`REQ-FN-002`) |
| `seller_photo_urls` | `List[String]` | รูปถ่ายของเก่าของผู้ขาย (`REQ-FN-004`) |
| `arbitrated_amount` | `Optional[Float]` | ยอดเงินสุทธิที่แอดมินตัดสินชี้ขาด (บาท) |
| `arbitration_note` | `Optional[String]` | หมายเหตุคำตัดสินชี้ขาดของแอดมิน |
| `arbitrated_by` | `Optional[String]` | รหัสแอดมินผู้ชี้ขาด |
| `arbitrated_at` | `Optional[String]` | วันเวลาที่ตัดสินชี้ขาด |
| `created_at` | `String (ISO 8601)` | วันเวลาที่ส่งข้อพิพาท |

### 3.3 ตาราง `audit_logs` (บันทึกประวัติความปลอดภัยตาม `REQ-SEC-001`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `log_id` | `String` | รหัสบันทึกประวัติ (UUID) |
| `action` | `String` | `ADMIN_MANUAL_DISPATCH`, `ADMIN_EXPAND_DISPATCH_RADIUS`, `ADMIN_RESOLVED_DISPUTE`, `ADMIN_CANCELLED_DISPUTE` |
| `entity_id` | `String` | `order_id` หรือ `dispute_id` |
| `actor_id` | `String` | รหัสแอดมินผู้กระทำ (เช่น `admin-01`) |
| `actor_role` | `String` | ค่าคงที่ `'ADMIN'` |
| `details` | `JSON / Dict` | รายละเอียด เช่น ซาเล้งที่ได้รับงาน, รัศมีใหม่, หรือยอดเงินชี้ขาด |
| `timestamp` | `String (ISO 8601)` | เวลาประทับที่เกิดเหตุการณ์ |

---

## 4. การออกแบบ API / Endpoints (API Specification)

ทุกเส้นทางต้องระบุ Header `X-Admin-Role: ADMIN` ตามข้อกำหนด `CC-03` และ `D-A03-06`

### 4.1 รายการ API สำหรับแอดมิน

| Method | Endpoint | Request Body | Response (Success) | Error Codes |
| :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/admin/dispatch/stalled-orders` | Params: `min_wait_minutes` (default 30) | `List[StalledOrderItem]` (คำขอ S2 ที่ค้างเกินเวลา พร้อมพิกัดตำบล/แขวง และระยะเวลารอ) | `401`, `403` |
| `POST` | `/api/v1/admin/dispatch/assign` | `ManualDispatchAssignRequest` (`order_id`, `saleng_id`) | `ManualDispatchResponse` (`success`, `order_id`, `status: 'S3'`, `assigned_saleng`) | `400`, `403`, `404`, `409` |
| `POST` | `/api/v1/admin/dispatch/expand-radius` | `ExpandDispatchRadiusRequest` (`order_id`, `new_radius_km`: default 10.0) | `ExpandRadiusResponse` (`success`, `order_id`, `new_radius_km`) | `400`, `403`, `404` |
| `GET` | `/api/v1/admin/disputes` | Params: `status` (default `PENDING_ADMIN`) | `List[DisputeSummaryItem]` (รายการข้อพิพาทรอดำเนินการ) | `401`, `403` |
| `GET` | `/api/v1/admin/disputes/{dispute_id}` | - | `DisputeDossierResponse` (สำนวนหลักฐาน 4 มิติครบถ้วน) | `401`, `403`, `404` |
| `POST` | `/api/v1/admin/disputes/{dispute_id}/resolve` | `ResolveDisputeRequest` (`action`: `RESOLVE_COMPLETE` / `RESOLVE_CANCEL`, `arbitrated_amount`, `arbitration_note`) | `ResolveDisputeResponse` (`success`, `dispute_id`, `new_order_status`, `arbitrated_amount`) | `400`, `403`, `404`, `422` |

---

## 5. แผนการเชื่อมต่อระบบภายนอก (External Integrations / Third-party Services)

- **Mock Supabase Store:** ใช้งาน In-Memory Storage Adapter ใน `backend/app/core/supabase.py` ขยายฟังก์ชัน `get_stalled_orders`, `manual_dispatch_order`, `expand_order_search_radius`, `get_disputes`, `get_dispute_dossier`, และ `resolve_dispute`
- **Order State Sync:** เมื่อแอดมินมอบหมายงานตรง (`Direct Assign`) คำขอจะเปลี่ยนเป็น `S3 (Assigned)` ทันที และเปิดเผยพิกัดบ้านเลขที่ให้ซาเล้งที่ได้รับงานตาม `REQ-SEC-002`
- **Receipt & Settlement Sync:** เมื่อแอดมินตัดสินให้จบงาน (`RESOLVE_COMPLETE`), ระบบจะเปลี่ยนสถานะเป็น `S7 (Completed)` และออกใบเสร็จดิจิทัลตามยอดเงินชี้ขาด (`Arbitrated Amount`) ทันที
- **ระบบภายนอกในอนาคต (Non-goals):** ไม่เชื่อมต่อระบบ Voice Bot อัตโนมัติ, ไม่เชื่อมต่อระบบวิเคราะห์เสียงพูดหรือวิดีโอสดด้วย AI, และไม่เชื่อมต่อระบบ Escrow Wallet ใน MVP นี้

---

## 6. แผนการสร้างหน้าจอและปฏิสัมพันธ์ (Frontend Components & Interactions)

- **Layout & Structure:** หน้าจอแดชบอร์ดแอดมิน (SPA) จัดวางเป็น 2 แท็บหลัก:
  1. **แท็บที่ 1: ศูนย์กระจายงานกรณีสำรอง (`StalledOrdersTable.jsx`)**
     - แสดงตารางรายการคำขอ `S2` ที่ไม่มีซาเล้งกดรับเกิน 30 นาที
     - แสดงข้อมูล: รหัสคำขอ, เวลาที่โพสต์, ระยะเวลาที่รอ (นาที/ชั่วโมง), ตำบล/แขวง, ช่วงราคาประเมิน
     - ปุ่ม "มอบหมายงานตรง (Direct Assign)" เปิด Dropdown เลือกซาเล้งที่สถานะ `Online` และผ่าน KYC ในพื้นที่
     - ปุ่ม "ขยายรัศมีเป็น 10 กม. (Expand Radius)" เพื่อบรอดคาสต์คำขอให้ซาเล้งวงนอก
     - ทุกปุ่มกดมีทัชทาร์เก็ต $\ge 48\text{px}$ ตาม `REQ-UX-001` และ `CC-01`
  2. **แท็บที่ 2: ศูนย์จัดการและตัดสินข้อพิพาท (`DisputeDossierCard.jsx` & `ArbitrationModal.jsx`)**
     - แสดงรายการข้อพิพาทสถานะ `PENDING_ADMIN` (คำขอ `S8`)
     - แสดงสำนวนหลักฐาน 4 มิติ:
       - กล่องข้อมูลคำขอเดิมและ Price Snapshot
       - กล่องข้อมูลชั่งจริงและรูปถ่ายหน้าตาชั่งดิจิทัลของซาเล้ง
       - กล่องข้อโต้แย้งและเหตุผลปฏิเสธของผู้ขาย
       - กล่องข้อมูลติดต่อคู่กรณี
     - ปุ่ม "ตัดสินชี้ขาด (Arbitrate)" เปิด Modal ให้เลือก:
       - ตัวเลือกที่ 1: "ตัดสินให้จบงาน (`S7`)" พร้อมช่องกรอกยอดเงินชี้ขาด (บาท) และหมายเหตุ
       - ตัวเลือกที่ 2: "ตัดสินให้ยกเลิกคำขอ (`S9`)" พร้อมช่องกรอกเหตุผล
     - ปุ่มยืนยันคำตัดสินมีทัชทาร์เก็ต $\ge 48\text{px}$
  3. **หน้าจอหลักเชื่อมโยง (`AdminDispatchDisputeView.jsx`)**
     - กำกับแอตทริบิวต์ `data-req="UC-13"` ครบถ้วน
     - ป้ายสถานะระบุชัดเจนว่าทำงานในโหมด Online-only (`CC-05`)

---

## 7. แผนการทดสอบอัตโนมัติ (Automated Testing Strategy)

| รหัสการทดสอบ | ประเภท | สิ่งที่ทดสอบ | AC ที่รองรับ |
| :--- | :---: | :--- | :---: |
| `test_T01_dispatch_dispute_models.py` | Unit | ตรวจสอบ Pydantic Schemas, Field Validators, และ Store Methods | `T-01` |
| `test_AC_A03_01_manual_dispatch.py` | Backend API | คัดกรองคำขอ S2 ตกค้าง > 30 นาที, มอบหมายงานตรง (S2->S3), และขยายรัศมีเป็น 10 กม. | `AC-A03-01` |
| `test_AC_A03_02_dispute_dossier.py` | Backend API | เรียกดูรายการข้อพิพาท S8 และตรวจสอบสำนวนหลักฐาน 4 มิติ | `AC-A03-02` |
| `test_AC_A03_03_resolve_complete.py` | Backend API | ตัดสินชี้ขาดให้จบงาน (S8->S7), กำหนดยอดเงินชี้ขาด, และออกใบเสร็จ | `AC-A03-03` |
| `test_AC_A03_04_resolve_cancel.py` | Backend API | ตัดสินสั่งยกเลิกคำขอ (S8->S9) พร้อมบันทึกเหตุผล | `AC-A03-04` |
| `test_AC_A03_05_admin_dispute_rbac_audit.py` | Backend API | ตรวจสอบ Header X-Admin-Role (403 Forbidden) และความครบถ้วนของ Audit Logs ทั้ง 4 แอ็กชัน | `AC-A03-05` |
| `test_e2e_admin_dispatch_dispute.py` | Integration E2E | ทดสอบวงจรชีวิตเต็มรูปแบบ: กรองงานตกค้าง -> จ่ายงาน -> ตรวจข้อพิพาท -> ตัดสินชี้ขาด -> Audit Trail | `AC-A03-01..05` |
| `adminDispatchDisputeApi.test.mjs` | Frontend Unit | ทดสอบ API Client ครบทุกเมธอด พร้อมการจัดการ Error 403/400 | `T-06` |
| `AC-A03-01.test.jsx` | Component Test | ทดสอบหน้าจองานตกค้าง การเลือกซาเล้งมอบหมายงาน และปุ่มขยายรัศมี | `AC-A03-01` |
| `AC-A03-02.test.jsx` | Component Test | ทดสอบการแสดงผลสำนวนหลักฐานข้อพิพาท 4 มิติใน UI | `AC-A03-02` |
| `AC-A03-03.test.jsx` | Component Test | ทดสอบ Modal การตัดสินชี้ขาดข้อพิพาท ทั้งจบงาน (S7) และยกเลิก (S9) | `AC-A03-03`, `AC-A03-04` |

---

## 8. ตารางตรวจความครบถ้วนของข้อจำกัดกลาง (Constraints Compliance Matrix)

ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม [`specs/000-shared/constraints.md`](../../000-shared/constraints.md):

| รหัส Constraint | ข้อกำหนดใน Constraint กลาง | ผลการตรวจสอบ / รายละเอียดการปฏิบัติตาม |
| :---: | :--- | :--- |
| **`CC-01`** | Mobile-First Web SPA รองรับมือถือราคาประหยัด (`RAM >= 2 GB`, ปุ่ม `>= 48px`) | **สอดคล้อง:** พัฒนาแดชบอร์ดแอดมินด้วย React 18 + TailwindCSS ปุ่มกดมอบหมายงาน ขยายรัศมี และปุ่มตัดสินชี้ขาด มีขนาด $\ge 48\text{px}$ ทุกปุ่ม (`REQ-UX-001`) |
| **`CC-02`** | GPS Sync Interval ทุก 60 วินาทีขณะเปิดสถานะ Online | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** หน้าจอศูนย์ควบคุมแอดมินไม่มีการส่งพิกัด GPS เคลื่อนที่ |
| **`CC-03`** | Road Distance API รัศมี <= 5.0 กม. พร้อม Haversine Fallback | **สอดคล้อง:** ระบบกระจายงานสำรองเปิดให้แอดมินขยายรัศมีการค้นหาจากปกติ 5.0 กม. เป็น 10.0 กม. (`D-A03-03`) และบังคับ Header `X-Admin-Role: ADMIN` ทุก API |
| **`CC-04`** | PostgreSQL + Concurrency Control / Optimistic Locking (`BR-02`) | **สอดคล้อง:** การมอบหมายงานตรงของแอดมินใช้ Concurrency Lock ป้องกันการมอบหมายซ้อนทับกับซาเล้งคนอื่นที่อาจกดรับงานในจังหวะเดียวกัน |
| **`CC-05`** | Offline Cache ใน IndexedDB / Local Storage | **สอดคล้อง:** หน้าจอแอดมินทำงานแบบ **Online-only** ไม่อนุญาตให้จ่ายงานหรือตัดสินข้อพิพาทในโหมดออฟไลน์ เพื่อป้องกันข้อมูลขัดแย้ง |
| **`CC-06`** | PDPA & PII Masking ซ่อนบ้านเลขที่และพิกัดละเอียด | **สอดคล้อง:** ในคิวงานตกค้างแสดงเฉพาะตำบล/แขวง และในสำนวนข้อพิพาทแสดงข้อมูลคู่กรณีเท่าที่จำเป็นในการพิจารณาชี้ขาด (`REQ-SEC-002`) |
| **`REQ-SEC-001`** | บันทึกประวัติลงตาราง Audit Log | **สอดคล้อง:** บันทึกประวัติ `ADMIN_MANUAL_DISPATCH`, `ADMIN_EXPAND_DISPATCH_RADIUS`, `ADMIN_RESOLVED_DISPUTE`, `ADMIN_CANCELLED_DISPUTE` ลงใน `audit_logs` แบบ Append-only |
| **`REQ-SEC-002`** | ปกปิดข้อมูลส่วนบุคคล (PII) และควบคุมสิทธิ์การเข้าถึง | **สอดคล้อง:** จำกัดสิทธิ์การเข้าถึงคิวงานตกค้างและสำนวนข้อพิพาทเฉพาะผู้ดูแลระบบ (`X-Admin-Role: ADMIN`) |
| **`REQ-OP-001`** | Response Time Latency (< 2.0 วินาที P95) | **สอดคล้อง:** การดึงคิวงานตกค้างและสำนวนข้อพิพาทตอบสนองภายใน `< 2.0 วินาที` (P95) |
| **`REQ-OP-002`** | System Availability & Operational SLA | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** เป็นข้อกำหนด SLA ระดับโครงสร้างพื้นฐานของระบบภาพรวม |
| **`D-00-01`** | Precondition Gatekeeper for Buyer Verification | **สอดคล้อง:** เมื่อแอดมินมอบหมายงานตรง ระบบกรองให้เลือกเฉพาะซาเล้งที่ผ่าน KYC (`verified = True`) และเปิดสถานะ Online เท่านั้น |
| **`D-00-02`** | Benchmark Price Lock & Variance ($\pm 15\%$) | **สอดคล้อง:** ข้อพิพาท `S8` เกิดขึ้นจากการที่น้ำหนักหน้างานต่างเกิน $\pm 15\%$ หรือผู้ขายปฏิเสธ และแอดมินใช้ Price Snapshot อ้างอิงประกอบการตัดสิน |
| **`D-00-03`** | Dual-Engine Route Optimization | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** เป็นข้อกำหนดอัลกอริทึมจัดคิวและคำนวณเส้นทางอัตโนมัติใน `UC-04` |

