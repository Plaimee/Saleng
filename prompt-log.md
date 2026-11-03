# บันทึกการใช้คำสั่ง AI (`prompt-log.md`) — โครงการ Saleng (กลุ่ม 2)

เอกสารนี้บันทึกทุกคำสั่งที่ทีมสั่ง AI Coding Agent ตามสายงาน Spec-Driven Development (`/clarify` → `/plan` → `/tasks` → `/implement`) รวมถึงการตรวจสอบย้อนกลับด้วย RTM และการจัดการการเปลี่ยนแปลง (`CR`)

---

## บันทึก #01 — `/clarify specs/002-route/spec.md` (รอบที่ 1: ตรวจความกำกวมก่อนวางแผน)
- **วันที่:** 2026-03-07
- **คำสั่งที่ใช้:** `/clarify specs/002-route/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/002-route/spec.md` (v1.0), `specs/002-route/route.feature`, `specs/002-route/rules.md`, `specs/002-route/models.md`
- **จุดกำกวมที่ AI พบ (ส่วน A & B — 6 คำถาม):**
  1. **`Q-01` (`REQ-FN-002`, `BR-02`):** เกณฑ์ส่วนต่างน้ำหนักรวมเมื่อชั่งจริงที่หน้างาน (Re-weighing) เทียบกับน้ำหนักประเมิน ตอนแรกใน `spec.md` ระบุว่า `"คลาดเคลื่อนมาก"` ต้องให้ผู้ขายกดยืนยันใหม่ ตัวเลขที่ชัดเจนคือกี่เปอร์เซ็นต์ (ถ้าไม่ตอบ AI จะเดาว่า ±20%)
  2. **`Q-02` (`REQ-OP-001`):** เมื่อแอปทำงานในโหมดออฟไลน์ (`Offline Queue`) สามารถเก็บใบงานและรูปถ่ายค้างไว้ในเครื่องได้สูงสุดกี่รายการหรือกี่ชั่วโมงก่อนบังคับเชื่อมต่อ (ถ้าไม่ตอบ AI จะเดาว่าไม่จำกัด)
  3. **`Q-03` (`REQ-FN-003`, `REQ-UX-001`):** เมื่อผู้ใช้สลับจากหน้าแผนที่นำทางไปใช้แอปอื่นแล้วกลับมา ต้องคงสถานะเดิมไว้ภายในเวลากี่นาทีจึงจะไม่รีเซ็ตหน้าจอ
  4. **`Q-04` (`REQ-FN-004`, `BR-01`):** กรณีผู้ขายปฏิเสธใบเสนอราคาใบใหม่หลังชั่งจริง (`S5 -> S8`) ใครเป็นผู้อนุมัติปิดงานหรือคืนสถานะ และมีค่าธรรมเนียมเดินทางหรือไม่
  5. **`Q-05` (`REQ-FN-001`, `REQ-OP-002`):** หากบริการแผนที่ภายนอก (OSRM / Google Maps API) ล่มหรือเกินโควตา ระบบต้องคำนวณระยะทางสำรองอย่างไร
  6. **`Q-06` (`REQ-FN-002`, `REQ-DAT-001`):** รูปถ่ายหน้าตาชั่งบังคับความละเอียดขั้นต่ำและขนาดไฟล์สูงสุดเท่าใดเพื่อไม่ให้เครื่องซาเล้งรุ่นประหยัดค้าง
- **คำตอบของทีม:**
  - **`Q-01` (รู้ เพราะถามตัวแทนลานรับซื้อ `SH-03` และซาเล้ง `SH-01` แล้ว):** กำหนดเกณฑ์ตายตัวที่ **±15%** (`|actual_weight - est_weight| / est_weight > 0.15`) หากไม่เกิน ±15% ระบบคำนวณยอดและออกใบเสร็จได้ทันที (`S4 -> S6`) หากเกิน ±15% ต้องส่งใบเสนอราคาใหม่ให้ผู้ขายยืนยัน (`S4 -> S5`) -> บันทึกเป็น `D-01`
  - **`Q-02` (รู้ เพราะตกลงในทีมปฏิบัติการแล้ว):** เก็บใน SQLite/IndexedDB ได้สูงสุด **50 รายการ หรือภายใน 24 ชั่วโมง** และซิงก์อัตโนมัติแบบ FIFO ทันทีที่มีสัญญาณ (`REQ-OP-001`) -> บันทึกเป็น `D-02`
  - **`Q-03` (รู้):** คงสถานะหน้าจอเดิมไว้สูงสุด **30 นาที** ใน Local Session Storage
  - **`Q-04` (ไม่รู้ ต้องถามเจ้าของโครงการและตัวแทนซาเล้งเพิ่ม):** บันทึกค้างไว้เป็นคำถามเปิด `Q-04` และตั้งสมมติฐาน `AS-01` ว่าในเฟสแรกให้เปลี่ยนสถานะเป็น `S8 (Disputed)` เพื่อให้ Admin ตรวจสอบโดยยังไม่มีการตัดเงินอัตโนมัติ
  - **`Q-05` (รู้):** ใช้สูตร Haversine คำนวณระยะทางเส้นตรงคูณตัวคูณถนน `1.35` เป็น Fallback ทันที และบันทึกแจ้งเตือนลง Audit Log (`D-03`)
  - **`Q-06` (รู้):** บีบอัดภาพฝั่ง Client ให้ไม่เกิน `1 MB` (ความละเอียดขั้นต่ำ `800x600 px`) ก่อนบันทึกลง Offline Queue
- **ไฟล์ที่ถูกแก้ไข:** `specs/002-route/spec.md` (อัปเดตเป็น v2.0), `specs/002-route/rules.md`, `specs/002-route/route.feature`
- **สิ่งที่ป้องกันไม่ให้ AI เดาเอง:** ป้องกัน AI เดาเกณฑ์น้ำหนักเป็น 20% และป้องกันการตัดเงินค่าเดินทางอัตโนมัติใน `Q-04`

---

## บันทึก #02 — `/plan specs/002-route/spec.md` (สร้างแผนทางเทคนิค `plan.md`)
- **วันที่:** 2026-03-07
- **คำสั่งที่ใช้:** `/plan specs/002-route/spec.md`
- **คำถามที่ AI ถามก่อนสร้างแผน (ตามกติกาข้อ 6):**
  - ใน `constraints.md` บังคับเฉพาะรองรับ Offline-first (`CC-01`), ล็อก Audit Log แบบ Append-only (`CC-02`), และ PDPA Location Masking (`CC-03`) แต่ไม่ได้บังคับภาษาหลังบ้านและฐานข้อมูล ทีมต้องการเลือกใช้เทคโนโลยีใด?
- **คำตอบของทีม:**
  - หลังบ้านใช้ **Python 3.11 + FastAPI**, ฐานข้อมูลใช้ **SQLite (พร้อมโหมด WAL สำหรับทดสอบและ Offline Queue จำลอง)**, หน้าบ้านใช้ **HTML5 / React (Vite)** โดยให้ระบุใน `plan.md` ว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"`
- **ไฟล์ที่สร้าง:** `specs/002-route/plan.md` (`P-01..P-07` ครบ 8 ส่วน พร้อมตารางตรวจ Constraints กลาง)

---

## บันทึก #03 — `/tasks specs/002-route/plan.md` (แตกงานย่อย `tasks.md`)
- **วันที่:** 2026-03-07
- **คำสั่งที่ใช้:** `/tasks specs/002-route/plan.md`
- **ผลลัพธ์:** สร้างไฟล์ `specs/002-route/tasks.md` แบ่งเป็น 13 งาน (`T-01` ถึง `T-13`) ครบ 6 ช่องต่อ Task พร้อมตาราง Two-Way Traceability ตรวจครบทั้ง 12 AC (`AC-04-01..12`) และตารางตรวจ Constraints (`CC-01..06`)

---

## บันทึก #04 — `/implement T-01` ถึง `/implement T-11` (สร้างโค้ดและชุดทดสอบรอบแรก)
- **วันที่:** 2026-03-08
- **คำสั่งที่ใช้:** `/implement T-01` .. `/implement T-11` (สั่งทีละ Task และตรวจ 5 ข้อทุกครั้ง)
- **ผลลัพธ์การรันทดสอบรอบที่ 1 (`Round 1`):**
  - รัน `pytest -v -k "AC_"` ได้ผลลัพธ์: **ผ่าน 10 ข้อ, ไม่ผ่าน 2 ข้อ (`test_AC_04_05`, `test_AC_04_09`)**
  - สาเหตุที่พบและบันทึกใน `gaps.md`:
    - `GAP-01` (`test_AC_04_05` — สาเหตุ: `ai`): โค้ดตรวจสอบส่วนต่างน้ำหนักใช้เครื่องหมาย `>= 0.15` แทนที่จะเป็น `> 0.15` ตาม `BR-02` ทำให้กรณีส่วนต่างเท่ากับ 15.0% พอดีถูกส่งไป `S5` แทนที่จะผ่านไป `S6`
    - `GAP-02` (`test_AC_04_09` — สาเหตุ: `ai`): โมดูล `OfflineSyncQueue` ไม่ได้ตรวจเช็ค `idempotency_key` ซ้ำเมื่อส่งข้อมูลชุดเดิมซ้ำหลังเน็ตกลับมา ทำให้เกิดใบเสร็จซ้ำ 2 ใบ

---

## บันทึก #05 — แก้ไข `GAP-01` และ `GAP-02` แล้วรันทดสอบซ้ำ (`Round 2`)
- **วันที่:** 2026-03-08
- **คำสั่งที่ใช้:** `/implement T-05` (แก้เงื่อนไข `> 0.15` ตาม `BR-02`) และ `/implement T-08` (เพิ่มการตรวจ `idempotency_key` ใน `OfflineSyncQueue`) โดย **ไม่แก้ไฟล์ test**
- **ผลลัพธ์การรันทดสอบรอบที่ 2 (`Round 2`):**
  - รัน `pytest -v -k "AC_"` ได้ผลลัพธ์: **`12 passed in 0.42s` (ผ่านครบ 12/12 ข้อ)**
  - บันทึกผลลงใน `specs/002-route/test-run.txt` และ `specs/002-route/ac-results.md`

---

## บันทึก #06 — ร่างตารางตามรอย `rtm.md` และตรวจหาสายที่ขาด
- **วันที่:** 2026-03-14
- **คำสั่งที่ใช้:** สั่ง AI ร่าง `specs/002-route/rtm.md` ตามแม่แบบ `docs/rtm-template.md` แล้วทีมตรวจเองทุกแถว
- **ข้อค้นพบจากการตรวจ RTM (`F-01` ถึง `F-04`):**
  - `F-01`: `REQ-BR-002` (การล็อกราคากลาง ณ เวลาที่ผู้ขายกดยืนยันนัดหมาย `Price Snapshot`) มีโค้ด `snapshot_price_at_booking()` อยู่ในระบบแล้ว แต่ยังไม่มี `AC` และการทดสอบเจาะจงในรอบแรก -> ทีมตัดสินใจออก `CR-02` เพิ่มการตรวจสอบ
  - `F-02`: `REQ-UX-001` (ปุ่มกดขนาดใหญ่ไม่น้อยกว่า `48x48 px` สำหรับซาเล้งใช้งานมือเดียวกลางแจ้ง) มีระบุใน `spec.md` แต่ยังไม่มีการตรวจใน `ui-review.md` -> เพิ่มเข้าใบตรวจหน้าจอ 6 ข้อ
  - `F-03`: `REQ-SEC-002` (การซ่อนบ้านเลขที่จริงและเบอร์โทรผู้ขายก่อนซาเล้งกดรับงาน `S1..S2`) ตรวจพบครบทั้งไปข้างหน้าและย้อนกลับ (`AC-04-11`)
  - `F-04`: ไม่พบโค้ดส่วนเกิน (Orphan Code) ที่ไม่มี `REQ` รองรับ

---

## บันทึก #07 — `/clarify specs/002-route/spec.md` (รอบที่ 2: หลังเพิ่ม `mockups/` และตั้ง Baseline `B1`)
- **วันที่:** 2026-03-14
- **คำสั่งที่ใช้:** `/clarify specs/002-route/spec.md` (ด้วย `agent-pack v2` ที่อ่าน `mockups/` และตรวจสถานะ `baselined`)
- **ผลลัพธ์:**
  - AI ตรวจพบว่า `spec.md` มีสถานะ `baselined (BL-01)` แล้ว จึงไม่แก้ไข `spec.md` โดยตรง
  - AI ตรวจสอบไฟล์ใน `specs/002-route/mockups/` (`UI-04-01`, `UI-04-02`, `UI-04-03`) เทียบกับ `REQ` และช่วยร่าง `changes/CR-03.md` (เพิ่มการแสดงป้ายเตือนส่วนต่างน้ำหนักเกิน ±15% สีส้มบนหน้าจอ `UI-04-03` และแยกกรอบ `.todo` สำหรับ `Q-04` ไม่ให้สร้างปุ่มหักค่าเดินทางในโค้ดจริง)
  - อัปเดต `T-12`, `T-13` และบันทึกผลการตรวจหน้าจอ 6 ข้อใน `specs/002-route/ui-review/ui-review.md`

---

## บันทึก #08 — `/clarify specs/seller/04-pricing-and-decision/spec.md` (ตรวจความกำกวมและความสอดคล้องก่อนวางแผน)
- **วันที่:** 2026-11-01
- **คำสั่งที่ใช้:** `/clarify specs/seller/04-pricing-and-decision/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/seller/04-pricing-and-decision/spec.md`, `specs/000-shared/constraints.md`, `docs/srs/catalogue.md`, `docs/srs/use-cases.md`, `docs/srs/decisions.md`, `specs/seller/02-scrap-posting/spec.md`, `specs/seller/03-buyer-search-and-selection/spec.md`, `specs/seller/07-post-transaction/spec.md`
- **ความไม่สอดคล้องข้ามเอกสารที่พบ (Consistency Checks — 3 ข้อ):**
  1. **`CC-01` (การอ้างอิงรหัส `REQ-ID` ไม่ตรงกับ Catalogue กลาง):** ในสเปกนี้อ้าง `REQ-FN-001` (ตรวจมูลค่าขั้นต่ำ), `REQ-FN-006` (จุดรับรวมหอพัก >= 20 กก.), `REQ-DAT-001` (ตารางราคากลาง), `REQ-UX-001` และ `REQ-QA-001` (บันทึกซาเล้งคนโปรด) ซึ่งเป็นข้อความจากสไลด์ Studio แต่ใน `docs/srs/catalogue.md` กลาง 16 ข้อ รหัสเหล่านี้มีความหมายต่างกัน
  2. **`CC-02` (การอ้างอิงรหัส `UC-ID` ไม่ตรงกับสารบัญ Use Cases ทั้งระบบ):** ในสเปกนี้อ้าง `UC-01`, `UC-03`, `UC-08` จากการ์ดสตูดิโอเดิม แต่ใน `docs/srs/use-cases.md` กลาง ฟังก์ชันนี้อยู่ใน `UC-02` (โพสต์ขายและประเมินราคา) และ `UC-06` (ยืนยัน/ปฏิเสธใบเสนอราคาใหม่)
  3. **`CC-03` (ขอบเขตซ้ำซ้อนและไม่มี AC รองรับเรื่องซาเล้งคนโปรด):** ข้อ 1.4 ระบุเรื่อง "บันทึกซาเล้งคนโปรดไว้นัดซ้ำ" แต่ไม่มี AC ในไฟล์นี้ และหน้าที่นี้ถูกจัดการครบถ้วนแล้วใน `specs/seller/03-buyer-search-and-selection/` (`AC-S03-02`) และ `specs/seller/07-post-transaction/` (`AC-S07-01`)
- **จุดกำกวมที่ AI พบและต้องการคำตอบจากทีม (Open Questions — 6 คำถาม):**
  1. **`Q-01` (`AC-S04-03`, `BR-01`):** เกณฑ์มูลค่าประเมินรวม `>= 500 บาท` ตัดสินจากค่าต่ำสุด (`min_price`), ค่าสูงสุด (`max_price`), หรือค่าเฉลี่ยกึ่งกลางของช่วงราคาประเมิน
  2. **`Q-02` (`AC-S04-03`):** เงื่อนไขขวดแก้ว/พลาสติก `>= 2 กระสอบ` มีอัตราแปลงเป็นกิโลกรัมในการคำนวณราคาประเมินหรือไม่ หรือนับเป็นหน่วยกระสอบแยกต่างหาก
  3. **`Q-03` (`AC-S04-03`, `REQ-FN-001`, `REQ-FN-006`):** เมื่อผู้ขายเลือก "ฝากรวมกับจุดรับทางผ่าน" หรือ "จุดรับรวมประจำอาคาร" ใบงานจะถูกส่งเข้าสถานะใด (`S1 Draft` หรือ `S2 Pending`) และระบบตรวจเกณฑ์สะสม 20 กก. อย่างไร
  4. **`Q-04` (`AC-S04-01`, `REQ-BR-002`):** ช่วงราคากลางที่แสดงในตารางรายวัน มีรอบเวลาอัปเดตตายตัวกี่โมง และการล็อกราคา (Price Snapshot) เกิดขึ้น ณ ขั้นตอนใด
  5. **`Q-05` (Scope Boundary):** ควรตัดข้อ 1.4 ("บันทึกซาเล้งคนโปรด") ออกจากขอบเขตของสเปกนี้เพื่อไม่ให้ซ้ำซ้อนกับฟีเจอร์ที่ 3 และ 7 หรือไม่
  6. **`Q-06` (`AC-S04-02`, `MD-DOM-04`):** กรณีผู้ขายเลือกของเก่าหลายชนิดพร้อมกัน (Multi-item Basket) หน้าจอนี้ต้องสรุปช่วงราคารวมอย่างไร
- **คำตอบของทีม:**
  - **`CC-01` (รู้):** ยึดตาม `spec.md` และ `constraints.md` ที่ระบุในโมเดล และทำเครื่องหมายเชื่อมโยงชัดเจนเพื่อไม่ให้สับสนกับ Catalogue ของ `UC-04`
  - **`CC-02` (รู้):** ระบุหมายเหตุความเชื่อมโยงกับ `UC-02` กลาง เพื่อความเข้าใจตรงกันในการทำ RTM
  - **`CC-03` (รู้):** ตัดข้อ 1.4 ออกจากสเปกนี้ เพื่อไม่ให้ขอบเขตงานซ้ำซ้อนและไม่มี Orphan Requirement
  - **`Q-01` (รู้ — ทางเลือก A):** ใช้ค่าต่ำสุดของช่วงราคาประเมิน (`min_price >= 500 บาท`) ในการตัดสินเกณฑ์นัดหมายเดี่ยว เพื่อความคุ้มค่าของซาเล้ง -> บันทึกเป็น `D-01`
  - **`Q-02` (รู้):** ในหน้าจอมีตัวเลือกให้เลือกหน่วยเป็น "กระสอบ" โดยตรงสำหรับขวดแก้ว/พลาสติก และคำนวณราคาเหมาต่อกระสอบ -> บันทึกเป็น `D-02`
  - **`Q-03` (รู้):** ส่งเข้า `S2 (Pending)` ทันทีโดยมี Flag พิเศษ (`isRouteDropIn = true`) เพื่อให้ซาเล้งที่วิ่งผ่านแวะรับได้ และระบบตรวจสอบเกณฑ์รวม `>= 20 กก.` ในอาคารเดียวกันจากถังขยะ/จุดทิ้งรวมภายในอาคาร -> บันทึกเป็น `D-03`
  - **`Q-04` (รู้):** อัปเดตราคากลางวันละ 1 ครั้งเวลา `06:00 น.` และทำ Price Snapshot ล็อกราคา ณ จังหวะที่ซาเล้งกดรับนัดหมาย (`S2 -> S3`) ตาม `REQ-BR-002` -> บันทึกเป็น `D-04`
  - **`Q-05` (รู้):** ยืนยันตัดหัวข้อ 1.4 "บันทึกซาเล้งคนโปรดไว้นัดซ้ำ" ออกจากสเปกฟีเจอร์นี้ เพื่อไปอยู่ใน `03-buyer-search-and-selection` และ `07-post-transaction` -> บันทึกเป็น `D-05`
  - **`Q-06` (รู้):** การแสดงผลช่วงราคาต้องแสดงแยกแต่ละรายการ และมีแถบสรุปยอดรวม Min-Max ด้านล่าง (Multi-Item Basket) -> บันทึกเป็น `D-06`
- **ไฟล์ที่ถูกแก้ไข:** `specs/seller/04-pricing-and-decision/spec.md` (อัปเดตเป็น v2.0 พร้อม AC-S04-01..05 และบันทึก D-01..D-06)
- **สิ่งที่ป้องกันไม่ให้ AI เดาเอง:** ป้องกัน AI คิดสูตรตัดสินเกณฑ์ 500 บาทเอง, ป้องกันการแปลงหน่วยกระสอบโดยพลการ, ป้องกันการล็อกราคาผิดจังหวะ, และป้องกันการสร้างฟังก์ชันซาเล้งคนโปรดซ้ำซ้อน

---

## บันทึก #09 — `/plan specs/seller/04-pricing-and-decision/spec.md` (สร้างแผนทางเทคนิค `plan.md`)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/04-pricing-and-decision/spec.md`
- **คำถามที่ AI ถามก่อนสร้างแผน (ตามกติกาข้อ 6):**
  - ใน `constraints.md` ไม่ได้ระบุเทคโนโลยีสำหรับ Backend, Database และ Frontend ของฟีเจอร์นี้โดยตรง ทีมต้องการเลือกใช้เทคโนโลยีใด?
- **คำตอบของทีม:**
  - เลือกใช้ **Python 3.11 (FastAPI) + Supabase (PostgreSQL 15+) + React (Vite)** โดยให้ระบุใน `plan.md` ชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"`
- **ไฟล์ที่สร้าง:** `specs/seller/04-pricing-and-decision/plan.md` (`P-01..P-06` ครบ 8 ส่วนหลัก พร้อมตารางตรวจสอบ Constraints กลาง `CC-01..CC-06` และตารางความครอบคลุม Traceability Matrix)

---

