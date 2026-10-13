interface PriceGateNoticeProps { approved: boolean; }

export default function PriceGateNotice({ approved }: PriceGateNoticeProps) {
  return approved ? null : (
    <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900" role="status">
      <strong>Cổng duyệt giá:</strong> báo giá chưa được manager duyệt. Khách hàng sẽ thấy <span className="font-mono">[Presales điền]</span> thay cho số tiền.
    </div>
  );
}
