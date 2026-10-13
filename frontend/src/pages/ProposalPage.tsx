import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ApiError, downloadExport, getBid, getProposal, translateProposal as translateProposalApi, updateProposal } from '../api/client';
import type { ExportKind, ProposalDraft, ProposalSections } from '../api/types';
import ExportButtons from '../components/ExportButtons';

const LABELS: Record<keyof ProposalSections, Record<'vi' | 'en' | 'ja', string>> = {
  introduction: { vi: 'Giới thiệu', en: 'Introduction', ja: 'はじめに' },
  requirements_understanding: { vi: 'Hiểu yêu cầu', en: 'Requirements understanding', ja: 'ご要件の理解' },
  solution_overview: { vi: 'Tổng quan giải pháp', en: 'Solution overview', ja: '提案概要' },
  approach: { vi: 'Cách tiếp cận', en: 'Approach', ja: '進め方' },
  schedule: { vi: 'Lịch trình', en: 'Schedule', ja: 'スケジュール' },
  team: { vi: 'Đội ngũ', en: 'Team', ja: '体制' },
  assumptions_and_scope: { vi: 'Điều kiện và ngoài phạm vi', en: 'Assumptions and out of scope', ja: '前提条件・対象外' },
  risks: { vi: 'Rủi ro', en: 'Risks', ja: 'リスク' },
};
const LANGUAGES = [['vi', 'Tiếng Việt'], ['en', 'English'], ['ja', '日本語']] as const;
const SECTION_KEYS = Object.keys(LABELS) as Array<keyof ProposalSections>;
type ProposalLanguage = 'vi' | 'en' | 'ja';
type ProposalResponse = ProposalDraft;

