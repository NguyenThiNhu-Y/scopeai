import { useHealth } from '../hooks/useHealth';
import type { HealthStatus } from '../api/types';
import { useNavigate } from 'react-router-dom';

type BadgeKind = HealthStatus | 'error';

const BADGE_STYLES: Record<BadgeKind, string> = {
  ok: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  degraded: 'bg-amber-50 text-amber-700 ring-amber-200',
  error: 'bg-red-50 text-red-700 ring-red-200',
};

const BADGE_LABELS: Record<BadgeKind, string> = {
  ok: 'Dịch vụ sẵn sàng',
  degraded: 'Dịch vụ đang bị giới hạn',
  error: 'Không kết nối được dịch vụ',
};

const BADGE_DOTS: Record<BadgeKind, string> = {
  ok: 'bg-emerald-500',
  degraded: 'bg-amber-500',
  error: 'bg-red-500',
};

function StatusBadge({ kind }: { kind: BadgeKind }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ring-1 ring-inset ${BADGE_STYLES[kind]}`}
    >
      <span className={`h-2 w-2 rounded-full ${BADGE_DOTS[kind]}`} aria-hidden="true" />
      {BADGE_LABELS[kind]}
    </span>
  );
}

export default function HomePage() {
  const navigate = useNavigate();
  const { data, isPending, isError } = useHealth();

  return (
    <div className="mx-auto max-w-5xl px-8 py-12">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--brand)]">Workspace</p>
      <h1 className="mt-3 text-3xl font-bold tracking-tight text-[var(--ink)]">Tạo hồ sơ dự thầu</h1>
      <p className="mt-2 text-[var(--muted)]">Bắt đầu từ email, RFP hoặc bộ hồ sơ mẫu của khách hàng.</p>
      <section className="mt-8 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-6 shadow-sm">
        <label className="text-sm font-semibold text-[var(--ink)]" htmlFor="request">Nội dung yêu cầu</label>
        <textarea id="request" className="mt-3 min-h-48 w-full rounded-lg border border-[var(--line)] bg-transparent p-4 text-sm outline-none focus:border-[var(--brand)]" placeholder="Dán email hoặc yêu cầu RFP của khách hàng vào đây…" />
        <div className="mt-4 flex flex-wrap gap-3">
          <button type="button" onClick={() => navigate('/bids/new')} className="rounded-lg bg-[var(--brand)] px-5 py-2.5 font-semibold text-white">Tạo hồ sơ</button>
          <button type="button" onClick={() => navigate('/bids/new')} className="rounded-lg border border-[var(--line)] px-5 py-2.5 font-semibold text-[var(--ink)]">Nạp bộ hồ sơ mẫu</button>
          <button type="button" onClick={() => navigate('/bids/new')} className="rounded-lg border border-[var(--line)] px-5 py-2.5 text-[var(--muted)]">Đính kèm file</button>
        </div>
      </section>

       <section
        className="mt-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
         aria-label="Trạng thái dịch vụ"
      >
        <div className="flex flex-wrap items-center gap-3">
          {isPending ? (
            <span className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-500 ring-1 ring-inset ring-slate-200">
              <span className="h-2 w-2 animate-pulse rounded-full bg-slate-400" aria-hidden="true" />
               Đang kiểm tra kết nối dịch vụ…
            </span>
          ) : isError ? (
            <StatusBadge kind="error" />
          ) : (
            <StatusBadge kind={data.status} />
          )}

          {data && (
            <span className="inline-flex items-center rounded-full bg-slate-100 px-3 py-1 font-mono text-sm font-medium text-slate-700 ring-1 ring-inset ring-slate-200">
              LLM: {data.llm_provider}
            </span>
          )}
        </div>

        {isError && (
          <p className="mt-4 text-sm leading-relaxed text-slate-600">
             Không nhận được phản hồi từ dịch vụ. Vui lòng thử lại sau.
          </p>
        )}

        {data && (
          <dl className="mt-5 grid grid-cols-1 gap-x-8 gap-y-3 border-t border-slate-100 pt-5 sm:grid-cols-3">
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Ứng dụng
              </dt>
              <dd className="mt-1 font-mono text-sm text-slate-700">{data.app}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Phiên bản
              </dt>
              <dd className="mt-1 font-mono text-sm text-slate-700">{data.version}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Cơ sở dữ liệu
              </dt>
              <dd className="mt-1 font-mono text-sm text-slate-700">{data.database}</dd>
            </div>
          </dl>
        )}
       </section>

      <section className="mt-8">
        <h2 className="text-sm font-semibold text-slate-900">Bắt đầu</h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          Dùng menu bên trái để điều hướng: <strong>Tạo hồ sơ</strong> để nhập yêu cầu
          mới, <strong>Hồ sơ</strong> để xem danh sách hồ sơ dự thầu,{' '}
          <strong>Cài đặt</strong> để cấu hình hệ thống.
        </p>
      </section>
    </div>
  );
}
