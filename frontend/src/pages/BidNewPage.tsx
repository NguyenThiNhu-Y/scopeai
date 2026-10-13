import { useRef, useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ApiError,
  confirmParse,
  createBid,
  getSamplePreview,
  loadSample,
  parseAttachments,
  startPipeline,
  uploadAttachment,
} from '../api/client';
import type { BidCreate, CustomerLanguage, SampleKey, SamplePreview } from '../api/types';
import { LANGUAGE_LABELS } from '../lib/format';
import { useHealth } from '../hooks/useHealth';

const MIN_REQUEST_LENGTH = 30;
const MAX_FILES = 10;
const MAX_FILE_SIZE = 20 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = ['pdf', 'docx', 'txt', 'md', 'xlsx', 'xls', 'csv', 'zip'];
const LANGUAGE_OPTIONS: CustomerLanguage[] = ['vi', 'en', 'ja'];
const CURRENCY_OPTIONS = ['VND', 'JPY', 'USD'];

interface FormState {
  project_name: string;
  customer_name: string;
  submission_deadline: string;
  customer_language: CustomerLanguage;
  request_content: string;
  budget_currency: string;
}

interface PendingFile {
  file: File;
  fileType: 'rfp' | 'requirement' | 'sample_data';
  error?: string;
}

const EMPTY_FORM: FormState = {
  project_name: '', customer_name: '', submission_deadline: '', customer_language: 'vi',
  request_content: '', budget_currency: 'VND',
};
const INPUT = 'mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20';
const ERROR_INPUT = `${INPUT} border-red-300 focus:border-red-500 focus:ring-red-500/20`;

