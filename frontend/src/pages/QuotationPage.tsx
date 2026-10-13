import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ApiError, getBid, getQuotation } from '../api/client';
import { BID_STATUS } from '../api/types';
import QuotationTrace from '../components/QuotationTrace';
import PriceGateNotice from '../components/PriceGateNotice';
import { formatAmount, formatDate, CONTRACT_MODEL_LABELS } from '../lib/format';

export default function QuotationPage() {
  const id = Number(useParams<{ id: string }>().id);
  const query = useQuery({ queryKey: ['quotation', id], queryFn: () => getQuotation(id), enabled: Number.isFinite(id), retry: false });
  const bidQuery = useQuery({ queryKey: ['bid', id], queryFn: () => getBid(id), enabled: Number.isFinite(id), retry: false });
  if (query.isPending) return <PageMessage text="Đang tải báo giá…" />;
  if (query.isError || !query.data || bidQuery.isError || !bidQuery.data) return <PageMessage text={query.error instanceof ApiError ? query.error.message : bidQuery.error instanceof ApiError ? bidQuery.error.message : 'Không tải được báo giá.'} error />;
  const q = query.data;
  const currency = q.currency ?? q.budget?.currency ?? 'VND';
  const approved = bidQuery.data.status === BID_STATUS.priceApproved;
   return <div className="mx-auto max-w-5xl px-6 py-10"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">Báo giá · Hồ sơ #{id}</p><div className="mt-3 flex flex-wrap items-end justify-between gap-4"><div><h1 className="text-3xl font-bold tracking-tight text-slate-900">Báo giá</h1><p className="mt-1 text-sm text-slate-500">Mô hình {CONTRACT_MODEL_LABELS[q.contract_model as keyof typeof CONTRACT_MODEL_LABELS] ?? q.contract_model} · hiệu lực đến {formatDate(q.valid_until)}</p></div><div className="text-right"><p className="text-xs text-slate-500">Tổng dùng để duyệt nội bộ</p><p className="text-2xl font-bold tabular-nums text-slate-900">{formatAmount(q.totals.grand_total, currency)}</p></div></div><div className="mt-6"><PriceGateNotice approved={approved} /></div><div className="mt-6"><QuotationTrace quotation={q} /></div><div className="mt-5 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-900">Thuế: <strong>{q.tax_mode === 'tax_included' ? 'Đã gồm thuế' : 'Chưa gồm thuế'}</strong>. So sánh ngân sách: {q.budget ? `${formatAmount(q.budget.amount, q.budget.currency)} · chênh lệch ${q.budget.difference == null ? 'chưa đủ dữ liệu' : formatAmount(q.budget.difference, currency)}` : 'khách chưa cung cấp ngân sách'}.</div></div>;
}

function PageMessage({ text, error = false }: { text: string; error?: boolean }) { return <div className="mx-auto max-w-5xl px-6 py-12"><p className={error ? 'rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700' : 'text-sm text-slate-500'} role={error ? 'alert' : 'status'}>{text}</p></div>; }
