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
