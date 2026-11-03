# TASKS-S04: รายการงานย่อยระบบราคาและการตัดสินใจ (`tasks.md`)

- **Version:** `1.0` | **Status:** `ready-for-implement` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิง:** [`specs/seller/04-pricing-and-decision/spec.md`](./spec.md) (v2.0), [`specs/seller/04-pricing-and-decision/plan.md`](./plan.md) (v1.0), [`specs/000-shared/constraints.md`](../../000-shared/constraints.md)

---

## 1. รายการงานย่อย (`T-01` ถึง `T-08`)

| รหัส | ทำอะไร | สร้างหรือแก้ไฟล์ไหน | ต้องทำหลัง | รองรับ REQ / AC | เสร็จเมื่อ (Definition of Done) | ยังติดคำถาม (`Q-xx`/`AS-xx`) |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: |
| **`T-01`**<br>`[DONE]` | **ตั้งค่า Config, Supabase Client และสร้าง Data Model:**<br>สร้าง Config ค่าคงที่ระบบ (`THRESHOLD_MIN_ESTIMATED_BAHT = 500.0`, `THRESHOLD_MIN_BAGS = 2`, `THRESHOLD_BUILDING_KG = 20.0`), เชื่อมต่อ Supabase Client และกำหนด Pydantic/SQLAlchemy Schema สำหรับ `benchmark_prices`, `waste_pickup_orders`, และ `waste_items` พร้อมฟิลด์ `unit` ('kg'/'bag') และ `version` | `backend/app/core/config.py`<br>`backend/app/core/supabase.py`<br>`backend/app/models/pricing_models.py` | ไม่มี | `MD-DOM-04`, `REQ-DAT-001`, `CC-04`, `D-01`, `D-02`, `D-04` | รันสคริปต์ Migration หรือ Model Validation สำเร็จ โครงสร้างตารางและ Pydantic schema ตรงตาม Data Model ใน `plan.md §3` ครบถ้วน (`4 passed`) | ไม่มี |
| **`T-02`** | **สร้าง Service และ API ราคากลางประจำวัน พร้อม Scheduled Refresh:**<br>สร้างฟังก์ชันดึงราคากลางตามหมวดหมู่, Worker อัปเดตราคาทุกวันเวลา 06:00 น. (`daily_price_updater.py`), และเปิด Endpoint `GET /api/v1/pricing/benchmark-prices` คืนค่าช่วงราคา Min-Max พร้อมฟิลด์ `last_updated_at` | `backend/app/services/pricing_service.py`<br>`backend/app/cron/daily_price_updater.py`<br>`backend/app/api/v1/pricing.py`<br>`backend/tests/test_AC_S04_01_benchmark_price.py` | `T-01` | `REQ-DAT-001`, `AC-S04-01`, `P-04`, `D-04` | รัน `pytest backend/tests/test_AC_S04_01_benchmark_price.py` ผ่าน 100% ตอบกลับ `200 OK` พร้อมข้อมูลราคากลางและเวลาอัปเดต | ไม่มี |
| **`T-03`** | **สร้าง Service และ API คำนวณช่วงราคาประเมินและ Multi-Item Basket:**<br>พัฒนาลอจิกคำนวณช่วงราคาประเมิน (Min-Max) รองรับทั้งหน่วย `kg` และ `bag` (ราคาเหมาต่อกระสอบสำหรับขวดแก้ว/พลาสติก), รวมยอดทั้งตะกร้า (Multi-Item Basket), ตรวจสอบ `quantity > 0` (บล็อกเมื่อ <= 0), และเปิด Endpoint `POST /api/v1/pricing/calculate-estimate` | `backend/app/services/pricing_service.py`<br>`backend/app/api/v1/pricing.py`<br>`backend/tests/test_AC_S04_02_instant_calculation.py`<br>`backend/tests/test_AC_S04_04_invalid_quantity.py`<br>`backend/tests/test_AC_S04_05_bag_unit_pricing.py` | `T-02` | `Card 01`, `BR-01`, `AC-S04-02`, `AC-S04-04`, `AC-S04-05`, `P-01`, `P-02`, `P-06`, `D-02`, `D-06` | รัน Pytest ครบทั้ง 3 ข้อ:<br>1. `test_AC_S04_02_instant_calculation` ผ่าน<br>2. `test_AC_S04_04_invalid_quantity` ผ่าน (HTTP 422 เมื่อ quantity <= 0)<br>3. `test_AC_S04_05_bag_unit_pricing` ผ่าน | ไม่มี |
| **`T-04`** | **สร้าง Service ตรวจสอบเกณฑ์ขั้นต่ำ 500 บาท และ API ส่งคำขอนัดหมาย:**<br>พัฒนาลอจิก Guard ตรวจสอบ `min_price >= 500.0` หรือขวด `>= 2 กระสอบ`, บล็อกคำขอเดี่ยวหากไม่ผ่านเกณฑ์ พร้อมรองรับทางเลือกสร้างคำขอแบบฝากรวมทางผ่าน (`isRouteDropIn = true` -> สถานะ `S2`) และจุดรับรวมอาคาร (`isBuildingGroupDrop = true`, เกณฑ์รวม `>= 20 กก.`), บันทึก Audit Log และเปิด Endpoint `POST /api/v1/orders/validate-and-submit` | `backend/app/services/order_submission_service.py`<br>`backend/app/api/v1/pricing.py`<br>`backend/tests/test_AC_S04_03_minimum_threshold.py` | `T-03` | `REQ-FN-001`, `REQ-FN-006`, `REQ-SEC-001`, `AC-S04-03`, `P-03`, `P-05`, `D-01`, `D-03` | รัน `pytest backend/tests/test_AC_S04_03_minimum_threshold.py` ผ่าน 100% ครอบคลุมทั้ง Pass Case (>= 500 หรือ >= 2 กระสอบ) และ Alternative Cases (ฝากรวมทางผ่าน / อาคาร) | ไม่มี |
| **`T-05`** | **สร้าง Frontend API Client และโมดูล Local Cache:**<br>พัฒนาฟังก์ชันเรียก API ราคากลาง, คำนวณราคา, และส่งคำขอ พร้อมระบบแคชตารางราคากลางลง `localStorage` เพื่อรองรับการเปิดดูออฟไลน์เบื้องต้นตาม `CC-05` | `frontend/src/services/pricingApi.js` | `T-04` | `CC-01`, `CC-05`, `REQ-OP-001` | มีฟังก์ชันครบ: `fetchBenchmarkPrices()`, `calculateEstimate()`, `submitOrder()` พร้อมระบบ fallback อ่านจาก Cache เมื่อออฟไลน์ | ไม่มี |
| **`T-06`** | **พัฒนาหน้าจอและคอมโพเนนต์ React (Mobile-First SPA):**<br>สร้างหน้าจอ `PricingDecisionPage.jsx` ประกอบด้วย:<br>1. `BenchmarkPriceTable`: ตารางราคากลางพร้อมป้ายอัปเดต 06:00 น.<br>2. `ItemPriceCalculator`: ช่องกรอกขยะ ปริมาณ และสลับหน่วย กก./กระสอบ<br>3. `MultiItemBasketSummary`: สรุปรายการในตะกร้าและช่วงราคารวม Min-Max พร้อมป้ายกำกับตาม `BR-01`<br>4. `ThresholdGuardModal`: ป๊อปอัปบล็อกเมื่อ < 500 บาท พร้อมปุ่มทางเลือกฝากรวมทางผ่านและจุดรับรวมอาคาร | `frontend/src/components/BenchmarkPriceTable.jsx`<br>`frontend/src/components/ItemPriceCalculator.jsx`<br>`frontend/src/components/MultiItemBasketSummary.jsx`<br>`frontend/src/components/ThresholdGuardModal.jsx`<br>`frontend/src/pages/PricingDecisionPage.jsx` | `T-05` | `Card 01`, `BR-01`, `REQ-DAT-001`, `REQ-FN-001`, `REQ-FN-006`, `AC-S04-01..05`, `CC-01` | หน้าจอแสดงผลถูกต้องบนขนาดจอมือถือ (Viewport 375px–414px) ตอบสนองการคำนวณและปุ่มทางเลือกครบถ้วน | ไม่มี |
| **`T-07`** | **สร้างชุดทดสอบหน้าจอ Component & Integration Tests:**<br>เขียน Unit & Component Tests ด้วย Vitest และ React Testing Library เพื่อทดสอบการทำงานของหน้าจอครบทุก Acceptance Criteria (`AC-S04-01` ถึง `AC-S04-05`) | `frontend/tests/AC-S04-01.test.jsx`<br>`frontend/tests/AC-S04-02.test.jsx`<br>`frontend/tests/AC-S04-03.test.jsx`<br>`frontend/tests/AC-S04-04.test.jsx`<br>`frontend/tests/AC-S04-05.test.jsx` | `T-06` | `AC-S04-01`, `AC-S04-02`, `AC-S04-03`, `AC-S04-04`, `AC-S04-05` | รัน `npm run test` (Vitest) ผ่านครบทั้ง 5 ไฟล์ทดสอบ 100% | ไม่มี |
| **`T-08`** | **ทดสอบแบบครบวงจร (End-to-End) และวัดเกณฑ์ประสิทธิภาพ:**<br>ทดสอบ Flow รวมตั้งแต่เปิดหน้าราคากลาง -> เลือกวัสดุและกรอกกระสอบ -> สรุปตะกร้า -> ทดสอบกรณีไม่ถึง 500 บาทให้เปิดป๊อปอัป -> กดยืนยันฝากรวมทางผ่านสำเร็จเข้าสู่ `S2`, ตรวจสอบ Response Time `<= 3.0s` และการคงอยู่ของ Price Snapshot เมื่อเปลี่ยนเป็น `S3` | `backend/tests/test_e2e_pricing_decision.py` | `T-07` | `REQ-QA-001`, `REQ-BR-002`, `D-01..D-06` | รัน Integration Test ผ่านครบทั้งกระบวนการ เวลาในการคำนวณและโหลดผลไม่เกิน 3.0 วินาที (`P95`) | ไม่มี |

