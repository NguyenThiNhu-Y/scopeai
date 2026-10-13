import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiError,
  approvePrice,
  approveTech,
  getBid,
  getEffort,
  getEvaluations,
  getHistory,
  getQuestions,
  getQuotation,
  getSchedule,
  unlockBid,
  getBidQualification,
  updateBidQualification,
  updateDealStage,
  listProposalVersions,
  createProposalVersion,
  markProposalVersionSent,
} from '../api/client';
import { BID_STATUS, type DealStage } from '../api/types';
import BidStatusBadge from '../components/BidStatusBadge';
import { formatAmount, formatDate, CONTRACT_MODEL_LABELS } from '../lib/format';

const SOLUTION_LABELS: Record<string, string> = {
  none: 'Không dùng AI',
  traditional_ml: 'Học máy truyền thống',
  rag: 'Tra cứu theo tài liệu',
  agent: 'Trợ lý nhiều bước',
  fine_tune: 'Tinh chỉnh mô hình',
};

const HISTORY_ACTION_LABELS: Record<string, string> = {
  approve_tech: 'Duyệt kỹ thuật',
  approve_price: 'Duyệt giá',
  reject_tech: 'Yêu cầu sửa kỹ thuật',
  reject_price: 'Từ chối giá',
  unlock: 'Mở khóa hồ sơ',
  update: 'Cập nhật hồ sơ',
};

const DEAL_STAGE_LABELS: Record<DealStage, string> = {
  lead: 'Tiềm năng', qualified: 'Đã xác định', proposal: 'Đề xuất', negotiation: 'Đàm phán', won: 'Thắng', lost: 'Thua',
};

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm leading-6 text-slate-800">{value}</dd>
    </div>
  );
}

function EmptyState({ children }: { children: string }) {
  return <p className="rounded-lg bg-slate-50 px-3 py-2 text-sm leading-6 text-slate-500">{children}</p>;
}

function ErrorState({ children }: { children: string }) {
  return <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm leading-6 text-red-700">{children}</p>;
}

