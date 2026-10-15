import { useQuery } from '@tanstack/react-query';
import { getConfidence } from '../api/client';
import type { AnalogCase, HistoryBiasOut, WbsPhase } from '../api/types';
import { MARKET_LABELS, PHASE_LABELS, SOLUTION_LABELS, formatManDay } from '../lib/format';

const PHASES: WbsPhase[] = ['poc', 'mvp', 'production'];

/**
 * Khoảng thực tế (min–max) của một giai đoạn từ các case tương tự.
 * Trả null khi không case nào có actual_man_day cho giai đoạn đó.
 */
export function phaseActualRange(cases: AnalogCase[], phase: string): { min: number; max: number } | null {
  const values = cases
    .map((caseItem) => caseItem.actual_man_day?.[phase])
    .filter((value): value is number => typeof value === 'number' && Number.isFinite(value));
  if (values.length === 0) return null;
  return { min: Math.min(...values), max: Math.max(...values) };
}

/**
 * Dòng "Sai lệch lịch sử" (thiet_ke_danh_gia.md §7). Trả null khi chưa đủ
 * dữ liệu (dưới 2 case cùng hướng) — UI hiện "Chưa đủ dữ liệu tham chiếu".
 */
export function historyBiasText(bias: HistoryBiasOut | null | undefined): string | null {
  if (!bias || (bias.case_count ?? 0) < 2 || bias.median_actual_over_estimate == null) return null;
  const pct = Math.round(Math.abs(bias.median_actual_over_estimate - 1) * 100);
  const trend =
    bias.direction === 'above'
      ? `thực tế thường cao hơn ước lượng ${pct}%`
      : bias.direction === 'below'
        ? `thực tế thường thấp hơn ước lượng ${pct}%`
        : 'thực tế tương đương ước lượng';
  return `Sai lệch lịch sử: ${trend} (${bias.case_count} dự án cùng hướng)`;
}

