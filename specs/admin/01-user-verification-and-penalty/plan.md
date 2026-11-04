# แผนสถาปัตยกรรมและเทคโนโลยี: ระบบตรวจสอบและอนุมัติผู้ใช้งาน (`specs/admin/01-user-verification-and-penalty/plan.md`)

- **Version:** `1.0` | **Status:** `ready-for-tasks` | **Owner:** กลุ่ม 2 (แพลตฟอร์มรับซื้อของเก่า/ซาเล้ง)
- **อ้างอิงสเปก:** [`specs/admin/01-user-verification-and-penalty/spec.md`](./spec.md) (v2.0)
- **Use Cases หลัก:** `UC-11: ตรวจสอบอนุมัติ KYC และจัดการบทลงโทษผู้ใช้งาน` ([`docs/srs/use-cases.md`](../../../docs/srs/use-cases.md))
- **ข้อจำกัดกลาง:** [`specs/000-shared/constraints.md`](../../000-shared/constraints.md) (`CC-01..CC-06`, `REQ-SEC-001..002`, `REQ-OP-001..002`, `D-00-01..03`)

---

## 1. เทคโนโลยีที่ใช้ (Technology Stack & Architecture)

> [!NOTE]
> **หมายเหตุด้านเทคโนโลยี:** เทคโนโลยีที่ใช้ในโมดูลนี้ **`"ทีมเลือกเอง ไม่ได้มาจาก spec"`** เพื่อให้สอดคล้องกับโครงสร้างและฐานโค้ดหลักของระบบ Saleng:

- **Backend Framework:** **Python 3.11 + FastAPI**
  - สถาปัตยกรรมแบบแยกส่วน: Router (`api/v1/user_verification_penalty.py`), Service Layer (`services/user_verification_penalty_service.py`), และ Data Models (`models/user_verification_penalty_models.py`)
  - ตรวจสอบความถูกต้องของข้อมูลและ Schema ด้วย **Pydantic v2**
  - ควบคุมการเข้าถึงด้วย Role-based Header (`X-Admin-Role: ADMIN`) ส่งกลับ `HTTP 403 Forbidden` หากไม่ใช่แอดมินตาม `CC-03`
  - มาตรฐานรหัสตอบกลับ HTTP: `200 OK`, `201 Created`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`
- **Database & State Store:** **Supabase (PostgreSQL 15+)**
  - ตาราง `collector_kyc_submissions` (สถานะ `PENDING_REVIEW`, `VERIFIED`, `REJECTED`)
  - คอลัมน์สถานะบัญชีใน `saleng_profiles` และ `sellers` (`account_status`: `ACTIVE`, `SUSPENDED_TEMPORARY`, `BANNED`, `penalty_reason`, `penalized_at`)
  - ตาราง `audit_logs` สำหรับจัดเก็บบันทึกประวัติการกระทำของแอดมินตาม `REQ-SEC-001`
- **Frontend Framework:** **React 18 + Vite + TailwindCSS**
  - ออกแบบเป็น Single-Page Application (SPA) รองรับทั้งจอมือถือและแท็บเล็ต/เดสก์ท็อปของแอดมินตาม `CC-01`
  - ทัชทาร์เก็ตปุ่มกดและฟังก์ชันสำคัญขนาดไม่ต่ำกว่า `48px` ทุกปุ่มตาม `REQ-UX-001`
  - แอดมินทำงานแบบ **Online-only** ตาม `CC-05` และ `D-A01-06` เพื่อความปลอดภัยในการระงับสิทธิ์แบบเรียลไทม์
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
│   │   │   ├── user_verification_penalty.py         # [NEW] FastAPI Router สำหรับ Admin KYC & Penalty
│   │   │   └── pricing.py                          # [UPDATE] เมานต์ admin_router เข้ากับแอปหลัก
│   │   ├── core/
│   │   │   └── supabase.py                         # [UPDATE] เพิ่ม helper methods สำหรับ Admin KYC & User Penalty
│   │   ├── models/
│   │   │   └── user_verification_penalty_models.py  # [NEW] Pydantic Schemas สำหรับ KYC review และ User Penalty
│   │   └── services/
│   │       └── user_verification_penalty_service.py # [NEW] Service ตรรกะธุรกิจ KYC Approval และ Penalty Control
│   └── tests/
│       ├── test_T01_admin_user_models.py           # [NEW] ทดสอบ Pydantic Models & Supabase Store methods
│       ├── test_AC_A01_01_kyc_queue.py             # [NEW] ทดสอบคิวคำขอ KYC และ PII Masking
│       ├── test_AC_A01_02_kyc_review.py            # [NEW] ทดสอบการอนุมัติและปฏิเสธ KYC ซาเล้ง
│       ├── test_AC_A01_03_user_penalty.py          # [NEW] ทดสอบการระงับสิทธิ์บัญชี (Suspend/Ban)
│       ├── test_AC_A01_04_user_reactivate.py       # [NEW] ทดสอบการปลดระงับสิทธิ์ผู้ใช้ (Reactivate)
│       ├── test_AC_A01_05_admin_rbac_audit.py      # [NEW] ทดสอบ Admin RBAC Header (403) และ Audit Log
│       └── test_e2e_admin_user_verification_penalty.py # [NEW] ทดสอบ Integration E2E เต็มวงจร
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── admin/
│   │   │       ├── KycReviewQueueCard.jsx          # [NEW] การ์ดตรวจเอกสาร KYC ซาเล้ง + ภาพถ่าย + ปุ่มอนุมัติ/ปฏิเสธ
│   │   │       ├── UserPenaltyControlCard.jsx      # [NEW] การ์ดจัดการสถานะบัญชีผู้ใช้ + ปุ่ม Suspend/Ban/Reactivate
│   │   │       └── AdminUserVerificationView.jsx   # [NEW] หน้าจอหลักแอดมิน สลับแท็บ KYC และ Penalty (data-req="UC-11")
│   │   └── services/
│   │       └── adminUserApi.js                     # [NEW] Frontend API Client สำหรับติดต่อ Admin Endpoints
│   └── tests/
│       ├── adminUserApi.test.mjs                   # [NEW] ทดสอบ Vitest สำหรับ adminUserApi
│       ├── AC-A01-01.test.jsx                      # [NEW] ทดสอบคิวคำขอ KYC และการแสดงผล PII Masking
│       ├── AC-A01-02.test.jsx                      # [NEW] ทดสอบการอนุมัติและปฏิเสธ KYC ใน UI
│       ├── AC-A01-03.test.jsx                      # [NEW] ทดสอบการสั่งระงับสิทธิ์บัญชีใน UI
│       └── AC-A01-04.test.jsx                      # [NEW] ทดสอบการปลดระงับสิทธิ์ใน UI
```

