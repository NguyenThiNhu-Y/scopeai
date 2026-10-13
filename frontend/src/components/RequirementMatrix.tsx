import { useMemo, useState } from 'react';
import { downloadExport } from '../api/client';
import type { EvaluationsResponse, Requirement } from '../api/types';
import { SOLUTION_LABELS } from '../lib/format';

type FilterKey = 'all' | '○' | '△' | '×' | 'clarify';

const ratingStyles: Record<string, string> = {
  '◎': 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  '○': 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  '△': 'bg-amber-50 text-amber-700 ring-amber-200',
  '×': 'bg-rose-50 text-rose-700 ring-rose-200',
};

function RatingBadge({ item }: { item: Requirement }) {
  const label = item.needs_clarification || !item.rating ? 'Cần làm rõ' : item.rating;
  const className = item.needs_clarification || !item.rating
    ? 'bg-sky-50 text-sky-700 ring-sky-200'
    : ratingStyles[item.rating] ?? 'bg-slate-50 text-slate-700 ring-slate-200';

  return (
    <span className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-bold ring-1 ${className}`}>
      {label}
    </span>
  );
}

/** Nhãn cột "Thành phần": nhãn tiếng Việt theo hướng giải pháp, "—" khi none/chưa rõ. */
function componentLabel(item: Requirement): string {
  if (item.solution_direction) {
    if (item.solution_direction === 'none') return '—';
    return SOLUTION_LABELS[item.solution_direction] ?? '—';
  }
  return item.category || '—';
}

export default function RequirementMatrix({ data, bidId }: { data: EvaluationsResponse; bidId?: number }) {
  const items = data.items as Requirement[];
  const [filter, setFilter] = useState<FilterKey>('all');
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const counts = useMemo(() => ({
    all: items.length,
    '○': items.filter((item) => item.rating === '○' || item.rating === '◎').length,
    '△': items.filter((item) => item.rating === '△').length,
    '×': items.filter((item) => item.rating === '×').length,
    clarify: items.filter((item) => item.needs_clarification || !item.rating).length,
  }), [items]);

  const visible = useMemo(() => {
    if (filter === 'all') return items;
    if (filter === 'clarify') return items.filter((item) => item.needs_clarification || !item.rating);
    if (filter === '○') return items.filter((item) => item.rating === '○' || item.rating === '◎');
    return items.filter((item) => item.rating === filter);
  }, [filter, items]);

  async function exportRequirements() {
    if (!bidId || exporting) return;
    setExporting(true);
    setExportError(null);
    try {
      const file = await downloadExport(bidId, 'requirements');
      const link = document.createElement('a');
      link.href = URL.createObjectURL(file.blob);
      link.download = file.filename;
      link.click();
      // Keep the object URL alive until the browser has started the download.
      window.setTimeout(() => URL.revokeObjectURL(link.href), 0);
    } catch {
      setExportError('Không tải được bảng đáp ứng. Vui lòng thử lại.');
    } finally {
      setExporting(false);
    }
  }

  if (!items.length) {
    return (
      <section className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center" aria-label="Đáp ứng yêu cầu">
        <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-[var(--brand-soft)] text-xl text-[var(--brand)]">○</div>
        <h2 className="mt-3 font-semibold text-[var(--ink)]">Chưa có bảng đáp ứng</h2>
        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--muted)]">
          Hãy đính kèm file Excel requirement trong tab Yêu cầu &amp; câu hỏi, sau đó chạy lại bước đọc file để hệ thống đánh giá từng mục.
        </p>
      </section>
    );
  }

  const filters: Array<[FilterKey, string]> = [
    ['all', 'Tất cả'],
    ['○', 'Đạt'],
    ['△', 'Một phần'],
    ['×', 'Không đạt'],
    ['clarify', 'Cần làm rõ'],
  ];

  return (
    <section
      className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5"
      aria-label="Ma trận đáp ứng"
      aria-busy={exporting}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--muted)]">Đánh giá theo requirement</p>
          <h2 className="mt-1 font-semibold text-[var(--ink)]">Đáp ứng yêu cầu</h2>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <label className="flex items-center gap-2 text-xs text-[var(--muted)]">
            <span>Ngôn ngữ ghi chú</span>
            <select
              value="customer"
              disabled
              className="rounded-lg border border-[var(--line)] bg-slate-100 px-2 py-2 text-xs text-[var(--muted)] disabled:cursor-not-allowed"
              aria-label="Ngôn ngữ ghi chú trong file Excel"
              title="Ngôn ngữ hiển thị theo hồ sơ khách"
            >
              <option value="customer">Theo ngôn ngữ khách</option>
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
              <option value="ja">日本語</option>
            </select>
            <span className="sr-only">Đang dùng ngôn ngữ khách theo hồ sơ</span>
          </label>
          <button
            type="button"
            onClick={exportRequirements}
            disabled={!bidId || exporting}
            aria-label="Tải bảng đáp ứng dạng Excel"
            className="rounded-lg border border-[var(--brand)] px-3 py-2 text-xs font-semibold text-[var(--brand)] transition hover:bg-[var(--brand-soft)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {exporting ? 'Đang tạo file…' : 'Tải bảng đáp ứng'}
          </button>
          <button
            type="button"
            onClick={exportRequirements}
            disabled={!bidId || exporting}
            aria-label="Điền ○/△/× vào file Excel của khách"
            className="rounded-lg bg-[var(--brand)] px-3 py-2 text-xs font-semibold text-white transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {exporting ? 'Đang tạo file…' : 'Điền ○/△/× vào file Excel của khách'}
          </button>
        </div>
      </div>

      {exporting && <p className="mt-3 text-sm text-[var(--muted)]" role="status" aria-live="polite">Đang tạo file Excel…</p>}
      {exportError && <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700" role="alert">{exportError}</p>}

      <div className="mt-5 flex flex-wrap gap-2" aria-label="Bộ lọc đánh giá">
        {filters.map(([key, label]) => (
          <button
            key={key}
            type="button"
            aria-pressed={filter === key}
            onClick={() => setFilter(key)}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${filter === key ? 'bg-[var(--brand)] text-white shadow-sm' : 'bg-[var(--brand-soft)] text-[var(--brand)] hover:bg-slate-100'}`}
          >
            {label} <span className="ml-1 opacity-75">{counts[key]}</span>
          </button>
        ))}
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <caption className="sr-only">Bảng đánh giá mức độ đáp ứng từng yêu cầu</caption>
          <thead className="border-b border-[var(--line)] text-xs uppercase tracking-wide text-[var(--muted)]">
            <tr>
              <th scope="col" className="w-32 px-3 py-2">Mã</th>
              <th scope="col" className="min-w-[300px] px-3 py-2">Nội dung yêu cầu</th>
              <th scope="col" className="w-32 px-3 py-2">Đánh giá</th>
              <th scope="col" className="w-40 px-3 py-2">Thành phần</th>
              <th scope="col" className="min-w-[220px] px-3 py-2">Ghi chú</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((item) => (
              <tr key={item.req_code} className="border-b border-[var(--line)] align-top last:border-0 hover:bg-slate-50/70">
                <td className="whitespace-nowrap px-3 py-3 font-mono text-xs text-[var(--muted)]">{item.req_code}</td>
                <td className="px-3 py-3 leading-6 text-[var(--ink)]">{item.content}</td>
                <td className="px-3 py-3"><RatingBadge item={item} /></td>
                <td className="px-3 py-3 text-[var(--muted)]">{componentLabel(item)}</td>
                <td className="px-3 py-3 leading-6 text-[var(--muted)]">{item.note_vi || 'Chưa có ghi chú'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!visible.length && <p className="py-8 text-center text-sm text-[var(--muted)]">Không có requirement thuộc bộ lọc này.</p>}
      </div>
    </section>
  );
}
