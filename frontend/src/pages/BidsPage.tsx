import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ApiError, listBids } from '../api/client';
import { BID_STATUS } from '../api/types';
import BidStatusBadge from '../components/BidStatusBadge';
import { LANGUAGE_LABELS, formatDate } from '../lib/format';

const PAGE_SIZE = 10;
const DEAL_STAGES = ['discovery', 'qualification', 'proposal', 'negotiation', 'won', 'lost'];
const DEAL_STAGE_LABELS: Record<string, string> = {
  discovery: 'Tìm hiểu',
  qualification: 'Đánh giá cơ hội',
  proposal: 'Đề xuất',
  negotiation: 'Thương lượng',
  won: 'Đã thắng',
  lost: 'Đã thua',
};

const STATUS_FILTERS: { value: string; label: string }[] = [
  { value: '', label: 'Tất cả trạng thái' },
  { value: 'draft', label: 'Nháp' },
  { value: 'analyzing', label: 'Đang phân tích' },
  { value: BID_STATUS.clarification, label: 'Chờ làm rõ' },
  { value: BID_STATUS.technicalApproval, label: 'Chờ duyệt kỹ thuật' },
  { value: BID_STATUS.priceApproval, label: 'Chờ duyệt giá' },
  { value: BID_STATUS.priceApproved, label: 'Đã duyệt giá' },
  { value: 'rejected', label: 'Từ chối' },
  { value: 'error', label: 'Lỗi' },
];

function daysUntil(date: string): number | null {
  const deadline = new Date(`${date}T00:00:00`);
  if (Number.isNaN(deadline.getTime())) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.ceil((deadline.getTime() - today.getTime()) / 86_400_000);
}

function deadlineLabel(date: string): { text: string; urgent: boolean } {
  const days = daysUntil(date);
  if (days == null) return { text: formatDate(date), urgent: false };
  if (days < 0) return { text: `${formatDate(date)} · quá hạn`, urgent: true };
  if (days <= 7) return { text: `${formatDate(date)} · còn ${days} ngày`, urgent: true };
  return { text: `${formatDate(date)} · còn ${days} ngày`, urgent: false };
}

function formatPrice(value: number | null | undefined, currency: string | null | undefined): string {
  if (value == null || !currency) return 'Chưa có giá';
  return `${new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 0 }).format(value)} ${currency}`;
}

/**
 * Danh sách hồ sơ (FR-007): bảng + lọc status + tìm q (debounce) + phân trang.
 * Row click → /bids/{id}.
 */