---

## 3. การออกแบบฐานข้อมูล / Data Models (Database & Schema Design)

### 3.1 ตาราง `collector_kyc_submissions` (การตรวจเอกสารยืนยันตัวตนซาเล้ง)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `id` | `UUID / String` | รหัสอ้างอิงคำขอ KYC (Primary Key) |
| `saleng_id` | `String` | รหัสอ้างอิงซาเล้ง (`saleng-xx`) |
| `id_card_no` | `String` | หมายเลขบัตรประชาชน 13 หลัก (จัดเก็บเข้ารหัส ป้องกันรั่วไหล) |
| `full_name` | `String` | ชื่อ-นามสกุลตามบัตรประชาชน |
| `id_card_photo_url` | `String` | URL รูปถ่ายหน้าบัตรประชาชน |
| `selfie_photo_url` | `String` | URL รูปถ่ายหน้าตรงถือบัตรประชาชน |
| `vehicle_photo_url` | `Optional[String]` | URL รูปถ่ายยานพาหนะพร้อมป้ายทะเบียน |
| `status` | `String` | สถานะคำขอ: `PENDING_REVIEW`, `VERIFIED`, `REJECTED` |
| `rejection_reason` | `Optional[String]` | เหตุผลในการปฏิเสธคำขอ (ระบุเมื่อ `status = 'REJECTED'`) |
| `submitted_at` | `String (ISO 8601)` | วันเวลาที่ซาเล้งส่งเอกสารเข้ามา |
| `reviewed_at` | `Optional[String]` | วันเวลาที่แอดมินดำเนินการตรวจสอบ |
| `reviewed_by` | `Optional[String]` | รหัสแอดมินผู้ดำเนินการตรวจสอบ |

