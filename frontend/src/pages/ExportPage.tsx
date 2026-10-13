import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError, downloadExport } from '../api/client';
import type { ExportKind, JaCheckResult } from '../api/types';
import ExportButtons from '../components/ExportButtons';
import JaCheckPanel from '../components/JaCheckPanel';

export default function ExportPage() {
  const { id } = useParams<{ id: string }>();
  const bidId = Number(id);
  const navigate = useNavigate();
  const [downloading, setDownloading] = useState<ExportKind | null>(null);
  const [jaCheck, setJaCheck] = useState<JaCheckResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleDownload(kind: ExportKind) {
    setDownloading(kind); setError(null); setSuccess(null);
    try {
      const file = await downloadExport(bidId, kind);
      setJaCheck(file.jaCheck);
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a'); link.href = url; link.download = file.filename; link.click();
      URL.revokeObjectURL(url);
      setSuccess(`Đã tải ${file.filename}.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Không xuất được file. Vui lòng thử lại.');
    } finally { setDownloading(null); }
  }

  if (!Number.isFinite(bidId)) return <Message text="Mã hồ sơ không hợp lệ." error />;
  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <button type="button" onClick={() => navigate(`/bids/${bidId}`)} className="text-sm font-medium text-blue-700 hover:text-blue-800">← Hồ sơ</button>
      <p className="mt-6 text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">M7 · Xuất hồ sơ</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Tải bộ hồ sơ</h1>
      <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600">File được tạo từ dữ liệu đã duyệt. Tên file và nội dung được giữ ổn định; màn hình này không tự tính số liệu.</p>
      <div className="mt-6 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-900"><strong>Lưu ý cổng giá:</strong> nếu chưa duyệt giá, tài liệu sẽ dùng placeholder <code>[Presales điền]</code>.</div>
      <div className="mt-6"><ExportButtons downloading={downloading} onDownload={handleDownload} /></div>
      <div className="mt-5 space-y-3" aria-live="polite">
        {downloading && <p role="status" className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">Đang tạo file và bắt đầu tải xuống…</p>}
        {success && <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{success}</p>}
        {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800"><p>{error}</p><button type="button" onClick={() => setError(null)} className="mt-2 font-semibold underline">Đóng thông báo</button></div>}
        <JaCheckPanel result={jaCheck} />
      </div>
    </div>
  );
}

function Message({ text, error = false }: { text: string; error?: boolean }) { return <div className="mx-auto max-w-4xl px-6 py-12"><p role={error ? 'alert' : 'status'} className={error ? 'rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700' : 'text-sm text-slate-500'}>{text}</p></div>; }
