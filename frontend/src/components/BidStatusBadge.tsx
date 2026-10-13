import { BID_STATUS, type BidStatus } from '../api/types';

const STATUS_STYLES: Record<BidStatus, string> = {
  draft: 'bg-slate-100 text-slate-600 ring-slate-200',
  analyzing: 'bg-blue-50 text-blue-700 ring-blue-200',
  [BID_STATUS.clarification]: 'bg-amber-50 text-amber-700 ring-amber-200',
  [BID_STATUS.technicalApproval]: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  [BID_STATUS.priceApproval]: 'bg-violet-50 text-violet-700 ring-violet-200',
  [BID_STATUS.priceApproved]: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  rejected: 'bg-red-50 text-red-700 ring-red-200',
  error: 'bg-red-50 text-red-700 ring-red-200',
};

/** Nhãn trạng thái hồ sơ tiếng Việt (spec §4.4). */
const STATUS_LABELS: Record<BidStatus, string> = {
  draft: 'Nháp',
  analyzing: 'Đang phân tích',
  [BID_STATUS.clarification]: 'Chờ làm rõ',
  [BID_STATUS.technicalApproval]: 'Chờ duyệt kỹ thuật',
  [BID_STATUS.priceApproval]: 'Chờ duyệt giá',
  [BID_STATUS.priceApproved]: 'Đã duyệt giá',
  rejected: 'Từ chối',
  error: 'Lỗi — có thể chạy lại',
};

/** Badge trạng thái hồ sơ (dùng chung ở danh sách + chi tiết). */
export default function BidStatusBadge({ status }: { status: BidStatus }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ring-inset ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