### 3.2 ฟิลด์เพิ่มเติมใน `saleng_profiles` และ `sellers` (การควบคุมบทลงโทษ)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `account_status` | `String` | สถานะบัญชี: `ACTIVE` (ปกติ), `SUSPENDED_TEMPORARY` (ระงับชั่วคราว), `BANNED` (ระงับถาวร) |
| `penalty_reason` | `Optional[String]` | เหตุผลในการระงับสิทธิ์ (เช่น โกงตาชั่ง, เบี้ยวนัดหมาย No-show ซ้ำซาก) |
| `penalized_at` | `Optional[String]` | วันเวลาที่ถูกบันทึกบทลงโทษ |
| `penalized_by` | `Optional[String]` | รหัสแอดมินผู้สั่งลงโทษ |

### 3.3 ตาราง `audit_logs` (บันทึกประวัติการจัดการของผู้ดูแลระบบ)
| ชื่อฟิลด์ | ชนิดข้อมูล | เงื่อนไข / คำอธิบาย |
| :--- | :--- | :--- |
| `log_id` | `String` | รหัสบันทึกประวัติ (UUID) |
| `action` | `String` | `ADMIN_APPROVED_KYC`, `ADMIN_REJECTED_KYC`, `ADMIN_PENALIZED_USER`, `ADMIN_UNSUSPENDED_USER` |
| `entity_id` | `String` | รหัสเป้าหมายที่ถูกจัดการ (`saleng_id`, `seller_id`, หรือ `submission_id`) |
| `actor_id` | `String` | รหัสแอดมินผู้กระทำ (เช่น `admin-01`) |
| `actor_role` | `String` | ค่าคงที่ `'ADMIN'` |
| `details` | `JSON / Dict` | รายละเอียดเพิ่มเติม (`rejection_reason`, `penalty_reason`, `status_before`, `status_after`) |
| `timestamp` | `String (ISO 8601)` | เวลาประทับที่เกิดเหตุการณ์ |

---

## 4. การออกแบบ API / Endpoints (API Specification)

ทุกเส้นทางต้องระบุ Header `X-Admin-Role: ADMIN` ตามข้อกำหนด `CC-03` และ `D-A01-05`

### 4.1 รายการ API สำหรับแอดมิน

