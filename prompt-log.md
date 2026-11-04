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

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%

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

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%


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

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%


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

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%


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

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%

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


---

## บันทึก #62 — `/clarify specs/buyer/02-job-search-and-map/spec.md` (การตรวจสอบความสอดคล้องกับสารบัญกลางและการขยายสเปก v2.0)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/02-job-search-and-map/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/02-job-search-and-map/spec.md` (ปรับปรุงจาก Stub 28 บรรทัด สู่ Version 2.0 สถานะ `reviewed-post-clarify`, เชื่อมโยงรหัส `UC-04`, `REQ-FN-002`, `REQ-QA-002`, `REQ-SEC-002`, `REQ-OP-001..002`, `REQ-UX-001`, `CC-01..06`, และ `D-00-01..02`, กำหนดเกณฑ์การยอมรับ `AC-B02-01` ถึง `AC-B02-05`, และบันทึกข้อสรุปคำถามเปิด `Q-01` ถึง `Q-06`)
- **ประเด็นสำคัญที่พบและข้อสรุปแนวทางแก้ปัญหา (`Q-01` ถึง `Q-06`):**
  1. **`Q-01` (การซ่อนพิกัดหมุดบนแผนที่ก่อนรับงาน — `D-00-02`, `REQ-SEC-002`, `CC-06`):**
     - ใช้เทคนิค **Coordinate Fuzzing (สุ่มเบี่ยงเบนพิกัด ±300–500 ม.)** และส่งเฉพาะชื่อตำบล/แขวง เพื่อไม่ให้ทราบพิกัดบ้านที่แท้จริงของผู้ขายก่อนกดรับงาน ขณะที่การคำนวณระยะทางถนนจริงกระทำที่หลังบ้านอย่างแม่นยำ
  2. **`Q-02` (การแจ้งเตือนงานใหม่ในพื้นที่):**
     - ใช้กลไก **In-App Auto-Refresh / Polling ทุก 30–60 วินาที** พร้อม Toast Banner สีเขียวด้านบน, เสียง Audio Ping, และ Notification Badge สอดคล้องกับรอบ GPS Sync `CC-02` สำหรับรอบ R1
  3. **`Q-03` (ตัวเลือกและเงื่อนไขการกรองงาน — `AC-B02-05`):**
     - รองรับการกรอง 3 มิติ: หมวดหมู่วัสดุ 5 กลุ่ม, ช่วงน้ำหนักประเมิน 4 ช่วง, และจัดเรียงตามระยะทางใกล้สุด (Default) หรือมูลค่าประเมินสูงสุด
  4. **`Q-04` (โครงสร้างหน้าจอบนมือถือ — `CC-01`, `REQ-UX-001`):**
     - ใช้ **Segmented Control Tab Switcher** ด้านบน สลับระหว่าง **"รายการงาน" (List View)** และ **"แผนที่งาน" (Map View)** ขนาดปุ่มกด `>= 48px` ใช้งานง่ายกลางแจ้งและลื่นไหลบนมือถือราคาประหยัด
  5. **`Q-05` (การทำงานร่วมกับ Unverified Gate — `D-00-01`):**
     - ซาเล้งที่ยังไม่ผ่าน KYC สามารถเปิดค้นหาและดูแผนที่งานได้ แต่ปุ่มกดรับงานจะล็อกด้วยแม่กุญแจ และหากแตะจะแสดง Informative Gate Modal พร้อมปุ่มส่งเอกสาร KYC ใน Buyer 01 ทันที
  6. **`Q-06` (การขยายระยะทางค้นหา 10 กม. — `AC-B02-02` / `A1`):**
     - ค่าเริ่มต้นคือ 5.0 กม. เสมอเมื่อเปิดหน้าจอใหม่ หากกดยอมรับขยายเป็น 10.0 กม. ระบบจะคงค่านี้ไว้ตลอดเซสชันปัจจุบันในแอป
  7. **ระบบสำรองการคำนวณระยะทาง (`Dual-Engine Routing Fallback` — `CC-03`, `REQ-OP-002`):**
     - หาก Routing API ภายนอกตอบสนองช้าเกิน 1.5 วินาที หรือขัดข้อง ระบบจะสลับไปใช้สูตร **`Haversine * 1.35`** อัตโนมัติทันที เพื่อให้ตอบสนองภายใน `<= 2.0 วินาที`
- **สถานะ:** สเปก `spec.md` ได้รับการรับรองและอัปเดตเป็น Version 2.0 (`reviewed-post-clarify`) พร้อมสำหรับขั้นตอน `/plan`


---

