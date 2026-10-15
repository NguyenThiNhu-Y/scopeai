import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getBid,
  getConfidence,
  getEvaluations,
  getQuotation,
  getSchedule,
  getWbs,
  updateQuotation,
  updateSchedule,
  updateWbs,
} from '../api/client';
import type {
  ConfidenceOut,
  ContractModel,
  ScheduleResponse,
  ScheduleUpdateRequest,
  TeamAllocation,
  WbsChange,
  WbsRole,
  QuotationResponse,
} from '../api/types';
import WbsTreeTable from './WbsTreeTable';
import GanttChart from './GanttChart';
import AnalogCompare from './AnalogCompare';
import { CONTRACT_MODEL_LABELS, ROLE_LABELS, formatAmount, formatDate, formatManDay, WORKING_CALENDAR_LABELS } from '../lib/format';

const ROLES = Object.keys(ROLE_LABELS) as WbsRole[];
const field = 'rounded-lg border border-[var(--line)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--ink)] outline-none focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand)]/20 disabled:opacity-50';

/** Tab Kế hoạch & báo giá: số liệu và lịch luôn lấy từ backend; FE chỉ điều khiển form. */
export default function BidPlanTab({ bidId, onNavigateTab }: { bidId: number; onNavigateTab?: (tab: string) => void }) {
  const queryClient = useQueryClient();
  const bid = useQuery({ queryKey: ['bid', bidId], queryFn: () => getBid(bidId), retry: false });
  // E.2: chỉ gọi quotation/schedule/wbs khi pipeline đã qua bước tương ứng
  // (tránh lỗi 409 trên console khi hồ sơ còn draft/đang phân tích/chờ làm rõ).
  const advanced = Boolean(bid.data) && !['draft', 'analyzing', 'waiting_clarification'].includes(bid.data?.status ?? '');
  const quotation = useQuery({ queryKey: ['quotation', bidId], queryFn: () => getQuotation(bidId), enabled: advanced, retry: false });
  const schedule = useQuery({ queryKey: ['schedule', bidId], queryFn: () => getSchedule(bidId), enabled: advanced, retry: false });
  const wbs = useQuery({ queryKey: ['wbs', bidId], queryFn: () => getWbs(bidId), enabled: advanced, retry: false });
  // Đợt 13: độ tin cậy (thẻ/analog/truy vết) + danh sách requirement để map mã → nội dung.
  const confidence = useQuery({ queryKey: ['confidence', bidId], queryFn: () => getConfidence(bidId), enabled: advanced, retry: false });
  const evaluations = useQuery({ queryKey: ['evaluations', bidId], queryFn: () => getEvaluations(bidId), enabled: advanced, retry: false });

  const [wbsError, setWbsError] = React.useState<string | null>(null);
  const [scheduleError, setScheduleError] = React.useState<string | null>(null);
  const [savedSchedule, setSavedSchedule] = React.useState<ScheduleResponse | null>(null);
  const [staff, setStaff] = React.useState<TeamAllocation>({});

  const locked = bid.data?.locked === true || bid.data?.status === 'price_approved';
  const currentSchedule = savedSchedule ?? schedule.data;
  React.useEffect(() => {
    if (currentSchedule) setStaff(currentSchedule.team_allocation ?? {});
  }, [currentSchedule?.start_date]);

  const saveWbs = useMutation({
    mutationFn: (changes: WbsChange[]) => updateWbs(bidId, changes),
    onSuccess: (data) => {
      queryClient.setQueryData(['wbs', bidId], data);
      if (data.recalculated?.schedule) {
        setSavedSchedule(data.recalculated.schedule);
        queryClient.setQueryData(['schedule', bidId], data.recalculated.schedule);
      }
      // WBS đổi → độ tin cậy (wbs_checks, traceability, analog) đổi → tải lại thẻ.
      void queryClient.invalidateQueries({ queryKey: ['confidence', bidId] });
      setWbsError(null);
    },
    onError: () => setWbsError('Không lưu được WBS. Kiểm tra dữ liệu rồi thử lại.'),
  });
  const saveSchedule = useMutation({
    mutationFn: (payload: ScheduleUpdateRequest) => updateSchedule(bidId, payload),
    onSuccess: (data) => {
      setSavedSchedule(data);
      queryClient.setQueryData(['schedule', bidId], data);
      // Lịch đổi → tín hiệu schedule_checks đổi → tải lại độ tin cậy.
      void queryClient.invalidateQueries({ queryKey: ['confidence', bidId] });
      setScheduleError(null);
    },
    onError: () => setScheduleError('Không tính lại được lịch. Kiểm tra tham số rồi thử lại.'),
  });
  const saveQuotation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => updateQuotation(bidId, payload),
    onSuccess: (data) => queryClient.setQueryData(['quotation', bidId], data),
  });

  const saveStaffAndSchedule = (draft: ScheduleDraft) => {
    if (!currentSchedule) return;
    saveSchedule.mutate({
      start_date: draft.startDate,
      buffer_days: draft.bufferDays,
      working_calendar: draft.calendar,
      team_allocation: staff,
      payment_milestones: currentSchedule.payment_milestones,
      go_no_go_gap_working_days: draft.goNoGoGap,
      gantt_break_interval: 'week',
      by: 'presales',
    });
  };

  const handleWbsSave = (changes: WbsChange[]) => {
    saveWbs.mutate(changes);
  };

  // Map mã requirement → nội dung để hiện chip/hover và danh sách chưa truy vết.
  const requirementContents = Object.fromEntries(
    (evaluations.data?.items ?? []).map((item) => [item.req_code, item.content]),
  );
  const availableRequirementCodes = (evaluations.data?.items ?? []).map((item) => item.req_code);

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm" aria-label="Kế hoạch nhân sự và lịch">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div><p className="text-xs font-semibold uppercase tracking-wide text-[var(--brand)]">Kế hoạch triển khai</p><h2 className="mt-1 text-xl font-semibold text-[var(--ink)]">Nhân sự, effort và lịch</h2><p className="mt-1 text-sm text-[var(--muted)]">Chỉnh sửa tham số rồi lưu một lần; ngày và tổng effort được backend tính bằng code.</p></div>
          {currentSchedule && <div className="text-right text-sm text-[var(--muted)]"><div>{formatDate(currentSchedule.start_date)} → {formatDate(currentSchedule.end_date)}</div><strong className="text-lg text-[var(--ink)]">{formatManDay(Object.values(currentSchedule.by_role).reduce((sum, item) => sum + item.man_day, 0))} man-day</strong></div>}
        </div>
        {currentSchedule ? <><div className="mt-4 flex justify-end"><button type="button" disabled={locked || saveSchedule.isPending} onClick={() => setStaff(Object.fromEntries(ROLES.map((role) => [role, currentSchedule.by_role[role]?.headcount ?? staff[role] ?? 0])))} className="rounded-lg border border-[var(--line)] px-3 py-2 text-xs font-semibold text-[var(--brand)] disabled:opacity-50">Gợi ý theo effort</button></div><ScheduleControls schedule={currentSchedule} staff={staff} setStaff={setStaff} disabled={locked || saveSchedule.isPending} error={scheduleError} onSave={saveStaffAndSchedule} /></> : <Empty label="Chưa có master schedule. Chạy pipeline để tạo lịch." pending={schedule.isPending} />}
        {currentSchedule && <div className="mt-4"><GanttChart tasks={currentSchedule.tasks} startDate={currentSchedule.start_date} endDate={currentSchedule.end_date} taskNames={Object.fromEntries((wbs.data?.items ?? []).map((item) => [item.task_code, item.name_vi]))} breakStart={currentSchedule.go_no_go_start} breakEnd={currentSchedule.go_no_go_end} milestones={[...(currentSchedule.customer_mvp_start ? [{ label: 'MVP khách', date: currentSchedule.customer_mvp_start }] : []), ...(currentSchedule.customer_production_start ? [{ label: 'Production khách', date: currentSchedule.customer_production_start }] : [])]} /></div>}
      </section>

      <AnalogCompare bidId={bidId} enabled={advanced} wbsByPhase={wbs.data?.totals.by_phase} />

      <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm" aria-label="Cấu trúc công việc">
        <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-wide text-[var(--brand)]">WBS</p><h2 className="mt-1 text-xl font-semibold text-[var(--ink)]">Cấu trúc công việc</h2></div></div>
        {wbs.data ? <><div className="mt-3 flex items-center justify-between text-sm text-[var(--muted)]"><span>Tổng backend tính: <strong className="text-[var(--ink)]">{wbs.data.totals.man_day} man-day</strong></span><span>{wbs.data.check.within_20pct ? 'Trong khoảng tham chiếu' : 'Cần rà soát effort'}</span></div>{wbsError && <p role="alert" className="mt-3 text-sm text-[var(--danger)]">{wbsError}</p>}<div className="mt-4"><WbsTreeTable items={wbs.data.items} saving={saveWbs.isPending} onSaveChanges={handleWbsSave} requirementContents={requirementContents} availableRequirementCodes={availableRequirementCodes} /></div><TraceabilityLine confidence={confidence.data} requirementContents={requirementContents} onNavigateCoverage={() => onNavigateTab?.('coverage')} /><p className="mt-3 text-xs text-[var(--muted)]">Sửa trực tiếp trong dòng; dùng ＋ Thêm task ở cuối mỗi nhóm để thêm task con, ＋ Thêm nhóm cấp 1 để tạo nhóm mới. Lưu xong tổng man-day và lịch tự tính lại.</p></> : <Empty label="Chưa có danh sách công việc." pending={wbs.isPending} />}
      </section>

      <QuotationSection quotation={quotation.data} locked={locked} pending={saveQuotation.isPending} onSave={(payload) => saveQuotation.mutate(payload)} />
    </div>
  );
}