export default function ProposalPage() {
  const id = Number(useParams<{ id: string }>().id);
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ['proposal', id], queryFn: () => getProposal(id) as Promise<ProposalResponse>, enabled: Number.isFinite(id) });
  const bidQuery = useQuery({ queryKey: ['bid', id], queryFn: () => getBid(id), enabled: Number.isFinite(id) });
  const [draft, setDraft] = useState<ProposalSections | null>(null);
  const [language, setLanguage] = useState<ProposalLanguage | null>(null);
  const customerLanguage = bidQuery.data?.customer_language;
  const effectiveLanguage = language;
  const [editing, setEditing] = useState(false);
  const [downloading, setDownloading] = useState<ExportKind | null>(null);
  const [markdownDownloading, setMarkdownDownloading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [copyNotice, setCopyNotice] = useState<string | null>(null);
  const [documentView, setDocumentView] = useState(false);
  const [translating, setTranslating] = useState(false);

  const mutation = useMutation({
    mutationFn: (sections: ProposalSections) => updateProposal(id, sections),
    onSuccess: (data) => {
      setDraft(data.sections);
      query.refetch();
      setEditing(false);
      setNotice('Đã lưu nội dung proposal.');
    },
    onError: (error) => setNotice(error instanceof ApiError ? error.message : 'Không lưu được proposal.'),
  });

  const proposalMarkdown = useMemo(() => {
    const data = query.data;
    const sections = draft ?? data?.sections;
    if (!data || !sections || !effectiveLanguage) return '';
    const translated = effectiveLanguage === (customerLanguage ?? 'vi') ? sections : data.translations?.[effectiveLanguage];
    const visibleSections = translated ?? sections;
    const quotation = data.price_gate === 'placeholder' ? '[Presales điền]' : data.quotation_markdown ?? '[Presales điền]';
    const body = SECTION_KEYS.map((key) => `## ${LABELS[key][effectiveLanguage]}\n\n${(visibleSections[key] ?? sections[key] ?? '').split('{{QUOTATION}}').join(quotation)}`).join('\n\n');
    return body;
  }, [customerLanguage, draft, effectiveLanguage, query.data]);

  if (query.isPending) return <Message text="Đang tải proposal…" />;
  if (query.isError || !query.data) return <Message text={query.error instanceof ApiError ? query.error.message : 'Không tải được proposal.'} error />;

  const sections = draft ?? query.data.sections;
  const quotationIsPresent = Object.values(sections).some((value) => value?.includes('{{QUOTATION}}'));
  const canEdit = query.data.editable;
  const hasTranslation = !language || language === (customerLanguage ?? 'vi') || Boolean(query.data.translations?.[language]);
  const missingTranslationSections = language && language !== (customerLanguage ?? 'vi') && query.data.translations?.[language]
    ? SECTION_KEYS.filter((key) => !query.data.translations?.[language]?.[key])
    : [];

  async function translateProposal() {
    if (!language || hasTranslation) return;
    setTranslating(true);
    setNotice(null);
    try {
      const translated = await translateProposalApi(id, language);
      queryClient.setQueryData(['proposal', id], translated);
      setNotice(`Đã dịch proposal sang ${LANGUAGES.find(([key]) => key === language)?.[1]}.`);
    } catch (error) {
      setNotice(error instanceof ApiError ? error.message : 'Không dịch được proposal. Nội dung gốc vẫn được giữ nguyên.');
    } finally { setTranslating(false); }
  }

  function downloadMarkdown() {
    setMarkdownDownloading(true);
    try {
      const blob = new Blob([proposalMarkdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `proposal-${id}.md`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
      setNotice(`Đã tải proposal-${id}.md.`);
    } finally {
      setMarkdownDownloading(false);
    }
  }

  async function copyMarkdown() {
    setCopyNotice(null);
    try {
      await navigator.clipboard.writeText(proposalMarkdown);
      setCopyNotice('Đã copy Markdown.');
    } catch {
      setCopyNotice('Không thể copy trên trình duyệt này.');
    }
  }

  async function handleExport(kind: ExportKind) {
    setDownloading(kind);
    setNotice(null);
    try {
      const file = await downloadExport(id, kind);
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.filename;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
      setNotice(`Đã tải ${file.filename}.`);
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : 'Không tải được hồ sơ.');
    } finally {
      setDownloading(null);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--brand)]">Hồ sơ proposal · #{id}</p>
      <section className="mt-6 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5">
        <div className="mb-4">
          <h1 className="text-xl font-bold tracking-tight text-[var(--ink)]">Tải hồ sơ</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">Các file được tạo từ dữ liệu hiện có. Trước khi duyệt giá, proposal dùng nhãn [Presales điền].</p>
        </div>
        <ExportButtons downloading={downloading} onDownload={handleExport} />
        <button type="button" disabled={markdownDownloading || downloading !== null} onClick={downloadMarkdown} aria-busy={markdownDownloading} className="mt-3 flex w-full items-center justify-between rounded-lg border border-[var(--line)] bg-[var(--surface)] px-4 py-3 text-left transition hover:border-blue-300 hover:bg-blue-50 disabled:cursor-wait disabled:opacity-60">
          <span><span className="block text-sm font-semibold text-[var(--ink)]">{markdownDownloading ? 'Đang chuẩn bị…' : 'Proposal Markdown'}</span><span className="mt-1 block text-xs text-[var(--muted)]">.md · nội dung đang xem</span></span>
          <span className="text-[var(--brand)]" aria-hidden="true">↓</span>
        </button>
        {notice && <p role="status" className="mt-3 text-sm text-[var(--muted)]">{notice}</p>}
      </section>

      <section className="mt-5 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-semibold text-[var(--ink)]">Nội dung proposal</h2>
          <div className="flex gap-2">
            <button type="button" onClick={() => setDocumentView(true)} className="rounded-lg bg-[var(--brand)] px-3 py-1.5 text-xs font-semibold text-white">Xem dạng tài liệu</button>
             <button type="button" disabled={!canEdit || !language || language !== (customerLanguage ?? 'vi')} onClick={() => setEditing(!editing)} className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-50">{editing ? 'Xem trước' : 'Chỉnh sửa'}</button>
            <button type="button" onClick={copyMarkdown} className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-xs font-semibold">Copy Markdown</button>
          </div>
        </div>
        <div className="mt-4 flex gap-2 overflow-x-auto border-b border-[var(--line)] pb-3" role="tablist" aria-label="Ngôn ngữ proposal">
          {LANGUAGES.map(([key, label]) => <button key={key} role="tab" aria-selected={language === key} type="button" onClick={() => setLanguage(key)} className={`whitespace-nowrap px-3 py-1.5 text-xs font-semibold ${language === key ? 'rounded bg-[var(--brand-soft)] text-[var(--brand)]' : 'text-[var(--muted)]'}`}>{label}</button>)}
        </div>
        {!language ? <p role="status" className="mt-4 rounded-lg border border-[var(--line)] bg-[var(--brand-soft)] p-4 text-sm text-[var(--ink)]">Chọn ngôn ngữ trước khi soạn proposal.</p> : <>
           <p className="mt-3 text-xs text-[var(--muted)]">Nội dung hiển thị theo bản dịch đã lưu; phần thiếu bản dịch sẽ giữ nguyên nội dung gốc. Chỉ chỉnh sửa được ngôn ngữ gốc.</p>
          {missingTranslationSections.length > 0 && <p role="status" className="mt-2 text-xs text-amber-700">Một số mục chưa có bản dịch ({missingTranslationSections.map((key) => LABELS[key][language]).join(', ')}), đang hiển thị nội dung gốc.</p>}
          {!hasTranslation && <div className="mt-3 flex flex-wrap items-center gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800"><span>Chưa có bản dịch {LANGUAGES.find(([key]) => key === language)?.[1]}.</span><button type="button" onClick={translateProposal} disabled={translating} className="rounded bg-amber-700 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60">{translating ? 'Đang dịch…' : `Dịch sang ${LANGUAGES.find(([key]) => key === language)?.[1]}`}</button></div>}
        </>}
        {copyNotice && <p role="status" className="mt-3 text-xs text-[var(--muted)]">{copyNotice}</p>}
        {language && editing ? (
          <div className="mt-5 grid gap-5 lg:grid-cols-2">
            <div>
              <p className="text-sm font-semibold text-[var(--ink)]">Soạn Markdown</p>
              <div className="mt-3 space-y-4">
                {SECTION_KEYS.map((key) => <label key={key} className="block"><span className="text-sm font-semibold text-[var(--ink)]">{LABELS[key][language]}</span><textarea value={sections[key] ?? ''} onChange={(event) => setDraft({ ...sections, [key]: event.target.value })} rows={8} className="mt-2 block w-full rounded-lg border border-[var(--line)] bg-transparent px-3 py-2 text-sm leading-relaxed text-[var(--ink)]" /></label>)}
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-[var(--ink)]">Xem trước</p>
              <article aria-label="Xem trước Markdown" className="mt-3 rounded-lg border border-[var(--line)] bg-white p-6 text-[var(--ink)]"><MarkdownView markdown={proposalMarkdown} /></article>
            </div>
            {!quotationIsPresent && <p role="alert" className="lg:col-span-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">Bạn đã xóa dòng <code>{'{{QUOTATION}}'}</code>. Hãy giữ dòng này để hệ thống chèn giá sau khi được duyệt.</p>}
            <div className="lg:col-span-2 flex flex-wrap gap-2">
              <button type="button" disabled={!draft || mutation.isPending || !quotationIsPresent} onClick={() => draft && mutation.mutate(draft)} className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">{mutation.isPending ? 'Đang lưu…' : 'Lưu thay đổi'}</button>
              <button type="button" onClick={() => { setDraft(null); setEditing(false); }} className="rounded-lg border border-[var(--line)] px-4 py-2 text-sm font-semibold">Hủy</button>
            </div>
          </div>
        ) : language ? (
          <article aria-label="Nội dung Markdown" className="mt-5 rounded-lg border border-[var(--line)] bg-white p-6 text-[var(--ink)]"><MarkdownView markdown={proposalMarkdown} /></article>
        ) : null}
      </section>
      {documentView && language && <DocumentView id={id} language={language} markdown={proposalMarkdown} onClose={() => setDocumentView(false)} />}
    </div>
  );
}

