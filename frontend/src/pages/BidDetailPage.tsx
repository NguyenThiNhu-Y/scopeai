import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { ApiError, createEmailDraft, downloadExport, getBid, getQuestions, getEvaluations, getEffort, getQuotation, getSchedule, importQuestions, listAttachments, rerunPipeline, startPipeline, downloadQuestions } from '../api/client';
import { usePipelineEvents } from '../hooks/usePipelineEvents';
import { BID_STATUS, type IntakeOutput, type Question, type StepState, type StepStatus } from '../api/types';
import BidStatusBadge from '../components/BidStatusBadge';
import ClarifySection from '../components/ClarifySection';
import PipelineProgress from '../components/PipelineProgress';
import { formatAmount, formatDate, coveragePercent, COVERAGE_DISPLAY_KEYS, SOLUTION_LABELS } from '../lib/format';
import AttachmentUploader from '../components/AttachmentUploader';
import FileParseReview from '../components/FileParseReview';
import RequirementMatrix from '../components/RequirementMatrix';
import EffortBreakdown from '../components/EffortBreakdown';
import BidPlanTab from '../components/BidPlanTab';
import ProposalPage from './ProposalPage';
import ApprovalsPage from './ApprovalsPage';

const TAB_KEYS = ['overview', 'requirements', 'solution', 'plan', 'coverage', 'proposal', 'approval'] as const;
type DetailTab = (typeof TAB_KEYS)[number];

function OverviewEmpty({ text, tone = 'neutral' }: { text: string; tone?: 'neutral' | 'error' }) {
  return <p className={`rounded-lg px-3 py-2 text-sm leading-6 ${tone === 'error' ? 'bg-red-50 text-red-700' : 'bg-slate-50 text-[var(--muted)]'}`}>{text}</p>;
}

