import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { ApiError, updateSchedule } from '../api/client';
import type {
  PaymentMilestone,
  ScheduleResponse,
  TeamAllocation,
  WbsRole,
  WorkingCalendar,
} from '../api/types';
import { ROLE_LABELS, WORKING_CALENDAR_LABELS } from '../lib/format';

interface ScheduleFormProps {
  bidId: number;
  /** Lịch hiện tại (nếu có) để điền sẵn form; null khi chưa có lịch. */
  initial: ScheduleResponse | null;
  onSaved: (schedule: ScheduleResponse) => void;
}

const ALL_ROLES = Object.keys(ROLE_LABELS) as WbsRole[];
const CALENDARS = Object.keys(WORKING_CALENDAR_LABELS) as WorkingCalendar[];

interface MilestoneDraft {
  name: string;
  percent: string;
  due_offset_days: string;
}

function emptyAllocation(): Record<WbsRole, string> {
  const record = {} as Record<WbsRole, string>;
  for (const role of ALL_ROLES) record[role] = '0';
  return record;
}

/**
 * Form tham số lịch (spec M4 §4.2, contract §8.4a): ngày bắt đầu, buffer,
 * lịch nghỉ (vn/jp/both), số người mỗi vai trò, mốc thanh toán (tùy chọn).
 * Bấm "Tính lịch" → PUT /schedule → backend tính lại, KHÔNG gọi AI.
 * Lỗi 400 kèm details.missing_roles được hiển thị nổi bật.
 */