## บันทึก #10 — `/tasks specs/seller/04-pricing-and-decision/plan.md` (แตกงานย่อย `tasks.md`)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/04-pricing-and-decision/plan.md`
- **ผลลัพธ์:** สร้างไฟล์ `specs/seller/04-pricing-and-decision/tasks.md` แบ่งเป็น 8 งานย่อย (`T-01` ถึง `T-08`) ครบ 6 ช่องต่อ Task พร้อมตาราง Two-Way Traceability ตรวจครบทั้ง 5 AC (`AC-S04-01..05`) และตารางตรวจ Constraints กลาง (`CC-01..06`, `REQ-SEC`, `REQ-OP`, `D-00`)

---

## บันทึก #11 — `/implement T-01` (ตั้งค่า Config, Supabase Client และสร้าง Data Model)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/core/config.py` (ตั้งค่า Config ค่าคงที่ระบบตาม `D-01`, `D-03`, `D-04`)
  - `backend/app/core/supabase.py` (สร้าง SupabaseStore Adapter พร้อม Seed ราคากลางตั้งต้นตาม `REQ-DAT-001`, `CC-04`)
  - `backend/app/models/pricing_models.py` (สร้าง Pydantic Data Models สำหรับ BenchmarkPrice, WasteItemEstimate, OrderSubmission พร้อม Custom Validator ตาม `BR-01`, `AC-S04-04`, `AC-S04-05`)
  - `backend/tests/test_T01_models_and_config.py` (ชุดทดสอบ Config และ Model Validation)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-01` และไฟล์สนับสนุน (`pytest.ini`, `.gitignore`)
  2. **ผลการรัน Test:** รัน `pytest backend/tests/test_T01_models_and_config.py` ได้ผล: **`4 passed in 0.13s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** โค้ดและ Test มีคอมเมนต์อ้างอิง `REQ-DAT-001`, `REQ-FN-001`, `REQ-FN-006`, `BR-01`, `AC-S04-01..05`, `D-01..D-04` ชัดเจน
  4. **Non-goals & Open Questions:** ไม่มีการสร้างโค้ดส่วนเกินจาก Non-goals และค่าเกณฑ์ต่าง ๆ ถูกแยกเป็น Config ใน `config.py`
  5. **การบันทึกผล:** อัปเดตสถานะ `T-01` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #12 — `/implement T-02` (สร้าง Service และ API ราคากลางประจำวัน พร้อม Scheduled Refresh)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-02`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/services/pricing_service.py` (สร้าง PricingService ดึงและรีเฟรชราคากลางรายวันตาม `REQ-DAT-001`, `AC-S04-01`, `D-04`)
  - `backend/app/cron/daily_price_updater.py` (สร้าง Scheduled Worker อัปเดตราคากลางประจำวัน 06:00 น. พร้อมบันทึก Audit Log ตาม `REQ-SEC-001`, `D-04`)
  - `backend/app/api/v1/pricing.py` (เปิด Endpoint `GET /api/v1/pricing/benchmark-prices`)
  - `backend/app/core/supabase.py` (ปรับปรุง `upsert_benchmark_price` ให้รักษา timestamp อัปเดตที่ระบุ)
  - `backend/tests/test_AC_S04_01_benchmark_price.py` (ชุดทดสอบอัตโนมัติสำหรับ `AC-S04-01`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-02` และไฟล์แพ็กเกจ `__init__.py` ที่เกี่ยวข้อง
  2. **ผลการรัน Test:** รัน `pytest backend/tests/` ได้ผล: **`6 passed in 0.11s`** (ผ่าน 100% ครอบคลุมทั้ง `T-01` 4 passed และ `T-02` 2 passed)
  3. **การอ้างอิง ID:** โค้ดและ Test อ้างอิง `REQ-DAT-001`, `AC-S04-01`, `P-04`, `D-04` และตั้งชื่อฟังก์ชันทดสอบตามรหัส AC
  4. **Non-goals & Open Questions:** ไม่มีฟีเจอร์นอกขอบเขต ราคากลางอัปเดตเวลา 06:00 น. ตามคอนฟิก
  5. **การบันทึกผล:** อัปเดตสถานะ `T-02` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #13 — `/implement T-03` (สร้าง Service และ API คำนวณช่วงราคาประเมินและ Multi-Item Basket)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-03`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/pricing_models.py` (เพิ่ม `CalculationEstimateRequest` สำหรับรับรายการของเก่าในตะกร้า)
  - `backend/app/services/pricing_service.py` (พัฒนาฟังก์ชัน `calculate_estimate()` คำนวณช่วงราคาประเมิน Min-Max, รวมยอด Multi-Item Basket, รองรับหน่วยกระสอบตาม `Card 01`, `BR-01`, `AC-S04-02`, `AC-S04-05`, `D-02`, `D-06`)
  - `backend/app/api/v1/pricing.py` (เปิด Endpoint `POST /api/v1/pricing/calculate-estimate`)
  - `backend/tests/test_AC_S04_02_instant_calculation.py` (ชุดทดสอบคำนวณราคาประเมินทันที <= 3 วินาที และ Multi-Item Basket สำหรับ `AC-S04-02`)
  - `backend/tests/test_AC_S04_04_invalid_quantity.py` (ชุดทดสอบบล็อกปริมาณ <= 0 แจ้งเตือน 'กรุณากรอกปริมาณมากกว่า 0' สำหรับ `AC-S04-04`)
  - `backend/tests/test_AC_S04_05_bag_unit_pricing.py` (ชุดทดสอบราคาเหมาต่อกระสอบสำหรับขวดแก้วและขวดพลาสติก สำหรับ `AC-S04-05`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-03`
  2. **ผลการรัน Test:** รัน `pytest backend/tests/` ได้ผล: **`14 passed in 0.14s`** (ผ่าน 100% ครอบคลุมทั้ง `T-01` 4 passed, `T-02` 2 passed, และ `T-03` 8 passed)
  3. **การอ้างอิง ID:** โค้ดและ Test มีคอมเมนต์อ้างอิง `Card 01`, `BR-01`, `AC-S04-02`, `AC-S04-04`, `AC-S04-05`, `P-01`, `P-02`, `P-06`, `D-02`, `D-06` ครบถ้วน
  4. **Non-goals & Open Questions:** ตรวจสอบข้อความกำกับ 'ราคาจริงขึ้นกับสภาพของหน้างาน' ตามกฎ `BR-01` ครบถ้วน
  5. **การบันทึกผล:** อัปเดตสถานะ `T-03` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #14 — `/implement T-04` (สร้าง Service ตรวจสอบเกณฑ์ขั้นต่ำ 500 บาท และ API ส่งคำขอนัดหมาย)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-04`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/services/order_submission_service.py` (สร้าง OrderSubmissionService พร้อม Guard ตรวจสอบ `min_price >= 500.0` หรือขวด `>= 2 กระสอบ`, บล็อกคำขอเดี่ยวหากไม่ถึงเกณฑ์, รองรับทางเลือกฝากรวมทางผ่าน `isRouteDropIn` และจุดรับรวมอาคาร `isBuildingGroupDrop`, บันทึก Audit Log และเปลี่ยนสถานะเป็น `S2 Pending` ตาม `REQ-FN-001`, `REQ-FN-006`, `REQ-SEC-001`, `AC-S04-03`, `D-01`, `D-03`)
  - `backend/app/api/v1/pricing.py` (เปิด Endpoint `POST /api/v1/orders/validate-and-submit`)
  - `backend/tests/test_AC_S04_03_minimum_threshold.py` (ชุดทดสอบอัตโนมัติสำหรับ `AC-S04-03` ครอบคลุม Pass Case, Blocked Case, และทางเลือกทั้ง 2 รูปแบบ)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-04`
  2. **ผลการรัน Test:** รัน `pytest backend/tests/` ได้ผล: **`19 passed in 0.15s`** (ผ่าน 100% ครอบคลุมทั้ง `T-01` 4 passed, `T-02` 2 passed, `T-03` 8 passed, และ `T-04` 5 passed)
  3. **การอ้างอิง ID:** โค้ดและ Test มีการอ้างอิง `REQ-FN-001`, `REQ-FN-006`, `REQ-SEC-001`, `AC-S04-03`, `P-03`, `P-05`, `D-01`, `D-03` ครบถ้วน
  4. **Non-goals & Open Questions:** สถานะถูกตั้งเป็น `S2` รอผู้รับซื้อตอบรับ ไม่มีโค้ดส่วนเกินจาก Non-goals
  5. **การบันทึกผล:** อัปเดตสถานะ `T-04` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #15 — `/implement T-05` (สร้าง Frontend API Client และโมดูล Local Cache)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-05`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `frontend/src/services/pricingApi.js` (สร้างโมดูลเรียก API `fetchBenchmarkPrices`, `calculateEstimate`, `submitOrder` พร้อมระบบ Local Storage Cache สำรองข้อมูลราคากลางเมื่อออฟไลน์ตาม `CC-01`, `CC-05`, `REQ-OP-001`, `AC-S04-01..05`)
  - `frontend/tests/pricingApi.test.mjs` (ชุดทดสอบอัตโนมัติ Unit Test สำหรับ `pricingApi.js`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-05`
  2. **ผลการรัน Test:**
     - รัน `node --test frontend/tests/pricingApi.test.mjs` ได้ผล: **`5 passed in 33ms`** (ผ่าน 100%)
     - รัน Regression Check ฝั่งหลังบ้าน `pytest backend/tests/` ได้ผล: **`19 passed in 0.14s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `CC-01`, `CC-05`, `REQ-OP-001`, `AC-S04-01..05`, `D-01..D-06` ครบถ้วน
  4. **Non-goals & Open Questions:** รองรับการทำงานแบบ Offline Cache โดยไม่มีโค้ดส่วนเกิน
  5. **การบันทึกผล:** อัปเดตสถานะ `T-05` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #16 — `/implement T-06` (พัฒนาหน้าจอและคอมโพเนนต์ React Mobile-First SPA)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-06`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `frontend/src/components/BenchmarkPriceTable.jsx` (คอมโพเนนต์ตารางราคากลางพร้อมป้ายอัปเดต 06:00 น. และป้ายออฟไลน์ตาม `REQ-DAT-001`, `AC-S04-01`, `CC-05`, `D-04`)
  - `frontend/src/components/ItemPriceCalculator.jsx` (ฟอร์มเลือกของเก่า สลับหน่วย กก./กระสอบ และตรวจสอบปริมาณ > 0 ตาม `Card 01`, `AC-S04-02`, `AC-S04-04`, `AC-S04-05`, `D-02`)
  - `frontend/src/components/MultiItemBasketSummary.jsx` (สรุปรายการในตะกร้าและช่วงราคารวม Min-Max พร้อมป้ายกำกับตาม `BR-01`, `AC-S04-02`, `D-06`)
  - `frontend/src/components/ThresholdGuardModal.jsx` (ป๊อปอัปบล็อกเมื่อ < 500 บาท พร้อมปุ่มทางเลือกฝากรวมทางผ่านและจุดรับรวมอาคารตาม `REQ-FN-001`, `REQ-FN-006`, `AC-S04-03`, `D-01`, `D-03`)
  - `frontend/src/pages/PricingDecisionPage.jsx` (หน้าจอหลักแบบ Mobile-First SPA รองรับขนาดจอมือถือตาม `CC-01`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-06` และไฟล์คอนฟิกแพ็กเกจ `frontend/package.json`
  2. **ผลการรัน Test:**
     - รัน `node --test frontend/tests/pricingApi.test.mjs` ได้ผล: **`5 passed`**
     - รัน Regression Check ฝั่งหลังบ้าน `pytest backend/tests/` ได้ผล: **`19 passed in 0.13s`** (ผ่าน 100% รวม 24 ข้อ)
  3. **การอ้างอิง ID:** คอมโพเนนต์ทุกชิ้นมี `data-req="REQ-..."` กำกับตรงตามที่ระบุในสเปก
  4. **Non-goals & Open Questions:** ไม่มีฟังก์ชันซาเล้งคนโปรดในหน้านี้ตามขอบเขตที่ตัดออก
  5. **การบันทึกผล:** อัปเดตสถานะ `T-06` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #17 — `/implement T-07` (สร้างชุดทดสอบหน้าจอ Component & Integration Tests)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-07`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `frontend/tests/AC-S04-01.test.jsx` (ทดสอบการแสดงผลตารางช่วงราคากลาง และป้ายเวลาอัปเดต 06:00 น. ตาม `AC-S04-01`)
  - `frontend/tests/AC-S04-02.test.jsx` (ทดสอบการคำนวณราคาของเก่าทันทีแบบ Multi-Item Basket และป้ายกำกับตาม `AC-S04-02`, `BR-01`)
  - `frontend/tests/AC-S04-03.test.jsx` (ทดสอบ Threshold Guard Modal ป๊อปอัปบล็อกเมื่อ < 500 บาท และปุ่มทางเลือกฝากรวมทางผ่าน/อาคารตาม `AC-S04-03`)
  - `frontend/tests/AC-S04-04.test.jsx` (ทดสอบการบล็อกการคำนวณและแจ้งเตือนเมื่อกรอกปริมาณ <= 0 ตาม `AC-S04-04`)
  - `frontend/tests/AC-S04-05.test.jsx` (ทดสอบการเลือกหน่วยนับเป็นกระสอบสำหรับขวดแก้ว/พลาสติก และคำนวณราคาเหมาต่อกระสอบตาม `AC-S04-05`, `D-02`)
  - `frontend/tests/pricingApi.test.mjs` (ปรับปรุงให้อยู่ในชุด Vitest)
  - `frontend/vitest.config.js` (คอนฟิก JSDOM สภาพแวดล้อมทดสอบสำหรับ React Testing Library)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ทดสอบและคอนฟิกทดสอบที่กำหนดใน `T-07`
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`6 test files passed, 15 passed in 0.59s`** (ผ่าน 100%)
     - รัน Regression Check ฝั่งหลังบ้าน `.venv/bin/pytest backend/tests/`: **`19 passed in 0.14s`** (ผ่าน 100%)
     - ยอดรวมชุดทดสอบทั้งหมดที่ผ่าน: **34 ผ่าน / 0 ตก**
  3. **การอ้างอิง ID:** ไฟล์ทดสอบตั้งชื่อและอ้างอิงรหัส `AC-S04-01` ถึง `AC-S04-05`, `REQ-DAT-001`, `REQ-FN-001`, `REQ-FN-006`, `BR-01`, `D-01..D-06` ครบถ้วน
  4. **Non-goals & Open Questions:** ชุดทดสอบทดสอบเฉพาะตามเกณฑ์การยอมรับในสเปก ไม่มีเคสนอกเหนือขอบเขต
  5. **การบันทึกผล:** อัปเดตสถานะ `T-07` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #18 — `/implement T-08` (ทดสอบแบบครบวงจร End-to-End และวัดเกณฑ์ประสิทธิภาพ)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/services/order_submission_service.py` (เพิ่มเมธอด `accept_order_and_lock_price` สำหรับช่วงเปลี่ยนผ่านสถานะ `S2 -> S3` พร้อมบันทึก Price Snapshot ลงใน `locked_unit_price` และ Audit Log ตาม `REQ-BR-002`, `D-04`, `REQ-SEC-001`)
  - `backend/app/api/v1/pricing.py` (เพิ่ม Endpoint `POST /api/v1/orders/{order_id}/accept` จำลองการรับงานของผู้ซื้อ)
  - `backend/tests/test_e2e_pricing_decision.py` (ชุดทดสอบ End-to-End Lifecycle ครอบคลุมการเปิดดูราคากลางรายวัน -> คำนวณช่วงราคาตะกร้า -> Threshold Guard บล็อกเมื่อ < 500 บาท -> ส่งทางเลือกฝากรวมทางผ่านเข้า `S2` -> ผู้ซื้อกดรับงานเข้า `S3` และล็อก Price Snapshot ถาวร พร้อมทดสอบประสิทธิภาพ Latency Benchmark P95 <= 3.0s ตาม `REQ-QA-001`, `AC-S04-02`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-08`
  2. **ผลการรัน Test:**
     - รัน `pytest backend/tests/test_e2e_pricing_decision.py`: **`2 passed in 0.14s`** (ผ่าน 100%)
     - รัน Full Backend Suite `pytest backend/tests/`: **`21 passed in 0.17s`** (ผ่าน 100%)
     - รัน Full Frontend Suite `npm test --prefix frontend`: **`6 files passed, 15 passed in 0.56s`** (ผ่าน 100%)
     - **ยอดรวมการทดสอบทั้งหมดของฟีเจอร์นี้: 36 ข้อ ผ่าน 100% (Backend 21, Frontend 15)**
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `REQ-QA-001`, `REQ-BR-002`, `REQ-FN-001`, `REQ-FN-006`, `REQ-SEC-001`, `AC-S04-01..05`, `D-01..D-06` ครบถ้วน
  4. **Non-goals & Open Questions:** ตรวจสอบ Price Snapshot คงเดิมแม้ราคากลางวันถัดไปจะเปลี่ยนแปลง ไม่มีฟังก์ชันนอกขอบเขต
  5. **การบันทึกผล:** อัปเดตสถานะ `T-08` เป็น `[DONE]` และสถานะของ `tasks.md` เป็น `completed` พร้อมบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #19 — `/clarify specs/seller/06-payment-and-verification` (ระบบชำระเงินและตรวจสอบ)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/clarify specs/seller/06-payment-and-verification`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/06-payment-and-verification/spec.md` (ปรับปรุงขึ้นเป็น Version 2.0 หลังเคลียร์จุดกำกวม CC-01..03 และคำถาม Q-01..05 ครบถ้วน)
- **ประเด็นที่เคลียร์และข้อตกลงของทีม:**
  1. **`CC-01`**: เชื่อมโยงรหัส Requirement ตาม Catalogue กลาง: ใช้ `REQ-FN-004` (ตรวจสอบและยืนยันน้ำหนักชั่งจริง บล็อก 100% หากยังไม่กดยืนยัน) และ `REQ-FN-005` (สร้างใบเสร็จดิจิทัลเมื่อจบงาน)
  2. **`CC-02`**: ปรับรหัส Use Case ให้ตรงกับสารบัญกลาง: `UC-06` (ยืนยันผลชั่ง/ราคา) และ `UC-07` (ชำระเงินและออกใบเสร็จดิจิทัล)
  3. **`CC-03`**: ผังสถานะยึดตาม `MD-STM-04`: `S4 (Weighing)` -> `S5 (Re-Quote / Weight Confirmed)` -> `S6 (Settled / Pending Payment)` -> `S7 (Completed)` และทางเลือกข้อพิพาท `S8 (Disputed)`
  4. **`Q-01` (ทางเลือก A)**: บังคับผู้ขายกดยืนยันตัวเลขน้ำหนักบนหน้าจอของตนเอง 100% ทุกครั้ง (Gate ก่อนเข้า `S6`) เพื่อความโปร่งใสและเป็นหลักฐาน
  5. **`Q-02` (ทางเลือก A)**: กรณีผลชั่งไม่ถูกต้อง มีปุ่ม "ขอให้ชั่งซ้ำ" และปุ่ม "ปฏิเสธผลชั่ง / แจ้งข้อพิพาท" (เปลี่ยนสถานะเป็น `S8: Disputed` ตาม `REQ-FN-006` พร้อมล็อกภาพตาชั่งส่งแอดมิน)
  6. **`Q-03` (ทางเลือก A)**: ผู้ขายเป็นผู้กดยืนยันรับเงิน (เงินสดหรือ PromptPay) บนหน้าจอของตนเอง คำขอจึงจะเปลี่ยนเป็น `S7: Completed` และออกใบเสร็จดิจิทัล
  7. **`Q-04` (ทางเลือก A)**: โครงสร้างใบเสร็จดิจิทัล (`DigitalReceipt`) ครบถ้วน: รหัสใบเสร็จ, วันที่เวลา, ข้อมูลผู้ขายและซาเล้งพร้อม PII Masking (`REQ-SEC-002`), รายการของเก่า น้ำหนักจริง ราคาที่ล็อกไว้ (`REQ-BR-002`), ยอดสุทธิ, วิธีชำระเงิน, ปุ่มบันทึกภาพ/ดาวน์โหลด
  8. **`Q-05`**: ยืนยันขอบเขต ไม่ทำ In-App Wallet หรือ Payment Gateway ตัดบัตรเครดิต (ใช้เงินสด/PromptPay ภายนอก) และระบบรีวิวตัดไปอยู่ใน `seller/07`
- **สถานะ:** สเปก `seller/06` ได้รับการรับรองและพร้อมสำหรับขั้นตอน `/plan`


---

## บันทึก #20 — `/plan specs/seller/06-payment-and-verification/spec.md` (แผนสถาปัตยกรรมและเทคโนโลยี)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/06-payment-and-verification/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/06-payment-and-verification/plan.md` (จัดทำแผนสถาปัตยกรรมระบบ 8 หัวข้อหลัก ครอบคลุม P-01 ถึง P-06, Tech Stack "ทีมเลือกเอง ไม่ได้มาจาก spec", Data Model, Endpoints, UI Plan, และตารางตรวจ Constraints 13 ข้อ)
- **ประเด็นสำคัญในแผน:**
  1. **Tech Stack:** Python 3.11 (FastAPI) + Supabase (PostgreSQL 15+) + React 18 (Vite + TailwindCSS) (`"ทีมเลือกเอง ไม่ได้มาจาก spec"`)
  2. **สถาปัตยกรรม 6 การตัดสินใจ (`P-01` ถึง `P-06`):**
     - `P-01`: WeightConfirmationService และ 100% Confirmation Gate (`REQ-FN-004`, `AC-S06-01`)
     - `P-02`: Dispute & Re-Weigh Service รองรับปุ่มขอชั่งซ้ำ และแจ้งข้อพิพาทเข้า `S8: Disputed` (`REQ-FN-006`, `AC-S06-02`)
     - `P-03`: SettlementCalculationService คำนวณยอดเงินสุทธิจาก `actual_quantity * locked_unit_price` (`REQ-BR-002`, `AC-S06-03`)
     - `P-04`: Payment Confirmation Flow รองรับเงินสด/PromptPay โดยผู้ขายเป็นผู้กดยืนยันรับเงินก่อนเข้า `S7` (`UC-07`, `AC-S06-03`)
     - `P-05`: ReceiptGenerationService สร้างใบเสร็จดิจิทัล พร้อม PII Masking `08X-XXX-XXXX` (`REQ-FN-005`, `REQ-SEC-002`, `AC-S06-04`)
     - `P-06`: State Machine & Audit Logging ควบคุมสถานะ `S4 -> S5 -> S6 -> S7` (`REQ-SEC-001`, `AC-S06-05`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` พร้อมระบุเหตุผลข้อที่ไม่เกี่ยวข้อง
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #21 — `/tasks specs/seller/06-payment-and-verification/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/06-payment-and-verification/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/06-payment-and-verification/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S06-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: ขยาย Data Models, Schema, และ In-memory Supabase store สำหรับค่าน้ำหนักชั่งจริง ยอดสุทธิ และใบเสร็จ
     - `T-02`: สร้าง Service บันทึกผลชั่งจริงและคำนวณยอดเงินสุทธิหน้างาน (`actual_quantity * locked_unit_price`)
     - `T-03`: สร้าง Service ตรวจสอบและบังคับ Seller Confirmation Gate 100% (`AC-S06-01`, `REQ-FN-004`)
     - `T-04`: สร้าง Service รองรับการขอชั่งซ้ำ และแจ้งข้อพิพาทเข้าสถานะ `S8: Disputed` (`AC-S06-02`, `REQ-FN-006`)
     - `T-05`: สร้าง Service ยืนยันการรับเงิน (เงินสด/PromptPay) และออกใบเสร็จดิจิทัล พร้อม PII Masking (`AC-S06-03`, `AC-S06-04`)
     - `T-06`: สร้าง Frontend API Client (`paymentApi.js`) และระบบแคชใบเสร็จออฟไลน์ (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React Mobile-First SPA (`WeightVerificationCard`, `PaymentConfirmationCard`, `DigitalReceiptCard`, `PaymentVerificationPage`)
     - `T-08`: สร้างชุดทดสอบ Vitest Component Tests (`AC-S06-01..04`) และ E2E Integration Test (`AC-S06-05`)
  2. **Traceability:** ทุก `AC`, `REQ`, `BR` และ `CC` เชื่อมโยงกลับไปยังงานและไฟล์ทดสอบชัดเจน 100%
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมเริ่มขั้นตอนการพัฒนาจริง `/implement T-01`


---

## บันทึก #22 — `/implement T-01` (ขยาย Data Models และ Schema สำหรับระบบชำระเงินและตรวจสอบ)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/payment_models.py` (สร้าง Pydantic Models: ActualWeightItemInput, RecordWeighingRequest, WeighingRecordResponse, WeightConfirmationRequest, WeightConfirmationResponse, DisputeRequest, DisputeResponse, PaymentConfirmationRequest, DigitalReceiptResponse, DigitalReceiptItem)
  - `backend/app/core/supabase.py` (เพิ่มโครงสร้างเก็บ `receipts`, เมธอด `update_order`, `update_item`, `create_digital_receipt`, `get_receipt`, `get_receipt_by_order`)
  - `backend/tests/test_T01_payment_models.py` (ชุดทดสอบอัตโนมัติ Unit Test 4 เคส ตรวจสอบ Validation และฟังก์ชันใน Store)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-01`
  2. **ผลการรัน Test:**
     - รัน `pytest backend/tests/test_T01_payment_models.py`: **`4 passed in 0.05s`** (ผ่าน 100%)
     - รัน Full Backend Regression `pytest backend/tests/`: **`25 passed in 0.20s`** (ผ่าน 100% รวมของเดิม 21 + ใหม่ 4)
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `MD-DOM-04`, `REQ-FN-004`, `REQ-FN-005`, `REQ-FN-006`, `REQ-BR-002`, `REQ-SEC-002`, `CC-04`, `P-03`, `P-05` ครบถ้วน
  4. **Non-goals & Open Questions:** รองรับเฉพาะ CASH และ PROMPTPAY ตามมติ ไม่ทำ Payment Gateway
  5. **การบันทึกผล:** อัปเดตสถานะ `T-01` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #23 — `/implement T-02` (สร้าง Service บันทึกผลชั่งจริงและคำนวณยอดเงินสุทธิหน้างาน)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-02`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/services/payment_service.py` (สร้างเมธอด `record_weighing` คำนวณยอดเงินสุทธิจาก actual_quantity * locked_unit_price พร้อมบันทึกภาพตาชั่งและอัปเดตสถานะเป็น S5)
  - `backend/app/api/v1/payment.py` (เปิด Endpoint `POST /api/v1/orders/{order_id}/record-weighing`)
  - `backend/app/api/v1/pricing.py` (เชื่อมต่อ `payment_router` เข้ากับ FastAPI app)
  - `backend/tests/test_weighing_and_settlement.py` (ชุดทดสอบอัตโนมัติ 3 เคส: ตรวจสอบการคำนวณยอดเงินสุทธิหลายรายการ, ตรวจสอบสถานะใบงานไม่ถูกต้อง, ตรวจสอบ item_id ไม่พบ)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-02` และไฟล์เชื่อมเราเตอร์
  2. **ผลการรัน Test:**
     - รัน `pytest backend/tests/test_weighing_and_settlement.py`: **`3 passed in 0.13s`** (ผ่าน 100%)
     - รัน Full Backend Regression `pytest backend/tests/`: **`28 passed in 0.18s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `REQ-BR-002`, `REQ-FN-004`, `REQ-SEC-001`, `P-03`, `D-04` ครบถ้วน
  4. **Non-goals & Open Questions:** คำนวณยอดเงินสุทธิจากราคาที่ล็อกไว้จริง ณ วันนัดหมาย ไม่มีการเปลี่ยนราคาตามวันถัดไป
  5. **การบันทึกผล:** อัปเดตสถานะ `T-02` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #24 — `/implement T-03` (สร้าง Service ตรวจสอบและบังคับ Seller Confirmation Gate 100%)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-03`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/services/payment_service.py` (สร้างเมธอด `confirm_weights` ตรวจสอบสิทธิ์ผู้ขาย seller_id, บล็อก 100% หากผู้ขายยังไม่กดยืนยัน, เปลี่ยนสถานะเป็น S6 และบันทึก Audit Log)
  - `backend/app/api/v1/payment.py` (เปิด Endpoint `POST /api/v1/orders/{order_id}/confirm-weights`)
  - `backend/tests/test_AC_S06_01_weight_confirmation.py` (ชุดทดสอบอัตโนมัติ 4 เคส: ยืนยันน้ำหนักสำเร็จเปลี่ยนเป็น S6, บล็อกผู้ใช้คนอื่น HTTP 403, บล็อกคำขอที่ยังไม่อยู่ใน S5, และทดสอบ 100% Confirmation Gate)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-03`
  2. **ผลการรัน Test:**
     - รัน `pytest backend/tests/test_AC_S06_01_weight_confirmation.py`: **`4 passed in 0.12s`** (ผ่าน 100%)
     - รัน Full Backend Regression `pytest backend/tests/`: **`32 passed in 0.19s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `REQ-FN-004`, `REQ-SEC-001`, `AC-S06-01`, `P-01`, `Q-01` ครบถ้วน
  4. **Non-goals & Open Questions:** บังคับให้ผู้ขายเป็นผู้กดยืนยันตัวเลขน้ำหนัก 100% ตามมติ เพื่อความโปร่งใสและหลักฐานก่อนชำระเงิน
  5. **การบันทึกผล:** อัปเดตสถานะ `T-03` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #25 — `/implement T-04` (สร้าง Service รองรับการขอชั่งซ้ำ และแจ้งข้อพิพาทผลชั่ง)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-04`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/payment_models.py` (เพิ่ม Model `RequestReweighResponse`)
  - `backend/app/services/payment_service.py` (สร้างเมธอด `request_reweigh` คืนสถานะกลับสู่ S4 เพื่อชั่งใหม่ และ `raise_dispute` เปลี่ยนสถานะเป็น S8 พร้อมล็อกหลักฐานภาพตาชั่งและราคาตาม REQ-FN-006)
  - `backend/app/api/v1/payment.py` (เปิด Endpoints `POST /api/v1/orders/{order_id}/request-reweigh` และ `POST /api/v1/orders/{order_id}/dispute`)
  - `backend/tests/test_AC_S06_02_dispute_and_reweigh.py` (ชุดทดสอบอัตโนมัติ 4 เคส: ขอชั่งซ้ำสำเร็จ, แจ้งข้อพิพาท S8 สำเร็จพร้อมล็อกหลักฐาน, บล็อกผู้ใช้คนอื่น HTTP 403, บล็อกสถานะไม่ถูกต้อง HTTP 400)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-04`
  2. **ผลการรัน Test:**
     - รัน `pytest backend/tests/test_AC_S06_02_dispute_and_reweigh.py`: **`4 passed in 0.13s`** (ผ่าน 100%)
     - รัน Full Backend Regression `pytest backend/tests/`: **`36 passed in 0.19s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `REQ-FN-006`, `REQ-SEC-001`, `AC-S06-02`, `P-02`, `Q-02` ครบถ้วน
  4. **Non-goals & Open Questions:** ล็อกหลักฐานภาพตาชั่ง `is_frozen = True` สำหรับส่งให้แอดมินตาม REQ-FN-006 ไม่มีโค้ดส่วนเกิน
  5. **การบันทึกผล:** อัปเดตสถานะ `T-04` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #26 — `/implement T-05` (ยืนยันการรับเงินและออกใบเสร็จดิจิทัล พร้อม PII Masking)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-05`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/services/payment_service.py` (เพิ่ม `mask_phone`, `_generate_receipt_no`, `confirm_payment` (S6 -> S7 + สร้างใบเสร็จ + Audit Log), `get_receipt`)
  - `backend/app/api/v1/payment.py` (เพิ่ม `POST /api/v1/orders/{order_id}/confirm-payment` และ `receipt_router` สำหรับ `GET /api/v1/receipts/{order_id}`)
  - `backend/app/api/v1/pricing.py` (ลงทะเบียน `receipt_router`)
  - `backend/tests/test_AC_S06_03_payment_and_receipt.py` (10 เคส: ยืนยันรับเงิน CASH/PROMPTPAY, บล็อกผู้ที่ไม่ใช่ผู้ขาย 403, บล็อกสถานะ S5/S8, บล็อกยืนยันซ้ำ, เนื้อหาใบเสร็จ+Masking, รหัสใบเสร็จไม่ซ้ำ, 404 เมื่อยังไม่มีใบเสร็จ, ฟังก์ชัน mask_phone)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ใน `T-05` และไฟล์ลงทะเบียนเราเตอร์ `pricing.py`
  2. **ผลการรัน Test:** `pytest backend/tests/` ได้ **`46 passed in 0.22s`** (ใหม่ 10 ข้อ ผ่าน 100%)
  3. **การอ้างอิง ID:** `UC-07`, `REQ-FN-005`, `REQ-SEC-001`, `REQ-SEC-002`, `AC-S06-03`, `AC-S06-04`, `P-04`, `P-05`, `Q-03`, `Q-04`
  4. **Non-goals & Open Questions:** รองรับเฉพาะ CASH/PROMPTPAY ไม่มี Payment Gateway/Wallet (`Q-05`) — ไม่ได้สร้าง PromptPay QR Payload ในงานนี้ (อยู่ในส่วน UI `T-07`)
  5. **การบันทึกผล:** อัปเดต `T-05` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` แล้ว
- **ข้อสังเกตที่ต้องให้ทีมยืนยัน (ยังไม่สร้าง ID ใหม่ตาม Rule 5):**
  - ยังไม่มีตาราง/ที่มาของเบอร์โทรผู้ใช้ในสเปก ระบบจึงอ่านจากฟิลด์ `seller_phone` / `buyer_phone` ของใบงาน หากไม่มีข้อมูลจะแสดง `XXX-XXX-XXXX` (ปกปิดทั้งหมด ไม่เดาค่า)
  - รูปแบบ Masking ใช้ตามตัวอย่างใน `Q-04` คือคง 2 หลักแรกและ 4 หลักท้าย (`08X-XXX-1234`)


---

## บันทึก #27 — `/implement T-06` (สร้าง Frontend API Client และระบบแคชใบเสร็จดิจิทัลออฟไลน์)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-06`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `frontend/src/services/paymentApi.js` (สร้างโมดูลเรียก API: recordWeighing, confirmWeights, requestReweigh, raiseDispute, confirmPayment, fetchReceipt พร้อมระบบ Local Storage Cache สำหรับใบเสร็จดิจิทัล CC-05, REQ-OP-001)
  - `frontend/tests/paymentApi.test.mjs` (ชุดทดสอบอัตโนมัติ Vitest 9 เคส: ครอบคลุมทุก API endpoint, Error handling, และการเปิดดูใบเสร็จโหมดออฟไลน์)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-06`
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`7 files passed, 24 passed in 0.73s`** (ผ่าน 100% รวม paymentApi.test.mjs 9 passed)
     - รัน Full Backend Regression `pytest backend/tests/`: **`46 passed in 0.23s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** โค้ดและฟังก์ชันทดสอบอ้างอิง `CC-01`, `CC-05`, `REQ-OP-001`, `AC-S06-01..05` ครบถ้วน
  4. **Non-goals & Open Questions:** รองรับแคชแบบ Offline Read สำหรับใบเสร็จดิจิทัลที่เคยเปิดแล้ว ไม่มีโค้ดส่วนเกิน
  5. **การบันทึกผล:** อัปเดตสถานะ `T-06` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #28 — `/implement T-07` (พัฒนาคอมโพเนนต์และหน้าจอ React Mobile-First SPA)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-07`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `frontend/src/components/WeightVerificationCard.jsx` (คอมโพเนนต์แสดงผลชั่งจริง, รูปตาชั่งดิจิทัล REQ-FN-002, ปุ่มยืนยันน้ำหนัก REQ-FN-004, ปุ่มขอชั่งซ้ำและปุ่มแจ้งข้อพิพาท REQ-FN-006)
  - `frontend/src/components/PaymentConfirmationCard.jsx` (คอมโพเนนต์เลือกวิธีรับเงิน เงินสด/PromptPay QR พร้อมปุ่มยืนยันรับเงิน UC-07, Q-03)
  - `frontend/src/components/DigitalReceiptCard.jsx` (คอมโพเนนต์ใบเสร็จดิจิทัล REQ-FN-005 พร้อม PII Masking เบอร์โทร 08X-XXX-XXXX REQ-SEC-002, ป้ายออฟไลน์ CC-05)
  - `frontend/src/pages/PaymentVerificationPage.jsx` (หน้าจอหลักเชื่อมโยงโฟลว์การทำงาน S5 -> S6 -> S7 หรือ S8 ควบคุมผ่าน State Machine)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-07`
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`7 files passed, 24 passed in 0.58s`** (ผ่าน 100%)
     - รัน Full Backend Regression `pytest backend/tests/`: **`46 passed in 0.21s`** (ผ่าน 100%)
  3. **การอ้างอิง ID:** คอมโพเนนต์ทุกชิ้นมี `data-req="REQ-..."` กำกับตรงตามสเปกและ Mockup
  4. **Non-goals & Open Questions:** ไม่มีฟังก์ชัน Wallet หรือการชำระเงินตัดบัตรนอกขอบเขต
  5. **การบันทึกผล:** อัปเดตสถานะ `T-07` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #29 — `/implement T-08` (สร้างชุดทดสอบหน้าจอ Component Tests และ Integration E2E Test)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `frontend/tests/AC-S06-01.test.jsx` (Vitest UI Component Test: ตรวจสอบ 100% Weight Confirmation Gate ตาม `REQ-FN-004`, `AC-S06-01`)
  - `frontend/tests/AC-S06-02.test.jsx` (Vitest UI Component Test: ตรวจสอบการขอชั่งซ้ำ และการแจ้งข้อพิพาท `S8: Disputed` ตาม `REQ-FN-006`, `AC-S06-02`)
  - `frontend/tests/AC-S06-03.test.jsx` (Vitest UI Component Test: ตรวจสอบการเลือกชำระเงิน CASH / PROMPTPAY และปุ่มยืนยันรับเงินตาม `UC-07`, `AC-S06-03`)
  - `frontend/tests/AC-S06-04.test.jsx` (Vitest UI Component Test: ตรวจสอบการแสดงใบเสร็จดิจิทัล และ PII Masking `08X-XXX-XXXX` ตาม `REQ-FN-005`, `REQ-SEC-002`, `AC-S06-04`)
  - `backend/tests/test_e2e_payment_and_verification.py` (Pytest Integration E2E Test: ครอบคลุมวงจรเต็มตั้งแต่ชั่งจริง -> ตรวจสอบเกต -> ยืนยันน้ำหนัก -> ชำระเงิน PromptPay -> รับเงิน -> ออกใบเสร็จดิจิทัล ตรวจสอบ Audit Log `AC-S06-05` และ Price Snapshot Integrity `REQ-BR-002`)
  - `specs/seller/06-payment-and-verification/tasks.md` (อัปเดตสถานะ `T-08` เป็น `[DONE]` และอัปเดตสถานะรวมของ Tasks เป็น `completed`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ทดสอบและเอกสาร Tasks ตามที่ระบุใน `T-08`
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`11 files passed, 32 passed in 0.90s`** (ผ่าน 100% ครบทุก Component Tests)
     - รัน Full Backend Suite `.venv/bin/pytest backend/tests/`: **`47 passed in 0.26s`** (ผ่าน 100% ครบทุก E2E และ AC tests)
     - ยอดรวมชุดทดสอบทั้งระบบ: **79 tests ผ่าน 100% (Backend 47 + Frontend 32)**
  3. **การอ้างอิง ID:** ฟังก์ชันและชุดทดสอบทุกไฟล์ตั้งชื่อและอ้างอิงรหัส `AC-S06-01..05`, `REQ-FN-004..006`, `REQ-SEC-001..002`, `REQ-BR-002`, `P-01..P-06` ครบถ้วนตามกฎข้อ 7 และ 8 ของ `AGENTS.md`
  4. **Non-goals & Open Questions:** ชุดทดสอบทดสอบเฉพาะฟังก์ชันที่อยู่ในขอบเขต ไม่มีเคสที่เกินสเปก
  5. **การบันทึกผล:** อัปเดตสถานะ `T-08` เป็น `[DONE]` ใน `tasks.md`, สถานะภาพรวมเป็น `completed`, และบันทึกประวัติลง `prompt-log.md` เรียบร้อย


---

## บันทึก #30 — `/clarify specs/seller/07-post-transaction` (ระบบหลังทำธุรกรรม)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/clarify specs/seller/07-post-transaction`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/07-post-transaction/spec.md` (ปรับปรุงเป็น Version 2.0 สถานะ reviewed-post-clarify หลังเคลียร์จุดกำกวม CC-01..03 และคำถาม Q-01..05 ครบถ้วน)
- **ประเด็นที่เคลียร์และข้อตกลงของทีม:**
  1. **`CC-01`**: ปรับรหัส Use Case ให้ตรงกับสารบัญกลางใน `docs/srs/use-cases.md`: ใช้ `UC-10: ให้คะแนนรีวิว สรุปยอดรายวัน และจัดการหลังจบงาน` (เดิมระบุผิดเป็น `UC-11` ซึ่งเป็น Use Case ตรวจสอบ KYC ของแอดมิน)
  2. **`CC-02`**: ปรับการเชื่อมโยงรหัส Requirement ตาม Catalogue กลาง: ยกเลิกการอ้างอิง `REQ-QA-001` และ `REQ-UX-001` ที่ไม่ตรงความหมาย โดยเชื่อมโยงกับ `UC-10` / `SC-05` (การให้คะแนนรีวิวและบันทึกผู้รับซื้อประจำ), `REQ-FN-005` (ใบเสร็จดิจิทัล), `REQ-SEC-002` (PDPA Masking `08X-XXX-XXXX`), `REQ-OP-001` / `CC-05` (Offline Cache ใน Local Storage), และ `REQ-SEC-001` (Audit Logging)
  3. **`CC-03`**: ผังสถานะยึดตาม `MD-STM-04`: ดำเนินการในสถานะ `S7: สำเร็จ / ปิดงาน (Completed)` เท่านั้น
  4. **`Q-01` (ทางเลือก A)**: การให้คะแนนรีวิวไม่บังคับ (Optional) มีปุ่ม *"ส่งรีวิว"* และปุ่ม *"ข้าม / ดูใบเสร็จ"* เพื่อไม่บล็อกผู้ขายที่เร่งรีบ
  5. **`Q-02` (ทางเลือก A)**: โครงสร้างคะแนน 1–5 ดาว พร้อมข้อความความคิดเห็น (ไม่เกิน 500 ตัวอักษร) ส่งได้ 1 ครั้งต่อคำขอ ไม่อนุญาตให้แก้ไขย้อนหลัง เพื่อป้องกันการปั่นคะแนน
  6. **`Q-03` (ทางเลือก A)**: บันทึกความสัมพันธ์ "ผู้รับซื้อประจำ" ลงในตาราง `seller_favorites` (`seller_id`, `collector_id`) รองรับการ Toggle เพิ่ม/ยกเลิกได้ตลอดเวลา
  7. **`Q-04` (ทางเลือก A)**: หน้าประวัติการขายแสดงสถิติสรุปสะสม (ยอดเงินรวม, น้ำหนักรวม, จำนวนครั้งสำเร็จ) และรายการคำขอย้อนหลังพร้อม PII Masking และรองรับการเปิดดูใบเสร็จดิจิทัลแบบ Offline Read
  8. **`Q-05`**: ยืนยันขอบเขต Non-goals ไม่ทำระบบให้ทิป (Tipping), ไม่ทำระบบแชทคุยต่อหลังจบงาน, และไม่ทำเว็บบอร์ดสนทนาสาธารณะ
- **สถานะ:** สเปก `seller/07` ได้รับการรับรองและพร้อมสำหรับขั้นตอน `/plan`


---

## บันทึก #31 — `/plan specs/seller/07-post-transaction/spec.md` (แผนสถาปัตยกรรมและเทคโนโลยี)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/07-post-transaction/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/07-post-transaction/plan.md` (จัดทำแผนสถาปัตยกรรมระบบ 8 หัวข้อหลัก ครอบคลุม P-01 ถึง P-06, Tech Stack "ทีมเลือกเอง ไม่ได้มาจาก spec", Data Model, Endpoints, UI Plan, และตารางตรวจ Constraints 13 ข้อ)
- **ประเด็นสำคัญในแผน:**
  1. **Tech Stack:** Python 3.11 (FastAPI) + Supabase (PostgreSQL 15+) + React 18 (Vite + TailwindCSS) (`"ทีมเลือกเอง ไม่ได้มาจาก spec"`)
  2. **สถาปัตยกรรม 6 การตัดสินใจ (`P-01` ถึง `P-06`):**
     - `P-01`: RatingReviewService บันทึกคะแนน 1–5 ดาว รีวิวไม่เกิน 500 ตัวอักษร จำกัด 1 ครั้งต่อคำขอ และมีปุ่มข้าม (`UC-10`, `SC-05`, `AC-S07-01`)
     - `P-02`: FavoriteCollectorService ตาราง `seller_favorites` ระบบ Toggle Bookmark ผู้รับซื้อประจำ (`UC-10`, `SC-05`, `AC-S07-02`)
     - `P-03`: SalesHistoryAggregationService สรุปยอดเงินรวม น้ำหนักรวม จำนวนครั้ง พร้อม PII Masking เบอร์โทร `08X-XXX-XXXX` (`REQ-FN-005`, `REQ-SEC-002`, `AC-S07-03`)
     - `P-04`: Digital Receipt Inspection & Offline Access รองรับแคชประวัติและใบเสร็จใน Local Storage (`REQ-FN-005`, `REQ-OP-001`, `CC-05`, `AC-S07-04`)
     - `P-05`: Audit Logging for Post-Transaction บันทึกประวัติการส่งรีวิวและเพิ่ม/ลบผู้รับซื้อประจำ (`REQ-SEC-001`, `AC-S07-05`)
     - `P-06`: Mobile-First UI Architecture คอมโพเนนต์ React รองรับจอมือถือ 375px–414px (`CC-01`, `AC-S07-01..05`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` พร้อมระบุเหตุผลข้อที่ไม่เกี่ยวข้อง
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #32 — `/tasks specs/seller/07-post-transaction/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/07-post-transaction/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/07-post-transaction/tasks.md` (แตกงานย่อย 7 งาน `T-01` ถึง `T-07` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S07-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 7 งาน (`T-01` ถึง `T-07`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบรีวิว (`collector_reviews`) และผู้รับซื้อประจำ (`seller_favorites`)
     - `T-02`: สร้าง Service และ API ให้คะแนน 1–5 ดาวและรีวิวบริการซาเล้ง (`RatingReviewService`, `AC-S07-01`)
     - `T-03`: สร้าง Service และ API จัดการผู้รับซื้อประจำ Bookmark (`FavoriteCollectorService`, `AC-S07-02`)
     - `T-04`: สร้าง Service และ API สรุปประวัติการขาย สถิติสะสม และ PII Masking `08X-XXX-XXXX` (`SalesHistoryAggregationService`, `AC-S07-03`)
     - `T-05`: สร้าง Frontend API Client และระบบแคชประวัติการขายออฟไลน์ใน `localStorage` (`AC-S07-04`)
     - `T-06`: พัฒนาคอมโพเนนต์และหน้าจอ React Mobile-First SPA (`PostTransactionRatingModal`, `SalesSummaryCards`, `SalesOrderCard`, `SalesHistoryPage`)
     - `T-07`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S07-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S07-01` ถึง `AC-S07-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยแรก `/implement T-01`


---

## บันทึก #37 — `/implement T-01..08` (พัฒนาระบบแจ้งเตือนและการช่วยเหลือ Notifications & Help Center ครบวงจร)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/notification_help_models.py` (Pydantic models สำหรับ Notifications, Sorting Guides, FAQs, Support Tickets, Contact Info)
  - `backend/app/core/supabase.py` (เพิ่มคอลเลกชัน `seller_notifications`, `support_tickets`, ฟังก์ชัน `generate_draft_reminders_for_seller`, `mark_all_notifications_as_read`, `create_support_ticket`)
  - `backend/app/services/notification_help_service.py` (`NotificationService`, `KnowledgeBaseService`, `SupportTicketService` พร้อม PDPA masking `08X-XXX-XXXX` และบันทึก Audit Log)
  - `backend/app/api/v1/notifications_help.py` (FastAPI Router สำหรับ endpoints แจ้งเตือน, คู่มือคัดแยก, FAQ, และส่งคำร้องขอความช่วยเหลือ)
  - `backend/app/api/v1/pricing.py` (ลงทะเบียน `notifications_help_router`)
  - `frontend/src/services/notificationHelpApi.js` (API Client ฝั่งหน้าบ้านพร้อมระบบ LocalStorage Caching สำหรับคู่มือและ FAQ โหมดออฟไลน์ CC-05, REQ-OP-001)
  - `frontend/src/components/NotificationCenterModal.jsx` (คอมโพเนนต์ศูนย์แจ้งเตือน พร้อมตัวเลขนับ badge, รายการแจ้งเตือน, ปุ่มอ่านแล้วรายข้อ/อ่านทั้งหมด `UC-08`)
  - `frontend/src/components/WasteSortingGuideView.jsx` (คอมโพเนนต์คู่มือแนะนำคัดแยกขยะ 4 หมวดหลัก พร้อมเคล็ดลับเพิ่มมูลค่าราคาและข้อควรระวัง `UC-08`)
  - `frontend/src/components/FaqAccordionView.jsx` (คอมโพเนนต์คำถามที่พบบ่อย 3 หมวดหมู่ แบบ Accordion พร้อม Search Filter ค้นหาคำสำคัญ `UC-08`)
  - `frontend/src/components/SupportTicketModal.jsx` (แบบฟอร์มส่งคำร้องขอความช่วยเหลือ พร้อมปกปิดเบอร์โทรศัพท์และข้อมูลติดต่อสายด่วน Call Center / LINE `UC-13`, `REQ-SEC-002`)
  - `frontend/src/pages/HelpCenterPage.jsx` (หน้าจอรวมศูนย์ช่วยเหลือและการแจ้งเตือน Mobile-First SPA)
  - `backend/tests/test_T01_notifications_and_help_models.py` (Unit tests สำหรับ Pydantic Models และ Supabase Store: 3 passed)
  - `backend/tests/test_AC_S08_01_notifications.py` (Backend test สำหรับ AC-S08-01: 1 passed)
  - `backend/tests/test_AC_S08_02_sorting_guides.py` (Backend test สำหรับ AC-S08-02: 1 passed)
  - `backend/tests/test_AC_S08_03_faqs.py` (Backend test สำหรับ AC-S08-03: 2 passed)
  - `backend/tests/test_AC_S08_04_support_tickets.py` (Backend test สำหรับ AC-S08-04: 2 passed)
  - `backend/tests/test_e2e_notifications_and_help.py` (Backend E2E Integration test สำหรับ AC-S08-01..05: 1 passed)
  - `frontend/tests/notificationHelpApi.test.mjs` (Frontend API & Offline Cache test: 5 passed)
  - `frontend/tests/AC-S08-01.test.jsx` (Vitest UI Component test: 2 passed)
  - `frontend/tests/AC-S08-02.test.jsx` (Vitest UI Component test: 1 passed)
  - `frontend/tests/AC-S08-03.test.jsx` (Vitest UI Component test: 1 passed)
  - `frontend/tests/AC-S08-04.test.jsx` (Vitest UI Component test: 1 passed)
  - `specs/seller/08-notifications-and-help/tasks.md` (อัปเดตสถานะงาน `T-01` ถึง `T-08` เป็น `[DONE]` และอัปเดตสถานะรวมเป็น `completed`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดไว้ใน `tasks.md` (T-01 ถึง T-08)
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`21 files passed, 55 passed in 1.57s`** (ผ่าน 100% ครอบคลุม UI Components และ Offline Cache)
     - รัน `pytest backend/tests/` (Pytest): **`67 passed in 0.28s`** (ผ่าน 100% ครอบคลุม Unit, AC, และ E2E Lifecycle)
     - **ยอดรวมทั้งระบบ: 122 tests ผ่านทั้งหมด 100% (Backend 67 + Frontend 55)**
  3. **การอ้างอิง ID:** ฟังก์ชัน คอมโพเนนต์ และชุดทดสอบทุกไฟล์ระบุรหัส `UC-08`, `UC-13`, `REQ-OP-001`, `REQ-SEC-001`, `REQ-SEC-002`, `CC-01..06`, `AC-S08-01..05`, `P-01..P-06`, `T-01..T-08` ครบถ้วนตามกฎของ `AGENTS.md`
  4. **Non-goals & Open Questions:** ขอบเขตตรงตามสเปก v2.0 ไม่ทำ AI Live Agent Chatbot 24 ชม., และไม่เชื่อมโยง Push Notifications ข้ามเครื่อง (APNs/FCM)
  5. **การบันทึกสถานะ:** อัปเดตงานย่อย `T-01..T-08` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย



---

## บันทึก #33 — `/implement T-01..07` (พัฒนาระบบหลังทำธุรกรรมครบทุกงานย่อย T-01 ถึง T-07)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01..07`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/post_transaction_models.py` (Pydantic models: ReviewCreateRequest, ReviewResponse, FavoriteCollectorRequest, FavoriteCollectorResponse, SalesSummaryResponse, SalesOrderHistoryItem, SalesHistoryResponse)
  - `backend/app/core/supabase.py` (ขยาย Supabase store: collector_reviews, seller_favorites, create_review, get_review_by_order, get_collector_rating_summary, add_favorite, remove_favorite, is_favorite, get_completed_orders_for_seller)
  - `backend/app/services/post_transaction_service.py` (Service Layer: PostTransactionService รองรับ submit_review, get_review, toggle_favorite, get_favorites, get_sales_history พร้อม PII Masking)
  - `backend/app/api/v1/post_transaction.py` (API Router: endpoints สำหรับส่งรีวิว, จัดการผู้รับซื้อประจำ, และดึงประวัติการขาย)
  - `backend/app/api/v1/pricing.py` (ลงทะเบียน post_transaction_router เข้าสู่ FastAPI app)
  - `frontend/src/services/postTransactionApi.js` (Frontend API Client พร้อมระบบ Local Storage Cache สำหรับประวัติการขายและใบเสร็จดิจิทัล CC-05, REQ-OP-001)
  - `frontend/src/components/PostTransactionRatingModal.jsx` (คอมโพเนนต์ให้คะแนนดาว 1–5 ดาว, ความคิดเห็น, ปุ่มทางลัดผู้รับซื้อประจำ, และปุ่มข้าม UC-10, Q-01, Q-02)
  - `frontend/src/components/SalesSummaryCards.jsx` (คอมโพเนนต์แสดงสถิติสะสม 3 ด้าน: รายรับรวม, น้ำหนักรวม, จำนวนครั้งสำเร็จ UC-10)
  - `frontend/src/components/SalesOrderCard.jsx` (คอมโพเนนต์แสดงรายการคำขอสำเร็จ พร้อม PII Masking เบอร์โทร 08X-XXX-XXXX, ไอคอนผู้รับซื้อประจำ, และปุ่มดูใบเสร็จ REQ-FN-005, REQ-SEC-002)
  - `frontend/src/pages/SalesHistoryPage.jsx` (หน้าจอหลักรวมประวัติการขาย Mobile-First SPA พร้อมป้ายสถานะออฟไลน์แคชและ Modal ใบเสร็จดิจิทัล)
  - `backend/tests/test_T01_post_transaction_models.py` (Unit tests สำหรับ Schema และ Validation)
  - `backend/tests/test_AC_S07_01_rating_and_review.py` (Automated tests สำหรับรีวิว 1-5 ดาว, ตรวจสอบ S7, และบล็อกส่งซ้ำ 409)
  - `backend/tests/test_AC_S07_02_favorite_collector.py` (Automated tests สำหรับ Toggle ผู้รับซื้อประจำ และ Audit Logs)
  - `backend/tests/test_AC_S07_03_sales_history_and_masking.py` (Automated tests สำหรับประวัติการขาย, สรุปสถิติสะสม, และ PII Masking)
  - `backend/tests/test_e2e_post_transaction.py` (Integration E2E Test ทดสอบครบวงจร S7 -> รีวิว -> ผู้รับซื้อประจำ -> ประวัติการขาย -> ใบเสร็จดิจิทัล -> Audit Logs AC-S07-05)
  - `frontend/tests/postTransactionApi.test.mjs` (Unit tests สำหรับ Client & Offline Local Storage Cache)
  - `frontend/tests/AC-S07-01.test.jsx` (Component Test: การให้คะแนนดาว, เขียนรีวิว, และการกดข้าม)
  - `frontend/tests/AC-S07-02.test.jsx` (Component Test: ปุ่มบันทึกผู้รับซื้อประจำ และป้ายขาประจำ)
  - `frontend/tests/AC-S07-03.test.jsx` (Component Test: สถิติสรุปสะสม และ PII Masking 08X-XXX-XXXX)
  - `frontend/tests/AC-S07-04.test.jsx` (Component Test: การเปิดดูใบเสร็จดิจิทัล และป้ายแสดงออฟไลน์แคช)
  - `specs/seller/07-post-transaction/tasks.md` (อัปเดตสถานะ T-01..T-07 เป็น [DONE] และสถานะรวมเป็น completed)
- **ผลการตรวจ 5 ข้อหลังจบ Tasks (5 Checkpoints):**
  1. **ไฟล์ที่แตะ:** สร้างและแก้ไขเฉพาะไฟล์ตามที่ระบุใน `tasks.md` (`T-01` ถึง `T-07`)
  2. **ผลการรัน Test:**
     - รัน Frontend Tests ทั้งหมด `npm test --prefix frontend`: **`16 files passed, 45 passed in 1.25s`** (100% ผ่านทุกการทดสอบ)
     - รัน Backend Tests ทั้งหมด `.venv/bin/pytest backend/tests/`: **`57 passed in 0.28s`** (100% ผ่านทุกการทดสอบ)
     - **ยอดรวมทั้งระบบ: 102 tests ผ่านทั้งหมด 100% (Backend 57 + Frontend 45)**
  3. **การอ้างอิง ID:** ฟังก์ชันและชุดทดสอบทุกไฟล์ระบุรหัส `UC-10`, `SC-05`, `REQ-FN-005`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-OP-001`, `CC-01..06`, `AC-S07-01..05`, `P-01..P-06` ครบถ้วนตามกฎของ `AGENTS.md`
  4. **Non-goals & Open Questions:** ขอบเขตตรงตามสเปก v2.0 ไม่ทำระบบให้ทิป (Tipping), ไม่ทำระบบแชทคุยต่อหลังจบงาน, และไม่ทำเว็บบอร์ดสาธารณะ
  5. **การบันทึกสถานะ:** อัปเดตงานย่อย `T-01..T-07` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #34 — `/clarify specs/seller/08-notifications-and-help` (ระบบแจ้งเตือนและการช่วยเหลือ)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/clarify specs/seller/08-notifications-and-help`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/08-notifications-and-help/spec.md` (ปรับปรุงเป็น Version 2.0 สถานะ reviewed-post-clarify หลังเคลียร์จุดกำกวม CC-01..03 และคำถาม Q-01..05 ครบถ้วน)
- **ประเด็นที่เคลียร์และข้อตกลงของทีม:**
  1. **`CC-01`**: เชื่อมโยง Use Case หลักตามสารบัญกลาง `docs/srs/use-cases.md`: ใช้ `UC-08: สื่อสารผ่านข้อความมาตรฐานและแจ้งเตือนสถานะนัดหมาย` และเชื่อมโยง Customer Support กับศูนย์ดูแลระบบ Admin `UC-13`
  2. **`CC-02`**: ปรับการเชื่อมโยงรหัส Requirement ให้สอดคล้องกับ Catalogue กลาง 16 ข้อ: ยกเลิกการอ้างอิง `REQ-UX-002` (ซึ่งหมายถึงเกณฑ์เตือนส่วนต่างน้ำหนัก ±15%) และเชื่อมโยงกับ `UC-08`, `REQ-OP-001` / `CC-05` (Offline Cache สำหรับคู่มือและ FAQ), `REQ-SEC-002` (PDPA Masking `08X-XXX-XXXX` ใน Ticket), และ `REQ-SEC-001` (Audit Logging)
  3. **`CC-03`**: ผังสถานะยึดตาม `MD-STM-04`: การแจ้งเตือนของค้างทำงานบนสถานะ `S1 (Draft/Posted)` ที่ค้างเกิน 3 วัน และการแจ้งเตือนสถานะคำขอทำงานบนสถานะ `S2..S7`
  4. **`Q-01` (ทางเลือก A)**: ระบบแจ้งเตือนแบบ In-App Notification Feed (Notification Center) มี Badge แสดงตัวเลขที่ยังไม่ได้อ่าน แจ้งเตือนของค้างใน S1 เกิน 3 วัน และแจ้งเตือนเมื่อคำขอเปลี่ยนสถานะ
  5. **`Q-02` (ทางเลือก A)**: คู่มือแนะนำการคัดแยกขยะเพื่อเพิ่มมูลค่า 4 หมวดหลัก (`MAT-CARDBOARD`, `MAT-WHITE-PAPER`, `MAT-GLASS-BOTTLE`, `MAT-PLASTIC-PET`) พร้อมเคล็ดลับเพิ่มมูลค่า และเปิดอ่านออฟไลน์ได้
  6. **`Q-03` (ทางเลือก A)**: ศูนย์ช่วยเหลือและคำถามที่พบบ่อย (FAQ) แบ่งเป็น 3 หมวดหมู่หลักในรูปแบบ Accordion พร้อมกล่องค้นหาตามคำสำคัญ (Search Filter)
  7. **`Q-04` (ทางเลือก A)**: ช่องทางติดต่อ Customer Support มีแบบฟอร์มส่ง Ticket บันทึกลงตารางพร้อม PII Masking และแสดงข้อมูลติดต่อสายด่วน Call Center / LINE Official
  8. **`Q-05`**: ยืนยันขอบเขต Non-goals ไม่ทำ AI Chatbot 24 ชม., และไม่ส่ง Push Notification ข้ามเครื่องผ่าน APNs/FCM
- **สถานะ:** สเปก `seller/08` ได้รับการรับรองและพร้อมสำหรับขั้นตอน `/plan`


---

## บันทึก #35 — `/plan specs/seller/08-notifications-and-help/spec.md` (แผนสถาปัตยกรรมและเทคโนโลยี)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/08-notifications-and-help/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/08-notifications-and-help/plan.md` (จัดทำแผนสถาปัตยกรรมระบบ 7 หัวข้อหลัก ครอบคลุม P-01 ถึง P-06, Tech Stack "ทีมเลือกเอง ไม่ได้มาจาก spec", Data Model, Endpoints, และตารางตรวจ Constraints 13 ข้อ)
- **ประเด็นสำคัญในแผน:**
  1. **Tech Stack:** Python 3.11 (FastAPI) + Supabase (PostgreSQL 15+) + React 18 (Vite + TailwindCSS) (`"ทีมเลือกเอง ไม่ได้มาจาก spec"`)
  2. **สถาปัตยกรรม 6 การตัดสินใจ (`P-01` ถึง `P-06`):**
     - `P-01`: NotificationService ตรวจสอบคำขอค้างใน `S1` > 3 วันเพื่อสร้าง Draft Reminder และแจ้งเตือนสถานะคำขอ (`UC-08`, `AC-S08-01`)
     - `P-02`: Waste Sorting Knowledge Base คู่มือ 4 หมวดหลักพร้อมเคล็ดลับเพิ่มมูลค่า และออฟไลน์แคช (`UC-08`, `CC-05`, `AC-S08-02`)
     - `P-03`: Categorized FAQ Knowledge Base คำถาม 3 หมวดหมู่ แบบ Accordion พร้อม Search Filter (`UC-08`, `CC-05`, `AC-S08-03`)
     - `P-04`: Customer Support Ticket Service ตาราง `support_tickets` พร้อมรหัส `TCK-YYYYMMDD-XXXX`, PII Masking `08X-XXX-XXXX`, และข้อมูลสายด่วน (`UC-13`, `REQ-SEC-002`, `AC-S08-04`)
     - `P-05`: Audit Logging for Support Events บันทึกประวัติการส่งตั๋วและเคลียร์การแจ้งเตือน (`REQ-SEC-001`, `AC-S08-05`)
     - `P-06`: Mobile-First UI Architecture คอมโพเนนต์ React รองรับจอมือถือ 375px–414px (`CC-01`, `AC-S08-01..05`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` พร้อมระบุเหตุผลข้อที่ไม่เกี่ยวข้อง
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #36 — `/tasks specs/seller/08-notifications-and-help/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/08-notifications-and-help/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/08-notifications-and-help/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S08-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบแจ้งเตือน (`seller_notifications`) และตั๋วช่วยเหลือ (`support_tickets`)
     - `T-02`: สร้าง Service และ API สำหรับศูนย์แจ้งเตือนและเตือนของค้างในฉบับร่าง S1 > 3 วัน (`NotificationService`, `AC-S08-01`)
     - `T-03`: สร้าง Service และ API สำหรับคู่มือแนะนำการคัดแยกขยะ 4 หมวดหลัก (`KnowledgeBaseService`, `AC-S08-02`)
     - `T-04`: สร้าง Service และ API สำหรับคำถามที่พบบ่อย (FAQ) 3 หมวดหมู่ พร้อมระบบค้นหา (`AC-S08-03`)
     - `T-05`: สร้าง Service และ API สำหรับส่งตั๋วแจ้งปัญหาพร้อม PII Masking และข้อมูลสายด่วน (`SupportTicketService`, `AC-S08-04`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชคู่มือ/FAQ ออฟไลน์ใน `localStorage` (`AC-S08-02`, `AC-S08-03`)
     - `T-07`: พัฒนาคอมโพเนนต์และหน้าจอศูนย์ช่วยเหลือ React Mobile-First SPA (`NotificationCenterModal`, `WasteSortingGuideView`, `FaqAccordionView`, `SupportTicketModal`, `HelpCenterPage`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S08-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S08-01` ถึง `AC-S08-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยแรก `/implement T-01`


---

## บันทึก #37 — `/implement T-01..08` (พัฒนาระบบแจ้งเตือนและการช่วยเหลือ Notifications & Help Center ครบวงจร)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/notification_help_models.py` (Pydantic models สำหรับ Notifications, Sorting Guides, FAQs, Support Tickets, Contact Info)
  - `backend/app/core/supabase.py` (เพิ่มคอลเลกชัน `seller_notifications`, `support_tickets`, ฟังก์ชัน `generate_draft_reminders_for_seller`, `mark_all_notifications_as_read`, `create_support_ticket`)
  - `backend/app/services/notification_help_service.py` (`NotificationService`, `KnowledgeBaseService`, `SupportTicketService` พร้อม PDPA masking `08X-XXX-XXXX` และบันทึก Audit Log)
  - `backend/app/api/v1/notifications_help.py` (FastAPI Router สำหรับ endpoints แจ้งเตือน, คู่มือคัดแยก, FAQ, และส่งคำร้องขอความช่วยเหลือ)
  - `backend/app/api/v1/pricing.py` (ลงทะเบียน `notifications_help_router`)
  - `frontend/src/services/notificationHelpApi.js` (API Client ฝั่งหน้าบ้านพร้อมระบบ LocalStorage Caching สำหรับคู่มือและ FAQ โหมดออฟไลน์ CC-05, REQ-OP-001)
  - `frontend/src/components/NotificationCenterModal.jsx` (คอมโพเนนต์ศูนย์แจ้งเตือน พร้อมตัวเลขนับ badge, รายการแจ้งเตือน, ปุ่มอ่านแล้วรายข้อ/อ่านทั้งหมด `UC-08`)
  - `frontend/src/components/WasteSortingGuideView.jsx` (คอมโพเนนต์คู่มือแนะนำคัดแยกขยะ 4 หมวดหลัก พร้อมเคล็ดลับเพิ่มมูลค่าราคาและข้อควรระวัง `UC-08`)
  - `frontend/src/components/FaqAccordionView.jsx` (คอมโพเนนต์คำถามที่พบบ่อย 3 หมวดหมู่ แบบ Accordion พร้อม Search Filter ค้นหาคำสำคัญ `UC-08`)
  - `frontend/src/components/SupportTicketModal.jsx` (แบบฟอร์มส่งคำร้องขอความช่วยเหลือ พร้อมปกปิดเบอร์โทรศัพท์และข้อมูลติดต่อสายด่วน Call Center / LINE `UC-13`, `REQ-SEC-002`)
  - `frontend/src/pages/HelpCenterPage.jsx` (หน้าจอรวมศูนย์ช่วยเหลือและการแจ้งเตือน Mobile-First SPA)
  - `backend/tests/test_T01_notifications_and_help_models.py` (Unit tests สำหรับ Pydantic Models และ Supabase Store: 3 passed)
  - `backend/tests/test_AC_S08_01_notifications.py` (Backend test สำหรับ AC-S08-01: 1 passed)
  - `backend/tests/test_AC_S08_02_sorting_guides.py` (Backend test สำหรับ AC-S08-02: 1 passed)
  - `backend/tests/test_AC_S08_03_faqs.py` (Backend test สำหรับ AC-S08-03: 2 passed)
  - `backend/tests/test_AC_S08_04_support_tickets.py` (Backend test สำหรับ AC-S08-04: 2 passed)
  - `backend/tests/test_e2e_notifications_and_help.py` (Backend E2E Integration test สำหรับ AC-S08-01..05: 1 passed)
  - `frontend/tests/notificationHelpApi.test.mjs` (Frontend API & Offline Cache test: 5 passed)
  - `frontend/tests/AC-S08-01.test.jsx` (Vitest UI Component test: 2 passed)
  - `frontend/tests/AC-S08-02.test.jsx` (Vitest UI Component test: 1 passed)
  - `frontend/tests/AC-S08-03.test.jsx` (Vitest UI Component test: 1 passed)
  - `frontend/tests/AC-S08-04.test.jsx` (Vitest UI Component test: 1 passed)
  - `specs/seller/08-notifications-and-help/tasks.md` (อัปเดตสถานะงาน `T-01` ถึง `T-08` เป็น `[DONE]` และอัปเดตสถานะรวมเป็น `completed`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดไว้ใน `tasks.md` (T-01 ถึง T-08)
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`21 files passed, 55 passed in 1.57s`** (ผ่าน 100% ครอบคลุม UI Components และ Offline Cache)
     - รัน `pytest backend/tests/` (Pytest): **`67 passed in 0.28s`** (ผ่าน 100% ครอบคลุม Unit, AC, และ E2E Lifecycle)
     - **ยอดรวมทั้งระบบ: 122 tests ผ่านทั้งหมด 100% (Backend 67 + Frontend 55)**
  3. **การอ้างอิง ID:** ฟังก์ชัน คอมโพเนนต์ และชุดทดสอบทุกไฟล์ระบุรหัส `UC-08`, `UC-13`, `REQ-OP-001`, `REQ-SEC-001`, `REQ-SEC-002`, `CC-01..06`, `AC-S08-01..05`, `P-01..P-06`, `T-01..T-08` ครบถ้วนตามกฎของ `AGENTS.md`
  4. **Non-goals & Open Questions:** ขอบเขตตรงตามสเปก v2.0 ไม่ทำ AI Live Agent Chatbot 24 ชม., และไม่เชื่อมโยง Push Notifications ข้ามเครื่อง (APNs/FCM)
  5. **การบันทึกสถานะ:** อัปเดตงานย่อย `T-01..T-08` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย
---

## บันทึก #38 — `/clarify specs/seller/09-transaction-safety` (ระบบความปลอดภัยขณะทำธุรกรรม)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/clarify specs/seller/09-transaction-safety/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/09-transaction-safety/spec.md` (ปรับปรุงเป็น Version 2.0 สถานะ `reviewed-post-clarify` หลังคลี่คลายจุดกำกวม CC-01..03 และคำถาม Q-01..05 ครบถ้วน)
- **ประเด็นที่เคลียร์และข้อตกลงของทีม:**
  1. **`CC-01`**: เชื่อมโยง Use Case หลักตามสารบัญกลาง `docs/srs/use-cases.md`: ใช้ **`UC-09: ดูแลความปลอดภัยขณะทำธุรกรรมและปุ่มฉุกเฉิน SOS`** และเชื่อมโยงกับการส่งต่อแจ้งเหตุด่วน/ข้อพิพาทไปยังศูนย์ดูแลระบบ **`UC-13`**
  2. **`CC-02`**: ปรับรหัสความต้องการและหลักฐานให้สอดคล้องกับสารบัญกลาง: ปลดรหัส `EV-014` ที่อยู่นอกสารบัญ และเชื่อมโยงกับรหัสหลักฐานกลาง **`EV-08`** (ความปลอดภัยหน้างาน) และ **`EV-09`** (PDPA Masking) พร้อมผูกเข้ากับข้อกำหนด **`REQ-SEC-001`** (Audit Log), **`REQ-SEC-002`** (PDPA Masking), **`REQ-QA-001`** (Latency < 2.0 วินาที), **`REQ-UX-001`** (ปุ่มฉุกเฉิน >= 48px), และ **`REQ-FN-006`** (ล็อกหลักฐานห้ามแก้ไขเมื่อมีข้อพิพาท)
  3. **`CC-03`**: ผังสถานะยึดตาม `MD-STM-04`: ปุ่ม **`SOS ฉุกเฉิน`** ใช้งานได้ในสถานะ **`S3..S6`** (ตั้งแต่ซาเล้งกำลังเดินทางมาจนถึงทำธุรกรรมเสร็จ) ส่วนการบันทึกเสียง/วิดีโอหลักฐาน ใช้งานได้ในสถานะหน้างาน **`S4..S6`** โดยไฟล์จะถูกล็อกห้ามลบ/แก้ไขทันทีเมื่อคำขอเปลี่ยนเป็นสถานะ **`S8: Disputed`**
  4. **`Q-01` (ทางเลือก A)**: ระบบบันทึกเสียงและคลิปวิดีโอหลักฐานหน้างาน (In-App Media Evidence Recorder) ผ่าน MediaRecorder API แสดงตัวจับเวลา จำกัดขนาด 25 MB ต่อไฟล์ (`CC-01`) แนบไฟล์เข้ากับ `order_id` และบันทึก Audit Log ทุกครั้ง
  5. **`Q-02` (ทางเลือก A)**: ปุ่มฉุกเฉิน SOS One-Tap Trigger ส่งพิกัดบ้าน ข้อมูลซาเล้ง และรหัสคำขอไปยังศูนย์ดูแลระบบ Admin ภายใน 2.0 วินาที (`REQ-QA-001`) พร้อมแสดงหน้าต่างโทรออกด่วน (`tel:`) ไปยังเบอร์ญาติหรือสายด่วน Saleng / 191
  6. **`Q-03` (ทางเลือก A)**: การจัดการเบอร์ผู้ติดต่อฉุกเฉินที่ไว้ใจได้ (Trusted Emergency Contact) พร้อม PDPA Masking `08X-XXX-XXXX` (`REQ-SEC-002`) และมีค่าเริ่มต้นเป็นเบอร์ Saleng Hotline (`02-123-4567`)
  7. **`Q-04` (ทางเลือก A)**: ล็อกหลักฐานความปลอดภัย (Evidence Immutability) เมื่อมีการกด SOS หรือเปลี่ยนเป็นสถานะ `S8: Disputed` ให้เป็น Read-only ทันทีตาม `REQ-FN-006` เพื่อส่งต่อให้ Admin ใน `UC-13`
  8. **`Q-05` (ทางเลือก A)**: ยืนยัน Non-goals ชัดเจน ไม่ทำ AI Audio Surveillance ดักฟังอัตโนมัติ, ไม่ทำ in-app VoIP calling, และไม่เชื่อมต่อ API ตำรวจ 191 โดยตรง
- **สถานะ:** สเปก `seller/09` ได้รับการรับรอง Version 2.0 และพร้อมสำหรับขั้นตอน `/plan`
---

## บันทึก #39 — `/plan specs/seller/09-transaction-safety/spec.md` (แผนสถาปัตยกรรมและเทคโนโลยี)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/09-transaction-safety/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/09-transaction-safety/plan.md` (จัดทำแผนสถาปัตยกรรมระบบ 8 หัวข้อหลัก ครอบคลุม P-01 ถึง P-06, Tech Stack "ทีมเลือกเอง ไม่ได้มาจาก spec", Data Model, Endpoints, UI Plan, และตารางตรวจ Constraints 13 ข้อ)
- **ประเด็นสำคัญในแผน:**
  1. **Tech Stack:** Python 3.11 (FastAPI) + Supabase (PostgreSQL 15+) + React 18 (Vite + TailwindCSS) (`"ทีมเลือกเอง ไม่ได้มาจาก spec"`)
  2. **สถาปัตยกรรม 6 การตัดสินใจ (`P-01` ถึง `P-06`):**
     - `P-01`: MediaEvidenceService บันทึกเสียงและคลิปวิดีโอหน้างานในสถานะ S4..S6 จำกัดขนาด 25 MB ต่อไฟล์ (`UC-09`, `AC-S09-01`)
     - `P-02`: EmergencySosService ระบบส่งสัญญาณฉุกเฉิน SOS ไปยัง Admin ภายใน 2.0 วินาที พร้อมพิกัดและข้อมูลซาเล้ง และปุ่มโทรด่วน `tel:` (`UC-09`, `REQ-QA-001`, `AC-S09-02`)
     - `P-03`: EmergencyContactService ตาราง `emergency_contacts` เก็บข้อมูลผู้ติดต่อฉุกเฉินที่ไว้ใจได้ พร้อม PDPA Masking `08X-XXX-XXXX` และเบอร์สายด่วน Saleng เป็น Default (`UC-09`, `REQ-SEC-002`, `AC-S09-03`)
     - `P-04`: Evidence Immutability ล็อกหลักฐานเป็น Read-only ทันทีเมื่อเกิดข้อพิพาท `S8` หรือกด SOS ตาม `REQ-FN-006` เพื่อส่งต่อให้ Admin ใน `UC-13` (`AC-S09-04`)
     - `P-05`: Security Audit Logging for Safety Events บันทึกประวัติการเริ่ม/หยุดอัดเสียง, กด SOS, และแก้เบอร์ฉุกเฉิน (`REQ-SEC-001`, `AC-S09-05`)
     - `P-06`: Mobile-First UI Architecture & Big SOS Button คอมโพเนนต์ React ปุ่ม SOS สีแดงเด่นชัด `height >= 48px` สำหรับจอมือถือ 375px–414px (`CC-01`, `REQ-UX-001`, `AC-S09-01..05`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` พร้อมระบุเหตุผลข้อที่ไม่เกี่ยวข้อง
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`
---

## บันทึก #40 — `/tasks specs/seller/09-transaction-safety/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/09-transaction-safety/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/09-transaction-safety/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S09-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบความปลอดภัย (`safety_evidences`, `emergency_contacts`, `sos_alerts`)
     - `T-02`: สร้าง Service และ API บันทึกเสียงและวิดีโอหลักฐานหน้างาน S4..S6 (`MediaEvidenceService`, `AC-S09-01`)
     - `T-03`: สร้าง Service และ API ส่งสัญญาณฉุกเฉิน SOS Dispatch < 2.0s (`EmergencySosService`, `AC-S09-02`)
     - `T-04`: สร้าง Service และ API ตั้งค่าเบอร์ผู้ติดต่อฉุกเฉิน พร้อม PDPA Masking `08X-XXX-XXXX` (`EmergencyContactService`, `AC-S09-03`)
     - `T-05`: สร้าง Service และ API ล็อกหลักฐานห้ามแก้ไขเมื่อมีข้อพิพาท/SOS (`lock_evidence_for_order`, `AC-S09-04`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชข้อมูลความปลอดภัยออฟไลน์ใน `localStorage` (`AC-S09-01..04`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ความปลอดภัยและปุ่ม SOS (`EmergencySosButton`, `SosConfirmationModal`, `MediaEvidenceRecorder`, `EmergencyContactModal`, `TransactionSafetyPanel`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S09-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S09-01` ถึง `AC-S09-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยแรก `/implement T-01`
---

## บันทึก #41 — `/implement T-01..08` (พัฒนาระบบความปลอดภัยขณะทำธุรกรรม Transaction Safety & SOS ครบวงจร)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/safety_models.py` (Pydantic models สำหรับ Evidence, Emergency Contact, SOS Alert, Lock Evidence)
  - `backend/app/core/supabase.py` (ขยาย Supabase store: `safety_evidences`, `emergency_contacts`, `sos_alerts`, ฟังก์ชัน `add_safety_evidence`, `lock_safety_evidences_for_order`, `upsert_emergency_contact`, `create_sos_alert`)
  - `backend/app/services/safety_service.py` (`MediaEvidenceService`, `EmergencySosService`, `EmergencyContactService`, `EvidenceLockService` พร้อม Audit Logging)
  - `backend/app/api/v1/safety.py` (FastAPI Router สำหรับ endpoints บันทึกหลักฐาน, ดึงหลักฐาน, ส่ง SOS, จัดการเบอร์ฉุกเฉิน, และล็อกหลักฐาน)
  - `backend/app/api/v1/pricing.py` (ลงทะเบียน `safety_router`)
  - `frontend/src/services/safetyApi.js` (Frontend API Client พร้อมระบบ LocalStorage Caching สำหรับเบอร์ติดต่อฉุกเฉินและข้อมูลสายด่วนเมื่อออฟไลน์ CC-05, REQ-OP-001)
  - `frontend/src/components/EmergencySosButton.jsx` (ปุ่ม SOS ฉุกเฉิน สีแดงสะดุดตา ขนาดใหญ่ min-h-[48px] REQ-UX-001, data-req="UC-09")
  - `frontend/src/components/SosConfirmationModal.jsx` (หน้าต่างยืนยันการส่งสัญญาณฉุกเฉิน แสดงพิกัดบ้านและปุ่มโทรออกด่วน tel: data-req="UC-09")
  - `frontend/src/components/MediaEvidenceRecorder.jsx` (แผงอัดเสียง/วิดีโอหน้างาน S4..S6 มีตัวจับเวลา คลื่นเสียง Waveform ปุ่มเริ่ม/หยุด และรายการหลักฐาน data-req="UC-09")
  - `frontend/src/components/EmergencyContactModal.jsx` (ฟอร์มตั้งค่าเบอร์ผู้ติดต่อฉุกเฉิน พร้อมแสดงผล PII Masking 08X-XXX-XXXX data-req="UC-09")
  - `frontend/src/components/TransactionSafetyPanel.jsx` (แผงรวมระบบความปลอดภัยขณะทำธุรกรรม Mobile-First SPA data-req="UC-09")
  - `backend/tests/test_T01_safety_models.py` (Unit tests สำหรับ Pydantic Models และ Supabase Store: 3 passed)
  - `backend/tests/test_AC_S09_01_media_evidence.py` (Backend test สำหรับ AC-S09-01: 3 passed)
  - `backend/tests/test_AC_S09_02_emergency_sos.py` (Backend test สำหรับ AC-S09-02: 2 passed)
  - `backend/tests/test_AC_S09_03_emergency_contact.py` (Backend test สำหรับ AC-S09-03: 1 passed)
  - `backend/tests/test_AC_S09_04_evidence_immutability.py` (Backend test สำหรับ AC-S09-04: 1 passed)
  - `backend/tests/test_e2e_transaction_safety.py` (Backend E2E Integration test สำหรับ AC-S09-01..05: 1 passed)
  - `frontend/tests/safetyApi.test.mjs` (Frontend API & Offline Cache test: 5 passed)
  - `frontend/tests/AC-S09-01.test.jsx` (Vitest UI Component test: 2 passed)
  - `frontend/tests/AC-S09-02.test.jsx` (Vitest UI Component test: 2 passed)
  - `frontend/tests/AC-S09-03.test.jsx` (Vitest UI Component test: 1 passed)
  - `frontend/tests/AC-S09-04.test.jsx` (Vitest UI Component test: 1 passed)
  - `specs/seller/09-transaction-safety/tasks.md` (อัปเดตสถานะงาน `T-01` ถึง `T-08` เป็น `[DONE]` และอัปเดตสถานะรวมเป็น `completed`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดไว้ใน `tasks.md` (T-01 ถึง T-08)
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`26 files passed, 66 passed in 1.95s`** (ผ่าน 100% ครอบคลุม UI Components และ Offline Cache)
     - รัน `pytest backend/tests/` (Pytest): **`78 passed in 0.31s`** (ผ่าน 100% ครอบคลุม Unit, AC, และ E2E Lifecycle)
     - **ยอดรวมทั้งระบบ: 144 tests ผ่านทั้งหมด 100% (Backend 78 + Frontend 66)**
  3. **การอ้างอิง ID:** ฟังก์ชัน คอมโพเนนต์ และชุดทดสอบทุกไฟล์ระบุรหัส `UC-09`, `UC-13`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-QA-001`, `REQ-UX-001`, `REQ-FN-006`, `CC-01..06`, `AC-S09-01..05`, `P-01..P-06`, `T-01..T-08` ครบถ้วนตามกฎของ `AGENTS.md`
  4. **Non-goals & Open Questions:** ขอบเขตตรงตามสเปก v2.0 ไม่ทำ AI Audio Surveillance ดักฟังอัตโนมัติ, ไม่ทำ in-app VoIP calling, และไม่เชื่อมต่อ API ตำรวจ 191 โดยตรง
  5. **การบันทึกสถานะ:** อัปเดตงานย่อย `T-01..T-08` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #42 — `/clarify specs/seller/01-account-and-access/spec.md` (การตรวจสอบความสอดคล้องกับสารบัญกลางและการขยายสเปก v2.0)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/clarify specs/seller/01-account-and-access/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/01-account-and-access/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify`, ปรับ Use Case เป็น `UC-01`, เชื่อมโยง `REQ-SEC-001`, `REQ-SEC-002`, `REQ-UX-001/002`, `REQ-QA-001`, `REQ-OP-001`, หลักฐาน `EV-08`, `EV-09`, `DR-02`, `D-01`, ขยายเกณฑ์การยอมรับเป็น 5 ข้อ `AC-S01-01` ถึง `AC-S01-05`, และกำหนด Non-goals ชัดเจน)
- **ประเด็นสำคัญที่ทีมเห็นชอบ:**
  1. **`CC-01` (Use Case Alignment):** แก้ไขรหัส Use Case ให้สอดคล้องกับสารบัญกลางใน `docs/srs/use-cases.md` เป็น **`UC-01: ลงทะเบียน เข้าสู่ระบบ และยืนยันตัวตน (KYC / บัญชีผู้ใช้) ฝั่งผู้ขาย`** โดยกำหนดให้การมีบัญชีและที่อยู่นัดหมาย (`PickupLocation`) เป็น Precondition ก่อนการสร้างคำขอใน `UC-02`
  2. **`CC-02` (Requirements Catalogue & Evidence Mapping):** ปลดรหัส `CT-01` และเชื่อมโยงรหัสกลาง `REQ-SEC-001` (Audit Log), `REQ-SEC-002` (PDPA Masking & PII Protection), `REQ-UX-001/002` (Mobile-First SPA), `REQ-QA-001` (< 2.0s), `REQ-OP-001` (Offline Persistence) และหลักฐาน `EV-08`, `EV-09`, `DR-02`
  3. **`CC-03` (State Machine Preconditions):** การมีบัญชีผู้ขายที่เข้าสู่ระบบและมีที่อยู่นัดหมายอย่างน้อย 1 รายการ เป็นเงื่อนไขจำเป็นก่อนเปลี่ยนสถานะคำขอจาก `S1 (Draft)` สู่ `S2 (Pending/Open)`
  4. **มติในคำถามเปิด `Q-01` ถึง `Q-05` (เลือกทางเลือก A ทั้งหมด):**
     - `Q-01` (Authentication Mechanism): ใช้เบอร์โทรศัพท์มือถือ + OTP verification 6 หลัก (Option A)
     - `Q-02` (Pickup Location Input): รองรับทั้งปุ่มดึงพิกัด GPS ปัจจุบันและฟอร์มระบุตำบล/แขวงและบ้านเลขที่ (Option A)
     - `Q-03` (Multiple Pickup Locations): รองรับการบันทึกที่อยู่นัดหมายหลายแห่งและกำหนดเป็นที่อยู่เริ่มต้น (Default Location) ได้ (Option A)
     - `Q-04` (PDPA & PII Protection): แสดงเบอร์โทรศัพท์แบบ Masking `08X-XXX-XXXX` และแยกฟิลด์ `subDistrict` ออกจาก `addressText` และ `geoPoint` อย่างชัดเจน (Option A)
     - `Q-05` (Non-goals): ไม่ทำ KYC บัตรประชาชนผู้ขาย (D-01), ไม่ทำ Social Login ภายนอก, ไม่ทำระบบกู้คืนบัญชีข้ามเบอร์โทรศัพท์ (Option A)
- **สถานะ:** สเปก `spec.md` ได้รับการรับรองและอัปเดตเป็น Version 2.0 (`reviewed-post-clarify`) พร้อมสำหรับขั้นตอน `/plan`

---

## บันทึก #43 — `/plan specs/seller/01-account-and-access/spec.md` (แผนสถาปัตยกรรม เทคโนโลยี และการปฏิบัติตาม Constraints ครบทั้ง 13 ข้อ)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/01-account-and-access/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/01-account-and-access/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรม Service Layer, กำหนดการตัดสินใจ `P-01` ถึง `P-06`, กำหนด DDL Schema และ Pydantic Models, ออกแบบ API 11 เส้นทาง, แผนพัฒนาหน้าจอ 5 คอมโพเนนต์, และตารางตรวจสอบ Constraints ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (FastAPI, Supabase/PostgreSQL, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **การตัดสินใจเชิงสถาปัตยกรรม (`P-01` ถึง `P-06`):**
     - `P-01`: บริการ OTP Phone Authentication ออก Session Token 30 วัน ตอบสนอง `< 2.0 วินาที` (`AC-S01-01`)
     - `P-02`: บริการจัดการที่อยู่นัดหมาย `PickupLocationService` และ GPS Pinning (`AC-S01-02`)
     - `P-03`: ฟังก์ชัน Masking เบอร์โทรศัพท์ `08X-XXX-XXXX` และแยกฟิลด์ `sub_district` ออกจาก `address_text` (`AC-S01-03`)
     - `P-04`: การคงสภาพ Token และแคชข้อมูลที่อยู่ใน `localStorage` เมื่อออฟไลน์ (`AC-S01-04`, `CC-05`, `REQ-OP-001`)
     - `P-05`: การบันทึก Audit Log แบบ Append-only ทุกเหตุการณ์สำคัญ (`AC-S01-05`, `REQ-SEC-001`)
     - `P-06`: Precondition Readiness สำหรับส่งต่อที่อยู่นัดหมายเริ่มต้นไปยังการสร้างคำขอใน `UC-02`
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` พร้อมระบุเหตุผลข้อที่ไม่เกี่ยวข้อง
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`

---

## บันทึก #44 — `/tasks specs/seller/01-account-and-access/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/01-account-and-access/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/01-account-and-access/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S01-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบบัญชีและที่อยู่นัดหมาย (`account_models.py`, `supabase.py`)
     - `T-02`: สร้าง Service และ API สำหรับลงทะเบียนและเข้าสู่ระบบด้วยเบอร์โทรศัพท์และ OTP (`SellerAuthService`, `AC-S01-01`)
     - `T-03`: สร้าง Service และ API สำหรับจัดการที่อยู่นัดหมายและพิกัด GPS (`PickupLocationService`, `AC-S01-02`, `P-06`)
     - `T-04`: สร้าง Service และ API สำหรับคุ้มครองข้อมูลส่วนบุคคลและ Masking เบอร์โทรศัพท์ `08X-XXX-XXXX` (`AC-S01-03`)
     - `T-05`: สร้าง Service ตรวจสอบความถูกต้องของเซสชันและการบันทึก Audit Log (`AC-S01-04`, `AC-S01-05`, `REQ-SEC-001`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชข้อมูลบัญชีและที่อยู่ออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบบัญชีและการเข้าใช้งาน (`PhoneOtpLoginForm`, `SellerProfileCard`, `PickupLocationList`, `PickupLocationModal`, `AccountAccessPanel`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S01-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S01-01` ถึง `AC-S01-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #45 — `/implement T-01..08` (พัฒนาระบบบัญชีและการเข้าใช้งานของผู้ขาย Seller Account & Access ครบวงจร)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/account_models.py` (Pydantic models: `OtpRequest`, `OtpRequestResponse`, `OtpVerifyRequest`, `AuthSessionResponse`, `SellerProfileResponse`, `SellerProfileUpdateRequest`, `GeoPoint`, `PickupLocationCreateRequest`, `PickupLocationUpdateRequest`, `PickupLocationResponse`, `PickupLocationListResponse`, ฟังก์ชัน `mask_phone_number`)
  - `backend/app/core/supabase.py` (ขยาย Supabase store: `sellers`, `seller_otps`, `seller_sessions`, `pickup_locations` พร้อม CRUD และการจัดการ Default Location, ปรับ `add_audit_log` ให้ยืดหยุ่น)
  - `backend/app/services/account_service.py` (`SellerAuthService`, `PickupLocationService`, `verify_seller_session` พร้อม Audit Logging ทุกเหตุการณ์)
  - `backend/app/api/v1/account.py` (FastAPI Router สำหรับ endpoints ขอ OTP, ยืนยัน OTP, โปรไฟล์, ที่อยู่นัดหมาย, และออกจากระบบ)
  - `backend/app/api/v1/pricing.py` (ลงทะเบียน `account_router` ภายใต้ prefix `/api/v1`)
  - `frontend/src/services/accountApi.js` (Frontend API Client พร้อมระบบแคชลง `localStorage` สำหรับ Token, Profile, และ Locations เมื่อออฟไลน์ CC-05, REQ-OP-001)
  - `frontend/src/components/PhoneOtpLoginForm.jsx` (ฟอร์มขอ OTP และยืนยัน 6 หลัก มีตัวนับถอยหลัง Cooldown 60s REQ-UX-002, data-req="UC-01")
  - `frontend/src/components/SellerProfileCard.jsx` (การ์ดโปรไฟล์ผู้ขาย แสดงเบอร์โทรศัพท์ Masked 08X-XXX-XXXX และปุ่มแก้ไขชื่อ displayName data-req="UC-01")
  - `frontend/src/components/PickupLocationList.jsx` (รายการที่อยู่นัดหมาย แสดงป้าย Default Location ปุ่มแก้ไข/ลบ และปุ่มตั้งค่าเริ่มต้น data-req="UC-01")
  - `frontend/src/components/PickupLocationModal.jsx` (ป๊อปอัปเพิ่ม/แก้ไขที่อยู่ พร้อมปุ่มปักหมุด GPS ดึงตำแหน่งปัจจุบัน data-req="UC-01")
  - `frontend/src/components/AccountAccessPanel.jsx` (แผงรวมระบบบัญชีและที่อยู่ Mobile-First Dashboard data-req="UC-01")
  - `backend/tests/test_T01_account_models.py` (Unit tests สำหรับ Pydantic Models และ Supabase Store: 4 passed)
  - `backend/tests/test_AC_S01_01_seller_auth.py` (Backend test สำหรับ AC-S01-01: 3 passed)
  - `backend/tests/test_AC_S01_02_pickup_locations.py` (Backend test สำหรับ AC-S01-02: 1 passed)
  - `backend/tests/test_AC_S01_03_pii_masking.py` (Backend test สำหรับ AC-S01-03: 2 passed)
  - `backend/tests/test_AC_S01_04_session_persistence.py` (Backend test สำหรับ AC-S01-04: 1 passed)
  - `backend/tests/test_AC_S01_05_audit_logging.py` (Backend test สำหรับ AC-S01-05: 1 passed)
  - `backend/tests/test_e2e_account_and_access.py` (Backend E2E Integration test สำหรับ AC-S01-01..05: 1 passed)
  - `frontend/tests/accountApi.test.mjs` (Frontend API & Offline Cache test: 4 passed)
  - `frontend/tests/AC-S01-01.test.jsx` (Vitest UI Component test: 2 passed)
  - `frontend/tests/AC-S01-02.test.jsx` (Vitest UI Component test: 2 passed)
  - `frontend/tests/AC-S01-03.test.jsx` (Vitest UI Component test: 2 passed)
  - `specs/seller/01-account-and-access/tasks.md` (อัปเดตสถานะงาน `T-01` ถึง `T-08` เป็น `[DONE]` และอัปเดตสถานะรวมเป็น `completed`)
- **ผลการตรวจ 5 ข้อหลังจบ Task:**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดไว้ใน `tasks.md` (T-01 ถึง T-08)
  2. **ผลการรัน Test:**
     - รัน `npm test --prefix frontend` (Vitest): **`30 files passed, 76 passed in 2.21s`** (ผ่าน 100% ครอบคลุม UI Components และ Offline Cache)
     - รัน `pytest backend/tests/` (Pytest): **`91 passed in 0.59s`** (ผ่าน 100% ครอบคลุม Unit, AC, และ E2E Lifecycle)
     - **ยอดรวมทั้งระบบ: 167 tests ผ่านทั้งหมด 100% (Backend 91 + Frontend 76)**
  3. **การอ้างอิง ID:** ฟังก์ชัน คอมโพเนนต์ และชุดทดสอบทุกไฟล์ระบุรหัส `UC-01`, `UC-02`, `MD-DOM-04`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-UX-001/002`, `REQ-QA-001`, `REQ-OP-001`, `CC-01..06`, `AC-S01-01..05`, `P-01..P-06`, `T-01..T-08` ครบถ้วนตามกฎของ `AGENTS.md`
  4. **Non-goals & Open Questions:** ขอบเขตตรงตามสเปก v2.0 ไม่ทำ KYC บัตรประชาชนผู้ขาย (D-01), ไม่ทำ Social Login, และไม่ทำระบบกู้คืนบัญชีข้ามเบอร์
  5. **การบันทึกสถานะ:** อัปเดตงานย่อย `T-01..T-08` เป็น `[DONE]` ใน `tasks.md` และบันทึกลง `prompt-log.md` เรียบร้อย

---

## บันทึก #46 — `/clarify specs/seller/02-scrap-posting/spec.md` (การตรวจสอบความสอดคล้องกับสารบัญกลางและการขยายสเปก v2.0)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/clarify specs/seller/02-scrap-posting/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/02-scrap-posting/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify`, ปรับ Use Case เป็น `UC-02`, เชื่อมโยง `Card 03`, `REQ-UX-002`, `REQ-FN-003`, `REQ-FN-004`, `REQ-DAT-001`, `REQ-SEC-001`, หลักฐาน `EV-01`, `EV-03`, `EV-08`, ขยายเกณฑ์การยอมรับเป็น 5 ข้อ `AC-S02-01` ถึง `AC-S02-05`, และกำหนด Non-goals ชัดเจน)
- **ประเด็นสำคัญที่ทีมเห็นชอบ:**
  1. **`CC-01` (Use Case Alignment):** แก้ไขรหัส Use Case ให้สอดคล้องกับสารบัญกลางใน `docs/srs/use-cases.md` เป็น **`UC-02: โพสต์ขายของเก่า ประเมินน้ำหนัก และอัปโหลดรูปถ่าย`** ซึ่งครอบคลุมคู่มือภาพ, การประเมินราคาของชิ้นใหญ่เหมาจ่ายและวัสดุบรรจุลังตาม Card 03, การอัปโหลดรูปถ่าย, และบริการขอคนช่วยยก
  2. **`CC-02` (Requirements Catalogue & Evidence Mapping):** ปลดรหัส `EV-008` และ `EV-011` ที่อยู่นอกสารบัญ และเชื่อมโยงรหัสกลาง `REQ-UX-002` (Visual Scrap Guide), `REQ-FN-003` (Bulky & Boxed Items), `REQ-FN-004` (Photos & Lifting Help), `REQ-DAT-001`, `REQ-SEC-001` และหลักฐาน `EV-01`, `EV-03`, `EV-08`, และ `Card 03`
  3. **`CC-03` (State Machine & Preconditions):** การโพสต์ขายของเก่าทำงานในสถานะ `S1 (Draft)` โดยผูกกับที่อยู่นัดหมายเริ่มต้นของผู้ขายจาก `UC-01` อัตโนมัติเป็น Precondition ก่อนส่งต่อเข้าสู่การคำนวณและตรวจสอบเกณฑ์ขั้นต่ำใน `UC-04 / S2`
  4. **มติในคำถามเปิด `Q-01` ถึง `Q-05` (เลือกทางเลือก A ทั้งหมด):**
     - `Q-01` (Visual Scrap Guide & Category Hierarchy): จัดหมวดหมู่ 3 กลุ่มหลักชัดเจนพร้อมไอคอนและรูปตัวอย่าง (Option A)
     - `Q-02` (Missing Sub-Category Guard): บล็อกและแจ้งเตือนเมื่อเลือกของชิ้นใหญ่เหมาจ่ายแต่ไม่ระบุประเภทย่อย (Option A)
     - `Q-03` (Photo Upload Limits): แนบรูปได้สูงสุด 5 รูป (ขนาด <= 5 MB) พร้อม Thumbnail และปุ่มลบรูป (Option A)
     - `Q-04` (Lifting Help Request): มีตัวเลือกขอคนช่วยยกของหนัก พร้อมช่องระบุหมายเหตุ และติดป้ายสัญลักษณ์เตือนซาเล้ง (Option A)
     - `Q-05` (Non-goals): ไม่ทำ AI Computer Vision ตรวจจับรูปภาพ, ไม่คิดค่าบริการช่วยยกในรอบนี้, ไม่ทำประมูลราคา (Option A)
- **สถานะ:** สเปก `spec.md` ได้รับการรับรองและอัปเดตเป็น Version 2.0 (`reviewed-post-clarify`) พร้อมสำหรับขั้นตอน `/plan`

---

## บันทึก #47 — `/plan specs/seller/02-scrap-posting/spec.md` (แผนสถาปัตยกรรม เทคโนโลยี และการปฏิบัติตาม Constraints ครบทั้ง 13 ข้อ)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/plan specs/seller/02-scrap-posting/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/02-scrap-posting/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรม Service Layer, กำหนดการตัดสินใจ `P-01` ถึง `P-06`, กำหนด DDL Schema และ Pydantic Models, ออกแบบ API 8 เส้นทาง, แผนพัฒนาหน้าจอ 5 คอมโพเนนต์, และตารางตรวจสอบ Constraints ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (FastAPI, Supabase/PostgreSQL, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **การตัดสินใจเชิงสถาปัตยกรรม (`P-01` ถึง `P-06`):**
     - `P-01`: บริการ Catalog คู่มือภาพ 3 หมวดหลัก (`GENERAL_WEIGHT`, `BOXED_CRATE_ITEMS`, `BULKY_FLAT_RATE`) พร้อมช่วงราคาอ้างอิง (`AC-S02-01`)
     - `P-02`: บริการประเมินราคาของชิ้นใหญ่เหมาจ่าย พร้อม Missing Sub-Category Guard บล็อกเมื่อไม่ระบุประเภทย่อยตาม Card 03 (`AC-S02-02`, `AC-S02-03`)
     - `P-03`: บริการประเมินราคาวัสดุบรรจุลัง/กระสอบแยกเฉพาะ (`Card 03 Alt Case`, `AC-S02-02`)
     - `P-04`: บริการแนบรูปถ่ายของเก่าสูงสุด 5 รูป (ขนาด <= 5 MB) พร้อมภาพตัวอย่าง Thumbnail (`AC-S02-04`)
     - `P-05`: บริการบันทึกตัวเลือกขอคนช่วยยกของหนัก (`needLiftingHelp`) พร้อมข้อจำกัดหน้างาน และติดป้ายเตือนซาเล้ง (`AC-S02-05`)
     - `P-06`: บริการสร้างฉบับร่างคำขอ `S1 Draft` ผูกกับที่อยู่นัดหมายเริ่มต้นจาก `UC-01` เป็น Precondition
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` พร้อมระบุเหตุผลข้อที่ไม่เกี่ยวข้อง
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`

---

## บันทึก #48 — `/tasks specs/seller/02-scrap-posting/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/tasks specs/seller/02-scrap-posting/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/02-scrap-posting/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S02-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบโพสต์ขายของเก่า (`scrap_posting_models.py`, `supabase.py`)
     - `T-02`: สร้าง Service และ API สำหรับคู่มือภาพและการคำนวณราคา 3 หมวดหลัก (`AC-S02-01`, `P-01`)
     - `T-03`: สร้าง Service และ API สำหรับของชิ้นใหญ่เหมาจ่าย และ Missing Sub-Category Guard ตาม Card 03 (`AC-S02-02`, `AC-S02-03`, `P-02`, `P-03`)
     - `T-04`: สร้าง Service และ API สำหรับแนบรูปถ่ายของเก่าและตรวจสอบขีดจำกัดไฟล์ (สูงสุด 5 รูป, <= 5 MB) (`AC-S02-04`, `P-04`)
     - `T-05`: สร้าง Service และ API สำหรับตัวเลือกขอคนช่วยยกของหนักและหมายเหตุหน้างาน (`AC-S02-05`, `P-05`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชฉบับร่างออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบโพสต์ขายของเก่า (`VisualScrapGuide`, `BulkyItemSelector`, `PhotoUploadManager`, `LiftingHelpToggle`, `ScrapPostingPanel`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S02-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S02-01` ถึง `AC-S02-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`


---

## บันทึก #49 — `/implement T-01..08` (พัฒนาระบบโพสต์ขายของเก่าของผู้ขาย Seller Feature 02 ครบถ้วน 100%)
- **วันที่:** 2026-11-03
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/seller/02-scrap-posting/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Store (`T-01`):**
    - `backend/app/models/scrap_posting_models.py` (สร้าง Pydantic models: `ScrapCategoryResponse`, `CategoryCatalogResponse`, `WasteItemCreateRequest`, `WasteItemResponse`, `LiftingHelpUpdateRequest`, `DraftOrderCreateRequest`, `DraftOrderResponse`)
    - `backend/app/core/supabase.py` (ขยายตาราง `scrap_categories`, `waste_pickup_orders`, `waste_items` พร้อม Seed ข้อมูลคู่มือภาพ 3 หมวดหมู่ และรองรับ positional/keyword argument ใน `add_audit_log`)
    - `backend/tests/test_T01_scrap_posting_models.py` (Unit tests สำหรับ Pydantic validation และ Supabase seeding)
  - **Backend Service & API (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/scrap_posting_service.py` (จัดการ Visual Scrap Guide, ตะกร้าของเก่า, การคิดราคาเหมาตู้เย็น 200–300 บ. ตาม Card 03, Guard แจ้งเตือนเมื่อไม่ระบุประเภทย่อยของชิ้นใหญ่, การแนบรูปถ่ายไม่เกิน 5 รูป/ไม่เกิน 5 MB, การขอคนช่วยยกพร้อมหมายเหตุหน้างาน, และการบันทึก Audit Logs)
    - `backend/app/api/v1/scrap_posting.py` (FastAPI router ให้บริการ 8 endpoints: `GET /categories`, `POST /drafts`, `GET /drafts/{id}`, `POST /drafts/{id}/items`, `DELETE /drafts/{id}/items/{item_id}`, `POST /drafts/{id}/items/{item_id}/photos`, `DELETE /drafts/{id}/items/{item_id}/photos/{photo_idx}`, `PATCH /drafts/{id}/lifting-help`)
    - `backend/app/api/v1/pricing.py` (รวมและเมานต์ scrap_posting router)
  - **Backend Automated Tests:**
    - `backend/tests/test_AC_S02_01_visual_scrap_guide.py` (ทดสอบหมวดหมู่คู่มือภาพและราคาประเมิน)
    - `backend/tests/test_AC_S02_02_bulky_and_boxed_items.py` (ทดสอบราคาเหมาตู้เย็นและวัสดุบรรจุลังตาม Card 03)
    - `backend/tests/test_AC_S02_03_missing_bulky_sub_category.py` (ทดสอบ Missing Sub-Category Guard บล็อก HTTP 422)
    - `backend/tests/test_AC_S02_04_photo_attachment.py` (ทดสอบการแนบรูปถ่ายสูงสุด 5 รูปและจำกัดขนาด 5 MB)
    - `backend/tests/test_AC_S02_05_lifting_help_badge.py` (ทดสอบตัวเลือกขอคนช่วยยกและป้ายเตือนซาเล้ง)
    - `backend/tests/test_e2e_scrap_posting.py` (E2E Integration test ครบวงจรตั้งแต่ S1 Draft จนถึง Audit Log)
  - **Frontend API Client & Components (`T-06`, `T-07`):**
    - `frontend/src/services/scrapPostingApi.js` (API client พร้อม fallback แคชออฟไลน์ใน localStorage: `saleng_draft_order`)
    - `frontend/tests/scrapPostingApi.test.mjs` (Unit test สำหรับ API client)
    - `frontend/src/components/VisualScrapGuide.jsx` (แท็บ 3 หมวดหมู่ ไอคอนใหญ่ แตะเลือกง่ายไม่ต้องพิมพ์ `REQ-UX-002`)
    - `frontend/src/components/BulkyItemSelector.jsx` (ตัวเลือกชิ้นใหญ่เหมาจ่าย พร้อม Guard แสดงกล่องแจ้งเตือนสีแดงเมื่อไม่เลือกประเภทย่อย)
    - `frontend/src/components/PhotoUploadManager.jsx` (อัปโหลดรูป แสดง Thumbnail สูงสุด 5 รูป และปุ่มลบรูป)
    - `frontend/src/components/LiftingHelpToggle.jsx` (ช่องติ๊กขอคนช่วยยก กล่องระบุหมายเหตุหน้างาน และป้ายเตือน `⚠️ ขอคนช่วยยก`)
    - `frontend/src/components/ScrapPostingPanel.jsx` (แผงหลักรวมตะกร้า คำนวณราคาประเมินรวม Min-Max และผูกกับที่อยู่นัดหมายเริ่มต้น)
  - **Frontend Automated Tests (`T-08`):**
    - `frontend/tests/AC-S02-01.test.jsx` (Component test สำหรับ VisualScrapGuide)
    - `frontend/tests/AC-S02-02.test.jsx` (Component test สำหรับ BulkyItemSelector และ Guard)
    - `frontend/tests/AC-S02-04.test.jsx` (Component test สำหรับ PhotoUploadManager)
    - `frontend/tests/AC-S02-05.test.jsx` (Component test สำหรับ LiftingHelpToggle)
  - **Task Tracking:**
    - `specs/seller/02-scrap-posting/tasks.md` (ปรับสถานะเป็น `completed` และเช็คผ่าน `[DONE]` ครบทุกงาน `T-01` ถึง `T-08`)
- **ผลการทดสอบ (Verification & Regression):**
  - **Backend (Pytest):** 102 passed, 0 failed (ครอบคลุมทั้ง Seller 01, Seller 02, Seller 04, 06, 07, 08, 09, และระบบส่วนกลาง)
  - **Frontend (Vitest):** 35 test files passed, 87 tests passed, 0 failed (รวมทุกคอมโพเนนต์และ API tests)
  - **Zero Regressions:** ไม่พบผลกระทบต่อฟีเจอร์เดิมของระบบ
- **สถานะ:** ฟีเจอร์ Seller 02 พัฒนาและตรวจสอบคุณภาพเสร็จสมบูรณ์ 100% พร้อมใช้งาน


---

## บันทึก #50 — `/clarify specs/seller/03-buyer-search-and-selection/spec.md` (การตรวจสอบความสอดคล้องกับสารบัญกลางและการขยายสเปก v2.0)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/seller/03-buyer-search-and-selection/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/03-buyer-search-and-selection/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify`, ปรับ Use Case เป็น `UC-03`, เชื่อมโยง `REQ-FN-001`, `REQ-QA-001`, `REQ-UX-001`, `REQ-SEC-001`, `REQ-SEC-002`, `CC-03`, `Card 03`, หลักฐาน `EV-01`, `EV-02`, `EV-08`, `EV-09`, ขยายเกณฑ์การยอมรับเป็น 5 ข้อ `AC-S03-01` ถึง `AC-S03-05`, และบันทึกมติ `Q-01..05` พร้อม Non-goals ชัดเจน)
- **ประเด็นสำคัญที่ทีมเห็นชอบ:**
  1. **`CC-01` (Use Case Alignment):** กำหนด Use Case เป็น **`UC-03: ค้นหา เลือกผู้รับซื้อ และยืนยันนัดหมายพร้อมล็อกราคากลาง`** ตามสารบัญกลางใน `docs/srs/use-cases.md`
  2. **`CC-02` (Requirements Catalogue & Evidence Mapping):** แก้ไขรหัสความต้องการเป็น `REQ-FN-001` (ค้นหาในรัศมี <= 5 กม.), `REQ-QA-001` (KYC Verified), `REQ-UX-001` (Top Pinning Favorites), `REQ-SEC-001` (Audit Log), `REQ-SEC-002` (PDPA Masking) และเชื่อมโยงหลักฐาน `EV-01`, `EV-02`, `EV-08`, `EV-09` ครบถ้วน
  3. **`CC-03` (State Machine & Preconditions):** ฟีเจอร์นี้เชื่อมโยงจากฉบับร่าง `S1 (Draft)` ที่มีรายการของเก่าจาก `UC-02` และที่อยู่นัดหมายจาก `UC-01` เพื่อส่งคำขอนัดหมายแบบเจาะจงบุคคล (Direct Request) และเปลี่ยนผ่านสถานะสู่ `S2 (Matched / Pending)`
  4. **มติในคำถามเปิด `Q-01` ถึง `Q-05` (เลือกทางเลือก A ทั้งหมด):**
     - `Q-01` (Direct Request vs Open Broadcast): ส่งคำขอแบบ Direct Request ให้ซาเล้งที่เลือกก่อนพร้อมเวลารอตอบรับ 15 นาที หากปฏิเสธหรือหมดเวลาให้เลือกคนใหม่หรือเปิดเป็น Open Broadcast (Option A)
     - `Q-02` (Sorting Logic): ตรึง "ซาเล้งที่เคยใช้บริการ" ไว้บนสุด (`REQ-UX-001`) จากนั้นเรียงตามระยะทางใกล้ที่สุด (`Distance ASC`) และคะแนนรีวิว (`Rating DESC`) (Option A)
     - `Q-03` (Bulky Items Matching): ตรวจจับของชิ้นใหญ่ในตะกร้าอัตโนมัติ และแนะนำ/กรองเฉพาะซาเล้งที่มีรถกระบะหรือซาเล้งขนาดใหญ่ตาม `Card 03` (Option A)
     - `Q-04` (PDPA Protection): ผู้ขายโทรสอบถามซาเล้งได้ แต่ระบบต้องซ่อนบ้านเลขที่และพิกัดละเอียดของผู้ขายจนกว่าซาเล้งจะกดยืนยันรับงาน (Option A)
     - `Q-05` (Non-goals): ไม่ทำระบบ In-App VoIP, ไม่ทำประมูลราคาค่าเดินทาง, และไม่แสดงซาเล้ง Offline / Unverified (Option A)
- **สถานะ:** สเปก `spec.md` ได้รับการรับรองและอัปเดตเป็น Version 2.0 (`reviewed-post-clarify`) พร้อมสำหรับขั้นตอน `/plan`


---

## บันทึก #51 — `/plan specs/seller/03-buyer-search-and-selection/spec.md` (แผนสถาปัตยกรรม เทคโนโลยี และการปฏิบัติตาม Constraints ครบทั้ง 13 ข้อ)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/seller/03-buyer-search-and-selection/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/03-buyer-search-and-selection/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรม Service Layer, กำหนดการตัดสินใจ `P-01` ถึง `P-06`, กำหนด DDL Schema และ Pydantic Models, ออกแบบ API 5 เส้นทาง, แผนพัฒนาหน้าจอ 5 คอมโพเนนต์, และตารางตรวจสอบ Constraints ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (FastAPI, Supabase/PostgreSQL, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **การตัดสินใจเชิงสถาปัตยกรรม (`P-01` ถึง `P-06`):**
     - `P-01`: บริการค้นหาซาเล้งที่ผ่าน KYC 100% พร้อมคำนวณระยะทาง Haversine × 1.35 ในรัศมี <= 5.0 กม. (`AC-S03-01`)
     - `P-02`: บริการตรึงรายชื่อซาเล้งที่เคยใช้บริการ (Pinned Favorites) ไว้บนสุดเสมอ (`AC-S03-02`, `REQ-UX-001`, `Q-02`)
     - `P-03`: บริการตรวจจับของชิ้นใหญ่ในคำขออัตโนมัติ และแนะนำ/กรองเฉพาะรถกระบะหรือซาเล้งขนาดใหญ่ (`Card 03`, `AC-S03-03`, `Q-03`)
     - `P-04`: บริการโทรด่วนและแชตข้อความ พร้อมคุ้มครองข้อมูลส่วนบุคคล ซ่อนบ้านเลขที่และพิกัดละเอียดของผู้ขาย (`REQ-SEC-002`, `CC-06`, `AC-S03-04`, `Q-04`)
     - `P-05`: บริการส่งคำขอนัดหมายเจาะจงบุคคล เปลี่ยนสถานะจาก S1 เป็น S2 พร้อมนับถอยหลัง 15 นาที และบันทึก Audit Log (`MD-STM-04`, `AC-S03-05`, `Q-01`)
     - `P-06`: แคชรายชื่อซาเล้งล่าสุดใน `localStorage` (`saleng_cached_collectors`) รองรับโหมดออฟไลน์ (`CC-05`, `REQ-OP-001`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเชื่อมโยงการตัดสินใจ `P-01` ถึง `P-06` ครบถ้วน
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #52 — `/tasks specs/seller/03-buyer-search-and-selection/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/seller/03-buyer-search-and-selection/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/03-buyer-search-and-selection/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S03-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบค้นหาและเลือกผู้รับซื้อ (`buyer_search_models.py`, `supabase.py`)
     - `T-02`: สร้าง Service และ API สำหรับค้นหาซาเล้งที่ผ่าน KYC และคำนวณระยะทาง Haversine × 1.35 ในรัศมี <= 5.0 กม. (`AC-S03-01`, `P-01`)
     - `T-03`: สร้าง Service และ API สำหรับตรึงซาเล้งที่เคยใช้บริการไว้บนสุด (`AC-S03-02`, `P-02`, `Q-02`)
     - `T-04`: สร้าง Service และ API สำหรับตัวกรองหลายมิติและการจับคู่ของชิ้นใหญ่ตาม Card 03 (`AC-S03-03`, `P-03`, `Q-03`)
     - `T-05`: สร้าง Service และ API สำหรับช่องทางติดต่อด่วนและส่งคำขอนัดหมายเจาะจงบุคคล เปลี่ยนสถานะ S2 พร้อม Audit Log (`AC-S03-04`, `AC-S03-05`, `P-04`, `P-05`, `Q-01`, `Q-04`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชซาเล้งออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบค้นหาและเลือกผู้รับซื้อ (`SalengProfileCard`, `FavoriteCollectorPinList`, `CollectorFilterPanel`, `DirectRequestModal`, `BuyerSearchPanel`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S03-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S03-01` ถึง `AC-S03-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`


---

## บันทึก #53 — `/implement T-01..08` (พัฒนาระบบค้นหาและเลือกผู้รับซื้อ Seller Feature 03 ครบถ้วน 100%)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/seller/03-buyer-search-and-selection/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Store (`T-01`):**
    - `backend/app/models/buyer_search_models.py` (สร้าง Pydantic models: `SalengProfileResponse`, `CollectorSearchQuery`, `CollectorListResponse`, `DirectAppointmentRequest`, `DirectAppointmentResponse`, `FavoriteToggleResponse`)
    - `backend/app/core/supabase.py` (ขยายตาราง `saleng_profiles` พร้อม Seed ข้อมูลซาเล้ง KYC 100%, พิกัด GPS, ยานพาหนะ, และระบบรายการโปรด `seller_favorites`)
    - `backend/tests/test_T01_buyer_search_models.py` (Unit tests สำหรับ Pydantic validation และ Supabase seeding)
  - **Backend Service & API (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/buyer_search_service.py` (คำนวณระยะทาง Haversine × 1.35 รัศมี <= 5.0 กม. CC-03, คัดกรองเฉพาะ KYC 100% Online, Two-tier Sorting ตรึงคนโปรดไว้บนสุด, ตรวจจับของชิ้นใหญ่ในตะกร้าอัตโนมัติ Card 03, และส่ง Direct Request เปลี่ยนสถานะ S1 -> S2 พร้อมบันทึก Audit Log)
    - `backend/app/api/v1/buyer_search.py` (FastAPI router ให้บริการ 5 endpoints: `GET /collectors`, `GET /collectors/{saleng_id}`, `GET /favorites`, `POST /favorites/{saleng_id}/toggle`, `POST /orders/{order_id}/direct-request`)
    - `backend/app/api/v1/pricing.py` (เมานต์ buyer_search_router เข้ากับแอปพลิเคชันหลัก)
  - **Backend Automated Tests:**
    - `backend/tests/test_AC_S03_01_profile_and_kyc.py` (ทดสอบการแสดงโปรไฟล์และป้ายยืนยันตัวตน 100%)
    - `backend/tests/test_AC_S03_02_top_pinning_favorites.py` (ทดสอบการตรึงซาเล้งคนโปรดไว้บนสุดเสมอ)
    - `backend/tests/test_AC_S03_03_multi_criteria_filter.py` (ทดสอบตัวกรองยานพาหนะและแบนเนอร์ของชิ้นใหญ่)
    - `backend/tests/test_AC_S03_04_direct_contact_pdpa.py` (ทดสอบเบอร์โทรซาเล้งและการซ่อนพิกัดละเอียดของผู้ขาย)
    - `backend/tests/test_AC_S03_05_direct_request_transition.py` (ทดสอบการส่งคำขอเจาะจงบุคคล การเปลี่ยนสถานะ S2 และ Audit Log)
    - `backend/tests/test_e2e_buyer_search.py` (E2E Integration test ครบวงจรตั้งแต่ค้นหา กรอง สลับคนโปรด สู่ S2)
  - **Frontend API Client & Components (`T-06`, `T-07`):**
    - `frontend/src/services/buyerSearchApi.js` (API client พร้อมระบบแคชออฟไลน์ใน localStorage: `saleng_cached_collectors`)
    - `frontend/tests/buyerSearchApi.test.mjs` (Unit tests สำหรับ API client และ Offline cache: 3 passed)
    - `frontend/src/components/SalengProfileCard.jsx` (การ์ดซาเล้ง แสดงรูป ป้าย KYC 100% สถิติ ยานพาหนะ ปุ่มโทรด่วน แชต และปุ่มเลือกซาเล้ง)
    - `frontend/src/components/FavoriteCollectorPinList.jsx` (แถบแนวนอนตรึงซาเล้งที่เคยใช้บริการไว้บนสุด)
    - `frontend/src/components/CollectorFilterPanel.jsx` (ชิปตัวกรองรัศมี ยานพาหนะ คะแนนรีวิว และแบนเนอร์แจ้งเตือนของชิ้นใหญ่ Card 03)
    - `frontend/src/components/DirectRequestModal.jsx` (ป๊อปอัปยืนยันการส่งคำขอนัดหมายเจาะจงบุคคล พร้อมเวลานับถอยหลัง 15 นาที)
    - `frontend/src/components/BuyerSearchPanel.jsx` (แผงหลัก Mobile-First Dashboard รวบรวมฟังก์ชันค้นหาทั้งหมด)
  - **Frontend Automated Tests (`T-08`):**
    - `frontend/tests/AC-S03-01.test.jsx` (Component test สำหรับ SalengProfileCard และ KYC Badge: 2 passed)
    - `frontend/tests/AC-S03-02.test.jsx` (Component test สำหรับ FavoriteCollectorPinList: 2 passed)
    - `frontend/tests/AC-S03-03.test.jsx` (Component test สำหรับ CollectorFilterPanel: 2 passed)
    - `frontend/tests/AC-S03-04.test.jsx` (Component test สำหรับ Direct Contact hooks: 2 passed)
    - `frontend/tests/AC-S03-05.test.jsx` (Component test สำหรับ DirectRequestModal: 2 passed)
  - **Task Tracking:**
    - `specs/seller/03-buyer-search-and-selection/tasks.md` (ปรับสถานะเป็น `completed` และเช็คผ่าน `[DONE]` ครบทุกงาน `T-01` ถึง `T-08`)
- **ผลการทดสอบ (Verification & Regression):**
  - **Backend (Pytest):** 116 passed, 0 failed (รวมทุกชุดทดสอบของ Seller 01, 02, 03, 04, 06, 07, 08, 09)
  - **Frontend (Vitest):** 41 test files passed, 100 tests passed, 0 failed
  - **Zero Regressions:** ไม่พบผลกระทบต่อฟีเจอร์เดิมของระบบ
- **สถานะ:** ฟีเจอร์ Seller 03 พัฒนาและตรวจสอบคุณภาพเสร็จสมบูรณ์ 100% พร้อมใช้งาน


---

## บันทึก #54 — `/clarify specs/seller/05-booking-and-status-tracking/spec.md` (การตรวจสอบความสอดคล้องกับสารบัญกลางและการขยายสเปก v2.0)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/seller/05-booking-and-status-tracking/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/05-booking-and-status-tracking/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify`, ปรับ Use Case เป็น `UC-04` ร่วมกับ `MD-STM-04`, เชื่อมโยงกฎธุรกิจ `BR-03`, `REQ-FN-003`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-UX-001`, `REQ-QA-001`, หลักฐาน `EV-01`, `EV-02`, `EV-08`, ขยายเกณฑ์การยอมรับเป็น 5 ข้อ `AC-S05-01` ถึง `AC-S05-05`, และบันทึกมติ `Q-01..05` พร้อม Non-goals ชัดเจน)
- **ประเด็นสำคัญที่ทีมเห็นชอบ:**
  1. **`CC-01` (Use Case Alignment):** ปรับรหัส Use Case ให้สอดคล้องกับสารบัญกลางใน `docs/srs/use-cases.md` เป็น **`UC-04: จัดการคิวงาน คำนวณเส้นทางรับซื้อ และติดตามสถานะการเดินทาง`** (ฟังก์ชันฝั่งผู้ขาย: การนัดหมาย, ส่งคำขอ, ติดตามสถานะเรียลไทม์, และการยกเลิกตามกฎ `BR-03`) ร่วมกับผังสถานะ **`MD-STM-04`**
  2. **`CC-02` (Requirements Catalogue & Evidence Mapping):** ปลดรหัส `EV-012` ที่อยู่นอกสารบัญ และเชื่อมโยงรหัสหลักฐานกลาง `EV-01`, `EV-02`, `EV-08` พร้อมทั้งผูกรหัสความต้องการกลาง `REQ-FN-003`, `REQ-SEC-001`, `REQ-SEC-002`, และกฎธุรกิจ `BR-03` ครบถ้วน
  3. **`CC-03` (State Machine & Cancellation Guard `BR-03`):** ผู้ขายสามารถกดยกเลิกนัดหมายได้ในสถานะ `S1 (Draft)`, `S2 (Pending/Open)`, และ `S3 (Assigned/Accepted)` (`-> S8: ยกเลิก`) แต่เมื่อคำขอเข้าสู่สถานะ `S4 (กำลังเดินทาง)` ระบบต้องล็อกปุ่มยกเลิกบนหน้าจอทันที และบล็อกการยกเลิกผ่าน API (HTTP 400 ตามกฎ `BR-03`)
  4. **มติในคำถามเปิด `Q-01` ถึง `Q-05` (เลือกทางเลือก A ทั้งหมด):**
     - `Q-01` (Booking Slots): 2 รูปแบบ คือ เรียกทันที (1–2 ชม.) และนัดหมายล่วงหน้า (3 ช่วงเวลามาตรฐาน 09:00–12:00, 13:00–16:00, 16:00–18:00) (Option A)
     - `Q-02` (Cancellation in S3): ยกเลิกได้ตามกฎ BR-03 โดยเปลี่ยนเป็น S8, บันทึกเหตุผล, แจ้งเตือนซาเล้ง, และคืนโควตาน้ำหนักรถ (Option A)
     - `Q-03` (Tracking in S4 In-Transit): แสดงข้อความ 'กำลังเดินทางมาหาคุณ', ระยะทางที่เหลือ (กม.), และ ETA โดยล็อกปุ่มยกเลิกตาม BR-03 (Option A)
     - `Q-04` (Notifications): แจ้งเตือน In-App Banner ใน 3 จังหวะสำคัญ: S3 รับงาน, S4 ออกเดินทาง, S5 ถึงหน้างาน (Option A)
     - `Q-05` (Non-goals): ไม่ทำ Live GPS Animation ทุกวินาที, ไม่คิดค่าปรับการยกเลิกก่อนออกเดินทาง, และไม่อนุญาตให้แก้รายการของเก่าหลังรับงาน (Option A)
- **สถานะ:** สเปก `spec.md` ได้รับการรับรองและอัปเดตเป็น Version 2.0 (`reviewed-post-clarify`) พร้อมสำหรับขั้นตอน `/plan`


---

## บันทึก #55 — `/plan specs/seller/05-booking-and-status-tracking/spec.md` (แผนสถาปัตยกรรม เทคโนโลยี และการปฏิบัติตาม Constraints ครบทั้ง 13 ข้อ)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/seller/05-booking-and-status-tracking/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/05-booking-and-status-tracking/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรม Service Layer, กำหนดการตัดสินใจ `P-01` ถึง `P-06`, กำหนด DDL Schema และ Pydantic Models, ออกแบบ API 4 เส้นทาง, แผนพัฒนาหน้าจอ 5 คอมโพเนนต์, และตารางตรวจสอบ Constraints ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (FastAPI, Supabase/PostgreSQL, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **การตัดสินใจเชิงสถาปัตยกรรม (`P-01` ถึง `P-06`):**
     - `P-01`: บริการเลือกสล็อตเวลานัดหมาย (เรียกทันทีใน 1–2 ชม. หรือนัดล่วงหน้า 3 ช่วงเวลา) เปลี่ยนสถานะ S1 เป็น S2 พร้อม Audit Log (`AC-S05-01`, `Q-01`)
     - `P-02`: บริการติดตามสถานะ 9 สถานะแบบเรียลไทม์ พร้อม Stepper แสดงความคืบหน้าของใบงานตามผัง MD-STM-04 (`AC-S05-02`)
     - `P-03`: บริการบังคับใช้กฎเหล็กการยกเลิกนัดหมาย BR-03: ยกเลิกได้ใน S1..S3 แต่ล็อกปุ่มยกเลิกและบล็อก API ใน S4 In-Transit โยน HTTP 400 (`AC-S05-03`, `Q-02`)
     - `P-04`: บริการคำนวณและแสดงระยะทางที่เหลือ และเวลาประเมินถึงหน้างาน (ETA) ตามรอบพิกัด GPS ซาเล้งทุก 60 วินาที (`AC-S05-04`, `Q-03`, `CC-02`)
     - `P-05`: บริการแจ้งเตือน In-App Banner ใน 3 จังหวะสำคัญ: S3 รับงาน, S4 ออกเดินทาง, S5 ถึงหน้างาน พร้อม Audit Log (`AC-S05-04`, `Q-04`)
     - `P-06`: แคชข้อมูลสถานะและรายละเอียดคำขอล่าสุดใน `localStorage` (`saleng_active_order_tracking`) รองรับโหมดออฟไลน์ (`CC-05`, `REQ-OP-001`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเชื่อมโยงการตัดสินใจ `P-01` ถึง `P-06` ครบถ้วน
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #56 — `/tasks specs/seller/05-booking-and-status-tracking/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/seller/05-booking-and-status-tracking/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/seller/05-booking-and-status-tracking/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-S05-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบนัดหมายและติดตามสถานะ (`booking_tracking_models.py`, `supabase.py`)
     - `T-02`: สร้าง Service และ API สำหรับเลือกสล็อตเวลานัดหมาย (เรียกทันที vs นัดล่วงหน้า 3 ช่วงเวลา) เปลี่ยนสถานะ S1 เป็น S2 พร้อม Audit Log (`AC-S05-01`, `P-01`, `Q-01`)
     - `T-03`: สร้าง Service และ API สำหรับติดตามสถานะ 9 สถานะแบบเรียลไทม์ และ Stepper Timeline ตามผัง MD-STM-04 (`AC-S05-02`, `P-02`)
     - `T-04`: สร้าง Service และ API บังคับใช้กฎเหล็กการยกเลิกนัดหมาย BR-03: ยกเลิกได้ใน S1..S3 และบล็อกใน S4 In-Transit โยน HTTP 400 (`AC-S05-03`, `P-03`, `Q-02`)
     - `T-05`: สร้าง Service และ API สำหรับคำนวณระยะทาง ETA และแจ้งเตือนความคืบหน้าสถานะ S3/S4/S5 (`AC-S05-04`, `AC-S05-05`, `P-04`, `P-05`, `Q-03`, `Q-04`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชสถานะคำขอออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบนัดหมายและติดตามสถานะ (`BookingSlotSelector`, `StatusTimelineStepper`, `InTransitTrackingCard`, `CancelBookingModal`, `BookingTrackingPanel`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-S05-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-S05-01` ถึง `AC-S05-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`


---

## บันทึก #57 — `/implement T-01..08` (พัฒนาระบบนัดหมายและติดตามสถานะ Seller 05 ครบวงจรทั้ง Backend, Frontend, E2E และการบังคับใช้กฎเหล็ก BR-03)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (สำหรับ `specs/seller/05-booking-and-status-tracking/`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Data Models & Store (`T-01`):**
    - `backend/app/models/booking_tracking_models.py` (สร้าง Pydantic models: `BookingSlotRequest`, `OrderCancellationRequest`, `OrderTrackingResponse`, `SimulateStatusRequest`)
    - `backend/app/core/supabase.py` (เพิ่มการจัดเก็บและอัปเดตฟิลด์คำขอนัดหมาย `booking_type`, `scheduled_date`, `scheduled_slot`, `cancellation_reason`, `cancelled_by`, `cancelled_at` และ Audit Log `ORDER_SUBMITTED`, `ORDER_CANCELLED_BY_SELLER`)
    - `backend/tests/test_T01_booking_tracking_models.py` (Unit tests สำหรับ Schema Validation และความถูกต้องของ Data Models: 3 passed)
  - **Backend Service, Endpoints & Cancellation Enforcement (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/booking_tracking_service.py` (พัฒนา `BookingTrackingService` สำหรับการเลือกสล็อตเวลานัดหมาย, การเปลี่ยนสถานะตามผัง 9 สถานะ MD-STM-04, การบล็อกการยกเลิกในสถานะ S4 ตามกฎเหล็ก `BR-03`, การคำนวณระยะทางและ ETA ด้วยสูตร Haversine x 1.35 ตามรอบ GPS 60 วินาที `CC-02`, และการบันทึก Audit Log)
    - `backend/app/api/v1/booking_tracking.py` (เปิด FastAPI Router 4 endpoints: `POST /orders/{id}/book`, `GET /orders/{id}/status`, `POST /orders/{id}/cancel`, `PATCH /orders/{id}/simulate-status`)
    - `backend/app/api/v1/pricing.py` (รวม router เข้ากับแอปพลิเคชันหลัก)
  - **Backend Automated Tests (`T-02`, `T-03`, `T-04`, `T-05`, `T-08`):**
    - `backend/tests/test_AC_S05_01_booking_slot_submission.py` (2 passed)
    - `backend/tests/test_AC_S05_02_status_timeline_stepper.py` (1 passed)
    - `backend/tests/test_AC_S05_03_pre_transit_cancellation.py` (2 passed)
    - `backend/tests/test_AC_S05_04_in_transit_eta_display.py` (1 passed)
    - `backend/tests/test_AC_S05_05_audit_logging.py` (1 passed)
    - `backend/tests/test_e2e_booking_and_status_tracking.py` (Integration E2E test ทดสอบตั้งแต่เลือกสล็อต -> ส่งคำขอ S2 -> ซาเล้งรับงาน S3 -> ออกเดินทาง S4 -> ทดสอบบล็อกยกเลิก BR-03 -> ถึงหน้างาน S5 -> บันทึก Audit Log: 1 passed)
  - **Frontend Services & API Client (`T-06`):**
    - `frontend/src/services/bookingTrackingApi.js` (สร้าง API client สำหรับ `bookSlot`, `getStatus`, `cancelOrder`, `simulateStatus` พร้อมแคชออฟไลน์ใน `localStorage` `saleng_active_order_tracking` ตาม `CC-05`, `REQ-OP-001`)
    - `frontend/tests/bookingTrackingApi.test.mjs` (Unit test สำหรับ API client และแคชออฟไลน์: 3 passed)
  - **Frontend Mobile-First React Components (`T-07`):**
    - `frontend/src/components/BookingSlotSelector.jsx` (แผงเลือกสล็อตเวลานัดหมาย: เรียกทันที 1–2 ชม. หรือนัดล่วงหน้า 3 ช่วงเวลา เช้า, บ่าย, เย็น พร้อมหมายเหตุ)
    - `frontend/src/components/StatusTimelineStepper.jsx` (แถบแสดงขั้นตอนความคืบหน้า 5 ขั้นหลักตามผัง 9 สถานะ MD-STM-04 พร้อมแบนเนอร์ยกเลิก S8 และข้อพิพาท S9)
    - `frontend/src/components/InTransitTrackingCard.jsx` (การ์ดแสดงระยะทางที่เหลือ, เวลา ETA สดรอบ GPS 60 วินาที, โปรไฟล์ซาเล้งพร้อมป้าย KYC 100%, และปุ่มยกเลิกที่ถูกล็อกตามกฎ `BR-03`)
    - `frontend/src/components/CancelBookingModal.jsx` (ป๊อปอัปให้ผู้ขายเลือกเหตุผลสำเร็จรูปหรือพิมพ์เหตุผลเพิ่มเติม และกดยืนยันการยกเลิกนัดหมาย)
    - `frontend/src/components/BookingTrackingPanel.jsx` (แผงหลัก Mobile-First รวม Header, Stepper, Tracking Card, ปุ่มยกเลิก, แถบจำลองสถานะทดสอบ และป้ายเตือนออฟไลน์)
  - **Frontend Automated Tests (`T-08`):**
    - `frontend/tests/AC-S05-01.test.jsx` (Component test สำหรับ BookingSlotSelector และการส่งคำขอ: 2 passed)
    - `frontend/tests/AC-S05-02.test.jsx` (Component test สำหรับ StatusTimelineStepper 5 ขั้น และสถานะ S8/S9: 3 passed)
    - `frontend/tests/AC-S05-03.test.jsx` (Component test สำหรับ Pre-Transit Cancellation Guard BR-03: 2 passed)
    - `frontend/tests/AC-S05-04.test.jsx` (Component test สำหรับ In-Transit ETA & Distance Display: 1 passed)
    - `frontend/tests/AC-S05-05.test.jsx` (Component test สำหรับ CancelBookingModal และการส่งเหตุผลยกเลิก: 3 passed)
  - **Task Tracking:**
    - `specs/seller/05-booking-and-status-tracking/tasks.md` (ปรับสถานะเป็น `completed` และเช็คผ่าน `[DONE]` ครบทุกงาน `T-01` ถึง `T-08`)
- **ผลการทดสอบ (Verification & Regression):**
  - **Backend (Pytest):** 127 passed, 0 failed (รวมทุกชุดทดสอบของ Seller 01, 02, 03, 04, 05, 06, 07, 08, 09)
  - **Frontend (Vitest):** 47 test files passed, 114 tests passed, 0 failed
  - **Zero Regressions:** ฟีเจอร์เดิมทั้งหมดในระบบยังคงทำงานได้อย่างถูกต้อง 100%
- **สถานะ:** ฟีเจอร์ Seller 05 พัฒนาและตรวจสอบคุณภาพเสร็จสมบูรณ์ 100% พร้อมใช้งาน


---

## บันทึก #58 — `/clarify specs/buyer/01-account-and-kyc/spec.md` (การตรวจสอบความสอดคล้องกับสารบัญกลางและการขยายสเปก v2.0)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/01-account-and-kyc/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/01-account-and-kyc/spec.md` (อัปเดตเป็น Version 2.0 สถานะ `reviewed-post-clarify`, แก้ไข Phantom Requirement ID จาก `REQ-CON-003` เป็น `REQ-FN-001`, `BR-03`, `MD-DOM-04` และ `D-00-01`, ปรับรหัส AC ให้เป็น `AC-B01-01` ถึง `AC-B01-05`, ระบุขอบเขตการทำงานร่วมกับ Seller 03 และ Buyer 04, และตอบคำถามเปิด `Q-01` ถึง `Q-06`)
- **ประเด็นสำคัญที่พบและแก้ไข:**
  1. **การแก้ไขข้อขัดแย้งของรหัสความต้องการ (Consistency Fix):**
     - `CC-01`: นำรหัสอุปโลกน์ `REQ-CON-003` ออก และแทนที่ด้วยความต้องการจริงในสารบัญกลาง ได้แก่ `REQ-FN-001`, `BR-03`, `MD-DOM-04: Saleng.maxCapacityKg` และ `D-00-01`
     - `CC-02`: จัดกลุ่มและเปลี่ยนรหัสเกณฑ์การยอมรับจาก `AC-04-08` มาเป็น `AC-B01-01` ถึง `AC-B01-05` ให้สอดคล้องกับโครงสร้างรหัส Buyer Feature
     - `CC-03`: บังคับใช้เงื่อนไขเบื้องต้น `D-00-01` (Precondition: KYC ต้องผ่านก่อนรับงาน) โดยกำหนดให้ซาเล้งที่ไม่ผ่าน KYC ถูกบล็อกด้วย HTTP 403 เมื่อกดรับงาน
  2. **ข้อสรุปแนวทางในคำถามเปิด (`Q-01` ถึง `Q-06`):**
     - `Q-01` (Buyer Registration & Login): ใช้วิธีลงทะเบียนและเข้าสู่ระบบด้วยเบอร์โทรศัพท์และ Phone OTP 6 หลัก (Mock `123456`) พร้อมบันทึก Session Token ลงใน `localStorage`
     - `Q-02` (Thai-ID / DBD-ID KYC Submission): ซาเล้งต้องกรอกเลขบัตรประชาชน 13 หลัก, ชื่อ-นามสกุลจริง, พร้อมอัปโหลดรูปถ่าย 4 จุด (หน้าบัตร ปชช., เซลฟี่คู่กับบัตร, และรูปถ่ายรถพร้อมป้ายทะเบียน)
     - `Q-03` (KYC Lifecycle States): วงจรชีวิต KYC มี 4 สถานะ: `UNVERIFIED` ➔ `PENDING_REVIEW` ➔ `VERIFIED` (หรือ `REJECTED` พร้อมเหตุผลและเปิดให้ส่งใหม่)
     - `Q-04` (Vehicle Types & Max Capacity): กำหนดยานพาหนะมาตรฐาน 3 รูปแบบ (`TRICYCLE` 150 กก., `SIDE_CAR_MOTORCYCLE` 300 กก., `PICKUP_TRUCK` 1,000 กก.) และเปิดให้ปรับแต่งความจุจริง (`max_capacity_kg > 0`)
     - `Q-05` (Unverified Collector Gate): ซาเล้งที่ยังไม่ผ่าน KYC สามารถเปิดดูแอปและแผนที่งานได้ แต่เมื่อกด "รับงาน" ระบบจะบล็อกด้วย HTTP 403 ทันทีตามกฎ `D-00-01`
     - `Q-06` (Mock Admin Approval): เปิด Endpoint จำลอง `POST /api/v1/collectors/{id}/mock-kyc-approval` และ `rejection` เพื่อความคล่องตัวในการรัน Automated Test และ UAT
- **สถานะ:** สเปก `spec.md` ได้รับการรับรองและอัปเดตเป็น Version 2.0 (`reviewed-post-clarify`) พร้อมสำหรับขั้นตอน `/plan`

---

## บันทึก #59 — `/plan specs/buyer/01-account-and-kyc/spec.md` (แผนสถาปัตยกรรม เทคโนโลยี และการปฏิบัติตาม Constraints ครบทั้ง 13 ข้อ)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/01-account-and-kyc/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/01-account-and-kyc/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรม Service Layer, กำหนดการตัดสินใจ `P-01` ถึง `P-06`, ออกแบบ DDL Schema และ Pydantic Models, ออกแบบ API 11 เส้นทาง, แผนพัฒนาหน้าจอ Mobile-First 6 คอมโพเนนต์, และตารางตรวจสอบ Constraints ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (Python 3.11 + FastAPI, Supabase/PostgreSQL, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **การตัดสินใจเชิงสถาปัตยกรรม (`P-01` ถึง `P-06`):**
     - `P-01`: ระบบยืนยันตัวตนซาเล้งด้วยเบอร์โทรและรหัส OTP 6 หลัก พร้อมออก Session Token จัดเก็บใน `localStorage` รองรับการใช้งานต่อเนื่องและออฟไลน์ (`AC-B01-01`, `Q-01`)
     - `P-02`: รองรับการตั้งค่ายานพาหนะ 3 รูปแบบมาตรฐาน (`TRICYCLE` 150 กก., `SIDE_CAR_MOTORCYCLE` 300 กก., `PICKUP_TRUCK` 1,000 กก.) และปรับความจุจริงเพื่อใช้ใน `UC-04` (`AC-B01-02`, `Q-04`, `REQ-FN-001`, `BR-03`)
     - `P-03`: ระบบส่งเอกสาร Thai-ID / DBD-ID ตรวจสอบเลข ปชช. 13 หลัก และรูปถ่ายหลักฐาน 4 จุด (`AC-B01-03`, `Q-02`, `SC-04`)
     - `P-04`: ควบคุมสถานะวงจร KYC 4 ขั้นตอน (`UNVERIFIED` ➔ `PENDING_REVIEW` ➔ `VERIFIED` / `REJECTED`) พร้อมระบบแจ้งเหตุผลและเปิดให้ส่งใหม่ได้ (`AC-B01-03`, `Q-03`, `D-00-01`)
     - `P-05`: การบังคับใช้กฎเหล็ก Unverified Gate บล็อกการกดรับงานด้วย `HTTP 403 Forbidden` หาก `verified = false` ตามกฎความปลอดภัยกลาง `D-00-01` (`AC-B01-04`, `Q-05`)
     - `P-06`: เปิด Endpoint จำลอง `mock-kyc-approval` และ `rejection` สำหรับการทดสอบ และบันทึกประวัติลง `AuditLog` แบบ Append-only (`AC-B01-05`, `Q-06`, `REQ-SEC-001`)
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเชื่อมโยงการตัดสินใจ `P-01` ถึง `P-06` ครบถ้วน
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`

---

## บันทึก #60 — `/tasks specs/buyer/01-account-and-kyc/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/01-account-and-kyc/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/01-account-and-kyc/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-B01-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบบัญชีซาเล้ง ข้อมูลยานพาหนะ และการยืนยันตัวตน KYC (`collector_account_models.py`, `supabase.py`)
     - `T-02`: สร้าง Service และ API สำหรับลงทะเบียนและเข้าสู่ระบบของซาเล้งด้วยเบอร์โทรศัพท์และ Phone OTP (`AC-B01-01`, `P-01`, `Q-01`)
     - `T-03`: สร้าง Service และ API สำหรับตั้งค่าโปรไฟล์ยานพาหนะ 3 รูปแบบ และควบคุมน้ำหนักบรรทุกสูงสุดตามกฎ BR-03 (`AC-B01-02`, `P-02`, `Q-04`)
     - `T-04`: สร้าง Service และ API สำหรับส่งเอกสารยืนยันตัวตน Thai-ID/DBD-ID และจัดการสถานะวงจร KYC 4 ขั้นตอน (`AC-B01-03`, `P-03`, `P-04`, `Q-02`, `Q-03`)
     - `T-05`: สร้าง Service และ API บังคับใช้กฎเหล็ก Unverified Collector Job Claim Gate บล็อกด้วย HTTP 403 ตามกฎ D-00-01 พร้อมบันทึก Audit Log (`AC-B01-04`, `AC-B01-05`, `P-05`, `P-06`, `Q-05`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชข้อมูลซาเล้งออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบบัญชีและการยืนยันตัวตนซาเล้ง (Mobile-First SPA Viewport 375px–414px, ปุ่ม >= 48px ตาม `REQ-UX-001`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-B01-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-B01-01` ถึง `AC-B01-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #61 — `/implement T-01..08` (พัฒนาระบบบัญชีและการยืนยันตัวตนซาเล้ง Buyer 01 ครบถ้วน 8 งานย่อย)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Data Models & Schema (`T-01`):**
    - `backend/app/models/collector_account_models.py` (`CollectorOtpRequest`, `CollectorOtpVerifyRequest`, `CollectorAuthResponse`, `CollectorProfileUpdateRequest`, `VehicleProfileUpdateRequest`, `KycSubmissionRequest`, `KycStatusResponse`, `JobClaimGateCheckResponse`, `MockKycReviewRequest`, `mask_phone_number`, `validate_thai_id`)
    - `backend/app/core/supabase.py` (ขยาย Store สำหรับ `collector_otps`, `collector_sessions`, `collector_kyc_submissions` และฟังก์ชันจัดการโปรไฟล์/KYC ของซาเล้ง)
    - `backend/tests/test_T01_collector_account_models.py` (7 passed)
  - **Service Layer & API Routers (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/collector_account_service.py` (`CollectorAuthService`, `CollectorVehicleService`, `CollectorKycService`)
    - `backend/app/api/v1/collector_account.py` (เปิด API 11 เส้นทางสำหรับ Authentication, Profile, Vehicle, KYC, Gate Check, และ Mock Helpers)
    - `backend/app/api/v1/pricing.py` (เมานต์ `collector_account_router` ภายใต้ prefix `/api/v1`)
    - `backend/tests/test_AC_B01_01_collector_auth.py` (6 passed)
    - `backend/tests/test_AC_B01_02_vehicle_profile.py` (4 passed)
    - `backend/tests/test_AC_B01_03_kyc_submission.py` (2 passed)
    - `backend/tests/test_AC_B01_04_unverified_gate.py` (4 passed)
    - `backend/tests/test_AC_B01_05_collector_audit_logging.py` (1 passed)
  - **Frontend Client & Components (`T-06`, `T-07`):**
    - `frontend/src/services/collectorAccountApi.js` (API Client พร้อมแคชออฟไลน์ใน `localStorage` ตาม `CC-05`, `REQ-OP-001`)
    - `frontend/src/components/CollectorPhoneLoginForm.jsx` (ฟอร์มเบอร์โทร + OTP 6 หลัก + Cooldown 60s)
    - `frontend/src/components/CollectorProfileCard.jsx` (การ์ดโปรไฟล์ + เบอร์โทร Masked `08X-XXX-XXXX` + สถานะ KYC + Rating)
    - `frontend/src/components/VehicleConfigCard.jsx` (แผงเลือกยานพาหนะ 3 รูปแบบมาตรฐาน + ระบุทะเบียนและความจุน้ำหนัก)
    - `frontend/src/components/KycStatusBanner.jsx` (แบนเนอร์แจ้งสถานะ KYC 4 ขั้นตอน: `UNVERIFIED`, `PENDING_REVIEW`, `VERIFIED`, `REJECTED`)
    - `frontend/src/components/KycSubmissionModal.jsx` (ป๊อปอัปยื่นเลข ปชช. 13 หลัก พร้อมภาพถ่าย 4 จุด)
    - `frontend/src/components/CollectorAccountPanel.jsx` (แผงหลักรวมคอมโพเนนต์ + ปุ่มทดสอบ Claim Job Gate + Mock Dev Helpers)
    - `frontend/tests/collectorAccountApi.test.mjs` (7 passed)
  - **Automated Tests & E2E Integration Suite (`T-08`):**
    - `frontend/tests/AC-B01-01.test.jsx` (3 passed)
    - `frontend/tests/AC-B01-02.test.jsx` (3 passed)
    - `frontend/tests/AC-B01-03.test.jsx` (2 passed)
    - `frontend/tests/AC-B01-04.test.jsx` (2 passed)
    - `backend/tests/test_e2e_collector_account_and_kyc.py` (1 passed)
  - **Task Tracking:**
    - `specs/buyer/01-account-and-kyc/tasks.md` (ปรับสถานะเป็น `completed` และมาร์ก `T-01` ถึง `T-08` เป็น `[DONE]`)
- **ผลการทดสอบและการตรวจรับ 5 ด่าน:**
  1. **Backend Tests:** 153 passed 100% (รวม 25 backend tests สำหรับ Buyer 01 และ 128 tests เดิม)
  2. **Frontend Tests:** 131 passed across 52 test files 100% (รวม 17 frontend tests สำหรับ Buyer 01)
  3. **Zero Regressions:** ฟีเจอร์เดิมทั้งหมดของระบบ (Seller 01..09) ทำงานได้ปกติ 100%
  4. **PDPA & Security:** บังคับใช้ Phone Masking `08X-XXX-XXXX`, กฎเหล็ก Unverified Collector Block Gate `D-00-01` (HTTP 403), และบันทึก Security Audit Log ครบทุกเหตุการณ์
  5. **UX Mobile-First:** ปุ่มบนหน้าจอมีขนาดความสูง `>= 48px` ตามข้อกำหนด `REQ-UX-001`
- **สถานะ:** พัฒนาฟีเจอร์ Buyer 01 เสร็จสมบูรณ์ พร้อมส่งมอบและพร้อมสำหรับฟีเจอร์ถัดไป (`specs/buyer/02-search-and-filtering/`)
