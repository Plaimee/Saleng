# PLAN-S04: แผนทางเทคนิคระบบราคาและการตัดสินใจ (`plan.md`)

- **Version:** `1.0` | **Status:** `ready-for-tasks` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิง:** [`specs/seller/04-pricing-and-decision/spec.md`](./spec.md) (v2.0), [`specs/000-shared/constraints.md`](../../000-shared/constraints.md), [`specs/000-shared/quality-requirements.md`](../../000-shared/quality-requirements.md)

---

## การตัดสินใจทางเทคนิค (`HOW` — `P-01` ถึง `P-06`)

### `P-01`: การคำนวณช่วงราคาประเมินแบบเรียลไทม์และตะกร้าหลายรายการ (Multi-Item Basket)
- **Traceability:** `<- AC-S04-02, BR-01, D-06, Card 01`
- **การทำงาน:**
  - คำนวณแบบ 2 ชั้น: ประมวลผลบน Client ทันที (`< 100ms`) เพื่อให้ผู้ขายเห็นตัวเลขทันที และประมวลผลซ้ำบน Server (`FastAPI`) เพื่อความถูกต้องและรักษาความปลอดภัย
  - สูตรคำนวณแต่ละรายการ:
    $$\text{item\_min} = \text{quantity} \times \text{min\_price\_per\_unit}$$
    $$\text{item\_max} = \text{quantity} \times \text{max\_price\_per\_unit}$$
  - สรุปยอดรวม Min-Max ของทั้งคำขอ:
    $$\text{total\_est\_min} = \sum \text{item\_min}_i, \quad \text{total\_est\_max} = \sum \text{item\_max}_i$$
  - แสดงข้อความกำกับตามกฎ `BR-01`: `"ราคาจริงขึ้นกับสภาพของหน้างาน"`
- **ทางเลือกที่ปฏิเสธ:** แสดงเป็นตัวเลขเดี่ยวค่าเฉลี่ย (ขัดกฎ `BR-01` และทำให้เกิดข้อพิพาทหน้างาน)

### `P-02`: การจัดการหน่วย "กระสอบ" และราคาเหมาต่อกระสอบสำหรับขวดแก้ว/ขวดพลาสติก
- **Traceability:** `<- AC-S04-05, D-02`
- **การทำงาน:**
  - ในฟอร์มระบุของเก่า หากเป็นหมวดขวดแก้วหรือขวดพลาสติก ระบบอนุญาตให้เลือกหน่วยเป็น `"bag"` (กระสอบ) ได้โดยตรง
  - ในตารางราคากลาง (`benchmark_prices`) มีเรตราคาเหมาต่อกระสอบ (เช่น ขวดแก้ว `40–60 บาท/กระสอบ`, ขวดพลาสติก `30–50 บาท/กระสอบ`)
- **ทางเลือกที่ปฏิเสธ:** บังคับให้ผู้ขายต้องชั่งน้ำหนักเป็นกิโลกรัมก่อน (ผู้ขายตามบ้านไม่มีตาชั่งใหญ่สำหรับยกชั่งขวดทีละกระสอบ)

### `P-03`: การตรวจสอบเกณฑ์มูลค่าขั้นต่ำ (Guard Logic) และการส่งต่อสถานะคำขอ
- **Traceability:** `<- AC-S04-03, REQ-FN-001, REQ-FN-006, D-01, D-03`
- **การทำงาน:**
  - ตัดสินเกณฑ์ผ่านสำหรับนัดหมายเดี่ยว (`Pass Case`):
    $$\text{is\_pass} = (\text{total\_est\_min} \ge 500.0) \lor (\text{total\_bags} \ge 2)$$
  - หาก `is_pass == True`: อนุญาตให้ผู้ขายกดส่งคำขอนัดหมายเดี่ยว เข้าสู่สถานะ `S2 (Pending)`
  - หาก `is_pass == False` (`Alternative Case`): บล็อกคำขอนัดหมายเดี่ยว และแสดงปุ่มทางเลือก:
    1. **`"ฝากรวมกับจุดรับทางผ่าน"` (`isRouteDropIn = true`):** สร้างคำขอและส่งเข้าสถานะ `S2 (Pending)` ทันทีพร้อมติด Flag พิเศษ เพื่อให้ซาเล้งที่วิ่งผ่านในเส้นทางแวะรับได้ตาม `UC-04`
    2. **`"จุดรับรวมประจำอาคาร/หอพัก"` (`isBuildingGroupDrop = true`):** สร้างคำขอโดยผูกกับ `building_id` และตรวจสอบเกณฑ์น้ำหนักรวมของอาคาร `>= 20 กก.` ก่อนปล่อยใบงานให้ซาเล้ง
