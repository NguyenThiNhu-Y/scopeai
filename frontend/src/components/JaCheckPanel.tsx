import type { JaCheckResult } from '../api/types';

export default function JaCheckPanel({ result }: { result: JaCheckResult | null }) {
  if (!result) return null;
  const warning = result.result === 'warning';
  return (
    <section
      aria-label="Kiểm tra tiếng Nhật"
      className={`rounded-lg border p-4 ${warning ? 'border-amber-200 bg-amber-50' : 'border-emerald-200 bg-emerald-50'}`}
    >
      <div className="flex items-start gap-3">
        <span aria-hidden="true" className={`mt-0.5 text-lg ${warning ? 'text-amber-700' : 'text-emerald-700'}`}>{warning ? '!' : '✓'}</span>
        <div className="min-w-0">
          <h2 className={`text-sm font-semibold ${warning ? 'text-amber-900' : 'text-emerald-900'}`}>
            {warning ? 'Cảnh báo kiểm tra tiếng Nhật' : 'Kiểm tra tiếng Nhật đạt'}
          </h2>
          <p className="mt-1 text-xs text-slate-700">
            {warning ? 'Bạn vẫn có thể tải hồ sơ. Hãy xem lại các điểm cần chú ý bên dưới.' : 'Không phát hiện vấn đề theo bộ kiểm tra hiện tại.'}
          </p>
          {warning && (
            <ul className="mt-3 space-y-3" aria-label="Danh sách cảnh báo">
              {result.issues.map((issue, index) => (
                <li key={`${issue.section}-${index}`} className="border-t border-amber-200 pt-2 text-sm text-amber-950">
                  <p className="font-medium">{issue.message_vi}</p>
                  <p className="mt-1 text-xs text-amber-900">Gợi ý: {issue.suggestion_ja}</p>
                  <p className="mt-1 text-[11px] text-amber-800">Mục: {issue.section} · Nguồn: {issue.source}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
