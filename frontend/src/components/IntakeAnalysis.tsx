import type { IntakeOutput } from '../api/types';

const DETECTED_LANGUAGE_LABELS: Record<string, string> = {
  vi: 'Tiếng Việt',
  en: 'Tiếng Anh',
  ja: 'Tiếng Nhật',
  unknown: 'Không xác định',
};

/**
 * Kết quả phân tích B1 Intake — 7 nhóm thông tin (spec §3.1):
 * mục tiêu / người dùng / dữ liệu / ràng buộc / ngân sách / thời hạn / ngôn ngữ phát hiện.
 * Chỉ hiển thị khi backend trả `output_json` của bước intake.
 */
export default function IntakeAnalysis({ output }: { output: IntakeOutput }) {
  return (
    <section
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      aria-label="Kết quả phân tích yêu cầu"
    >
      <h2 className="text-base font-semibold text-slate-900">Kết quả phân tích yêu cầu</h2>

      <dl className="mt-4 grid grid-cols-1 gap-x-8 gap-y-4 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Mục tiêu
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">{output.objectives_vi}</dd>
        </div>

        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Người dùng
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">{output.users_vi}</dd>
        </div>

        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Dữ liệu
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">{output.data_vi}</dd>
        </div>

        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Ràng buộc
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">
            {output.constraints_vi.length > 0 ? (
              <ul className="list-disc space-y-1 pl-4">
                {output.constraints_vi.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            ) : (
              'Không đề cập'
            )}
          </dd>
        </div>

        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Ngân sách
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">
            {output.budget_mentioned ? output.budget_note_vi ?? 'Có đề cập' : 'Không đề cập'}
          </dd>
        </div>

        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Thời hạn
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">
            {output.deadline_mentioned ? output.deadline_note_vi ?? 'Có đề cập' : 'Không đề cập'}
          </dd>
        </div>

        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Ngôn ngữ phát hiện
          </dt>
          <dd className="mt-1 text-sm leading-relaxed text-slate-700">
            {DETECTED_LANGUAGE_LABELS[output.customer_language_detected] ??
              output.customer_language_detected}
          </dd>
        </div>

        {output.summary_vi && (
          <div className="sm:col-span-2">
            <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Tóm tắt
            </dt>
            <dd className="mt-1 text-sm leading-relaxed text-slate-700">{output.summary_vi}</dd>
          </div>
        )}
      </dl>
    </section>
  );
}