| Method | Endpoint | Request Body | Response (Success) | Error Codes |
| :---: | :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/admin/kyc/submissions` | Params: `status` (`PENDING_REVIEW`, `ALL`) | `List[KYCSubmissionResponse]` พร้อม PII Masking | `401`, `403` |
| `POST` | `/api/v1/admin/kyc/review` | `KYCReviewRequest` (`submission_id`, `action`: `APPROVE`/`REJECT`, `rejection_reason`) | `KYCReviewResponse` (`success`, `status`, `saleng_id`) | `400`, `403`, `404` |
| `GET` | `/api/v1/admin/users` | Params: `role` (`COLLECTOR`, `SELLER`, `ALL`), `status`, `search` | `List[UserAccountResponse]` | `401`, `403` |
| `POST` | `/api/v1/admin/users/penalty` | `UserPenaltyRequest` (`user_id`, `role`, `action`: `SUSPEND_TEMPORARY`/`BAN`, `penalty_reason`, `duration_days`) | `UserPenaltyResponse` (`success`, `user_id`, `account_status`) | `400`, `403`, `404` |
| `POST` | `/api/v1/admin/users/reactivate` | `UserReactivateRequest` (`user_id`, `role`, `reason`) | `UserReactivateResponse` (`success`, `user_id`, `account_status = 'ACTIVE'`) | `400`, `403`, `404` |

---

## 5. แผนการเชื่อมต่อระบบภายนอก (External Integrations / Third-party Services)

- **Mock Supabase Store:** ใช้งาน In-Memory Storage Adapter ใน `backend/app/core/supabase.py` ขยายฟังก์ชัน `collector_kyc_submissions` และ `user_accounts` โดยไม่ต้องพึ่งพาบริการภายนอกระหว่างการทดสอบอัตโนมัติ (Offline Testing)
- **ระบบภายนอกในอนาคต (Phase ถัดไป):** กรมพัฒนาธุรกิจการค้า (DBD Open API) สำหรับตรวจสอบนิติบุคคลร้านรับซื้อของเก่า ถูกจัดเป็น Non-goals ในรอบนี้ตาม `D-A01-02`

---

## 6. แผนการสร้างหน้าจอและปฏิสัมพันธ์ (Frontend Components & Interactions)

- **Layout & Structure:** หน้าจอแดชบอร์ดแอดมิน (SPA) จัดวางเป็นแท็บ 2 ส่วน:
  1. **แท็บที่ 1: คิวตรวจเอกสาร KYC ซาเล้ง (`KycReviewQueueCard.jsx`)**
     - แสดงรายการคำขอสถานะ `PENDING_REVIEW`
     - แสดงรูปถ่าย 3 ใบ: หน้าบัตรประชาชน, เซลฟี่คู่บัตร, ภาพถ่ายยานพาหนะพร้อมป้ายทะเบียน
     - หมายเลขบัตรประชาชนถูก Masking เป็น `1-1002-XXXXX-XX-X` ตาม `REQ-SEC-002`
     - ปุ่ม "อนุมัติ" (สีเขียว ทัชทาร์เก็ต $\ge 48\text{px}$)
     - ปุ่ม "ปฏิเสธ" (สีแดง ทัชทาร์เก็ต $\ge 48\text{px}$) เมื่อกดจะเปิดช่องป้อนเหตุผล (`rejection_reason`) บังคับกรอก
  2. **แท็บที่ 2: จัดการบทลงโทษผู้ใช้ (`UserPenaltyControlCard.jsx`)**
     - ช่องค้นหาผู้ใช้ตามชื่อ หรือ เบอร์โทรศัพท์ (แสดงแบบ Mask `08X-XXX-XXXX`)
     - ป้ายสถานะบัญชี (`ACTIVE` สีเขียว, `SUSPENDED_TEMPORARY` สีส้ม, `BANNED` สีแดง)
     - ปุ่มเลือกบทลงโทษ: "ระงับชั่วคราว (Suspend)" หรือ "แบนถาวร (Ban)" พร้อมฟอร์มระบุเหตุผล
     - ปุ่ม "ปลดระงับ (Reactivate)" สำหรับคืนสิทธิ์ให้กลับมาเป็น `ACTIVE`
  3. **หน้าจอหลักเชื่อมโยง (`AdminUserVerificationView.jsx`)**
     - กำกับแอตทริบิวต์ `data-req="UC-11"` ครบถ้วนทุกคอมโพเนนต์

---

## 7. การจัดการคำถามเปิดและการตัดสินใจ (Decisions & Open Questions)

- **`D-A01-01` (`Q-01`):** กำหนด Use Case ID เป็น `UC-11: ตรวจสอบอนุมัติ KYC และจัดการบทลงโทษผู้ใช้งาน` สอดคล้องกับ SRS กลาง
- **`D-A01-02` (`Q-02`):** ตรวจสอบคัดกรองเฉพาะซาเล้งบุคคลธรรมดา (`saleng_profiles`) ส่วนนิติบุคคล DBD เป็น Non-goals
- **`D-A01-03` (`Q-03`):** สถานะบัญชี 3 ระดับ: `ACTIVE`, `SUSPENDED_TEMPORARY`, `BANNED` บัญชีติดโทษถูกปฏิเสธด้วย `HTTP 403`
- **`D-A01-04` (`Q-04`):** รองรับบทลงโทษทั้งฝั่งซาเล้ง (โกงตาชั่ง, กดราคา) และฝั่งผู้ขาย (No-show ซ้ำซาก)
- **`D-A01-05` (`Q-05`):** บังคับสิทธิ์แอดมินผ่าน `X-Admin-Role: ADMIN` และบันทึก `audit_logs` ครบทุกขั้นตอนตาม `REQ-SEC-001`
- **`D-A01-06` (`Q-06`):** พัฒนา Admin UI SPA ปุ่มสัมผัส $\ge 48\text{px}$ ตาม `CC-01` และทำงานแบบ Online-only (`CC-05`)

---

## 8. ตารางตรวจ Constraints กลาง (Constraints Compliance Matrix)

| รหัส | หัวข้อข้อจำกัดกลาง (`Constraint`) | การปฏิบัติตามในแผนนี้ (`Compliance Details`) | สถานะ |
| :---: | :--- | :--- | :---: |
| **`CC-01`** | Single-Page Application (SPA) & Touch Target $\ge 48\text{px}$ | ออกแบบแดชบอร์ดแอดมินเป็น React SPA ปุ่มกดอนุมัติ ปฏิเสธ ระงับสิทธิ์ และปลดระงับ มีขนาด $\ge 48\text{px}$ ทุกปุ่ม | สอดคล้อง |
| **`CC-02`** | Architecture (FastAPI Backend + React Frontend) | ใช้ FastAPI ในฝั่งหลังบ้าน และ React 18 + TailwindCSS ในฝั่งหน้าบ้าน แยกส่วนชัดเจน | สอดคล้อง |
| **`CC-03`** | Role-based REST Endpoints (`/api/v1/admin/...`) | แยกเส้นทางแอดมินไว้ใต้ `/api/v1/admin/` และตรวจสอบสิทธิ์ผ่าน Header `X-Admin-Role: ADMIN` | สอดคล้อง |
| **`CC-04`** | Optimistic Concurrency Control / ACID Transaction | การปรับสถานะ KYC และการระงับสิทธิ์บัญชีดำเนินการแบบ Atomic ตรวจสอบเวอร์ชันและล็อกสถานะป้องกัน Race Condition | สอดคล้อง |
| **`CC-05`** | Offline Resilience & Network Handling | หน้าจอแอดมินทำงานแบบ **Online-only** ไม่อนุญาตให้อนุมัติ KYC หรือระงับสิทธิ์ออฟไลน์ เพื่อความปลอดภัยสูงสุด | สอดคล้อง |
| **`CC-06`** | PDPA & PII Protection (`REQ-SEC-002`) | ปกปิดหมายเลขบัตรประชาชนเป็น `1-1002-XXXXX-XX-X` และเบอร์โทรศัพท์เป็น `08X-XXX-XXXX` ในหน้ารวมรายการ | สอดคล้อง |
| **`REQ-SEC-001`** | Audit Logging (Append-only) | บันทึกเหตุการณ์ `ADMIN_APPROVED_KYC`, `ADMIN_REJECTED_KYC`, `ADMIN_PENALIZED_USER`, `ADMIN_UNSUSPENDED_USER` ลงใน `audit_logs` | สอดคล้อง |
| **`REQ-SEC-002`** | Role-based Data Access & Least Privilege | เฉพาะผู้ที่มีสิทธิ์แอดมิน (`X-Admin-Role: ADMIN`) เท่านั้นจึงจะสามารถเปิดดูภาพเอกสาร KYC และจัดการบทลงโทษได้ | สอดคล้อง |
| **`REQ-OP-001`** | Response Time Latency (< 2.0 วินาที P95) | การดึงคิวคำขอ KYC และการอัปเดตสถานะบัญชีตอบสนองภายใน `< 2.0 วินาที` (P95) | สอดคล้อง |
| **`REQ-OP-002`** | System Availability & Operational SLA | ไม่เกี่ยวกับ feature นี้โดยตรง เพราะเป็นข้อกำหนด SLA ระดับโครงสร้างพื้นฐานของระบบภาพรวม | สอดคล้อง |
| **`D-00-01`** | Precondition Gatekeeper for Buyer Verification | เมื่อแอดมินอนุมัติ KYC (`status = 'VERIFIED'`) ระบบจะเปิดสิทธิ์ `saleng_profiles.verified = true` ปลดล็อกให้ซาเล้งเริ่มรับงานใน `UC-04` ได้ | สอดคล้อง |
| **`D-00-02`** | Benchmark Price Lock & Variance ($\pm 15\%$) | ไม่เกี่ยวกับ feature นี้โดยตรง เพราะเป็นข้อกำหนดการชั่งน้ำหนักและการคิดเงินใน `UC-05` / `UC-06` | สอดคล้อง |
| **`D-00-03`** | Dual-Engine Route Optimization | ไม่เกี่ยวกับ feature นี้โดยตรง เพราะเป็นข้อกำหนดอัลกอริทึมจัดคิวและคำนวณเส้นทางใน `UC-04` | สอดคล้อง |