- **ทางเลือกที่ปฏิเสธ:** ใช้ `max_price >= 500` (เสี่ยงที่ซาเล้งไปถึงแล้วยอดเงินจริงไม่ถึง 500 บาท ทำให้ซาเล้งเสียค่าน้ำมันฟรี)

### `P-04`: ตารางราคากลางและการอัปเดตอัตโนมัติประจำวัน (Daily Benchmark Price Sync)
- **Traceability:** `<- AC-S04-01, REQ-DAT-001, D-04`
- **การทำงาน:**
  - สร้าง Scheduled Worker รันทุกวันเวลา `06:00 น.` (`CRON: 0 6 * * *`) เพื่ออัปเดตเรตราคากลางในตาราง `benchmark_prices`
  - หน้าจอ Client ดึงข้อมูลราคากลางพร้อมฟิลด์ `last_updated_at` เพื่อแสดงป้ายวันที่และเวลาอัปเดตล่าสุด
- **ทางเลือกที่ปฏิเสธ:** ดึงราคาภายนอกแบบ On-demand ทุกครั้งที่ผู้ใช้เปิดหน้าจอ (เสี่ยงระบบภายนอกล่มหรือช้าเกิน 3 วินาที ขัด `REQ-QA-001`)

### `P-05`: การล็อกราคา (Price Snapshot) ณ จังหวะซาเล้งกดรับนัดหมาย
- **Traceability:** `<- REQ-BR-002, D-04, CC-04`
- **การทำงาน:**
  - ราคาที่แสดงในหน้านี้เป็นช่วงราคาประเมินเบื้องต้น (`est_min_price` - `est_max_price`)
  - เมื่อคำขอเปลี่ยนสถานะจาก `S2 -> S3` (ซาเล้งกดรับนัดหมาย) ระบบจะบันทึกค่าราคากลางต่อหน่วย ณ วินาทีนั้นลงใน `waste_items.locked_unit_price` เพื่อใช้คำนวณเงินหน้างานอย่างไม่เปลี่ยนแปลง
- **ทางเลือกที่ปฏิเสธ:** ล็อกราคาตั้งแต่ขั้นตอนผู้ขายสร้างร่างคำขอ (ทำให้ราคากลางค้างเก่านานเกินไปหากไม่มีซาเล้งรับงานหลายวัน)

### `P-06`: การตรวจสอบความถูกต้องของปริมาณของเก่า (Invalid Quantity Guard)
- **Traceability:** `<- AC-S04-04`
- **การทำงาน:**
  - ใช้ Pydantic Validator บน FastAPI และ Input Validation บน React Form:
    $$\text{quantity} > 0 \quad (\text{type: float/decimal})$$
  - หากระบุ `quantity <= 0` ระบบแจ้งเตือน `"กรุณากรอกปริมาณมากกว่า 0"` และบล็อกการคำนวณทันที
- **ทางเลือกที่ปฏิเสธ:** ปล่อยให้คำนวณได้ 0 บาทแล้วไปบล็อกตอนส่งคำขอ (สร้างความสับสนแก่ผู้ใช้)

---

## 1. เทคโนโลยีที่ใช้ (Tech Stack)

| ส่วนของระบบ | เทคโนโลยีที่เลือก | ที่มา / การกำกับ |
|---|---|---|
| **รูปแบบสถาปัตยกรรม** | Mobile-First Single Page Application (SPA) | มาจาก Constraint กลาง `CC-01` |
| **ความถูกต้องของข้อมูลและ Transaction** | Relational Database + ACID Concurrency | มาจาก Constraint กลาง `CC-04` |
| **ภาษาและเฟรมเวิร์กหลังบ้าน (Backend)** | **Python 3.11 + FastAPI (Pydantic v2, Uvicorn)** | **ทีมเลือกเอง ไม่ได้มาจาก spec** |
| **ฐานข้อมูลและแพลตฟอร์มคลาวด์ (Database & BaaS)** | **Supabase (PostgreSQL 15+)** | **ทีมเลือกเอง ไม่ได้มาจาก spec** |
| **หน้าบ้าน (Frontend)** | **HTML5 / React 18+ (Vite, TailwindCSS)** | **ทีมเลือกเอง ไม่ได้มาจาก spec** |
| **เครื่องมือทดสอบอัตโนมัติ (Automated Testing)** | **Pytest (Backend) + Vitest / React Testing Library (Frontend)** | **ทีมเลือกเอง ไม่ได้มาจาก spec** |