function DocumentView({ id, language, markdown, onClose }: { id: number; language: ProposalLanguage; markdown: string; onClose: () => void }) {
  return <div className="proposal-document-overlay" role="dialog" aria-modal="true" aria-label="Tài liệu proposal A4">
    <div className="proposal-document-toolbar"><span>Proposal #{id} · {language.toUpperCase()}</span><div className="flex gap-2"><button type="button" onClick={() => window.print()} className="rounded bg-[var(--brand)] px-3 py-1.5 text-xs font-semibold text-white">In tài liệu</button><button type="button" onClick={onClose} className="rounded border border-[var(--line)] px-3 py-1.5 text-xs font-semibold">Đóng</button></div></div>
    <article className="proposal-a4"><header className="proposal-cover"><p className="proposal-kicker">PROPOSAL DOCUMENT</p><h1>Proposal</h1><p>Mã hồ sơ: #{id}</p><p>Ngôn ngữ: {language.toUpperCase()}</p></header><nav className="proposal-toc"><h2>Mục lục</h2><ol>{SECTION_KEYS.map((key) => <li key={key}>{LABELS[key][language]}</li>)}</ol></nav><section className="proposal-paper-content"><MarkdownView markdown={markdown} /></section></article>
  </div>;
}

function MarkdownView({ markdown }: { markdown: string }) {
  const blocks = markdown.split(/\n\s*\n/).filter(Boolean);
  return <div className="space-y-5 text-sm leading-7">{blocks.map((block, index) => <MarkdownBlock key={`${index}-${block.slice(0, 12)}`} block={block} />)}</div>;
}

