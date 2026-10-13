import type { QuotationResponse } from '../api/types';
import { formatAmount, formatDate, ROLE_LABELS } from '../lib/format';

export default function QuotationTrace({ quotation }: { quotation: QuotationResponse }) {
  const { totals, trace } = quotation;
  return <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" aria-label="Dấu vết tính toán">
    <h2 className="text-base font-semibold text-slate-900">Dấu vết tính toán</h2>
    <p className="mt-2 font-mono text-xs text-slate-600">{trace.formula}</p>
    <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
      <div><dt className="text-slate-500">Rate card</dt><dd className="font-medium">v{trace.rate_card_version}</dd></div>
      <div><dt className="text-slate-500">Snapshot</dt><dd className="font-medium">#{trace.reference_snapshot_id}</dd></div>
      <div><dt className="text-slate-500">Làm tròn</dt><dd className="font-medium">{trace.rounding}</dd></div>
    </dl>
    <div className="mt-5 overflow-x-auto"><table className="w-full text-left text-sm"><caption className="sr-only">Chi tiết theo vai trò</caption><thead className="border-b border-slate-200 text-xs text-slate-500"><tr><th className="py-2">Vai trò</th><th className="py-2">Man-day</th><th className="py-2">Đơn giá</th><th className="py-2">Thành tiền</th></tr></thead><tbody>{Object.entries(totals.by_role).map(([role, item]) => <tr key={role} className="border-b border-slate-100"><td className="py-2">{ROLE_LABELS[role as keyof typeof ROLE_LABELS] ?? role}</td><td className="py-2 tabular-nums">{item.man_day}</td><td className="py-2 tabular-nums">{formatAmount(item.rate)}</td><td className="py-2 tabular-nums">{formatAmount(item.amount)}</td></tr>)}</tbody></table></div>
    <div className="mt-5 grid gap-3 text-sm sm:grid-cols-2"><div>Overhead PM/BRSE: <strong>{formatAmount(totals.overhead.pm)} / {formatAmount(totals.overhead.brse)}</strong></div><div>Dự phòng: <strong>{formatAmount(totals.contingency_amount)}</strong></div><div>Subtotal: <strong>{formatAmount(totals.subtotal)}</strong></div><div>Tổng cuối: <strong>{formatAmount(totals.grand_total)}</strong></div></div>
    <p className="mt-4 text-xs text-slate-500">Hiệu lực đến {formatDate(quotation.valid_until)} · FX {quotation.fx_rate.pair}: {quotation.fx_rate.value} ({formatDate(quotation.fx_rate.date)})</p>
  </section>;
}
