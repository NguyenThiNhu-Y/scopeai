import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ApiError,
  getWbs,
  rerunPipelineFromWbs,
  snapshotWbs,
  updateWbs,
} from '../api/client';
import type {
  ScheduleResponse,
  WbsSnapshotResponse,
} from '../api/types';
import CheckWarnings from '../components/CheckWarnings';
import WbsTreeTable from '../components/WbsTreeTable';
import { PHASE_LABELS, formatDate } from '../lib/format';

type PendingAction = 'snapshot' | 'rerun' | null;

/**
 * Trang WBS 3 cấp (spec M4 §4.2, FR-032/FR-041):
 * - Bảng cây sửa TRỰC TIẾP trong dòng → "Lưu thay đổi" → PUT /wbs một lần
 *   → backend tính lại tổng + lịch, không gọi AI.
 * - Tổng + CheckWarnings (cờ do backend tính) — FE chỉ render.
 * - Chụp snapshot + xem diff; "Chạy lại từ WBS" (rerun from_step='wbs', giữ evaluate/solution).
 * - Sau mỗi lần sửa: hiển thị tóm tắt lịch đã tính lại.
 */
export default function WbsPage() {
  const { id } = useParams<{ id: string }>();
  const bidId = Number(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const wbsQuery = useQuery({
    queryKey: ['wbs', bidId],
    queryFn: () => getWbs(bidId),
    enabled: Number.isFinite(bidId),
    retry: false,
  });

  const [snapshotResult, setSnapshotResult] = useState<WbsSnapshotResponse | null>(null);
  const [recalculated, setRecalculated] = useState<ScheduleResponse | null>(null);
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [reasonDraft, setReasonDraft] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  const saveMutation = useMutation({
    mutationFn: (vars: { changes: Parameters<typeof updateWbs>[1]; note?: string | null }) =>
      updateWbs(bidId, vars.changes, vars.note),
    onSuccess: (data) => {
      queryClient.setQueryData(['wbs', bidId], data);
      setRecalculated(data.recalculated?.schedule ?? null);
      setActionError(null);
    },
    onError: (error: unknown) => {
      setActionError(
        error instanceof ApiError ? error.message : 'Không lưu được thay đổi WBS.',
      );
    },
  });

  const snapshotMutation = useMutation({
    mutationFn: (reason: string) => snapshotWbs(bidId, reason),
    onSuccess: (data) => {
      setSnapshotResult(data);
      setPendingAction(null);
      setReasonDraft('');
      setActionError(null);
    },
    onError: (error: unknown) => {
      setActionError(
        error instanceof ApiError ? error.message : 'Không chụp được snapshot WBS.',
      );
    },
  });

  const rerunMutation = useMutation({
    mutationFn: (reason: string) => rerunPipelineFromWbs(bidId, reason),
    onSuccess: () => {
      navigate(`/bids/${bidId}`);
    },
    onError: (error: unknown) => {
      setActionError(
        error instanceof ApiError ? error.message : 'Không chạy lại được từ bước WBS.',
      );
    },
  });

  function confirmPendingAction() {
    const reason = reasonDraft.trim() || 'Chỉnh sửa WBS trực tiếp';
    if (pendingAction === 'snapshot') snapshotMutation.mutate(reason);
    if (pendingAction === 'rerun') rerunMutation.mutate(reason);
  }

  if (!Number.isFinite(bidId)) {
    return <ErrorState message="Mã hồ sơ không hợp lệ." onBack={() => navigate('/bids')} />;
  }

  if (wbsQuery.isPending) {
    return (
      <div className="mx-auto max-w-5xl px-5 py-12 text-sm text-slate-500" role="status">
        Đang tải WBS…
      </div>
    );
  }

  if (wbsQuery.isError || !wbsQuery.data) {
    const error = wbsQuery.error;
    const isMissing =
      error instanceof ApiError && error.code === 'STATE_CONFLICT';
    const message =
      error instanceof ApiError
        ? error.message
        : 'Không tải được WBS.';
    return (
      <div className="mx-auto max-w-5xl px-5 py-12">
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <p className="text-sm font-medium text-red-700">{message}</p>
          {isMissing && (
            <p className="mt-1 text-sm text-red-600">
              Hãy chạy pipeline để tạo WBS trước (bước "WBS & lịch trình").
            </p>
          )}
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={() => wbsQuery.refetch()}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Thử lại
            </button>
            <button
              type="button"
              onClick={() => navigate(`/bids/${bidId}`)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Về hồ sơ
            </button>
          </div>
        </div>
      </div>
    );
  }

  const wbs = wbsQuery.data;
  const isEmpty = wbs.items.length === 0;
  const busy = saveMutation.isPending || snapshotMutation.isPending || rerunMutation.isPending;

  return (
    <div className="mx-auto max-w-5xl px-5 py-8 sm:px-8">
      <button
        type="button"
        onClick={() => navigate(`/bids/${bidId}`)}
        className="text-sm font-medium text-blue-600 hover:text-blue-700"
      >
        ← Hồ sơ
      </button>

      <div className="mt-4 border-b border-slate-200 pb-5">
        <p className="text-sm font-medium text-blue-600">M4 · WBS & lịch trình</p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">WBS 3 cấp</h1>
        <p className="mt-2 text-sm text-slate-600">
          Sửa WBS trực tiếp — tổng man-day và lịch được backend tính lại bằng code, không gọi AI.
        </p>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => setPendingAction('snapshot')}
          disabled={busy || isEmpty}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          Chụp snapshot
        </button>
        <button
          type="button"
          onClick={() => setPendingAction('rerun')}
          disabled={busy || isEmpty}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          Chạy lại từ WBS
        </button>
        <button
          type="button"
          onClick={() => navigate(`/bids/${bidId}/schedule`)}
          className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100"
        >
          Master schedule
        </button>
      </div>

      {pendingAction && (
        <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50/60 p-4">
          <p className="text-sm font-semibold text-blue-900">
            {pendingAction === 'snapshot'
              ? 'Chụp snapshot WBS'
              : 'Chạy lại từ bước WBS (giữ đánh giá requirement + hướng giải pháp)'}
          </p>
          <label className="mt-2 block text-xs font-medium text-slate-600">
            Lý do (góp ý)
            <textarea
              value={reasonDraft}
              onChange={(event) => setReasonDraft(event.target.value)}
              rows={2}
              placeholder="VD: Cần tách task infra thành sub-task"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
            />
          </label>
          <div className="mt-2 flex items-center gap-3">
            <button
              type="button"
              onClick={confirmPendingAction}
              disabled={busy}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {pendingAction === 'snapshot'
                ? snapshotMutation.isPending
                  ? 'Đang chụp…'
                  : 'Xác nhận chụp'
                : rerunMutation.isPending
                  ? 'Đang chạy lại…'
                  : 'Xác nhận chạy lại'}
            </button>
            <button
              type="button"
              onClick={() => {
                setPendingAction(null);
                setReasonDraft('');
              }}
              disabled={busy}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Hủy
            </button>
          </div>
        </div>
      )}

      {actionError && (
        <p
          role="alert"
          className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {actionError}
        </p>
      )}

      {isEmpty ? (
        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
          WBS đang trống. Hãy chạy pipeline để tạo WBS hoặc bấm "＋ Thêm task" để tạo thủ công.
        </div>
      ) : (
        <>
          <section
            className="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            aria-label="Tổng man-day và kiểm tra"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-blue-600">
                  Tổng man-day (backend tính)
                </p>
                <p className="mt-1 text-2xl font-bold tabular-nums text-slate-900">
                  {wbs.totals.man_day}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(wbs.totals.by_phase).map(([phase, value]) => (
                  <span
                    key={phase}
                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700"
                  >
                    {PHASE_LABELS[phase as keyof typeof PHASE_LABELS] ?? phase}:{' '}
                    <strong className="tabular-nums">{value}</strong>
                  </span>
                ))}
              </div>
            </div>
            <div className="mt-4 border-t border-slate-100 pt-4">
              <CheckWarnings check={wbs.check} />
            </div>
          </section>

          <div className="mt-6">
            <WbsTreeTable
              items={wbs.items}
              saving={saveMutation.isPending}
              onSaveChanges={(changes, note) => saveMutation.mutate({ changes, note })}
            />
          </div>
        </>
      )}

      {recalculated && (
        <section
          className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50/60 p-5"
          aria-label="Lịch đã tính lại"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-emerald-900">
                Lịch đã tính lại sau khi sửa WBS (không gọi AI)
              </p>
              <p className="mt-1 text-sm text-emerald-800">
                Ngày kết thúc:{' '}
                <strong className="tabular-nums">{formatDate(recalculated.end_date)}</strong>
              </p>
              {recalculated.warning && (
                <p className="mt-1 text-sm text-amber-800">{recalculated.warning}</p>
              )}
            </div>
            <button
              type="button"
              onClick={() => navigate(`/bids/${bidId}/schedule`)}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
            >
              Xem master schedule
            </button>
          </div>
        </section>
      )}

      {snapshotResult && (
        <section
          className="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
          aria-label="Diff snapshot WBS"
        >
          <h2 className="text-base font-semibold text-slate-900">
            Snapshot #{snapshotResult.snapshot_id}
          </h2>
          {!snapshotResult.diff_summary ? (
            <p className="mt-2 text-sm text-slate-600">
              Đã chụp snapshot. Không có thay đổi so với WBS hiện tại.
            </p>
          ) : (
            <div className="mt-3 grid grid-cols-1 gap-4 lg:grid-cols-3">
              <DiffBlock
                title={`Đã thêm (${snapshotResult.diff_summary.added.length})`}
                tone="emerald"
                items={snapshotResult.diff_summary.added}
              />
              <DiffBlock
                title={`Đã xóa (${snapshotResult.diff_summary.removed.length})`}
                tone="red"
                items={snapshotResult.diff_summary.removed}
              />
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Đã sửa ({snapshotResult.diff_summary.modified.length})
                </p>
                <ul className="mt-2 space-y-1.5">
                  {snapshotResult.diff_summary.modified.length === 0 && (
                    <li className="text-sm text-slate-400">Không có.</li>
                  )}
                  {snapshotResult.diff_summary.modified.map((mod, index) => (
                    <li
                      key={`${mod.task_code}-${mod.field}-${index}`}
                      className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900"
                    >
                      <span className="font-mono font-semibold">{mod.task_code}</span> ·{' '}
                      {mod.field}: {String(mod.old)} → <strong>{String(mod.new)}</strong>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function DiffBlock({
  title,
  tone,
  items,
}: {
  title: string;
  tone: 'emerald' | 'red';
  items: Array<Record<string, unknown>>;
}) {
  const border = tone === 'emerald' ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50';
  const text = tone === 'emerald' ? 'text-emerald-900' : 'text-red-900';
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <ul className="mt-2 space-y-1.5">
        {items.length === 0 && <li className="text-sm text-slate-400">Không có.</li>}
        {items.map((item, index) => (
          <li key={index} className={`rounded-lg border px-3 py-2 text-xs ${border} ${text}`}>
            <span className="font-mono font-semibold">{String(item.task_code ?? item.name_vi ?? '?')}</span>
            {Boolean(item.name_vi) && Boolean(item.task_code) && (
              <span className="ml-1">· {String(item.name_vi)}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

function ErrorState({ message, onBack }: { message: string; onBack: () => void }) {
  return (
    <div className="mx-auto max-w-5xl px-5 py-12">
      <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {message}
      </div>
      <button
        type="button"
        onClick={onBack}
        className="mt-3 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700"
      >
        Về hồ sơ
      </button>
    </div>
  );
}
