import type { Question, QuestionImpact, StepStatus } from './types';

export interface PipelineEventHandlers {
  /** event: step — data {bid_id, step, status, attempt?} (contract §5.2). */
  onStep?: (step: string, status: StepStatus, attempt?: number) => void;
  /** event: clarify — data {bid_id, round, questions[]} (spec §2.1). */
  onClarify?: (round: number, questions: Question[]) => void;
  /** event: error — data {bid_id, step, status, message} (BR-02). */
  onError?: (step: string, message: string) => void;
  /** event: done — data {bid_id, status} (M2: intake + gap xong). */
  onDone?: (status: string) => void;
  /** event: heartbeat — server gửi mỗi 15s để giữ kết nối. */
  onHeartbeat?: () => void;
}

interface StepEventData {
  bid_id: number;
  step: string;
  status: StepStatus;
  attempt?: number;
}

interface ClarifyEventData {
  bid_id: number;
  round: number;
  questions: Array<{
    id: number;
    question: string;
    reason_vi: string;
    impact: QuestionImpact;
    related_req_codes?: string[];
  }>;
}

interface ErrorEventData {
  bid_id: number;
  step: string;
  status: string;
  message: string;
}

interface DoneEventData {
  bid_id: number;
  status: string;
}

/**
 * Kết nối SSE tới GET /api/bids/{id}/pipeline/events (spec M2 §2.1).
 *
 * - EventSource tự reconnect khi mất kết nối (không cần xử lý thủ công).
 * - Parse `event:` + `data:` JSON; event sai định dạng bị bỏ qua.
 * - Trả về hàm unsubscribe để đóng kết nối khi component unmount.
 */
export function subscribePipelineEvents(
  bidId: number,
  handlers: PipelineEventHandlers,
): () => void {
  if (typeof EventSource === 'undefined') {
    // Môi trường không hỗ trợ EventSource (vd. jsdom) — no-op.
    return () => {};
  }

  const es = new EventSource(`/api/bids/${bidId}/pipeline/events`);

  es.addEventListener('step', (ev) => {
    try {
      const data = JSON.parse(ev.data) as StepEventData;
      handlers.onStep?.(data.step, data.status, data.attempt);
    } catch {
      // bỏ qua event không đúng định dạng
    }
  });

  es.addEventListener('clarify', (ev) => {
    try {
      const data = JSON.parse(ev.data) as ClarifyEventData;
      const questions: Question[] = (data.questions ?? []).map((q) => ({
        id: q.id,
        round_no: data.round,
        question: q.question,
        reason_vi: q.reason_vi,
        impact: q.impact,
        related_req_codes: q.related_req_codes ?? [],
        answer: null,
        is_assumption: false,
        status: 'awaiting_answer',
      }));
      handlers.onClarify?.(data.round, questions);
    } catch {
      // bỏ qua event không đúng định dạng
    }
  });

  es.addEventListener('error', (ev) => {
    // Lưu ý: event "error" cũng được fire khi kết nối lỗi (MessageEvent.data undefined) —
    // EventSource tự reconnect, ta bỏ qua trường hợp đó.
    const msgEv = ev as MessageEvent;
    if (!msgEv.data) return;
    try {
      const data = JSON.parse(msgEv.data) as ErrorEventData;
      handlers.onError?.(data.step, data.message);
    } catch {
      // bỏ qua event không đúng định dạng
    }
  });

  es.addEventListener('done', (ev) => {
    try {
      const data = JSON.parse(ev.data) as DoneEventData;
      handlers.onDone?.(data.status);
    } catch {
      // bỏ qua event không đúng định dạng
    }
  });

  es.addEventListener('heartbeat', () => {
    handlers.onHeartbeat?.();
  });

  return () => {
    es.close();
  };
}