import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError, getSchedule } from '../api/client';
import type { ScheduleResponse } from '../api/types';
import GanttChart from '../components/GanttChart';
import PaymentMilestonesView from '../components/PaymentMilestonesView';
import ScheduleForm from '../components/ScheduleForm';
import { ROLE_LABELS, WORKING_CALENDAR_LABELS, formatDate } from '../lib/format';

/**
 * Trang Master schedule (spec M4 §4.2, FR-034):
 * - Form tham số lịch → PUT /schedule → backend tính lại, không gọi AI.
 * - Gantt (tasks[]), mốc thanh toán, cảnh báo vượt hạn nộp.
 * - Chưa có lịch (409 STATE_CONFLICT) → hiện form để tạo lịch đầu tiên.
 * FE chỉ render response — không tự tính ngày/headcount.
 */
export default function SchedulePage() {
  const { id } = useParams<{ id: string }>();
  const bidId = Number(id);
  const navigate = useNavigate();
  const [savedSchedule, setSavedSchedule] = useState<ScheduleResponse | null>(null);

  const scheduleQuery = useQuery({
    queryKey: ['schedule', bidId],
    queryFn: () => getSchedule(bidId),
    enabled: Number.isFinite(bidId),
    retry: false,
  });

  if (!Number.isFinite(bidId)) {
    return <ErrorState message="Mã hồ sơ không hợp lệ." onBack={() => navigate('/bids')} />;
  }

  if (scheduleQuery.isPending) {
    return (
      <div className="mx-auto max-w-5xl px-5 py-12 text-sm text-slate-500" role="status">
        Đang tải lịch…
      </div>
    );
  }

  const scheduleMissing =
    scheduleQuery.isError &&
    scheduleQuery.error instanceof ApiError &&
    scheduleQuery.error.code === 'STATE_CONFLICT';

  if (scheduleQuery.isError && !scheduleMissing) {
    const message =
      scheduleQuery.error instanceof ApiError
        ? scheduleQuery.error.message
        : 'Không tải được lịch.';
    return <ErrorState message={message} onBack={() => navigate(`/bids/${bidId}`)} />;
  }

  const schedule = savedSchedule ?? scheduleQuery.data ?? null;

  return (
    <div className="mx-auto max-w-5xl px-5 py-8 sm:px-8">
      <button
        type="button"
        onClick={() => navigate(`/bids/${bidId}`)}
        className="text-sm font-medium text-blue-600 hover:text-blue-700"
      >
        ← Hồ sơ
      </button>

      <div className="mt-4 border-b border-slate-200 pb-5">
        <p className="text-sm font-medium text-blue-600">M4 · WBS & lịch trình</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Master schedule</h1>
        <p className="mt-2 text-sm text-slate-600">
          Lịch do backend tính từ WBS × số người/vai trò, ngày nghỉ và buffer — không gọi AI.
        </p>
      </div>

      {scheduleMissing && (
        <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          Chưa có lịch cho hồ sơ này. Điền tham số bên dưới và bấm "Tính lịch" để tạo lịch đầu tiên.
        </div>
      )}

      {schedule && schedule.warning && (
        <div role="alert" className="mt-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {schedule.warning}
        </div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <ScheduleForm bidId={bidId} initial={schedule} onSaved={setSavedSchedule} />

        <div className="space-y-6">
          {schedule && (
            <>
              <section
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                aria-label="Tóm tắt lịch"
              >
                <h2 className="text-base font-semibold text-slate-900">Tóm tắt lịch</h2>
                <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                  <div>
                    <dt className="text-xs text-slate-500">Ngày bắt đầu</dt>
                    <dd className="mt-0.5 font-medium tabular-nums text-slate-800">
                      {formatDate(schedule.start_date)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-500">Ngày kết thúc</dt>
                    <dd className="mt-0.5 font-medium tabular-nums text-slate-800">
                      {formatDate(schedule.end_date)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-500">Buffer</dt>
                    <dd className="mt-0.5 font-medium tabular-nums text-slate-800">
                      {schedule.buffer_days} ngày
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs text-slate-500">Lịch nghỉ</dt>
                    <dd className="mt-0.5 font-medium text-slate-800">
                      {WORKING_CALENDAR_LABELS[schedule.working_calendar] ?? schedule.working_calendar}
                    </dd>
                  </div>
                  {schedule.customer_mvp_start && <div><dt className="text-xs text-slate-500">MVP theo kế hoạch khách</dt><dd className="mt-0.5 font-medium tabular-nums text-slate-800">{formatDate(schedule.customer_mvp_start)}</dd></div>}
                  {schedule.customer_production_start && <div><dt className="text-xs text-slate-500">Production theo kế hoạch khách</dt><dd className="mt-0.5 font-medium tabular-nums text-slate-800">{formatDate(schedule.customer_production_start)}</dd></div>}
                </dl>

                <h3 className="mt-5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Thời lượng theo vai trò
                </h3>
                <table className="mt-2 w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                      <th className="py-1.5 font-medium">Vai trò</th>
                      <th className="py-1.5 text-right font-medium">Man-day</th>
                      <th className="py-1.5 text-right font-medium">Số người</th>
                      <th className="py-1.5 text-right font-medium">Thời lượng (ngày LV)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(schedule.by_role).map(([role, duration]) => (
                      <tr key={role} className="border-b border-slate-100">
                        <td className="py-1.5 text-slate-700">
                          {ROLE_LABELS[role as keyof typeof ROLE_LABELS] ?? role}
                        </td>
                        <td className="py-1.5 text-right tabular-nums text-slate-700">
                          {duration.man_day}
                        </td>
                        <td className="py-1.5 text-right tabular-nums text-slate-700">
                          {duration.headcount}
                        </td>
                        <td className="py-1.5 text-right tabular-nums text-slate-700">
                          {duration.duration_days}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {schedule.holidays_applied.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Ngày nghỉ đã áp dụng
                    </h3>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {schedule.holidays_applied.map((day) => (
                        <span
                          key={day}
                          className="rounded bg-slate-100 px-1.5 py-0.5 text-xs tabular-nums text-slate-600"
                        >
                          {formatDate(day)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </section>

              <section
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                aria-label="Mốc thanh toán"
              >
                <h2 className="text-base font-semibold text-slate-900">Mốc thanh toán</h2>
                <div className="mt-2">
                  <PaymentMilestonesView milestones={schedule.payment_milestones} />
                </div>
              </section>
            </>
          )}
        </div>
      </div>

      {schedule && (
        <div className="mt-6">
          <GanttChart
            tasks={schedule.tasks}
            startDate={schedule.start_date}
            endDate={schedule.end_date}
          />
        </div>
      )}
    </div>
  );
}

function ErrorState({ message, onBack }: { message: string; onBack: () => void }) {
  return (
    <div className="mx-auto max-w-5xl px-5 py-12">
      <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {message}
      </div>
      <button
        type="button"
        onClick={onBack}
        className="mt-3 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
      >
        Về hồ sơ
      </button>
    </div>
  );
}