---

## 2. โครงสร้างโฟลเดอร์ (Folder Structure)

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── pricing.py              <- REQ-DAT-001, REQ-FN-001, AC-S04-01..05
│   ├── core/
│   │   ├── config.py                   <- D-01 (THRESHOLD_MIN_BAHT=500), D-04
│   │   └── supabase.py                 <- CC-04, Supabase client
│   ├── models/
│   │   └── pricing_models.py           <- MD-DOM-04, REQ-DAT-001, BR-01
│   ├── services/
│   │   ├── pricing_service.py          <- AC-S04-02, AC-S04-05, BR-01, D-06
│   │   └── order_submission_service.py <- AC-S04-03, REQ-FN-001, REQ-FN-006, D-01, D-03
│   └── cron/
│       └── daily_price_updater.py      <- AC-S04-01, REQ-DAT-001, D-04 (06:00 AM)
└── tests/
    ├── test_AC_S04_01_benchmark_price.py
    ├── test_AC_S04_02_instant_calculation.py
    ├── test_AC_S04_03_minimum_threshold.py
    ├── test_AC_S04_04_invalid_quantity.py
    └── test_AC_S04_05_bag_unit_pricing.py

frontend/
├── src/
│   ├── components/
│   │   ├── BenchmarkPriceTable.jsx     <- AC-S04-01, REQ-DAT-001
│   │   ├── ItemPriceCalculator.jsx     <- AC-S04-02, AC-S04-05, BR-01
│   │   ├── MultiItemBasketSummary.jsx  <- AC-S04-02, D-06
│   │   └── ThresholdGuardModal.jsx     <- AC-S04-03, REQ-FN-001, REQ-FN-006, D-03
│   ├── pages/
│   │   └── PricingDecisionPage.jsx     <- AC-S04-01..05
│   └── services/
│       └── pricingApi.js               <- AC-S04-01..05
└── tests/
    ├── AC-S04-01.test.jsx
    ├── AC-S04-02.test.jsx
    ├── AC-S04-03.test.jsx
    ├── AC-S04-04.test.jsx
    └── AC-S04-05.test.jsx
```

---

## 3. ฐานข้อมูล (Data Model — Supabase / PostgreSQL)

### 3.1 ตาราง `benchmark_prices` (ตารางราคากลางอ้างอิงรายวัน — `REQ-DAT-001`)
```sql
CREATE TABLE benchmark_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg', -- 'kg' หรือ 'bag' (D-02)
    min_price_per_unit NUMERIC(10, 2) NOT NULL CHECK (min_price_per_unit > 0),
    max_price_per_unit NUMERIC(10, 2) NOT NULL CHECK (max_price_per_unit >= min_price_per_unit),
    grading_condition TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.2 ตาราง `waste_pickup_orders` (คำขอนัดหมาย — `MD-DOM-04`)
```sql
CREATE TABLE waste_pickup_orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL,
    pickup_location_id UUID NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'S1', -- 'S1' ถึง 'S9' ตาม MD-STM-04
    total_est_min_price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    total_est_max_price NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    is_route_drop_in BOOLEAN NOT NULL DEFAULT FALSE, -- REQ-FN-001, D-03
    is_building_group_drop BOOLEAN NOT NULL DEFAULT FALSE, -- REQ-FN-006, D-03
    building_id UUID NULL,
    version INT NOT NULL DEFAULT 1, -- Optimistic Locking ตาม CC-04
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 3.3 ตาราง `waste_items` (รายการของเก่าในคำขอ — `MD-DOM-04`)
```sql
CREATE TABLE waste_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES waste_pickup_orders(order_id) ON DELETE CASCADE,
    category_code VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg', -- 'kg' หรือ 'bag' (D-02)
    est_quantity NUMERIC(10, 2) NOT NULL CHECK (est_quantity > 0), -- AC-S04-04
    est_min_price NUMERIC(10, 2) NOT NULL,
    est_max_price NUMERIC(10, 2) NOT NULL,
    actual_weight NUMERIC(10, 2) NULL, -- ชั่งจริงหน้างาน S5 (REQ-FN-005)
    locked_unit_price NUMERIC(10, 2) NULL, -- Price Snapshot ตอน S2 -> S3 (REQ-BR-002, D-04)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 4. รายการ API (Endpoints)

