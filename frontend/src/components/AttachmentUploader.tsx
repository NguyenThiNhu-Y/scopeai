import { useRef, useState } from 'react';
import type { Attachment, AttachmentFileType } from '../api/types';
import { ApiError, uploadAttachment } from '../api/client';

const MAX_FILES = 10;
const MAX_BYTES = 20 * 1024 * 1024;

const TYPE_LABELS: Record<AttachmentFileType, string> = {
  requirement: 'Excel requirement',
  rfp: 'RFP / tài liệu',
  sample_data: 'Dữ liệu mẫu',
};

const STATUS_LABELS = {
  pending: 'Chờ đọc',
  ok: 'Đã đọc',
  error: 'Đọc lỗi',
} as const;

const MAPPING_LABELS = {
  requirement: 'Đã nhận diện là requirement',
  sample_data: 'Đã nhận diện là dữ liệu mẫu',
  other: 'Chưa xác định loại sheet',
} as const;

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function AttachmentUploader({ bidId, attachments, onUploaded }: { bidId: number; attachments: Attachment[]; onUploaded: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [type, setType] = useState<AttachmentFileType>('requirement');
  async function choose(files: FileList | null) {
    if (!files) return;
    const nextErrors: string[] = [];
    let remaining = MAX_FILES - attachments.length;
    const accepted = Array.from(files).filter((file) => {
      if (remaining <= 0) { nextErrors.push(`${file.name}: đã đủ tối đa ${MAX_FILES} file.`); return false; }
      if (file.size > MAX_BYTES) { nextErrors.push(`${file.name}: vượt quá 20 MB.`); return false; }
      remaining -= 1;
      return true;
    });
    setErrors(nextErrors);
    setBusy(true);
    for (const file of accepted) {
      try { await uploadAttachment(bidId, file, type); }
      catch (error) { nextErrors.push(`${file.name}: ${error instanceof ApiError ? error.message : 'Không tải lên được.'}`); }
    }
    setErrors([...nextErrors]); setBusy(false); if (accepted.length) onUploaded();
  }
  return <section className="rounded-xl border border-slate-200 bg-white p-5" aria-label="File đính kèm">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><h2 className="font-semibold text-slate-900">File đính kèm</h2><p className="mt-1 text-xs text-slate-500">{attachments.length}/{MAX_FILES} file · tối đa 20 MB/file</p></div>
      <div className="flex items-center gap-2">
        <label className="sr-only" htmlFor="attachment-type">Loại file</label>
        <select id="attachment-type" value={type} onChange={(e) => setType(e.target.value as AttachmentFileType)} className="rounded-lg border border-slate-300 px-2 py-2 text-sm">
          <option value="requirement">Requirement</option><option value="rfp">RFP</option><option value="sample_data">Dữ liệu mẫu</option>
        </select>
        <button type="button" disabled={busy || attachments.length >= MAX_FILES} onClick={() => inputRef.current?.click()} className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50">{busy ? 'Đang tải…' : 'Chọn file'}</button>
        <input ref={inputRef} className="sr-only" type="file" multiple accept=".pdf,.docx,.txt,.md,.xlsx,.xlsm,.csv,.xls" onChange={(e) => choose(e.target.files)} />
      </div>
    </div>
    {attachments.length > 0 ? (
      <ul className="mt-4 divide-y divide-slate-100 rounded-lg border border-slate-100">
        {attachments.map((attachment) => (
          <li key={attachment.id} className="flex flex-wrap items-center justify-between gap-3 px-3 py-3 text-sm">
            <div className="min-w-0">
              <p className="truncate font-medium text-slate-800">{attachment.filename}</p>
               <p className="mt-1 text-xs text-slate-500">{TYPE_LABELS[attachment.file_type]} · {formatBytes(attachment.size_bytes)}</p>
                {attachment.detected_type && attachment.detected_type !== attachment.file_type && <p className="mt-1 text-xs text-blue-700">Hệ thống nhận diện: {TYPE_LABELS[attachment.detected_type]}</p>}
               {attachment.sheet_mappings.length > 0 && <p className="mt-1 text-xs text-slate-500">{attachment.sheet_mappings.map((mapping) => `${mapping.sheet_name}: ${MAPPING_LABELS[mapping.sheet_kind]}`).join(' · ')}</p>}
            </div>
            <span className={`shrink-0 rounded-full px-2 py-1 text-xs font-semibold ${attachment.parse_status === 'error' ? 'bg-red-50 text-red-700' : attachment.parse_status === 'ok' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
              {STATUS_LABELS[attachment.parse_status]}
            </span>
            {attachment.parse_error && <p className="basis-full text-xs text-red-600">{attachment.parse_error}</p>}
          </li>
        ))}
      </ul>
    ) : (
      <p className="mt-4 rounded-lg bg-slate-50 px-3 py-3 text-sm text-slate-500">Chưa có file. Thêm RFP hoặc Excel requirement để bắt đầu đọc dữ liệu.</p>
    )}
    {errors.length > 0 && <ul role="alert" className="mt-3 space-y-1 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{errors.map((error) => <li key={error}>{error}</li>)}</ul>}
  </section>;
}
