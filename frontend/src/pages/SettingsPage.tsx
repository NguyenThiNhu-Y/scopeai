import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ApiError, getSettings, updateSetting } from '../api/client';
import type { SettingKey } from '../api/types';

type CaseStudy = { title: string; industry: string; summary: string };
type Criterion = { id: string; label_vi: string; weight: number };

const SETTINGS: Array<{ key: SettingKey; label: string; eyebrow: string }> = [
  { key: 'company', label: 'Công ty', eyebrow: 'Thông tin nhận diện' },
  { key: 'templates', label: 'Template', eyebrow: 'Mẫu xuất tài liệu' },
  { key: 'standard_content', label: 'Nội dung chuẩn', eyebrow: 'Theo ngôn ngữ' },
  { key: 'case_studies', label: 'Case study', eyebrow: 'Thư viện minh họa' },
  { key: 'bid_no_bid', label: 'Tiêu chí Bid/No-bid', eyebrow: 'Điều kiện sàng lọc' },
];
const LANGUAGES = [['vi', 'Tiếng Việt'], ['en', 'English'], ['ja', '日本語']] as const;
const EMPTY_CASE: CaseStudy = { title: '', industry: '', summary: '' };
const EMPTY_CRITERION: Criterion = { id: '', label_vi: '', weight: 0 };

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}
function text(value: unknown): string { return typeof value === 'string' ? value : ''; }
function settingLabel(key: SettingKey): string { return SETTINGS.find((item) => item.key === key)?.label ?? key; }

