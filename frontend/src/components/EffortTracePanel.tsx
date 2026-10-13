import type { EffortTrace, AppliedFactor } from '../api/types';

interface Props {
  trace: EffortTrace;
  factors: AppliedFactor[];
  product: number;
  cap: number;
}

export default function EffortTracePanel({ trace, factors, product, cap }: Props) {
  return (
    <details className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
      <summary className="cursor-pointer text-sm font-semibold text-slate-800">
        Xem dấu vết tính toán
      </summary>
      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div><dt className="text-xs text-slate-500">Phiên bản bảng chuẩn</dt><dd className="font-mono text-slate-800">{trace.table_version}</dd></div>
        <div><dt className="text-xs text-slate-500">Nguồn</dt><dd className="break-words text-slate-800">{trace.source}</dd></div>
        <div><dt className="text-xs text-slate-500">Tích hệ số trước trần</dt><dd className="tabular-nums text-slate-800">{trace.factor_product_raw ?? product}</dd></div>
        <div><dt className="text-xs text-slate-500">Tích hệ số sau trần</dt><dd className="tabular-nums text-slate-800">{trace.factor_product_capped ?? product} / trần {cap}</dd></div>
      </dl>
      <p className="mt-4 border-t border-slate-200 pt-3 font-mono text-xs leading-relaxed text-slate-600">{trace.formula}</p>
      {factors.length > 0 && (
        <ul className="mt-3 space-y-2 border-t border-slate-200 pt-3" aria-label="Các hệ số áp dụng">
          {factors.map((factor) => <li key={factor.key} className="flex justify-between gap-4 text-sm"><span className="text-slate-600">{factor.reason}</span><strong className="tabular-nums text-slate-800">×{factor.value}</strong></li>)}
        </ul>
      )}
    </details>
  );
}
