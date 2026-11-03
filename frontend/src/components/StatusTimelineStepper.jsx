/**
 * แถบแสดงขั้นตอนความคืบหน้า 5 ขั้นหลักตามผัง 9 สถานะ MD-STM-04 (StatusTimelineStepper)
 * รองรับ UC-04, MD-STM-04, REQ-FN-003, REQ-UX-001, AC-S05-02, P-02
 */

import React from 'react';

const STEPS = [
  { step: 1, title: 'ส่งคำขอ', desc: 'รอซาเล้งรับงาน', icon: '📝' },
  { step: 2, title: 'มีผู้รับงาน', desc: 'ซาเล้งยืนยันแล้ว', icon: '🤝' },
  { step: 3, title: 'กำลังเดินทาง', desc: 'ติดตามเส้นทางสด', icon: '🛵' },
  { step: 4, title: 'ถึงหน้างาน', desc: 'ตรวจชั่งน้ำหนัก', icon: '⚖️' },
  { step: 5, title: 'ปิดงานสำเร็จ', desc: 'รับชำระเงิน', icon: '✅' },
];

export default function StatusTimelineStepper({
  status = 'S2',
  statusLabel = 'รอซาเล้งรับงาน',
  stepperStep = 1,
  scheduledTimeDisplay = '',
  cancellationReason = '',
}) {
  const isCancelled = status === 'S8';
  const isDisputed = status === 'S9';

  return (
    <div
      data-req="UC-04"
      data-testid="status-stepper"
      className="p-4 bg-white rounded-3xl border border-gray-200 shadow-2xs space-y-4"
    >
      {/* สถานะปัจจุบัน Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
            สถานะคำขอ ({status})
          </span>
          <h3
            data-testid="status-label"
            className={`text-base font-bold ${
              isCancelled
                ? 'text-red-600'
                : isDisputed
                ? 'text-amber-600'
                : 'text-emerald-700'
            }`}
          >
            {statusLabel}
          </h3>
        </div>
        {scheduledTimeDisplay && (
          <span
            data-testid="scheduled-time-badge"
            className="text-[11px] bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full font-medium border border-emerald-200"
          >
            ⏰ {scheduledTimeDisplay}
          </span>
        )}
      </div>

      {/* แจ้งเตือนกรณียกเลิก หรือ ข้อพิพาท */}
      {isCancelled && (
        <div
          data-testid="cancellation-banner"
          className="p-3 bg-red-50 border border-red-200 rounded-2xl text-xs text-red-700 flex items-start gap-2"
        >
          <span className="text-base">⚠️</span>
          <div>
            <p className="font-bold">นัดหมายนี้ถูกยกเลิกแล้ว</p>
            {cancellationReason && (
              <p className="text-[11px] text-red-600 mt-0.5">เหตุผล: {cancellationReason}</p>
            )}
          </div>
        </div>
      )}

      {isDisputed && (
        <div
          data-testid="dispute-banner"
          className="p-3 bg-amber-50 border border-amber-200 rounded-2xl text-xs text-amber-700 flex items-start gap-2"
        >
          <span className="text-base">⚖️</span>
          <div>
            <p className="font-bold">มีข้อพิพาท</p>
            <p className="text-[11px] text-amber-600 mt-0.5">
              เจ้าหน้าที่กำลังประสานงานและตรวจสอบรายละเอียด
            </p>
          </div>
        </div>
      )}

      {/* Timeline Stepper 5 ขั้น */}
      <div className="relative pt-2 pb-1">
        {/* เส้นเชื่อมระหว่างขั้นตอน */}
        <div className="absolute top-5 left-4 right-4 h-1 bg-gray-200 -z-0">
          <div
            className={`h-full transition-all duration-300 ${
              isCancelled ? 'bg-red-400' : 'bg-emerald-500'
            }`}
            style={{
              width: isCancelled
                ? '0%'
                : `${Math.min(100, Math.max(0, ((stepperStep - 1) / (STEPS.length - 1)) * 100))}%`,
            }}
          />
        </div>

        <div className="grid grid-cols-5 gap-1 relative z-10">
          {STEPS.map((s) => {
            const isCompleted = !isCancelled && stepperStep > s.step;
            const isCurrent = !isCancelled && stepperStep === s.step;

            let circleClass = 'bg-gray-100 text-gray-400 border-2 border-gray-300';
            if (isCompleted) {
              circleClass = 'bg-emerald-600 text-white border-2 border-emerald-600 shadow-xs';
            } else if (isCurrent) {
              circleClass =
                'bg-white text-emerald-600 border-2 border-emerald-600 ring-4 ring-emerald-100 font-bold';
            } else if (isCancelled) {
              circleClass = 'bg-gray-100 text-gray-300 border-2 border-gray-200';
            }

            return (
              <div
                key={s.step}
                data-testid={`stepper-step-${s.step}`}
                data-active={isCurrent ? 'true' : 'false'}
                data-completed={isCompleted ? 'true' : 'false'}
                className="flex flex-col items-center text-center"
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs transition-colors ${circleClass}`}
                >
                  {isCompleted ? '✓' : s.step}
                </div>
                <span
                  className={`text-[10px] font-medium mt-1.5 line-clamp-1 ${
                    isCurrent
                      ? 'text-emerald-700 font-bold'
                      : isCompleted
                      ? 'text-gray-700'
                      : 'text-gray-400'
                  }`}
                >
                  {s.title}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