interface ScheduleDraft { startDate: string; bufferDays: number; calendar: ScheduleUpdateRequest['working_calendar']; goNoGoGap: number; }

/**
 * Dòng "Truy vết: x/y requirement có task" + danh sách requirement chưa có task
 * (thiet_ke_danh_gia.md §7). Dữ liệu từ tín hiệu traceability của confidence —
 * bấm vào mã chưa truy vết chuyển sang tab Đáp ứng.
 */
function TraceabilityLine({
  confidence,
  requirementContents,
  onNavigateCoverage,
}: {
  confidence?: ConfidenceOut;
  requirementContents: Record<string, string>;
  onNavigateCoverage: () => void;
}) {
  const trace = confidence?.signals.find((signal) => signal.key === 'traceability');
  const data = trace?.data as { covered?: number; total?: number; uncovered?: string[] } | undefined;
  if (!trace || !data || !data.total) return null;
  const uncovered = data.uncovered ?? [];
  return (
    <div className="mt-3 rounded-lg border border-[var(--line)] bg-[var(--page)] p-3 text-sm">
      <p className="text-[var(--ink)]">
        Truy vết: <strong className="font-semibold">{data.covered}/{data.total}</strong> requirement có task
      </p>
      {uncovered.length > 0 && (
        <div className="mt-2">
          <p className="text-xs text-[var(--muted)]">Requirement chưa có task:</p>
          <ul className="mt-1 space-y-1">
            {uncovered.map((code) => (
              <li key={code}>
                <button type="button" onClick={onNavigateCoverage} className="font-mono text-xs font-semibold text-[var(--brand)] hover:underline">
                  {code}
                </button>
                <span className="ml-2 text-xs text-[var(--muted)]">{requirementContents[code] ?? ''}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ScheduleControls({ schedule, staff, setStaff, disabled, error, onSave }: { schedule: ScheduleResponse; staff: TeamAllocation; setStaff: React.Dispatch<React.SetStateAction<TeamAllocation>>; disabled: boolean; error: string | null; onSave: (draft: ScheduleDraft) => void }) {
  const [startDate, setStartDate] = React.useState(schedule.start_date);
  const [bufferDays, setBufferDays] = React.useState(String(schedule.buffer_days));
  const [calendar, setCalendar] = React.useState<ScheduleDraft['calendar']>(schedule.working_calendar);
  const [gap, setGap] = React.useState(String(schedule.go_no_go_gap_working_days ?? 10));
  return <div className="mt-5 space-y-4"><div><h3 className="text-sm font-semibold text-[var(--ink)]">Phân bổ nhân sự theo vai trò</h3><p className="mt-1 text-xs text-[var(--muted)]">Backend dùng phân bổ này để tính thời lượng. WBS vẫn là nguồn effort; hợp đồng hiện chưa có phân bổ riêng theo phase.</p><div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-8">{ROLES.map((role) => <label key={role} className="text-xs text-[var(--muted)]">{ROLE_LABELS[role]}<input aria-label={`Số người ${ROLE_LABELS[role]}`} type="number" min={0} step={1} value={staff[role] ?? 0} disabled={disabled} onChange={(event) => setStaff((prev) => ({ ...prev, [role]: Math.max(0, Number(event.target.value)) }))} className={`${field} mt-1 w-full tabular-nums`} /></label>)}</div></div><div className="grid gap-3 sm:grid-cols-4"><label className="text-xs text-[var(--muted)]">Ngày bắt đầu<input type="date" value={startDate} disabled={disabled} onChange={(event) => setStartDate(event.target.value)} className={`${field} mt-1 w-full`} /></label><label className="text-xs text-[var(--muted)]">Buffer (ngày)<input type="number" min={0} value={bufferDays} disabled={disabled} onChange={(event) => setBufferDays(event.target.value)} className={`${field} mt-1 w-full`} /></label><label className="text-xs text-[var(--muted)]">Lịch nghỉ<select value={calendar} disabled={disabled} onChange={(event) => setCalendar(event.target.value as ScheduleDraft['calendar'])} className={`${field} mt-1 w-full`}>{Object.entries(WORKING_CALENDAR_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label><label className="text-xs text-[var(--muted)]">Khoảng go/no-go (ngày LV)<input type="number" min={0} value={gap} disabled={disabled} onChange={(event) => setGap(event.target.value)} className={`${field} mt-1 w-full`} /></label></div><div className="grid gap-2 text-xs text-[var(--muted)] sm:grid-cols-2"><span>MVP theo kế hoạch khách: {schedule.customer_mvp_start ? formatDate(schedule.customer_mvp_start) : 'Chưa có dữ liệu'}</span><span>Production theo kế hoạch khách: {schedule.customer_production_start ? formatDate(schedule.customer_production_start) : 'Chưa có dữ liệu'}</span></div>{error && <p role="alert" className="text-sm text-[var(--danger)]">{error}</p>}<div className="flex flex-wrap items-center gap-3"><button type="button" disabled={disabled} onClick={() => onSave({ startDate, bufferDays: Number(bufferDays), calendar, goNoGoGap: Number(gap) })} className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{disabled ? 'Đang tính lại…' : 'Lưu & tính lại lịch'}</button>{schedule.go_no_go_start && schedule.go_no_go_end && <span className="text-xs text-[var(--muted)]">Khoảng nghỉ: {formatDate(schedule.go_no_go_start)} → {formatDate(schedule.go_no_go_end)}</span>}</div></div>;
}

function QuotationSection({ quotation, locked, pending, onSave }: { quotation?: QuotationResponse; locked: boolean; pending: boolean; onSave: (payload: Record<string, unknown>) => void }) {
  const [model, setModel] = React.useState<ContractModel>(quotation?.contract_model ?? 'fixed_price');
  const [contingency, setContingency] = React.useState(String(quotation?.contingency_percent ?? 0));
  // Đồng bộ state với dữ liệu đã lưu khi quotation tải xong (trước đây luôn giữ 0).
  React.useEffect(() => {
    if (quotation) {
      setModel(quotation.contract_model);
      setContingency(String(quotation.contingency_percent ?? 0));
    }
  }, [quotation?.contract_model, quotation?.contingency_percent]);
  if (!quotation) return <Empty label="Báo giá sẽ hiển thị sau khi hệ thống tính xong effort và đơn giá chuẩn." pending={pending} />;
  const taxAmount = quotation.totals.tax_amount ?? 0;
  const taxPercent = quotation.totals.tax_percent ?? 0;
  return <section className="rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 shadow-sm" aria-label="Chi tiết báo giá"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-semibold uppercase tracking-wide text-[var(--brand)]">Báo giá nội bộ</p><h2 className="mt-1 text-xl font-semibold text-[var(--ink)]">Chi tiết báo giá</h2></div><p className="text-2xl font-bold tabular-nums text-[var(--ink)]">{formatAmount(quotation.totals.grand_total, quotation.currency)}</p></div><div className="mt-4 grid gap-3 sm:grid-cols-3"><label className="text-xs text-[var(--muted)]">Mô hình<select disabled={locked} value={model} onChange={(event) => setModel(event.target.value as ContractModel)} className={`${field} mt-1 w-full`}>{Object.entries(CONTRACT_MODEL_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label><label className="text-xs text-[var(--muted)]">Dự phòng (%)<input disabled={locked} type="number" min={0} max={100} value={contingency} onChange={(event) => setContingency(event.target.value)} className={`${field} mt-1 w-full`} /></label><div className="flex items-end"><button type="button" disabled={locked || pending} onClick={() => onSave({ contract_model: model, contingency_percent: Number(contingency) })} className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{pending ? 'Đang lưu…' : 'Lưu báo giá'}</button></div></div><div className="mt-4 grid gap-4 sm:grid-cols-3"><Metric label="Tạm tính (trước dự phòng)" value={formatAmount(quotation.totals.subtotal, quotation.currency)} /><Metric label="Dự phòng" value={formatAmount(quotation.totals.contingency_amount, quotation.currency)} /><Metric label="Tổng chưa gồm thuế" value={formatAmount(quotation.totals.tax_excluded, quotation.currency)} /></div><p className="mt-3 text-xs text-[var(--muted)]">{quotation.tax_mode === 'tax_included' ? `Đã gồm thuế ${taxPercent > 0 ? `${taxPercent}%` : ''} trong tổng giá.` : `Thuế ${taxPercent > 0 ? `${taxPercent}%` : ''}: ${formatAmount(taxAmount, quotation.currency)} · chưa gồm trong tổng giá.`}</p>{quotation.budget && <div className="mt-4 rounded-lg border border-[var(--line)] p-3 text-sm"><h3 className="font-semibold text-[var(--ink)]">So với ngân sách khách</h3><div className="mt-2 grid gap-1 sm:grid-cols-2"><span>Ngân sách: {formatAmount(quotation.budget.amount, quotation.budget.currency)}</span><span>Giá của mình: {formatAmount(quotation.totals.grand_total, quotation.currency)}</span><span>Chênh lệch: {quotation.budget.difference == null ? 'Chưa đủ dữ liệu so sánh' : formatAmount(quotation.budget.difference, quotation.currency)}</span><span>Gợi ý điều chỉnh: {quotation.budget.adjustment_suggestion_percent == null ? 'Chưa đủ dữ liệu' : (quotation.budget.adjustment_suggestion_percent >= 0 ? `tăng ${Math.abs(quotation.budget.adjustment_suggestion_percent)}%` : `giảm ${Math.abs(quotation.budget.adjustment_suggestion_percent)}%`)}</span></div>{quotation.budget.difference_percent != null && Math.abs(quotation.budget.difference_percent) > 30 && <p role="alert" className="mt-2 rounded bg-amber-50 px-2 py-1 text-amber-800">Giá lệch ngân sách quá ±30%: kiểm tra lại phạm vi/effort.</p>}</div>}<details className="mt-5"><summary className="cursor-pointer text-sm font-semibold text-[var(--brand)]">Chi tiết báo giá theo vai trò và thanh toán</summary><div className="mt-3 grid gap-5 lg:grid-cols-2"><RolePriceTable quotation={quotation} /><PaymentTable quotation={quotation} /></div>{quotation.totals.odc_fte_months != null && <p className="mt-2 text-xs text-[var(--muted)]">Tổng quy đổi ODC: {quotation.totals.odc_fte_months} FTE-tháng.</p>}</details></section>;
}
function RolePriceTable({ quotation }: { quotation: QuotationResponse }) { return <div className="overflow-x-auto"><table className="w-full min-w-[420px] text-sm"><caption className="mb-2 text-left font-semibold text-[var(--ink)]">Theo vai trò</caption><thead><tr className="border-b border-[var(--line)] text-left text-xs text-[var(--muted)]"><th className="py-2">Vai trò</th><th className="py-2 text-right">Man-day</th><th className="py-2 text-right">Thành tiền</th></tr></thead><tbody>{Object.entries(quotation.totals.by_role).map(([role, item]) => <tr key={role} className="border-b border-[var(--line)]"><td className="py-2">{ROLE_LABELS[role as WbsRole] ?? role}</td><td className="py-2 text-right tabular-nums">{item.man_day}</td><td className="py-2 text-right tabular-nums">{formatAmount(item.amount, quotation.currency)}</td></tr>)}</tbody></table></div>; }
function PaymentTable({ quotation }: { quotation: QuotationResponse }) { return <div className="overflow-x-auto"><table className="w-full min-w-[420px] text-sm"><caption className="mb-2 text-left font-semibold text-[var(--ink)]">Kế hoạch thanh toán</caption><thead><tr className="border-b border-[var(--line)] text-left text-xs text-[var(--muted)]"><th className="py-2">Kỳ</th><th className="py-2 text-right">Tỷ lệ</th><th className="py-2 text-right">Số tiền</th></tr></thead><tbody>{(quotation.totals.payment_plan ?? quotation.payment_milestones).map((payment) => <tr key={payment.name} className="border-b border-[var(--line)]"><td className="py-2">{payment.name}</td><td className="py-2 text-right">{payment.percent}%</td><td className="py-2 text-right tabular-nums">{'amount' in payment && payment.amount != null ? formatAmount(payment.amount, quotation.currency) : '—'}</td></tr>)}</tbody></table></div>; }
function Metric({ label, value }: { label: string; value: string }) { return <div className="rounded-lg border border-[var(--line)] px-3 py-2"><dt className="text-xs text-[var(--muted)]">{label}</dt><dd className="mt-1 text-sm font-semibold text-[var(--ink)]">{value}</dd></div>; }
function Empty({ label, pending }: { label: string; pending: boolean }) { return <p role={pending ? 'status' : 'note'} className="rounded-lg border border-dashed border-[var(--line)] bg-[var(--page)] p-4 text-sm text-[var(--muted)]">{pending ? 'Đang tải dữ liệu…' : label}</p>; }