export default function ApprovalsPage() {
  const id = Number(useParams<{ id: string }>().id);
  const queryClient = useQueryClient();
  const [techComment, setTechComment] = useState('');
  const [priceComment, setPriceComment] = useState('');
  const [sentNote, setSentNote] = useState('');

  const bid = useQuery({ queryKey: ['bid', id], queryFn: () => getBid(id), enabled: Number.isFinite(id) });
  // E.2: chỉ gọi effort/quotation/schedule khi pipeline đã qua bước tương ứng (tránh 409).
  const advanced = Boolean(bid.data) && !['draft', 'analyzing', 'waiting_clarification'].includes(bid.data?.status ?? '');
  const effort = useQuery({ queryKey: ['effort', id], queryFn: () => getEffort(id), enabled: advanced, retry: false });
  const evaluations = useQuery({ queryKey: ['evaluations', id], queryFn: () => getEvaluations(id), enabled: Number.isFinite(id), retry: false });
  const quotation = useQuery({ queryKey: ['quotation', id], queryFn: () => getQuotation(id), enabled: advanced, retry: false });
  const schedule = useQuery({ queryKey: ['schedule', id], queryFn: () => getSchedule(id), enabled: advanced, retry: false });
  const questions = useQuery({ queryKey: ['questions', id], queryFn: () => getQuestions(id), enabled: Number.isFinite(id), retry: false });
  const history = useQuery({ queryKey: ['history', id], queryFn: () => getHistory({ bid_id: id }), enabled: Number.isFinite(id), retry: false });
  const qualification = useQuery({ queryKey: ['bid-qualification', id], queryFn: () => getBidQualification(id), enabled: Number.isFinite(id), retry: false });
  const versions = useQuery({ queryKey: ['proposal-versions', id], queryFn: () => listProposalVersions(id), enabled: Number.isFinite(id), retry: false });
  const [stage, setStage] = useState<DealStage | ''>('');
  const [confirmer, setConfirmer] = useState('');
  const [decision, setDecision] = useState<'bid' | 'no-bid'>('bid');

  const techMutation = useMutation({
    mutationFn: () => approveTech(id, { decision: 'approved', by: 'ai_developer', comment: techComment.trim() || null }),
    onSuccess: () => bid.refetch(),
  });
  const techRejectMutation = useMutation({
    mutationFn: () => approveTech(id, { decision: 'rejected', by: 'ai_developer', comment: techComment.trim() || null }),
    onSuccess: () => bid.refetch(),
  });
  const priceMutation = useMutation({
    mutationFn: () => approvePrice(id, { decision: 'approved', by: 'manager', comment: priceComment.trim() || null }),
    onSuccess: () => bid.refetch(),
  });
  const priceRejectMutation = useMutation({
    mutationFn: () => approvePrice(id, { decision: 'rejected', by: 'manager', comment: priceComment.trim() || null }),
    onSuccess: () => bid.refetch(),
  });
  const unlock = useMutation({
    mutationFn: () => unlockBid(id, priceComment.trim()),
    onSuccess: () => bid.refetch(),
  });
  const stageMutation = useMutation({
    mutationFn: () => updateDealStage(id, stage as DealStage),
    onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['bid', id] }); void queryClient.invalidateQueries({ queryKey: ['bids'] }); },
  });
  const qualificationMutation = useMutation({
    mutationFn: () => updateBidQualification(id, { criteria: qualification.data?.criteria ?? [], decision, confirmer: confirmer.trim() || undefined }),
    onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ['bid-qualification', id] }); void queryClient.invalidateQueries({ queryKey: ['history', id] }); },
  });
  const versionMutation = useMutation({
    mutationFn: () => createProposalVersion(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['proposal-versions', id] }),
  });
  const sentMutation = useMutation({
    mutationFn: (versionId: number) => markProposalVersionSent(id, versionId, sentNote.trim()),
    onSuccess: () => { setSentNote(''); void queryClient.invalidateQueries({ queryKey: ['proposal-versions', id] }); void queryClient.invalidateQueries({ queryKey: ['history', id] }); },
  });

  const bidHistory = history.data?.items ?? [];
  const techApprovalEvent = bidHistory.find((item) => item.action === 'approve_tech');
  const priceApprovalEvent = bidHistory.find((item) => item.action === 'approve_price');

  if (bid.isPending) return <Message text="Đang tải trạng thái duyệt…" />;
  if (bid.isError || !bid.data) return <Message text={bid.error instanceof ApiError ? bid.error.message : 'Không tải được hồ sơ.'} error />;

  const currentStatus = bid.data.status;
  const techApproved = currentStatus === BID_STATUS.priceApproval || currentStatus === BID_STATUS.priceApproved;
  const priceApproved = currentStatus === BID_STATUS.priceApproved;
  const techPending = currentStatus === BID_STATUS.technicalApproval;
  const pricePending = currentStatus === BID_STATUS.priceApproval;
  const techBusy = techMutation.isPending || techRejectMutation.isPending;
  const priceBusy = priceMutation.isPending || priceRejectMutation.isPending;
  const openQuestions = questions.data ? String(questions.data.items.filter((question) => !question.answer).length) : 'Chưa có dữ liệu';
   const effortTotal = effort.data ? `${effort.data.midpoint_total.toLocaleString('vi-VN', { maximumFractionDigits: 1 })} man-day midpoint` : 'Chưa có dữ liệu effort';
  const quotationTotal = quotation.data ? formatAmount(quotation.data.totals.grand_total, quotation.data.currency) : 'Chưa có dữ liệu báo giá';
  const budgetComparison = quotation.data?.budget
    ? quotation.data.budget.difference == null
      ? 'Chưa đủ dữ liệu so sánh'
      : formatAmount(quotation.data.budget.difference, quotation.data.currency)
    : 'Chưa có ngân sách khách';
  const technicalError = effort.isError || evaluations.isError;
  const priceError = quotation.isError;
  const wbsWarning = schedule.data?.warning ?? null;
  const qualificationError = qualification.error instanceof ApiError ? qualification.error.message : 'Không tải được tiêu chí Bid/No-bid.';

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <p className="flex flex-wrap items-center gap-2 text-sm text-slate-500">
          Trạng thái hiện tại: <BidStatusBadge status={currentStatus} /> · {bid.data.locked ? 'Đã khóa' : 'Chưa khóa'}
        </p>
        {bid.data.locked && (
          <button
            type="button"
            disabled={!priceComment.trim() || unlock.isPending}
            onClick={() => unlock.mutate()}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 disabled:opacity-40"
          >
            {unlock.isPending ? 'Đang mở khóa…' : 'Mở khóa hồ sơ'}
          </button>
        )}
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="technical-approval">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div><h3 id="technical-approval" className="text-lg font-semibold text-slate-900">Duyệt kỹ thuật</h3><p className="mt-1 text-sm text-slate-500">Kiểm tra phạm vi, effort và cảnh báo trước khi chuyển sang duyệt giá.</p></div>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${techApproved ? 'bg-emerald-100 text-emerald-800' : techPending ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'}`}>{techApproved ? 'Đã duyệt' : techPending ? 'Chờ duyệt' : 'Chưa sẵn sàng'}</span>
        </div>
        {technicalError || schedule.isError || questions.isError ? <div className="mt-4"><ErrorState>Không tải được đầy đủ tóm tắt kỹ thuật. Vui lòng thử lại dữ liệu hồ sơ.</ErrorState></div> : null}
        <dl className="mt-5 grid gap-3 sm:grid-cols-2">
          <Summary label="Hướng giải pháp" value={evaluations.data?.solution_direction ? SOLUTION_LABELS[evaluations.data.solution_direction.direction] ?? 'Hướng chưa xác định' : 'Chưa có dữ liệu'} />
          <Summary label="Tổng effort" value={effortTotal} />
          <Summary label="Cảnh báo WBS" value={wbsWarning ?? (evaluations.data?.warnings.length ? `${evaluations.data.warnings.length} cảnh báo đánh giá` : 'Chưa có cảnh báo WBS')} />
          <Summary label="Câu hỏi còn mở" value={questions.isError ? 'Không tải được' : openQuestions} />
        </dl>
        {effort.isPending || evaluations.isPending || schedule.isPending || questions.isPending ? <p role="status" className="mt-4 text-sm text-slate-500">Đang tải tóm tắt kỹ thuật…</p> : null}
        {techApprovalEvent && <p className="mt-4 text-xs text-slate-500">Đã duyệt bởi {techApprovalEvent.actor} · {formatDate(techApprovalEvent.created_at)}</p>}
        <label className="mt-5 block text-sm font-medium text-slate-800">Nhận xét kỹ thuật
          <textarea value={techComment} onChange={(event) => setTechComment(event.target.value)} rows={3} className="mt-2 w-full rounded-lg border border-slate-300 p-3 font-normal outline-none focus:border-blue-500" placeholder="Nêu điều kiện duyệt hoặc nội dung cần sửa" />
        </label>
        <div className="mt-4 flex flex-wrap gap-3">
          <button type="button" disabled={!techPending || techBusy || bid.data.locked} onClick={() => techMutation.mutate()} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">{techMutation.isPending ? 'Đang duyệt…' : 'Duyệt kỹ thuật'}</button>
          <button type="button" disabled={!techPending || techBusy || bid.data.locked || !techComment.trim()} onClick={() => techRejectMutation.mutate()} className="rounded-lg border border-red-300 px-4 py-2 text-sm font-semibold text-red-700 disabled:opacity-40">{techRejectMutation.isPending ? 'Đang gửi…' : 'Yêu cầu sửa'}</button>
        </div>
        {(techMutation.isError || techRejectMutation.isError) && <div className="mt-4"><ErrorState>{(techMutation.error ?? techRejectMutation.error) instanceof ApiError ? (techMutation.error ?? techRejectMutation.error)?.message ?? 'Không thực hiện được quyết định.' : 'Không thực hiện được quyết định.'}</ErrorState></div>}
      </section>

      <section className="rounded-xl border border-amber-200 bg-amber-50/40 p-6 shadow-sm" aria-labelledby="qualification">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div><h3 id="qualification" className="text-lg font-semibold text-slate-900">Bid/No-bid</h3><p className="mt-1 text-sm text-slate-600">Điểm gợi ý chỉ để tham khảo. Người phụ trách phải tự xác nhận quyết định.</p></div>
          {qualification.data?.confirmed_at && <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">Đã xác nhận</span>}
        </div>
        {qualification.isPending && <p role="status" className="mt-4 text-sm text-slate-500">Đang tải tiêu chí…</p>}
        {qualification.isError && <ErrorState>{qualificationError}</ErrorState>}
        {qualification.data && <>
          <div className="mt-4 divide-y divide-amber-200 rounded-lg border border-amber-200 bg-white">
            {qualification.data.criteria.map((criterion) => {
              const suggestion = qualification.data?.suggestions.find((item) => item.criterion_id === criterion.id);
              return <div key={criterion.id} className="grid gap-2 p-4 sm:grid-cols-[1fr_auto_auto] sm:items-center"><div><p className="font-semibold text-slate-800">{criterion.label_vi}</p><p className="text-xs text-slate-500">Trọng số {criterion.weight}%{criterion.note_vi ? ` · ${criterion.note_vi}` : ''}</p></div><span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">{criterion.score == null ? 'Chưa có điểm' : `${criterion.score}/5`}</span><span className="text-xs text-amber-700">{suggestion ? 'Gợi ý từ phân tích' : 'Tham khảo'}</span></div>;
            })}
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
            <label className="text-sm font-medium text-slate-700">Người xác nhận<input value={confirmer || qualification.data.confirmer || ''} onChange={(event) => setConfirmer(event.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 font-normal" placeholder="Tên người xác nhận" /></label>
            <label className="text-sm font-medium text-slate-700">Quyết định<select value={decision} onChange={(event) => setDecision(event.target.value as 'bid' | 'no-bid')} className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 font-normal"><option value="bid">Bid — tiếp tục</option><option value="no-bid">No-bid — không tiếp tục</option></select></label>
            <button type="button" disabled={qualificationMutation.isPending || !confirmer.trim()} onClick={() => qualificationMutation.mutate()} className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">{qualificationMutation.isPending ? 'Đang lưu…' : 'Xác nhận'}</button>
          </div>
        </>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="deal-stage">
        <div><h3 id="deal-stage" className="text-lg font-semibold text-slate-900">Giai đoạn deal</h3><p className="mt-1 text-sm text-slate-500">Lưu giai đoạn hiện tại để theo dõi cơ hội bán hàng.</p></div>
        <div className="mt-4 flex flex-wrap items-end gap-3"><label className="text-sm font-medium text-slate-700">Giai đoạn<select value={stage || bid.data.deal_stage || ''} onChange={(event) => setStage(event.target.value as DealStage)} className="mt-1 block rounded-lg border border-slate-300 bg-white px-3 py-2 font-normal"><option value="">Chọn giai đoạn</option>{Object.entries(DEAL_STAGE_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><button type="button" disabled={!stage || stageMutation.isPending} onClick={() => stageMutation.mutate()} className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">{stageMutation.isPending ? 'Đang lưu…' : 'Lưu giai đoạn'}</button></div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="price-approval">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div><h3 id="price-approval" className="text-lg font-semibold text-slate-900">Duyệt giá</h3><p className="mt-1 text-sm text-slate-500">Chỉ mở sau khi duyệt kỹ thuật thành công.</p></div>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${priceApproved ? 'bg-emerald-100 text-emerald-800' : pricePending ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'}`}>{priceApproved ? 'Đã duyệt' : pricePending ? 'Chờ duyệt' : 'Đang khóa'}</span>
        </div>
        {!techApproved && <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">Cần duyệt kỹ thuật trước khi có thể duyệt giá.</p>}
        {priceError && <div className="mt-4"><ErrorState>Không tải được tóm tắt báo giá. Vui lòng thử lại.</ErrorState></div>}
        <dl className="mt-5 grid gap-3 sm:grid-cols-3">
          <Summary label="Tổng giá" value={quotationTotal} />
          <Summary label="So với ngân sách" value={budgetComparison} />
          <Summary label="Dự phòng / mô hình" value={quotation.data ? `${quotation.data.contingency_percent}% · ${CONTRACT_MODEL_LABELS[quotation.data.contract_model as keyof typeof CONTRACT_MODEL_LABELS] ?? 'Mô hình chưa xác định'}` : 'Chưa có dữ liệu'} />
        </dl>
        {quotation.isPending ? <p role="status" className="mt-4 text-sm text-slate-500">Đang tải tóm tắt giá…</p> : null}
        {priceApprovalEvent && <p className="mt-4 text-xs text-slate-500">Đã duyệt bởi {priceApprovalEvent.actor} · {formatDate(priceApprovalEvent.created_at)}</p>}
        <label className="mt-5 block text-sm font-medium text-slate-800">Nhận xét giá
          <textarea value={priceComment} onChange={(event) => setPriceComment(event.target.value)} rows={3} className="mt-2 w-full rounded-lg border border-slate-300 p-3 font-normal outline-none focus:border-blue-500" placeholder="Bắt buộc khi yêu cầu sửa hoặc từ chối" />
        </label>
        <div className="mt-4 flex flex-wrap gap-3">
          <button type="button" disabled={!pricePending || !techApproved || priceBusy || bid.data.locked} onClick={() => priceMutation.mutate()} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-40">{priceMutation.isPending ? 'Đang duyệt…' : 'Duyệt giá'}</button>
          <button type="button" disabled={!pricePending || !techApproved || priceBusy || bid.data.locked || !priceComment.trim()} onClick={() => priceRejectMutation.mutate()} className="rounded-lg border border-red-300 px-4 py-2 text-sm font-semibold text-red-700 disabled:opacity-40">{priceRejectMutation.isPending ? 'Đang gửi…' : 'Từ chối'}</button>
        </div>
        {(priceMutation.isError || priceRejectMutation.isError || unlock.isError) && <div className="mt-4"><ErrorState>{(priceMutation.error ?? priceRejectMutation.error ?? unlock.error) instanceof ApiError ? (priceMutation.error ?? priceRejectMutation.error ?? unlock.error)?.message ?? 'Không thực hiện được quyết định.' : 'Không thực hiện được quyết định.'}</ErrorState></div>}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="approval-history">
        <div className="flex flex-wrap items-start justify-between gap-3"><div><h3 id="approval-history" className="text-lg font-semibold text-slate-900">Lịch sử &amp; phiên bản</h3><p className="mt-1 text-sm text-slate-500">Các thay đổi và lần duyệt đã ghi nhận cho hồ sơ này.</p></div><span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{bidHistory.length} sự kiện</span></div>
        {history.isPending && <p role="status" className="mt-4 text-sm text-slate-500">Đang tải lịch sử…</p>}
        {history.isError && <div className="mt-4"><ErrorState>Không tải được lịch sử hồ sơ.</ErrorState></div>}
        {!history.isPending && !history.isError && bidHistory.length === 0 && <div className="mt-4"><EmptyState>Chưa có lịch sử duyệt hoặc thay đổi cho hồ sơ này.</EmptyState></div>}
        {bidHistory.length > 0 && <ol className="mt-5 space-y-4 border-l border-slate-200 pl-5">{bidHistory.map((item) => <li key={item.id} className="relative"><span className="absolute -left-[1.65rem] top-1 h-2.5 w-2.5 rounded-full bg-blue-500" /><p className="text-sm font-semibold text-slate-800">{HISTORY_ACTION_LABELS[item.action] ?? 'Thay đổi hồ sơ'}</p><p className="text-xs text-slate-500">{item.actor} · {formatDate(item.created_at)}{item.field_changed ? ` · ${item.field_changed}` : ''}</p>{item.note && <p className="mt-1 text-sm text-slate-600">{item.note}</p>}</li>)}</ol>}
           <div className="mt-5 border-t border-dashed border-slate-200 pt-4"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-semibold text-slate-700">Phiên bản gửi khách</p><p className="mt-1 text-sm text-slate-500">Tạo phiên bản theo chuỗi 1.0 → 1.1 → 2.0.</p></div><button type="button" disabled={versionMutation.isPending} onClick={() => versionMutation.mutate()} className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-40">{versionMutation.isPending ? 'Đang tạo…' : 'Tạo phiên bản'}</button></div><label className="mt-4 block text-sm font-medium text-slate-700">Ghi chú gửi khách<textarea value={sentNote} onChange={(event) => setSentNote(event.target.value)} rows={2} className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 font-normal" placeholder="Ví dụ: Đã gửi qua email ngày..." /></label>{versions.isPending && <p role="status" className="mt-3 text-sm text-slate-500">Đang tải phiên bản…</p>}{versions.isError && <div className="mt-3"><ErrorState>Không tải được danh sách phiên bản.</ErrorState></div>}{versions.data?.length ? <div className="mt-4 space-y-2">{versions.data.map((version) => <div key={version.id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 px-3 py-3"><div><p className="font-semibold text-slate-800">v{version.version} {version.sent && <span className="ml-2 rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800">Đã gửi</span>}</p><p className="text-xs text-slate-500">Tạo ngày {formatDate(version.created_at)} · {version.created_by}{version.sent && version.sent_at ? ` · Gửi ngày ${formatDate(version.sent_at)}` : ''}</p>{version.sent_note && <p className="mt-1 text-sm text-slate-600">Ghi chú: {version.sent_note}</p>}</div>{!version.sent && <button type="button" disabled={sentMutation.isPending} onClick={() => sentMutation.mutate(version.id)} className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 disabled:opacity-40">Đánh dấu đã gửi</button>}</div>)}</div> : !versions.isPending && <p className="mt-3 text-sm text-slate-500">Chưa có phiên bản gửi khách.</p>}</div>
       </section>
      </div>
  );
}

function Message({ text, error = false }: { text: string; error?: boolean }) {
  return <div className="py-8"><p role={error ? 'alert' : 'status'} className={error ? 'rounded-lg bg-red-50 p-4 text-sm text-red-700' : 'text-sm text-slate-500'}>{text}</p></div>;
}
