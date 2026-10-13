import { STEP_STATUS, type StepStatus } from '../api/types';

const STATUS_STYLES: Record<StepStatus, string> = {
  pending: 'bg-slate-50 text-slate-400 ring-slate-200',
  running: 'bg-blue-50 text-blue-700 ring-blue-200',
  completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  failed: 'bg-red-50 text-red-700 ring-red-200',
  [STEP_STATUS.clarification]: 'bg-amber-50 text-amber-700 ring-amber-200',
  skipped: 'bg-slate-100 text-slate-500 ring-slate-200',
};

const STATUS_LABELS: Record<StepStatus, string> = {
  pending: 'Chờ',
  running: 'Đang chạy',
  completed: 'Hoàn tất',
  failed: 'Lỗi',
  [STEP_STATUS.clarification]: 'Chờ làm rõ',
  skipped: 'Bỏ qua',
};

/** Badge trạng thái bước pipeline (dùng chung trong PipelineProgress). */
export default function StepBadge({ status }: { status: StepStatus }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${STATUS_STYLES[status]}`}
    >
      {status === 'running' && (
        <span
          className="h-3 w-3 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"
          aria-hidden="true"
        />
      )}
      {status === 'completed' && <span aria-hidden="true">✓</span>}
      {status === 'failed' && <span aria-hidden="true">✗</span>}
      {status === STEP_STATUS.clarification && <span aria-hidden="true">⏸</span>}
      {STATUS_LABELS[status]}
    </span>
  );
}
