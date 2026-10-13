import { useMemo } from 'react';
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

      <div className="mt-4 overflow-x-auto">
         <div style={{ minWidth: `${Math.max(range.totalWeeks * WEEK_WIDTH, 640)}px` }}>
           {/* Trục tuần */}
           <div className="flex border-b border-slate-200">
             <div className="w-44 shrink-0" />
             <div className="flex flex-1">
               {Array.from({ length: range.totalWeeks }, (_, i) => {
                 const date = new Date(range.start.getFullYear(), range.start.getMonth(), range.start.getDate() + i * 7);
                 const iso = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                 return (
                   <div key={iso} className="shrink-0 border-r border-slate-100 px-2 py-2 text-center text-[10px] text-slate-500" style={{ width: WEEK_WIDTH }}>
                     Tuần {i + 1}<span className="block text-[9px] text-slate-400">{date.getDate()}/{date.getMonth() + 1}</span>
                   </div>
                 );
              })}
            </div>
          </div>

          {/* Các thanh task */}
          <div className="divide-y divide-slate-100">
            {tasks.map((task) => {
              const startIdx = Math.max(0, diffDays(range.start, parseDate(task.start_date)));
              const endIdx = Math.min(range.totalDays - 1, diffDays(range.start, parseDate(task.end_date)));
              const left = (startIdx / range.totalDays) * 100;
              const width = Math.max(((endIdx - startIdx + 1) / range.totalDays) * 100, 1.5);
              return (
                <div key={task.task_code} className="flex items-center">
                  <div className="w-44 shrink-0 py-1 pr-2">
                   <p className="truncate text-xs font-medium text-slate-700" title={taskNames[task.task_code] ?? task.task_code}>{taskNames[task.task_code] ?? task.task_code}</p>
                    <p className="truncate text-[11px] text-slate-500">
                       {ROLE_LABELS[task.role] ?? 'Vai trò chưa xác định'} · {task.man_day} man-day
                    </p>
                  </div>
                  <div className="relative h-8 flex-1">
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
                </div>
              );
            })}
          </div>
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