## บันทึก #63 — `/plan specs/buyer/02-job-search-and-map/spec.md` (แผนสถาปัตยกรรม เทคโนโลยี และการปฏิบัติตาม Constraints ครบทั้ง 13 ข้อ)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/02-job-search-and-map/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/02-job-search-and-map/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรม Dual-Engine Routing, กำหนดการตัดสินใจ `P-01` ถึง `P-06`, ออกแบบ DDL Schema และ Pydantic Models, ออกแบบ API 3 เส้นทางสำหรับ Nearby Jobs, Summary, และ Simulate Order, แผนพัฒนาหน้าจอ Mobile-First 6 คอมโพเนนต์, และตารางตรวจสอบ Constraints ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (Python 3.11 + FastAPI, In-memory Supabase/PostgreSQL Adapter, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **การตัดสินใจเชิงสถาปัตยกรรม (`P-01` ถึง `P-06`):**
     - `P-01`: Coordinate Fuzzing & Subdistrict Snapping เบี่ยงเบนสุ่มพิกัด ±300–500 ม. และซ่อนบ้านเลขที่/พิกัดจริงตามกฎ PDPA และ `D-00-02`
     - `P-02`: In-App Live Alert & Polling ทุก 30–60 วินาที ตรวจจับงานใหม่ในรัศมี 5.0 กม. พร้อม Toast แจ้งเตือนและเสียง Audio Ping สอดคล้องกับรอบ GPS Sync `CC-02`
     - `P-03`: Multi-Criteria Filtering & Sorting รองรับตัวกรองหมวดหมู่วัสดุ 5 กลุ่ม, ช่วงน้ำหนักประเมิน 4 ช่วง, และจัดเรียงตามระยะทางใกล้สุดหรือมูลค่าสูงสุด (`AC-B02-05`)
     - `P-04`: Mobile Segmented Tab Switcher สลับระหว่าง `List View` และ `Map View` ขนาดปุ่มกด `>= 48px` ใช้งานง่ายกลางแจ้งบนมือถือราคาประหยัด (`RAM >= 2 GB` ตาม `CC-01`)
     - `P-05`: บูรณาการกับ Unverified Gate `D-00-01` ซาเล้งที่ยังไม่ผ่าน KYC สามารถเปิดดูงานและแผนที่ได้ แต่ปุ่มกดรับงานจะล็อกด้วยแม่กุญแจ และมี Modal แจ้งเตือน
     - `P-06`: Radius Expansion ค่าเริ่มต้น 5.0 กม. เสมอเมื่อเปิดหน้าจอใหม่ หากกดยอมรับขยายเป็น 10.0 กม. ระบบจะคงค่านี้ไว้ตลอดเซสชันปัจจุบันในแอป
  3. **ตารางตรวจ Constraints:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเชื่อมโยงการตัดสินใจ `P-01` ถึง `P-06` ครบถ้วน
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #64 — `/tasks specs/buyer/02-job-search-and-map/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/02-job-search-and-map/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/02-job-search-and-map/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-B02-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบค้นหาและแสดงงาน (`job_search_models.py`, ฟังก์ชัน `fuzz_coordinates`, ขยาย `supabase.py`)
     - `T-02`: สร้าง Dual-Engine Routing Service และ API ค้นหาคำขอขายในรัศมี 5.0 กม. ตอบสนอง `<= 3.0s` (`AC-B02-01`, `REQ-FN-002`, `REQ-QA-002`, `CC-03`)
     - `T-03`: สร้างระบบขยายรัศมีการค้นหาเป็น 10.0 กม. เมื่อไม่พบงานในรัศมี 5.0 กม. (`A1`, `AC-B02-02`, `Q-06`)
     - `T-04`: สร้างระบบป้องกันข้อมูลส่วนบุคคล PII & Coordinate Protection และการจัดการ GPS Error (`E1`, `AC-B02-03`, `AC-B02-04`, `REQ-SEC-002`, `D-00-02`)
     - `T-05`: สร้างระบบกรองงานหลายมิติ 3 ด้าน, จัดเรียงลำดับ, และจำลองคำขอขายใหม่ (`AC-B02-05`, `Q-02`, `Q-03`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชค้นหางานออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบค้นหาและแสดงงาน (Mobile-First SPA Viewport 375px–414px, Segmented Control Tab Switcher List ⇄ Map, ปุ่ม >= 48px ตาม `REQ-UX-001`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-B02-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-B02-01` ถึง `AC-B02-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #65 — `/implement T-01..08` (พัฒนาระบบค้นหาและแสดงงานรับซื้อตามพิกัด Buyer 02 ครบวงจร)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/02-job-search-and-map/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/job_search_models.py` (Pydantic Models: `JobSearchQueryParams`, `NearbyJobSummaryResponse`, `NearbyJobListResponse`, `SimulateOrderRequest`, ฟังก์ชัน `fuzz_coordinates` สุ่มเบี่ยงเบนพิกัด ±300–500 ม. ตาม `REQ-SEC-002`, `D-00-02`, `CC-06`)
  - `backend/app/services/job_search_service.py` (`DualEngineRoutingService` คำนวณระยะทางถนนจริงและสลับใช้ `Haversine * 1.35` อัตโนมัติ `REQ-OP-002`, `PrivacyProtectionService` ตัด PII ทิ้ง 100%, `JobSearchService` ค้นหาและกรองคำขอขาย)
  - `backend/app/api/v1/job_search.py` (FastAPI Router สำหรับ `GET /api/v1/collectors/jobs/nearby`, `GET /api/v1/collectors/jobs/{order_id}/summary`, และ `POST /api/v1/collectors/jobs/simulate-new-order`)
  - `backend/app/api/v1/pricing.py` (เมานต์ `job_search_router` เข้ากับ FastAPI Application)
  - `backend/app/core/supabase.py` (เพิ่ม `_seed_default_orders_s2()`, `get_open_orders_s2()`, `add_simulated_order()`, และ `record_audit_log()` ตาม `REQ-SEC-001`, `CC-04`)
  - `frontend/src/services/jobSearchApi.js` (API Client สำหรับเรียก Nearby Jobs, Summary, Simulate Order พร้อม Offline Cache ใน `localStorage` ตาม `CC-05`, `REQ-OP-001`)
  - `frontend/src/components/JobSearchFilterBar.jsx` (แถบตัวกรองหมวดหมู่วัสดุ 5 กลุ่ม, ช่วงน้ำหนัก 4 ช่วง, และการจัดเรียง)
  - `frontend/src/components/JobCardList.jsx` (รายการการ์ดงานแบบเลื่อนแนวตั้ง พร้อมกล่องเตือนไม่มีงานและปุ่มขยาย 10 กม. `AC-B02-02`)
  - `frontend/src/components/JobMapView.jsx` (แผนที่แสดงหมุดจำลอง Fuzzed Pins, หมุดซาเล้ง, และ Bottom Sheet Mini Preview)
  - `frontend/src/components/GpsWarningBanner.jsx` (กล่องแจ้งเตือนกรณีปิด GPS พร้อมปุ่มลองใหม่ `AC-B02-04`)
  - `frontend/src/components/LiveJobAlertToast.jsx` (Toast แจ้งเตือนงานใหม่ในพื้นที่พร้อมตัวนับรอบการรีเฟรช 30–60s `Q-02`, `CC-02`)
  - `frontend/src/components/JobSearchPanel.jsx` (แผงควบคุมหลักรวม Segmented Tab Switcher List ⇄ Map ปุ่ม >= 48px และ Unverified Gate Modal `D-00-01`)
  - `backend/tests/test_T01_job_search_models.py` (Unit Test Schema, Fuzzing Bounds 300–500m, PII Masking)
  - `backend/tests/test_AC_B02_01_job_discovery.py` (Test การค้นหางานในรัศมี 5.0 กม. เวลาตอบสนอง <= 3.0s และ Routing Fallback)
  - `backend/tests/test_AC_B02_02_radius_expansion.py` (Test แจ้งเตือนไม่มีงานใน 5 กม. และการขยายรัศมีเป็น 10.0 กม.)
  - `backend/tests/test_AC_B02_03_pii_coordinate_protection.py` (Test การปิดบังบ้านเลขที่ เบอร์โทร และตรวจสอบระยะ Fuzzed Pins)
  - `backend/tests/test_AC_B02_04_gps_handling.py` (Test ปฏิเสธพิกัด GPS ว่างหรือไม่ถูกต้อง HTTP 400 ไม่ใช้พิกัดเก่าหมดอายุ)
  - `backend/tests/test_AC_B02_05_job_filtering.py` (Test ตัวกรองหมวดหมู่, ช่วงน้ำหนัก, จัดเรียงลำดับ, และจำลอง Order ใหม่)
  - `backend/tests/test_e2e_buyer_job_search_and_map.py` (Integration E2E Test ครบวงจร Lifecycle)
  - `frontend/tests/jobSearchApi.test.mjs` (Unit Test Frontend API Client และ Offline Cache)
  - `frontend/tests/AC-B02-01.test.jsx` (Component Test ค้นหางานรัศมี 5.0 กม.)
  - `frontend/tests/AC-B02-02.test.jsx` (Component Test กล่องแจ้งเตือนไม่มีงานและปุ่มขยาย 10 กม.)
  - `frontend/tests/AC-B02-03.test.jsx` (Component Test ป้องกัน PII ใน List และ Map View)
  - `frontend/tests/AC-B02-04.test.jsx` (Component Test แจ้งเตือน GPS ปิดพร้อมปุ่มลองใหม่)
  - `frontend/tests/AC-B02-05.test.jsx` (Component Test ตัวกรอง, สลับ List/Map Tab, และ Unverified Gate Modal `D-00-01`)
  - `specs/buyer/02-job-search-and-map/tasks.md` (อัปเดตสถานะ `T-01` ถึง `T-08` เป็น `[DONE]` และอัปเดตสถานะเอกสารเป็น `completed`)
- **ผลการตรวจ 5 ด่านหลังจบงาน (Verification Checklist):**
  1. **ไฟล์ที่แตะ:** แตะเฉพาะไฟล์ที่กำหนดใน `T-01` ถึง `T-08` ของ Buyer 02 ไม่มีไฟล์นอกขอบเขต
  2. **ผลการรัน Test:**
     - Backend Test Suite (`pytest backend/tests/`): **`172 passed, 3 warnings in 0.64s`** (ผ่าน 100% ครบทุกโมดูล เดิม 153 -> 172 passed เพิ่มขึ้น 19 tests)
     - Frontend Test Suite (`npm test --prefix frontend`): **`58 test files passed, 141 passed in 4.32s`** (ผ่าน 100% ครบทุกโมดูล เดิม 131 -> 141 passed เพิ่มขึ้น 10 tests)
     - Zero Regressions: ไม่มีผลกระทบต่อ Seller 01..09 และ Buyer 01
  3. **การอ้างอิง ID:** ฟังก์ชันในโค้ดและชุดทดสอบทุกไฟล์ระบุรหัส `UC-04`, `REQ-FN-002`, `REQ-QA-002`, `REQ-SEC-002`, `REQ-OP-002`, `CC-01..06`, `D-00-01`, `D-00-02`, `AC-B02-01..05`, `P-01..P-06` ครบถ้วน
  4. **Non-goals & Constraints:**
     - ไม่มีการกดรับงานหรือผูกใบงานจริง (ยกไปทำใน Buyer 04)
     - ไม่มีระบบ Turn-by-turn Navigation
     - ข้อมูลคำขอขายก่อนรับงานไม่มี `address_text`, เบอร์โทรศัพท์, หรือพิกัดจริงเด็ดขาด (Coordinate Fuzzing ±300–500 ม. และแสดงเฉพาะระดับตำบล/แขวง)
     - ปุ่มกดบนหน้าจอมือถือมีขนาดความสูงไม่น้อยกว่า `48px` ทุกปุ่มตาม `REQ-UX-001`
     - ซาเล้งที่ยังไม่ผ่าน KYC สามารถเปิดดูงานและแผนที่ได้ แต่ถูกล็อกปุ่มรับงานด้วย Informative Gate Modal ตาม `D-00-01`
  5. **การบันทึกผล:** อัปเดตสถานะ `tasks.md` เป็น `completed` พร้อมเครื่องหมาย `[DONE]` ครบทุกงานย่อย และบันทึกลง `prompt-log.md` เรียบร้อย


---

## บันทึก #66 — `/clarify specs/buyer/03-pre-acceptance-evaluation/spec.md` (การประเมินงานและค่าน้ำมันก่อนรับ)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/03-pre-acceptance-evaluation/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/03-pre-acceptance-evaluation/spec.md` (ปรับปรุงจากฉบับร่างเดิมเป็น Version `2.0`, สถานะ `reviewed-post-clarify`, เพิ่มรายละเอียดขอบเขตงาน 7 ด้าน, Acceptance Criteria 5 ข้อ `AC-B03-01..05`, บันทึกข้อสรุปคำถาม `Q-01` ถึง `Q-06` / `D-B03-01` ถึง `D-B03-06`, และตารางตรวจสอบ Constraints กลางครบทั้ง 13 ข้อ)
- **ประเด็นที่ค้นพบและข้อสรุปจากการ Clarify:**
  1. **สูตรคิดค่าน้ำมันตามประเภทยานพาหนะ (`Q-01` / `D-B03-01`):** คำนวณจาก `road_distance_km * fuel_rate` โดยอิงตาม `vehicle_type` ของซาเล้ง: รถปั่น = 0.00 บ./กม., มอเตอร์ไซค์พ่วงข้าง = 2.50 บ./กม., รถกระบะ = 4.50 บ./กม. (Default = 2.50 บ./กม.)
  2. **การรับมือเมื่อบริการแผนที่ภายนอกล้มเหลว (`Q-02` / `D-B03-02`):** ยึดตาม `CC-03` และ `REQ-OP-002` โดยสลับใช้สูตร `Haversine * 1.35` อัตโนมัติเมื่อบริการแผนที่ภายนอกช้าเกิน 1.5 วินาที พร้อมแสดงป้ายโหมดสำรอง
  3. **การตรวจสอบความจุรถ (`Q-03` / `D-B03-03`):** นำน้ำหนักปัจจุบันในรถ (`current_load_kg`) + น้ำหนักประเมินของงานใหม่ เทียบกับ `max_capacity_kg` เพื่อจัดสรรพื้นที่รถได้ถูกต้องตาม `BR-03`
  4. **การบล็อกปุ่มรับงานเมื่อเกินความจุ (`Q-04` / `D-B03-04`):** หากน้ำหนักสะสมรวมเกินความจุรถ ให้เปลี่ยนแถบความจุเป็นสีแดง และ **Disable ปุ่มกดรับงาน** พร้อมแจ้งเตือนให้เคลียร์รอบวิ่งก่อน
  5. **สถานะ Offline (`Q-05` / `D-B03-05`):** ซาเล้งสถานะ Offline สามารถเปิดดูรายละเอียดและประเมินงานได้ แต่ปุ่มรับงานจะถูกล็อกพร้อมข้อความเตือนให้สลับเป็น Online ก่อน
  6. **Unverified KYC Gate (`Q-06` / `D-B03-06`):** ซาเล้งที่ยังไม่ผ่าน KYC สามารถดูรายละเอียดงานได้ แต่ปุ่มรับงานจะล็อกด้วยรูปแม่กุญแจ 🔒 และมี Informative Gate Modal นำทางไปยื่นเอกสาร KYC ตามกฎ `D-00-01`
- **สถานะ:** สเปก `spec.md` ได้รับการปรับปรุงเป็น Version `2.0` (reviewed-post-clarify) เรียบร้อยแล้ว พร้อมสำหรับขั้นตอนการจัดทำแผนพัฒนาทางเทคนิค `/plan`


---

## บันทึก #67 — `/plan specs/buyer/03-pre-acceptance-evaluation/spec.md` (แผนสถาปัตยกรรมและการพัฒนาทางเทคนิค)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/03-pre-acceptance-evaluation/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/03-pre-acceptance-evaluation/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ออกแบบสถาปัตยกรรมระบบประเมินงานและค่าน้ำมันก่อนรับ, แผนผัง Mermaid Flowchart, การตัดสินใจเชิงเทคนิค `D-B03-01` ถึง `D-B03-06`, Data Models & Schemas, API Endpoints 3 เส้นทาง, แผนพัฒนาหน้าจอ 5 คอมโพเนนต์ Mobile-First SPA ปุ่ม >= 48px, และตารางตรวจสอบ Constraints กลางครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (Python 3.11 + FastAPI, In-memory Supabase/PostgreSQL Adapter, React 18 + TailwindCSS, Pytest, Vitest + RTL + JSDOM)
  2. **สถาปัตยกรรมและการคำนวณ (`D-B03-01` ถึง `D-B03-06`):**
     - `D-B03-01`: คำนวณค่าน้ำมันตามประเภทพาหนะ (`vehicle_type`): รถปั่น 0 บาท/กม., มอเตอร์ไซค์พ่วงข้าง 2.50 บาท/กม., รถกระบะ 4.50 บาท/กม. (Default 2.50 บาท/กม.)
     - `D-B03-02`: ใช้ Dual-Engine Routing สลับใช้ `Haversine * 1.35` อัตโนมัติเมื่อแผนที่ภายนอกขัดข้อง พร้อม Flag `is_fallback_distance: true` ภายใน `<= 2.0s` (`CC-03`, `REQ-OP-002`)
     - `D-B03-03` & `D-B03-04`: คำนวณน้ำหนักสะสม `current_load_kg + job_est_weight_kg` เทียบกับ `max_capacity_kg` (200 กก. ตาม `BR-03`, `REQ-CON-003`); หากเกินให้เปลี่ยนแถบความจุเป็นสีแดง และ Disable ปุ่มรับงาน
     - `D-B03-05`: สลับสถานะ Online/Offline (CC-02); หาก Offline อนุญาตให้ดูรายละเอียดและประเมินค่าน้ำมันได้ แต่ล็อกปุ่มรับงาน
     - `D-B03-06`: กฎเหล็ก Unverified Collector Gate (`D-00-01`); ซาเล้งที่ยังไม่ผ่าน KYC สามารถดูรายละเอียดได้ แต่ปุ่มรับงานล็อกด้วยรูปกุญแจ 🔒 และมี Gate Modal นำทางไป KYC
  3. **ตารางตรวจ Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` สอดคล้องกับ SRS และ Mockup หน้า 62 (`Card 02`)
- **สถานะ:** แผน `plan.md` พร้อมสำหรับการแตกงานย่อยในขั้นตอน `/tasks`


---

## บันทึก #68 — `/tasks specs/buyer/03-pre-acceptance-evaluation/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/03-pre-acceptance-evaluation/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/03-pre-acceptance-evaluation/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-B03-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบประเมินงานและค่าน้ำมัน (`job_evaluation_models.py`, ฟังก์ชัน `calculate_fuel_cost`, ขยาย `supabase.py`)
     - `T-02`: สร้าง Service และ API ประเมินระยะทางและค่าน้ำมันตามประเภทยานพาหนะ (`AC-B03-01`, `Card 02`, `REQ-FN-002`, `REQ-QA-002`, `AC-04-11`, `D-B03-01`)
     - `T-03`: สร้างระบบสำรอง Dual-Engine Routing Fallback เมื่อบริการแผนที่ขัดข้อง (`AC-B03-02`, `CC-03`, `REQ-OP-002`, `D-B03-02`)
     - `T-04`: สร้างระบบตรวจสอบความจุรถซาเล้งและการสลับสถานะ Online/Offline (`AC-B03-03`, `BR-03`, `REQ-CON-003`, `CC-02`, `D-B03-03..05`)
     - `T-05`: สร้างระบบป้องกันข้อมูลส่วนบุคคล PII & Coordinate Protection และ KYC Gate (`AC-B03-04`, `AC-B03-05`, `REQ-SEC-002`, `D-00-01`, `D-00-02`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชการประเมินงานออฟไลน์ใน `localStorage` (`CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบประเมินงานและค่าน้ำมัน (Mobile-First SPA Viewport 375px–414px, ปุ่ม >= 48px ตาม `REQ-UX-001`, แถบความจุรถสะสม เขียว/ฟ้า/แดง)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-B03-01..05`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-B03-01` ถึง `AC-B03-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%


---

## บันทึก #69 — `/implement T-01..08` (พัฒนาระบบประเมินงานและค่าน้ำมันก่อนรับ Buyer 03 ครบถ้วน)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ขอบเขต:** พัฒนาระบบประเมินรายละเอียดคำขอขายและค่าน้ำมันก่อนรับงาน (Buyer Feature 03: `specs/buyer/03-pre-acceptance-evaluation/`) ตาม Use Case `UC-04` และ User Story `Card 02` บนหน้า 62
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models, Services, และ Router:**
    - `backend/app/models/job_evaluation_models.py` (Pydantic models: `JobEvaluationResponse`, `EvaluatedItemSummary`, `CollectorStatusToggleRequest`, `CollectorCapacityResponse`, ฟังก์ชันคำนวณค่าน้ำมัน `calculate_fuel_cost` ตามประเภทรถ `TRICYCLE`, `MOTORCYCLE`, `PICKUP` ตาม `D-B03-01`)
    - `backend/app/core/supabase.py` (เพิ่ม helper methods: `get_saleng_current_load`, `set_saleng_current_load`, `update_saleng_online_status`, `get_order_evaluation_data`)
    - `backend/app/services/job_evaluation_service.py` (`JobEvaluationService` คำนวณระยะทางถนน ค่าน้ำมัน ความจุรถ ระบบสำรอง Dual-Engine Routing Fallback และการตัดข้อมูล PII)
    - `backend/app/api/v1/job_evaluation.py` (FastAPI Router สำหรับ `GET /jobs/{order_id}/evaluate`, `PATCH /{saleng_id}/status`, `GET /{saleng_id}/capacity`)
    - `backend/app/api/v1/pricing.py` (เมานต์ `job_evaluation_router` เข้ากับ `/api/v1/collectors`)
  - **Backend Tests (Unit, Acceptance, Integration E2E):**
    - `backend/tests/test_T01_job_evaluation_models.py` (3 tests passed)
    - `backend/tests/test_AC_B03_01_fuel_cost_estimation.py` (2 tests passed)
    - `backend/tests/test_AC_B03_02_routing_timeout_fallback.py` (1 test passed)
    - `backend/tests/test_AC_B03_03_capacity_and_online_toggle.py` (3 tests passed)
    - `backend/tests/test_AC_B03_04_pii_masking.py` (2 tests passed)
    - `backend/tests/test_e2e_buyer_pre_acceptance_evaluation.py` (6 tests passed)
  - **Frontend Services และ Components:**
    - `frontend/src/services/jobEvaluationApi.js` (API Client รองรับการดึงข้อมูลประเมิน แคชออฟไลน์ใน `localStorage`, สลับสถานะ Online/Offline, ตรวจสอบความจุรถ)
    - `frontend/src/components/CapacityIndicatorBar.jsx` (แถบแสดงความจุรถสะสม current + job เทียบกับ max 200 กก. พร้อมเตือนสีแดงเมื่อน้ำหนักเกินตาม `BR-03`, `REQ-CON-003`)
    - `frontend/src/components/OnlineStatusToggle.jsx` (สวิตช์เปิด/ปิด Online/Offline ขนาด >= 48px ตาม `REQ-UX-001`, `CC-01`, `CC-02`)
    - `frontend/src/components/FuelCostEstimateCard.jsx` (การ์ดแสดงระยะทางถนนจริง ความคลาดเคลื่อน <= 15% ค่าน้ำมันตามประเภทรถ และป้ายสำรอง `⚡ ระยะทางประเมินสำรอง`)
    - `frontend/src/components/BulkyItemDetailList.jsx` (รายการของเก่าที่จะขาย รูปถ่าย `REQ-FN-004` และป้ายขอคนช่วยยก `need_lifting_help`)
    - `frontend/src/components/JobEvaluationView.jsx` (หน้าจอหลักรวบรวมทุกคอมโพเนนต์ พร้อม Fixed Bottom Action Bar ขนาด >= 48px รองรับ 4 สถานะ: KYC Locked, Offline Disabled, Overload Disabled, Normal Claim และ KYC Gate Modal ตาม `D-00-01`)
  - **Frontend Tests (Vitest + RTL):**
    - `frontend/tests/jobEvaluationApi.test.mjs` (5 tests passed)
    - `frontend/tests/AC-B03-01.test.jsx` (2 tests passed)
    - `frontend/tests/AC-B03-02.test.jsx` (2 tests passed)
    - `frontend/tests/AC-B03-03.test.jsx` (3 tests passed)
    - `frontend/tests/AC-B03-04.test.jsx` (1 test passed)
    - `frontend/tests/AC-B03-05.test.jsx` (1 test passed)
  - **Tasks:**
    - `specs/buyer/03-pre-acceptance-evaluation/tasks.md` (ปรับสถานะเป็น `completed`, มาร์ก `T-01` ถึง `T-08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน (5-point verification checklist):**
  1. **ความครบถ้วนของ Automated Tests:**
     - Backend (Pytest): ผ่าน 189/189 ข้อ (100% pass)
     - Frontend (Vitest): ผ่าน 155/155 ข้อ (100% pass)
  2. **ความตรงตามสเปก (`spec.md` v2.0):**
     - คำนวณค่าน้ำมันตรงตามประเภทรถ (`D-B03-01`): รถซาเล้งถีบ 0.00 บ./กม., มอเตอร์ไซค์พ่วงข้าง 2.50 บ./กม., รถกระบะ 4.50 บ./กม.
     - ระบบสำรอง Dual-Engine Routing Fallback (`Haversine * 1.35`) เมื่อช้ากว่า 1.5 วินาที พร้อมส่ง Flag `is_fallback_distance: true` (`CC-03`, `REQ-OP-002`)
     - ตรวจสอบน้ำหนักสะสมเกิน 200 กก. บล็อกรับงานด้วย `CAPACITY_EXCEEDED` (`BR-03`, `REQ-CON-003`)
     - สลับสถานะ Online/Offline และบล็อกรับงานเมื่อ Offline (`CC-02`, `D-B03-05`)
     - ซ่อนข้อมูลส่วนบุคคล PII และพิกัดจริง 100% ด้วย Coordinate Fuzzing (±300–500 ม.) (`REQ-SEC-002`, `D-00-02`, `CC-06`)
     - ซาเล้งที่ยังไม่ผ่าน KYC สามารถเปิดดูรายละเอียดได้ แต่ปุ่มรับงานล็อก 🔒 และเปิด Gate Modal นำทางไป KYC (`D-00-01`, `AC-B03-05`)
  3. **การปฏิบัติตาม Constraints กลาง:**
     - รองรับ `CC-01..06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03` ครบถ้วน
  4. **การตรวจสอบย้อนกลับและชื่ออ้างอิง:**
     - ฟังก์ชันและชุดทดสอบตั้งชื่ออ้างอิง `AC-B03-01..05`, `T-01..08` ตรงตามข้อกำหนด
  5. **การไม่เกิด Regression:**
     - ชุดทดสอบเดิมทั้งหมดของระบบฝั่ง Seller และ Buyer 01, 02 ยังคงผ่าน 100%
- **สถานะ:** การพัฒนา `T-01..08` เสร็จสมบูรณ์ พร้อมส่งมอบงานรอบ Buyer Feature 03


---

## บันทึก #70 — `/clarify specs/buyer/04-job-and-route-management/spec.md` (ตรวจความกำกวมรอบที่ 1 และสรุปการตัดสินใจ)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/04-job-and-route-management/spec.md`
- **ไฟล์ที่อ่าน:** `specs/buyer/04-job-and-route-management/spec.md` (ฉบับร่างเดิม), `specs/SPEC-ROUTE/spec.md`, `specs/SPEC-ROUTE/rules.md`, `specs/SPEC-ROUTE/models.md`, `docs/srs/UC-04.md`, `specs/000-shared/constraints.md`
- **จุดกำกวมที่พบและคำถามที่ถามทีม (`Q-01` ถึง `Q-06`):**
  1. `Q-01` (`CC-04`, `BR-02`): กลไก Atomic Claim ในการป้องกันรับงานซ้ำ (ในร่างเดิมมี Redis Lock ซึ่งขัดกับข้อจำกัดกลาง `CC-04` ที่กำหนดให้ใช้ PostgreSQL OCC)
  2. `Q-02` (`BR-03`, `REQ-CON-003`): ขอบเขต Route Optimization และจำนวนงานที่รับได้ในคิววิ่งสะสม
  3. `Q-03` (`UC-09`, `CC-01`): รูปแบบการเชื่อมต่อระบบนำทาง GPS ใน Mobile-First Web SPA
  4. `Q-04` (`BR-03`, `MD-STM-04`): วงจรชีวิตเมื่อซาเล้งกดยกเลิกงานในสถานะ `S3` หรือ `S4`
  5. `Q-05` (`AC-S05-02`, `AC-S05-04`): ข้อมูลโปรไฟล์ซาเล้งที่ต้องเปิดเผยและส่งแจ้งเตือนให้ผู้ขายทราบเมื่อรับงาน
  6. `Q-06` (`REQ-OP-001`, `CC-05`): พฤติกรรมตารางนัดหมายและการเปลี่ยนสถานะในโหมดออฟไลน์
- **ข้อสรุปการตัดสินใจ (`D-B04-01` ถึง `D-B04-06`):**
  - **`D-B04-01`:** ตัด Redis ออกและใช้ PostgreSQL Optimistic Concurrency Control (`version` column) ตาม `CC-04` และ `BR-02`
  - **`D-B04-02`:** รับงานสะสมในสถานะ `S3` ได้ตราบใดที่น้ำหนักรวมไม่เกินความจุรถ `200 กก.` (`BR-03`) และจัดลำดับด้วย Nearest-Neighbor ตามช่วงเวลานัดหมาย
  - **`D-B04-03`:** การนำทาง GPS ทำงานโดยเปิดแอปนำทางภายนอก (Google Maps / Apple Maps) ผ่าน URL Scheme มาตรฐาน
  - **`D-B04-04`:** เมื่อซาเล้งกดยกเลิกในสถานะ `S3` ระบบจะคืนสถานะคำขอขายกลับเป็น `S2 (Pending)` อัตโนมัติ เพื่อให้ซาเล้งคนอื่นรับต่อได้ทันที และบันทึกลง `audit_logs`
  - **`D-B04-05`:** เมื่อรับงานสำเร็จ ระบบจะผูกข้อมูลซาเล้งและส่ง Event แจ้งเตือนไปยังหน้าจอติดตามของผู้ขายทันที
  - **`D-B04-06`:** แคชตารางงานลงใน `localStorage` ให้เปิดดูที่อยู่จริงและเบอร์โทรได้แม้ออฟไลน์ และเก็บคำขอเปลี่ยนสถานะใน `Offline Queue` พร้อม `idempotency_key`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/04-job-and-route-management/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify` ครบถ้วนทั้ง 5 ส่วนหลัก)
- **สถานะ:** สเปกผ่านการ Clarify เรียบร้อย พร้อมเข้าสู่ขั้นตอน `/plan specs/buyer/04-job-and-route-management/spec.md`


---

## บันทึก #71 — `/plan specs/buyer/04-job-and-route-management/spec.md` (แผนสถาปัตยกรรมและการพัฒนาทางเทคนิค)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/04-job-and-route-management/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/04-job-and-route-management/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ครบ 8 ส่วนหลักตามมาตรฐานโครงการ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (Python 3.11 + FastAPI, Pydantic v2, In-memory Supabase Database Adapter พร้อม OCC version column, React 18 + TailwindCSS Mobile-First SPA ปุ่ม >= 48px, Google Maps Deep Link URL Scheme, Pytest และ Vitest)
  2. **สถาปัตยกรรมและกลไกสำคัญ (`D-B04-01` ถึง `D-B04-06`):**
     - `D-B04-01`: ใช้ PostgreSQL Optimistic Concurrency Control (`version` column) ตรวจสอบเงื่อนไข Atomic Claim หากชนกันตอบกลับ HTTP 409 Conflict `"มีผู้รับงานนี้แล้ว"` ตาม `CC-04` และ `BR-02`
     - `D-B04-02`: รองรับการรับงานสะสมในคิว (`S3`) ตราบใดที่น้ำหนักสะสมไม่เกิน 200 กก. (`BR-03`) และจัดลำดับเส้นทางด้วย Greedy Nearest-Neighbor
     - `D-B04-03`: เชื่อมต่อระบบนำทาง GPS ด้วย Deep Link URL Scheme มาตรฐานเปิดแอปภายนอก (Google Maps / Apple Maps)
     - `D-B04-04`: เมื่อซาเล้งกดยกเลิกในสถานะ `S3` คำขอขายจะคืนสถานะกลับเป็น `S2: รอผู้รับงาน` อัตโนมัติ เพื่อให้ซาเล้งอื่นรับต่อได้ทันที และบันทึกประวัติลง `audit_logs`
     - `D-B04-05`: ส่ง Event แจ้งเตือนข้อมูลซาเล้ง (ชื่อ, เบอร์โทร, ประเภท/ทะเบียนรถ, รูปโปรไฟล์, คะแนนรีวิว) ไปยังหน้าจอติดตามของผู้ขาย (`AC-S05-02..04`)
     - `D-B04-06`: แคชตารางงานลงใน `localStorage` ให้เปิดดูที่อยู่จริงและเบอร์โทรได้แม้ออฟไลน์ และเก็บคำสั่งเปลี่ยนสถานะใน `Offline Queue` พร้อม `idempotency_key`
  3. **การออกแบบ API 5 เส้นทาง:** `POST /jobs/{id}/claim`, `POST /jobs/{id}/skip`, `GET /{saleng_id}/active-jobs`, `POST /jobs/{id}/start-transit`, `POST /jobs/{id}/cancel`
  4. **การออกแบบ Frontend 5 คอมโพเนนต์:** `ActiveJobQueueView`, `ActiveJobCard`, `RouteOptimizationBar`, `CollectorCancelModal`, `ClaimConflictModal` (ทัชทาร์เก็ตทุกปุ่มสูง `>= 48px` ตาม `REQ-UX-001`)
  5. **ตารางตรวจ Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยไม่มีการละเว้น
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/buyer/04-job-and-route-management/plan.md`


---

## บันทึก #72 — `/tasks specs/buyer/04-job-and-route-management/plan.md` (รายการงานย่อยและ Two-way Traceability Matrix)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/04-job-and-route-management/plan.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/04-job-and-route-management/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกเกณฑ์ `AC-B04-01..07`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schemas สำหรับระบบจัดการงานและเส้นทาง (`job_route_models.py`, ขยาย `supabase.py` เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`)
     - `T-02`: สร้าง Service และ API กดรับงานแบบ Single Collector Atomic Claim (OCC version column) ป้องกันรับซ้ำ 409 Conflict และเปิดเผย PII (`AC-B04-01`, `AC-04-05`, `BR-02`, `CC-04`, `REQ-SEC-002`)
     - `T-03`: สร้าง Service และ API ข้ามงาน (Skip Job คงสถานะ S2) และสร้าง URL Scheme เชื่อมต่อระบบนำทาง GPS Google Maps (`AC-B04-02`, `AC-B04-03`, `Extension A2`, `UC-09`, `D-B04-03`)
     - `T-04`: สร้าง Service และ API คิวงานสะสมและการจัดลำดับเส้นทาง Route Optimization ตรวจสอบน้ำหนักสะสมไม่เกิน 200 กก. (`AC-B04-04`, `BR-03`, `REQ-CON-003`, `D-B04-02`)
     - `T-05`: สร้าง Service และ API ออกเดินทาง (Start Transit S3 -> S4 ล็อกปุ่มยกเลิกผู้ขาย) และการยกเลิกงานคืนสถานะกลับ S2 อัตโนมัติ (`AC-B04-05`, `AC-B04-06`, `BR-03`, `MD-STM-04`, `D-B04-04`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชตารางนัดหมาย/คิวออฟไลน์ (`jobRouteApi.js`, `saleng_active_schedule_cache`, `offline_transit_queue` ตาม `CC-05`, `REQ-OP-001`, `D-B04-06`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบจัดการงานและเส้นทาง Mobile-First SPA (Viewport 375px–414px, ทัชทาร์เก็ตปุ่มกด `>= 48px` ตาม `REQ-UX-001` และ `CC-01`: `ActiveJobQueueView`, `ActiveJobCard`, `RouteOptimizationBar`, `CollectorCancelModal`, `ClaimConflictModal`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests (`AC-B04-01.test.jsx` ถึง `AC-B04-06.test.jsx`) และ Backend Integration E2E Test Suite (`test_e2e_buyer_job_route_management.py`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับครบทั้ง 7 ข้อ (`AC-B04-01` ถึง `AC-B04-07`) เชื่อมโยงกับงานย่อยและชื่อชุดทดสอบอย่างสมบูรณ์
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #73 — `/implement T-01..08` (พัฒนาระบบจัดการงานและเส้นทางของซาเล้ง — Buyer 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/04-job-and-route-management/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Schemas (`T-01`):** `backend/app/models/job_route_models.py` (Pydantic models, navigation URL builder), ขยาย `backend/app/core/supabase.py` (เพิ่ม `claim_order_occ`, `revert_order_to_pending`, `get_collector_active_jobs`), และชุดทดสอบ `backend/tests/test_T01_job_route_models.py`
  - **Backend Services & APIs (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/job_route_service.py` (Atomic claim ด้วย OCC version column, skip job, active queue พร้อม greedy route optimization, start transit S3 -> S4 พร้อมล็อกปุ่มยกเลิกผู้ขาย, collector cancel พร้อมคืนสถานะ S2 อัตโนมัติและบันทึก audit log)
    - `backend/app/api/v1/job_route.py` (FastAPI router ติดตั้ง 5 endpoints ภายใต้ `/api/v1/collectors`)
    - `backend/app/api/v1/pricing.py` (Mount router)
  - **Backend Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B04_01_atomic_claim.py`
    - `backend/tests/test_AC_B04_02_skip_job.py`
    - `backend/tests/test_AC_B04_03_address_unmasking.py`
    - `backend/tests/test_AC_B04_04_active_queue_route.py`
    - `backend/tests/test_AC_B04_05_in_transit_lock.py`
    - `backend/tests/test_AC_B04_06_collector_cancel.py`
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/jobRouteApi.js` (Methods: `claimJob`, `skipJob`, `getActiveQueue`, `startTransit`, `cancelJob`, พร้อมแคช `saleng_active_schedule_cache` และคิวออฟไลน์ `saleng_offline_transit_queue` พร้อม `idempotency_key`)
    - `frontend/tests/jobRouteApi.test.mjs` (11 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ActiveJobCard.jsx` (ปุ่มนำทาง GPS, ปุ่มเริ่มเดินทาง, ปุ่มสละสิทธิ์ ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/RouteOptimizationBar.jsx` (แถบ Waypoint timeline, ระยะทางรวม, ETA)
    - `frontend/src/components/CollectorCancelModal.jsx` (Modal สละสิทธิ์ 4 เหตุผล พร้อมระบุหมายเหตุ)
    - `frontend/src/components/ClaimConflictModal.jsx` (Modal แจ้งเตือนเมื่อเกิด 409 Conflict "มีผู้รับงานนี้แล้ว")
    - `frontend/src/components/ActiveJobQueueView.jsx` (หน้ารวมคิวงานสะสม, แถบความจุรถ, และ Offline banner)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B04-01.test.jsx` (Single Collector Atomic Claim & 409 Conflict Modal)
    - `frontend/tests/AC-B04-02.test.jsx` (Skip Job Option)
    - `frontend/tests/AC-B04-03.test.jsx` (Address Unmasking & GPS Navigation Launch)
    - `frontend/tests/AC-B04-04.test.jsx` (Active Queue & Route Ordering)
    - `frontend/tests/AC-B04-05.test.jsx` (In-Transit Status Transition & Seller Cancel Lock)
    - `frontend/tests/AC-B04-06.test.jsx` (Collector Cancellation with Automatic State Reversion)
    - `backend/tests/test_e2e_buyer_job_route_management.py` (6 integration lifecycle tests)
  - **Task Checklist:** อัปเดต `specs/buyer/04-job-and-route-management/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-04`, `UC-09`, `UC-12`, `BR-02`, `BR-03`, `AC-B04-01..07` และการตัดสินใจ `D-B04-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** นำทาง GPS ใช้ URL Scheme ภายนอก, Concurrency ใช้ OCC `version` column, ยกเลิกงานคืนสถานะ S2 และเคลียร์ `collector_id = None` ตามกฎ
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache & queue (`CC-05`, `REQ-OP-001`), PII Masking ก่อนรับงาน (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **208 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **71 test files passed, 178 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-03) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 04: ระบบจัดการงานและเส้นทาง (`specs/buyer/04-job-and-route-management/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%

---

## บันทึก #74 — `/clarify specs/buyer/05-communication/spec.md` (รอบที่ 1: ตรวจสอบความกำกวมก่อนวางแผน)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/05-communication/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/05-communication/spec.md` (v1.0), `specs/000-shared/constraints.md`, `specs/seller/03-buyer-search-and-selection/spec.md`, `specs/seller/08-notifications-and-help/spec.md`, `docs/srs/use-cases.md` (`UC-08`)
- **จุดกำกวมที่ AI ตรวจพบ (6 ประเด็น):**
  1. `Q-01` (`REQ-SEC-002`, `CC-06`): สิทธิ์การแชตและดูข้อมูลผู้ขายในสถานะ `S2` (Direct Request) ว่าอนุญาตให้แชตได้หรือไม่ และจะ Mask PII อย่างไร
  2. `Q-02` (`REQ-FN-003`, `CC-01`): เทคโนโลยีโทรด่วน (Quick Call) ว่าใช้ Native Phone Dialer (`tel:<phone>`) และกำหนดให้ In-App VoIP เป็น Non-goals หรือไม่
  3. `Q-03` (`REQ-UX-001`, `Digital Literacy`): รายการชุดข้อความด่วนสำเร็จรูป (Quick Replies) 4 ข้อความมาตรฐาน และการเปิดช่องพิมพ์ข้อความอิสระ
  4. `Q-04` (`REQ-FN-003`, `CC-01`): ขอบเขตประเภทสื่อในแชต กำหนดให้รูปภาพและข้อความเสียงเป็น Non-goals ในเฟสนี้
  5. `Q-05` (`REQ-SEC-002`, `MD-STM-04`): การปิดห้องแชตเป็น Read-Only และซ่อนปุ่มโทรด่วนทันทีเมื่อจบงาน (`S7`) หรือยกเลิก (`S8`) เพื่อความปลอดภัยข้อมูลส่วนบุคคล (PDPA)
  6. `Q-06` (`REQ-OP-001`, `CC-05`): การแคชประวัติแชตใน `localStorage` ให้เปิดดูได้แม้ออฟไลน์ และปิดการส่งข้อความใหม่เมื่อไม่มีเน็ต
- **ข้อสรุปการตัดสินใจ (`D-B05-01` ถึง `D-B05-06`):**
  - **`D-B05-01`:** อนุญาตให้เปิดแชตได้ใน `S2` กรณี Direct Request โดยระบบจะ Mask เบอร์โทรศัพท์และบ้านเลขที่จริงของผู้ขาย จนกว่าซาเล้งจะกดยืนยันรับงาน (`S3`)
  - **`D-B05-02`:** ปุ่มโทรด่วนทำงานโดยเปิด Native Phone Dialer (`tel:<phone>`) ของอุปกรณ์โดยตรง และไม่ทำ In-App VoIP ตาม `CC-01`
  - **`D-B05-03`:** ติดตั้ง 4 ข้อความด่วนมาตรฐาน (กำลังเดินทางไปครับ, ถึงหน้าบ้านแล้วครับ, ช่วยออกมารับหน่อยครับ, ขอเลื่อนเวลาประมาณ 15 นาทีครับ) พร้อมช่องพิมพ์ข้อความอิสระ
  - **`D-B05-04`:** แชตรองรับเฉพาะข้อความและ Quick Replies ส่วนรูปภาพและข้อความเสียงกำหนดเป็น Non-goals
  - **`D-B05-05`:** เมื่อเข้าสู่สถานะ `S7 (สำเร็จ)` หรือ `S8 (ยกเลิก)` ล็อกห้องแชตเป็น Read-only ทันที และซ่อนปุ่มโทรด่วนเพื่อคุ้มครอง PDPA
  - **`D-B05-06`:** แคชประวัติแชตลง `localStorage` (`saleng_chat_cache_{order_id}`) เปิดดูได้แม้ออฟไลน์ แต่ไม่อนุญาตให้ส่งข้อความใหม่จนกว่าจะมีสัญญาณเน็ต
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/05-communication/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify` ครบทั้ง 5 ส่วนหลัก)
- **สถานะ:** สเปกผ่านการ Clarify เรียบร้อย พร้อมเข้าสู่ขั้นตอน `/plan specs/buyer/05-communication/spec.md`

---

## บันทึก #75 — `/plan specs/buyer/05-communication/spec.md` (แผนสถาปัตยกรรมและการพัฒนาทางเทคนิค)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/05-communication/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/05-communication/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ครบ 8 ส่วนหลักตามมาตรฐานโครงการ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (Python 3.11 + FastAPI, Pydantic v2, In-memory Supabase Database Adapter พร้อมตาราง `chat_messages`, React 18 + TailwindCSS Mobile-First SPA ปุ่ม >= 48px, Native Phone Dialer URL Scheme `tel:<phone>`, Pytest และ Vitest)
  2. **สถาปัตยกรรมและกลไกสำคัญ (`D-B05-01` ถึง `D-B05-06`):**
     - `D-B05-01`: ในสถานะ `S2` (Direct Request) เปิดให้แชตได้ แต่ปิดบังเบอร์โทรศัพท์และที่อยู่จริงของผู้ขาย จนกว่าจะรับงานเข้าสู่สถานะ `S3` ตาม `REQ-SEC-002` และ `CC-06`
     - `D-B05-02`: ปุ่มโทรด่วนเปิด Native Phone Dialer (`tel:<phone>`) โดยตรง และกำหนดให้ In-App VoIP เป็น Non-goals เพื่อประหยัด RAM/CPU บนมือถือตาม `CC-01`
     - `D-B05-03`: ติดตั้งแถบข้อความด่วนสำเร็จรูป 4 ข้อความมาตรฐาน (กำลังเดินทางไปครับ, ถึงหน้าบ้านแล้วครับ, ช่วยออกมารับหน่อยครับ, ขอเลื่อนเวลาประมาณ 15 นาทีครับ) ขนาดปุ่ม `>= 48px` รองรับ Digital Literacy
     - `D-B05-04`: แชตรองรับเฉพาะข้อความและ Quick Replies ส่วนรูปภาพและข้อความเสียงกำหนดเป็น Non-goals ในเฟสนี้
     - `D-B05-05`: เมื่อเข้าสู่สถานะ `S7 (สำเร็จ)` หรือ `S8 (ยกเลิก)` ล็อกห้องแชตเป็น Read-Only ทันที และซ่อนปุ่มโทรด่วนเพื่อคุ้มครองข้อมูลส่วนบุคคลตาม PDPA
     - `D-B05-06`: แคชประวัติแชตลง `localStorage` (`saleng_chat_cache_{order_id}`) เปิดดูได้แม้ออฟไลน์ และปิดการส่งข้อความใหม่เมื่อไม่มีเน็ต
  3. **การออกแบบ API 4 เส้นทาง:**
     - `GET /api/v1/collectors/chat/{order_id}/messages` (ดึงประวัติข้อความ ข้อมูลคู่สนทนา และสิทธิ์ Read-Only)
     - `POST /api/v1/collectors/chat/{order_id}/messages` (ส่งข้อความใหม่ / Quick Reply)
     - `POST /api/v1/collectors/chat/{order_id}/call-log` (บันทึก Audit Log การกดโทรด่วน)
     - `GET /api/v1/collectors/chat/quick-replies` (ดึงรายการ 4 ข้อความด่วนมาตรฐาน)
  4. **การออกแบบ Frontend 6 คอมโพเนนต์:**
     - `ChatView`, `ChatHeader`, `ChatMessageList`, `QuickRepliesBar`, `ChatInputBar`, `ReadOnlyNoticeBanner` (ทัชทาร์เก็ตทุกปุ่มสูง `>= 48px` ตาม `REQ-UX-001` และ `CC-01`)
  5. **ตารางตรวจ Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยไม่มีการละเว้น
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/buyer/05-communication/plan.md`

---

## บันทึก #76 — `/tasks specs/buyer/05-communication/plan.md` (แตกงานย่อยระบบสื่อสาร Buyer 05)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/05-communication/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/05-communication/spec.md` (v2.0), `specs/buyer/05-communication/plan.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-08`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/05-communication/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-B05-01..06`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบสื่อสาร (`communication_models.py`, ขยาย `supabase.py` เพิ่มตาราง `chat_messages` และ helper methods, `test_T01_communication_models.py`)
     - `T-02`: สร้าง Service และ API ส่งและดึงข้อความแชต (`communication_service.py`, `communication.py`, `pricing.py`, `test_AC_B05_01_chat_messaging.py`)
     - `T-03`: สร้าง Service และ API ข้อความด่วนสำเร็จรูป Quick Replies 4 รูปแบบ (`test_AC_B05_02_quick_replies.py`, `REQ-UX-001`, `CC-01`, `D-B05-03`)
     - `T-04`: สร้าง Service และ API ปุ่มโทรด่วน Native Quick Call & Audit Logging (`test_AC_B05_03_quick_call.py`, `REQ-SEC-001`, `CC-01`, `D-B05-02`)
     - `T-05`: สร้าง Pre-Claim Privacy Guard ในสถานะ S2 และ Post-Transaction Read-Only Guard ในสถานะ S7/S8 (`test_AC_B05_04_pre_claim_pdpa.py`, `test_AC_B05_05_post_job_lock.py`, `REQ-SEC-002`, `CC-06`, `MD-STM-04`, `D-B05-01`, `D-B05-05`)
     - `T-06`: สร้าง Frontend API Client และระบบแคชแชตออฟไลน์ใน `localStorage` (`communicationApi.js`, `communicationApi.test.mjs`, `CC-05`, `REQ-OP-001`, `D-B05-06`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบสื่อสาร (`ChatView`, `ChatHeader`, `ChatMessageList`, `QuickRepliesBar`, `ChatInputBar`, `ReadOnlyNoticeBanner` ทัชทาร์เก็ตทุกปุ่ม >= 48px ตาม `REQ-UX-001` และ `CC-01`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-B05-01..06`, `test_e2e_buyer_communication.py`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-B05-01` ถึง `AC-B05-06`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #77 — `/implement T-01..08` (พัฒนาระบบสื่อสาร Buyer 05 ครบถ้วน)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08` (อ้างอิง `specs/buyer/05-communication/tasks.md`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - **Backend Models & Database Schema (`T-01`):**
    - `backend/app/models/communication_models.py` (Pydantic models: `ChatMessage`, `SendChatMessageRequest`, `ChatMessageResponse`, `SellerContactInfo`, `ChatRoomResponse`, `LogCallRequest`, `LogCallResponse`, `QuickReplyItem`, `QuickRepliesResponse`, พร้อม `DEFAULT_QUICK_REPLIES` 4 ข้อความมาตรฐาน)
    - `backend/app/core/supabase.py` (เพิ่มตาราง `chat_messages`, เมธอด `get_order_chat_messages`, `send_chat_message`, และ `log_communication_audit`)
    - `backend/tests/test_T01_communication_models.py` (5 unit tests ผ่าน 100%)
  - **Backend Services & API Router (`T-02`, `T-03`, `T-04`, `T-05`):**
    - `backend/app/services/communication_service.py` (`CommunicationService` ตรวจสอบสิทธิ์ KYC `D-00-01`, ตรรกะ PDPA Masking เบอร์โทรใน `S2`, เปิดเผยเบอร์ใน `S3..S6`, ล็อกห้องแชต Read-only ใน `S7/S8`, ตรวจสอบความยาวข้อความ 1-500 ตัวอักษร, บันทึก Audit Log ทุกข้อความและการโทร)
    - `backend/app/api/v1/communication.py` (FastAPI Router สำหรับ `GET /quick-replies`, `GET /{order_id}/messages`, `POST /{order_id}/messages`, `POST /{order_id}/call-log`)
    - `backend/app/api/v1/pricing.py` (เมานต์ `communication_router` ภายใต้ `/api/v1/collectors`)
  - **Backend Acceptance Tests (`T-02` ถึง `T-05`):**
    - `backend/tests/test_AC_B05_01_chat_messaging.py` (3 tests ผ่าน 100%)
    - `backend/tests/test_AC_B05_02_quick_replies.py` (2 tests ผ่าน 100%)
    - `backend/tests/test_AC_B05_03_quick_call.py` (3 tests ผ่าน 100%)
    - `backend/tests/test_AC_B05_04_pre_claim_pdpa.py` (3 tests ผ่าน 100%)
    - `backend/tests/test_AC_B05_05_post_job_lock.py` (3 tests ผ่าน 100%)
  - **Frontend API Client & Cache (`T-06`):**
    - `frontend/src/services/communicationApi.js` (Methods: `getQuickReplies`, `getMessages`, `sendMessage`, `sendQuickReply`, `logCall`, พร้อมระบบแคช `localStorage` คีย์ `saleng_chat_cache_{order_id}` และ fallback ออฟไลน์)
    - `frontend/tests/communicationApi.test.mjs` (7 unit tests ผ่าน 100%)
  - **Frontend React Components (`T-07`):**
    - `frontend/src/components/ChatHeader.jsx` (ส่วนหัวห้องแชต, ป้ายสถานะคำขอ, ปุ่มโทรด่วน Native Quick Call `tel:<phone>` ทัชทาร์เก็ต >= 48px พร้อมล็อกใน S2 และซ่อนใน S7/S8)
    - `frontend/src/components/ChatMessageList.jsx` (ฟีดข้อความแยกฝั่ง ซาเล้งเขียวมรกต vs ผู้ขายเทาอ่อน พร้อมป้าย `ส่งด่วน ⚡`)
    - `frontend/src/components/QuickRepliesBar.jsx` (แถบ 4 ปุ่มลัดข้อความด่วน เลื่อนแนวนอน ทัชทาร์เก็ต >= 48px)
    - `frontend/src/components/ChatInputBar.jsx` (ช่องพิมพ์ข้อความอิสระและปุ่มส่ง >= 48px พร้อมล็อกเมื่อ Read-only หรือออฟไลน์)
    - `frontend/src/components/ReadOnlyNoticeBanner.jsx` (แบนเนอร์แจ้งเตือนห้องแชตล็อก Read-only ตามกฎหมาย PDPA)
    - `frontend/src/components/ChatView.jsx` (หน้าจอหลักห้องแชตรวบรวมทุกคอมโพเนนต์ พร้อมป้ายแจ้งเตือนโหมดออฟไลน์)
  - **Frontend Component Tests & Integration E2E Suite (`T-08`):**
    - `frontend/tests/AC-B05-01.test.jsx` (In-App Direct Chat Messaging)
    - `frontend/tests/AC-B05-02.test.jsx` (Quick Replies Preset Bar ทัชทาร์เก็ต >= 48px)
    - `frontend/tests/AC-B05-03.test.jsx` (Native Quick Call Launch tel: protocol)
    - `frontend/tests/AC-B05-04.test.jsx` (Pre-Claim Privacy Guard Masking ใน S2)
    - `frontend/tests/AC-B05-05.test.jsx` (Post-Transaction Privacy Guard Read-Only ใน S7/S8)
    - `frontend/tests/AC-B05-06.test.jsx` (Offline Chat History Cache & Banner)
    - `backend/tests/test_e2e_buyer_communication.py` (2 integration lifecycle tests S2 -> S3 -> S4 -> S7 และ KYC Guard)
  - **Task Checklist:** อัปเดต `specs/buyer/05-communication/tasks.md` เป็นสถานะ `completed` (`T-01..08` เป็น `[DONE]`)
- **การตรวจสอบ 5 ด่านก่อนจบงาน:**
  1. **สเปกตรง 100%:** ทุกฟังก์ชันรองรับ `UC-08`, `MD-STM-04`, `AC-B05-01..06` และการตัดสินใจ `D-B05-01..06` ครบถ้วน
  2. **ไม่มีโค้ดเดาเอง:** ไม่ทำ In-App VoIP/WebRTC ตาม Non-goals (ใช้ Native Phone Dialer `tel:`), ข้อความด่วน 4 รูปแบบตรงตามสเปก, และล็อกห้องแชต Read-only อัตโนมัติเมื่อสิ้นสุดงาน
  3. **ไม่ละเมิด Constraints:** Mobile-first ปุ่มกด >= 48px (`REQ-UX-001`, `CC-01`), Offline cache ใน `localStorage` (`CC-05`, `REQ-OP-001`), PDPA Masking เบอร์โทรใน S2 และ S7/S8 (`REQ-SEC-002`, `CC-06`), Audit Logging (`REQ-SEC-001`)
  4. **Automated Tests ผ่าน 100%:**
     - Backend (Pytest): **229 passed, 0 failed** (ครอบคลุมโมเดล, ทุก AC, และ E2E)
     - Frontend (Vitest): **78 test files passed, 193 tests passed, 0 failed** (ครอบคลุม API client, ทุก AC component test)
  5. **Zero Regression:** ชุดทดสอบเดิมทั้งหมดของระบบผู้ขาย (Seller 01-09) และระบบผู้ซื้อ (Buyer 01-04) ยังคงผ่าน 100% ไม่มีข้อผิดพลาด
- **สถานะ:** ฟีเจอร์ Buyer 05: ระบบสื่อสาร (`specs/buyer/05-communication/`) พัฒนาและตรวจรับเสร็จสมบูรณ์ 100%

---

## บันทึก #78 — `/clarify specs/buyer/06-billing-and-receipt/spec.md` (รอบที่ 1: ตรวจสอบความกำกวมก่อนวางแผน)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/06-billing-and-receipt/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/06-billing-and-receipt/spec.md` (v1.0), `specs/seller/06-payment-and-verification/spec.md`, `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-05`, `UC-06`, `UC-07`), `specs/002-route/models.md` (`MD-STM-04`)
- **จุดกำกวมที่ AI ตรวจพบ (6 ประเด็น):**
  1. `Q-01` (`MD-STM-04`, `use-cases.md`): ลำดับสถานะ State Machine เดิมขัดกับระบบกลาง ปรับเป็น `S4 (ชั่งน้ำหนักหน้างาน)` -> `S5 (ผู้ขายตรวจน้ำหนัก/ใบเสนอราคาใหม่)` -> `S6 (ชำระเงิน)` -> `S7 (สำเร็จ/ออกใบเสร็จ)` และอ้างอิง `UC-05`, `UC-06`, `UC-07`
  2. `Q-02` (`REQ-FN-002`, `UC-05`): บังคับแนบรูปถ่ายหน้าตาชั่งดิจิทัล (`scale_photo_url`) อย่างน้อย 1 ภาพ เพื่อส่งให้ผู้ขายตรวจสอบความโปร่งใส
  3. `Q-03` (`REQ-BR-002`, `REQ-DAT-001`): การคำนวณยอดเงินสุทธิหน้างานต้องใช้ราคาต่อหน่วยที่ล็อกไว้ตอนนัดหมาย (`locked_unit_price`) คูณกับน้ำหนักจริง
  4. `Q-04` (`UC-07`, `Payment Confirmation`): ซาเล้งเลือกช่องทางจ่ายเงิน (เงินสด/PromptPay QR) และผู้ขายเป็นผู้กดยืนยันรับเงินเพื่อเปลี่ยนสถานะเป็น `S7` (Completed)
  5. `Q-05` (`CT-02`, `CC-05`, `REQ-OP-001`): โหมดกึ่งออฟไลน์ในจุดอับสัญญาณขณะชั่งน้ำหนัก บันทึกลง `localStorage` (`saleng_weighing_offline_queue`) พร้อม `idempotency_key` เพื่อซิงก์เมื่อต่อเน็ต
  6. `Q-06` (`REQ-FN-005`, `REQ-SEC-002`, `SC-03`): โครงสร้างใบเสร็จดิจิทัล (`DigitalReceipt`) รหัสไม่ซ้ำ สรุปรายการน้ำหนักและยอดเงินสุทธิ พร้อม Mask เบอร์โทรศัพท์เป็น `08X-XXX-XXXX`
- **ข้อสรุปการตัดสินใจ (`D-B06-01` ถึง `D-B06-06`):**
  - **`D-B06-01`:** ยึดตาม `MD-STM-04` ปรับลำดับสถานะเป็น `S4 -> S5 -> S6 -> S7` และอ้างอิง `UC-05`, `UC-06`, `UC-07`
  - **`D-B06-02`:** บังคับแนบรูปถ่ายหน้าตาชั่งดิจิทัล (`scale_photo_url`) เมื่อกรอกน้ำหนักชั่งจริง
  - **`D-B06-03`:** คำนวณยอดเงินด้วยราคาต่อหน่วยที่ล็อกไว้ตอนนัดหมาย (`locked_unit_price`) ตาม `REQ-BR-002`
  - **`D-B06-04`:** ซาเล้งเลือกช่องทางชำระเงิน (เงินสด/PromptPay) และให้ผู้ขายเป็นผู้กดยืนยันรับเงินเพื่อเปลี่ยนสถานะเป็น `S7`
  - **`D-B06-05`:** บันทึกข้อมูลผลชั่งและภาพตาชั่งลง Offline Queue ใน `localStorage` เมื่ออยู่ในจุดอับสัญญาณ
  - **`D-B06-06`:** ออกใบเสร็จดิจิทัลอัตโนมัติเมื่อเข้าสู่ `S7` พร้อม Mask เบอร์โทรศัพท์ตามกฎหมาย PDPA
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/06-billing-and-receipt/spec.md` (ปรับปรุงเป็น Version `2.0`, สถานะ `reviewed-post-clarify` ครบทั้ง 5 ส่วนหลัก)
- **สถานะ:** สเปกผ่านการ Clarify เรียบร้อย พร้อมเข้าสู่ขั้นตอน `/plan specs/buyer/06-billing-and-receipt/spec.md`

---

## บันทึก #79 — `/plan specs/buyer/06-billing-and-receipt/spec.md` (แผนสถาปัตยกรรมและการพัฒนาทางเทคนิค)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/06-billing-and-receipt/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/06-billing-and-receipt/plan.md` (Version `1.0`, สถานะ `ready-for-tasks`, ครบ 8 ส่วนหลักตามมาตรฐานโครงการ)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยีที่ใช้:** ระบุกำกับชัดเจนว่า `"ทีมเลือกเอง ไม่ได้มาจาก spec"` (Python 3.11 + FastAPI, Pydantic v2, In-memory Supabase Database Adapter พร้อมตาราง `orders`, `items`, `receipts`, `audit_logs`, React 18 + TailwindCSS Mobile-First SPA ปุ่ม >= 48px, PromptPay EMVCo QR Protocol, LocalStorage Offline Queue, Pytest และ Vitest)
  2. **สถาปัตยกรรมและกลไกสำคัญ (`D-B06-01` ถึง `D-B06-06`):**
     - `D-B06-01`: ยึดผังสถานะตาม `MD-STM-04` และ `use-cases.md` อย่างเคร่งครัด (`S4: Weighing` -> `S5: Re-Quote/Weight Confirmed` -> `S6: Pending Payment` -> `S7: Completed`)
     - `D-B06-02`: บังคับแนบรูปถ่ายหน้าตาชั่งดิจิทัล (`scale_photo_url`) อย่างน้อย 1 ภาพ เพื่อส่งให้ผู้ขายตรวจสอบความโปร่งใสตาม `REQ-FN-002`
     - `D-B06-03`: คำนวณยอดเงินสุทธิหน้างานโดยใช้ราคาต่อหน่วยที่ล็อกไว้ตอนนัดหมาย (`locked_unit_price`) คูณกับน้ำหนักจริงตาม `REQ-BR-002`
     - `D-B06-04`: ซาเล้งเลือกจ่ายด้วยเงินสดหรือ PromptPay QR และให้ผู้ขายเป็นผู้กดยืนยันรับเงินเพื่อเปลี่ยนสถานะเป็น `S7` ตามสเปก Seller 06
     - `D-B06-05`: บันทึกข้อมูลผลชั่งและภาพตาชั่งลง Offline Queue ใน `localStorage` (`saleng_weighing_offline_queue`) พร้อม `idempotency_key` เมื่ออยู่ในจุดอับสัญญาณ (`CT-02`, `CC-05`, `REQ-OP-001`)
     - `D-B06-06`: ออกใบเสร็จดิจิทัลอัตโนมัติ (`REC-YYYYMMDD-XXXX`) พร้อม Mask เบอร์โทรศัพท์เป็น `08X-XXX-XXXX` ตามกฎหมาย PDPA (`REQ-SEC-002`, `SC-03`)
  3. **การออกแบบ API 4 เส้นทาง:**
     - `GET /api/v1/collectors/billing/{order_id}/weighing-sheet` (ดึงข้อมูลใบชั่งและราคาล็อก)
     - `POST /api/v1/collectors/billing/{order_id}/weighing` (บันทึกน้ำหนักจริง + ภาพตาชั่ง)
     - `POST /api/v1/collectors/billing/{order_id}/payment-method` (เลือกช่องทางชำระเงิน)
     - `GET /api/v1/collectors/billing/{order_id}/receipt` (ดึงใบเสร็จดิจิทัลสรุปรายการ)
  4. **การออกแบบ Frontend 5 คอมโพเนนต์:**
     - `WeighingInputForm`, `SellerConfirmationGate`, `PaymentMethodSelector`, `DigitalReceiptCard`, `BillingReceiptView` (ทัชทาร์เก็ตทุกปุ่มสูง `>= 48px` ตาม `REQ-UX-001` และ `CC-01`)
  5. **ตารางตรวจ Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยไม่มีการละเว้น
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/buyer/06-billing-and-receipt/plan.md`

---

## บันทึก #80 — `/tasks specs/buyer/06-billing-and-receipt/plan.md` (แตกงานย่อยระบบคิดเงินและออกใบเสร็จ Buyer 06)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/06-billing-and-receipt/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/06-billing-and-receipt/spec.md` (v2.0), `specs/buyer/06-billing-and-receipt/plan.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-05`, `UC-06`, `UC-07`), `specs/002-route/models.md` (`MD-STM-04`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/06-billing-and-receipt/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-B06-01..06`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบคิดเงินและออกใบเสร็จ (`billing_models.py`, ขยาย `supabase.py` เพิ่ม helper methods `get_order_weighing_sheet`, `update_order_payment_method`, และ `test_T01_billing_models.py`)
     - `T-02`: สร้าง Service และ API บันทึกน้ำหนักชั่งจริงและแนบภาพถ่ายหน้าตาชั่งดิจิทัล (`billing_service.py`, `billing.py`, `pricing.py`, `test_AC_B06_01_actual_weight.py`)
     - `T-03`: สร้าง Logic คำนวณยอดเงินตามราคาที่ล็อกไว้ (`locked_unit_price`) และการตรวจเกณฑ์ส่วนต่าง `±15%` ปรับสถานะเป็น S5 (`test_AC_B06_02_price_calc.py`, `REQ-BR-002`)
     - `T-04`: สร้างระบบและ API ประตูยืนยันผลชั่งโดยผู้ขาย Seller Confirmation Gate 100% Lock (`test_AC_B06_03_seller_gate.py`, `REQ-FN-004`, `UC-06`)
     - `T-05`: สร้าง Service และ API เลือกช่องทางชำระเงิน (เงินสด/PromptPay) และออกใบเสร็จดิจิทัล (`test_AC_B06_04_payment_method.py`, `test_AC_B06_05_digital_receipt.py`, `REQ-FN-005`, `REQ-SEC-002`)
     - `T-06`: สร้าง Frontend API Client และระบบคิวออฟไลน์ (`billingReceiptApi.js`, `billingReceiptApi.test.mjs`, `CT-02`, `CC-05`, `REQ-OP-001`)
     - `T-07`: พัฒนาคอมโพเนนต์ React ระบบคิดเงินและออกใบเสร็จ (`WeighingInputForm`, `SellerConfirmationGate`, `PaymentMethodSelector`, `DigitalReceiptCard`, `BillingReceiptView` ทัชทาร์เก็ตทุกปุ่ม >= 48px ตาม `REQ-UX-001` และ `CC-01`)
     - `T-08`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests และ Backend Integration E2E Test Suite (`AC-B06-01..06`, `test_e2e_buyer_billing_receipt.py`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-B06-01` ถึง `AC-B06-06`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #81 — `/implement T-01..08` (พัฒนาระบบคิดเงินและออกใบเสร็จ Buyer 06)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/06-billing-and-receipt/spec.md` (v2.0), `specs/buyer/06-billing-and-receipt/plan.md` (v1.0), `specs/buyer/06-billing-and-receipt/tasks.md` (v1.0), `specs/000-shared/constraints.md`, `specs/seller/06-payment-and-verification/spec.md`, `backend/app/api/v1/payment.py`, `backend/app/services/payment_service.py`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/billing_models.py` (สร้าง Data Models Pydantic สำหรับคำขอบันทึกผลชั่งจริง, ใบชั่งน้ำหนัก, การเลือกช่องทางชำระเงิน, และใบเสร็จดิจิทัล)
  - `backend/app/core/supabase.py` (เพิ่ม helper methods `get_order_weighing_sheet` และ `update_order_payment_method`)
  - `backend/app/services/billing_service.py` (สร้าง BillingService: จัดการใบชั่ง, บันทึกผลชั่งจริง, คำนวณราคาด้วย `locked_unit_price`, ตรวจเกณฑ์ส่วนต่าง `±15%`, ตรวจสอบประตูกั้นยืนยันน้ำหนัก 100% `seller_confirmed_weight`, บันทึกช่องทางชำระเงิน, และออกใบเสร็จดิจิทัลพร้อม Masking เบอร์โทรศัพท์)
  - `backend/app/api/v1/billing.py` (สร้าง FastAPI Router 4 endpoints: `GET /{order_id}/weighing-sheet`, `POST /{order_id}/weighing`, `POST /{order_id}/payment-method`, `GET /{order_id}/receipt`)
  - `backend/app/api/v1/pricing.py` (เมานต์ billing router ภายใต้ prefix `/api/v1/collectors`)
  - `frontend/src/services/billingReceiptApi.js` (สร้าง Frontend API Client พร้อมระบบ Offline Queue `saleng_weighing_offline_queue`, `idempotency_key`, และการซิงก์อัตโนมัติเมื่อต่อเน็ต)
  - `frontend/src/components/WeighingInputForm.jsx` (คอมโพเนนต์ฟอร์มกรอกน้ำหนักจริง, แนบรูปตาชั่งดิจิทัล, แสดงยอดคำนวณสด, และแจ้งเตือนเกณฑ์ ±15%)
  - `frontend/src/components/SellerConfirmationGate.jsx` (คอมโพเนนต์ประตูกั้น 100% Confirmation Gate ล็อกไม่ให้ข้ามไปชำระเงินจนกว่าผู้ขายจะกดยืนยัน)
  - `frontend/src/components/PaymentMethodSelector.jsx` (คอมโพเนนต์เลือกเงินสด หรือ PromptPay QR พร้อมคำแนะนำ)
  - `frontend/src/components/DigitalReceiptCard.jsx` (ปรับปรุงรองรับทั้ง Buyer และ Seller receipt models พร้อม PII Masking)
  - `frontend/src/components/BillingReceiptView.jsx` (คอมโพเนนต์หน้าจอหลักรวบรวมทุกขั้นตอนคิดเงินและออกใบเสร็จ `data-req="UC-07"`)
  - `backend/tests/test_T01_billing_models.py` (ทดสอบ Models และ Store methods)
  - `backend/tests/test_AC_B06_01_actual_weight.py` (ทดสอบ AC-B06-01 บันทึกน้ำหนักจริงและภาพตาชั่ง)
  - `backend/tests/test_AC_B06_02_price_calc.py` (ทดสอบ AC-B06-02 คำนวณด้วยราคาล็อกและตรวจเกณฑ์ ±15%)
  - `backend/tests/test_AC_B06_03_seller_gate.py` (ทดสอบ AC-B06-03 ประตูกั้น 100% Seller Confirmation Gate)
  - `backend/tests/test_AC_B06_04_payment_method.py` (ทดสอบ AC-B06-04 เลือกช่องทางชำระเงินสด/PromptPay)
  - `backend/tests/test_AC_B06_05_digital_receipt.py` (ทดสอบ AC-B06-05 ออกใบเสร็จดิจิทัลและ Mask เบอร์โทรศัพท์)
  - `backend/tests/test_e2e_buyer_billing_receipt.py` (ทดสอบ E2E เต็มวงรอบ S4 -> S5 -> S6 -> S7)
  - `frontend/tests/billingReceiptApi.test.mjs` (ทดสอบ Vitest สำหรับ API client และ Offline queue)
  - `frontend/tests/AC-B06-01.test.jsx` ถึง `AC-B06-06.test.jsx` (ทดสอบ Vitest UI Component tests)
  - `specs/buyer/06-billing-and-receipt/tasks.md` (อัปเดตสถานะงาน `T-01` ถึง `T-08` เป็น `[DONE]` และภาพรวมเป็น `completed`)
- **ผลการทดสอบและการตรวจรับ 5 ด่าน:**
  1. **Automated Tests:**
     - Backend (Pytest): ผ่าน 100% รวม 251 passed (0 failed)
     - Frontend (Vitest): ผ่าน 100% รวม 85 test files, 214 passed (0 failed)
  2. **Constraints กลาง:** ปฏิบัติตามครบถ้วน (`CC-01` ปุ่ม >= 48px, `CC-04` Optimistic concurrency, `CC-05` Offline queue, `CC-06` / `REQ-SEC-002` PII masking `08X-XXX-XXXX`, `D-00-01` KYC gate)
  3. **Traceability:** ฟังก์ชันและคอมโพเนนต์ทุกชิ้นอ้างอิง `UC-05`, `UC-06`, `UC-07`, `REQ-FN-002`, `REQ-FN-004`, `REQ-FN-005`, `REQ-BR-002`, `AC-B06-01..06` ครบถ้วน
  4. **Mockups:** โครงสร้างป้ายภาษาไทย, ขนาดปุ่มสัมผัส >= 48px, และแอตทริบิวต์ `data-req="UC-07"` ครบถ้วน
  5. **Non-goals:** ไม่มี In-App digital wallet หรือ payment gateway SDK ตามขอบเขต `D-B06-04` และบังคับใช้ Two-Party Safety Gate 100%
- **สถานะ:** พัฒนาและตรวจรับระบบคิดเงินและออกใบเสร็จ Buyer 06 สำเร็จสมบูรณ์ พร้อมส่งมอบงาน

---

## บันทึก #82 — `/clarify specs/buyer/07-post-job/spec.md` (เคลียร์จุดกำกวมระบบหลังจบงาน Buyer 07)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/buyer/07-post-job/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/07-post-job/spec.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-10`, `UC-13`), `specs/002-route/models.md` (`MD-STM-04`), `specs/seller/07-post-transaction/spec.md`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/07-post-job/spec.md` (ยกระดับเป็น Version `2.0`, สถานะ `reviewed-post-clarify`, เพิ่มตาราง Resolved Questions `Q-01` ถึง `Q-06`)
- **ประเด็นคำถามและข้อสรุปที่ทีมเห็นชอบ:**
  1. `Q-01` (สถานะปลายทางของการรายงานผู้ขาย): เปลี่ยนสถานะเป็น `S8: Disputed` ส่งเรื่องเข้าคิว Admin (`UC-13`, `UC-11`) และปลดล็อกซาเล้งออกจากงานเพื่อไปรับงานถัดไปในคิวได้
  2. `Q-02` (จุดที่รายงานผู้ขายได้): อนุญาตให้รายงานได้ทั้งในสถานะ `S3: En Route` (กรณี No-show) และ `S4: Weighing` (กรณีของปนเปื้อน/ไม่ตรงสเปกอย่างมาก)
  3. `Q-03` (ข้อมูลลูกค้าประจำตาม PDPA): จัดเก็บลงตาราง `collector_favorite_sellers` ประกอบด้วย `collector_id`, `seller_id`, พิกัด (`latitude`, `longitude`), ป้ายชื่อ/บันทึกย่อส่วนตัว, และ Mask เบอร์โทรศัพท์เป็น `08X-XXX-XXXX` (`REQ-SEC-002`, `CC-06`)
  4. `Q-04` (การให้คะแนนผู้ขาย): ซาเล้งไม่มีการให้คะแนนดาว 1–5 ดาวแก่ผู้ขาย แต่เน้นการปักหมุดลูกค้าประจำสำหรับผู้ขายที่ดี และรายงานข้อพิพาทเมื่อพบปัญหา
  5. `Q-05` (สถิติสรุปสะสม): แสดงการ์ดสรุป 3 มิติ (รายจ่ายรวม, น้ำหนักรวม, จำนวนงานสำเร็จ) พร้อมตัวกรองรายวัน/รายเดือน และรายการคำขอ `S7` ที่เปิดดูใบเสร็จดิจิทัลได้
  6. `Q-06` (Non-goals): ไม่ทำแชทคุยต่อหลังจบงาน (`S7`), ไม่ทำระบบจ่ายเงินชดเชยค่าเดินทางอัตโนมัติ, ไม่เปิดเผย PII ที่ไม่ Mask เกิน 24 ชม., และไม่ทำระบบรีวิวดาวผู้ขาย
- **สถานะ:** เคลียร์จุดกำกวมเสร็จสมบูรณ์ สเปกพร้อมเข้าสู่ขั้นตอน `/plan specs/buyer/07-post-job/spec.md`

---

## บันทึก #83 — `/plan specs/buyer/07-post-job/spec.md` (วางแผนระบบหลังจบงานซาเล้ง Buyer 07)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/buyer/07-post-job/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/07-post-job/spec.md` (v2.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-10`, `UC-13`), `specs/002-route/models.md` (`MD-STM-04`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/07-post-job/plan.md` (สร้างเอกสารแผนสถาปัตยกรรม 8 ส่วนสมบูรณ์)
- **ประเด็นสำคัญใน plan.md:**
  1. **เทคโนโลยี:** Python 3.11 + FastAPI (Pydantic v2), Supabase / PostgreSQL (Optimistic Locking ด้วย `version`), React 18 + TailwindCSS (Mobile-First SPA, ปุ่มกดทัชทาร์เก็ต `>= 48px`), Pytest และ Vitest
  2. **โครงสร้างไฟล์และตารางข้อมูล:**
     - Data Models: `backend/app/models/post_job_models.py`
     - Backend Service & API: `backend/app/services/post_job_service.py` และ `backend/app/api/v1/post_job.py`
     - Database: `collector_favorite_sellers`, `dispute_reports`, `waste_pickup_orders`, `audit_logs`
     - Frontend API Client & Components: `postJobApi.js`, `PurchaseHistoryCard.jsx`, `RegularCustomerList.jsx`, `SellerMismatchReportModal.jsx`, `PostJobCollectorView.jsx` (`data-req="UC-10"`)
  3. **การออกแบบ API 4 เส้นทาง:**
     - `GET /api/v1/collectors/post-job/history` (ประวัติรับซื้อ + สถิติสะสม 3 มิติ)
     - `GET /api/v1/collectors/post-job/regular-customers` (รายชื่อลูกค้าประจำ)
     - `POST /api/v1/collectors/post-job/regular-customers` (Toggle ปักหมุดลูกค้าประจำ)
     - `POST /api/v1/collectors/post-job/report-mismatch` (รายงานข้อพิพาทหน้างาน S3/S4 -> S8)
  4. **การปฏิบัติตาม Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเฉพาะ `CC-01` (ปุ่ม >= 48px), `CC-05` (Offline Cache ใน `localStorage`), `CC-06` (PDPA Masking เบอร์โทรเป็น `08X-XXX-XXXX` และซ่อนบ้านเลขที่เกิน 24 ชม.), `REQ-SEC-001` (Audit Logging), และ `D-00-01` (KYC Verified Gate)
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/buyer/07-post-job/plan.md`

---

## บันทึก #84 — `/tasks specs/buyer/07-post-job/plan.md` (แตกงานย่อยระบบหลังจบงานซาเล้ง Buyer 07)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/buyer/07-post-job/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/07-post-job/spec.md` (v2.0), `specs/buyer/07-post-job/plan.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-10`, `UC-13`), `specs/002-route/models.md` (`MD-STM-04`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/buyer/07-post-job/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-B07-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบหลังจบงานซาเล้ง (`post_job_models.py`, ขยาย `supabase.py` เพิ่มตาราง `collector_favorite_sellers`, `dispute_reports`, helper methods, และ `test_T01_post_job_models.py`)
     - `T-02`: สร้าง Service และ API ประวัติการรับซื้อและสถิติสะสม 3 มิติ (`post_job_service.py`, `post_job.py`, `pricing.py`, `test_AC_B07_01_history_log.py`)
     - `T-03`: สร้าง Service และ API จัดการลูกค้าประจำ (`collector_favorite_sellers`) และบันทึกย่อส่วนตัว (`post_job_service.py`, `post_job.py`, `test_AC_B07_02_regular_customer.py`)
     - `T-04`: สร้าง Service และ API รายงานข้อพิพาทหน้างานกรณี No-show หรือของไม่ตรงสเปก เปลี่ยนสถานะเป็น `S8: Disputed` และปลดล็อกซาเล้ง (`post_job_service.py`, `post_job.py`, `test_AC_B07_03_seller_mismatch.py`)
     - `T-05`: สร้าง Frontend API Client และระบบแคชออฟไลน์ (`postJobApi.js`, `postJobApi.test.mjs`, `CC-05`, `REQ-OP-001`)
     - `T-06`: พัฒนาคอมโพเนนต์ React ระบบประวัติและลูกค้าประจำ (`PurchaseHistoryCard`, `RegularCustomerList`, `SellerMismatchReportModal`, `PostJobCollectorView` ทัชทาร์เก็ตทุกปุ่ม >= 48px ตาม `REQ-UX-001`, `CC-01`)
     - `T-07`: สร้างชุดทดสอบหน้าจอ Vitest Component Tests สำหรับระบบหลังจบงาน (`AC-B07-01.test.jsx`, `AC-B07-02.test.jsx`, `AC-B07-03.test.jsx`)
     - `T-08`: สร้างชุดทดสอบ Integration E2E Test Suite เต็มวงรอบ (`test_e2e_buyer_post_job.py`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-B07-01` ถึง `AC-B07-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`


---

## บันทึก #85 — `/implement T-01..08` (พัฒนาระบบหลังจบงานซาเล้ง Buyer 07: Post-Job Management)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/buyer/07-post-job/spec.md` (v2.0), `specs/buyer/07-post-job/plan.md` (v1.0), `specs/buyer/07-post-job/tasks.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-10`, `UC-13`), `specs/002-route/models.md` (`MD-STM-04`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/post_job_models.py` (สร้าง Data Models และ Pydantic v2 schemas: PurchaseHistorySummary, PurchaseHistoryItem, PurchaseHistoryResponse, RegularCustomerItem, ToggleRegularCustomerRequest, ToggleRegularCustomerResponse, ReportSellerMismatchRequest, ReportSellerMismatchResponse)
  - `backend/app/core/supabase.py` (ขยาย mock Supabase store เพิ่มตาราง `collector_favorite_sellers`, `dispute_reports`, helper methods: `get_collector_favorite_sellers`, `toggle_collector_favorite_seller`, `create_dispute_report`)
  - `backend/app/services/post_job_service.py` (สร้าง Service ตรรกะธุรกิจหลังจบงาน: ดึงประวัติ S7 พร้อมสรุปสถิติ 3 มิติ, กรอง All/Today/Month, PII masking 08X-XXX-XXXX, จัดการลูกค้าประจำพร้อมพิกัดและบันทึกย่อ <= 200 ตัวอักษร, รายงานข้อพิพาทหน้างาน S3/S4 -> S8: Disputed พร้อมปลดล็อก active_collector_lock และ Audit Logging REQ-SEC-001)
  - `backend/app/api/v1/post_job.py` (สร้าง FastAPI Router 4 endpoints: GET /history, GET /regular-customers, POST /regular-customers, POST /report-mismatch พร้อม KYC gate D-00-01)
  - `backend/app/api/v1/pricing.py` (เมานต์ post_job.router เข้ากับ API v1)
  - `backend/tests/test_T01_post_job_models.py` (ชุดทดสอบ Pydantic models & Store methods 4 เคส: ผ่าน 100%)
  - `backend/tests/test_AC_B07_01_history_log.py` (ชุดทดสอบประวัติรับซื้อ สถิติสะสม 3 มิติ และ PII masking 3 เคส: ผ่าน 100%)
  - `backend/tests/test_AC_B07_02_regular_customer.py` (ชุดทดสอบลูกค้าประจำ Toggle & Notes 2 เคส: ผ่าน 100%)
  - `backend/tests/test_AC_B07_03_seller_mismatch.py` (ชุดทดสอบรายงานข้อพิพาท S3/S4 -> S8 และปลดล็อกซาเล้ง 4 เคส: ผ่าน 100%)
  - `backend/tests/test_e2e_buyer_post_job.py` (Integration E2E test ครอบคลุมวงจร S7 history, favorite seller, dispute S3/S4->S8, audit logs 1 เคส: ผ่าน 100%)
  - `frontend/src/services/postJobApi.js` (สร้าง API client สำหรับฝั่งหน้าบ้าน พร้อม LocalStorage caching CC-05, REQ-OP-001)
  - `frontend/src/components/PurchaseHistoryCard.jsx` (คอมโพเนนต์แสดงผลประวัติรับซื้อ S7, สถิติสะสม 3 มิติ, ปุ่มดูใบเสร็จ, ปุ่มปักหมุดลูกค้าประจำ ทัชทาร์เก็ต >= 48px REQ-UX-001)
  - `frontend/src/components/RegularCustomerList.jsx` (คอมโพเนนต์รายชื่อลูกค้าประจำ พร้อมบันทึกย่อส่วนตัว ปุ่มนำทางพิกัด และปุ่มลบ)
  - `frontend/src/components/SellerMismatchReportModal.jsx` (คอมโพเนนต์โมดอลรายงานข้อพิพาทหน้างาน บังคับแนบรูปหลักฐาน REQ-FN-006 ทัชทาร์เก็ต >= 48px)
  - `frontend/src/components/PostJobCollectorView.jsx` (หน้าจอหลักรวบรวมประวัติและลูกค้าประจำ กำกับ data-req="UC-10")
  - `frontend/tests/postJobApi.test.mjs` (ชุดทดสอบ API client & Offline cache 6 เคส: ผ่าน 100%)
  - `frontend/tests/AC-B07-01.test.jsx` (Vitest UI Component Test: ประวัติรับซื้อ, สถิติ 3 มิติ, ตัวกรอง, PII masking 2 เคส: ผ่าน 100%)
  - `frontend/tests/AC-B07-02.test.jsx` (Vitest UI Component Test: ปักหมุดลูกค้าประจำ, บันทึกย่อ Notes 3 เคส: ผ่าน 100%)
  - `frontend/tests/AC-B07-03.test.jsx` (Vitest UI Component Test: โมดอลรายงานข้อพิพาทหน้างาน แนบรูปหลักฐาน 2 เคส: ผ่าน 100%)
  - `specs/buyer/07-post-job/tasks.md` (อัปเดตสถานะ T-01 ถึง T-08 เป็น [DONE] และอัปเดตสถานะรวมเป็น completed)
- **ผลการตรวจ 5 ด่านหลังจบงาน (Checkpoints):**
  1. **Automated Tests:**
     - Backend (Pytest): ผ่าน 100% รวม 265 passed, 0 failed ใน 0.94s
     - Frontend (Vitest): ผ่าน 100% รวม 89 test files, 227 passed, 0 failed ใน 7.19s
  2. **Constraints กลาง:** ปฏิบัติตามครบถ้วน (`CC-01` ทัชทาร์เก็ตปุ่มกด >= 48px, `CC-04` Optimistic concurrency, `CC-05` Offline Cache ใน LocalStorage, `CC-06` / `REQ-SEC-002` PII masking เบอร์โทร `08X-XXX-XXXX`, `D-00-01` KYC gate)
  3. **Traceability:** ฟังก์ชันและคอมโพเนนต์ทุกชิ้นอ้างอิง `UC-10`, `UC-13`, `REQ-FN-005`, `REQ-FN-006`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-OP-001`, `REQ-UX-001`, `AC-B07-01..05` ครบถ้วน
  4. **Mockups:** โครงสร้างป้ายภาษาไทย, ปุ่มกดขนาดใหญ่ >= 48px, และแอตทริบิวต์ `data-req="UC-10"` ครบถ้วน
  5. **Non-goals:** ไม่มีแชทต่อหลัง S7, ไม่มีการจ่ายชดเชยค่าเดินทางอัตโนมัติ (เป็นดุลยพินิจ Admin ใน UC-13), ไม่เปิดเผย PII ที่ไม่ Mask เกิน 24 ชม., และไม่มีระบบรีวิวดาวผู้ขาย (ใช้ปักหมุดลูกค้าประจำแทน) ตาม `D-B07-04` และ `D-B07-06`
- **สถานะ:** พัฒนาและตรวจรับระบบหลังจบงานซาเล้ง Buyer 07 สำเร็จสมบูรณ์ พร้อมส่งมอบงาน


---

## บันทึก #86 — `/clarify specs/admin/01-user-verification-and-penalty/spec.md` (ตรวจความกำกวมระบบตรวจสอบอนุมัติ KYC และจัดการบทลงโทษผู้ใช้งาน)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/admin/01-user-verification-and-penalty/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/01-user-verification-and-penalty/spec.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-11`, `UC-01`, `UC-04`), `docs/srs/decisions.md` (`D-00-01`), `specs/002-route/models.md`
- **จุดกำกวมที่ AI พบและคำตอบของทีม (ส่วน A & B — 6 คำถาม):**
  1. **`Q-01` (`AC-A01-01`):** เอกสารภาพถ่ายที่ใช้ตรวจสอบ KYC ซาเล้งต้องมีรายการใดบ้าง -> บันทึก `D-A01-01`: บังคับ 3 รูป ได้แก่ ภาพหน้าบัตรประชาชน, ภาพเซลฟี่ถือบัตร, และภาพถ่ายยานพาหนะพร้อมป้ายทะเบียน
  2. **`Q-02` (`AC-A01-02`, `D-00-01`):** การอนุมัติ KYC เชื่อมโยงกับสิทธิ์รับงานใน `UC-04` อย่างไร -> บันทึก `D-A01-02`: การอนุมัติจะปรับ `saleng_profiles.verified = true` และ `kyc_status = 'VERIFIED'` ปลดล็อกให้ค้นหาและกดรับงานใน `UC-04` ได้ทันที หากปฏิเสธต้องระบุ `rejection_reason`
  3. **`Q-03` (`AC-A01-03`, `D-A01-03`):** ระดับของบทลงโทษบัญชีผู้ใช้ -> บันทึก `D-A01-03`: แบ่งเป็น 3 ระดับ `ACTIVE` (ปกติ), `SUSPENDED_TEMPORARY` (ระงับชั่วคราว), และ `BANNED` (แบนถาวร)
  4. **`Q-04` (`AC-A01-03`):** ขอบเขตการลงโทษครอบคลุมบทบาทใดบ้าง -> บันทึก `D-A01-04`: ครอบคลุมทั้งซาเล้ง (`saleng_profiles`) และผู้ขาย (`sellers`)
  5. **`Q-05` (`CC-03`, `REQ-SEC-001`):** การควบคุมสิทธิ์ของระบบแอดมิน -> บันทึก `D-A01-05`: บังคับ Header `X-Admin-Role: ADMIN` หากไม่มีสิทธิ์ให้ส่งกลับ `HTTP 403 Forbidden`
  6. **`Q-06` (`REQ-SEC-002`, `CC-06`):** การปกปิดข้อมูลส่วนบุคคล (PII) ในหน้ารวมรายการ -> บันทึก `D-A01-06`: ปกปิดหมายเลขบัตรประชาชนเป็น `1-1002-XXXXX-XX-X` และเบอร์โทรศัพท์เป็น `08X-XXX-XXXX`
- **ไฟล์ที่สร้าง/แก้ไข:** `specs/admin/01-user-verification-and-penalty/spec.md` (ปรับปรุงเป็น Version 2.0 สถานะ `reviewed-post-clarify`)
- **สถานะ:** Clarification เสร็จสมบูรณ์ พร้อมสำหรับการวางแผนทางเทคนิค `/plan`

---

## บันทึก #87 — `/plan specs/admin/01-user-verification-and-penalty/spec.md` (สร้างแผนทางเทคนิคระบบตรวจสอบและอนุมัติผู้ใช้งาน Admin 01)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/admin/01-user-verification-and-penalty/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/01-user-verification-and-penalty/spec.md` (v2.0), `specs/000-shared/constraints.md`, `specs/000-shared/quality-requirements.md`, `docs/srs/use-cases.md` (`UC-11`, `UC-01`, `UC-04`), `docs/srs/decisions.md` (`D-00-01`), `specs/002-route/models.md`
- **ไฟล์ที่สร้าง:** `specs/admin/01-user-verification-and-penalty/plan.md` (ครบ 8 ส่วนตามโครงสร้างมาตรฐาน)
- **ประเด็นสำคัญในแผน:**
  1. **การตัดสินใจทางเทคนิค 6 ข้อ (`P-01` ถึง `P-06`):**
     - `P-01`: โครงสร้าง Data Schema สำหรับ `collector_kyc_submissions` และขยาย `saleng_profiles` / `sellers` ให้รองรับ `account_status` และ `penalty_reason`
     - `P-02`: การออกแบบ Service Layer `UserVerificationPenaltyService` สำหรับคิวตรวจคำขอ KYC และการลงโทษบัญชีผู้ใช้
     - `P-03`: การบังคับสิทธิ์ Admin RBAC ผ่าน FastAPI Dependency ตรวจสอบ `X-Admin-Role: ADMIN` และส่งกลับ `HTTP 403 Forbidden`
     - `P-04`: การปกปิดข้อมูลส่วนบุคคล PII Masking สำหรับเลขบัตรประชาชนและเบอร์โทรศัพท์ตาม `REQ-SEC-002` และ `CC-06`
     - `P-05`: การบันทึก Audit Log แบบ Append-only สำหรับทุกการกระทำของแอดมินตาม `REQ-SEC-001`
     - `P-06`: แดชบอร์ดแอดมิน React Responsive SPA ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ตาม `REQ-UX-001` และ `CC-01`
  2. **โครงสร้างไฟล์และโมดูล:**
     - Data Models: `backend/app/models/user_verification_penalty_models.py`
     - Backend Service & API: `backend/app/services/user_verification_penalty_service.py` และ `backend/app/api/v1/user_verification_penalty.py`
     - Mock Store & Database: `collector_kyc_submissions`, `saleng_profiles`, `sellers`, `audit_logs`
     - Frontend API Client & Components: `adminUserApi.js`, `KycReviewQueueCard.jsx`, `UserPenaltyControlCard.jsx`, `AdminUserVerificationView.jsx` (`data-req="UC-11"`)
  3. **การออกแบบ API แอดมิน 5 เส้นทาง:**
     - `GET /api/v1/admin/kyc/submissions` (คิวคำขอ KYC พร้อม PII Masking)
     - `POST /api/v1/admin/kyc/review` (อนุมัติ/ปฏิเสธคำขอ KYC พร้อมระบุเหตุผล)
     - `GET /api/v1/admin/users` (รายชื่อผู้ใช้ทั้งซาเล้งและผู้ขาย)
     - `POST /api/v1/admin/users/penalty` (ระงับสิทธิ์ชั่วคราวหรือถาวร)
     - `POST /api/v1/admin/users/reactivate` (ปลดระงับสิทธิ์คืนสถานะ ACTIVE)
  4. **การปฏิบัติตาม Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเฉพาะ `CC-01` (ปุ่ม $\ge 48\text{px}$), `CC-03` (สิทธิ์ `X-Admin-Role: ADMIN`), `CC-05` (Online-only สำหรับแอดมิน), `CC-06` / `REQ-SEC-002` (PDPA Masking เลขบัตร `1-1002-XXXXX-XX-X`), `REQ-SEC-001` (Audit Logging), และ `D-00-01` (KYC Gatekeeper)
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/admin/01-user-verification-and-penalty/plan.md`

---

## บันทึก #88 — `/tasks specs/admin/01-user-verification-and-penalty/plan.md` (แตกงานย่อยระบบตรวจสอบและอนุมัติผู้ใช้งาน Admin 01)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/admin/01-user-verification-and-penalty/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/01-user-verification-and-penalty/spec.md` (v2.0), `specs/admin/01-user-verification-and-penalty/plan.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-11`, `UC-01`, `UC-04`), `docs/srs/decisions.md` (`D-00-01`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/admin/01-user-verification-and-penalty/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-A01-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบตรวจสอบ KYC และบทลงโทษ (`user_verification_penalty_models.py`, ขยาย `supabase.py` เพิ่ม methods และกำหนดสถานะเริ่มต้น `account_status = 'ACTIVE'`, `test_T01_admin_user_models.py`)
     - `T-02`: สร้าง Service และ API คิวตรวจคำขอ KYC ซาเล้ง และ PII Masking (`user_verification_penalty_service.py`, `user_verification_penalty.py`, `pricing.py`, `test_AC_A01_01_kyc_queue.py`)
     - `T-03`: สร้าง Service และ API อนุมัติและปฏิเสธคำขอ KYC ซาเล้ง เปิด verified=true ปลดล็อก `UC-04` หรือปฏิเสธพร้อมระบุเหตุผล (`user_verification_penalty_service.py`, `user_verification_penalty.py`, `test_AC_A01_02_kyc_review.py`)
     - `T-04`: สร้าง Service และ API จัดการบทลงโทษผู้ใช้และปลดระงับทั้งซาเล้งและผู้ขาย (`user_verification_penalty_service.py`, `user_verification_penalty.py`, `test_AC_A01_03_user_penalty.py`, `test_AC_A01_04_user_reactivate.py`)
     - `T-05`: สร้างระบบตรวจสอบความปลอดภัย Admin RBAC (`X-Admin-Role: ADMIN` -> 403 Forbidden) และความครบถ้วนของ Audit Logging (`test_AC_A01_05_admin_rbac_audit.py`)
     - `T-06`: สร้าง Frontend API Client สำหรับแอดมิน (`adminUserApi.js`, `adminUserApi.test.mjs`, `CC-03`, `CC-05`)
     - `T-07`: พัฒนาคอมโพเนนต์ React แดชบอร์ดแอดมิน (`KycReviewQueueCard`, `UserPenaltyControlCard`, `AdminUserVerificationView` ทัชทาร์เก็ตทุกปุ่ม $\ge 48\text{px}$ ตาม `REQ-UX-001`, `CC-01`)
     - `T-08`: สร้างชุดทดสอบ Vitest Component Tests และ Integration E2E Test Suite เต็มวงรอบ พร้อมตรวจรับ 5 ด่าน (`test_e2e_admin_user_verification_penalty.py`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-A01-01` ถึง `AC-A01-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`

---

## บันทึก #89 — `/implement T-01..08` (พัฒนาระบบตรวจสอบอนุมัติผู้ใช้งานและจัดการบทลงโทษ Admin 01 จนเสร็จสมบูรณ์)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/01-user-verification-and-penalty/spec.md` (v2.0), `specs/admin/01-user-verification-and-penalty/plan.md` (v1.0), `specs/admin/01-user-verification-and-penalty/tasks.md` (v1.1), `specs/000-shared/constraints.md`
- **งานย่อยที่พัฒนาครบทั้ง 8 งาน (`T-01` ถึง `T-08`):**
  1. **`T-01` (Data Models & Schemas):**
     - สร้าง `backend/app/models/user_verification_penalty_models.py` (`KYCSubmissionItem`, `KYCReviewRequest`, `KYCReviewResponse`, `UserAccountItem`, `UserPenaltyRequest`, `UserPenaltyResponse`, `UserReactivateRequest`, `UserReactivateResponse`, `mask_thai_id_card`)
     - ขยาย `backend/app/core/supabase.py` เพิ่มคลังข้อมูลและเมธอด: `collector_kyc_submissions`, `sellers`, `get_collector_kyc_submissions`, `get_collector_kyc_submission`, `review_collector_kyc`, `get_admin_users`, `penalize_user_account`, `reactivate_user_account`
     - สร้างชุดทดสอบ `backend/tests/test_T01_admin_user_models.py` (4 passed)
  2. **`T-02` (KYC Queue & PII Masking):**
     - พัฒนา `UserVerificationPenaltyService.list_kyc_submissions` และเปิด Endpoint `GET /api/v1/admin/kyc/submissions`
     - เมานต์เราเตอร์แอดมินใน `backend/app/api/v1/pricing.py`
     - ปกปิดหมายเลขบัตรประชาชน 13 หลักเป็น `1-1002-XXXXX-XX-X` ตาม `REQ-SEC-002` และ `CC-06`
     - สร้างชุดทดสอบ `backend/tests/test_AC_A01_01_kyc_queue.py` (2 passed)
  3. **`T-03` (KYC Review & Gatekeeper Verification):**
     - พัฒนา `review_kyc_submission` และเปิด Endpoint `POST /api/v1/admin/kyc/review`
     - กรณี `APPROVE`: ปรับสถานะคำขอเป็น `VERIFIED` และเปิดสิทธิ์ `saleng_profiles.verified = True`, `kyc_status = 'VERIFIED'` ปลดล็อกให้ค้นหาและรับงานใน `UC-04` ตาม `D-00-01`
     - กรณี `REJECT`: บังคับระบุเหตุผล `rejection_reason` และคงสถานะ `verified = False`
     - บันทึก Audit Log `ADMIN_APPROVED_KYC` / `ADMIN_REJECTED_KYC` พร้อม `actor_role = 'ADMIN'`
     - สร้างชุดทดสอบ `backend/tests/test_AC_A01_02_kyc_review.py` (3 passed)
  4. **`T-04` (User Penalty & Reactivation):**
     - พัฒนา `list_users`, `penalize_user`, `reactivate_user` และเปิด Endpoint:
       - `GET /api/v1/admin/users` (ค้นหาและกรองตาม role / status)
       - `POST /api/v1/admin/users/penalty` (ระงับชั่วคราว `SUSPENDED_TEMPORARY` หรือแบนถาวร `BANNED`)
       - `POST /api/v1/admin/users/reactivate` (ปลดระงับคืนสถานะ `ACTIVE`)
     - รองรับทั้งซาเล้ง (`COLLECTOR`) และผู้ขาย (`SELLER`) ตาม `D-A01-03`, `D-A01-04`
     - บันทึก Audit Log `ADMIN_PENALIZED_USER` / `ADMIN_UNSUSPENDED_USER`
     - สร้างชุดทดสอบ `backend/tests/test_AC_A01_03_user_penalty.py` และ `test_AC_A01_04_user_reactivate.py` (6 passed)
  5. **`T-05` (Admin RBAC & Audit Integrity):**
     - พัฒนา Dependency `verify_admin_role` บังคับ Header `X-Admin-Role: ADMIN` ปฏิเสธการเข้าถึงด้วย `HTTP 403 Forbidden` หากไม่มีสิทธิ์ตาม `CC-03`
     - ตรวจสอบความถูกต้องของ Audit Log ครบทุกเหตุการณ์ความปลอดภัยตาม `REQ-SEC-001`
     - สร้างชุดทดสอบ `backend/tests/test_AC_A01_05_admin_rbac_audit.py` (2 passed)
  6. **`T-06` (Frontend API Client):**
     - สร้าง `frontend/src/services/adminUserApi.js` รองรับ `getKycSubmissions`, `reviewKyc`, `getUsers`, `penalizeUser`, `reactivateUser` พร้อมแนบ Header `X-Admin-Role: ADMIN` และรองรับทั้ง positional & object argument options
     - สร้างชุดทดสอบ `frontend/tests/adminUserApi.test.mjs` (6 passed)
  7. **`T-07` (React Admin Dashboard SPA):**
     - สร้าง `frontend/src/components/admin/KycReviewQueueCard.jsx` (แสดงภาพบัตรประชาชน/เซลฟี่คู่บัตร/ยานพาหนะ, เลขบัตร Masked, ปุ่มอนุมัติและปฏิเสธพร้อม Modal ระบุเหตุผล)
     - สร้าง `frontend/src/components/admin/UserPenaltyControlCard.jsx` (แสดงบทบาท ป้ายสถานะ Active/Suspended/Banned, ปุ่มสั่งระงับสิทธิ์ชั่วคราว/แบนถาวรพร้อม Modal, ปุ่มปลดระงับ)
     - สร้าง `frontend/src/components/admin/AdminUserVerificationView.jsx` (แดชบอร์ดแท็บคู่ แท็บ KYC และแท็บจัดการบทลงโทษผู้ใช้ กำกับ `data-req="UC-11"`)
     - ทุกปุ่มกดมีทัชทาร์เก็ต $\ge 48\text{px}$ ตาม `REQ-UX-001` และ `CC-01`
  8. **`T-08` (Vitest Component Tests, Integration E2E & ตรวจรับ 5 ด่าน):**
     - สร้าง Vitest UI Tests:
       - `frontend/tests/AC-A01-01.test.jsx` (3 passed)
       - `frontend/tests/AC-A01-02.test.jsx` (2 passed)
       - `frontend/tests/AC-A01-03.test.jsx` (3 passed)
       - `frontend/tests/AC-A01-04.test.jsx` (3 passed)
     - สร้าง Integration E2E Test:
       - `backend/tests/test_e2e_admin_user_verification_penalty.py` (1 passed)
- **ผลการตรวจรับ 5 ด่านหลังจบงาน (Checkpoints):**
  1. *ด่าน 1 (ครบทุก Task):* ทำครบทั้ง 8 งาน `T-01` ถึง `T-08` และอัปเดต `tasks.md` เป็น `completed`
  2. *ด่าน 2 (Automated Tests ครบทุก AC):* ครอบคลุมทั้ง `AC-A01-01` ถึง `AC-A01-05` ครบถ้วนทั้งฝั่งหน้าบ้าน หลังบ้าน และ E2E
  3. *ด่าน 3 (Constraints ครบถ้วน):* ผ่าน `CC-01` (ปุ่ม $\ge 48\text{px}$), `CC-03` (RBAC `X-Admin-Role: ADMIN`), `CC-05` (Online-only), `CC-06` (PDPA Masking), `REQ-SEC-001` (Audit Logs), `D-00-01` (Gatekeeper KYC)
  4. *ด่าน 4 (Zero Regression):*
     - Backend Test Suite: **283 passed** (0 failed)
     - Frontend Vitest Suite: **244 passed** (94 test files, 0 failed)
     - รวมทั้งสิ้น **527 automated tests ผ่าน 100% ปราศจากข้อผิดพลาดและ Regression**
  5. *ด่าน 5 (บันทึก prompt-log):* บันทึกประวัติรอบ #89 เรียบร้อย
- **สถานะ:** ฟีเจอร์ Admin 01 (`specs/admin/01-user-verification-and-penalty/`) เสร็จสมบูรณ์พร้อมใช้งาน


---

## บันทึก #90 — `/clarify specs/admin/02-benchmark-price-and-grading/spec.md` (ตรวจความกำกวมระบบจัดการราคากลางและหมวดหมู่วัสดุ Admin 02)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/admin/02-benchmark-price-and-grading/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/02-benchmark-price-and-grading/spec.md` (v1.0 draft), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-03`, `UC-05`), `docs/srs/decisions.md` (`D-00-02`), `specs/seller/04-pricing-and-decision/spec.md` (`AC-S04-01`, `D-04`)
- **จุดกำกวมที่ AI พบและคำตอบของทีม (ส่วน A & B — 6 คำถาม):**
  1. **`Q-01` (`REQ-DAT-001`, `AC-A02-01`):** เวลาตัดรอบเผยแพร่ราคากลางประจำวันขัดแย้งกันระหว่าง `08:30 น.` ในสเปกเดิมกับ `06:00 น.` ใน Seller 04 -> บันทึก `D-A02-01`: กำหนดเวลาตัดรอบเผยแพร่ราคากลางประจำวันอย่างเป็นทางการ ณ เวลา **`06:00 น.`** ของทุกวัน หากไม่ได้อัปเดตระบบจะดึงราคาฐานของวันก่อนหน้ามาใช้โดยอัตโนมัติพร้อมแสดงวันเวลาอัปเดตล่าสุด
  2. **`Q-02` (`BR-01`, `REQ-DAT-001`):** กฎการตรวจสอบความถูกต้องของช่วงราคากลาง -> บันทึก `D-A02-02`: บังคับ `min_price > 0`, `max_price >= min_price`, ทศนิยมไม่เกิน 2 ตำแหน่ง และมีระบบเตือนยืนยันหากราคาขยับเกิน `±50%` จากวันก่อนหน้า เพื่อป้องกัน Human Error
  3. **`Q-03` (`REQ-FN-003`, `AC-A02-02`):** โครงสร้างเกณฑ์คุณภาพและการหักน้ำหนักสิ่งปนเปื้อน -> บันทึก `D-A02-03`: กำหนด 3 ระดับมาตรฐาน ได้แก่ `GRADE_A` (สะอาด/แห้ง หักสิ่งปนเปื้อน `0%`), `GRADE_B` (ปนเปื้อน/ชื้นเล็กน้อย หัก `5%`), `GRADE_C` (ปนเปื้อนมาก/เปียกน้ำ หัก `10%`)
  4. **`Q-04` (`REQ-FN-003`, `AC-A02-02`):** หมวดหมู่และช่วงราคาประเมินขยะชิ้นใหญ่เหมาจ่าย -> บันทึก `D-A02-04`: กำหนดหน่วยนับเป็น **"ชิ้น/เครื่อง" (`PIECE`)** ครอบคลุม: ตู้เย็น (`200–300 บาท`), เครื่องซักผ้า (`150–250 บาท`), เครื่องปรับอากาศ/แอร์ (`300–500 บาท`), โทรทัศน์/จอภาพ (`50–150 บาท`), เฟอร์นิเจอร์/เตียง (`0–100 บาท`)
  5. **`Q-05` (`REQ-BR-002`, `D-00-02`):** ผลกระทบต่อออเดอร์ในระบบเมื่อมีการปรับราคากลาง -> บันทึก `D-A02-05`: ออเดอร์สถานะ `S1 (Draft)` และ `S2 (Pending)` คำนวณราคาใหม่ตามเรตล่าสุดทันที ส่วนออเดอร์สถานะ `S3..S7` ล็อกราคาเดิมตาม Price Snapshot ณ เวลาที่ซาเล้งกดรับงานอย่างเคร่งครัด
  6. **`Q-06` (`REQ-SEC-001`, `CC-03`, `CC-05`):** สิทธิ์การเข้าถึงและความปลอดภัย -> บันทึก `D-A02-06`: บังคับ Header `X-Admin-Role: ADMIN` (`HTTP 403 Forbidden` หากไม่มีสิทธิ์), ทำงานแบบ Online-only (`CC-05`), บันทึก Audit Log แบบ Append-only (`ADMIN_UPDATED_BENCHMARK_PRICE`, `ADMIN_UPDATED_GRADING_RULES`) พร้อมค่าเก่าและใหม่
- **ไฟล์ที่สร้าง/แก้ไข:** `specs/admin/02-benchmark-price-and-grading/spec.md` (ปรับปรุงเป็น Version 2.0 สถานะ `reviewed-post-clarify`)
- **สิ่งที่ป้องกันไม่ให้ AI เดาเอง:** ป้องกัน AI สับสนเวลาตัดรอบเผยแพร่ราคา, ป้องกันการเดาสูตรหักสิ่งปนเปื้อนคลาดเคลื่อน, ป้องกันการคิดราคาขยะชิ้นใหญ่ผิดหน่วยนับ, และป้องกันการกระทบต่อออเดอร์ที่ล็อก Price Snapshot แล้ว
- **สถานะ:** Clarification เสร็จสมบูรณ์ พร้อมสำหรับการวางแผนทางเทคนิค `/plan specs/admin/02-benchmark-price-and-grading/spec.md`


---

## บันทึก #91 — `/plan specs/admin/02-benchmark-price-and-grading/spec.md` (สร้างแผนทางเทคนิคระบบจัดการราคากลางและหมวดหมู่วัสดุ Admin 02)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/admin/02-benchmark-price-and-grading/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/02-benchmark-price-and-grading/spec.md` (v2.0), `specs/000-shared/constraints.md`, `specs/000-shared/quality-requirements.md`, `docs/srs/use-cases.md` (`UC-03`, `UC-05`), `docs/srs/decisions.md` (`D-00-02`), `specs/seller/04-pricing-and-decision/spec.md`
- **ไฟล์ที่สร้าง:** `specs/admin/02-benchmark-price-and-grading/plan.md` (ครบ 8 ส่วนตามโครงสร้างมาตรฐาน)
- **ประเด็นสำคัญในแผน:**
  1. **การตัดสินใจทางเทคโนโลยี:** ระบุชัดเจนว่า **`"ทีมเลือกเอง ไม่ได้มาจาก spec"`** ตามกติกาข้อ 6 (FastAPI + Pydantic v2 หลังบ้าน, React 18 + TailwindCSS หน้าบ้าน, และ In-Memory Adapter จำลอง Supabase)
  2. **โครงสร้างไฟล์และโมดูล:**
     - Data Models: `backend/app/models/benchmark_price_grading_models.py`
     - Backend Service & API: `backend/app/services/benchmark_price_grading_service.py` และ `backend/app/api/v1/benchmark_price_grading.py`
     - Mock Store & Database: `benchmark_prices`, `quality_grading_rules`, `price_history_logs`, `audit_logs`
     - Frontend API Client & Components: `adminBenchmarkApi.js`, `BenchmarkPriceTable.jsx`, `QualityGradingRuleCard.jsx`, `BulkyItemPriceTable.jsx`, `AdminBenchmarkGradingView.jsx` (`data-req="UC-03"`)
  3. **การออกแบบ API แอดมิน 6 เส้นทาง:**
     - `GET /api/v1/admin/benchmark-prices` (ดึงรายการราคากลางทั้งหมด)
     - `PUT /api/v1/admin/benchmark-prices/{category_code}` (แก้ไขช่วงราคา Min-Max พร้อมเตือน 50%)
     - `POST /api/v1/admin/benchmark-prices/batch-update` (อัปเดตราคาแบบกลุ่มประจำวัน)
     - `GET /api/v1/admin/benchmark-prices/grading/{category_code}` (ดึงเกณฑ์คุณภาพ 3 ระดับ)
     - `PUT /api/v1/admin/benchmark-prices/grading/{category_code}` (แก้ไขเกณฑ์คุณภาพและ % หักสิ่งปนเปื้อน)
     - `GET /api/v1/admin/benchmark-prices/history/{category_code}` (ดึงประวัติการปรับราคา)
  4. **การปฏิบัติตาม Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเฉพาะ `CC-01` (ปุ่ม $\ge 48\text{px}$), `CC-03` (สิทธิ์ `X-Admin-Role: ADMIN`), `CC-05` (Online-only สำหรับแอดมิน), `REQ-SEC-001` (Audit Logging `ADMIN_UPDATED_BENCHMARK_PRICE`, `ADMIN_UPDATED_GRADING_RULES`), และ `D-00-02` (ล็อกราคา Price Snapshot ณ `S3`)
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/admin/02-benchmark-price-and-grading/plan.md`


---

## บันทึก #92 — `/tasks specs/admin/02-benchmark-price-and-grading/plan.md` (แตกงานย่อยระบบจัดการราคากลางและหมวดหมู่วัสดุ Admin 02)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/admin/02-benchmark-price-and-grading/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/02-benchmark-price-and-grading/spec.md` (v2.0), `specs/admin/02-benchmark-price-and-grading/plan.md` (v1.0), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-03`, `UC-05`), `docs/srs/decisions.md` (`D-00-02`)
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/admin/02-benchmark-price-and-grading/tasks.md` (แตกงานย่อย 8 งาน `T-01` ถึง `T-08` ครบทั้ง 6 คอลัมน์, พร้อมตาราง Two-way Traceability Matrix ครบทุกข้อ `AC-A02-01..05`, และตาราง Constraints Traceability ครบทั้ง 13 ข้อ)
- **ประเด็นสำคัญใน tasks.md:**
  1. **งานย่อย 8 งาน (`T-01` ถึง `T-08`):**
     - `T-01`: สร้าง Data Models และ Schema สำหรับระบบราคากลางและเกณฑ์คุณภาพ (`benchmark_price_grading_models.py`, ขยาย `supabase.py` เพิ่ม `quality_grading_rules`, `price_history_logs`, `test_T01_benchmark_grading_models.py`)
     - `T-02`: สร้าง Service และ API เผยแพร่ราคากลางรายวันและ Price Validation (`benchmark_price_grading_service.py`, `benchmark_price_grading.py`, `pricing.py`, `test_AC_A02_01_benchmark_publishing.py`)
     - `T-03`: สร้าง Service และ API กำหนดเกณฑ์คุณภาพ 3 ระดับและการหักสิ่งปนเปื้อน 0%/5%/10% (`benchmark_price_grading_service.py`, `benchmark_price_grading.py`, `test_AC_A02_02_grading_rules.py`)
     - `T-04`: สร้าง Service และ API จัดการช่วงราคาขยะชิ้นใหญ่เหมาจ่ายหน่วย PIECE และ Batch Update (`benchmark_price_grading_service.py`, `benchmark_price_grading.py`, `test_AC_A02_03_bulky_item_prices.py`)
     - `T-05`: สร้างระบบตรวจสอบความปลอดภัย Admin RBAC (`X-Admin-Role: ADMIN` -> 403), เตือนราคาเปลี่ยนเกิน 50%, ทดสอบ Price Snapshot Lock ณ S3 และ Audit Logging (`test_AC_A02_04_price_snapshot_integrity.py`, `test_AC_A02_05_admin_price_audit.py`)
     - `T-06`: สร้าง Frontend API Client สำหรับแอดมิน (`adminBenchmarkApi.js`, `adminBenchmarkApi.test.mjs`, `CC-03`, `CC-05`)
     - `T-07`: พัฒนาคอมโพเนนต์ React แดชบอร์ดจัดการราคากลางและเกณฑ์คุณภาพ (`BenchmarkPriceTable`, `BulkyItemPriceTable`, `QualityGradingRuleCard`, `AdminBenchmarkGradingView` ทัชทาร์เก็ตทุกปุ่ม $\ge 48\text{px}$ ตาม `REQ-UX-001`, `CC-01`)
     - `T-08`: สร้างชุดทดสอบ Vitest Component Tests และ Integration E2E Test Suite เต็มวงรอบ พร้อมตรวจรับ 5 ด่าน (`test_e2e_admin_benchmark_price_grading.py`)
  2. **Two-way Traceability Matrix:** เกณฑ์การยอมรับทุกข้อ (`AC-A02-01` ถึง `AC-A02-05`) เชื่อมโยงกับงานย่อยและชื่อไฟล์ชุดทดสอบอย่างครบถ้วน
  3. **Constraints Traceability:** ตรวจสอบข้อจำกัดกลางทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` ครบถ้วน
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมสำหรับการเริ่มพัฒนางานย่อยในขั้นตอน `/implement T-01..08`


---

## บันทึก #93 — `/implement T-01..08` (พัฒนาระบบจัดการราคากลางและเกณฑ์คุณภาพ Admin 02 จนเสร็จสมบูรณ์)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/02-benchmark-price-and-grading/spec.md` (v2.0), `specs/admin/02-benchmark-price-and-grading/plan.md` (v1.0), `specs/admin/02-benchmark-price-and-grading/tasks.md` (v1.1), `specs/000-shared/constraints.md`, `docs/srs/use-cases.md` (`UC-03`, `UC-05`), `docs/srs/decisions.md` (`D-00-02`)
- **งานย่อยที่พัฒนาครบทั้ง 8 งาน (`T-01` ถึง `T-08`):**
  1. **`T-01` (Data Models & Schemas):**
     - สร้าง `backend/app/models/benchmark_price_grading_models.py` (`BenchmarkPriceAdminItem`, `UpdateBenchmarkPriceRequest`, `BatchUpdateBenchmarkPricesRequest`, `QualityGradingRuleItem`, `UpdateGradingRulesRequest`, `PriceHistoryLogItem`, `BenchmarkPriceResponse`, `BatchUpdateResponse`, `GradingRulesResponse`)
     - ขยาย `backend/app/core/supabase.py` เพิ่ม `quality_grading_rules`, `price_history_logs` และ helper methods: `get_all_benchmark_prices_admin`, `update_benchmark_price`, `get_quality_grading_rules`, `update_quality_grading_rules`, `batch_update_benchmark_prices`, `get_benchmark_price_history`
     - สร้างชุดทดสอบ `backend/tests/test_T01_benchmark_grading_models.py` (8 passed)
  2. **`T-02` (Daily Benchmark Publishing & Price Validation):**
     - พัฒนา `BenchmarkPriceGradingService.list_benchmark_prices` และ `update_benchmark_price` ใน `backend/app/services/benchmark_price_grading_service.py`
     - เปิด Endpoint `GET /api/v1/admin/benchmark-prices`, `PUT /api/v1/admin/benchmark-prices/{category_code}` และเมานต์ใน `backend/app/api/v1/pricing.py`
     - ตรวจสอบ `min_price > 0`, `max_price >= min_price`, ทศนิยม $\le 2$ ตำแหน่ง และกลไก Fallback ราคาก่อนหน้าอัตโนมัติหากไม่มีการตั้งราคาใหม่ก่อน 06:00 น. (`D-A02-01`, `D-A02-02`)
     - สร้างชุดทดสอบ `backend/tests/test_AC_A02_01_benchmark_publishing.py` (4 passed)
  3. **`T-03` (Quality Grading & Contamination Rules):**
     - พัฒนา `get_grading_rules` และ `update_grading_rules` เปิด Endpoint `GET /api/v1/admin/benchmark-prices/grading/{category_code}` และ `PUT /api/v1/admin/benchmark-prices/grading/{category_code}`
     - รองรับเกณฑ์คุณภาพ 3 ระดับมาตรฐาน: `GRADE_A` (สะอาด หัก 0%, คิดราคา MAX), `GRADE_B` (ปนเปื้อนเล็กน้อย หัก 5%, คิดราคา MID), `GRADE_C` (ปนเปื้อนมาก หัก 10%, คิดราคา MIN) ตาม `D-A02-03`
     - บันทึก Audit Log `ADMIN_UPDATED_GRADING_RULES`
     - สร้างชุดทดสอบ `backend/tests/test_AC_A02_02_grading_rules.py` (4 passed)
  4. **`T-04` (Bulky Waste Lump-sum Pricing & Batch Update):**
     - รองรับขยะชิ้นใหญ่หน่วย `PIECE` (ตู้เย็น 200–300 บ., เครื่องซักผ้า 150–250 บ., แอร์ 300–500 บ., ทีวี 50–150 บ., เตียง/เฟอร์นิเจอร์ 10–100 บ.) ตาม `D-A02-04` และ `UC-05`
     - เปิด Endpoint `POST /api/v1/admin/benchmark-prices/batch-update` สำหรับอัปเดตราคากลางหลายหมวดหมู่พร้อมกันประจำวัน
     - บันทึกประวัติลง `price_history_logs`
     - สร้างชุดทดสอบ `backend/tests/test_AC_A02_03_bulky_item_prices.py` (4 passed)
  5. **`T-05` (Admin RBAC, 50% Price Shift Warning & Price Snapshot Integrity):**
     - ตรวจสอบ Header `X-Admin-Role: ADMIN` ปฏิเสธผู้ไม่มีสิทธิ์ด้วย `HTTP 403 Forbidden` (`CC-03`, `D-A02-06`)
     - แจ้งเตือนและบังคับยืนยัน flag `confirm_shift = True` เมื่อราคาเปลี่ยนเกิน $\pm 50\%$ เพื่อป้องกันความผิดพลาดจากคน (`D-A02-02`)
     - ทดสอบผลกระทบต่อออเดอร์: ออเดอร์ `S1/S2` ได้รับราคาคำนวณใหม่ตามเรตล่าสุดทันที ส่วนออเดอร์ `S3..S7` ล็อกราคาเดิมตาม Price Snapshot อย่างเคร่งครัดตาม `D-00-02` และ `D-A02-05`
     - บันทึก Audit Log `ADMIN_UPDATED_BENCHMARK_PRICE` แบบ Append-only
     - สร้างชุดทดสอบ `backend/tests/test_AC_A02_04_price_snapshot_integrity.py` และ `test_AC_A02_05_admin_price_audit.py` (4 passed)
  6. **`T-06` (Frontend API Client):**
     - สร้าง `frontend/src/services/adminBenchmarkApi.js` (`getBenchmarkPrices`, `updateBenchmarkPrice`, `batchUpdatePrices`, `getGradingRules`, `updateGradingRules`, `getPriceHistory`)
     - แนบ Header `X-Admin-Role: ADMIN` อัตโนมัติ จัดการ Error 403 และ Error 400 (50% shift)
     - สร้างชุดทดสอบ `frontend/tests/adminBenchmarkApi.test.mjs` (8 passed)
  7. **`T-07` (React Admin Dashboard Components):**
     - พัฒนาชุดคอมโพเนนต์ Responsive SPA ใน `frontend/src/components/admin/`:
       - `BenchmarkPriceTable.jsx`: ตารางราคากลางรายวัน, ฟอร์มแก้ไข Inline, Modal ยืนยันเปลี่ยนราคาเกิน 50%
       - `BulkyItemPriceTable.jsx`: ตารางราคาเหมาจ่ายขยะชิ้นใหญ่ (หน่วย PIECE)
       - `QualityGradingRuleCard.jsx`: การ์ดเกณฑ์คุณภาพ 3 ระดับ พร้อม % หักสิ่งปนเปื้อน 0%/5%/10%
       - `AdminBenchmarkGradingView.jsx`: หน้าจอหลักแท็บคู่ กำกับ `data-req="UC-03"`, ป้ายโหมด Online-only (`CC-05`), และปุ่มกดมีทัชทาร์เก็ต $\ge 48\text{px}$ ทุกปุ่ม (`REQ-UX-001`, `CC-01`)
  8. **`T-08` (Vitest Component Tests & Integration E2E Test Suite):**
     - สร้างชุดทดสอบหน้าจอ: `frontend/tests/AC-A02-01.test.jsx` (4 passed), `AC-A02-02.test.jsx` (2 passed), `AC-A02-03.test.jsx` (2 passed)
     - สร้างชุดทดสอบ E2E เต็มวงจร: `backend/tests/test_e2e_admin_benchmark_price_grading.py` (1 passed)
- **ผลการตรวจรับ 5 ด่าน (5-Gate Checkpoints):**
  1. **ตรวจ `git status`:** ไฟล์ที่แตะตรงตามที่ระบุใน tasks.md ช่อง "สร้างหรือแก้ไฟล์ไหน" ครบถ้วน ไม่แตะไฟล์นอกขอบเขต
  2. **ตรวจผลรัน test:**
     - Backend (Pytest): ผ่าน 308/308 tests (100% pass, 0 regressions)
     - Frontend (Vitest): ผ่าน 260/260 tests (100% pass, 0 regressions)
     - รวมผ่านทั้งหมด 568 tests ทั่วทั้งคลังโค้ด
  3. **ตรวจการอ้างอิง ID:** ทุกโมดูล ฟังก์ชัน และชุดทดสอบอ้างอิง ID สเปกครบถ้วน (`UC-03`, `UC-05`, `REQ-DAT-001`, `REQ-FN-003`, `REQ-BR-002`, `REQ-SEC-001`, `REQ-UX-001`, `CC-01..06`, `D-00-02`, `D-A02-01..06`, `AC-A02-01..05`)
  4. **ตรวจ Non-goals / คำถามเปิด:** ปฏิบัติตามขอบเขตเคร่งครัด (ไม่ทำ Bidding, ไม่เชื่อมต่อ API ตลาดต่างประเทศอัตโนมัติ, ไม่ทำ AI image detection, โหมด Online-only สำหรับแอดมิน)
  5. **บันทึกลง tasks.md & prompt-log.md:** ปรับสถานะ tasks.md เป็น `completed` (ทุกงาน `[DONE]`) และบันทึกประวัติลง `prompt-log.md` เรียบร้อย
- **สถานะ:** พัฒนาฟีเจอร์ Admin 02 เสร็จสมบูรณ์ 100% พร้อมสำหรับการตรวจรับหรือขึ้นสู่ฟีเจอร์ถัดไป


---

## บันทึก #94 — `/clarify specs/admin/03-dispatch-and-dispute-center/spec.md` (เคลียร์จุดกำกวมศูนย์ควบคุมการจับคู่งานและข้อพิพาท Admin 03)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/admin/03-dispatch-and-dispute-center/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/03-dispatch-and-dispute-center/spec.md` (v1.0), `specs/000-shared/constraints.md`, `specs/002-route/models.md`, `docs/srs/glossary.md`, `docs/srs/use-cases.md` (`UC-13`), `backend/app/services/payment_service.py`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `specs/admin/03-dispatch-and-dispute-center/spec.md` (อัปเกรดเป็น Version 2.0, สถานะ `reviewed-post-clarify`, เคลียร์ 6 ประเด็นเปิด `Q-01` ถึง `Q-06` พร้อมมติ `D-A03-01` ถึง `D-A03-06`, กำหนดเกณฑ์การยอมรับ `AC-A03-01..05`, Non-goals, แผนภาพ Workflow Diagram และ API Endpoints)
- **ประเด็นคำถามเปิดและมติที่บันทึก (`D-A03-01` ถึง `D-A03-06`):**
  1. **`D-A03-01` (สถานะข้อพิพาทและการยกเลิกใน State Machine `MD-STM-04`):** ยึดตาม `glossary.md` และโค้ดปัจจุบันอย่างเป็นทางการ:
     - `S8`: อยู่ระหว่างตรวจสอบข้อพิพาท (`Disputed / Frozen`)
     - `S9`: ยกเลิกใบงาน (`Cancelled`)
     - `S7`: จบงานสมบูรณ์ (`Completed`)
     - แอดมินตัดสินให้จบงาน: `S8 -> S7`
     - แอดมินตัดสินยกเลิก/คืนเงิน: `S8 -> S9`
  2. **`D-A03-02` (เกณฑ์เวลาตัดสินงานตกค้าง `Pending Timeout`):** คำขอในสถานะ `S2 (Pending)` ที่ไม่มีซาเล้งกดรับเกิน **30 นาที** นับจากเวลาโพสต์ หรือเวลาปัจจุบันเข้าใกล้เวลานัดหมายภายใน 1 ชั่วโมง จะถูกดึงเข้าคิวงานตกค้างเพื่อให้แอดมินแทรกแซง
  3. **`D-A03-03` (ทางเลือกการกระจายงานสำรอง `Manual Dispatch Fallback`):** แอดมินมี 2 ทางเลือก:
     - `Direct Assign`: มอบหมายงานเจาะจงให้ซาเล้งที่ออนไลน์และผ่านการยืนยันตัวตน (`verified = True`)
     - `Expand Radius`: ขยายรัศมีการค้นหาจาก 5.0 กม. เป็น 10.0 กม. เพื่อบรอดคาสต์คำขอให้ซาเล้งวงนอก
  4. **`D-A03-04` (ชุดหลักฐานสำนวนข้อพิพาท `Dispute Dossier`):** แสดง 4 มิติ: ข้อมูลคำขอเดิมและ Price Snapshot, ข้อมูลหน้างานจากซาเล้ง (น้ำหนักชั่งจริง, รูปตาชั่ง `scale_photo_url`, ราคาเสนอใหม่), ข้อมูลข้อโต้แย้งจากผู้ขาย (`dispute_reason`), และข้อมูลติดต่อคู่กรณี
  5. **`D-A03-05` (ผลการตัดสินชี้ขาดข้อพิพาท):** แอดมินมี 2 ทางเลือก:
     - `RESOLVE_COMPLETE -> S7`: ระบุยอดเงินสุทธิที่ตัดสินชี้ขาด (Arbitrated Amount บาท) พร้อมหมายเหตุ และออกใบเสร็จดิจิทัล
     - `RESOLVE_CANCEL -> S9`: สั่งยกเลิกคำขอ ไม่มีการชำระเงิน พร้อมระบุเหตุผล
  6. **`D-A03-06` (การควบคุมสิทธิ์ Admin RBAC และ Audit Trail):** บังคับ Header `X-Admin-Role: ADMIN` (`403 Forbidden` หากไม่มีสิทธิ์) ตาม `CC-03`, ทำงานแบบ Online-only (`CC-05`), บันทึก Audit Log 4 แอ็กชัน (`ADMIN_MANUAL_DISPATCH`, `ADMIN_EXPAND_DISPATCH_RADIUS`, `ADMIN_RESOLVED_DISPUTE`, `ADMIN_CANCELLED_DISPUTE`) ตาม `REQ-SEC-001`, และทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ตาม `REQ-UX-001`, `CC-01`
- **สถานะ:** Clarification เสร็จสมบูรณ์ สเปก Version 2.0 พร้อมสำหรับการวางแผนในขั้นตอน `/plan specs/admin/03-dispatch-and-dispute-center/spec.md`


---

## บันทึก #95 — `/plan specs/admin/03-dispatch-and-dispute-center/spec.md` (จัดทำแผนสถาปัตยกรรมศูนย์ควบคุมการจับคู่งานและข้อพิพาท Admin 03)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/admin/03-dispatch-and-dispute-center/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/03-dispatch-and-dispute-center/spec.md` (v2.0), `specs/000-shared/constraints.md`, `specs/002-route/models.md`, `docs/srs/use-cases.md` (`UC-13`), `docs/srs/decisions.md` (`D-00-01..03`)
- **ไฟล์ที่สร้าง:**
  - `specs/admin/03-dispatch-and-dispute-center/plan.md` (แผนทางเทคนิค 8 ส่วนตามมาตรฐาน agent-pack v2: สถาปัตยกรรม, โครงสร้างไฟล์, ฐานข้อมูล, API Specification, แผนระบบภายนอก, แผนหน้าจอ React SPA, แผน Automated Tests, และตารางตรวจ Constraints กลาง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **สถาปัตยกรรมและเทคโนโลยี (ทีมเลือกเอง ไม่ได้มาจาก spec):**
     - Backend: Python 3.11 + FastAPI (`dispatch_dispute.py`, `dispatch_dispute_service.py`, `dispatch_dispute_models.py`)
     - State Store: Supabase Store (`orders`, `dispute_reports`, `audit_logs`)
     - Frontend: React 18 + TailwindCSS (`AdminDispatchDisputeView.jsx`, `StalledOrdersTable.jsx`, `DisputeDossierCard.jsx`, `ArbitrationModal.jsx`, `adminDispatchDisputeApi.js`)
  2. **โครงสร้างโมเดลข้อมูลและ API:**
     - `orders` รองรับการคัดกรองคำขอ `S2` ตกค้าง > 30 นาที, บันทึกการขยายรัศมี `search_radius_km` และการมอบหมายงาน `buyer_id`
     - `dispute_reports` บันทึกสำนวนข้อพิพาท 4 มิติ (`dispute_id`, `order_id`, `status: PENDING_ADMIN / RESOLVED_COMPLETED / RESOLVED_CANCELLED`, `arbitrated_amount`, `arbitration_note`)
     - API Endpoints:
       - `GET /api/v1/admin/dispatch/stalled-orders` (ดึงคิวนัดหมายตกค้าง)
       - `POST /api/v1/admin/dispatch/assign` (มอบหมายงานให้ซาเล้งเจาะจง -> S3)
       - `POST /api/v1/admin/dispatch/expand-radius` (ขยายรัศมีการค้นหาเป็น 10 กม.)
       - `GET /api/v1/admin/disputes` (ดึงรายการข้อพิพาท S8)
       - `GET /api/v1/admin/disputes/{dispute_id}` (ดึงสำนวนหลักฐานข้อพิพาท 4 มิติ)
       - `POST /api/v1/admin/disputes/{dispute_id}/resolve` (ตัดสินชี้ขาดให้จบงาน S8->S7 หรือยกเลิก S8->S9)
  3. **การปฏิบัติตาม Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเฉพาะ `CC-01` (ปุ่ม $\ge 48\text{px}$), `CC-03` (สิทธิ์ `X-Admin-Role: ADMIN`), `CC-05` (Online-only สำหรับแอดมิน), `D-00-01` (กรองเฉพาะซาเล้งที่ verified = True สำหรับ Direct Assign), `D-00-02` (ใช้ Price Snapshot ในการพิจารณาข้อพิพาท), และ `REQ-SEC-001` (Audit Logging 4 แอ็กชัน)
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/admin/03-dispatch-and-dispute-center/plan.md`


---

## บันทึก #96 — `/tasks specs/admin/03-dispatch-and-dispute-center/plan.md` (แตกงานย่อยศูนย์ควบคุมการจับคู่งานและข้อพิพาท Admin 03)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/admin/03-dispatch-and-dispute-center/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/03-dispatch-and-dispute-center/plan.md` (v1.0), `specs/admin/03-dispatch-and-dispute-center/spec.md` (v2.0), `specs/000-shared/constraints.md`, `specs/002-route/models.md`
- **ไฟล์ที่สร้าง:** `specs/admin/03-dispatch-and-dispute-center/tasks.md`
- **ผลลัพธ์การแตกงานย่อย (8 งาน `T-01` ถึง `T-08` ครบ 6 ช่องต่อ Task):**
  1. **`T-01`:** สร้าง Data Models และ Schema สำหรับระบบกระจายงานสำรองและตัดสินข้อพิพาท (`dispatch_dispute_models.py`, `supabase.py` ขยาย store methods และ seed ข้อมูล, `test_T01_dispatch_dispute_models.py`)
  2. **`T-02`:** สร้าง Service และ API จัดการคิวนัดหมายตกค้างและการกระจายงานกรณีสำรอง (Manual Dispatch Fallback: กรอง S2 > 30 นาที, Direct Assign -> S3 สำหรับซาเล้งออนไลน์ KYC, Expand Radius เป็น 10.0 กม., `test_AC_A03_01_manual_dispatch.py`)
  3. **`T-03`:** สร้าง Service และ API เรียกดูคิวข้อพิพาทและสำนวนหลักฐาน 4 มิติ (Dispute Dossier: คำขอเดิม, ภาพตาชั่งซาเล้ง, ข้อโต้แย้งผู้ขาย, ข้อมูลติดต่อ, `test_AC_A03_02_dispute_dossier.py`)
  4. **`T-04`:** สร้าง Service และ API ตัดสินชี้ขาดข้อพิพาทให้จบงาน (RESOLVE_COMPLETE -> S7, Arbitrated Amount > 0, ออกใบเสร็จดิจิทัล, `test_AC_A03_03_resolve_complete.py`)
  5. **`T-05`:** สร้าง Service และ API ตัดสินสั่งยกเลิกข้อพิพาท (RESOLVE_CANCEL -> S9), Admin RBAC (`X-Admin-Role: ADMIN` ปฏิเสธ 403), และ Audit Trail 4 แอ็กชัน (`test_AC_A03_04_resolve_cancel.py`, `test_AC_A03_05_admin_dispute_rbac_audit.py`)
  6. **`T-06`:** สร้าง Frontend API Client สำหรับแอดมิน (`adminDispatchDisputeApi.js`, `adminDispatchDisputeApi.test.mjs`)
  7. **`T-07`:** พัฒนาคอมโพเนนต์ React แดชบอร์ดศูนย์ควบคุมการจับคู่งานและข้อพิพาท (`StalledOrdersTable.jsx`, `DisputeDossierCard.jsx`, `ArbitrationModal.jsx`, `AdminDispatchDisputeView.jsx` พร้อม `data-req="UC-13"`, ปุ่ม $\ge 48\text{px}$)
  8. **`T-08`:** สร้างชุดทดสอบ Vitest Component Tests (`AC-A03-01.test.jsx`, `AC-A03-02.test.jsx`, `AC-A03-03.test.jsx`), Integration E2E Test Suite (`test_e2e_admin_dispatch_dispute.py`) และตรวจรับ 5 ด่าน
- **ตารางตรวจทานท้ายไฟล์:**
  - ตาราง Two-way Traceability Matrix ครบทั้ง 5 AC (`AC-A03-01` ถึง `AC-A03-05`) รองรับทั้งหลังบ้าน หน้าบ้าน และ E2E
  - ตาราง Constraints Traceability Matrix ครบทั้ง 13 ข้อ (`CC-01..06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมดำเนินการพัฒนาในขั้นตอน `/implement T-01..08`


---

## บันทึก #101 — `/implement T-01..08` (พัฒนาระบบตรวจสอบ ความปลอดภัย และปฏิบัติตามกฎหมาย Admin Feature 04 เสร็จสมบูรณ์ 100%)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/security_compliance_models.py` (Data Models, Pydantic Schemas, ฟังก์ชันคำนวณ `compute_audit_log_hash` SHA-256)
  - `backend/app/core/supabase.py` (ขยาย `SupabaseStore`: คำนวณ `log_hash` อัตโนมัติใน `add_audit_log`, `record_audit_log`, `add_billing_audit_log`, เมธอด `query_audit_logs`, `verify_audit_logs_integrity`, `get_community_waste_report`, `get_pdpa_retention_status`, `purge_expired_pdpa_data`, และ `_seed_default_security_compliance`)
  - `backend/app/services/security_compliance_service.py` (Service Layer ตรวจสอบ RBAC 4 บทบาท, บริหารจัดการ Audit Trail, Integrity Check, Anonymized Community Report, และ PDPA Retention & Purge)
  - `backend/app/api/v1/security_compliance.py` (FastAPI Router สำหรับ 7 Endpoints ภายใต้แท็ก Admin - Security & Compliance)
  - `backend/app/api/v1/pricing.py` (เมานต์ `admin_security_compliance_router` ภายใต้ prefix `/api/v1/admin/compliance`)
  - `frontend/src/services/adminSecurityComplianceApi.js` (Frontend API Client 7 ฟังก์ชันพร้อม Header แอดมิน `X-Admin-Role`)
  - `frontend/src/components/admin/AuditTrailViewer.jsx` (คอมโพเนนต์ตรวจสอบ Audit Trail, กรองหลายมิติ, Verify SHA-256 Hash, ส่งออก CSV/JSON)
  - `frontend/src/components/admin/CommunityWasteReportView.jsx` (คอมโพเนนต์รายงานสถิติขยะชุมชนรายเขต No PII 100% พร้อมปุ่มส่งออก CSV)
  - `frontend/src/components/admin/PdpaRetentionPanel.jsx` (คอมโพเนนต์ตรวจสอบสถานะ Retention GPS 90 วัน / Masked Address 24 ชม. และปุ่มสั่ง Purge ข้อมูลหมดอายุ)
  - `frontend/src/components/admin/AdminSecurityComplianceView.jsx` (หน้าจอหลัก 3 แท็บ กำกับ `data-req="UC-13"`, แถบ Online-only `CC-05`, ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ทุกปุ่ม)
  - **ชุดทดสอบ Backend (Pytest):**
    - `backend/tests/test_T01_security_compliance_models.py` (4 passed)
    - `backend/tests/test_AC_A04_01_audit_log_query_export.py` (5 passed)
    - `backend/tests/test_AC_A04_02_immutable_audit_integrity.py` (2 passed)
    - `backend/tests/test_AC_A04_03_rbac_enforcement.py` (5 passed)
    - `backend/tests/test_AC_A04_04_pdpa_retention_purge.py` (2 passed)
    - `backend/tests/test_AC_A04_05_community_waste_report.py` (3 passed)
    - `backend/tests/test_e2e_admin_security_compliance.py` (1 passed)
  - **ชุดทดสอบ Frontend (Vitest):**
    - `frontend/tests/adminSecurityComplianceApi.test.mjs` (5 passed)
    - `frontend/tests/AC-A04-01.test.jsx` (2 passed)
    - `frontend/tests/AC-A04-02.test.jsx` (1 passed)
    - `frontend/tests/AC-A04-03.test.jsx` (1 passed)
  - `specs/admin/04-audit-security-and-compliance/tasks.md` (ปรับสถานะเป็น `completed` และติ๊กเสร็จ `[x]` ครบ `T-01` ถึง `T-08`)
- **ผลการตรวจ 5 ด่าน (Quality Gates):**
  1. **ด่านที่ 1 (ความตรงตามสเปก):** ตรวจสอบย้อนกลับรหัส `UC-13`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-OP-001`, `REQ-UX-001`, `CT-01`, `P-07`, `D-A04-01..06`, `AC-A04-01..05` ครบถ้วน 100%
  2. **ด่านที่ 2 (ความถูกต้องตาม Constraints):**
     - `CC-01`: ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ (`min-h-[48px]`, `min-w-[48px]`) ทุกปุ่มบนหน้าจอ React
     - `CC-03`: ควบคุมการเข้าถึงด้วย Header `X-Admin-Role` แยก 4 บทบาท (`ADMIN`, `AUDITOR`, `DPO`, `SUPPORT`) บล็อกคำขอไม่มีสิทธิ์ด้วย 403 Forbidden
     - `CC-04`: Transactional & Append-only integrity ใน Store Layer
     - `CC-05`: Online-only UI พร้อมข้อความแจ้งเตือนโหมดออนไลน์
     - `CC-06`: ปลอด PII 100% ในรายงานสถิติขยะชุมชนรายเขต
     - `REQ-SEC-001` / `P-07`: SHA-256 Checksum ตรวจสอบความถูกต้องและป้องกันการดัดแปลงย้อนหลัง
     - `REQ-SEC-002` / `CT-01`: PDPA Data Retention ล้างพิกัด GPS เกิน 90 วัน และ Mask ที่อยู่หลังจบงานเกิน 24 ชม.
  3. **ด่านที่ 3 (Automated Test Pass):**
     - Backend: 352 passed, 0 failed ในเวลา 1.08 วินาที
     - Frontend: 106 test files passed, 283 passed, 0 failed ในเวลา 7.57 วินาที
  4. **ด่านที่ 4 (Zero Regression):** ไม่มีฟีเจอร์เดิมใดๆ ได้รับผลกระทบหรือทดสอบไม่ผ่าน
  5. **ด่านที่ 5 (Prompt Log Complete):** บันทึกประวัติและผลลัพธ์ลงใน `prompt-log.md` เรียบร้อย
- **สถานะ:** ฟีเจอร์ Admin 04 (และกลุ่ม Admin ครบทั้ง 4 ฟีเจอร์) พัฒนาเสร็จสิ้นสมบูรณ์ 100% พร้อมส่งมอบและตรวจรับ


---

## บันทึก #97 — `/implement T-01..08` (พัฒนาระบบศูนย์ควบคุมการจับคู่งานและข้อพิพาท Admin 03 ครบทั้ง 8 Tasks)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/03-dispatch-and-dispute-center/tasks.md` (v1.0), `specs/admin/03-dispatch-and-dispute-center/plan.md`, `specs/admin/03-dispatch-and-dispute-center/spec.md`, `specs/000-shared/constraints.md`
- **งานย่อยที่พัฒนาครบถ้วน (`T-01` ถึง `T-08`):**
  1. **`T-01` (Data Models & Schemas):**
     - สร้าง `backend/app/models/dispatch_dispute_models.py` (`StalledOrderItem`, `ManualDispatchAssignRequest`, `ExpandDispatchRadiusRequest`, `ManualDispatchResponse`, `ExpandRadiusResponse`, `DisputeDossierResponse`, `DisputeSummaryItem`, `ResolveDisputeRequest`, `ResolveDisputeResponse`)
     - ขยาย `backend/app/core/supabase.py` เพิ่ม `_seed_default_dispatch_dispute`, `get_stalled_orders`, `manual_dispatch_order`, `expand_order_search_radius`, `get_disputes`, `get_dispute_dossier`, `resolve_dispute`
     - ทดสอบ `test_T01_dispatch_dispute_models.py` ผ่าน 7/7 passed
  2. **`T-02` (Stalled Orders Queue & Manual Dispatch Fallback):**
     - พัฒนา `backend/app/services/dispatch_dispute_service.py` (`list_stalled_orders`, `assign_order_manually`, `expand_search_radius`)
     - สร้าง `backend/app/api/v1/dispatch_dispute.py` และเมานต์ใน `backend/app/api/v1/pricing.py`
     - ทดสอบ `test_AC_A03_01_manual_dispatch.py` ผ่าน 4/4 passed (กรองงานตกค้าง > 30 นาที, มอบหมายตรงเปลี่ยนเป็น S3, ขยายรัศมีเป็น 10 กม., Latency < 2.0s)
  3. **`T-03` (Dispute Inspection Dossier Display):**
     - เปิด Endpoint `GET /api/v1/admin/disputes` และ `GET /api/v1/admin/disputes/{dispute_id}`
     - แสดงชุดสำนวนหลักฐาน 4 มิติ: คำขอเดิม & Price Snapshot, ข้อมูลหน้างานและภาพตาชั่ง, ข้อโต้แย้งผู้ขาย, ข้อมูลติดต่อคู่กรณี
     - ทดสอบ `test_AC_A03_02_dispute_dossier.py` ผ่าน 3/3 passed
  4. **`T-04` (Dispute Resolution to Complete):**
     - ตัดสินชี้ขาดให้จบงาน (`RESOLVE_COMPLETE -> S7`) พร้อมยอดเงินชี้ขาดสุทธิ (Arbitrated Amount > 0)
     - สร้างใบเสร็จดิจิทัล (`REC-DISP-...`) ตามยอดเงินชี้ขาด
     - ทดสอบ `test_AC_A03_03_resolve_complete.py` ผ่าน 3/3 passed
  5. **`T-05` (Dispute Resolution to Cancel, RBAC & Audit Trail):**
     - ตัดสินสั่งยกเลิกคำขอ (`RESOLVE_CANCEL -> S9`) โดยไม่มีการชำระเงิน พร้อมบันทึกเหตุผล
     - บังคับ Header `X-Admin-Role: ADMIN` ปฏิเสธ 403 Forbidden หากไม่มีสิทธิ์
     - บันทึก Audit Log แบบ Append-only ทั้ง 4 แอ็กชัน (`ADMIN_MANUAL_DISPATCH`, `ADMIN_EXPAND_DISPATCH_RADIUS`, `ADMIN_RESOLVED_DISPUTE`, `ADMIN_CANCELLED_DISPUTE`)
     - ทดสอบ `test_AC_A03_04_resolve_cancel.py` และ `test_AC_A03_05_admin_dispute_rbac_audit.py` ผ่าน 4/4 passed
  6. **`T-06` (Frontend API Client):**
     - สร้าง `frontend/src/services/adminDispatchDisputeApi.js` รองรับทั้ง 6 เมธอด แนบ Header `X-Admin-Role: ADMIN` อัตโนมัติ
     - ทดสอบ `frontend/tests/adminDispatchDisputeApi.test.mjs` ผ่าน 8/8 passed
  7. **`T-07` (React Admin Dashboard Components):**
     - สร้าง `StalledOrdersTable.jsx`, `DisputeDossierCard.jsx`, `ArbitrationModal.jsx`, `AdminDispatchDisputeView.jsx`
     - กำกับ `data-req="UC-13"`, ป้าย Online-only (`CC-05`), ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ทุกปุ่ม
  8. **`T-08` (Vitest Tests & E2E Integration Suite):**
     - สร้างชุดทดสอบ Vitest: `AC-A03-01.test.jsx`, `AC-A03-02.test.jsx`, `AC-A03-03.test.jsx` ผ่าน 6/6 passed
     - สร้างและทดสอบ Integration E2E `backend/tests/test_e2e_admin_dispatch_dispute.py` ผ่าน 1/1 passed
- **ผลการตรวจ 5 ด่าน:**
  1. `git status`: ตรวจสอบความถูกต้องของไฟล์ที่สร้างและแก้ไขตรงตาม Tasks
  2. ผลรัน Automated Tests:
     - Backend (Pytest): **330/330 passed** (100%)
     - Frontend (Vitest): **274/274 passed** (100% across 102 test suites)
     - รวมทั้งระบบ: **604 passed** ปราศจาก Regression
  3. การอ้างอิง ID: ตรงตาม `UC-13`, `AC-A03-01..05`, `D-A03-01..06`, `CC-01..06`, `REQ-SEC-001`, `REQ-FN-004..005`, `D-00-01..02`
  4. Non-goals: ไม่สร้าง Voice Bot, ไม่สร้าง AI วิเคราะห์เสียง/วิดีโอสด, ไม่สร้าง Escrow Wallet ตามที่กำหนดไว้
  5. ปรับปรุงสถานะ: อัปเดต `specs/admin/03-dispatch-and-dispute-center/tasks.md` เป็นสถานะ `completed`
- **สถานะ:** พัฒนาเสร็จสมบูรณ์ 100%


---

## บันทึก #98 — `/clarify specs/admin/04-audit-security-and-compliance/spec.md` (เคลียร์จุดกำกวมระบบตรวจสอบ ความปลอดภัย และปฏิบัติตามกฎหมาย Admin 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/clarify specs/admin/04-audit-security-and-compliance/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/04-audit-security-and-compliance/spec.md` (Draft), `specs/000-shared/constraints.md`, `docs/srs/operations.md`, `docs/srs/catalogue.md`, `docs/srs/decisions.md`
- **ไฟล์ที่สร้าง/แก้ไข:** `specs/admin/04-audit-security-and-compliance/spec.md` (อัปเกรดเป็น Version 2.0 สถานะ `reviewed-post-clarify`)
- **ข้อสรุปและผลการตัดสินใจ 6 ข้อ (`D-A04-01` ถึง `D-A04-06`):**
  1. **`D-A04-01` (การค้นหา กรอง และส่งออก Audit Trail Log):** รองรับการกรองตาม `action`, `actor_id`, `actor_role` (`ADMIN`, `AUDITOR`, `COLLECTOR`, `SELLER`), ช่วงวันที่ `start_date` ถึง `end_date` พร้อม pagination และปุ่มส่งออกไฟล์ `CSV` และ `JSON`
  2. **`D-A04-02` (การบังคับใช้ RBAC 4 บทบาท):** กำหนด Header `X-Admin-Role`:
     - `ADMIN`: เข้าถึงและจัดการได้ทุกฟังก์ชัน
     - `AUDITOR`: สิทธิ์ Read-only สำหรับดู Audit Log และดาวน์โหลดรายงานสถิติชุมชน (บล็อกการแก้ไขด้วย `403 Forbidden`)
     - `DPO`: เข้าถึงแดชบอร์ด PDPA Compliance และสั่ง Purge ข้อมูลส่วนบุคคลที่หมดอายุ
     - `SUPPORT`: ช่วยเหลือผู้ใช้ทั่วไป แต่ห้ามเข้าถึงระบบ Audit Log เชิงลึก
     - ปฏิเสธคำขอที่ไม่มีสิทธิ์ด้วย `HTTP 403 Forbidden`
  3. **`D-A04-03` (รายงานสถิติขยะชุมชน Anonymized Report):** จัดกลุ่มสถิติระดับเขต/แขวง รายเดือน/ปี แสดงน้ำหนักรวม (`กก.`), มูลค่ารวม (`บาท`), รอบรับซื้อ ปลอดข้อมูล PII 100% ส่งออกเป็น `CSV` และ `JSON` สำหรับส่งมอบ กทม. และเทศบาล
  4. **`D-A04-04` (นโยบาย Data Retention & Purge ตาม PDPA):** พิกัด GPS ซาเล้งเก็บรักษาไว้ไม่เกิน **90 วัน** เพื่อตรวจสอบข้อพิพาท หลังจากนั้น Purge ทิ้ง ข้อมูลบ้านเลขที่ผู้ขายเปิดเผยเฉพาะช่วงเดินทาง และกลับมา Masked ถาวรหลังจบงานเกิน **24 ชั่วโมง** พร้อม API สำหรับ DPO สั่งล้างข้อมูลหมดอายุ
  5. **`D-A04-05` (Immutable Audit Trail & Hash Verification):** บันทึกระเบียนลง `audit_logs` แบบ Append-only ทุกระเบียนคำนวณ `log_hash` ด้วย `SHA-256` พร้อม API ตรวจสอบ Integrity เพื่อยืนยันว่าไม่มีการแก้ไขย้อนหลัง
  6. **`D-A04-06` (หน้าจอแดชบอร์ดความปลอดภัยและตรวจสอบ):** คอมโพเนนต์ SPA 3 แท็บ (Audit Trail Viewer, Anonymized Community Report, PDPA Compliance & Retention) กำกับ `data-req="UC-13"`, ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ทุกปุ่ม, ทำงานในโหมด Online-only (`CC-05`)
- **สถานะ:** Clarification เสร็จสมบูรณ์ สเปก Version 2.0 พร้อมสำหรับการวางแผนในขั้นตอน `/plan specs/admin/04-audit-security-and-compliance/spec.md`


---

## บันทึก #99 — `/plan specs/admin/04-audit-security-and-compliance/spec.md` (จัดทำแผนสถาปัตยกรรมระบบตรวจสอบ ความปลอดภัย และปฏิบัติตามกฎหมาย Admin 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/plan specs/admin/04-audit-security-and-compliance/spec.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/04-audit-security-and-compliance/spec.md` (v2.0), `specs/000-shared/constraints.md`, `docs/srs/operations.md`, `docs/srs/use-cases.md` (`UC-13`), `docs/srs/catalogue.md` (`REQ-SEC-001..002`)
- **ไฟล์ที่สร้าง:**
  - `specs/admin/04-audit-security-and-compliance/plan.md` (แผนทางเทคนิค 8 ส่วนตามมาตรฐาน agent-pack v2: สถาปัตยกรรม, โครงสร้างไฟล์, ฐานข้อมูล, API Specification, แผนระบบภายนอก, แผนหน้าจอ React SPA, แผน Automated Tests, และตารางตรวจ Constraints กลาง 13 ข้อ)
- **ประเด็นสำคัญใน plan.md:**
  1. **สถาปัตยกรรมและเทคโนโลยี (ทีมเลือกเอง ไม่ได้มาจาก spec):**
     - Backend: Python 3.11 + FastAPI (`security_compliance.py`, `security_compliance_service.py`, `security_compliance_models.py`)
     - State Store: Supabase Store (`audit_logs` พร้อม SHA-256 Hash, `orders`, `pickup_locations`)
     - Frontend: React 18 + TailwindCSS (`AdminSecurityComplianceView.jsx`, `AuditTrailViewer.jsx`, `CommunityWasteReportView.jsx`, `PdpaRetentionPanel.jsx`, `adminSecurityComplianceApi.js`)
  2. **โครงสร้างโมเดลข้อมูลและ API:**
     - ตาราง `audit_logs` บันทึกแบบ Append-only เพิ่มฟิลด์ `log_hash` (SHA-256)
     - API Endpoints:
       - `GET /api/v1/admin/compliance/audit-logs` (สืบค้นและกรอง Audit Log)
       - `GET /api/v1/admin/compliance/audit-logs/export` (ส่งออกไฟล์ CSV / JSON)
       - `GET /api/v1/admin/compliance/audit-logs/verify-integrity` (ตรวจสอบความถูกต้องของ Hash)
       - `GET /api/v1/admin/compliance/reports/community-waste` (สรุปสถิติขยะชุมชน ปลอด PII 100%)
       - `GET /api/v1/admin/compliance/reports/community-waste/export` (ส่งออกรายงานชุมชนสำหรับ กทม./เทศบาล)
       - `GET /api/v1/admin/compliance/retention-status` (ตรวจสอบสถานะ Retention พิกัด > 90 วัน)
       - `POST /api/v1/admin/compliance/purge-expired` (สั่ง Purge พิกัดหมดอายุและ Masking ข้อมูลหลัง 24 ชม.)
  3. **การปฏิบัติตาม Constraints กลาง:** ครบทั้ง 13 ข้อตาม `specs/000-shared/constraints.md` โดยเฉพาะ `CC-01` (ปุ่ม $\ge 48\text{px}$), `CC-03` (สิทธิ์ `X-Admin-Role` แยก 4 บทบาท), `CC-05` (Online-only), `CC-06` (ปลอด PII 100%), `REQ-SEC-001` (SHA-256 Hash ใน Audit Log), และ `REQ-SEC-002` (PDPA Retention 90 วัน)
- **สถานะ:** แผน `plan.md` สมบูรณ์ พร้อมเข้าสู่ขั้นตอนการแตกงานย่อย `/tasks specs/admin/04-audit-security-and-compliance/plan.md`


---

## บันทึก #100 — `/tasks specs/admin/04-audit-security-and-compliance/plan.md` (แตกงานย่อยระบบตรวจสอบ ความปลอดภัย และปฏิบัติตามกฎหมาย Admin 04)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/tasks specs/admin/04-audit-security-and-compliance/plan.md`
- **ไฟล์ที่ AI อ่าน:** `AGENTS.md`, `specs/admin/04-audit-security-and-compliance/plan.md` (v1.0), `specs/admin/04-audit-security-and-compliance/spec.md` (v2.0), `specs/000-shared/constraints.md`, `docs/srs/operations.md`
- **ไฟล์ที่สร้าง:** `specs/admin/04-audit-security-and-compliance/tasks.md`
- **ผลลัพธ์การแตกงานย่อย (8 งาน `T-01` ถึง `T-08` ครบ 6 ช่องต่อ Task):**
  1. **`T-01`:** สร้าง Data Models และ Schema สำหรับระบบตรวจสอบ ความปลอดภัย และ PDPA (`security_compliance_models.py`, `compute_audit_log_hash`, `supabase.py` ขยาย store methods และ seed ข้อมูล, `test_T01_security_compliance_models.py`)
  2. **`T-02`:** สร้าง Service และ API สืบค้น กรอง และส่งออก Audit Trail Log (`query_audit_logs`, `export_audit_logs`, เมานต์ใน `pricing.py`, `test_AC_A04_01_audit_log_query_export.py`)
  3. **`T-03`:** สร้าง Service และ API ยืนยันความไม่เปลี่ยนแปลงของ Audit Log ด้วย SHA-256 Hash (`verify_audit_integrity`, `test_AC_A04_02_immutable_audit_integrity.py`)
  4. **`T-04`:** พัฒนาระบบควบคุมการเข้าถึงตามบทบาท (RBAC Enforcement 4 Roles: `ADMIN`, `AUDITOR`, `DPO`, `SUPPORT`, `test_AC_A04_03_rbac_enforcement.py`)
  5. **`T-05`:** สร้าง Service และ API จัดการนโยบายการจัดเก็บและทำลายข้อมูลส่วนบุคคล (`get_retention_status`, `purge_expired_data`, `test_AC_A04_04_pdpa_retention_purge.py`)
  6. **`T-06`:** สร้าง Service และ API สรุปและส่งออกรายงานสถิติขยะชุมชนแบบไม่ระบุตัวตน (`get_community_waste_report`, `export_community_waste_report`, `test_AC_A04_05_community_waste_report.py`)
  7. **`T-07`:** สร้าง Frontend API Client และคอมโพเนนต์ React แดชบอร์ดตรวจสอบและความปลอดภัย (`adminSecurityComplianceApi.js`, `adminSecurityComplianceApi.test.mjs`, `AuditTrailViewer.jsx`, `CommunityWasteReportView.jsx`, `PdpaRetentionPanel.jsx`, `AdminSecurityComplianceView.jsx` พร้อม `data-req="UC-13"`, ปุ่ม $\ge 48\text{px}$)
  8. **`T-08`:** สร้างชุดทดสอบ Vitest Component Tests (`AC-A04-01.test.jsx`, `AC-A04-02.test.jsx`, `AC-A04-03.test.jsx`), Integration E2E Test Suite (`test_e2e_admin_security_compliance.py`) และตรวจรับ 5 ด่าน
- **ตารางตรวจทานท้ายไฟล์:**
  - ตาราง Two-way Traceability Matrix ครบทั้ง 5 AC (`AC-A04-01` ถึง `AC-A04-05`) รองรับทั้งหลังบ้าน หน้าบ้าน และ E2E
  - ตาราง Constraints Traceability Matrix ครบทั้ง 13 ข้อ (`CC-01..06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)
- **สถานะ:** แตกงานย่อยเสร็จสมบูรณ์ พร้อมดำเนินการพัฒนาในขั้นตอน `/implement T-01..08`


---

## บันทึก #101 — `/implement T-01..08` (พัฒนาระบบตรวจสอบ ความปลอดภัย และปฏิบัติตามกฎหมาย Admin Feature 04 เสร็จสมบูรณ์ 100%)
- **วันที่:** 2026-11-04
- **คำสั่งที่ใช้:** `/implement T-01..08`
- **ไฟล์ที่สร้าง/แก้ไข:**
  - `backend/app/models/security_compliance_models.py` (Data Models, Pydantic Schemas, ฟังก์ชันคำนวณ `compute_audit_log_hash` SHA-256)
  - `backend/app/core/supabase.py` (ขยาย `SupabaseStore`: คำนวณ `log_hash` อัตโนมัติใน `add_audit_log`, `record_audit_log`, `add_billing_audit_log`, เมธอด `query_audit_logs`, `verify_audit_logs_integrity`, `get_community_waste_report`, `get_pdpa_retention_status`, `purge_expired_pdpa_data`, และ `_seed_default_security_compliance`)
  - `backend/app/services/security_compliance_service.py` (Service Layer ตรวจสอบ RBAC 4 บทบาท, บริหารจัดการ Audit Trail, Integrity Check, Anonymized Community Report, และ PDPA Retention & Purge)
  - `backend/app/api/v1/security_compliance.py` (FastAPI Router สำหรับ 7 Endpoints ภายใต้แท็ก Admin - Security & Compliance)
  - `backend/app/api/v1/pricing.py` (เมานต์ `admin_security_compliance_router` ภายใต้ prefix `/api/v1/admin/compliance`)
  - `frontend/src/services/adminSecurityComplianceApi.js` (Frontend API Client 7 ฟังก์ชันพร้อม Header แอดมิน `X-Admin-Role`)
  - `frontend/src/components/admin/AuditTrailViewer.jsx` (คอมโพเนนต์ตรวจสอบ Audit Trail, กรองหลายมิติ, Verify SHA-256 Hash, ส่งออก CSV/JSON)
  - `frontend/src/components/admin/CommunityWasteReportView.jsx` (คอมโพเนนต์รายงานสถิติขยะชุมชนรายเขต No PII 100% พร้อมปุ่มส่งออก CSV)
  - `frontend/src/components/admin/PdpaRetentionPanel.jsx` (คอมโพเนนต์ตรวจสอบสถานะ Retention GPS 90 วัน / Masked Address 24 ชม. และปุ่มสั่ง Purge ข้อมูลหมดอายุ)
  - `frontend/src/components/admin/AdminSecurityComplianceView.jsx` (หน้าจอหลัก 3 แท็บ กำกับ `data-req="UC-13"`, แถบ Online-only `CC-05`, ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ ทุกปุ่ม)
  - **ชุดทดสอบ Backend (Pytest):**
    - `backend/tests/test_T01_security_compliance_models.py` (4 passed)
    - `backend/tests/test_AC_A04_01_audit_log_query_export.py` (5 passed)
    - `backend/tests/test_AC_A04_02_immutable_audit_integrity.py` (2 passed)
    - `backend/tests/test_AC_A04_03_rbac_enforcement.py` (5 passed)
    - `backend/tests/test_AC_A04_04_pdpa_retention_purge.py` (2 passed)
    - `backend/tests/test_AC_A04_05_community_waste_report.py` (3 passed)
    - `backend/tests/test_e2e_admin_security_compliance.py` (1 passed)
  - **ชุดทดสอบ Frontend (Vitest):**
    - `frontend/tests/adminSecurityComplianceApi.test.mjs` (5 passed)
    - `frontend/tests/AC-A04-01.test.jsx` (2 passed)
    - `frontend/tests/AC-A04-02.test.jsx` (1 passed)
    - `frontend/tests/AC-A04-03.test.jsx` (1 passed)
  - `specs/admin/04-audit-security-and-compliance/tasks.md` (ปรับสถานะเป็น `completed` และติ๊กเสร็จ `[x]` ครบ `T-01` ถึง `T-08`)
- **ผลการตรวจ 5 ด่าน (Quality Gates):**
  1. **ด่านที่ 1 (ความตรงตามสเปก):** ตรวจสอบย้อนกลับรหัส `UC-13`, `REQ-SEC-001`, `REQ-SEC-002`, `REQ-OP-001`, `REQ-UX-001`, `CT-01`, `P-07`, `D-A04-01..06`, `AC-A04-01..05` ครบถ้วน 100%
  2. **ด่านที่ 2 (ความถูกต้องตาม Constraints):**
     - `CC-01`: ทัชทาร์เก็ตปุ่มกด $\ge 48\text{px}$ (`min-h-[48px]`, `min-w-[48px]`) ทุกปุ่มบนหน้าจอ React
     - `CC-03`: ควบคุมการเข้าถึงด้วย Header `X-Admin-Role` แยก 4 บทบาท (`ADMIN`, `AUDITOR`, `DPO`, `SUPPORT`) บล็อกคำขอไม่มีสิทธิ์ด้วย 403 Forbidden
     - `CC-04`: Transactional & Append-only integrity ใน Store Layer
     - `CC-05`: Online-only UI พร้อมข้อความแจ้งเตือนโหมดออนไลน์
     - `CC-06`: ปลอด PII 100% ในรายงานสถิติขยะชุมชนรายเขต
     - `REQ-SEC-001` / `P-07`: SHA-256 Checksum ตรวจสอบความถูกต้องและป้องกันการดัดแปลงย้อนหลัง
     - `REQ-SEC-002` / `CT-01`: PDPA Data Retention ล้างพิกัด GPS เกิน 90 วัน และ Mask ที่อยู่หลังจบงานเกิน 24 ชม.
  3. **ด่านที่ 3 (Automated Test Pass):**
     - Backend: 352 passed, 0 failed ในเวลา 1.08 วินาที
     - Frontend: 106 test files passed, 283 passed, 0 failed ในเวลา 7.57 วินาที
  4. **ด่านที่ 4 (Zero Regression):** ไม่มีฟีเจอร์เดิมใดๆ ได้รับผลกระทบหรือทดสอบไม่ผ่าน
  5. **ด่านที่ 5 (Prompt Log Complete):** บันทึกประวัติและผลลัพธ์ลงใน `prompt-log.md` เรียบร้อย
- **สถานะ:** ฟีเจอร์ Admin 04 (และกลุ่ม Admin ครบทั้ง 4 ฟีเจอร์) พัฒนาเสร็จสิ้นสมบูรณ์ 100% พร้อมส่งมอบและตรวจรับ