export default function SettingsPage() {
  const query = useQuery({ queryKey: ['settings'], queryFn: getSettings });
  const [selected, setSelected] = useState<SettingKey>('company');
  const [draft, setDraft] = useState<unknown>(null);
  const [language, setLanguage] = useState<'vi' | 'en' | 'ja'>('vi');
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<{ kind: 'success' | 'error'; text: string } | null>(null);
  const active = query.data?.keys.find((item) => item.key === selected);

  useEffect(() => { if (active) setDraft(structuredClone(active.payload)); }, [active]);
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
      const result = await updateSetting(selected, JSON.stringify(draft, null, 2), 'manager_web');
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
        <div className="mb-7 flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--brand)]">{active?.source === 'db' ? `Đã chỉnh sửa · v${active.version}` : 'Giá trị mặc định'}</p><h2 className="mt-2 text-2xl font-semibold text-[var(--ink)]">{settingLabel(selected)}</h2></div><button type="button" onClick={save} disabled={saving || !active} className="rounded-lg bg-[var(--brand)] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50">{saving ? 'Đang lưu…' : 'Lưu thay đổi'}</button></div>
        {draft !== null && selected === 'company' && <CompanyEditor value={asRecord(draft)} onChange={patchRecord} />}
        {draft !== null && selected === 'templates' && <TemplatesEditor value={asRecord(draft)} onChange={patchRecord} />}
        {draft !== null && selected === 'standard_content' && <ContentEditor value={asRecord(draft)} language={language} onLanguageChange={setLanguage} onChange={patchRecord} />}
        {draft !== null && selected === 'case_studies' && <CaseStudiesEditor value={Array.isArray(draft) ? draft as CaseStudy[] : []} onChange={setDraft} />}
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
function TemplatesEditor({ value, onChange }: { value: Record<string, unknown>; onChange: (patch: Record<string, unknown>) => void }) { return <div className="space-y-4">{(['word', 'excel'] as const).map((kind) => { const item = asRecord(value[kind]); return <div key={kind} className="grid gap-4 rounded-xl border border-[var(--line)] p-4 sm:grid-cols-[120px_1fr_1fr_auto] sm:items-end"><h3 className="font-semibold text-[var(--ink)]">{kind === 'word' ? 'Word' : 'Excel'}</h3><Field label="Mẫu có sẵn" value={text(item.filename)} onChange={(filename) => onChange({ [kind]: { ...item, filename } })} /><Field label="Nguồn" value={text(item.source)} onChange={(source) => onChange({ [kind]: { ...item, source } })} /><label className="flex items-center gap-2 pb-3 text-sm text-[var(--ink)]"><input type="checkbox" checked={item.valid === true} onChange={(event) => onChange({ [kind]: { ...item, valid: event.target.checked } })} /> Hợp lệ</label></div>; })}<p className="text-xs text-[var(--muted)]">Trạng thái hợp lệ được backend kiểm tra khi lưu.</p></div>; }
function ContentEditor({ value, language, onLanguageChange, onChange }: { value: Record<string, unknown>; language: 'vi' | 'en' | 'ja'; onLanguageChange: (value: 'vi' | 'en' | 'ja') => void; onChange: (patch: Record<string, unknown>) => void }) { const content = asRecord(value[language]); return <div><div className="mb-5 flex gap-2" role="tablist" aria-label="Ngôn ngữ nội dung">{LANGUAGES.map(([code, label]) => <button key={code} type="button" role="tab" aria-selected={language === code} onClick={() => onLanguageChange(code)} className={`rounded-full px-3 py-1.5 text-sm ${language === code ? 'bg-[var(--brand)] text-white' : 'bg-[var(--page)] text-[var(--muted)]'}`}>{label}</button>)}</div><div className="grid gap-5"><Field label="Giới thiệu công ty" multiline value={text(content.company_intro)} onChange={(company_intro) => onChange({ [language]: { ...content, company_intro } })} /><Field label="Bảo mật" multiline value={text(content.security)} onChange={(security) => onChange({ [language]: { ...content, security } })} /><Field label="Điều khoản" multiline value={text(content.terms)} onChange={(terms) => onChange({ [language]: { ...content, terms } })} /></div></div>; }
function CaseStudiesEditor({ value, onChange }: { value: CaseStudy[]; onChange: (value: unknown) => void }) { return <div className="space-y-4">{value.map((item, index) => <div key={index} className="rounded-xl border border-[var(--line)] p-4"><div className="grid gap-4 sm:grid-cols-2"><Field label="Tên case study" value={text(item.title)} onChange={(title) => onChange(value.map((row, i) => i === index ? { ...row, title } : row))} /><Field label="Ngành" value={text(item.industry)} onChange={(industry) => onChange(value.map((row, i) => i === index ? { ...row, industry } : row))} /></div><div className="mt-4"><Field label="Tóm tắt" multiline value={text(item.summary)} onChange={(summary) => onChange(value.map((row, i) => i === index ? { ...row, summary } : row))} /></div><button type="button" className="mt-3 text-sm font-semibold text-red-700 underline" onClick={() => onChange(value.filter((_, i) => i !== index))}>Xóa case study</button></div>)}<button type="button" className="rounded-lg border border-dashed border-[var(--brand)] px-4 py-2 text-sm font-semibold text-[var(--brand)]" onClick={() => onChange([...value, EMPTY_CASE])}>+ Thêm case study</button></div>; }
function CriteriaEditor({ value, total, onChange }: { value: Criterion[]; total: number; onChange: (value: Criterion[]) => void }) { return <div><div className={`mb-5 rounded-xl border px-4 py-3 text-sm ${Math.abs(total - 100) < 0.001 ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-900'}`}>Tổng trọng số: <strong>{total}%</strong> · {Math.abs(total - 100) < 0.001 ? 'Đã đủ 100%' : 'Cần đúng 100% trước khi lưu'}</div><div className="space-y-3">{value.map((item, index) => <div key={index} className="grid gap-3 rounded-xl border border-[var(--line)] p-4 sm:grid-cols-[1fr_2fr_110px_auto] sm:items-end"><Field label="Mã tiêu chí" value={item.id} onChange={(id) => onChange(value.map((row, i) => i === index ? { ...row, id } : row))} /><Field label="Tiêu chí" value={item.label_vi} onChange={(label_vi) => onChange(value.map((row, i) => i === index ? { ...row, label_vi } : row))} /><label className="block text-sm font-medium text-[var(--ink)]">Trọng số (%)<input type="number" min="0" className="mt-2 w-full rounded-lg border border-[var(--line)] bg-[var(--page)] px-3 py-2.5 text-sm" value={item.weight} onChange={(event) => onChange(value.map((row, i) => i === index ? { ...row, weight: Number(event.target.value) } : row))} /></label><button type="button" aria-label={`Xóa tiêu chí ${index + 1}`} className="pb-2 text-sm font-semibold text-red-700 underline" onClick={() => onChange(value.filter((_, i) => i !== index))}>Xóa</button></div>)}</div><button type="button" className="mt-4 rounded-lg border border-dashed border-[var(--brand)] px-4 py-2 text-sm font-semibold text-[var(--brand)]" onClick={() => onChange([...value, EMPTY_CRITERION])}>+ Thêm tiêu chí</button></div>; }
