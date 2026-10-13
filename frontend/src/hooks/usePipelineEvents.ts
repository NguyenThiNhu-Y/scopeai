import { useEffect, useState } from 'react';
import { subscribePipelineEvents } from '../api/events';
import type { Question, StepStatus } from '../api/types';

export interface PipelineEventState {
  /** Trạng thái mới nhất từng bước pipeline (step_key → status) từ SSE. */
  steps: Record<string, StepStatus>;
  /** Câu hỏi làm rõ nhận từ event `clarify` (null khi chưa có). */
  clarifyQuestions: Question[] | null;
  /** Đã nhận event `done` (M2: intake + gap hoàn tất). */
  done: boolean;
  /** Thông báo lỗi từ event `error` (BR-02) — null khi không lỗi. */
  error: string | null;
}

const INITIAL_STATE: PipelineEventState = {
  steps: {},
  clarifyQuestions: null,
  done: false,
  error: null,
};

/**
 * Hook quản lý kết nối SSE tiến độ pipeline (spec M2 §2.1).
 *
 * - Bật khi `enabled=true` và `bidId` hợp lệ; reset state mỗi lần bật.
 * - Cập nhật `steps` theo event `step`, `clarifyQuestions` theo `clarify`,
 *   `done` theo `done`, `error` theo `error`.
 * - Tự đóng kết nối khi unmount / tắt.
 */
export function usePipelineEvents(bidId: number | undefined, enabled: boolean) {
  const [state, setState] = useState<PipelineEventState>(INITIAL_STATE);

  useEffect(() => {
    if (!bidId || !enabled) return;

    setState(INITIAL_STATE);

    const unsubscribe = subscribePipelineEvents(bidId, {
      onStep: (step, status) =>
        setState((prev) => ({
          ...prev,
          steps: { ...prev.steps, [step]: status },
        })),
      onClarify: (_round, questions) =>
        setState((prev) => ({ ...prev, clarifyQuestions: questions })),
      onError: (step, message) =>
        setState((prev) => ({
          ...prev,
          steps: { ...prev.steps, [step]: 'failed' },
          error: message,
        })),
      onDone: () => setState((prev) => ({ ...prev, done: true })),
    });

    return unsubscribe;
  }, [bidId, enabled]);

  return state;
}