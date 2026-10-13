import type { WbsCheck } from '../api/types';

interface CheckWarningsProps {
  check: WbsCheck;
}

/**
 * Hiển thị kết quả kiểm tra ngữ nghĩa WBS do BACKEND tính (FR-032, spec M4 §2.1):
 * ±20% so midpoint, PM/QA mỗi phase, không vòng phụ thuộc, lá ≤ 10 man-day.
 * FE chỉ render các cờ từ response — KHÔNG tự suy diễn/tính lại (BR-01).
 */
export default function CheckWarnings({ check }: CheckWarningsProps) {
  const flags = [
    { key: 'within_20pct' as const, label: 'Tổng effort trong ±20% midpoint', ok: check.within_20pct },
    { key: 'pm_qa_ok' as const, label: 'Mỗi phase có PM + QA', ok: check.pm_qa_ok },
    { key: 'cycle_free' as const, label: 'Phụ thuộc không vòng', ok: check.cycle_free },
    { key: 'leaf_within_limit' as const, label: 'Mọi task lá ≤ 10 man-day', ok: check.leaf_within_limit },
  ];

  return (
    <div className="space-y-3">
      {check.warning && (
        <div
          role="alert"
          className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
        >
          <p className="font-medium">Cảnh báo</p>
          <p className="mt-1">{check.warning}</p>
        </div>
      )}

      <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {flags.map((flag) => (
          <li
            key={flag.key}
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
              flag.ok
                ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
                : 'border-red-200 bg-red-50 text-red-800'
            }`}
          >
            <span aria-hidden="true">{flag.ok ? '✓' : '✗'}</span>
            <span>{flag.label}</span>
          </li>
        ))}
      </ul>

      <dl className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-slate-600">
        <div>
          <dt className="inline text-slate-500">Midpoint: </dt>
          <dd className="inline font-semibold tabular-nums text-slate-900">{check.midpoint}</dd>
        </div>
        <div>
          <dt className="inline text-slate-500">Độ lệch: </dt>
          <dd className="inline font-semibold tabular-nums text-slate-900">
            {check.deviation_pct}%
          </dd>
        </div>
        <div>
          <dt className="inline text-slate-500">Lá lớn nhất: </dt>
          <dd className="inline font-semibold tabular-nums text-slate-900">
            {check.leaf_max_man_day} man-day
          </dd>
        </div>
      </dl>
    </div>
  );
}