| ลำดับ | Method | Path | Request Body | Response Body / Status | รองรับ `REQ` / `AC` |
|---|---|---|---|---|---|
| 1 | `GET` | `/api/v1/pricing/benchmark-prices` | ไม่มี | `200 OK`<br>`{ prices: [...], last_updated_at: "2026-11-03T06:00:00Z" }` | `REQ-DAT-001`, `AC-S04-01`, `D-04` |
| 2 | `POST` | `/api/v1/pricing/calculate-estimate` | `{ items: [ { category_code, unit, quantity } ] }` | `200 OK`<br>`{ items: [...], total_min, total_max, disclaimer, time_ms }`<br>`422 Unprocessable Entity` หาก quantity <= 0 | `Card 01`, `BR-01`, `AC-S04-02`, `AC-S04-04`, `AC-S04-05`, `D-02`, `D-06` |
| 3 | `POST` | `/api/v1/orders/validate-and-submit` | `{ seller_id, pickup_location_id, items: [...], submission_type: "DIRECT" \| "ROUTE_DROP_IN" \| "BUILDING_GROUP" }` | `201 Created` `{ order_id, status: "S2", ... }`<br>`400 Bad Request` `{ error: "MINIMUM_THRESHOLD_NOT_MET", min_price, allowed_alternatives: [...] }` | `REQ-FN-001`, `REQ-FN-006`, `AC-S04-03`, `D-01`, `D-03` |

---

## 5. การต่อระบบภายนอก (External Interfaces)

1. **Supabase PostgreSQL Interface:**
   - เชื่อมต่อผ่าน Supabase Client (`supabase-py`) และ PostgREST API
   - ตรวจสอบ Row Level Security (RLS) และใช้ Service Role สำหรับงานระบบเบื้องหลัง
2. **Daily Price Sync Cron Worker:**
   - Service รันตามกำหนดเวลา `06:00 น.` ทุกวันเพื่อรีเฟรชราคากลางลงฐานข้อมูล Supabase (`D-04`)
3. **Mock & Adapters สำหรับการทดสอบ (Automated Testing):**
   - `MockPricingRepository`: จำลองตารางราคากลางออฟไลน์สำหรับการทดสอบความเร็วในระดับ Unit/Integration Test
   - `MockBuildingTrashService`: จำลองจุดทิ้งรวมของอาคารเพื่อทดสอบเงื่อนไขสะสมน้ำหนัก `>= 20 กก.`

---

## 6. แผนหน้าจอ (UI Plan)

ออกแบบเป็น Mobile-First SPA บนหน้าจอเดียว เชื่อมโยงตาม `spec.md` และ `constraints.md`:
1. **Header & Date Banner:** แสดงหัวข้อ "ราคากลางวันนี้" พร้อมป้ายกำกับ "อัปเดตล่าสุด: วันนี้ 06:00 น." (`AC-S04-01`)
2. **Item Input & Unit Switcher:** ช่องเลือกประเภทขยะและกรอกจำนวน พร้อมปุ่มสลับหน่วย `[กก.]` / `[กระสอบ]` สำหรับขวด (`AC-S04-05`)
3. **Live Min–Max Calculation:** แสดงช่วงราคาประเมินต่อชิ้นและยอดรวมทันทีเมื่อกรอกตัวเลข พร้อมข้อความกำกับ *"ราคาจริงขึ้นกับสภาพของหน้างาน"* (`AC-S04-02`, `BR-01`)
4. **Multi-Item Basket View:** รายการขยะในตะกร้าพร้อมปุ่มลบ/แก้ไข และแถบสรุปยอดรวม Min-Max ด้านล่าง (`D-06`)
5. **Threshold Guard Modal (Popup):** แสดงป๊อปอัปแจ้งเตือนเมื่อ `min_price < 500` และ `bags < 2` พร้อม 2 ปุ่มทางเลือก:
   - ปุ่ม *"ฝากรวมจุดรับทางผ่าน"* (ส่งเข้า `S2` ทันทีพร้อม `isRouteDropIn = true`)
   - ปุ่ม *"จุดรับรวมประจำอาคาร"* (`isBuildingGroupDrop = true`)

