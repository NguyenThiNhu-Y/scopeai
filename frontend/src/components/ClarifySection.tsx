import { useMemo, useState } from 'react';
import { ApiError, submitAnswers } from '../api/client';
import type { AnswerItem, Question, QuestionImpact } from '../api/types';

const IMPACT_LABELS: Record<QuestionImpact, string> = {
  solution: 'Giải pháp',
  effort: 'Effort',
  price: 'Giá',
};

const IMPACT_STYLES: Record<QuestionImpact, string> = {
  solution: 'bg-blue-50 text-blue-700 ring-blue-200',
  effort: 'bg-amber-50 text-amber-700 ring-amber-200',
  price: 'bg-rose-50 text-rose-700 ring-rose-200',
};

interface ClarifySectionProps {
  bidId: number;
  questions: Question[];
  roundsUsed: number;
  maxRounds: number;
  /** Lý do hỏi vòng 2 (backend trả khi còn thông tin chặn) — hiển thị khi có vòng 2. */
  roundTwoReason?: string | null;
  /** Gọi sau khi gửi trả lời thành công — pipeline resume (FR-011.3). */
  onSubmitted: () => void;
}

/**
 * Form trả lời câu hỏi làm rõ (spec §4.2):
 * - Hiện ĐỦ MỌI câu theo từng vòng (Đợt 10 — trước đây mất câu vòng 2).
 * - Vòng đang chờ trả lời: hiện textarea; vòng khác: hiện trạng thái đã trả lời.
 * - Lý do vòng 2 (round_two_reason_vi) hiển thị khi có câu vòng 2 chờ trả lời.
 * - "Gửi trả lời" → submitAnswers → pipeline tự chạy tiếp từ bước `gap`.
 */
export default function ClarifySection({
  bidId,
  questions,
  roundsUsed,
  maxRounds,
  roundTwoReason,
  onSubmitted,
}: ClarifySectionProps) {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [assumptions, setAssumptions] = useState<Record<number, boolean>>({});
  const [missingIds, setMissingIds] = useState<number[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const unanswered = useMemo(() => questions.filter((q) => !q.answer), [questions]);
  const rounds = useMemo(() => Array.from(new Set(questions.map((q) => q.round_no))).sort((a, b) => a - b), [questions]);
  // Vòng đang chờ trả lời = vòng của câu hỏi chưa trả lời đầu tiên.
  const currentRound = unanswered[0]?.round_no ?? rounds[rounds.length - 1] ?? 1;
  const hasRoundTwo = rounds.some((roundNo) => roundNo >= 2);

  function handleSubmit() {
    const missing = unanswered
      .filter((q) => !(answers[q.id] ?? '').trim())
      .map((q) => q.id);

    if (missing.length > 0) {
      setMissingIds(missing);
      setSubmitError('Vui lòng trả lời tất cả câu hỏi trước khi gửi.');
      return;
    }

    setMissingIds([]);
    setSubmitError(null);
    setSubmitting(true);

    const items: AnswerItem[] = unanswered.map((q) => ({
      question_id: q.id,
      answer: (answers[q.id] ?? '').trim(),
      is_assumption: assumptions[q.id] ?? false,
    }));

    submitAnswers(bidId, currentRound, items)
      .then(() => {
        setAnswers({});
        setAssumptions({});
        onSubmitted();
      })
      .catch((err) => {
        setSubmitError(
          err instanceof ApiError
            ? err.message
            : 'Không gửi được câu trả lời. Vui lòng thử lại.',
        );
      })
      .finally(() => setSubmitting(false));
  }

  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      aria-label="Câu hỏi làm rõ"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-base font-semibold text-slate-900">Câu hỏi làm rõ</h2>
        <span className="text-xs font-medium text-slate-500">
          Vòng {roundsUsed}/{maxRounds}
        </span>
      </div>

      {unanswered.length === 0 && <p className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">Đã trả lời tất cả câu hỏi làm rõ.</p>}
      {hasRoundTwo && currentRound >= 2 && roundTwoReason && (
        <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          Vòng 2: {roundTwoReason}
        </p>
      )}
      {rounds.map((roundNo) => {
        const roundQuestions = questions.filter((q) => q.round_no === roundNo);
        const isActive = roundNo === currentRound && unanswered.length > 0;
        const firstQuestionIndex = questions.findIndex((q) => q.round_no === roundNo);
        return (
          <div key={roundNo} className="mt-5">
            <h3 className="text-sm font-semibold text-slate-700">
              Vòng {roundNo}
              {!isActive && roundNo < currentRound && <span className="ml-2 text-xs font-normal text-emerald-600">✓ đã hoàn tất</span>}
              {!isActive && roundNo > currentRound && <span className="ml-2 text-xs font-normal text-slate-400">chưa mở</span>}
            </h3>
            <ul className="mt-3 space-y-3">
              {roundQuestions.map((q: Question, index: number) => {
                const isMissing = missingIds.includes(q.id);
                const isAnswered = Boolean(q.answer);
                const editable = isActive && !isAnswered;
                return (
                  <li
                    key={q.id}
                    className={`rounded-lg border p-4 ${isAnswered ? 'border-slate-100 bg-slate-50/60' : isMissing ? 'border-red-300 bg-red-50/50' : 'border-slate-200'}`}
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Câu hỏi {firstQuestionIndex + index + 1}</p>
                        <p className="mt-1 text-sm font-medium text-slate-900">{q.question}</p>
                      </div>
                      <span
                        className={`inline-flex shrink-0 items-center rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ring-inset ${IMPACT_STYLES[q.impact]}`}
                      >
                        {IMPACT_LABELS[q.impact]}
                      </span>
                    </div>
                    <p className="mt-2 text-xs leading-relaxed text-slate-500"><span className="font-semibold text-slate-600">Vì sao hỏi:</span> {q.reason_vi}</p>

                    {isAnswered ? <p className="mt-1 text-xs text-slate-500">Đã trả lời{q.is_assumption ? ' (giả định)' : ''}: {q.answer}</p> : editable ? <>
                      <textarea
                        value={answers[q.id] ?? ''}
                        onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                        rows={2}
                        placeholder="Nhập câu trả lời…"
                        aria-label={`Câu trả lời cho câu hỏi ${q.id}`}
                        className={`mt-3 w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 ${isMissing ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : 'border-slate-300 focus:border-blue-500 focus:ring-blue-500/20'}`}
                      />
                      {isMissing && <p className="mt-1 text-xs font-medium text-red-600">Vui lòng trả lời câu hỏi này.</p>}
                      <label className="mt-2 flex items-center gap-2 text-xs text-slate-600">
                        <input type="checkbox" checked={assumptions[q.id] ?? false} onChange={(e) => setAssumptions((prev) => ({ ...prev, [q.id]: e.target.checked }))} className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
                        Trả lời theo giả định — cần khách xác nhận
                      </label>
                    </> : <p className="mt-1 text-xs text-slate-400">Vòng này chưa mở — hoàn tất vòng {roundNo - 1} trước.</p>}
                  </li>
                );
              })}
            </ul>
          </div>
        );
      })}

      {submitError && (
        <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {submitError}
        </p>
      )}

      {unanswered.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center justify-end gap-3">
          <p className="text-xs text-slate-500">Trả lời đủ → pipeline tự chạy tiếp.</p>
          <button type="button" onClick={handleSubmit} disabled={submitting} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
            {submitting ? 'Đang gửi…' : 'Gửi trả lời'}
          </button>
        </div>
      )}
    </section>
  );
}