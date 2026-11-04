# แผนสถาปัตยกรรมและเทคโนโลยี: ระบบจัดการราคากลางและหมวดหมู่วัสดุ (`specs/admin/02-benchmark-price-and-grading/plan.md`)

- **Version:** `1.0` | **Status:** `ready-for-tasks` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิงสเปก:** [`specs/admin/02-benchmark-price-and-grading/spec.md`](./spec.md) (v2.0)
- **Use Cases หลัก:** `UC-03: ตรวจสอบราคากลางประจำวัน` และ `UC-05: ประเมินราคาของชิ้นใหญ่เหมาจ่าย` ([`docs/srs/use-cases.md`](../../../docs/srs/use-cases.md))
- **ข้อจำกัดกลาง:** [`specs/000-shared/constraints.md`](../../000-shared/constraints.md) (`CC-01..CC-06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)

---

## 1. เทคโนโลยีที่ใช้ (Technology Stack & Architecture)

> [!NOTE]
> **หมายเหตุด้านเทคโนโลยี:** เทคโนโลยีที่ใช้ในโมดูลนี้ **`"ทีมเลือกเอง ไม่ได้มาจาก spec"`** เพื่อให้สอดคล้องกับโครงสร้างและฐานโค้ดหลักของระบบ Saleng:

- **Backend Framework:** **Python 3.11 + FastAPI**
  - สถาปัตยกรรมแบบแยกส่วน: Router (`api/v1/benchmark_price_grading.py`), Service Layer (`services/benchmark_price_grading_service.py`), และ Data Models (`models/benchmark_price_grading_models.py`)
  - ตรวจสอบความถูกต้องของข้อมูลและ Schema ด้วย **Pydantic v2** (ตรวจสอบ `min_price > 0`, `max_price >= min_price`, ทศนิยมไม่เกิน 2 ตำแหน่ง ตาม `D-A02-02`)
  - ควบคุมการเข้าถึงด้วย Role-based Header (`X-Admin-Role: ADMIN`) ส่งกลับ `HTTP 403 Forbidden` หากไม่ใช่แอดมินตาม `CC-03` และ `D-A02-06`
  - มาตรฐานรหัสตอบกลับ HTTP: `200 OK`, `201 Created`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`
- **Database & State Store:** **Supabase (PostgreSQL 15+)**
  - ตาราง `benchmark_prices` (หมวดหมู่วัสดุรีไซเคิลและขยะชิ้นใหญ่, ช่วงราคา Min-Max, วันที่บังคับใช้)
  - ตาราง `quality_grading_rules` (เกณฑ์คุณภาพ 3 ระดับ: `GRADE_A`, `GRADE_B`, `GRADE_C` พร้อม % การหักสิ่งปนเปื้อน `0%`, `5%`, `10%`)
  - ตาราง `price_history_logs` สำหรับเก็บประวัติการปรับเปลี่ยนราคาย้อนหลัง
  - ตาราง `audit_logs` สำหรับจัดเก็บบันทึกประวัติความปลอดภัยตาม `REQ-SEC-001`
- **Frontend Framework:** **React 18 + Vite + TailwindCSS**
  - ออกแบบเป็น Single-Page Application (SPA) รองรับทั้งจอมือถือและเดสก์ท็อปของแอดมินตาม `CC-01`
  - ทัชทาร์เก็ตปุ่มกดและฟังก์ชันสำคัญขนาดไม่ต่ำกว่า `48px` ทุกปุ่มตาม `REQ-UX-001`
  - มีกล่องเตือนยืนยัน (Confirmation Warning Modal) เมื่อราคาเปลี่ยนเกิน `±50%` ตาม `D-A02-02`
  - แอดมินทำงานแบบ **Online-only** ตาม `CC-05` และ `D-A02-06` เพื่อความปลอดภัยในการเผยแพร่ราคาแบบเรียลไทม์
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
│   │   │   ├── benchmark_price_grading.py           # [NEW] FastAPI Router สำหรับ Admin ราคากลางและเกณฑ์คุณภาพ
│   │   │   └── pricing.py                          # [UPDATE] เมานต์ benchmark_price_grading.router เข้ากับแอปหลัก
│   │   ├── core/
│   │   │   └── supabase.py                         # [UPDATE] เพิ่ม helper methods สำหรับ benchmark_prices และ grading rules
│   │   ├── models/
│   │   │   └── benchmark_price_grading_models.py   # [NEW] Pydantic Schemas สำหรับราคากลาง, เกณฑ์คุณภาพ, และประวัติราคา
│   │   └── services/
│   │       └── benchmark_price_grading_service.py  # [NEW] Service ตรรกะธุรกิจ ราคากลางประจำวัน, การตรวจราคา, และ Snapshot
│   └── tests/
│       ├── test_T01_benchmark_grading_models.py    # [NEW] ทดสอบ Pydantic Models & Store methods
│       ├── test_AC_A02_01_benchmark_publishing.py  # [NEW] ทดสอบการเผยแพร่ราคากลางรายวัน, Fallback, และ Validation
│       ├── test_AC_A02_02_grading_rules.py         # [NEW] ทดสอบการกำหนดเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน
│       ├── test_AC_A02_03_bulky_item_prices.py     # [NEW] ทดสอบช่วงราคาประเมินขยะชิ้นใหญ่เหมาจ่าย (PIECE)
│       ├── test_AC_A02_04_price_snapshot_integrity.py # [NEW] ทดสอบผลกระทบต่อออเดอร์ S1/S2 vs S3..S7 (Snapshot Lock)
│       ├── test_AC_A02_05_admin_price_audit.py     # [NEW] ทดสอบ Admin RBAC Header (403) และ Audit Logging
│       └── test_e2e_admin_benchmark_price_grading.py # [NEW] ทดสอบ Integration E2E เต็มวงจรรอบด้าน
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── admin/
│   │   │       ├── BenchmarkPriceTable.jsx         # [NEW] ตารางจัดการราคากลางรายวัน + แก้ไข Min-Max + เตือน 50%
│   │   │       ├── QualityGradingRuleCard.jsx      # [NEW] การ์ดเกณฑ์คุณภาพ 3 ระดับ + % หักสิ่งปนเปื้อน
│   │   │       ├── BulkyItemPriceTable.jsx         # [NEW] ตารางราคาเหมาจ่ายขยะชิ้นใหญ่ (หน่วย PIECE)
│   │   │       └── AdminBenchmarkGradingView.jsx   # [NEW] หน้าจอหลักแอดมินแท็บคู่ (data-req="UC-03")
│   │   └── services/
│   │       └── adminBenchmarkApi.js                # [NEW] Frontend API Client สำหรับติดต่อ Admin Benchmark Endpoints
│   └── tests/
│       ├── adminBenchmarkApi.test.mjs              # [NEW] ทดสอบ Vitest สำหรับ adminBenchmarkApi
│       ├── AC-A02-01.test.jsx                      # [NEW] ทดสอบการแสดงผลตารางราคาและการแก้ไขช่วงราคาใน UI
│       ├── AC-A02-02.test.jsx                      # [NEW] ทดสอบการปรับเกณฑ์คุณภาพและการหักสิ่งปนเปื้อนใน UI
│       └── AC-A02-03.test.jsx                      # [NEW] ทดสอบการจัดการราคาขยะชิ้นใหญ่ใน UI
```

---

## 3. การออกแบบฐานข้อมูล / Data Models (Database & Schema Design)

### 3.1 ตาราง `benchmark_prices` (ราคากลางอ้างอิงรายวัน — `REQ-DAT-001`, `BR-01`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `id` | `UUID / String` | รหัสอ้างอิงราคากลาง (Primary Key) |
| `category_code` | `String` | รหัสหมวดหมู่วัสดุ (เช่น `MAT-CARDBOARD`, `MAT-PLASTIC-BOTTLE`, `BULKY-FRIDGE`) |
| `category_name` | `String` | ชื่อหมวดหมู่ภาษาไทย (เช่น กระดาษลัง, ขวดพลาสติกใส, ตู้เย็น) |
| `unit` | `String` | หน่วยนับ: `kg` (ของเก่าทั่วไป) หรือ `piece` (ขยะชิ้นใหญ่เหมาจ่าย) |
| `min_price_per_unit` | `Float` | ราคาต่ำสุดของช่วง (`> 0`, ทศนิยม $\le 2$ ตำแหน่ง) |
| `max_price_per_unit` | `Float` | ราคาสูงสุดของช่วง (`>= min_price_per_unit`, ทศนิยม $\le 2$ ตำแหน่ง) |
| `grading_condition` | `String` | เงื่อนไขคุณภาพการคัดแยกเบื้องต้น |
| `effective_date` | `String (YYYY-MM-DD)` | วันที่ราคาเริ่มมีผลบังคับใช้ |
| `is_active` | `Boolean` | สถานะเปิดใช้งานหมวดหมู่นี้ (ค่าเริ่มต้น `True`) |
| `updated_at` | `String (ISO 8601)` | วันเวลาที่อัปเดตล่าสุด |
| `updated_by` | `String` | รหัสแอดมินผู้อัปเดต |

### 3.2 ตาราง `quality_grading_rules` (เกณฑ์คุณภาพและการหักสิ่งปนเปื้อน — `REQ-FN-003`, `D-A02-03`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `rule_id` | `UUID / String` | รหัสอ้างอิงกฎเกณฑ์คุณภาพ |
| `category_code` | `String` | รหัสหมวดหมู่วัสดุที่เกี่ยวข้อง |
| `grade_level` | `String` | `GRADE_A` (สะอาดสมบูรณ์), `GRADE_B` (ปนเปื้อนเล็กน้อย), `GRADE_C` (ปนเปื้อนมาก) |
| `grade_name` | `String` | ชื่อเรียกเกรดภาษาไทย |
| `description` | `String` | คำอธิบายสภาพทางกายภาพ เช่น แห้งสนิท, มีลวดเย็บ, เปียกน้ำ |
| `contamination_deduction_percent` | `Float` | เปอร์เซ็นต์การหักสิ่งปนเปื้อน: `GRADE_A` (0.0%), `GRADE_B` (5.0%), `GRADE_C` (10.0%) |
| `price_target` | `String` | ตำแหน่งราคาที่ใช้: `MAX` (ขอบบน), `MID` (กึ่งกลาง), `MIN` (ขอบล่าง) |
| `updated_at` | `String (ISO 8601)` | วันเวลาที่อัปเดตล่าสุด |
| `updated_by` | `String` | รหัสแอดมินผู้อัปเดต |

### 3.3 ตาราง `price_history_logs` (ประวัติการปรับเปลี่ยนราคา)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `history_id` | `String` | รหัสประวัติ (UUID) |
| `category_code` | `String` | รหัสหมวดหมู่ |
| `old_min_price` | `Float` | ราคาต่ำสุดเดิม |
| `old_max_price` | `Float` | ราคาสูงสุดเดิม |
| `new_min_price` | `Float` | ราคาต่ำสุดใหม่ |
| `new_max_price` | `Float` | ราคาสูงสุดใหม่ |
| `changed_at` | `String (ISO 8601)` | วันเวลาที่เปลี่ยนแปลง |
| `changed_by` | `String` | รหัสแอดมินผู้กระทำ |
| `change_reason` | `Optional[String]` | เหตุผลการปรับเปลี่ยนราคา (ถ้ามี) |

### 3.4 ตาราง `audit_logs` (บันทึกประวัติความปลอดภัยตาม `REQ-SEC-001`)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `log_id` | `String` | รหัสบันทึกประวัติ (UUID) |
| `action` | `String` | `ADMIN_UPDATED_BENCHMARK_PRICE`, `ADMIN_UPDATED_GRADING_RULES` |
| `entity_id` | `String` | รหัสหมวดหมู่วัสดุ (`category_code`) |
| `actor_id` | `String` | รหัสแอดมินผู้กระทำ (เช่น `admin-01`) |
| `actor_role` | `String` | ค่าคงที่ `'ADMIN'` |
| `details` | `JSON / Dict` | รายละเอียดค่าราคาก่อน-หลังแก้ และค่าความเปลี่ยนแปลง % |
| `timestamp` | `String (ISO 8601)` | เวลาประทับที่เกิดเหตุการณ์ |

---

## 4. การออกแบบ API / Endpoints (API Specification)

ทุกเส้นทางต้องระบุ Header `X-Admin-Role: ADMIN` ตามข้อกำหนด `CC-03` และ `D-A02-06`

### 4.1 รายการ API สำหรับแอดมิน

| Method | Endpoint | Request Body | Response (Success) | Error Codes |
| :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/admin/benchmark-prices` | Params: `unit` (`all`, `kg`, `piece`), `q` | `List[BenchmarkPriceAdminItem]` พร้อมวันเวลาอัปเดตล่าสุด | `401`, `403` |
| `PUT` | `/api/v1/admin/benchmark-prices/{category_code}` | `UpdateBenchmarkPriceRequest` (`min_price`, `max_price`, `grading_condition`, `confirm_shift`) | `BenchmarkPriceResponse` (`success`, `category_code`, `new_min`, `new_max`) | `400`, `403`, `404`, `422` |
| `POST` | `/api/v1/admin/benchmark-prices/batch-update` | `BatchUpdateBenchmarkPricesRequest` (`items: List[...]`, `effective_date`) | `BatchUpdateResponse` (`success`, `updated_count`) | `400`, `403`, `422` |
| `GET` | `/api/v1/admin/benchmark-prices/grading/{category_code}` | - | `List[QualityGradingRuleItem]` (เกรด A, B, C) | `401`, `403`, `404` |
| `PUT` | `/api/v1/admin/benchmark-prices/grading/{category_code}` | `UpdateGradingRulesRequest` (`rules: List[...]`) | `GradingRulesResponse` (`success`, `category_code`) | `400`, `403`, `404`, `422` |
| `GET` | `/api/v1/admin/benchmark-prices/history/{category_code}` | Params: `limit` (default 20) | `List[PriceHistoryLogItem]` | `401`, `403`, `404` |

---

## 5. แผนการเชื่อมต่อระบบภายนอก (External Integrations / Third-party Services)

- **Mock Supabase Store:** ใช้งาน In-Memory Storage Adapter ใน `backend/app/core/supabase.py` ขยายฟังก์ชัน `benchmark_prices`, `quality_grading_rules`, และ `price_history_logs` สำหรับทดสอบแบบ Offline Testing
- **Public API Synchronization:** เมื่อแอดมินอัปเดตราคากลาง ฝั่งผู้ขาย (`/api/v1/pricing/benchmark-prices`) และฝั่งซาเล้งจะได้รับราคาล่าสุดแบบ Real-time ทันทีตามเงื่อนไข `D-A02-05`
- **ระบบภายนอกในอนาคต (Non-goals):** ไม่เชื่อมต่อ API ตลาดซื้อขายขยะรีไซเคิลต่างประเทศอัตโนมัติใน MVP นี้ แอดมินเป็นผู้ควบคุมราคาเอง (`Human-in-the-loop`)

---

## 6. แผนการสร้างหน้าจอและปฏิสัมพันธ์ (Frontend Components & Interactions)

- **Layout & Structure:** หน้าจอแดชบอร์ดแอดมิน (SPA) จัดวางเป็น 2 แท็บหลัก:
  1. **แท็บที่ 1: ตารางราคากลางรายวันและของชิ้นใหญ่ (`BenchmarkPriceTable.jsx` & `BulkyItemPriceTable.jsx`)**
     - แสดงรายการวัสดุรีไซเคิลจำแนกตามประเภท (กระดาษ, พลาสติก, โลหะ, แก้ว) และหมวดขยะชิ้นใหญ่ (ตู้เย็น, เครื่องซักผ้า, แอร์, ทีวี)
     - แสดงช่วงราคาปัจจุบัน `min_price – max_price บาท/หน่วย` พร้อมวันเวลาอัปเดตล่าสุด
     - ช่องแก้ไขราคาแบบ Inline หรือ Modal: ตรวจสอบความถูกต้อง `min_price > 0`, `max_price >= min_price`
     - หากราคาเปลี่ยนแปลงเพิ่มขึ้นหรือลดลงเกิน `50%` ระบบจะแสดง Modal เตือนยืนยันก่อนบันทึก (`D-A02-02`)
     - ปุ่ม "บันทึกราคารายการนี้" และปุ่ม "อัปเดตราคาแบบกลุ่ม (Batch Update)"
  2. **แท็บที่ 2: เกณฑ์คุณภาพและการหักสิ่งปนเปื้อน (`QualityGradingRuleCard.jsx`)**
     - แสดงเกณฑ์ 3 ระดับ: `GRADE_A` (หัก 0%), `GRADE_B` (หัก 5%), `GRADE_C` (หัก 10%)
     - สามารถปรับปรุงคำอธิบายสภาพวัสดุ และเปอร์เซ็นต์การหักสิ่งปนเปื้อนได้
  3. **หน้าจอหลักเชื่อมโยง (`AdminBenchmarkGradingView.jsx`)**
     - กำกับแอตทริบิวต์ `data-req="UC-03"` ครบถ้วนทุกคอมโพเนนต์
     - ทุกปุ่มกดมีทัชทาร์เก็ต $\ge 48\text{px}$ ตาม `REQ-UX-001` และ `CC-01`
     - ป้ายสถานะระบุชัดเจนว่าทำงานในโหมด Online-only (`CC-05`)

---

## 7. การจัดการคำถามเปิดและการตัดสินใจ (Decisions & Open Questions)

- **`D-A02-01` (`Q-01`):** กำหนดเวลาตัดรอบเผยแพร่ราคากลางรายวันทางการ ณ เวลา **`06:00 น.`** ของทุกวัน หากไม่ได้อัปเดตระบบจะดึงราคาฐานของวันก่อนหน้ามาใช้อัตโนมัติพร้อมแสดงวันเวลาอัปเดตล่าสุด
- **`D-A02-02` (`Q-02`):** กฎการตรวจสอบช่วงราคา `BR-01`: บังคับ `min_price > 0`, `max_price >= min_price`, ทศนิยมไม่เกิน 2 ตำแหน่ง และมีระบบเตือนยืนยันหากราคาขยับเกิน `±50%` เพื่อป้องกัน Human Error
- **`D-A02-03` (`Q-03`):** เกณฑ์คุณภาพและการหักสิ่งปนเปื้อน 3 ระดับมาตรฐาน: `GRADE_A` (สะอาดสมบูรณ์ หัก 0%), `GRADE_B` (ปนเปื้อนเล็กน้อย หัก 5%), `GRADE_C` (ปนเปื้อนมาก หัก 10%)
- **`D-A02-04` (`Q-04`):** ขยะชิ้นใหญ่เหมาจ่าย (`PIECE`): ตู้เย็น (`200–300 บาท`), เครื่องซักผ้า (`150–250 บาท`), แอร์ (`300–500 บาท`), ทีวี (`50–150 บาท`), เตียง/เฟอร์นิเจอร์ (`0–100 บาท`)
- **`D-A02-05` (`Q-05`):** ผลกระทบต่อออเดอร์: ออเดอร์ `S1` และ `S2` คำนวณราคาใหม่ตามเรตล่าสุด, ออเดอร์ `S3..S7` ล็อกราคาเดิมตาม Price Snapshot ณ เวลาที่ซาเล้งกดรับงานอย่างเคร่งครัด (`REQ-BR-002`, `D-00-02`)
- **`D-A02-06` (`Q-06`):** สิทธิ์แอดมินและความปลอดภัย: ตรวจสอบ Header `X-Admin-Role: ADMIN` (`HTTP 403`), ทำงานแบบ Online-only (`CC-05`), บันทึก Audit Log `ADMIN_UPDATED_BENCHMARK_PRICE` และ `ADMIN_UPDATED_GRADING_RULES` พร้อมค่าเก่าและใหม่

---

## 8. ตารางตรวจ Constraints กลาง (Constraints Compliance Matrix)

| รหัส | หัวข้อข้อจำกัดกลาง (`Constraint`) | การปฏิบัติตามในแผนนี้ (`Compliance Details`) | สถานะ |
| :---: | :--- | :--- | :---: |
| **`CC-01`** | Single-Page Application (SPA) & Touch Target $\ge 48\text{px}$ | ออกแบบแดชบอร์ดแอดมินเป็น React SPA ปุ่มกดแก้ไข บันทึกราคา ปรับเกณฑ์ และปุ่มยืนยัน มีขนาด $\ge 48\text{px}$ ทุกปุ่ม | สอดคล้อง |
| **`CC-02`** | Architecture (FastAPI Backend + React Frontend) | ใช้ FastAPI ในฝั่งหลังบ้าน และ React 18 + TailwindCSS ในฝั่งหน้าบ้าน แยกส่วนชัดเจน | สอดคล้อง |
| **`CC-03`** | Role-based REST Endpoints (`/api/v1/admin/...`) | แยกเส้นทางแอดมินไว้ใต้ `/api/v1/admin/benchmark-prices/...` และตรวจสอบสิทธิ์ผ่าน Header `X-Admin-Role: ADMIN` | สอดคล้อง |
| **`CC-04`** | Optimistic Concurrency Control / ACID Transaction | การอัปเดตราคากลางและเกณฑ์คุณภาพดำเนินการแบบ Atomic พร้อมบันทึกประวัติการเปลี่ยนแปลง | สอดคล้อง |
| **`CC-05`** | Offline Resilience & Network Handling | หน้าจอแอดมินทำงานแบบ **Online-only** ไม่อนุญาตให้อัปเดตราคากลางออฟไลน์ เพื่อให้ราคาสะท้อนตรงกันทั้งระบบแบบเรียลไทม์ | สอดคล้อง |
| **`CC-06`** | PDPA & PII Protection (`REQ-SEC-002`) | ไม่เกี่ยวข้องกับ feature นี้โดยตรง เพราะราคากลางและเกณฑ์คุณภาพเป็นข้อมูลสาธารณะ ไม่มีข้อมูลส่วนบุคคล PII ของผู้ใช้ | สอดคล้อง |
| **`REQ-SEC-001`** | Audit Logging (Append-only) | บันทึกเหตุการณ์ `ADMIN_UPDATED_BENCHMARK_PRICE`, `ADMIN_UPDATED_GRADING_RULES` ลงใน `audit_logs` พร้อมราคาเก่าและใหม่ | สอดคล้อง |
| **`REQ-SEC-002`** | Role-based Data Access & Least Privilege | เฉพาะผู้ที่มีสิทธิ์แอดมิน (`X-Admin-Role: ADMIN`) เท่านั้นจึงจะสามารถเข้าถึง API การแก้ไขราคาและเกณฑ์คุณภาพได้ | สอดคล้อง |
| **`REQ-OP-001`** | Response Time Latency (< 2.0 วินาที P95) | การดึงตารางราคากลางและการบันทึกอัปเดตราคาตอบสนองภายใน `< 2.0 วินาที` (P95) | สอดคล้อง |
| **`REQ-OP-002`** | System Availability & Operational SLA | ไม่เกี่ยวข้องกับ feature นี้โดยตรง เพราะเป็นข้อกำหนด SLA ระดับโครงสร้างพื้นฐานของระบบภาพรวม | สอดคล้อง |
| **`D-00-01`** | Precondition Gatekeeper for Buyer Verification | ไม่เกี่ยวกับ feature นี้โดยตรง เพราะเป็นข้อกำหนดการเปิดสิทธิ์ซาเล้งใน `Admin 01` / `Buyer 01` | สอดคล้อง |
| **`D-00-02`** | Benchmark Price Lock & Variance ($\pm 15\%$) | ล็อกราคา Price Snapshot เมื่อซาเล้งกดรับงาน (`S2 -> S3`) การปรับราคากลางของแอดมินจะไม่กระทบต่อออเดอร์ตั้งแต่ `S3` ขึ้นไปอย่างเคร่งครัด | สอดคล้อง |
| **`D-00-03`** | Dual-Engine Route Optimization | ไม่เกี่ยวข้องกับ feature นี้โดยตรง เพราะเป็นข้อกำหนดอัลกอริทึมจัดคิวและคำนวณเส้นทางใน `UC-04` | สอดคล้อง |