---

## 7. การจัดการค่าคงที่และการแยก Config (`Q-xx` / `AS-xx` / Config Isolation)

| รหัส Config | ค่าตั้งต้น | การใช้งานและความหมาย | อ้างอิงการตัดสินใจ |
|---|---|---|---|
| `THRESHOLD_MIN_ESTIMATED_BAHT` | `500.0` | เกณฑ์มูลค่าประเมินขั้นต่ำ (บาท) โดยใช้ `min_price` ตัดสิน | `D-01`, `AC-S04-03` |
| `THRESHOLD_MIN_BAGS` | `2` | จำนวนกระสอบขั้นต่ำสำหรับขวดแก้ว/พลาสติก | `D-01`, `AC-S04-03` |
| `THRESHOLD_BUILDING_KG` | `20.0` | เกณฑ์น้ำหนักสะสมรวมขั้นต่ำสำหรับจุดรับรวมประจำอาคาร | `REQ-FN-006`, `D-03` |
| `BENCHMARK_PRICE_REFRESH_TIME` | `"06:00"` | เวลาอัปเดตราคากลางประจำวัน | `D-04`, `AC-S04-01` |
| `PRICE_CALCULATION_TIMEOUT_MS` | `3000` | เกณฑ์เวลาสูงสุดในการคำนวณและแสดงผลช่วงราคา | `AC-S04-02`, `REQ-QA-001` |

---

## 8. ตารางตรวจ Constraints กลาง และ Non-goals

### 8.1 ตารางตรวจสอบ Constraints กลางจาก `specs/000-shared/constraints.md`

| รหัส | ข้อกำหนดใน Constraint กลาง | ผลการตรวจสอบในแผนนี้ |
|---|---|---|
| **`CC-01`** | Web App แบบ Mobile-First SPA รองรับสมาร์ตโฟนราคาประหยัด | **สอดคล้อง** — ออกแบบหน้าจอด้วย React + TailwindCSS แบบ Single-Page น้ำหนักเบา โหลดเร็ว ไม่กิน RAM |
| **`CC-02`** | GPS Sync Interval ทุก 60 วินาทีขณะพร้อมรับงาน | **ไม่เกี่ยวกับ feature นี้ เพราะ** ฟีเจอร์นี้เป็นฝั่งผู้ขายคำนวณราคากลางก่อนนัดหมาย ไม่มีการแทร็กพิกัดซาเล้งแบบเรียลไทม์ |
| **`CC-03`** | Road Distance API รัศมี <= 5 กม. พร้อม Haversine Fallback | **ไม่เกี่ยวกับ feature นี้ เพราะ** การคำนวณระยะทางถนนเป็นหน้าที่ของโมดูลค้นหางานฝั่งซาเล้ง (`UC-04`) |
| **`CC-04`** | PostgreSQL + PostGIS พร้อม Optimistic Concurrency Control | **สอดคล้อง** — ใช้ Supabase (PostgreSQL) พร้อมฟิลด์ `version` ในตาราง `waste_pickup_orders` |
| **`CC-05`** | Offline Cache ใน IndexedDB / Local Storage | **สอดคล้อง** — หน้าบ้านแคชตารางราคากลางล่าสุด (`benchmark_prices`) ใน Local Storage เพื่อให้ดูราคาได้แม้ออฟไลน์ชั่วคราว |
| **`CC-06`** | PDPA & PII Masking ซ่อนพิกัดละเอียดจนกว่าจะรับงาน | **สอดคล้อง** — หน้าราคานี้ทำงานในขั้นตอน `S1 (Draft)` ยังไม่มีการเปิดเผยข้อมูลส่วนบุคคลหรือที่อยู่ของผู้ขาย |
| **`REQ-SEC-001`** | บันทึกการเปลี่ยนสถานะใบงานลงใน Audit Log แบบ Append-only | **สอดคล้อง** — เมื่อส่งคำขอผ่านการตรวจเกณฑ์และเปลี่ยนเป็น `S2` ระบบจะบันทึก Log ลงตาราง AuditLog |
| **`REQ-SEC-002`** | ปกปิดบ้านเลขที่และแปลงเบอร์โทรศัพท์เป็น `08X-XXX-XXXX` | **ไม่เกี่ยวกับ feature นี้ เพราะ** หน้านี้ยังไม่ได้แสดงข้อมูลผู้ขายให้ผู้ซื้อเห็น |
| **`REQ-OP-001`** | รองรับการทำงานในโหมด Offline Queue | **สอดคล้อง** — รองรับการแคชราคากลางเปิดดูออฟไลน์ |
| **`REQ-OP-002`** | Fallback การคำนวณระยะทางเมื่อ Maps API ล่ม | **ไม่เกี่ยวกับ feature นี้ เพราะ** ไม่มีการเรียก Routing API ในการคำนวณราคาของเก่า |
| **`D-00-01`** | KYC เป็น Precondition ของระบบผู้ซื้อ | **ไม่เกี่ยวกับ feature นี้ เพราะ** หน้านี้เป็นฝั่งผู้ขาย |
| **`D-00-02`** | ซ่อนพิกัดผู้ขายจนกว่าจะรับงาน | **สอดคล้อง** — ไม่มีการส่งพิกัดบ้านของผู้ขายในหน้านี้ |
| **`D-00-03`** | หยุดขอบเขตที่สถานะมีผู้รับงานแล้ว | **สอดคล้อง** — หน้านี้ดูแลการสร้างและส่งคำขอที่สถานะ `S1 -> S2` เท่านั้น |

