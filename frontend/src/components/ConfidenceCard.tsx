import { useQuery } from '@tanstack/react-query';
import { getConfidence } from '../api/client';
import type { ConfidenceSignal, SignalStatus } from '../api/types';
import { signalStatusMeta } from '../lib/format';

const LEVEL_TONE: Record<string, string> = {
  high: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  medium: 'border-amber-200 bg-amber-50 text-amber-800',
  low: 'border-red-200 bg-red-50 text-red-800',
};

const STATUS_RANK: Record<SignalStatus, number> = { fail: 0, warn: 1, pass: 2, na: 3 };

/**
 * Chọn tối đa `max` lý do từ danh sách tín hiệu — ưu tiên fail rồi warn,
 * giữ thứ tự quan trọng như backend decide_level (§5.3). Hàm thuần, có test.
 */
export function confidenceReasons(signals: ConfidenceSignal[], max = 3): ConfidenceSignal[] {
  return signals
    .filter((signal) => signal.status === 'fail' || signal.status === 'warn')
    .sort((a, b) => STATUS_RANK[a.status] - STATUS_RANK[b.status])
    .slice(0, max);
}

/**
 * Thẻ "Độ tin cậy ước lượng" trên Tổng quan (thiet_ke_danh_gia.md §7):
 * huy hiệu Cao/Trung bình/Thấp, tối đa 3 lý do từ signals, link Xem chi tiết
 * sang tab Kế hoạch. Dữ liệu từ GET /bids/{id}/confidence — code tính, không LLM.
 */
export default function ConfidenceCard({
  bidId,
  enabled,
  onViewDetail,
}: {
  bidId: number;
  enabled: boolean;
  onViewDetail: () => void;
}) {
  const query = useQuery({
    queryKey: ['confidence', bidId],
    queryFn: () => getConfidence(bidId),
    enabled,
    retry: false,
  });

  return (
    <section className="min-h-36 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold text-[var(--ink)]">Độ tin cậy ước lượng</h2>
        {query.data && (
          <button type="button" onClick={onViewDetail} className="text-xs font-semibold text-[var(--brand)] hover:underline">
            Xem chi tiết ›
          </button>
        )}
      </div>
      <div className="mt-4">
        {query.isPending ? (
          query.fetchStatus === 'idle' ? (
            <p className="text-sm text-[var(--muted)]">Chưa có dữ liệu độ tin cậy. Chạy pipeline để hệ thống tự đánh giá.</p>
          ) : (
            <p role="status" className="text-sm text-[var(--muted)]">Đang tải độ tin cậy…</p>
          )
        ) : query.isError || !query.data ? (
          <p className="text-sm text-[var(--muted)]">Chưa có dữ liệu độ tin cậy. Chạy pipeline để hệ thống tự đánh giá.</p>
        ) : (
          <>
            <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${LEVEL_TONE[query.data.level] ?? 'border-slate-200 bg-slate-50 text-slate-700'}`}>
              {query.data.level_label_vi}
            </span>
            {(() => {
              const reasons = confidenceReasons(query.data.signals);
              if (reasons.length === 0) {
                return <p className="mt-3 text-sm leading-6 text-[var(--muted)]">{query.data.summary_vi}</p>;
              }
              return (
                <ul className="mt-3 space-y-2">
                  {reasons.map((signal) => {
                    const meta = signalStatusMeta(signal.status);
                    return (
                      <li key={signal.key} className="flex gap-2 text-sm leading-6 text-[var(--muted)]">
                        <span className="mt-0.5 shrink-0 font-semibold" aria-hidden="true">{meta.icon}</span>
                        <span>
                          <strong className="font-semibold text-[var(--ink)]">{signal.label_vi}:</strong> {signal.detail_vi || 'Chưa có thông tin chi tiết.'}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              );
            })()}
          </>
        )}
      </div>
    </section>
  );
}