function OverviewCard({ title, tab, onNavigate, children }: { title: string; tab: string; onNavigate: (tab: string) => void; children: ReactNode }) {
  return (
    <section className="min-h-36 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold text-[var(--ink)]">{title}</h2>
        <button type="button" onClick={() => onNavigate(tab)} className="text-xs font-semibold text-[var(--brand)] hover:underline">Chi tiết ›</button>
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function MarkdownPreview({ content }: { content: string }) {
  const lines = content.split('\n').map((line) => line.trim()).filter(Boolean);
  return (
    <div className="space-y-3 text-sm leading-6 text-[var(--muted)]">
      {lines.map((line, index) => {
        if (/^[-*]\s+/.test(line)) {
          return <p key={index} className="pl-5 before:mr-2 before:content-['•']">{line.replace(/^[-*]\s+/, '')}</p>;
        }
        if (/^#{1,6}\s+/.test(line)) {
          const level = line.match(/^#+/)?.[0].length ?? 2;
          const Heading = level <= 2 ? 'h3' : 'h4';
          return <Heading key={index} className="font-semibold text-[var(--ink)]">{line.replace(/^#{1,6}\s+/, '')}</Heading>;
        }
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

const COVERAGE_LABELS: Record<string, string> = {
  '◎': '◎', '○': '○', '△': '△', '×': '×',
  pass: '◎', partial: '○', fail: '×',
  unclear: 'Cần làm rõ',
  pass_count: '◎', partial_count: '○', fail_count: '×',
  unclear_count: 'Cần làm rõ',
};

/**
 * Chi tiết hồ sơ (FR-007) + điều khiển pipeline M2 (FR-023):
 * - "Phân tích" → startPipeline; disabled khi đang chạy hoặc đang chờ làm rõ chưa trả lời.
 * - Tiến độ realtime qua SSE (usePipelineEvents).
 * - "Chạy lại" (rerun) khi có bước failed.
 * - Kết quả phân tích B1 (IntakeAnalysis) nếu hệ thống trả output bước intake.
 */
export default function BidDetailPage() {
  const { id } = useParams<{ id: string }>();
  const bidId = Number(id);
   const navigate = useNavigate();
   const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedTab = searchParams.get('tab');
  const activeTab: DetailTab = TAB_KEYS.includes(requestedTab as DetailTab) ? requestedTab as DetailTab : 'overview';
  const setTab = (tab: string) => setSearchParams({ tab });

  const bidQuery = useQuery({
    queryKey: ['bid', bidId],
    queryFn: () => getBid(bidId),
    enabled: Number.isFinite(bidId),
  });
  const bid = bidQuery.data;
  const attachmentsQuery = useQuery({ queryKey: ['attachments', bidId], queryFn: () => listAttachments(bidId), enabled: Number.isFinite(bidId) });
  const evaluationsQuery = useQuery({ queryKey: ['evaluations', bidId], queryFn: () => getEvaluations(bidId), enabled: Boolean(bid), retry: false });
  // E.2: chỉ gọi effort/quotation/schedule khi pipeline đã qua các bước tương ứng
  // (tránh lỗi 409 trên console khi hồ sơ còn draft/đang phân tích/chờ làm rõ).
  const pipelineAdvanced = Boolean(bid) && !['draft', 'analyzing', 'waiting_clarification'].includes(bid?.status ?? '');
  const effortQuery = useQuery({ queryKey: ['effort', bidId], queryFn: () => getEffort(bidId), enabled: pipelineAdvanced, retry: false });
  const quotationQuery = useQuery({ queryKey: ['quotation', bidId], queryFn: () => getQuotation(bidId), enabled: pipelineAdvanced, retry: false });
  const scheduleQuery = useQuery({ queryKey: ['schedule', bidId], queryFn: () => getSchedule(bidId), enabled: pipelineAdvanced, retry: false });

  const [streamOn, setStreamOn] = useState(false);
  const [startingPipeline, setStartingPipeline] = useState(false);
  const [rerunning, setRerunning] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [downloadingBundle, setDownloadingBundle] = useState(false);
  const [questionFileBusy, setQuestionFileBusy] = useState(false);
  const [questionExportBusy, setQuestionExportBusy] = useState(false);
  const [emailBusy, setEmailBusy] = useState(false);
  const [emailDraft, setEmailDraft] = useState<{ customer_name: string; sender: string; subject: string; body: string } | null>(null);
  const questionFileInput = useRef<HTMLInputElement>(null);

  const events = usePipelineEvents(bidId, streamOn);

  const isWaitingClarification = bid?.status === BID_STATUS.clarification;

  const questionsQuery = useQuery({
    queryKey: ['questions', bidId],
    queryFn: () => getQuestions(bidId),
    enabled: Number.isFinite(bidId),
  });

  // Mở lại hồ sơ đang "Đang phân tích" → bật stream để nhận tiếp tiến độ.
  useEffect(() => {
    if (bid?.status === 'analyzing') setStreamOn(true);
  }, [bid?.status]);

  // E.2: poll mỗi 3 giây khi pipeline đang chạy — trạng thái và tab tự cập nhật
  // kể cả khi mất kết nối SSE.
  useEffect(() => {
    if (bid?.status !== 'analyzing') return;
    const timer = window.setInterval(() => {
      void queryClient.invalidateQueries({ queryKey: ['bid', bidId] });
      void queryClient.invalidateQueries({ queryKey: ['questions', bidId] });
      void queryClient.invalidateQueries({ queryKey: ['evaluations', bidId] });
    }, 3000);
    return () => window.clearInterval(timer);
  }, [bidId, bid?.status, queryClient]);

  // SSE `clarify` → cập nhật dữ liệu đã persist; pipeline đang chờ → tắt stream.
  useEffect(() => {
    if (events.clarifyQuestions) {
      void queryClient.invalidateQueries({ queryKey: ['bid', bidId] });
      void queryClient.invalidateQueries({ queryKey: ['questions', bidId] });
      void queryClient.invalidateQueries({ queryKey: ['evaluations', bidId] });
      setStreamOn(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bidId, events.clarifyQuestions, queryClient]);

  // SSE `done` → hồ sơ chuyển sang bước duyệt kỹ thuật → cập nhật + tắt stream.
  useEffect(() => {
    if (events.done) {
      for (const key of ['bid', 'attachments', 'evaluations', 'effort', 'quotation', 'schedule', 'questions', 'proposal', 'wbs', 'history']) {
        void queryClient.invalidateQueries({ queryKey: [key, bidId] });
      }
      void queryClient.invalidateQueries({ queryKey: ['bids'] });
      setStreamOn(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bidId, events.done, queryClient]);

  // SSE `error` → cập nhật trạng thái bước lỗi đã persist + tắt stream (tránh reconnect loop).
  useEffect(() => {
    if (events.error) {
      void queryClient.invalidateQueries({ queryKey: ['bid', bidId] });
      setStreamOn(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bidId, events.error, queryClient]);

  // Gộp trạng thái bước: ưu tiên trạng thái realtime từ SSE, fallback từ pipeline_progress.
  const mergedSteps = useMemo<StepState[]>(() => {
    const map = new Map<string, StepState>();
    (bid?.pipeline_progress?.steps ?? []).forEach((s) => map.set(s.step_key, s));
    Object.entries(events.steps).forEach(([key, status]) => {
      const existing = map.get(key);
      map.set(key, { ...(existing ?? { step_key: key, status: status as StepStatus }), status: status as StepStatus });
    });
    return Array.from(map.values());
  }, [bid?.pipeline_progress?.steps, events.steps]);

  const intakeOutput = useMemo<IntakeOutput | null>(() => {
    const intakeStep = mergedSteps.find((s) => s.step_key === 'intake');
    return intakeStep?.output_json ?? null;
  }, [mergedSteps]);

  const failedStep = mergedSteps.find((s) => s.status === 'failed');
  const anyRunning =
    mergedSteps.some((s) => s.status === 'running') || bid?.status === BID_STATUS.analyzing;
   const unansweredQuestions = questionsQuery.data?.items.filter((q) => !q.answer) ?? [];
   const hasUnanswered = unansweredQuestions.length > 0;

  useEffect(() => {
    if (isWaitingClarification && hasUnanswered && activeTab !== 'requirements') {
      setTab('requirements');
    }
    // The clarification banner should guide the user to the first unanswered question.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isWaitingClarification, hasUnanswered]);

  const clarifyQuestions: Question[] = events.clarifyQuestions ?? questionsQuery.data?.items ?? [];
  const pipelineErrorMessage = events.error ?? failedStep?.error_message ?? null;

  const analyzeDisabled =
    startingPipeline || anyRunning || (isWaitingClarification && hasUnanswered) || Boolean(bid && !bid.no_requirement_file && !bid.data_readiness);
  const analyzeHint =
    startingPipeline || anyRunning
      ? 'Pipeline đang chạy — vui lòng chờ.'
      : isWaitingClarification && hasUnanswered
        ? 'Hãy trả lời câu hỏi làm rõ trước'
        : null;

  async function handleAnalyze() {
    setActionError(null);
    setStartingPipeline(true);
    try {
      await startPipeline(bidId);
      setStreamOn(true);
      bidQuery.refetch();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : 'Không chạy được phân tích. Vui lòng thử lại.',
      );
    } finally {
      setStartingPipeline(false);
    }
  }

  async function handleRerun() {
    setActionError(null);
    setRerunning(true);
    try {
      await rerunPipeline(bidId);
      setStreamOn(true);
      bidQuery.refetch();
    } catch (err) {
      setActionError(
        err instanceof ApiError ? err.message : 'Không chạy lại được. Vui lòng thử lại.',
      );
    } finally {
      setRerunning(false);
    }
  }

  async function handleDownloadBundle() {
    setActionError(null);
    setDownloadingBundle(true);
    try {
      const file = await downloadExport(bidId, 'bundle');
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Không tải được bộ hồ sơ.');
    } finally {
      setDownloadingBundle(false);
    }
  }

  async function handleImportQuestions(file: File) {
    setActionError(null);
    setQuestionFileBusy(true);
    try {
      const result = await importQuestions(bidId, file);
      if (result.warnings?.length) {
        setActionError(`Đã nhập câu trả lời, nhưng có ${result.warnings.length} dòng được bỏ qua.`);
      }
      await Promise.all([questionsQuery.refetch(), bidQuery.refetch()]);
      setStreamOn(true);
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Không nhập được bảng câu hỏi. Vui lòng thử lại.');
    } finally {
      setQuestionFileBusy(false);
      if (questionFileInput.current) questionFileInput.current.value = '';
    }
  }

  async function handleExportQuestions() {
    setActionError(null);
    setQuestionExportBusy(true);
    try {
      const file = await downloadQuestions(bidId);
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.filename;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Không tải được bảng câu hỏi. Vui lòng thử lại.');
    } finally {
      setQuestionExportBusy(false);
    }
  }

  async function handleCreateEmailDraft() {
    setActionError(null);
    setEmailBusy(true);
    try {
      const draft = await createEmailDraft(bidId);
      setEmailDraft(draft);
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Không soạn được email. Vui lòng thử lại.');
    } finally {
      setEmailBusy(false);
    }
  }

  async function handleCopyEmail() {
    if (!emailDraft) return;
    try {
      await navigator.clipboard.writeText(`Tiêu đề: ${emailDraft.subject}\n\n${emailDraft.body}`);
      setActionError(null);
    } catch {
      setActionError('Không thể sao chép email. Bạn có thể bôi đen nội dung để sao chép thủ công.');
    }
  }

  function handleAnswersSubmitted() {
    // E.2: gửi trả lời → pipeline resume → invalidate MỌI tab để tự tải lại.
    setStreamOn(true);
    for (const key of ['bid', 'attachments', 'evaluations', 'effort', 'quotation', 'schedule', 'questions', 'proposal', 'wbs', 'history']) {
      void queryClient.invalidateQueries({ queryKey: [key, bidId] });
    }
    void queryClient.invalidateQueries({ queryKey: ['bids'] });
  }

  if (bidQuery.isPending) {
    return (
      <div className="mx-auto max-w-5xl px-8 py-12">
        <p className="text-sm text-slate-500" role="status">
          Đang tải hồ sơ…
        </p>
      </div>
    );
  }

  if (bidQuery.isError || !bid) {
    const message =
      bidQuery.error instanceof ApiError
        ? bidQuery.error.message
        : 'Không tải được hồ sơ.';
    return (
      <div className="mx-auto max-w-5xl px-8 py-12">
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <p className="text-sm font-medium text-red-700">{message}</p>
          <button
            type="button"
            onClick={() => navigate('/bids')}
            className="mt-2 rounded-lg bg-red-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-red-700"
          >
            Về danh sách hồ sơ
          </button>
        </div>
      </div>
    );
  }

  const questionCount = clarifyQuestions.filter((question) => !question.answer).length;
  const requirementCount = evaluationsQuery.data?.items.length ?? 0;
  const displayQuotation = quotationQuery.data
    ? formatAmount(quotationQuery.data.totals.grand_total, quotationQuery.data.currency)
    : null;
  const hasRun = mergedSteps.length > 0;
  const answeredQuestionCount = clarifyQuestions.filter((question) => Boolean(question.answer)).length;
  // E.1: % đáp ứng = (◎ + ○) / tổng ĐÃ ĐÁNH GIÁ (stats.evaluated) — không cộng total/evaluated.
  const coveragePct = coveragePercent(evaluationsQuery.data?.stats ?? {});

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <header className="border-b border-[var(--line)] pb-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="min-w-0">
            <button type="button" onClick={() => navigate('/bids')} className="text-xs font-medium text-[var(--brand)] hover:underline">
              Hồ sơ <span aria-hidden="true">›</span> #{bid.id}
            </button>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-[var(--ink)] sm:text-2xl">{bid.project_name}</h1>
              <span className="text-xs text-[var(--muted)]">Sửa</span>
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[var(--muted)]">
              <span>{bid.customer_name}</span>
              {bid.customer_schedule_start && <span>Bắt đầu dự án: {formatDate(bid.customer_schedule_start)}</span>}
              <span>Giai đoạn: {bid.status === BID_STATUS.clarification ? 'Chờ làm rõ' : 'Đang xử lý'}</span>
              <BidStatusBadge status={bid.status} />
              <span className="rounded bg-slate-100 px-2 py-0.5">KT {bid.status === BID_STATUS.technicalApproval || bid.status === BID_STATUS.priceApproval || bid.status === BID_STATUS.priceApproved ? '✓' : '–'}</span>
              <span className="rounded bg-slate-100 px-2 py-0.5">Giá {bid.status === BID_STATUS.priceApproved ? '✓' : '–'}</span>
              {displayQuotation && <span className="font-semibold text-[var(--ink)]">{displayQuotation}</span>}
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={handleDownloadBundle} disabled={downloadingBundle} className="rounded-md border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)] disabled:opacity-50">{downloadingBundle ? 'Đang chuẩn bị…' : 'Tải trọn bộ hồ sơ'}</button>
            <button type="button" onClick={() => setTab('approval')} className="rounded-md border border-[var(--line)] bg-white px-3 py-2 text-xs font-semibold text-[var(--ink)]">Yêu cầu sửa</button>
            <button type="button" onClick={() => setTab('approval')} className="rounded-md bg-[var(--brand)] px-3 py-2 text-xs font-semibold text-white hover:opacity-90">Duyệt</button>
          </div>
        </div>
      </header>

      {isWaitingClarification && questionCount > 0 && (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900" role="status">
           <span>AI cần bạn trả lời {questionCount} câu hỏi để phân tích tiếp{questionsQuery.data?.blocking_reason ? `: ${questionsQuery.data.blocking_reason}` : '.'}</span>
          <button type="button" onClick={() => setTab('requirements')} className="font-semibold underline">Trả lời câu hỏi</button>
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={hasRun ? handleRerun : handleAnalyze}
          disabled={analyzeDisabled}
          title={analyzeHint ?? undefined}
          className={hasRun
            ? 'rounded-lg border border-blue-200 bg-white px-5 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50'
            : 'rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50'}
        >
          {startingPipeline || anyRunning || rerunning ? 'Đang phân tích…' : hasRun ? 'Chạy lại' : 'Phân tích'}
        </button>
        {failedStep && <span className="text-sm text-[var(--danger)]">Cần xử lý bước thất bại trong thanh tiến độ bên dưới.</span>}
      </div>

      {analyzeDisabled && analyzeHint && (
        <p className="mt-2 text-xs text-amber-600">{analyzeHint}</p>
      )}
      {actionError && (
        <p
          role="alert"
          className="mt-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {actionError}
        </p>
      )}

       <div className="mt-3">
        <PipelineProgress
          steps={mergedSteps}
          errorMessage={pipelineErrorMessage}
          onRetry={failedStep ? handleRerun : undefined}
          retrying={rerunning}
        />
       </div>

       <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6" aria-label="Chỉ số hồ sơ">
         <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-3"><p className="text-xs text-[var(--muted)]">Requirement</p><p className="mt-1 text-lg font-semibold text-[var(--ink)]">{requirementCount}{coveragePct != null ? ` · ${coveragePct}%` : ''}</p></div>
         <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-3"><p className="text-xs text-[var(--muted)]">Câu hỏi</p><p className="mt-1 text-lg font-semibold text-[var(--ink)]">{answeredQuestionCount}/{clarifyQuestions.length}</p></div>
         <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-3"><p className="text-xs text-[var(--muted)]">Man-day</p><p className="mt-1 text-lg font-semibold text-[var(--ink)]">{effortQuery.data?.midpoint_total ?? '—'}</p></div>
         <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-3"><p className="text-xs text-[var(--muted)]">Giá nội bộ</p><p className="mt-1 text-lg font-semibold text-[var(--ink)]">{displayQuotation ?? '—'}</p></div>
         <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-3"><p className="text-xs text-[var(--muted)]">Ngày kết thúc</p><p className="mt-1 text-lg font-semibold text-[var(--ink)]">{scheduleQuery.data ? formatDate(scheduleQuery.data.end_date) : '—'}</p></div>
         <div className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-3"><p className="text-xs text-[var(--muted)]">Trạng thái duyệt</p><p className="mt-1 text-sm font-semibold text-[var(--ink)]"><BidStatusBadge status={bid.status} /></p></div>
       </div>

      <div className="mt-3 overflow-x-auto border-b border-[var(--line)]">
        <div className="flex min-w-max gap-6" role="tablist" aria-label="Các phần của hồ sơ">
          {[
            ['overview', 'Tổng quan'], ['requirements', `Yêu cầu & câu hỏi${questionCount ? ` (${questionCount})` : ''}`], ['solution', 'Giải pháp'],
             ['plan', 'Kế hoạch & báo giá'], ['coverage', `Đáp ứng yêu cầu${requirementCount ? ` (${requirementCount})` : ''}`], ['proposal', 'Proposal & hồ sơ'], ['approval', 'Quy trình & phê duyệt'],
          ].map(([key, label]) => <button key={key} id={`tab-${key}`} type="button" role="tab" aria-selected={activeTab === key} tabIndex={activeTab === key ? 0 : -1} onClick={() => setTab(key)} className={`border-b-2 px-1 py-3 text-sm font-semibold ${activeTab === key ? 'border-[var(--brand)] text-[var(--brand)]' : 'border-transparent text-[var(--muted)]'}`}>{label}</button>)}
        </div>
      </div>
      {activeTab === 'overview' && (
        <div role="tabpanel" aria-labelledby="tab-overview">
        <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <OverviewCard title="Mục tiêu của khách" tab="requirements" onNavigate={setTab}>
            {intakeOutput ? (
              <div className="space-y-3">
                <p className="leading-6 text-[var(--ink)]">{intakeOutput.objectives_vi}</p>
                <div className="flex flex-wrap gap-2">
                  {intakeOutput.constraints_vi.slice(0, 4).map((constraint) => (
                    <span key={constraint} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">{constraint}</span>
                  ))}
                  {intakeOutput.constraints_vi.length > 4 && <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">+{intakeOutput.constraints_vi.length - 4} ràng buộc khác</span>}
                </div>
              </div>
            ) : <OverviewEmpty text="Chạy phân tích để hệ thống tóm tắt mục tiêu và ràng buộc của khách." />}
          </OverviewCard>

          <OverviewCard title="Hướng giải pháp" tab="solution" onNavigate={setTab}>
            {evaluationsQuery.data?.solution_direction ? (
              <div className="space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold text-[var(--ink)]">{SOLUTION_LABELS[evaluationsQuery.data.solution_direction.direction] ?? 'Hướng giải pháp'}</span>
                  <span className="rounded-full border border-slate-200 px-2 py-0.5 text-xs text-slate-600">Đang đề xuất</span>
                </div>
                <p className="whitespace-pre-wrap leading-6 text-[var(--muted)]">{evaluationsQuery.data.solution_direction.reason_vi}</p>
                {evaluationsQuery.data.solution_direction.risks_vi?.length ? <ul className="list-disc space-y-1 pl-5 text-sm text-[var(--muted)]">{evaluationsQuery.data.solution_direction.risks_vi.slice(0, 2).map((risk) => <li key={risk}>{risk}</li>)}</ul> : null}
              </div>
            ) : <OverviewEmpty text="Chưa có hướng giải pháp. Hãy chạy phân tích để nhận đề xuất có căn cứ." />}
          </OverviewCard>

           <OverviewCard title="Khả thi" tab="solution" onNavigate={setTab}>
             {bid.status === BID_STATUS.error ? <OverviewEmpty text="Hồ sơ đang lỗi. Mở Giải pháp để xem bước cần chạy lại." tone="error" /> : evaluationsQuery.data?.solution_direction?.feasibility ? <p className="text-sm text-[var(--muted)]">Đã có đánh giá khả thi định tính. Mở Giải pháp để xem chi tiết.</p> : null}
          </OverviewCard>

          <OverviewCard title="Rủi ro lớn nhất" tab="solution" onNavigate={setTab}>
             {pipelineErrorMessage ? <p className="rounded-lg bg-red-50 px-3 py-2 text-sm leading-6 text-red-700">{pipelineErrorMessage}</p> : evaluationsQuery.data?.solution_direction?.risks_vi?.length ? <ul className="space-y-2 text-sm text-[var(--muted)]">{evaluationsQuery.data.solution_direction.risks_vi.slice(0, 3).map((risk) => <li key={risk} className="border-l-2 border-amber-400 pl-3">{risk}</li>)}</ul> : null}
          </OverviewCard>

          <OverviewCard title="Effort & kế hoạch" tab="plan" onNavigate={setTab}>
            {effortQuery.data ? (
              <div className="space-y-3">
                <div className="text-2xl font-semibold text-[var(--ink)]">{effortQuery.data.midpoint_total.toLocaleString('vi-VN', { maximumFractionDigits: 1 })} <span className="text-sm font-normal text-[var(--muted)]">man-day midpoint</span></div>
                <div className="grid grid-cols-3 gap-2 text-xs text-[var(--muted)]">{(['poc', 'mvp', 'production'] as const).map((phase) => <div key={phase} className="rounded-lg bg-slate-50 p-2"><div className="font-semibold text-[var(--ink)]">{phase === 'poc' ? 'PoC' : phase === 'mvp' ? 'MVP' : 'Production'}</div>{effortQuery.data?.by_phase[phase].min}–{effortQuery.data?.by_phase[phase].max}</div>)}</div>
                {scheduleQuery.isPending && <p className="text-xs text-[var(--muted)]">Đang tải số task và lịch kết thúc…</p>}
                {scheduleQuery.isError && <p className="text-xs text-amber-700">Chưa tải được lịch; mở tab Kế hoạch & báo giá để thử lại.</p>}
                {scheduleQuery.data && <div className="flex flex-wrap gap-2 text-xs"><span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-700">{scheduleQuery.data.tasks.length} task WBS</span><span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-700">Kết thúc {formatDate(scheduleQuery.data.end_date)}</span></div>}
              </div>
            ) : <OverviewEmpty text="Effort sẽ xuất hiện sau khi hoàn tất đánh giá hướng giải pháp." />}
          </OverviewCard>

          <OverviewCard title="Báo giá sơ bộ" tab="plan" onNavigate={setTab}>
            {quotationQuery.data ? (
              <div className="space-y-3">
                <div className="text-2xl font-semibold text-[var(--ink)]">{formatAmount(quotationQuery.data.totals.grand_total, quotationQuery.data.currency)}</div>
                <div className="grid grid-cols-2 gap-2 text-xs text-[var(--muted)]">
                  <div className="rounded-lg bg-slate-50 p-2"><span className="block font-semibold text-[var(--ink)]">Dự phòng</span>{formatAmount(quotationQuery.data.totals.contingency_amount, quotationQuery.data.currency)} ({quotationQuery.data.contingency_percent}%)</div>
                  <div className="rounded-lg bg-slate-50 p-2"><span className="block font-semibold text-[var(--ink)]">Vận hành/tháng</span>{formatAmount(quotationQuery.data.totals.operating_cost, quotationQuery.data.currency)}</div>
                </div>
                {quotationQuery.data.budget && (
                  <p className="text-xs text-[var(--muted)]">
                    Ngân sách khách: {formatAmount(quotationQuery.data.budget.amount, quotationQuery.data.budget.currency)} ·{' '}
                    {quotationQuery.data.budget.difference == null
                      ? 'chưa đủ dữ liệu so sánh'
                      : `chênh lệch ${formatAmount(quotationQuery.data.budget.difference, quotationQuery.data.currency)}`}
                  </p>
                )}
                <p className="text-sm text-[var(--muted)]">Giá nội bộ, chờ phê duyệt trước khi đưa vào tài liệu khách hàng.</p>
              </div>
            ) : <OverviewEmpty text="Báo giá sẽ hiển thị sau khi hệ thống tính xong effort và đơn giá chuẩn." />}
          </OverviewCard>

          <OverviewCard title="Đáp ứng yêu cầu" tab="coverage" onNavigate={setTab}>
            {evaluationsQuery.data ? (() => { const stats = evaluationsQuery.data?.stats ?? {}; const chips = COVERAGE_DISPLAY_KEYS.filter((key) => (stats[key] ?? 0) > 0); return <div className="flex flex-wrap gap-2">{chips.map((key) => <span key={key} className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">{COVERAGE_LABELS[key] ?? 'Cần làm rõ'}: {stats[key]}</span>)}{chips.length === 0 && <span className="text-sm text-[var(--muted)]">Đã có ma trận nhưng chưa có thống kê phân loại.</span>}</div>; })() : <OverviewEmpty text="Chưa có dữ liệu đáp ứng. Kiểm tra file requirement ở tab Yêu cầu & câu hỏi." />}
          </OverviewCard>

          <OverviewCard title="Câu hỏi cần khách xác nhận" tab="requirements" onNavigate={setTab}>
             {questionCount ? <div className="space-y-2"><p className="text-2xl font-bold text-[var(--ink)]">{questionCount}</p><p className="text-sm text-[var(--muted)]">câu chưa có trả lời{questionsQuery.data?.blocking_reason ? ` · ${questionsQuery.data.blocking_reason}` : ''}</p></div> : <OverviewEmpty text="Không có câu hỏi cần xác nhận ở thời điểm này." />}
          </OverviewCard>
        </div>
        <details className="mt-4 rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5">
           <summary className="cursor-pointer font-semibold text-[var(--ink)]">Yêu cầu gốc của khách</summary>
           {bid.request_content ? <div className="mt-4"><MarkdownPreview content={bid.request_content} /></div> : <p className="mt-4 text-sm text-[var(--muted)]">Chưa có nội dung yêu cầu. Hãy bổ sung nội dung ở tab Yêu cầu & câu hỏi.</p>}
         </details>
         </div>
      )}

      {activeTab === 'requirements' && (
        <div role="tabpanel" aria-labelledby="tab-requirements" className="mt-8 space-y-6">
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div><h2 className="text-lg font-semibold text-slate-900">Kết quả phân tích yêu cầu</h2><p className="mt-1 text-sm text-slate-500">Tóm tắt được trích xuất từ hồ sơ, không thay thế nội dung gốc.</p></div>
              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">Nội bộ</span>
            </div>
            {intakeOutput ? <dl className="mt-5 grid gap-4 sm:grid-cols-2">
              {[['Mục tiêu', intakeOutput.objectives_vi], ['Người dùng', intakeOutput.users_vi], ['Dữ liệu', intakeOutput.data_vi], ['Ràng buộc', intakeOutput.constraints_vi.join(' · ') || 'Chưa xác định'], ['Ngân sách', intakeOutput.budget_note_vi || (intakeOutput.budget_mentioned ? 'Đã đề cập trong hồ sơ' : 'Chưa đề cập')], ['Thời hạn', intakeOutput.deadline_note_vi || (intakeOutput.deadline_mentioned ? 'Đã đề cập trong hồ sơ' : 'Chưa đề cập')]].map(([label, value]) => <div key={label} className="rounded-lg bg-slate-50 p-4"><dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</dt><dd className="mt-1 text-sm leading-6 text-slate-800">{value}</dd></div>)}
            </dl> : <OverviewEmpty text="Chưa có kết quả phân tích. Chạy phân tích để hệ thống tóm tắt yêu cầu." />}
          </section>
          {attachmentsQuery.isPending && <p role="status" className="rounded-lg border border-[var(--line)] bg-[var(--surface)] p-4 text-sm text-[var(--muted)]">Đang tải danh sách file…</p>}
          {attachmentsQuery.isError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">Không tải được danh sách file. Vui lòng thử lại.</p>}
          {!attachmentsQuery.isPending && !attachmentsQuery.isError && <AttachmentUploader bidId={bidId} attachments={attachmentsQuery.data?.items ?? []} onUploaded={() => attachmentsQuery.refetch()} />}
          <FileParseReview bidId={bidId} attachments={attachmentsQuery.data?.items ?? []} onConfirmed={() => bidQuery.refetch()} />
          {questionsQuery.isPending && <p role="status" className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">Đang tải yêu cầu và câu hỏi…</p>}
          {questionsQuery.isError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">Không tải được câu hỏi. Vui lòng thử lại.</p>}
          {!questionsQuery.isPending && !questionsQuery.isError && clarifyQuestions.length === 0 && <p className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-500">Chưa có câu hỏi làm rõ cho hồ sơ này.</p>}
          {clarifyQuestions.length > 0 && <ClarifySection bidId={bidId} questions={clarifyQuestions} roundsUsed={questionsQuery.data?.rounds_used ?? 1} maxRounds={questionsQuery.data?.max_rounds ?? 2} roundTwoReason={questionsQuery.data?.round_two_reason_vi} onSubmitted={handleAnswersSubmitted} />}
          {!bid.no_requirement_file && evaluationsQuery.isPending && <p role="status" className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">Đang tải ma trận đáp ứng…</p>}
          {!bid.no_requirement_file && evaluationsQuery.isError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">Không tải được ma trận đáp ứng.</p>}
           <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
             <details>
               <summary className="cursor-pointer font-semibold text-slate-900">Yêu cầu gốc của khách</summary>
               {bid.request_content ? <div className="mt-4"><MarkdownPreview content={bid.request_content} /></div> : <p className="mt-4 text-sm text-slate-500">Chưa có nội dung yêu cầu.</p>}
             </details>
           </section>
             <section className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4" aria-label="Trao đổi Q&A">
                <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-semibold text-slate-800">Trao đổi Q&A</h2><p className="mt-1 text-sm text-slate-500">Xuất bảng theo ngôn ngữ khách, điền cột trả lời màu vàng rồi nhập lại để tiếp tục phân tích.</p></div><div className="flex flex-wrap gap-2"><button type="button" onClick={() => void handleExportQuestions()} disabled={questionExportBusy || questionFileBusy} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold disabled:opacity-50">{questionExportBusy ? 'Đang xuất…' : 'Xuất Q&A sheet'}</button><button type="button" onClick={() => questionFileInput.current?.click()} disabled={questionFileBusy || questionExportBusy} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold disabled:opacity-50">{questionFileBusy ? 'Đang nhập…' : 'Nhập Q&A đã điền'}</button><input ref={questionFileInput} type="file" accept=".xlsx" className="hidden" onChange={(event) => { const file = event.target.files?.[0]; if (file) void handleImportQuestions(file); }} /></div></div>
                <div className="mt-4 border-t border-slate-200 pt-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><h3 className="font-semibold text-slate-800">Email gửi khách</h3><p className="mt-1 text-sm text-slate-500">Bản nháp dùng ngôn ngữ khách; tên khách và người gửi được điền tự động, bạn có thể sửa trước khi gửi.</p></div><button type="button" onClick={() => void handleCreateEmailDraft()} disabled={emailBusy} className="rounded-lg bg-[var(--brand)] px-3 py-2 text-sm font-semibold text-white disabled:opacity-50">{emailBusy ? 'Đang soạn…' : 'Soạn email gửi khách'}</button></div>{emailDraft && <div className="mt-4 space-y-3 rounded-lg border border-slate-200 bg-white p-4"><label className="block text-sm font-semibold text-slate-700">Người nhận<input value={emailDraft.customer_name} onChange={(event) => setEmailDraft({ ...emailDraft, customer_name: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label><label className="block text-sm font-semibold text-slate-700">Người gửi<input value={emailDraft.sender} onChange={(event) => setEmailDraft({ ...emailDraft, sender: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label><label className="block text-sm font-semibold text-slate-700">Tiêu đề<input value={emailDraft.subject} onChange={(event) => setEmailDraft({ ...emailDraft, subject: event.target.value })} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label><label className="block text-sm font-semibold text-slate-700">Nội dung<textarea value={emailDraft.body} onChange={(event) => setEmailDraft({ ...emailDraft, body: event.target.value })} rows={7} className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-normal" /></label><button type="button" onClick={() => void handleCopyEmail()} className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold">Copy email</button></div>}</div>
             </section>
         </div>
      )}

      {activeTab === 'solution' && (
        <div role="tabpanel" aria-labelledby="tab-solution" className="mt-8 space-y-6">
          {evaluationsQuery.isPending && <p role="status" className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">Đang tải hướng giải pháp…</p>}
          {evaluationsQuery.isError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">Không tải được hướng giải pháp. Vui lòng thử lại.</p>}
          {!evaluationsQuery.isPending && !evaluationsQuery.isError && !evaluationsQuery.data?.solution_direction && <p className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-500">Chưa có hướng giải pháp. Hãy chạy phân tích hoặc mở màn hình rà soát.</p>}
          {evaluationsQuery.data?.solution_direction && (() => {
            const proposal = evaluationsQuery.data.solution_direction;
            const feasibility = proposal.feasibility;
             return (
              <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Hướng giải pháp đề xuất</p>
                    <h2 className="mt-1 text-lg font-semibold text-slate-900">{SOLUTION_LABELS[proposal.direction] ?? 'Hướng giải pháp'}</h2>
                  </div>
                  <button type="button" onClick={() => navigate(`/bids/${bidId}/solution`)} className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-100">Rà soát hướng giải pháp</button>
                </div>
                <dl className="mt-5 space-y-4 text-sm">
                   <div><dt className="font-semibold text-slate-500">Độ tin cậy</dt><dd className="mt-1 text-slate-700">{proposal.reliability_vi || 'Chưa có mô tả độ tin cậy.'}</dd></div>
                  <div><dt className="font-semibold text-slate-500">Lý do</dt><dd className="mt-1 whitespace-pre-wrap text-slate-700">{proposal.reason_vi || 'Chưa có lý do.'}</dd></div>
                   <div><dt className="font-semibold text-slate-500">Giả định</dt><dd className="mt-1">{proposal.assumptions_vi?.length ? <ul className="list-disc space-y-1 pl-5 text-slate-700">{proposal.assumptions_vi.map((assumption) => <li key={assumption}>{assumption}</li>)}</ul> : <span className="text-slate-500">Chưa có giả định.</span>}</dd></div>
                </dl>
                <div className="mt-5 border-t border-slate-200 pt-4">
                  <h3 className="text-sm font-semibold text-slate-700">Các hướng đã loại</h3>
                   {proposal.excluded_directions?.length ? <ul className="mt-2 space-y-2 text-sm text-slate-700">{proposal.excluded_directions.map((direction) => <li key={direction}><span className="font-semibold line-through">{SOLUTION_LABELS[direction]}</span></li>)}</ul> : <p className="mt-2 text-sm text-slate-500">Chưa có hướng nào bị loại.</p>}
                </div>
                 <div className="mt-5 border-t border-slate-200 pt-4">
                   <h3 className="text-sm font-semibold text-slate-700">Khả thi & rủi ro</h3>
                     {proposal.feasibility_score ? <div className="mt-3 rounded-lg border border-blue-100 bg-blue-50 p-3"><p className="text-xs font-semibold text-blue-700">Điểm khả thi</p><p className="mt-1 text-2xl font-bold tabular-nums text-blue-900">{proposal.feasibility_score.score}/5</p><p className="mt-1 text-sm text-blue-900">{proposal.feasibility_score.reason_vi}</p></div> : null}
                     {feasibility ? <dl className="mt-3 grid gap-3 sm:grid-cols-3">{Object.entries(feasibility).map(([key, value]) => <div key={key} className="rounded-lg bg-slate-50 p-3"><dt className="text-xs font-semibold text-slate-500">{key === 'technical' ? 'Kỹ thuật' : key === 'delivery' ? 'Triển khai' : key === 'operational' ? 'Vận hành' : key}</dt><dd className="mt-1 text-sm text-slate-700">{value}</dd></div>)}</dl> : null}
                     {proposal.risks?.length ? <div className="mt-3 grid gap-3 sm:grid-cols-2">{proposal.risks.map((risk) => <article key={`${risk.type_vi}-${risk.description_vi}`} className="rounded-lg border border-amber-100 bg-amber-50/50 p-3"><div className="flex items-center justify-between gap-2"><h4 className="text-sm font-semibold text-slate-800">{risk.type_vi}</h4><span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">Mức {risk.level}/5</span></div><p className="mt-2 text-sm text-slate-700">{risk.description_vi}</p><p className="mt-2 text-xs text-slate-600"><span className="font-semibold">Giảm thiểu:</span> {risk.mitigation_vi}</p></article>)}</div> : proposal.risks_vi?.length ? <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">{proposal.risks_vi.map((risk) => <li key={risk}>{risk}</li>)}</ul> : <p className="mt-3 text-sm text-slate-500">Chưa có rủi ro được ghi nhận.</p>}
                </div>
                <div className="mt-5 border-t border-slate-200 pt-4"><h3 className="text-sm font-semibold text-slate-700">Ghi chú kiến trúc</h3><p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">{proposal.architecture_notes_vi || 'Chưa có ghi chú kiến trúc.'}</p>{proposal.risks_vi?.length ? <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600">{proposal.risks_vi.map((risk) => <li key={risk}>{risk}</li>)}</ul> : null}</div>
              </section>
            );
          })()}
          {effortQuery.isPending && <p role="status" className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">Đang tải effort…</p>}
           {effortQuery.isError && <OverviewEmpty text="Chưa có dữ liệu effort cho hồ sơ này." />}
          {effortQuery.data && <EffortBreakdown effort={effortQuery.data} />}
        </div>
      )}

      {activeTab === 'plan' && <div role="tabpanel" aria-labelledby="tab-plan" className="mt-8"><BidPlanTab bidId={bidId} /></div>}
      {activeTab === 'coverage' && <div role="tabpanel" aria-labelledby="tab-coverage" className="mt-8 space-y-6">
        {bid.no_requirement_file && <p className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">Khách không gửi file Excel requirement. Ma trận đáp ứng sẽ không hiển thị.</p>}
        {!bid.no_requirement_file && evaluationsQuery.isPending && <p role="status" className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-500">Đang tải ma trận đáp ứng…</p>}
        {!bid.no_requirement_file && evaluationsQuery.isError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">Không tải được ma trận đáp ứng. Vui lòng thử lại.</p>}
        {!bid.no_requirement_file && evaluationsQuery.data && <RequirementMatrix data={evaluationsQuery.data} bidId={bidId} />}
      </div>}
      {activeTab === 'proposal' && <div role="tabpanel" aria-labelledby="tab-proposal" className="mt-8"><ProposalPage /></div>}
      {activeTab === 'approval' && <div role="tabpanel" aria-labelledby="tab-approval" className="mt-8"><ApprovalsPage /></div>}
    </div>
  );
}
