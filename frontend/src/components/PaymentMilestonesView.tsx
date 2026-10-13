import type { PaymentMilestone } from '../api/types';
import { formatDate } from '../lib/format';

interface PaymentMilestonesViewProps {
  milestones: PaymentMilestone[];
}

/**
 * Danh sách mốc thanh toán (contract §8.4): tên / % / ngày đến hạn.
 * due_date do backend tính (start_date + due_offset_days) — FE chỉ hiển thị.
 */
export default function PaymentMilestonesView({ milestones }: PaymentMilestonesViewProps) {
  if (milestones.length === 0) {
    return (
      <p className="text-sm text-slate-500">Chưa có mốc thanh toán.</p>
    );
  }

  return (
    <ul className="divide-y divide-slate-100">
      {milestones.map((milestone, index) => (
        <li key={`${milestone.name}-${index}`} className="flex items-center justify-between gap-3 py-2.5">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-slate-800">{milestone.name}</p>
            {milestone.due_date && (
              <p className="text-xs text-slate-500">Đến hạn: {formatDate(milestone.due_date)}</p>
            )}
          </div>
          <span className="shrink-0 rounded-full bg-blue-50 px-2.5 py-0.5 text-sm font-semibold tabular-nums text-blue-700 ring-1 ring-inset ring-blue-200">
            {milestone.percent}%
          </span>
        </li>
      ))}
    </ul>
  );
}