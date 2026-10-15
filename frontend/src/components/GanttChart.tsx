import { Fragment, useMemo } from 'react';
import type { TaskDate, WbsPhase } from '../api/types';
import { PHASE_LABELS, ROLE_LABELS } from '../lib/format';

interface GanttChartProps {
  tasks: TaskDate[];
  startDate: string;
  endDate: string;
  taskNames?: Record<string, string>;
  breakStart?: string | null;
  breakEnd?: string | null;
  milestones?: Array<{ label: string; date: string }>;
}

const WEEK_WIDTH = 112;

const PHASE_BAR_COLOR: Record<WbsPhase, string> = {
  poc: 'bg-sky-500',
  mvp: 'bg-emerald-500',
  production: 'bg-violet-500',
};

/** Parse "YYYY-MM-DD" → Date theo giờ địa phương (tránh lệch múi giờ). */
function parseDate(value: string): Date {
  const [y, m, d] = value.split('-').map(Number);
  return new Date(y, (m ?? 1) - 1, d ?? 1);
}

/** Số ngày giữa hai mốc (a ≤ b). */
function diffDays(a: Date, b: Date): number {
  return Math.round((b.getTime() - a.getTime()) / 86_400_000);
}

function formatShortDate(value: string): string {
  const [, m, d] = value.split('-');
  return `${Number(d)}/${Number(m)}`;
}

/**
 * Gantt dựng bằng CSS/div từ tasks[] do BACKEND trả (BR-09, spec M4 §4.2):
 * trục ngày từ start_date → end_date, thanh task theo start/end, màu theo phase.
 * FE không tự tính lịch — chỉ vẽ lại đúng dữ liệu response.
 */