export default function ScheduleForm({ bidId, initial, onSaved }: ScheduleFormProps) {
  const [startDate, setStartDate] = useState(initial?.start_date ?? '');
  const [bufferDays, setBufferDays] = useState(String(initial?.buffer_days ?? 0));
  const [workingCalendar, setWorkingCalendar] = useState<WorkingCalendar>(
    initial?.working_calendar ?? 'vn',
  );
  const [allocation, setAllocation] = useState<Record<WbsRole, string>>(() => {
    const record = emptyAllocation();
    if (initial) {
      for (const role of ALL_ROLES) {
        const value = initial.team_allocation[role];
        if (value != null) record[role] = String(value);
      }
    }
    return record;
  });
  const [milestones, setMilestones] = useState<MilestoneDraft[]>(
    initial?.payment_milestones?.map((m) => ({
      name: m.name,
      percent: String(m.percent),
      due_offset_days: String(m.due_offset_days),
    })) ?? [],
  );
  const [clientError, setClientError] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [missingRoles, setMissingRoles] = useState<WbsRole[]>([]);
  const [success, setSuccess] = useState(false);

  const mutation = useMutation({
    mutationFn: (payload: Parameters<typeof updateSchedule>[1]) => updateSchedule(bidId, payload),
    onSuccess: (data) => {
      setServerError(null);
      setMissingRoles([]);
      setSuccess(true);
      onSaved(data);
    },
    onError: (error: unknown) => {
      setSuccess(false);
      if (error instanceof ApiError) {
        setServerError(error.message);
        const details = error.details;
        if (details && Array.isArray(details.missing_roles)) {
          setMissingRoles(details.missing_roles as WbsRole[]);
        }
      } else {
        setServerError('Không tính được lịch. Vui lòng thử lại.');
      }
    },
  });

  function setRoleCount(role: WbsRole, value: string) {
    setAllocation((prev) => ({ ...prev, [role]: value }));
  }

  function updateMilestone(index: number, patch: Partial<MilestoneDraft>) {
    setMilestones((prev) => prev.map((m, i) => (i === index ? { ...m, ...patch } : m)));
  }

  function handleSubmit() {
    setClientError(null);
    setServerError(null);
    setMissingRoles([]);
    setSuccess(false);

    if (!startDate) {
      setClientError('Vui lòng nhập ngày bắt đầu.');
      return;
    }
    const buffer = Number(bufferDays);
    if (!Number.isFinite(buffer) || buffer < 0) {
      setClientError('Buffer phải là số nguyên ≥ 0.');
      return;
    }

    const teamAllocation: TeamAllocation = {};
    for (const role of ALL_ROLES) {
      const value = Number(allocation[role]);
      if (!Number.isInteger(value) || value < 0) {
        setClientError(`Số người của vai trò ${ROLE_LABELS[role]} phải là số nguyên ≥ 0.`);
        return;
      }
      teamAllocation[role] = value;
    }

    const payload: Parameters<typeof updateSchedule>[1] = {
      start_date: startDate,
      buffer_days: buffer,
      working_calendar: workingCalendar,
      team_allocation: teamAllocation,
      by: 'ai_developer',
    };

    if (milestones.length > 0) {
      const parsed: PaymentMilestone[] = [];
      for (const m of milestones) {
        const percent = Number(m.percent);
        const offset = Number(m.due_offset_days);
        if (!m.name.trim()) {
          setClientError('Mốc thanh toán cần có tên.');
          return;
        }
        if (!Number.isFinite(percent) || percent < 0 || percent > 100) {
          setClientError(`Phần trăm mốc "${m.name.trim()}" phải trong khoảng 0–100.`);
          return;
        }
        if (!Number.isInteger(offset) || offset < 0) {
          setClientError(`Số ngày đến hạn của mốc "${m.name.trim()}" phải là số nguyên ≥ 0.`);
          return;
        }
        parsed.push({ name: m.name.trim(), percent, due_offset_days: offset });
      }
      payload.payment_milestones = parsed;
    }

    mutation.mutate(payload);
  }

  const inputClass =
    'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20';

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-label="Tham số lịch">
      <h2 className="text-base font-semibold text-slate-900">Tham số lịch</h2>
      <p className="mt-1 text-xs text-slate-500">
        Lưu tham số → backend tính lại lịch bằng code, không gọi AI.
      </p>

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <label className="block text-xs font-medium text-slate-600">
          Ngày bắt đầu dự án *
          <input
            type="date"
            value={startDate}
            onChange={(event) => setStartDate(event.target.value)}
            className={`${inputClass} mt-1`}
          />
        </label>
        <label className="block text-xs font-medium text-slate-600">
          Buffer (ngày)
          <input
            type="number"
            min={0}
            step={1}
            value={bufferDays}
            onChange={(event) => setBufferDays(event.target.value)}
            className={`${inputClass} mt-1 tabular-nums`}
          />
        </label>
        <label className="block text-xs font-medium text-slate-600">
          Lịch nghỉ
          <select
            value={workingCalendar}
            onChange={(event) => setWorkingCalendar(event.target.value as WorkingCalendar)}
            className={`${inputClass} mt-1`}
          >
            {CALENDARS.map((calendar) => (
              <option key={calendar} value={calendar}>
                {WORKING_CALENDAR_LABELS[calendar]}
              </option>
            ))}
          </select>
        </label>
      </div>

      <fieldset className="mt-4">
        <legend className="text-xs font-medium text-slate-600">
          Số người mỗi vai trò (headcount) — mọi vai trò trong WBS cần ≥ 1
        </legend>
        <div className="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {ALL_ROLES.map((role) => (
            <label key={role} className="block text-xs font-medium text-slate-600">
              {ROLE_LABELS[role]}
              <input
                type="number"
                min={0}
                step={1}
                value={allocation[role]}
                onChange={(event) => setRoleCount(role, event.target.value)}
                className={`${inputClass} mt-1 tabular-nums`}
              />
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset className="mt-4">
        <legend className="text-xs font-medium text-slate-600">
          Mốc thanh toán (tùy chọn — để trống dùng mặc định)
        </legend>
        {milestones.length === 0 ? (
          <p className="mt-1 text-xs text-slate-400">Chưa có mốc nào. Bấm "Thêm mốc" để tạo.</p>
        ) : (
          <div className="mt-2 space-y-2">
            {milestones.map((milestone, index) => (
              <div key={index} className="flex flex-wrap items-end gap-2">
                <label className="block min-w-40 flex-1 text-xs font-medium text-slate-600">
                  Tên mốc
                  <input
                    value={milestone.name}
                    onChange={(event) => updateMilestone(index, { name: event.target.value })}
                    placeholder="VD: Kickoff"
                    className={`${inputClass} mt-1`}
                  />
                </label>
                <label className="block w-24 text-xs font-medium text-slate-600">
                  Phần trăm (%)
                  <input
                    type="number"
                    min={0}
                    max={100}
                    step={1}
                    value={milestone.percent}
                    onChange={(event) => updateMilestone(index, { percent: event.target.value })}
                    className={`${inputClass} mt-1 tabular-nums`}
                  />
                </label>
                <label className="block w-32 text-xs font-medium text-slate-600">
                  Đến hạn sau (ngày)
                  <input
                    type="number"
                    min={0}
                    step={1}
                    value={milestone.due_offset_days}
                    onChange={(event) =>
                      updateMilestone(index, { due_offset_days: event.target.value })
                    }
                    className={`${inputClass} mt-1 tabular-nums`}
                  />
                </label>
                <button
                  type="button"
                  onClick={() => setMilestones((prev) => prev.filter((_, i) => i !== index))}
                  className="rounded-lg border border-red-200 px-3 py-2 text-xs font-medium text-red-600 hover:bg-red-50"
                >
                  Xóa
                </button>
              </div>
            ))}
          </div>
        )}
        <button
          type="button"
          onClick={() =>
            setMilestones((prev) => [...prev, { name: '', percent: '', due_offset_days: '0' }])
          }
          className="mt-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-100"
        >
          ＋ Thêm mốc
        </button>
      </fieldset>

      {missingRoles.length > 0 && (
        <div role="alert" className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <p className="text-sm font-medium text-red-800">
            Thiếu số người cho vai trò:{' '}
            {missingRoles.map((role) => ROLE_LABELS[role] ?? role).join(', ')}
          </p>
          <p className="mt-1 text-xs text-red-700">
            Mọi vai trò xuất hiện trong WBS phải có ít nhất 1 người. Hãy bổ sung rồi tính lại.
          </p>
        </div>
      )}

      {clientError && (
        <p role="alert" className="mt-3 text-sm text-red-700">
          {clientError}
        </p>
      )}
      {serverError && !missingRoles.length && (
        <p role="alert" className="mt-3 text-sm text-red-700">
          {serverError}
        </p>
      )}
      {success && (
        <p role="status" className="mt-3 text-sm text-emerald-700">
          Đã lưu tham số và tính lại lịch.
        </p>
      )}

      <button
        type="button"
        onClick={handleSubmit}
        disabled={mutation.isPending}
        className="mt-4 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {mutation.isPending ? 'Đang tính lịch…' : 'Tính lịch'}
      </button>
    </section>
  );
}