function MarkdownBlock({ block }: { block: string }) {
  const lines = block.split('\n');
  const content = lines[0].startsWith('## ') ? lines.slice(1) : lines;
  const heading = lines[0].startsWith('## ') ? <h3 className="border-b border-[var(--line)] pb-2 text-lg font-bold text-[var(--ink)]">{inlineMarkdown(lines[0].slice(3))}</h3> : null;
  if (content.length > 1 && content.every((line) => line.startsWith('|'))) return <section>{heading}<MarkdownTable lines={content} /></section>;
  if (content.length > 0 && content.every((line) => line.startsWith('- '))) return <section>{heading}<ul className="list-disc space-y-1 pl-5">{content.map((line, index) => <li key={`${index}-${line}`}>{inlineMarkdown(line.slice(2))}</li>)}</ul></section>;
  return <section>{heading}<p className={heading ? 'mt-3' : undefined}>{content.map((line, index) => <span key={`${index}-${line}`}>{inlineMarkdown(line)}<br /></span>)}</p></section>;
}

function MarkdownTable({ lines }: { lines: string[] }) {
  const rows = lines.filter((line) => !/^\|\s*:?-+/.test(line)).map((line) => line.split('|').slice(1, -1).map((cell) => cell.trim()));
  return <div className="overflow-x-auto"><table className="min-w-full border-collapse text-left"><thead><tr>{rows[0]?.map((cell) => <th key={cell} className="border-b border-[var(--line)] px-3 py-2 font-semibold">{inlineMarkdown(cell)}</th>)}</tr></thead><tbody>{rows.slice(1).map((row, rowIndex) => <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={`${rowIndex}-${cellIndex}`} className="border-b border-[var(--line)] px-3 py-2 align-top">{inlineMarkdown(cell)}</td>)}</tr>)}</tbody></table></div>;
}

function inlineMarkdown(value: string) {
  const parts = value.split(/(\[Presales điền\]|\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    if (part === '[Presales điền]') {
      return <mark key={index} className="rounded bg-amber-100 px-1.5 py-0.5 font-semibold text-amber-800">{part}</mark>;
    }
    return part.startsWith('**') && part.endsWith('**')
      ? <strong key={index}>{part.slice(2, -2)}</strong>
      : part;
  });
}

function Message({ text, error = false }: { text: string; error?: boolean }) {
  return <div className="mx-auto max-w-4xl px-6 py-12"><p role={error ? 'alert' : 'status'} className={error ? 'rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700' : 'text-sm text-slate-500'}>{text}</p></div>;
}
