import { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ApiError,
  downloadCaseStudiesTemplate,
  getEvalReportLatest,
  getSettings,
  importCaseStudies,
  updateSetting,
} from '../api/client';
import type { CaseStudyImportPreview, SettingKey } from '../api/types';
import { MARKET_LABELS, SOLUTION_LABELS, formatManDay } from '../lib/format';

/** Case study theo bảng 3.2 (thiet_ke_danh_gia.md §3.2) — payload từ GET /settings, không bịa. */
interface CaseStudy {
  id: string;
  title: string;
  industry: string;
  market: string;
  customer_language: string;
  direction: string;
  requirement_count: number;
  factors?: string[];
  year?: number | null;
  public?: boolean;
  summary: string;
  estimated_man_day?: Record<string, number>;
  actual_man_day?: Record<string, number>;
  actual_duration_weeks?: Record<string, number>;
  team_peak?: Record<string, number>;
  lessons_vi?: string[];
  tech?: string[];
  bid_outcome?: Record<string, unknown>;
  wbs_file?: string | null;
}
type Criterion = { id: string; label_vi: string; weight: number };

const SETTINGS: Array<{ key: SettingKey | 'eval_report'; label: string; eyebrow: string }> = [
  { key: 'company', label: 'Công ty', eyebrow: 'Thông tin nhận diện' },
  { key: 'templates', label: 'Template', eyebrow: 'Mẫu xuất tài liệu' },
  { key: 'standard_content', label: 'Nội dung chuẩn', eyebrow: 'Theo ngôn ngữ' },
  { key: 'case_studies', label: 'Case study', eyebrow: 'Thư viện minh họa' },
  { key: 'confidence', label: 'Ngưỡng độ tin cậy', eyebrow: 'Ngưỡng đánh giá' },
  { key: 'bid_no_bid', label: 'Tiêu chí Bid/No-bid', eyebrow: 'Điều kiện sàng lọc' },
  { key: 'eval_report', label: 'Đánh giá hệ thống', eyebrow: 'Báo cáo offline' },
];
const LANGUAGES = [['vi', 'Tiếng Việt'], ['en', 'English'], ['ja', '日本語']] as const;
const EMPTY_CRITERION: Criterion = { id: '', label_vi: '', weight: 0 };

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}
function text(value: unknown): string { return typeof value === 'string' ? value : ''; }
function settingLabel(key: SettingKey | 'eval_report'): string { return SETTINGS.find((item) => item.key === key)?.label ?? key; }