export default function GanttChart({ tasks, startDate, endDate, taskNames = {}, breakStart, breakEnd, milestones = [] }: GanttChartProps) {
  const range = useMemo(() => {
    const start = parseDate(startDate);
    const end = parseDate(endDate);
    const totalDays = Math.max(diffDays(start, end) + 1, 1);
    const totalWeeks = Math.max(Math.ceil(totalDays / 7), 1);
    return { start, end, totalDays, totalWeeks };
  }, [startDate, endDate]);

  const weekendSegments = useMemo(() => {
    const segments: { left: number; width: number }[] = [];
    let runStart: number | null = null;
    for (let i = 0; i < range.totalDays; i += 1) {
      const date = new Date(range.start.getFullYear(), range.start.getMonth(), range.start.getDate() + i);
      const isWeekend = date.getDay() === 0 || date.getDay() === 6;
      if (isWeekend && runStart == null) runStart = i;
      if (!isWeekend && runStart != null) {
        segments.push({ left: (runStart / range.totalDays) * 100, width: ((i - runStart) / range.totalDays) * 100 });
        runStart = null;
      }
    }
    if (runStart != null) {
      segments.push({ left: (runStart / range.totalDays) * 100, width: ((range.totalDays - runStart) / range.totalDays) * 100 });
    }
    return segments;
  }, [range]);

  const breakSegment = useMemo(() => {
    if (!breakStart || !breakEnd) return null;
    const start = Math.max(0, diffDays(range.start, parseDate(breakStart)));
    const end = Math.min(range.totalDays - 1, diffDays(range.start, parseDate(breakEnd)));
    if (end < start) return null;
    return { left: (start / range.totalDays) * 100, width: ((end - start + 1) / range.totalDays) * 100 };
  }, [breakStart, breakEnd, range]);

  const milestoneMarkers = milestones.map((milestone) => ({
    ...milestone,
    index: Math.max(0, Math.min(range.totalDays - 1, diffDays(range.start, parseDate(milestone.date)))),
  }));

  if (tasks.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-500" role="status">
        Chưa có task nào để hiển thị Gantt.
      </div>
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-label="Biểu đồ Gantt">
      <h2 className="text-base font-semibold text-slate-900">Biểu đồ Gantt</h2>
      <p className="mt-1 text-xs text-slate-500">
        Lịch theo tuần; ngày từng task do backend tính theo số người/vai trò, nghỉ lễ và buffer.
      </p>

      <div
        className="mt-4 max-h-[480px] overflow-auto rounded-lg border border-slate-200"
        role="region"
        aria-label="Biểu đồ Gantt — cuộn ngang dọc"
        tabIndex={0}
      >
        <div
          className="grid"
          style={{
            minWidth: `${176 + Math.max(range.totalWeeks * WEEK_WIDTH, 556)}px`,
            gridTemplateColumns: `176px minmax(0, 1fr)`,
          }}
        >
          {/* Ô Task (góc) — cố định cả 2 chiều, trùm lên trục tuần + dòng ngày */}
          <div className="sticky left-0 top-0 z-40 row-span-2 flex items-center border-b border-r border-slate-200 bg-white px-3">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Task</span>
          </div>

          {/* Trục tuần — cố định trên cùng khi cuộn dọc */}
          <div className="sticky top-0 z-30 flex h-9 border-b border-slate-200 bg-white">
            {Array.from({ length: range.totalWeeks }, (_, i) => {
              const date = new Date(range.start.getFullYear(), range.start.getMonth(), range.start.getDate() + i * 7);
              const iso = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
              return (
                <div key={iso} className="flex shrink-0 items-center justify-center border-r border-slate-100 px-2 text-center text-[10px] text-slate-500" style={{ width: WEEK_WIDTH }}>
                  <span>
                    Tuần {i + 1}<span className="block text-[9px] text-slate-400">{date.getDate()}/{date.getMonth() + 1}</span>
                  </span>
                </div>
              );
            })}
          </div>

          {/* Dòng ngày tháng — cố định dưới trục tuần */}
          <div className="sticky top-9 z-30 flex h-6 border-b border-slate-200 bg-white">
            {Array.from({ length: range.totalDays }, (_, i) => {
              const date = new Date(range.start.getFullYear(), range.start.getMonth(), range.start.getDate() + i);
              const iso = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
              const isWeekend = date.getDay() === 0 || date.getDay() === 6;
              const isFirstOfMonth = date.getDate() === 1;
              return (
                <div
                  key={iso}
                  className={`flex shrink-0 items-center justify-center border-r border-slate-100 text-[9px] leading-none ${isWeekend ? 'bg-slate-100/70' : ''}`}
                  style={{ width: WEEK_WIDTH / 7 }}
                  title={iso}
                >
                  <span className={isFirstOfMonth ? 'font-semibold text-slate-700' : 'text-slate-400'}>
                    {isFirstOfMonth ? `${date.getDate()}/${date.getMonth() + 1}` : date.getDate()}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Các hàng task — cột tên cố định bên trái khi cuộn ngang */}
          {tasks.map((task) => {
            const startIdx = Math.max(0, diffDays(range.start, parseDate(task.start_date)));
            const endIdx = Math.min(range.totalDays - 1, diffDays(range.start, parseDate(task.end_date)));
            const left = (startIdx / range.totalDays) * 100;
            const width = Math.max(((endIdx - startIdx + 1) / range.totalDays) * 100, 1.5);
            return (
              <Fragment key={task.task_code}>
                <div className="sticky left-0 z-30 border-b border-r border-slate-100 bg-white py-1 pl-3 pr-2">
                  <p className="truncate text-xs font-medium text-slate-700" title={taskNames[task.task_code] ?? task.task_code}>{taskNames[task.task_code] ?? task.task_code}</p>
                  <p className="truncate text-[11px] text-slate-500">
                    {ROLE_LABELS[task.role] ?? 'Vai trò chưa xác định'} · {task.man_day} man-day
                  </p>
                </div>
                <div className="relative h-full min-h-8">
                  {breakSegment && <div className="absolute inset-y-0 z-10 border-x-2 border-dashed border-amber-400 bg-amber-100/60" style={{ left: `${breakSegment.left}%`, width: `${breakSegment.width}%` }} title="Khoảng nghỉ go/no-go" />}
                  {milestoneMarkers.map((marker) => <div key={marker.label} className="absolute inset-y-0 z-20 border-l-2 border-dotted border-blue-500" style={{ left: `${(marker.index / range.totalDays) * 100}%` }} title={`${marker.label}: ${formatShortDate(marker.date)}`} />)}
                  {weekendSegments.map((seg, idx) => (
                    <div
                      key={idx}
                      className="absolute inset-y-0 bg-slate-100/70"
                      style={{ left: `${seg.left}%`, width: `${seg.width}%` }}
                    />
                  ))}
                  <div
                    className={`absolute inset-y-1.5 rounded-md ${PHASE_BAR_COLOR[task.phase]} shadow-sm`}
                    style={{ left: `${left}%`, width: `${width}%`, minWidth: '6px' }}
                    title={`${PHASE_LABELS[task.phase]} · ${formatShortDate(task.start_date)} → ${formatShortDate(task.end_date)}`}
                  />
                </div>
              </Fragment>
            );
          })}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-600">
        {(Object.keys(PHASE_LABELS) as WbsPhase[]).map((phase) => (
          <span key={phase} className="inline-flex items-center gap-1.5">
            <span className={`h-2.5 w-2.5 rounded-sm ${PHASE_BAR_COLOR[phase]}`} aria-hidden="true" />
            {PHASE_LABELS[phase]}
          </span>
        ))}
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm bg-slate-200" aria-hidden="true" />
          Cuối tuần (T7/CN)
        </span>
        {breakSegment && <span className="inline-flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm border border-amber-400 bg-amber-100" aria-hidden="true" />Khoảng nghỉ go/no-go</span>}
        {milestoneMarkers.length > 0 && <span className="inline-flex items-center gap-1.5"><span className="h-2.5 w-2.5 border-l-2 border-dotted border-blue-500" aria-hidden="true" />Mốc khách</span>}
      </div>
    </section>
  );
}