---

## 2. ตารางตรวจสอบความครบถ้วนของเกณฑ์การยอมรับ (Two-way Traceability Matrix)

| รหัส `AC` | หัวข้อเกณฑ์การยอมรับ (`Acceptance Criteria`) | งานที่รองรับ (`T-xx`) | การทดสอบที่ตรวจรับ (Test Function / File) | สถานะความครอบคลุม |
| :---: | :--- | :---: | :--- | :---: |
| **`AC-S04-01`** | แสดงตารางช่วงราคากลาง (`ต่ำสุด–สูงสุด`) พร้อมแสดงเวลาอัปเดตล่าสุดทุกวัน ณ เวลา `06:00 น.` | `T-02`, `T-06`, `T-07` | `test_AC_S04_01_benchmark_price.py`<br>`AC-S04-01.test.jsx` | ครบถ้วน (หลังบ้าน + หน้าบ้าน) |
| **`AC-S04-02`** | คำนวณช่วงราคาประเมินและ Multi-Item Basket ภายใน `<= 3 วินาที` พร้อมข้อความกำกับ *"ราคาจริงขึ้นกับสภาพของหน้างาน"* | `T-03`, `T-06`, `T-07`, `T-08` | `test_AC_S04_02_instant_calculation.py`<br>`AC-S04-02.test.jsx` | ครบถ้วน (หลังบ้าน + หน้าบ้าน + E2E) |
| **`AC-S04-03`** | ตรวจสอบเกณฑ์ขั้นต่ำ `min_price >= 500 บาท` หรือขวด `>= 2 กระสอบ` หากไม่ถึงให้บล็อกและเสนอทางเลือก "ฝากรวมจุดรับทางผ่าน" หรือ "จุดรับรวมอาคาร" | `T-04`, `T-06`, `T-07`, `T-08` | `test_AC_S04_03_minimum_threshold.py`<br>`AC-S04-03.test.jsx` | ครบถ้วน (ทั้ง Pass Case และ Alt Cases) |
| **`AC-S04-04`** | บล็อกการคำนวณและแจ้งเตือนเมื่อกรอกปริมาณเป็น `0` หรือค่าติดลบ (`"กรุณากรอกปริมาณมากกว่า 0"`) | `T-03`, `T-06`, `T-07` | `test_AC_S04_04_invalid_quantity.py`<br>`AC-S04-04.test.jsx` | ครบถ้วน (Backend Validation + Frontend Form) |
| **`AC-S04-05`** | รองรับการเลือกหน่วยเป็น `"กระสอบ"` สำหรับขวดแก้ว/พลาสติก และคำนวณราคาเหมาต่อกระสอบได้ถูกต้อง | `T-03`, `T-06`, `T-07` | `test_AC_S04_05_bag_unit_pricing.py`<br>`AC-S04-05.test.jsx` | ครบถ้วน (ราคาเหมาต่อกระสอบ) |