export default function SettingsPage() {
  const query = useQuery({ queryKey: ['settings'], queryFn: getSettings });
  const [selected, setSelected] = useState<SettingKey | 'eval_report'>('company');
  const [draft, setDraft] = useState<unknown>(null);
  const [language, setLanguage] = useState<'vi' | 'en' | 'ja'>('vi');
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<{ kind: 'success' | 'error'; text: string } | null>(null);
  const active = query.data?.keys.find((item) => item.key === selected);

  useEffect(() => {
    if (!active) return;
    setDraft(
      selected === 'confidence'
        ? JSON.stringify(active.payload, null, 2)
        : structuredClone(active.payload),
    );
  }, [active, selected]);
  const totalWeight = useMemo(() => Array.isArray(draft) ? 0 : ((asRecord(draft).criteria as Criterion[] | undefined) ?? []).reduce((sum, item) => sum + Number(item.weight || 0), 0), [draft]);

  function patchRecord(patch: Record<string, unknown>) { setDraft((current: unknown) => ({ ...asRecord(current), ...patch })); setNotice(null); }
  function validate(): string | null {
    if (selected !== 'bid_no_bid') return null;
    const criteria = (asRecord(draft).criteria as Criterion[] | undefined) ?? [];
    if (!criteria.length) return 'Cần ít nhất một tiêu chí Bid/No-bid.';
    if (criteria.some((item) => !text(item.id).trim() || !text(item.label_vi).trim() || !Number.isFinite(Number(item.weight)) || Number(item.weight) < 0)) return 'Mỗi tiêu chí cần có mã, tên và trọng số không âm.';
    if (Math.abs(totalWeight - 100) > 0.001) return `Tổng trọng số hiện là ${totalWeight}%. Tổng phải đúng 100%.`;
    return null;
  }
  async function save() {
    const error = validate();
    if (error) { setNotice({ kind: 'error', text: error }); return; }
    setSaving(true); setNotice(null);
    try {
      // Ngưỡng độ tin cậy: textarea giữ nguyên nội dung YAML (JSON hợp lệ là YAML hợp lệ).
      const content = selected === 'confidence' && typeof draft === 'string'
        ? draft
        : JSON.stringify(draft, null, 2);
      const result = await updateSetting(selected as SettingKey, content, 'manager_web');
      setNotice({ kind: 'success', text: `Đã lưu ${settingLabel(selected)} · phiên bản ${result.version}.` });
      await query.refetch();
    } catch (error) { setNotice({ kind: 'error', text: error instanceof ApiError ? error.message : 'Không lưu được cài đặt.' }); }
    finally { setSaving(false); }
  }

  return <div className="mx-auto max-w-6xl px-6 py-10 lg:px-10">
    <header className="mb-8 border-b border-[var(--line)] pb-7">
      <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--brand)]">Workspace / quản trị</p>
      <h1 className="text-4xl font-semibold tracking-tight text-[var(--ink)]">Cài đặt</h1>
      <p className="mt-2 max-w-2xl text-sm text-[var(--muted)]">Các giá trị dưới đây được dùng khi tạo hồ sơ mới. Chỉ dữ liệu đã có trong hệ thống được hiển thị và lưu lại.</p>
    </header>
    {query.isPending && <p role="status" className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 text-sm text-[var(--muted)]">Đang tải cài đặt…</p>}
    {query.isError && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800">Không tải được cài đặt. <button className="font-semibold underline" onClick={() => query.refetch()}>Thử lại</button></div>}
    {query.data && <div className="grid gap-6 lg:grid-cols-[230px_1fr]">
      <nav aria-label="Các nhóm cài đặt" className="flex gap-2 overflow-x-auto lg:block lg:space-y-2">
        {SETTINGS.map((item) => <button key={item.key} type="button" onClick={() => { setSelected(item.key); setNotice(null); }} className={`w-max rounded-lg px-4 py-3 text-left text-sm transition lg:block lg:w-full ${selected === item.key ? 'bg-[var(--brand)] font-semibold text-white shadow-sm' : 'text-[var(--muted)] hover:bg-[var(--brand-soft)] hover:text-[var(--ink)]'}`}><span className="block">{item.label}</span><span className={`mt-1 block text-xs ${selected === item.key ? 'text-white/70' : 'text-[var(--muted)]'}`}>{item.eyebrow}</span></button>)}
      </nav>
      <section className="min-w-0 rounded-2xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm sm:p-7">
        <div className="mb-7 flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--brand)]">{selected === 'eval_report' ? 'Báo cáo mới nhất' : active?.source === 'db' ? `Đã chỉnh sửa · v${active.version}` : 'Giá trị mặc định'}</p><h2 className="mt-2 text-2xl font-semibold text-[var(--ink)]">{settingLabel(selected)}</h2></div>{selected !== 'eval_report' && <button type="button" onClick={save} disabled={saving || !active} className="rounded-lg bg-[var(--brand)] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50">{saving ? 'Đang lưu…' : 'Lưu thay đổi'}</button>}</div>
        {draft !== null && selected === 'company' && <CompanyEditor value={asRecord(draft)} onChange={patchRecord} />}
        {draft !== null && selected === 'templates' && <TemplatesEditor value={asRecord(draft)} onChange={patchRecord} />}
        {draft !== null && selected === 'standard_content' && <ContentEditor value={asRecord(draft)} language={language} onLanguageChange={setLanguage} onChange={patchRecord} />}
        {draft !== null && selected === 'case_studies' && <CaseStudiesEditor value={Array.isArray(draft) ? draft as CaseStudy[] : []} onChange={setDraft} onImported={() => void query.refetch()} />}
        {draft !== null && selected === 'confidence' && <ConfidenceEditor value={typeof draft === 'string' ? draft : ''} onChange={setDraft} />}
        {selected === 'eval_report' && <EvalReportPanel />}
        {draft !== null && selected === 'bid_no_bid' && <CriteriaEditor value={(asRecord(draft).criteria as Criterion[] | undefined) ?? []} total={totalWeight} onChange={(criteria) => patchRecord({ criteria })} />}
        {notice && <p role={notice.kind === 'error' ? 'alert' : 'status'} className={`mt-6 rounded-lg border px-4 py-3 text-sm ${notice.kind === 'error' ? 'border-red-200 bg-red-50 text-red-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800'}`}>{notice.text}</p>}
      </section>
    </div>}
  </div>;
}

function Field({ label, value, onChange, multiline = false }: { label: string; value: string; onChange: (value: string) => void; multiline?: boolean }) {
  const className = "mt-2 w-full rounded-lg border border-[var(--line)] bg-[var(--page)] px-3 py-2.5 text-sm text-[var(--ink)] outline-none transition focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand)]/20";
  return <label className="block text-sm font-medium text-[var(--ink)]">{label}{multiline ? <textarea rows={4} className={className} value={value} onChange={(event) => onChange(event.target.value)} /> : <input className={className} value={value} onChange={(event) => onChange(event.target.value)} />}</label>;
}
function CompanyEditor({ value, onChange }: { value: Record<string, unknown>; onChange: (patch: Record<string, unknown>) => void }) { return <div className="grid gap-5 sm:grid-cols-2"><Field label="Tên công ty" value={text(value.company_name)} onChange={(company_name) => onChange({ company_name })} /><Field label="Quy tắc đặt tên file" value={text(value.filename_rule)} onChange={(filename_rule) => onChange({ filename_rule })} /></div>; }
function TemplatesEditor({ value, onChange }: { value: Record<string, unknown>; onChange: (patch: Record<string, unknown>) => void }) { return <div className="space-y-4">{(['word', 'excel', 'powerpoint'] as const).map((kind) => { const item = asRecord(value[kind]); return <div key={kind} className="grid gap-4 rounded-xl border border-[var(--line)] p-4 sm:grid-cols-[120px_1fr_1fr_auto] sm:items-end"><h3 className="font-semibold text-[var(--ink)]">{kind === 'word' ? 'Word' : kind === 'excel' ? 'Excel' : 'PowerPoint'}</h3><Field label="Mẫu có sẵn" value={text(item.filename)} onChange={(filename) => onChange({ [kind]: { ...item, filename } })} /><Field label="Nguồn" value={text(item.source)} onChange={(source) => onChange({ [kind]: { ...item, source } })} /><label className="flex items-center gap-2 pb-3 text-sm text-[var(--ink)]"><input type="checkbox" checked={item.valid === true} onChange={(event) => onChange({ [kind]: { ...item, valid: event.target.checked } })} /> Hợp lệ</label></div>; })}<p className="text-xs text-[var(--muted)]">Trạng thái hợp lệ được backend kiểm tra khi lưu.</p></div>; }
function ContentEditor({ value, language, onLanguageChange, onChange }: { value: Record<string, unknown>; language: 'vi' | 'en' | 'ja'; onLanguageChange: (value: 'vi' | 'en' | 'ja') => void; onChange: (patch: Record<string, unknown>) => void }) { const content = asRecord(value[language]); return <div><div className="mb-5 flex gap-2" role="tablist" aria-label="Ngôn ngữ nội dung">{LANGUAGES.map(([code, label]) => <button key={code} type="button" role="tab" aria-selected={language === code} onClick={() => onLanguageChange(code)} className={`rounded-full px-3 py-1.5 text-sm ${language === code ? 'bg-[var(--brand)] text-white' : 'bg-[var(--page)] text-[var(--muted)]'}`}>{label}</button>)}</div><div className="grid gap-5"><Field label="Giới thiệu công ty" multiline value={text(content.company_intro)} onChange={(company_intro) => onChange({ [language]: { ...content, company_intro } })} /><Field label="Bảo mật" multiline value={text(content.security)} onChange={(security) => onChange({ [language]: { ...content, security } })} /><Field label="Điều khoản" multiline value={text(content.terms)} onChange={(terms) => onChange({ [language]: { ...content, terms } })} /></div></div>; }
const INPUT = 'mt-2 w-full rounded-lg border border-[var(--line)] bg-[var(--page)] px-3 py-2.5 text-sm text-[var(--ink)] outline-none transition focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand)]/20';

const MARKET_OPTIONS: Array<[string, string]> = [['jp', 'Nhật Bản'], ['vn', 'Việt Nam'], ['other', 'Khác']];
const LANGUAGE_OPTIONS: Array<[string, string]> = [['ja', 'Tiếng Nhật'], ['vi', 'Tiếng Việt'], ['en', 'Tiếng Anh']];

function actualTotal(item: CaseStudy): string {
  const amd = asRecord(item.actual_man_day);
  const total = Object.values(amd).reduce((sum: number, v) => sum + (typeof v === 'number' ? v : Number(v || 0)), 0);
  return total > 0 ? formatManDay(total) : '—';
}

/** Bảng danh sách + form sửa đủ trường §3.2 + tải file mẫu + nhập từ file (thiet_ke_danh_gia.md §7). */
function CaseStudiesEditor({ value, onChange, onImported }: { value: CaseStudy[]; onChange: (value: unknown) => void; onImported: () => void }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [importState, setImportState] = useState<{ file: File; preview: CaseStudyImportPreview } | null>(null);
  const [importing, setImporting] = useState(false);
  const [importSaving, setImportSaving] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importNotice, setImportNotice] = useState<string | null>(null);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selected = value.find((item) => item.id === selectedId) ?? null;

  const byDirection = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const item of value) counts[item.direction] = (counts[item.direction] ?? 0) + 1;
    return counts;
  }, [value]);

  function updateCase(updated: CaseStudy) {
    onChange(value.map((item) => (item.id === updated.id ? updated : item)));
  }

  async function handleTemplateDownload() {
    setDownloadingTemplate(true); setImportError(null);
    try {
      const file = await downloadCaseStudiesTemplate();
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a'); link.href = url; link.download = file.filename; link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setImportError(err instanceof ApiError ? err.message : 'Không tải được file mẫu.');
    } finally { setDownloadingTemplate(false); }
  }

  async function handleFilePick(file: File) {
    setImporting(true); setImportError(null); setImportNotice(null);
    try {
      const result = await importCaseStudies(file, 'preview');
      if (result.mode !== 'preview') return;
      setImportState({ file, preview: result });
    } catch (err) {
      setImportError(err instanceof ApiError ? err.message : 'Không đọc được file.');
    } finally { setImporting(false); }
  }

  async function handleImportSave() {
    if (!importState) return;
    setImportSaving(true); setImportError(null);
    try {
      const result = await importCaseStudies(importState.file, 'save');
      if (result.mode === 'save') {
        setImportNotice(
          result.error_count > 0
            ? `Đã nhập ${result.saved} case · phiên bản ${result.version} · ${result.error_count} dòng lỗi bị bỏ qua.`
            : `Đã nhập ${result.saved} case · phiên bản ${result.version}.`,
        );
      }
      setImportState(null);
      onImported();
    } catch (err) {
      setImportError(err instanceof ApiError ? err.message : 'Không lưu được file.');
    } finally { setImportSaving(false); }
  }

  if (selected) {
    return (
      <div className="space-y-5">
        <button type="button" onClick={() => setSelectedId(null)} className="text-sm font-semibold text-[var(--brand)]">← Về danh sách case</button>
        <CaseStudyForm value={selected} onChange={updateCase} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-[var(--line)] p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">Số case theo hướng giải pháp</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {Object.entries(SOLUTION_LABELS).map(([direction, label]) => (
            <span key={direction} className="rounded-full border border-[var(--line)] bg-[var(--page)] px-3 py-1 text-sm text-[var(--ink)]">{label}: <strong className="tabular-nums">{byDirection[direction] ?? 0}</strong></span>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[var(--line)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-[var(--page)] text-xs uppercase tracking-wide text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2">Tên</th>
              <th className="px-3 py-2">Hướng</th>
              <th className="px-3 py-2">Thị trường</th>
              <th className="px-3 py-2">Req</th>
              <th className="px-3 py-2">Tổng thực tế</th>
              <th className="px-3 py-2">Công khai</th>
              <th className="px-3 py-2">Sửa</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--line)]">
            {value.map((item) => (
              <tr key={item.id}>
                <td className="px-3 py-2">{item.title}</td>
                <td className="px-3 py-2">{SOLUTION_LABELS[item.direction] ?? item.direction}</td>
                <td className="px-3 py-2">{MARKET_LABELS[item.market] ?? item.market}</td>
                <td className="px-3 py-2 tabular-nums">{item.requirement_count}</td>
                <td className="px-3 py-2 tabular-nums">{actualTotal(item)}</td>
                <td className="px-3 py-2">{item.public !== false ? 'Có' : 'Không'}</td>
                <td className="px-3 py-2"><button type="button" onClick={() => setSelectedId(item.id)} className="font-semibold text-[var(--brand)]">Sửa</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button type="button" onClick={() => void handleTemplateDownload()} disabled={downloadingTemplate} className="rounded-lg border border-[var(--line)] bg-[var(--page)] px-4 py-2 text-sm font-semibold text-[var(--ink)] disabled:opacity-50">{downloadingTemplate ? 'Đang tải…' : 'Tải file mẫu'}</button>
        <button type="button" onClick={() => fileInputRef.current?.click()} disabled={importing} className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{importing ? 'Đang đọc…' : 'Nhập từ file'}</button>
        <input ref={fileInputRef} type="file" accept=".xlsx,.csv,.yaml,.yml" aria-label="Chọn file case study" className="hidden" onChange={(event) => { const file = event.target.files?.[0]; if (file) void handleFilePick(file); event.target.value = ''; }} />
      </div>

      {importState && (
        <div className="rounded-xl border border-[var(--line)] p-4">
          <p className="text-sm font-semibold text-[var(--ink)]">Xem trước: {importState.preview.valid_count} dòng hợp lệ · {importState.preview.error_count} lỗi (tổng {importState.preview.total} dòng)</p>
          {importState.preview.errors.length > 0 && (
            <ul className="mt-3 space-y-1 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
              {importState.preview.errors.map((error, index) => <li key={index}>{error}</li>)}
            </ul>
          )}
          {importState.preview.valid.length > 0 && (
            <ul className="mt-3 space-y-1 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
              {importState.preview.valid.map((item) => <li key={String(item.id)}>{String(item.title ?? item.id)}</li>)}
            </ul>
          )}
          <div className="mt-3 flex gap-2">
            <button type="button" onClick={() => void handleImportSave()} disabled={importSaving || importState.preview.valid_count === 0} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{importSaving ? 'Đang lưu…' : 'Lưu'}</button>
            <button type="button" onClick={() => setImportState(null)} className="rounded-lg border border-[var(--line)] px-4 py-2 text-sm font-semibold text-[var(--muted)]">Hủy</button>
          </div>
        </div>
      )}
      {importNotice && <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{importNotice}</p>}
      {importError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{importError}</p>}
    </div>
  );
}

function SelectField({ label, value, options, onChange }: { label: string; value: string; options: Array<[string, string]>; onChange: (value: string) => void }) {
  return (
    <label className="block text-sm font-medium text-[var(--ink)]">{label}<select value={value} onChange={(event) => onChange(event.target.value)} className={INPUT}><option value="">— Chọn —</option>{options.map(([optionValue, optionLabel]) => <option key={optionValue} value={optionValue}>{optionLabel}</option>)}</select></label>
  );
}

function NumMapEditor({ label, value, keys, onChange }: { label: string; value: Record<string, number> | undefined; keys: string[]; onChange: (next: Record<string, number>) => void }) {
  const current = value ?? {};
  return (
    <fieldset className="rounded-xl border border-[var(--line)] p-4">
      <legend className="px-1 text-sm font-medium text-[var(--ink)]">{label}</legend>
      <div className="grid gap-3 sm:grid-cols-3">
        {keys.map((key) => (
          <label key={key} className="block text-xs font-medium text-[var(--muted)]">{key}<input type="number" min="0" step="0.5" className={INPUT} value={current[key] ?? ''} onChange={(event) => onChange({ ...current, [key]: event.target.value === '' ? 0 : Number(event.target.value) })} /></label>
        ))}
      </div>
    </fieldset>
  );
}

function ListField({ label, value, onChange }: { label: string; value: string[]; onChange: (next: string[]) => void }) {
  return <Field label={label} value={value.join(', ')} onChange={(raw) => onChange(raw.split(',').map((item) => item.trim()).filter(Boolean))} />;
}

function BidOutcomeEditor({ value, onChange }: { value: Record<string, unknown> | undefined; onChange: (next: Record<string, unknown>) => void }) {
  const current = asRecord(value);
  const contract = asRecord(current.contract_model);
  return (
    <fieldset className="rounded-xl border border-[var(--line)] p-4">
      <legend className="px-1 text-sm font-medium text-[var(--ink)]">Kết quả chào thầu</legend>
      <div className="grid gap-4 sm:grid-cols-2">
        <SelectField label="Kết quả" value={text(current.result)} options={[['won', 'Thắng'], ['lost', 'Thua']]} onChange={(result) => onChange({ ...current, result })} />
        <Field label="Tháng chào thầu" value={text(current.bid_month)} onChange={(bid_month) => onChange({ ...current, bid_month })} />
        <Field label="Lý do thắng" multiline value={text(current.win_reason_vi)} onChange={(win_reason_vi) => onChange({ ...current, win_reason_vi })} />
        <Field label="Lý do thua" multiline value={text(current.lost_reason_vi)} onChange={(lost_reason_vi) => onChange({ ...current, lost_reason_vi })} />
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {['poc', 'mvp', 'production'].map((phase) => (
          <Field key={phase} label={`Hợp đồng ${phase}`} value={text(contract[phase])} onChange={(contractValue) => onChange({ ...current, contract_model: { ...contract, [phase]: contractValue } })} />
        ))}
      </div>
    </fieldset>
  );
}

function CaseStudyForm({ value, onChange }: { value: CaseStudy; onChange: (next: CaseStudy) => void }) {
  const set = (patch: Partial<CaseStudy>) => onChange({ ...value, ...patch });
  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Mã case (id)" value={text(value.id)} onChange={(id) => set({ id })} />
        <Field label="Tên case" value={text(value.title)} onChange={(title) => set({ title })} />
        <Field label="Ngành" value={text(value.industry)} onChange={(industry) => set({ industry })} />
        <SelectField label="Thị trường" value={text(value.market)} options={MARKET_OPTIONS} onChange={(market) => set({ market })} />
        <SelectField label="Ngôn ngữ khách" value={text(value.customer_language)} options={LANGUAGE_OPTIONS} onChange={(customer_language) => set({ customer_language })} />
        <SelectField label="Hướng giải pháp" value={text(value.direction)} options={Object.entries(SOLUTION_LABELS)} onChange={(direction) => set({ direction })} />
        <label className="block text-sm font-medium text-[var(--ink)]">Số requirement<input type="number" min="1" className={INPUT} value={value.requirement_count ?? ''} onChange={(event) => set({ requirement_count: Number(event.target.value) })} /></label>
        <label className="block text-sm font-medium text-[var(--ink)]">Năm<input type="number" className={INPUT} value={value.year ?? ''} onChange={(event) => set({ year: event.target.value === '' ? null : Number(event.target.value) })} /></label>
      </div>
      <label className="flex items-center gap-2 text-sm font-medium text-[var(--ink)]"><input type="checkbox" checked={value.public !== false} onChange={(event) => set({ public: event.target.checked })} /> Công khai (được trích vào proposal)</label>
      <Field label="Tóm tắt" multiline value={text(value.summary)} onChange={(summary) => set({ summary })} />
      <NumMapEditor label="Ước lượng man-day" value={value.estimated_man_day} keys={['poc', 'mvp', 'production']} onChange={(estimated_man_day) => set({ estimated_man_day })} />
      <NumMapEditor label="Thực tế man-day" value={value.actual_man_day} keys={['poc', 'mvp', 'production']} onChange={(actual_man_day) => set({ actual_man_day })} />
      <NumMapEditor label="Thời gian thực tế (tuần)" value={value.actual_duration_weeks} keys={['poc', 'go_no_go', 'mvp', 'production']} onChange={(actual_duration_weeks) => set({ actual_duration_weeks })} />
      <NumMapEditor label="Team cao điểm (người)" value={value.team_peak} keys={['pm', 'ba', 'brse', 'ai_engineer', 'backend', 'frontend', 'qa', 'infra']} onChange={(team_peak) => set({ team_peak })} />
      <ListField label="Factors (phân tách bằng dấu phẩy)" value={value.factors ?? []} onChange={(factors) => set({ factors })} />
      <ListField label="Bài học (phân tách bằng dấu phẩy)" value={value.lessons_vi ?? []} onChange={(lessons_vi) => set({ lessons_vi })} />
      <ListField label="Công nghệ (phân tách bằng dấu phẩy)" value={value.tech ?? []} onChange={(tech) => set({ tech })} />
      <BidOutcomeEditor value={value.bid_outcome} onChange={(bid_outcome) => set({ bid_outcome })} />
      <Field label="File WBS (wbs_file)" value={text(value.wbs_file)} onChange={(wbs_file) => set({ wbs_file })} />
    </div>
  );
}

/** Ngưỡng độ tin cậy — textarea YAML (JSON hợp lệ cũng là YAML hợp lệ), backend validate khi lưu. */
function ConfidenceEditor({ value, onChange }: { value: string; onChange: (value: unknown) => void }) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-[var(--muted)]">Sửa ngưỡng độ tin cậy (confidence.yaml). Backend kiểm tra cấu trúc khi lưu và tạo phiên bản mới.</p>
      <textarea rows={18} aria-label="Nội dung ngưỡng độ tin cậy" spellCheck={false} className="w-full rounded-lg border border-[var(--line)] bg-[var(--page)] px-3 py-2.5 font-mono text-xs leading-5 text-[var(--ink)] outline-none transition focus:border-[var(--brand)]" value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

const EVAL_SUMMARY_ROWS: Array<[string, string]> = [
  ['MAPE (sai số tổng)', 'mape'],
  ['Tỉ lệ tổng nằm trong khoảng đáp án', 'total_in_expected_rate'],
  ['Tỉ lệ khoảng chạm đáp án', 'interval_hit_rate'],
  ['Hướng giải pháp đúng', 'direction_ok_pct'],
  ['Truy vết trung bình', 'avg_traceability_pct'],
  ['Kiểm tra đạt', 'checks_pass_pct'],
  ['Số lần gọi LLM trung bình', 'avg_llm_calls'],
  ['Thời gian trung bình (giây)', 'avg_seconds'],
];

const CONFIDENCE_LEVEL_LABELS: Record<string, string> = { low: 'Thấp', medium: 'Trung bình', high: 'Cao' };

function num(value: Record<string, unknown>, key: string): number | null {
  const raw = value[key];
  return typeof raw === 'number' && Number.isFinite(raw) ? raw : null;
}
function bool(value: Record<string, unknown>, key: string): boolean | null {
  const raw = value[key];
  return typeof raw === 'boolean' ? raw : null;
}

/** Đánh giá hệ thống (thiet_ke_danh_gia.md §6.4) — đọc báo cáo mới nhất, chỉ hiển thị. */
function EvalReportPanel() {
  const report = useQuery({ queryKey: ['eval-report'], queryFn: getEvalReportLatest, retry: false });
  if (report.isPending) return <p role="status" className="text-sm text-[var(--muted)]">Đang tải báo cáo…</p>;
  if (report.isError) {
    const notFound = report.error instanceof ApiError && report.error.status === 404;
    return <p className="rounded-lg border border-[var(--line)] bg-[var(--page)] px-4 py-3 text-sm text-[var(--muted)]">{notFound ? 'Chưa có báo cáo đánh giá hệ thống.' : report.error instanceof ApiError ? report.error.message : 'Không tải được báo cáo.'}</p>;
  }
  const data = report.data;
  const caseRows = Object.entries(data.per_case).flatMap(([caseId, runs]) =>
    runs.map((run, index) => ({ caseId, run, index })),
  );
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-[var(--ink)]">
        <span>Provider: <strong>{data.provider}</strong></span>
        <span>Model: <strong>{data.model}</strong></span>
        <span>Thời gian chạy: <strong>{data.started_at}</strong></span>
        <span>Tổng thời gian: <strong>{data.seconds}s</strong></span>
        {data.repeat > 1 && <span>Số lần lặp: <strong>{data.repeat}</strong></span>}
      </div>
      {data.provider === 'mock' && <p className="text-xs text-[var(--muted)]">Mock chỉ kiểm tra harness, không đo chất lượng AI.</p>}

      <div className="overflow-x-auto rounded-xl border border-[var(--line)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-[var(--page)] text-xs uppercase tracking-wide text-[var(--muted)]">
            <tr><th className="px-3 py-2">Chỉ số tổng hợp</th><th className="px-3 py-2">Giá trị</th></tr>
          </thead>
          <tbody className="divide-y divide-[var(--line)]">
            {EVAL_SUMMARY_ROWS.map(([label, key]) => {
              const value = data.summary[key];
              const display = key.endsWith('_rate') && typeof value === 'number'
                ? `${Math.round(value * 100)}%`
                : value == null ? '—' : String(value);
              return <tr key={key}><td className="px-3 py-2 text-[var(--muted)]">{label}</td><td className="px-3 py-2 tabular-nums">{display}</td></tr>;
            })}
          </tbody>
        </table>
      </div>

      <div className="overflow-x-auto rounded-xl border border-[var(--line)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-[var(--page)] text-xs uppercase tracking-wide text-[var(--muted)]">
            <tr>
              <th className="px-3 py-2">Case</th>
              <th className="px-3 py-2">Hướng đúng</th>
              <th className="px-3 py-2">APE tổng</th>
              <th className="px-3 py-2">Trong khoảng</th>
              <th className="px-3 py-2">Khoảng chạm</th>
              <th className="px-3 py-2">Sai lệch tỉ trọng</th>
              <th className="px-3 py-2">Truy vết</th>
              <th className="px-3 py-2">Bắt buộc truy vết</th>
              <th className="px-3 py-2">Kiểm tra đạt</th>
              <th className="px-3 py-2">Sai lệch tuần</th>
              <th className="px-3 py-2">Độ tin cậy</th>
              <th className="px-3 py-2">LLM calls</th>
              <th className="px-3 py-2">Giây</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--line)]">
            {caseRows.map(({ caseId, run, index }) => {
              const directionOk = bool(run, 'direction_ok');
              const inExpected = bool(run, 'total_in_expected');
              const intervalHit = bool(run, 'interval_hit');
              const mustTraceOk = bool(run, 'must_trace_ok');
              const checksPass = num(run, 'checks_pass');
              return (
                <tr key={`${caseId}-${index}`}>
                  <td className="px-3 py-2 font-mono text-xs">{caseId}</td>
                  <td className="px-3 py-2">{directionOk == null ? '—' : directionOk ? '✓' : '✕'}</td>
                  <td className="px-3 py-2 tabular-nums">{num(run, 'total_ape') == null ? '—' : `${num(run, 'total_ape')}%`}</td>
                  <td className="px-3 py-2">{inExpected == null ? '—' : inExpected ? '✓' : '✕'}</td>
                  <td className="px-3 py-2">{intervalHit == null ? '—' : intervalHit ? '✓' : '✕'}</td>
                  <td className="px-3 py-2 tabular-nums">{num(run, 'phase_share_error') == null ? '—' : num(run, 'phase_share_error')}</td>
                  <td className="px-3 py-2 tabular-nums">{num(run, 'traceability_pct') == null ? '—' : `${num(run, 'traceability_pct')}%`}</td>
                  <td className="px-3 py-2">{mustTraceOk == null ? '—' : mustTraceOk ? '✓' : '✕'}</td>
                  <td className="px-3 py-2 tabular-nums">{checksPass == null ? '—' : `${Math.round(checksPass * 100)}%`}</td>
                  <td className="px-3 py-2 tabular-nums">{num(run, 'duration_weeks_error') == null ? '—' : `${num(run, 'duration_weeks_error')} tuần`}</td>
                  <td className="px-3 py-2">{CONFIDENCE_LEVEL_LABELS[String(run.confidence_level)] ?? '—'}</td>
                  <td className="px-3 py-2 tabular-nums">{num(run, 'llm_calls') ?? '—'}</td>
                  <td className="px-3 py-2 tabular-nums">{num(run, 'seconds') ?? '—'}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
function CriteriaEditor({ value, total, onChange }: { value: Criterion[]; total: number; onChange: (value: Criterion[]) => void }) { return <div><div className={`mb-5 rounded-xl border px-4 py-3 text-sm ${Math.abs(total - 100) < 0.001 ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-900'}`}>Tổng trọng số: <strong>{total}%</strong> · {Math.abs(total - 100) < 0.001 ? 'Đã đủ 100%' : 'Cần đúng 100% trước khi lưu'}</div><div className="space-y-3">{value.map((item, index) => <div key={index} className="grid gap-3 rounded-xl border border-[var(--line)] p-4 sm:grid-cols-[1fr_2fr_110px_auto] sm:items-end"><Field label="Mã tiêu chí" value={item.id} onChange={(id) => onChange(value.map((row, i) => i === index ? { ...row, id } : row))} /><Field label="Tiêu chí" value={item.label_vi} onChange={(label_vi) => onChange(value.map((row, i) => i === index ? { ...row, label_vi } : row))} /><label className="block text-sm font-medium text-[var(--ink)]">Trọng số (%)<input type="number" min="0" className="mt-2 w-full rounded-lg border border-[var(--line)] bg-[var(--page)] px-3 py-2.5 text-sm" value={item.weight} onChange={(event) => onChange(value.map((row, i) => i === index ? { ...row, weight: Number(event.target.value) } : row))} /></label><button type="button" aria-label={`Xóa tiêu chí ${index + 1}`} className="pb-2 text-sm font-semibold text-red-700 underline" onClick={() => onChange(value.filter((_, i) => i !== index))}>Xóa</button></div>)}</div><button type="button" className="mt-4 rounded-lg border border-dashed border-[var(--brand)] px-4 py-2 text-sm font-semibold text-[var(--brand)]" onClick={() => onChange([...value, EMPTY_CRITERION])}>+ Thêm tiêu chí</button></div>; }
