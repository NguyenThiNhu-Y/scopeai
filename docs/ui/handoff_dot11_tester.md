# Handoff QA Đợt 11

Ngày: 2026-10-12  
Vai trò: tester / QA  
Phạm vi: kiểm tra Preview/API cho frontend Đợt 11; không sửa mã nguồn ứng dụng.

## Đã kiểm tra

- Preview stack chạy với backend và frontend; `GET /api/health` trả HTTP 200, database `ok`, `llm_provider=mock`.
- `GET /api/settings` trả HTTP 200 và đủ 5 key Dot 9: `company`, `templates`, `standard_content`, `case_studies`, `bid_no_bid`.
- Bid/No-bid: tổng trọng số sai bị từ chối HTTP 400; tổng 30/40/30 được chấp nhận; suggestion có nguồn `analysis` và trạng thái `review`, không tự quyết định.
- Deal stage: stage hợp lệ `qualified` được lưu qua HTTP 200.
- Proposal versions: API tạo đúng chuỗi `1.0`, `1.1`, `2.0`; đánh dấu gửi trả `sent_at` và `sent_note`.
- Proposal translation: bản dịch thiếu được tạo qua endpoint `POST /api/bids/80/proposal/translate`, HTTP 200, đủ section `en`.
- Proposal document: metadata trả A4, cover, table of contents và printable.
- Browser/UI: Blocked vì Playwright không tìm thấy Chromium executable. Không tạo screenshot hoặc bằng chứng giả.

## Kết quả

- API contract: đạt cho các mục có thể kiểm tra bằng HTTP.
- UI acceptance: chưa thể kết luận do browser executable không khả dụng.
- Ma trận TC-ID A/B/C đã được bổ sung vào `docs/ui/dot11_check.md`, gồm Pass qua API, Blocked và Đạt một phần theo từng kỳ vọng.
- Automated checks tham chiếu trong `docs/ui/dot11_check.md`: frontend build pass, 14 frontend tests pass, backend full suite pass với cảnh báo deprecation `httpx`/`starlette`.

## Dữ liệu fixture cần lưu ý

- Các kiểm thử version/translation đã dùng bid fixture `80`, tạo version `1.0`, `1.1`, `2.0`, đánh dấu `1.0` gửi với ghi chú `QA Đợt 11`, và thêm translation `en`.
- Deal-stage test đã đặt bid `80` thành `qualified`. API không nhận `null`, nên không thể khôi phục trạng thái rỗng ban đầu bằng API.

## DONE

Đã cập nhật `docs/ui/dot11_check.md`, ghi rõ kết quả thực tế và giới hạn browser. Dừng tại boundary tester, chờ reviewer.
