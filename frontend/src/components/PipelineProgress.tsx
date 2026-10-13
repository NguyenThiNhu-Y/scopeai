import type { StepState, StepStatus } from '../api/types';
import StepBadge from './StepBadge';

const STEP_LABELS: Record<string, string> = {
  intake: 'Trích xuất yêu cầu',
  gap: 'Câu hỏi làm rõ',
  solution: 'Hướng giải pháp',
  evaluate: 'Khả thi & rủi ro',
  architecture: 'Kiến trúc & effort',
  wbs: 'WBS & timeline',
  coverage: 'Đáp ứng yêu cầu',
  proposal: 'Proposal',
  ja_check: 'Kiểm tra bản tiếng Nhật',
};

interface PipelineProgressProps {
  /** Trạng thái các bước (từ GET /api/bids/{id} + SSE). */
  steps: StepState[];
  /** Thông báo lỗi (từ SSE event `error` hoặc error_message bước failed). */
  errorMessage?: string | null;
  /** Bấm "Chạy lại" → rerun pipeline từ bước lỗi (FR-023). */
  onRetry?: () => void;
  retrying?: boolean;
}

/**
 * Chỉ hiển thị các bước hệ thống thực sự trả về, tránh tạo trạng thái giả.
 */
export default function PipelineProgress({
  steps,
  errorMessage,
  onRetry,
  retrying,
}: PipelineProgressProps) {
  const failedStep = steps.find((s) => s.status === 'failed');
  const errorText = errorMessage ?? failedStep?.error_message ?? null;

  return (
    <section
      className="border-b border-[var(--line)] py-3"
      aria-label="Tiến độ phân tích"
    >
      <ul className="flex flex-wrap gap-1" aria-label="Các bước phân tích">
        {steps.map((step, index) => {
          const status = step.status as StepStatus;
          return (
            <li
              key={step.step_key}
              className="flex items-center gap-1 px-2 py-1 text-xs"
            >
              {index > 0 && <span className="text-slate-300" aria-hidden="true">—</span>}
              <span className={status === 'pending' ? 'text-slate-400' : 'font-medium text-slate-700'}>
                {STEP_LABELS[step.step_key] ?? step.step_key}
              </span>
              <StepBadge status={status} />
            </li>
          );
        })}
      </ul>

      {errorText && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <p className="text-sm font-medium text-red-700">{errorText}</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              disabled={retrying}
              className="mt-2 inline-flex items-center gap-1.5 rounded-md border border-red-300 bg-white px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
            >
              {retrying ? 'Đang chạy lại…' : 'Chạy lại'}
            </button>
          )}
        </div>
      )}
    </section>
  );
}
