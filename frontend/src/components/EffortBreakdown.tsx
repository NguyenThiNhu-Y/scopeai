import type { EffortResponse } from '../api/types';
import { SOLUTION_DIRECTION_LABELS } from './SolutionDirectionSelector';
import EffortTracePanel from './EffortTracePanel';

const PHASES = [
  ['poc', 'PoC'],
  ['mvp', 'MVP'],
  ['production', 'Production'],
] as const;
const FACTOR_LABELS: Record<string, string> = { customer_jp: 'Khách hàng Nhật', data_complexity: 'Độ phức tạp dữ liệu', integration: 'Tích hợp', security: 'Bảo mật', solution_direction: 'Hướng giải pháp' };

export default function EffortBreakdown({ effort }: { effort: EffortResponse }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-label="Effort">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><p className="text-xs font-semibold uppercase tracking-wider text-blue-600">Effort do code tính</p><h2 className="mt-1 text-lg font-semibold text-slate-900">{SOLUTION_DIRECTION_LABELS[effort.direction]}</h2></div>
        <div className="text-right"><p className="text-xs text-slate-500">Tổng midpoint</p><p className="text-2xl font-bold tabular-nums text-slate-900">{effort.midpoint_total}</p><p className="text-xs text-slate-500">man-day</p></div>
      </div>
      <div className="mt-5 grid grid-cols-1 gap-2 sm:grid-cols-3">
        {PHASES.map(([key, label]) => { const range = effort.by_phase[key]; return <div key={key} className="rounded-lg border border-slate-200 px-4 py-3"><p className="text-xs font-semibold text-slate-500">{label}</p><p className="mt-1 text-lg font-semibold tabular-nums text-slate-900">{range.min}–{range.max}</p><p className="text-xs text-slate-500">man-day</p></div>; })}
      </div>
      <div className="mt-4 flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-600">
        <span>Hệ số áp dụng: <strong className="tabular-nums text-slate-900">×{effort.factor_product}</strong></span>
        <span>Trần: <strong className="tabular-nums text-slate-900">×{effort.cap}</strong></span>
      </div>
      {effort.factors.length > 0 && (
        <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200">
          <table className="min-w-full text-left text-sm">
            <caption className="sr-only">Bảng hệ số dùng để tính effort</caption>
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr><th className="px-3 py-2 font-semibold">Hệ số</th><th className="px-3 py-2 font-semibold">Giá trị</th><th className="px-3 py-2 font-semibold">Lý do</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {effort.factors.map((factor) => (
                <tr key={factor.key}>
                  <td className="px-3 py-2 font-medium text-slate-800">{FACTOR_LABELS[factor.key] ?? 'Hệ số bổ sung'}</td>
                  <td className="px-3 py-2 tabular-nums text-slate-800">×{factor.value}</td>
                  <td className="px-3 py-2 text-slate-600">{factor.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="mt-4"><EffortTracePanel trace={effort.trace} factors={effort.factors} product={effort.factor_product} cap={effort.cap} /></div>
    </section>
  );
}