function CaseTable({ cases }: { cases: AnalogCase[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] text-sm">
        <thead>
          <tr className="border-b border-[var(--line)] text-left text-xs text-[var(--muted)]">
            <th className="py-2 pr-3">Tên</th>
            <th className="py-2 pr-3">Hướng</th>
            <th className="py-2 pr-3">Thị trường</th>
            <th className="py-2 pr-3 text-right">Req</th>
            <th className="py-2 pr-3 text-right">PoC</th>
            <th className="py-2 pr-3 text-right">MVP</th>
            <th className="py-2 pr-3 text-right">Production</th>
            <th className="py-2 pr-3 text-right">Tổng</th>
            <th className="py-2 text-right">Tuần</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((caseItem) => (
            <tr key={caseItem.id} className="border-b border-[var(--line)]">
              <td className="py-2 pr-3 text-[var(--ink)]">{caseItem.title}</td>
              <td className="py-2 pr-3">{caseItem.direction ? (SOLUTION_LABELS[caseItem.direction] ?? caseItem.direction) : '—'}</td>
              <td className="py-2 pr-3">{caseItem.market ? (MARKET_LABELS[caseItem.market] ?? caseItem.market) : '—'}</td>
              <td className="py-2 pr-3 text-right tabular-nums">{caseItem.requirement_count ?? '—'}</td>
              <td className="py-2 pr-3 text-right tabular-nums">{formatManDay(caseItem.actual_man_day?.poc)}</td>
              <td className="py-2 pr-3 text-right tabular-nums">{formatManDay(caseItem.actual_man_day?.mvp)}</td>
              <td className="py-2 pr-3 text-right tabular-nums">{formatManDay(caseItem.actual_man_day?.production)}</td>
              <td className="py-2 pr-3 text-right font-semibold tabular-nums text-[var(--ink)]">{formatManDay(caseItem.actual_total)}</td>
              <td className="py-2 text-right tabular-nums">
                {caseItem.actual_duration_weeks
                  ? Object.entries(caseItem.actual_duration_weeks)
                      .filter(([, value]) => value != null && value !== '')
                      .map(([key, value]) => `${PHASE_LABELS[key as WbsPhase] ?? key} ${value}`)
                      .join(', ')
                  : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PhaseBar({
  phase,
  estimate,
  cases,
}: {
  phase: WbsPhase;
  estimate: number | null;
  cases: AnalogCase[];
}) {
  const range = phaseActualRange(cases, phase);
  if (!range) {
    return (
      <div className="text-xs text-[var(--muted)]">
        {PHASE_LABELS[phase]}: chưa có dữ liệu thực tế giai đoạn này
      </div>
    );
  }
  const maxValue = Math.max(range.max, estimate ?? 0, 1);
  const left = (range.min / maxValue) * 100;
  const width = ((range.max - range.min) / maxValue) * 100;
  const estimateLeft = estimate == null ? null : (estimate / maxValue) * 100;
  return (
    <div className="grid grid-cols-[72px_1fr_auto] items-center gap-2 text-xs">
      <span className="text-[var(--muted)]">{PHASE_LABELS[phase]}</span>
      <div className="relative h-4 rounded bg-slate-100">
        <div className="absolute inset-y-0 rounded bg-emerald-200/80" style={{ left: `${left}%`, width: `${width}%` }} title={`Khoảng thực tế ${formatManDay(range.min)}–${formatManDay(range.max)}`} />
        {estimateLeft != null && (
          <div className="absolute top-0 h-full w-0.5 bg-blue-600" style={{ left: `${estimateLeft}%` }} title={`Ước lượng ${formatManDay(estimate)}`} />
        )}
      </div>
      <span className="tabular-nums text-[var(--muted)]">
        ƯL {estimate == null ? '—' : formatManDay(estimate)} · TT {formatManDay(range.min)}–{formatManDay(range.max)}
      </span>
    </div>
  );
}

/**
 * Khối "So với dự án tương tự" trong tab Kế hoạch & báo giá (thiet_ke_danh_gia.md §7):
 * bảng case + thanh so sánh từng giai đoạn (ước lượng WBS vs khoảng thực tế) +
 * dòng sai lệch lịch sử. Trạng thái "Chưa đủ dữ liệu tham chiếu" khi position=insufficient.
 */
export default function AnalogCompare({
  bidId,
  enabled,
  wbsByPhase,
}: {
  bidId: number;
  enabled: boolean;
  wbsByPhase?: Partial<Record<WbsPhase, number>>;
}) {
  const query = useQuery({
    queryKey: ['confidence', bidId],
    queryFn: () => getConfidence(bidId),
    enabled,
    retry: false,
  });

  const analog = query.data?.analog;
  const cases = analog?.cases ?? [];
  const insufficient = !analog || analog.position === 'insufficient' || cases.length < 2;

  return (
    <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm" aria-label="So với dự án tương tự">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--brand)]">Tham chiếu</p>
        <h2 className="mt-1 text-xl font-semibold text-[var(--ink)]">So với dự án tương tự</h2>
        <p className="mt-1 text-sm text-[var(--muted)]">Effort thực tế của các dự án cùng hướng trong thư viện case study — chỉ để cảnh báo, không tự sửa con số.</p>
      </div>
      <div className="mt-4">
        {query.isPending ? (
          query.fetchStatus === 'idle' ? (
            <p className="rounded-lg border border-dashed border-[var(--line)] bg-[var(--page)] p-4 text-sm text-[var(--muted)]">
              Chưa đủ dữ liệu tham chiếu.
            </p>
          ) : (
            <p role="status" className="text-sm text-[var(--muted)]">Đang tải dữ liệu tham chiếu…</p>
          )
        ) : query.isError || insufficient ? (
          <p className="rounded-lg border border-dashed border-[var(--line)] bg-[var(--page)] p-4 text-sm text-[var(--muted)]">
            Chưa đủ dữ liệu tham chiếu{analog ? `: ${cases.length} case tương tự` : ''}.
          </p>
        ) : (
          <>
            <CaseTable cases={cases} />
            <div className="mt-4 space-y-2">
              {PHASES.map((phase) => (
                <PhaseBar key={phase} phase={phase} estimate={wbsByPhase?.[phase] ?? null} cases={cases} />
              ))}
            </div>
            {(() => {
              const biasText = historyBiasText(analog.history_bias);
              return (
                <p className={`mt-4 rounded-lg px-3 py-2 text-sm ${biasText ? 'bg-slate-50 text-[var(--ink)]' : 'text-[var(--muted)]'}`}>
                  {biasText ?? 'Sai lệch lịch sử: Chưa đủ dữ liệu tham chiếu (dưới 2 case cùng hướng).'}
                </p>
              );
            })()}
          </>
        )}
      </div>
    </section>
  );
}