export default function BidsPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState('');
  const [q, setQ] = useState('');
  const [debouncedQ, setDebouncedQ] = useState('');
  const [page, setPage] = useState(1);
  const [dealStage, setDealStage] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQ(q), 300);
    return () => clearTimeout(timer);
  }, [q]);

  // Đổi filter / từ khóa → quay về trang 1.
  useEffect(() => {
    setPage(1);
  }, [status, debouncedQ]);

  const { data, isPending, isError, error, isFetching, refetch } = useQuery({
    queryKey: ['bids', { status, q: debouncedQ, dealStage, page }],
    queryFn: () =>
      listBids({
        status: status || undefined,
        q: debouncedQ || undefined,
        deal_stage: dealStage || undefined,
        page,
        page_size: PAGE_SIZE,
      }),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  const errorMessage =
    error instanceof ApiError ? error.message : 'Không tải được danh sách hồ sơ.';
  const serverStats = data?.stats;
  // "Chờ duyệt" = chờ duyệt kỹ thuật + chờ duyệt giá (backend stats chưa có → tính từ items).
  const waitingApproval = data?.items.filter(
    (item) => item.status === BID_STATUS.technicalApproval || item.status === BID_STATUS.priceApproval,
  ).length ?? 0;
  const stats = [
    ['Tổng hồ sơ', serverStats?.total ?? data?.total ?? 0],
    ['Đang xử lý', serverStats?.analyzing ?? data?.items.filter((item) => item.status === 'analyzing').length ?? 0],
    ['Chờ làm rõ', serverStats?.waiting_clarification ?? data?.items.filter((item) => item.status === BID_STATUS.clarification).length ?? 0],
    ['Chờ duyệt', waitingApproval],
    ['Đã duyệt giá', serverStats?.price_approved ?? data?.items.filter((item) => item.status === BID_STATUS.priceApproved).length ?? 0],
    ['Đã gửi', serverStats?.sent ?? 0],
  ] as const;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-8 sm:py-10">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
            Không gian presales
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-[var(--ink)]">Danh sách hồ sơ</h1>
          <p className="mt-2 max-w-xl text-sm text-[var(--muted)]">
            Theo dõi các cơ hội đang phân tích và mở nhanh hồ sơ cần xử lý.
          </p>
        </div>
        <button
          type="button"
          onClick={() => navigate('/bids/new')}
          className="rounded-lg bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[var(--accent-strong)]"
        >
          Tạo hồ sơ
        </button>
      </div>

      <div className="mt-8 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-3 shadow-sm sm:p-4">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-56 flex-1">
          <label htmlFor="bid-search" className="sr-only">
            Tìm kiếm hồ sơ
          </label>
          <input
            id="bid-search"
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Tìm theo tên dự án / khách hàng…"
            className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/20"
          />
          </div>
          <div>
          <label htmlFor="bid-status-filter" className="sr-only">
            Lọc theo trạng thái
          </label>
          <select
            id="bid-status-filter"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--ink)] focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/20"
          >
            {STATUS_FILTERS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
          </div>
          <div className="min-w-44">
            <label htmlFor="bid-deal-stage-filter" className="mb-1 block text-xs font-medium text-[var(--muted)]">
              Giai đoạn deal
            </label>
            <select
              id="bid-deal-stage-filter"
              value={dealStage}
              onChange={(e) => setDealStage(e.target.value)}
              className="w-full rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--ink)]"
            >
              <option value="">Tất cả giai đoạn</option>
               {DEAL_STAGES.map((stage) => <option key={stage} value={stage}>{DEAL_STAGE_LABELS[stage]}</option>)}
            </select>
          </div>
        </div>
        <p id="deal-stage-filter-help" className="mt-2 text-xs text-[var(--muted)]">
          Giai đoạn sẽ hiển thị khi hồ sơ đã được phân loại.
        </p>
      </div>
       <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6" aria-label="Thống kê danh sách hồ sơ">
        {stats.map(([label, value]) => <div key={label} className="rounded-xl border border-[var(--line)] bg-[var(--surface)] px-4 py-4 shadow-sm"><p className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{label}</p><p className="mt-2 text-2xl font-bold tabular-nums text-[var(--ink)]">{value}</p></div>)}
      </div>

      {isPending ? (
        <p className="mt-8 text-sm text-[var(--muted)]" role="status">
          Đang tải danh sách hồ sơ…
        </p>
      ) : isError ? (
        <div className="mt-8 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <p className="text-sm font-medium text-red-700">{errorMessage}</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-2 rounded-lg bg-red-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-red-700"
          >
            Thử lại
          </button>
        </div>
      ) : data.items.length === 0 ? (
        <div className="mt-8 rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
          <p className="text-sm font-medium text-slate-700">
            Chưa có hồ sơ — bấm Tạo hồ sơ hoặc Nạp hồ sơ mẫu
          </p>
          <div className="mt-4 flex justify-center gap-3">
            <button
              type="button"
              onClick={() => navigate('/bids/new')}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Tạo hồ sơ
            </button>
            <button
              type="button"
              onClick={() => navigate('/bids/new')}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Nạp hồ sơ mẫu
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="mt-6 overflow-x-auto rounded-xl border border-[var(--line)] bg-[var(--surface)] shadow-sm">
            <table className="w-full min-w-[820px] text-left text-sm">
              <caption className="sr-only">Danh sách hồ sơ presales</caption>
              <thead>
                <tr className="border-b border-[var(--line)] bg-[var(--accent-soft)] text-xs uppercase tracking-wide text-[var(--muted)]">
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Tên dự án</th>
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Khách hàng</th>
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Giai đoạn deal</th>
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Trạng thái</th>
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Tổng giá</th>
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Hạn nộp</th>
                  <th className="whitespace-nowrap px-4 py-3 font-semibold">Ngày tạo</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => navigate(`/bids/${item.id}`)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        navigate(`/bids/${item.id}`);
                      }
                    }}
                    tabIndex={0}
                    role="link"
                    className="cursor-pointer border-b border-[var(--line)] last:border-b-0 hover:bg-[var(--accent-soft)] focus-visible:bg-[var(--accent-soft)]"
                  >
                    <td className="max-w-[220px] px-3 py-4 font-medium text-[var(--ink)]">
                      <p className="truncate" title={item.project_name}>{item.project_name}</p>
                      <p className="mt-1 text-xs font-normal text-[var(--muted)]">Mở hồ sơ để xem nội dung và các bước xử lý.</p>
                    </td>
                    <td className="whitespace-nowrap px-4 py-4 text-[var(--muted)]">{item.customer_name}</td>
                     <td className="whitespace-nowrap px-4 py-4 text-[var(--muted)]">{item.deal_stage ? DEAL_STAGE_LABELS[item.deal_stage] ?? 'Chưa phân loại' : 'Chưa phân loại'}</td>
                    <td className="whitespace-nowrap px-4 py-4">
                      <BidStatusBadge status={item.status} />
                    </td>
                    <td className="whitespace-nowrap px-4 py-4 tabular-nums text-[var(--muted)]">{formatPrice(item.total_price, item.total_price_currency)}</td>
                    <td className="whitespace-nowrap px-4 py-4 tabular-nums">
                      {(() => {
                        const deadline = deadlineLabel(item.submission_deadline);
                        const [dateText, ...hint] = deadline.text.split(' · ');
                        return (
                          <span className={deadline.urgent ? 'font-semibold text-[var(--danger)]' : 'text-[var(--muted)]'}>
                            <span>{dateText}</span>
                            {hint.length > 0 ? <span> · {hint.join(' · ')}</span> : null}
                          </span>
                        );
                      })()}
                    </td>
                    <td className="whitespace-nowrap px-4 py-4 text-[var(--muted)]">
                      {formatDate((item.created_at ?? item.updated_at).slice(0, 10))}
                      <span className="ml-2 rounded bg-[var(--accent-soft)] px-1.5 py-0.5 text-xs">
                        {LANGUAGE_LABELS[item.customer_language] ?? item.customer_language}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-slate-500">
              {isFetching ? 'Đang cập nhật…' : `Tổng ${data.total} hồ sơ`}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                Trước
              </button>
              <span className="text-sm tabular-nums text-slate-600">
                Trang {page} / {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                Sau
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
