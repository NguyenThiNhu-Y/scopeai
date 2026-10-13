import { useEffect, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiError, chooseSolution, getEffort, getEvaluations } from '../api/client';
import type { SolutionChoice, SolutionDirection } from '../api/types';
import EffortBreakdown from '../components/EffortBreakdown';
import SolutionDirectionSelector from '../components/SolutionDirectionSelector';

const FALLBACK_CHOICE: SolutionChoice = { direction: 'none', reason_vi: '', risks_vi: [], architecture_notes_vi: '' };

export default function SolutionReviewPage() {
  const { id } = useParams<{ id: string }>();
  const bidId = Number(id);
  const navigate = useNavigate();
  const [direction, setDirection] = useState<SolutionDirection>('none');
  const [reason, setReason] = useState('');
  const [saved, setSaved] = useState<SolutionChoice | null>(null);
  const [effortRequested, setEffortRequested] = useState(false);

  const evaluations = useQuery({ queryKey: ['evaluations', bidId], queryFn: () => getEvaluations(bidId), enabled: Number.isFinite(bidId) });
  const effort = useQuery({ queryKey: ['effort', bidId], queryFn: () => getEffort(bidId), enabled: Number.isFinite(bidId) && effortRequested });
  const mutation = useMutation({
    mutationFn: () => chooseSolution(bidId, { direction, reason_vi: reason.trim(), by: 'ai_developer' }),
    onSuccess: (response) => { setSaved({ ...FALLBACK_CHOICE, direction, reason_vi: reason.trim() }); setEffortRequested(true); effort.refetch(); if ((response.warnings ?? []).length) evaluations.refetch(); },
   });

  const current = evaluations.data?.solution_direction;
  useEffect(() => {
    if (current) {
      setDirection(current.direction);
      setReason(current.reason_vi);
    }
  }, [current]);

  if (!Number.isFinite(bidId)) return <ErrorState message="Mã hồ sơ không hợp lệ." onBack={() => navigate('/bids')} />;
  if (evaluations.isPending) return <LoadingState />;
  if (evaluations.isError) return <ErrorState message={evaluations.error instanceof ApiError ? evaluations.error.message : 'Không tải được hướng giải pháp.'} onBack={() => navigate(`/bids/${bidId}`)} />;

  const choice = saved ?? current;
  const warnings = evaluations.data.warnings ?? [];

  return (
    <div className="mx-auto max-w-5xl px-5 py-8 sm:px-8">
      <button type="button" onClick={() => navigate(`/bids/${bidId}`)} className="text-sm font-medium text-blue-600 hover:text-blue-700">← Hồ sơ</button>
      <div className="mt-4 border-b border-slate-200 pb-5"><p className="text-sm font-medium text-blue-600">M3 · Hướng giải pháp</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Rà soát hướng giải pháp</h1><p className="mt-2 text-sm text-slate-600">Chọn một hướng trong danh sách cố định. Effort chỉ hiển thị theo kết quả tính toán.</p></div>

      {warnings.map((warning) => <div key={`${warning.type}-${warning.message}`} role="alert" className="mt-5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{warning.message}</div>)}

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <SolutionDirectionSelector value={direction} onChange={setDirection} disabled={mutation.isPending} />
          <label htmlFor="solution-reason" className="mt-5 block text-sm font-semibold text-slate-900">Lý do chọn hướng <span className="font-normal text-slate-500">(bắt buộc)</span></label>
          <textarea id="solution-reason" value={reason} onChange={(event) => setReason(event.target.value)} rows={5} maxLength={2000} placeholder="Nhập lý do bằng tiếng Việt…" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20" />
          <button type="button" onClick={() => mutation.mutate()} disabled={!reason.trim() || mutation.isPending} className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">{mutation.isPending ? 'Đang lưu…' : 'Lưu hướng giải pháp'}</button>
          {mutation.isError && <p role="alert" className="mt-3 text-sm text-red-700">{mutation.error instanceof ApiError ? mutation.error.message : 'Không lưu được lựa chọn.'}</p>}
          {saved && <p role="status" className="mt-3 text-sm text-emerald-700">Đã lưu hướng giải pháp. Effort đã được tính lại.</p>}
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">Đề xuất hiện tại</h2>
          {choice ? <div className="mt-4 space-y-4 text-sm"><div><p className="text-xs text-slate-500">Lý do</p><p className="mt-1 whitespace-pre-wrap text-slate-700">{choice.reason_vi || 'Chưa có lý do.'}</p></div><div><p className="text-xs text-slate-500">Rủi ro</p>{(choice.risks_vi ?? []).length ? <ul className="mt-1 list-disc space-y-1 pl-5 text-slate-700">{(choice.risks_vi ?? []).map((risk) => <li key={risk}>{risk}</li>)}</ul> : <p className="mt-1 text-slate-500">Chưa có rủi ro được ghi nhận.</p>}</div><div><p className="text-xs text-slate-500">Ghi chú kiến trúc</p><p className="mt-1 whitespace-pre-wrap text-slate-700">{choice.architecture_notes_vi || 'Chưa có ghi chú.'}</p></div></div> : <p className="mt-4 text-sm text-slate-500">Chưa có đề xuất. Hãy chọn hướng và lưu lựa chọn.</p>}
        </section>
      </div>

      {effortRequested && (effort.isPending ? <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-500" role="status">Đang tải effort…</div> : effort.isError ? <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700" role="alert">{effort.error instanceof ApiError ? effort.error.message : 'Không tải được effort.'}<button type="button" onClick={() => effort.refetch()} className="ml-3 font-semibold underline">Thử lại</button></div> : effort.data ? <div className="mt-6"><EffortBreakdown effort={effort.data} /></div> : null)}
    </div>
  );
}

function LoadingState() { return <div className="mx-auto max-w-5xl px-5 py-12 text-sm text-slate-500" role="status">Đang tải hướng giải pháp…</div>; }
function ErrorState({ message, onBack }: { message: string; onBack: () => void }) { return <div className="mx-auto max-w-5xl px-5 py-12"><div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{message}</div><button type="button" onClick={onBack} className="mt-3 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700">Về hồ sơ</button></div>; }