---

## 3. ตารางตรวจสอบความครบถ้วนของข้อจำกัดกลาง (Constraints Traceability)

| รหัส Constraint | ข้อกำหนดใน Constraint กลาง (`specs/000-shared/constraints.md`) | งานที่รองรับ (`T-xx`) | รายละเอียดการปฏิบัติตาม |
| :---: | :--- | :---: | :--- |
| **`CC-01`** | Mobile-First Web SPA รองรับมือถือราคาประหยัด (`RAM >= 2 GB`) | `T-06`, `T-07` | สร้างหน้าจอแบบ SPA ด้วย React + TailwindCSS ไม่ใช้ไลบรารีหนัก โหลดเร็วบนมือถือ |
| **`CC-02`** | GPS Sync Interval ทุก 60 วินาทีขณะเปิดสถานะ Online | **ไม่เกี่ยวกับ feature นี้** | เป็นฟังก์ชันติดตามพิกัดซาเล้งระหว่างวิ่งงาน (`UC-04`) ฝั่งผู้ขายในหน้านี้ไม่มีการซิงก์พิกัดต่อเนื่อง |
| **`CC-03`** | Road Distance API รัศมี <= 5 กม. พร้อม Haversine Fallback | **ไม่เกี่ยวกับ feature นี้** | หน้านี้เป็นการคำนวณราคาของเก่า ไม่มีการคำนวณเส้นทางถนนของซาเล้ง |
| **`CC-04`** | PostgreSQL + Concurrency Control / Optimistic Locking | `T-01`, `T-04` | ใช้ Supabase (PostgreSQL 15+) พร้อมฟิลด์ `version` ในตาราง `waste_pickup_orders` |
| **`CC-05`** | Offline Cache ใน IndexedDB / Local Storage | `T-05`, `T-06` | บันทึกราคากลางลง `localStorage` เพื่อให้ผู้ขายเปิดดูราคาอ้างอิงได้แม้อินเทอร์เน็ตหลุดชั่วคราว |
| **`CC-06`** | PDPA & PII Masking ซ่อนบ้านเลขที่และพิกัดละเอียด | `T-04` | หน้านี้อยู่ในขั้นตอน `S1 -> S2` ผู้ซื้อยังไม่ได้รับงาน จึงไม่มีการเปิดเผยข้อมูลส่วนบุคคลหรือที่อยู่ของผู้ขาย |
| **`REQ-SEC-001`** | บันทึกประวัติการเปลี่ยนสถานะใบงานลงในตาราง Audit Log | `T-04` | บันทึก Audit Log ทุกครั้งที่ใบงานเปลี่ยนจาก `S1 (Draft)` เข้าสู่ `S2 (Pending)` |
| **`REQ-SEC-002`** | แปลงเบอร์โทรศัพท์เป็น `08X-XXX-XXXX` | **ไม่เกี่ยวกับ feature นี้** | หน้านี้ยังไม่ได้แสดงข้อมูลผู้ขายให้ซาเล้งเห็น |
| **`REQ-OP-001`** | โหมด Offline Queue สำหรับดูข้อมูลที่แคชไว้ | `T-05`, `T-06` | รองรับการอ่านตารางราคากลางจากแคชเมื่อไม่มีการเชื่อมต่อเครือข่าย |
| **`REQ-OP-002`** | Haversine Fallback สำหรับการคำนวณระยะทาง | **ไม่เกี่ยวกับ feature นี้** | ไม่มีการเรียกใช้งาน Maps Routing API ในการคำนวณราคาของเก่า |
| **`D-00-01`** | KYC เป็น Precondition ของระบบผู้ซื้อ | **ไม่เกี่ยวกับ feature นี้** | เป็นขอบเขตของฝั่งผู้ซื้อ (`UC-01`) |
| **`D-00-02`** | ซ่อนพิกัดผู้ขายจนกว่าจะรับงาน | `T-04` | ไม่มีการเปิดเผยพิกัดบ้านของผู้ขายใน API ของฟีเจอร์นี้ |
| **`D-00-03`** | ขอบเขตหยุดที่สถานะมีผู้รับงานแล้ว | `T-04`, `T-08` | ดูแลเฉพาะช่วงการร่างคำขอและการส่งคำขอเข้าสถานะ `S2` |
