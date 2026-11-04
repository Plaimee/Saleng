# แผนสถาปัตยกรรมและเทคโนโลยี: ระบบตรวจสอบ ความปลอดภัย และปฏิบัติตามกฎหมาย (`specs/admin/04-audit-security-and-compliance/plan.md`)

- **Version:** `1.0` | **Status:** `ready-for-tasks` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิงสเปก:** [`specs/admin/04-audit-security-and-compliance/spec.md`](./spec.md) (v2.0)
- **Use Case หลัก:** **`UC-13: ตัดสินข้อพิพาท (S8) และตรวจสอบ Audit Log / PDPA Compliance`** ([`docs/srs/use-cases.md`](../../../docs/srs/use-cases.md))
- **ข้อจำกัดกลาง:** [`specs/000-shared/constraints.md`](../../000-shared/constraints.md) (`CC-01..CC-06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)

---

## 1. เทคโนโลยีที่ใช้ (Technology Stack & Architecture)

> [!NOTE]
> **หมายเหตุด้านเทคโนโลยี:** เทคโนโลยีที่ใช้ในโมดูลนี้ **`"ทีมเลือกเอง ไม่ได้มาจาก spec"`** เพื่อให้สอดคล้องกับโครงสร้างและฐานโค้ดหลักของระบบ Saleng:

- **Backend Framework:** **Python 3.11 + FastAPI**
  - สถาปัตยกรรมแบบแยกส่วน: Router (`api/v1/security_compliance.py`), Service Layer (`services/security_compliance_service.py`), และ Data Models (`models/security_compliance_models.py`)
  - ตรวจสอบความถูกต้องของข้อมูลและ Schema ด้วย **Pydantic v2**
  - ควบคุมการเข้าถึงด้วย Role-based Header (`X-Admin-Role`) แยก 4 บทบาทเจ้าหน้าที่: `ADMIN`, `AUDITOR`, `DPO`, `SUPPORT` ส่งกลับ `HTTP 403 Forbidden` หากไม่มีสิทธิ์ตาม `CC-03` และ `D-A04-02`
  - ยืนยันความไม่เปลี่ยนแปลงของ Audit Log ด้วยอัลกอริทึม **SHA-256 (`hashlib.sha256`)** คำนวณ `log_hash` ลงในทุกระเบียนตาม `REQ-SEC-001` และ `D-A04-05`
  - รองรับการ Export ข้อมูลทั้งรูปแบบ **CSV** (ผ่าน `csv.writer` / `StreamingResponse`) และ **JSON**
- **Database & State Store:** **Supabase (PostgreSQL 15+)**
  - ตาราง `audit_logs`: บันทึกประวัติแบบ Append-only ไม่มีคำสั่ง UPDATE หรือ DELETE พร้อมฟิลด์ `log_hash`
  - ตาราง `orders` & `pickup_locations`: ตรวจสอบสถานะ Data Masking และระยะเวลา Retention หลังจบงาน 24 ชม.
  - ตารางประวัติพิกัด GPS ซาเล้ง: เก็บประวัติพิกัดไม่เกิน 90 วัน เพื่อรอการ Purge ตามกฎหมาย PDPA (`D-A04-04`)
- **Frontend Framework:** **React 18 + Vite + TailwindCSS**
  - ออกแบบเป็น Single-Page Application (SPA) รองรับทั้งจอมือถือและเดสก์ท็อปของแอดมินตาม `CC-01`
  - ทัชทาร์เก็ตปุ่มกดและฟังก์ชันสำคัญขนาดไม่ต่ำกว่า `48px` ทุกปุ่มตาม `REQ-UX-001`
  - แดชบอร์ดแบ่งเป็น 3 แท็บหลัก: (1) Audit Trail Viewer, (2) Anonymized Community Report, (3) PDPA Compliance & Retention
  - ทำงานในโหมด **Online-only** ตาม `CC-05` และ `D-A04-06` เพื่อความถูกต้องของการตรวจสอบข้อมูลแบบเรียลไทม์
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
│   │   │   ├── security_compliance.py          # [NEW] FastAPI Router สำหรับ Audit Log, RBAC, รายงานชุมชน และ PDPA
│   │   │   └── pricing.py                      # [UPDATE] เมานต์ security_compliance.router เข้ากับแอปหลัก
│   │   ├── core/
│   │   │   └── supabase.py                     # [UPDATE] เพิ่ม helper methods สำหรับ query audit logs, verify integrity, community report, และ pdpa purge
│   │   ├── models/
│   │   │   └── security_compliance_models.py   # [NEW] Pydantic Schemas สำหรับ Audit Filters, Verification, Community Report, และ Retention
│   │   └── services/
│   │       └── security_compliance_service.py  # [NEW] Service ตรรกะธุรกิจ RBAC, Audit Query/Export/Verify, Aggregation, และ PDPA Purge
│   └── tests/
│       ├── test_T01_security_compliance_models.py # [NEW] ทดสอบ Pydantic Models & Store methods
│       ├── test_AC_A04_01_audit_log_query_export.py # [NEW] ทดสอบค้นหา กรอง และส่งออก Audit Log (CSV/JSON)
│       ├── test_AC_A04_02_immutable_audit_integrity.py # [NEW] ทดสอบ SHA-256 Hash และการ Verify Integrity
│       ├── test_AC_A04_03_rbac_enforcement.py      # [NEW] ทดสอบการควบคุมสิทธิ์ 4 บทบาท (ADMIN, AUDITOR, DPO, SUPPORT)
│       ├── test_AC_A04_04_pdpa_retention_purge.py  # [NEW] ทดสอบ Data Retention 90 วัน และการสั่ง Purge ข้อมูล
│       ├── test_AC_A04_05_community_waste_report.py # [NEW] ทดสอบรายงานชุมชน Anonymized Report ปลอด PII 100%
│       └── test_e2e_admin_security_compliance.py   # [NEW] ทดสอบ Integration E2E ครบวงจรระบบตรวจสอบและความปลอดภัย
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── admin/
│   │   │       ├── AuditTrailViewer.jsx        # [NEW] ตาราง Audit Log, กรองหลายมิติ, ปุ่ม Export, ปุ่ม Verify Hash
│   │   │       ├── CommunityWasteReportView.jsx # [NEW] หน้ารายงานสถิติขยะชุมชนรายเขต/แขวง ปลอด PII 100% พร้อมปุ่ม Export CSV
│   │   │       ├── PdpaRetentionPanel.jsx      # [NEW] แผงตรวจสอบสถานะ PDPA Retention และปุ่มสั่ง Purge ข้อมูลหมดอายุ
│   │   │       └── AdminSecurityComplianceView.jsx # [NEW] หน้าจอหลักแอดมิน 3 แท็บ (data-req="UC-13", ปุ่ม >= 48px)
│   │   └── services/
│   │       └── adminSecurityComplianceApi.js   # [NEW] Frontend API Client สำหรับติดต่อ Compliance Endpoints
│   └── tests/
│       ├── adminSecurityComplianceApi.test.mjs # [NEW] ทดสอบ Vitest สำหรับ adminSecurityComplianceApi
│       ├── AC-A04-01.test.jsx                  # [NEW] ทดสอบ UI Audit Trail Viewer และการ Export
│       ├── AC-A04-02.test.jsx                  # [NEW] ทดสอบ UI ตรวจสอบความถูกต้องของ Hash (Verify Integrity)
│       └── AC-A04-03.test.jsx                  # [NEW] ทดสอบ UI รายงานชุมชน Anonymized Report และแผง PDPA Retention
```

---

## 3. การออกแบบฐานข้อมูล / Data Models (Database & Schema Design)

### 3.1 ตาราง `audit_logs` (ส่วนขยายฟิลด์ SHA-256 Hash — `P-07`, `REQ-SEC-001`, `D-A04-05`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `log_id` | `UUID / String` | รหัสบันทึกประวัติ (Primary Key) |
| `action` | `String` | ชื่อแอ็กชัน เช่น `ORDER_CLAIMED`, `ADMIN_MANUAL_DISPATCH`, `BENCHMARK_UPDATED`, `DISPUTE_RESOLVED`, `DATA_PURGED` |
| `entity_id` | `String` | รหัสอ้างอิงข้อมูล เช่น `order_id`, `category_code`, `dispute_id` |
| `actor_id` | `String` | รหัสผู้กระทำ เช่น `admin-01`, `auditor-01`, `saleng-01` |
| `actor_role` | `String` | บทบาทผู้กระทำ: `ADMIN`, `AUDITOR`, `DPO`, `SUPPORT`, `COLLECTOR`, `SELLER` |
| `details` | `JSON / Dict` | รายละเอียดเหตุการณ์ ค่าก่อนและหลังการเปลี่ยนแปลง |
| `timestamp` | `String (ISO 8601 UTC)` | เวลาประทับของเหตุการณ์ |
| `log_hash` | `String (SHA-256)` | Checksum เพื่อยืนยันความไม่เปลี่ยนแปลง (`actor_id + actor_role + action + entity_id + timestamp + details`) |

### 3.2 โครงสร้างข้อมูลสถิติรายงานชุมชน (`Community Waste Aggregate` — `AC-A04-05`, `D-A04-03`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `subdistrict` | `String` | แขวง/ตำบล (เช่น แขวงห้วยขวาง, แขวงสามเสนนอก) |
| `district` | `String` | เขต/อำเภอ (เช่น เขตห้วยขวาง, เขตจตุจักร) |
| `category_code` | `String` | รหัสหมวดหมู่วัสดุรีไซเคิล (เช่น `MAT-CARDBOARD`, `MAT-PET-BOTTLE`) |
| `category_name` | `String` | ชื่อภาษาไทย (เช่น กระดาษลัง, ขวดพลาสติกใส) |
| `total_weight_kg` | `Float` | น้ำหนักรวมที่รับซื้อสำเร็จ (กก.) |
| `total_amount_thb` | `Float` | มูลค่าเงินหมุนเวียนรวม (บาท) |
| `completed_trips_count` | `Integer` | จำนวนรอบการรับซื้อที่ปิดงานสำเร็จ (`S7`) |
| `period_month` | `String` | ช่วงเวลาสรุป เช่น `2026-11` |

### 3.3 โครงสร้างข้อมูลตรวจสอบ PDPA Retention (`D-A04-04`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `gps_retention_days` | `Integer` | ค่าคงที่นโยบายการจัดเก็บพิกัด GPS ซาเล้ง (`90 วัน`) |
| `expired_gps_count` | `Integer` | จำนวนพิกัดประวัติที่มีอายุเกิน 90 วันที่รอการ Purge |
| `unmasked_orders_count` | `Integer` | จำนวนออเดอร์ที่ปิดงานเกิน 24 ชั่วโมงที่รอการ Masking บ้านเลขที่ถาวร |
| `last_purged_at` | `Optional[String]` | วันเวลาที่สั่งรัน Purge ล่าสุด |
| `last_purged_by` | `Optional[String]` | รหัส DPO หรือแอดมินที่สั่งรัน |

---

## 4. การออกแบบ API / Endpoints (API Specification)

ทุกเส้นทางต้องระบุ Header `X-Admin-Role` โดยตรวจสอบสิทธิ์ตามบทบาทอย่างเคร่งครัดตาม `D-A04-02`:

| Method | Endpoint | สิทธิ์ที่อนุญาต (`Role`) | Request Body / Params | Response (Success) | Error Codes |
| :---: | :--- | :---: | :--- | :--- | :---: |
| `GET` | `/api/v1/admin/compliance/audit-logs` | `ADMIN`, `AUDITOR` | Params: `action`, `actor_role`, `start_date`, `end_date`, `limit`, `offset` | `AuditLogListResponse` (รายการบันทึก พร้อมจำนวนทั้งหมด และ pagination) | `401`, `403` |
| `GET` | `/api/v1/admin/compliance/audit-logs/export` | `ADMIN`, `AUDITOR` | Params: `format: 'csv' / 'json'`, filters | `AuditLogExportResponse` (ไฟล์ CSV หรือ JSON สำหรับดาวน์โหลด) | `401`, `403` |
| `GET` | `/api/v1/admin/compliance/audit-logs/verify-integrity` | `ADMIN`, `AUDITOR` | - | `VerifyIntegrityResponse` (`total_checked`, `is_valid: true/false`, `corrupted_log_ids`) | `401`, `403` |
| `GET` | `/api/v1/admin/compliance/reports/community-waste` | `ADMIN`, `AUDITOR` | Params: `district`, `period` | `CommunityWasteReportResponse` (สรุปสถิติตามเขต/แขวง ปลอด PII 100%) | `401`, `403` |
| `GET` | `/api/v1/admin/compliance/reports/community-waste/export` | `ADMIN`, `AUDITOR` | Params: `format: 'csv' / 'json'`, `district`, `period` | `File / CSV Stream` สำหรับส่งสำนักสิ่งแวดล้อม กทม. / เทศบาล | `401`, `403` |
| `GET` | `/api/v1/admin/compliance/retention-status` | `ADMIN`, `DPO` | - | `DataRetentionStatusResponse` (สถานะพิกัด > 90 วัน และออเดอร์ > 24 ชม.) | `401`, `403` |
| `POST` | `/api/v1/admin/compliance/purge-expired` | `ADMIN`, `DPO` | `PurgeExpiredDataRequest` (`confirm_purge: true`, `admin_id`) | `PurgeExpiredDataResponse` (`success`, `purged_gps_points_count`, `masked_orders_count`) | `400`, `403` |

---

## 5. แผนการเชื่อมต่อระบบภายนอก (External Integrations / Third-party Services)

- **Mock Supabase Store Integration:** ใช้งาน In-Memory Storage Adapter ใน `backend/app/core/supabase.py` ขยายฟังก์ชัน:
  - `query_audit_logs`: ค้นหาและกรองบันทึกใน `self.audit_logs`
  - `verify_audit_logs_integrity`: คำนวณ SHA-256 Hash ตรวจสอบความถูกต้องทุกระเบียน
  - `get_community_waste_report`: คำนวณสถิติ Aggregation จากออเดอร์สถานะ `S7 (Completed)`
  - `get_pdpa_retention_status` และ `purge_expired_pdpa_data`: ตรวจนับและล้างพิกัดประวัติเกิน 90 วัน
- **Municipal Waste Report Integration:** ระบบเตรียมไฟล์ส่งออก CSV มาตรฐานตามโครงสร้างข้อมูลของสำนักสิ่งแวดล้อม กทม. และเทศบาล
- **ระบบภายนอกในอนาคต (Non-goals):** ไม่เชื่อมต่อ Blockchain สาธารณะ, ไม่ทำ SAML/SSO กับ Active Directory ภายนอก, ไม่ต่อ Real-time Streaming API ตรงเข้า กทม. ใน MVP นี้

---

## 6. แผนการสร้างหน้าจอและปฏิสัมพันธ์ (Frontend Components & Interactions)

- **หน้าจอหลักแดชบอร์ด (`AdminSecurityComplianceView.jsx`):**
  - กำกับแอตทริบิวต์ `data-req="UC-13"`
  - ป้ายระบุสถานะ Online-only (`CC-05`)
  - แท็บ 3 ส่วน:
    1. **แท็บที่ 1: ตรวจสอบร่องรอยธุรกรรม (`AuditTrailViewer.jsx`)**
       - ตัวกรองค้นหาตาม Action, บทบาท, ช่วงวันที่
       - ตารางแสดงรายการ Log พร้อมเวลาประทับ UTC และ Hash ย่อ
       - ปุ่ม "ตรวจสอบความถูกต้อง (Verify Integrity)": คำนวณ Hash แสดง Badge สีเขียว "ข้อมูลถูกต้อง 100% ไม่มีการดัดแปลง"
       - ปุ่ม "ดาวน์โหลด CSV" และ "ดาวน์โหลด JSON"
       - ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ตาม `REQ-UX-001`
    2. **แท็บที่ 2: รายงานสถิติขยะชุมชน (`CommunityWasteReportView.jsx`)**
       - แดชบอร์ดสรุปสถิติน้ำหนักรวม (กก.), มูลค่าหมุนเวียน (บาท), และเที่ยววิ่งสำเร็จ
       - ตารางจัดกลุ่มแยกตามเขต/แขวง และหมวดหมู่วัสดุ
       - ป้ายยืนยัน **"ปลอดข้อมูลส่วนบุคคล 100% (No PII)"**
       - ปุ่ม "ส่งออกรายงาน กทม./เทศบาล (CSV)"
    3. **แท็บที่ 3: ความคุ้มครองข้อมูลส่วนบุคคล (`PdpaRetentionPanel.jsx`)**
       - การ์ดแสดงสถานะ Retention พิกัด GPS ซาเล้ง (> 90 วัน)
       - การ์ดแสดงสถานะ Data Masking ข้อมูลที่อยู่ผู้ขาย (> 24 ชม. หลังจบงาน)
       - ปุ่ม "สั่งล้างข้อมูลที่หมดอายุ (Purge Expired Data)" พร้อม Modal ยืนยันการทำลายข้อมูลตามกฎหมาย PDPA

---

## 7. แผนการทดสอบอัตโนมัติ (Automated Testing Strategy)

| รหัสการทดสอบ | ประเภท | สิ่งที่ทดสอบ | AC ที่รองรับ |
| :--- | :---: | :--- | :---: |
| `test_T01_security_compliance_models.py` | Unit | ตรวจสอบ Pydantic Schemas, SHA-256 Generator, และ Store Methods | `T-01` |
| `test_AC_A04_01_audit_log_query_export.py` | Backend API | ทดสอบค้นหา กรอง Audit Log และการส่งออก CSV/JSON (Latency < 2.0s) | `AC-A04-01` |
| `test_AC_A04_02_immutable_audit_integrity.py` | Backend API | ทดสอบ SHA-256 Hash ทุกระเบียน และการ Verify Integrity ตรวจจับการแก้ไข | `AC-A04-02` |
| `test_AC_A04_03_rbac_enforcement.py` | Backend API | ทดสอบการควบคุมสิทธิ์ 4 บทบาท (ADMIN, AUDITOR, DPO, SUPPORT) และบล็อก 403 | `AC-A04-03` |
| `test_AC_A04_04_pdpa_retention_purge.py` | Backend API | ทดสอบ Retention Status และคำสั่ง Purge พิกัดเกิน 90 วัน และ Masking 24 ชม. | `AC-A04-04` |
| `test_AC_A04_05_community_waste_report.py` | Backend API | ทดสอบการประมวลผลรายงานสถิติชุมชนระดับเขต/แขวง แบบไม่มี PII 100% | `AC-A04-05` |
| `test_e2e_admin_security_compliance.py` | Integration E2E | ทดสอบวงจรชีวิตเต็มรูปแบบ: บันทึก Log -> Verify Hash -> ตรวจ RBAC -> Purge PDPA -> ส่งออกรายงาน กทม. | `AC-A04-01..05` |
| `adminSecurityComplianceApi.test.mjs` | Frontend Unit | ทดสอบ API Client ครบทุกเมธอด พร้อมการจัดการ Error 403/400 | `T-06` |
| `AC-A04-01.test.jsx` | Component Test | ทดสอบหน้าจอ AuditTrailViewer และปุ่ม Export | `AC-A04-01` |
| `AC-A04-02.test.jsx` | Component Test | ทดสอบปุ่ม Verify Integrity Hash และการแสดงผล Badge บนหน้าจอ | `AC-A04-02` |
| `AC-A04-03.test.jsx` | Component Test | ทดสอบหน้ารายงานชุมชน Anonymized Report และแผง PDPA Retention Purge | `AC-A04-04`, `AC-A04-05` |

---

## 8. ตารางตรวจความครบถ้วนของข้อจำกัดกลาง (Constraints Compliance Matrix)

ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม [`specs/000-shared/constraints.md`](../../000-shared/constraints.md):

| รหัส Constraint | ข้อกำหนดใน Constraint กลาง | ผลการตรวจสอบ / รายละเอียดการปฏิบัติตาม |
| :---: | :--- | :--- |
| **`CC-01`** | Mobile-First Web SPA รองรับมือถือราคาประหยัด (`RAM >= 2 GB`, ปุ่ม `>= 48px`) | **สอดคล้อง:** พัฒนาแดชบอร์ดแอดมินด้วย React 18 + TailwindCSS ปุ่มค้นหา Export และปุ่ม Purge มีขนาด $\ge 48\text{px}$ ทุกปุ่ม (`REQ-UX-001`) |
| **`CC-02`** | GPS Sync Interval ทุก 60 วินาทีขณะเปิดสถานะ Online | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** หน้าจอศูนย์ควบคุมความปลอดภัยไม่มีการส่งพิกัด GPS เคลื่อนที่ |
| **`CC-03`** | Road Distance API รัศมี <= 5.0 กม. พร้อม Haversine Fallback | **สอดคล้อง:** กำหนดโครงสร้าง URL REST API แยกบทบาท `/api/v1/admin/compliance/...` และบังคับ Header `X-Admin-Role` แยกสิทธิ์ `ADMIN`, `AUDITOR`, `DPO`, `SUPPORT` |
| **`CC-04`** | PostgreSQL + Concurrency Control / Optimistic Locking (`BR-02`) | **สอดคล้อง:** การบันทึก `audit_logs` เป็นแบบ Append-only ป้องกัน Concurrency Conflict และการคำสั่ง Purge ทำงานแบบ Atomic |
| **`CC-05`** | Offline Cache ใน IndexedDB / Local Storage | **สอดคล้อง:** หน้าจอแอดมินทำงานแบบ **Online-only** ไม่อนุญาตให้ตรวจสอบ Audit Log หรือ Purge ข้อมูลในโหมดออฟไลน์ |
| **`CC-06`** | PDPA & PII Masking ซ่อนบ้านเลขที่และพิกัดละเอียด | **สอดคล้อง:** รายงานสถิติชุมชนตัดข้อมูล PII ออก 100% (`No PII`), ข้อมูลบ้านเลขที่ผู้ขายคืนสถานะเป็น Masked ถาวรหลังจบงานเกิน 24 ชม., และ Purge พิกัดเกิน 90 วัน (`D-A04-03`, `D-A04-04`) |
| **`REQ-SEC-001`** | บันทึกประวัติลงตาราง Audit Log | **สอดคล้อง:** ทุกเหตุการณ์ในระบบมีบันทึกใน `audit_logs` พร้อมคำนวณ `log_hash` ด้วย `SHA-256` ยืนยัน Immutability (`D-A04-05`) |
| **`REQ-SEC-002`** | ปกปิดข้อมูลส่วนบุคคล (PII) และควบคุมสิทธิ์การเข้าถึง | **สอดคล้อง:** บังคับใช้ RBAC 4 บทบาท (`D-A04-02`) และรับประกันรายงานสถิติส่งออก กทม./เทศบาล ไม่มี PII ปะปน (`D-A04-03`) |
| **`REQ-OP-001`** | Response Time Latency (< 2.0 วินาที P95) | **สอดคล้อง:** การสืบค้น Audit Log และการประมวลผลรายงานสถิติชุมชนตอบสนองภายใน `< 2.0 วินาที` (P95) |
| **`REQ-OP-002`** | System Availability & Operational SLA | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** เป็นข้อกำหนด SLA ระดับโครงสร้างพื้นฐานของระบบภาพรวม |
| **`D-00-01`** | Precondition Gatekeeper for Buyer Verification | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** เป็นข้อกำหนดการยืนยันตัวตนซาเล้งใน `Admin 01` / `Buyer 01` |
| **`D-00-02`** | Benchmark Price Lock & Variance ($\pm 15\%$) | **สอดคล้อง:** ทุกการเปลี่ยนแปลงราคากลางและการล็อก Price Snapshot มีการบันทึกลง Audit Log และสามารถตรวจสอบย้อนหลังได้ |
| **`D-00-03`** | Dual-Engine Route Optimization | **ไม่เกี่ยวกับ feature นี้โดยตรง เพราะ** เป็นข้อกำหนดอัลกอริทึมจัดคิวและคำนวณเส้นทางอัตโนมัติใน `UC-04` |

