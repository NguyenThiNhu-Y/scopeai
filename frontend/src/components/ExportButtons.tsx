import type { ExportKind } from '../api/types';

const ACTIONS: Array<{ kind: ExportKind; label: string; detail: string }> = [
  { kind: 'docx', label: 'Proposal Word', detail: '.docx' },
  { kind: 'xlsx', label: 'Bảng tính Excel', detail: '.xlsx' },
  { kind: 'pdf', label: 'Proposal PDF', detail: '.pdf' },
  { kind: 'pptx', label: 'Slide PowerPoint', detail: '.pptx · tóm tắt thuyết trình' },
  { kind: 'bundle', label: 'Gói đầy đủ', detail: '.zip · 4 file' },
  { kind: 'requirements', label: 'Excel requirement', detail: '.xlsx · đã điền đáp ứng' },
];

export default function ExportButtons({ downloading, onDownload }: { downloading: ExportKind | null; onDownload: (kind: ExportKind) => void }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2" aria-label="Tùy chọn xuất file">
      {ACTIONS.map(({ kind, label, detail }) => {
        const active = downloading === kind;
        return (
          <button key={kind} type="button" disabled={downloading !== null} onClick={() => onDownload(kind)}
            className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3 text-left transition hover:border-blue-300 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60">
            <span><span className="block text-sm font-semibold text-slate-800">{active ? 'Đang chuẩn bị…' : label}</span><span className="mt-1 block text-xs text-slate-500">{detail}</span></span>
            <span className="text-blue-700" aria-hidden="true">↓</span>
          </button>
        );
      })}
    </div>
  );
}