function formatSize(bytes: number) {
  return bytes < 1024 * 1024 ? `${Math.ceil(bytes / 1024)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function classifyFile(name: string): PendingFile['fileType'] {
  const extension = name.split('.').pop()?.toLowerCase();
  if (extension === 'xlsx' || extension === 'xls' || extension === 'csv') return 'requirement';
  if (extension === 'zip') return 'sample_data';
  return 'rfp';
}

function sampleForm(sample: SamplePreview): FormState {
  return {
    project_name: sample.project_name,
    customer_name: sample.customer_name,
    submission_deadline: sample.submission_deadline,
    customer_language: sample.customer_language,
    request_content: sample.request_content,
    budget_currency: sample.display_currency,
  };
}

export default function BidNewPage() {
  const navigate = useNavigate();
  const health = useHealth();
  const fileInput = useRef<HTMLInputElement>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [files, setFiles] = useState<PendingFile[]>([]);
  const [selectedSample, setSelectedSample] = useState<SampleKey | null>(null);
  const [samplePreview, setSamplePreview] = useState<SamplePreview | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [message, setMessage] = useState<{ kind: 'error' | 'info'; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState('');

  function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
    setErrors((previous) => { const next = { ...previous }; delete next[key]; return next; });
  }

  function currencyForLanguage(language: CustomerLanguage) {
    return language === 'ja' ? 'JPY' : language === 'en' ? 'USD' : 'VND';
  }

  async function importRequestFile(file: File) {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (extension === 'txt' || extension === 'md') {
      const text = await file.text();
      setField('request_content', text.slice(0, 200_000));
      setMessage({ kind: 'info', text: `Đã chèn nội dung từ ${file.name}. Giới hạn nội dung là 200.000 ký tự.` });
      return;
    }
    setMessage({ kind: 'info', text: `${file.name} đã được thêm vào tài liệu đính kèm. Nội dung DOCX/PDF sẽ được hệ thống trích xuất khi đọc file.` });
    addFiles([file]);
  }

  async function chooseSample(key: SampleKey) {
    setBusy(true); setMessage(null);
    try {
      const preview = await getSamplePreview(key);
      setForm(sampleForm(preview));
      setSelectedSample(key);
      setSamplePreview(preview);
      setFiles([]);
    } catch (error) {
      setMessage({ kind: 'error', text: error instanceof ApiError ? error.message : 'Không nạp được bộ mẫu.' });
    } finally { setBusy(false); }
  }

  function addFiles(incoming: FileList | File[] | null) {
    if (!incoming) return;
    const next = [...files];
    Array.from(incoming).forEach((file) => {
      let error: string | undefined;
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (!extension || !ACCEPTED_EXTENSIONS.includes(extension)) error = 'Định dạng file chưa được hỗ trợ.';
      else if (file.size > MAX_FILE_SIZE) error = 'File vượt quá giới hạn 20 MB.';
      else if (next.length >= MAX_FILES) error = 'Tối đa 10 file.';
      next.push({ file, fileType: classifyFile(file.name), error });
    });
    setFiles(next.slice(0, MAX_FILES));
  }

  function validate() {
    const next: Record<string, string> = {};
    if (!form.project_name.trim()) next.project_name = 'Vui lòng nhập tên dự án.';
    if (!form.customer_name.trim()) next.customer_name = 'Vui lòng nhập tên khách hàng.';
    if (!form.submission_deadline) next.submission_deadline = 'Vui lòng chọn hạn nộp.';
    if (form.request_content.trim().length < MIN_REQUEST_LENGTH) next.request_content = `Nội dung yêu cầu phải có ít nhất ${MIN_REQUEST_LENGTH} ký tự.`;
    files.forEach((item, index) => { if (item.error) next[`file_${index}`] = item.error; });
    return next;
  }

  async function handleAnalyze(event: FormEvent) {
    event.preventDefault();
    const next = validate(); setErrors(next); setMessage(null);
    if (Object.keys(next).length) return;
    setBusy(true); setProgress('Tạo hồ sơ');
    try {
      const bid = selectedSample
        ? await loadSample(selectedSample)
        : await createBid({
          project_name: form.project_name.trim(), customer_name: form.customer_name.trim(),
          submission_deadline: form.submission_deadline, customer_language: form.customer_language,
          request_content: form.request_content.trim(), budget_currency: form.budget_currency as BidCreate['budget_currency'],
        });
      const uploadable = selectedSample ? [] : files;
      for (let index = 0; index < uploadable.length; index += 1) {
        setProgress(`Tải file (${index + 1}/${uploadable.length})`);
        await uploadAttachment(bid.id, uploadable[index].file, uploadable[index].fileType);
      }
      setProgress('Đọc file');
      const parsed = await parseAttachments(bid.id);
      setProgress(`Đọc file (${parsed.requirements.count} requirement)`);
      await confirmParse(bid.id, parsed.sample_profile?.readiness_suggestion ?? 'medium');
      setProgress('Bắt đầu phân tích');
      await startPipeline(bid.id);
      navigate(`/bids/${bid.id}`);
    } catch (error) {
      setMessage({ kind: 'error', text: error instanceof ApiError ? error.message : 'Phân tích thất bại. Dữ liệu đã nhập được giữ lại, hãy thử lại.' });
      setProgress('');
    } finally { setBusy(false); }
  }

  const requestLength = form.request_content.trim().length;
  const renderFieldError = (key: string) => errors[key] && <p className="mt-1 text-xs font-medium text-red-600">{errors[key]}</p>;

  return (
    <div className="mx-auto max-w-6xl px-6 py-8 lg:px-10">
      <p className="text-sm font-medium text-blue-600">Tạo hồ sơ</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Tạo hồ sơ mới</h1>
      <p className="mt-2 text-base text-slate-600">Dán email/RFP và đính kèm mọi tài liệu. Trợ lý dự thầu sẽ phân tích sau một lần bấm.</p>
       <span className="sr-only" role="status">{health.data?.status === 'ok' ? 'Dịch vụ sẵn sàng' : ''}</span>

      {message && <p role="alert" className={`mt-5 rounded-lg border px-4 py-3 text-sm ${message.kind === 'error' ? 'border-red-200 bg-red-50 text-red-700' : 'border-blue-200 bg-blue-50 text-blue-700'}`}>{message.text}</p>}

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <form onSubmit={handleAnalyze} noValidate className="space-y-5">
          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-5 py-4"><h2 className="font-semibold text-slate-900">Thông tin hồ sơ</h2><p className="mt-1 text-xs text-slate-500">Các trường có dấu * là bắt buộc.</p></div>
            <div className="grid gap-4 p-5 sm:grid-cols-2">
              <label className="text-sm text-slate-700">Tên dự án *<input id="project_name" value={form.project_name} onChange={(e) => setField('project_name', e.target.value)} className={errors.project_name ? ERROR_INPUT : INPUT} />{renderFieldError('project_name')}</label>
              <label className="text-sm text-slate-700">Tên khách hàng *<input id="customer_name" value={form.customer_name} onChange={(e) => setField('customer_name', e.target.value)} className={errors.customer_name ? ERROR_INPUT : INPUT} />{renderFieldError('customer_name')}</label>
              <label className="text-sm text-slate-700">Hạn nộp<input id="submission_deadline" type="date" value={form.submission_deadline} onChange={(e) => setField('submission_deadline', e.target.value)} className={errors.submission_deadline ? ERROR_INPUT : INPUT} />{renderFieldError('submission_deadline')}</label>
               <label className="text-sm text-slate-700">Ngôn ngữ khách *<select value={form.customer_language} onChange={(e) => { const language = e.target.value as CustomerLanguage; setField('customer_language', language); setField('budget_currency', currencyForLanguage(language)); }} className={INPUT}>{LANGUAGE_OPTIONS.map((language) => <option key={language} value={language}>{LANGUAGE_LABELS[language]}</option>)}</select></label>
               <label className="text-sm text-slate-700">Đơn vị tiền tệ<select value={form.budget_currency} onChange={(e) => setField('budget_currency', e.target.value)} className={INPUT}>{CURRENCY_OPTIONS.map((currency) => <option key={currency}>{currency}</option>)}</select><span className="mt-1 block text-xs text-slate-500">Ngân sách không nhập thủ công. Nếu khách có nêu ngân sách, hệ thống sẽ lấy từ nội dung và hiển thị để đối chiếu.</span></label>
            </div>
          </section>

           <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
             <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4"><div><h2 className="font-semibold text-slate-900">Nội dung yêu cầu *</h2><p className="mt-1 text-xs text-slate-500">Giới hạn 200.000 ký tự; email/RFP được che thông tin liên hệ trước khi phân tích.</p></div><label className="cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700">Nhập file<input type="file" accept=".txt,.md,.docx,.pdf" className="sr-only" onChange={(e) => { const file = e.target.files?.[0]; if (file) void importRequestFile(file); e.currentTarget.value = ''; }} /></label></div>
             <div className="p-5"><textarea rows={8} maxLength={200000} value={form.request_content} onChange={(e) => setField('request_content', e.target.value)} placeholder="Dán email hoặc nội dung RFP của khách vào đây…" className={errors.request_content ? ERROR_INPUT : INPUT} /><div className="mt-1 flex justify-between text-xs"><span className={requestLength < MIN_REQUEST_LENGTH ? 'text-red-600' : 'text-slate-400'}>Tối thiểu {MIN_REQUEST_LENGTH} ký tự</span><span className="tabular-nums text-slate-500">{requestLength.toLocaleString('vi-VN')} / 200.000 ký tự</span></div>{renderFieldError('request_content')}</div>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-5 py-4"><div><h2 className="font-semibold text-slate-900">Tài liệu đính kèm ({files.length}/{MAX_FILES})</h2><p className="mt-1 text-xs text-slate-500">PDF, DOCX, TXT, MD, XLSX, XLS, CSV, ZIP · tối đa 20 MB/file</p></div><button type="button" onClick={() => fileInput.current?.click()} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Chọn file</button><input ref={fileInput} type="file" multiple accept=".pdf,.docx,.txt,.md,.xlsx,.xls,.csv,.zip" className="hidden" onChange={(event: ChangeEvent<HTMLInputElement>) => addFiles(event.target.files)} /></div>
            <div className="p-5" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); addFiles(event.dataTransfer.files); }}>
              {samplePreview && selectedSample ? <div className="mb-3 rounded-lg border border-blue-100 bg-blue-50 px-3 py-2 text-sm text-blue-800">Bộ mẫu đã chọn — các file dưới đây sẽ được tạo cùng hồ sơ khi bấm Phân tích.</div> : null}
              {files.length === 0 && !samplePreview && <button type="button" onClick={() => fileInput.current?.click()} className="w-full rounded-lg border border-dashed border-slate-300 px-4 py-8 text-center text-sm text-slate-500 hover:border-blue-400 hover:bg-blue-50">Kéo thả file vào đây hoặc chọn file</button>}
              {samplePreview && files.length === 0 && <div className="divide-y divide-slate-100 rounded-lg border border-slate-200">{samplePreview.files.map((file) => <div key={file.filename} className="flex items-center gap-3 px-3 py-3 text-sm"><span className="min-w-0 flex-1 truncate font-medium text-slate-700">{file.filename}</span><span className="text-xs text-slate-400">{formatSize(file.size_bytes)}</span><span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-500">{file.file_type === 'requirement' ? 'Excel requirement' : 'RFP/tài liệu'}</span></div>)}</div>}
              {files.map((item, index) => <div key={`${item.file.name}-${index}`} className="flex flex-wrap items-center gap-3 border-b border-slate-100 py-3 text-sm last:border-0"><span className="min-w-0 flex-1 truncate font-medium text-slate-700">{item.file.name} <span className="font-normal text-slate-400">({formatSize(item.file.size)})</span></span><select value={item.fileType} onChange={(event) => setFiles((current) => current.map((file, fileIndex) => fileIndex === index ? { ...file, fileType: event.target.value as PendingFile['fileType'] } : file))} className="rounded border border-slate-300 px-2 py-1 text-xs"><option value="rfp">RFP/tài liệu</option><option value="requirement">Excel requirement</option><option value="sample_data">Dữ liệu mẫu</option></select><button type="button" aria-label={`Xóa ${item.file.name}`} onClick={() => setFiles((current) => current.filter((_, fileIndex) => fileIndex !== index))} className="text-slate-400 hover:text-red-600">Xóa</button>{item.error && <p className="basis-full text-xs text-red-600">{item.error}</p>}</div>)}
            </div>
          </section>

          <div className="flex items-center justify-end gap-3"><button type="button" onClick={() => navigate('/bids')} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700">Hủy</button><button type="submit" disabled={busy} className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-wait disabled:opacity-60">{busy ? progress || 'Đang chuẩn bị…' : 'Phân tích →'}</button></div>
        </form>

        <aside className="space-y-5">
          <section className="rounded-xl border border-slate-200 bg-white shadow-sm"><div className="border-b border-slate-200 px-4 py-4"><h2 className="font-semibold text-slate-900">Bộ hồ sơ RFP mẫu</h2><p className="mt-1 text-xs text-slate-500">Email, tài liệu RFP và bảng yêu cầu mẫu.</p></div><div className="space-y-3 p-4">{(['ja_email', 'vi_email'] as SampleKey[]).map((key) => <div key={key} className="rounded-lg border border-slate-200 p-3"><div className="flex items-start justify-between gap-2"><div><span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold">{key === 'ja_email' ? 'JA' : 'VI'}</span><p className="mt-2 text-sm font-medium text-slate-800">{key === 'ja_email' ? 'Hồ sơ CRM cho khách hàng Nhật' : 'Bộ hồ sơ CRM tiếng Việt'}</p></div><button type="button" disabled={busy} onClick={() => chooseSample(key)} className="shrink-0 rounded-md bg-blue-50 px-2.5 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-100">{selectedSample === key ? 'Đã chọn' : 'Dùng bộ này'}</button></div>{selectedSample === key && samplePreview && <div className="mt-3 border-t border-slate-100 pt-2 text-xs text-slate-500">{samplePreview.files.map((file) => <div key={file.filename} className="flex justify-between gap-2 py-1"><span className="truncate">{file.filename}</span><span>{formatSize(file.size_bytes)}</span></div>)}</div>}</div>)}</div></section>
          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"><h2 className="font-semibold text-slate-900">Sau khi bấm Phân tích</h2><ol className="mt-3 space-y-2 text-sm text-slate-600"><li>1. Tạo hồ sơ và tải file</li><li>2. Đọc file, đếm requirement</li><li>3. Phân tích và hỏi làm rõ nếu cần</li></ol><p className="mt-3 text-xs leading-relaxed text-slate-500">Bạn không cần sang trang khác hay bấm thêm nút. Nếu có lỗi, dữ liệu vẫn được giữ lại để thử lại.</p></section>
        </aside>
      </div>
    </div>
  );
}