### 8.2 การยืนยันขอบเขตและ Non-goals
- **ยืนยันไม่สร้างระบบบันทึกซาเล้งคนโปรดในฟีเจอร์นี้:** ตามข้อตกลง `CC-03` และ `D-05` ขอบเขตนี้ถูกตัดออกเพื่อป้องกัน Orphan Code และขอบเขตซ้ำซ้อนกับ `specs/seller/03` และ `07`
- **ยืนยันไม่สร้างระบบชั่งน้ำหนักจริงหน้างาน:** ขอบเขตการชั่งจริงถูกจำกัดให้อยู่ในสถานะ `S5` ของโมดูลรับซื้อหน้างาน (`specs/002-route` และ `seller/05`)
- **ยืนยันไม่สร้างระบบสมัครสมาชิก/ยืนยันตัวตน:** ให้ถือเป็น Precondition ที่ทำใน `seller/01` แล้ว

---

## 9. ตารางความครอบคลุม (`Traceability Matrix: REQ / AC -> P-xx`)

| รหัส REQ / AC | หัวข้อความต้องการ / เกณฑ์การยอมรับ | การตัดสินใจทางเทคนิคที่รองรับ (`P-xx`) |
|---|---|---|
| `REQ-DAT-001` / `AC-S04-01` | ตารางช่วงราคากลางอ้างอิงรายวัน อัปเดตทุกวันเวลา 06:00 น. | `P-04` |
| `Card 01`, `BR-01` / `AC-S04-02` | คำนวณช่วงราคาประเมินทันที `<= 3 วินาที` พร้อมข้อความกำกับ และรองรับตะกร้าหลายรายการ | `P-01` |
| `REQ-FN-001`, `REQ-FN-006` / `AC-S04-03` | ตรวจสอบเกณฑ์ขั้นต่ำ 500 บาท (min_price) หรือ 2 กระสอบ พร้อมทางเลือกจุดรับทางผ่าน/จุดรับรวมอาคาร | `P-03` |
| `Card 01 Exception` / `AC-S04-04` | บล็อกการคำนวณและแจ้งเตือนเมื่อกรอกปริมาณ `<= 0` | `P-06` |
| `D-02` / `AC-S04-05` | รองรับการเลือกหน่วยเป็น "กระสอบ" สำหรับขวดแก้ว/พลาสติก พร้อมคำนวณราคาเหมาต่อกระสอบ | `P-02` |
| `REQ-BR-002` / `D-04` | ล็อกราคา Price Snapshot ณ จังหวะซาเล้งกดรับนัดหมาย (`S2 -> S3`) | `P-05` |
