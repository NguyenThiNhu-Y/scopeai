# Handoff Màn 2 — Frontend

## Boundary

- Chỉ sửa trang `frontend/src/pages/BidsPage.tsx` theo Màn 2.
- Không sửa Màn 10, backend, hoặc các màn khác.
- Giữ `LLM_PROVIDER=mock`; không thêm dữ liệu số/giá giả.

## Đã sửa

- Đổi header thành “Danh sách hồ sơ”, thêm mô tả ngắn và khu tìm/lọc có cấu trúc rõ hơn.
- Bảng có các cột theo prompt: tên dự án, khách hàng, giai đoạn deal, trạng thái, tổng giá, hạn nộp, ngày tạo.
- Giữ các field chưa có trong API ở trạng thái “Chưa có dữ liệu”; không bịa mục tiêu, giai đoạn, tổng giá hoặc ngày tạo.
- Hạn nộp hiển thị số ngày còn lại; ngày quá hạn hoặc còn không quá 7 ngày có màu cảnh báo.
- Badge trạng thái không xuống dòng; table có overflow ngang có chủ đích để giữ cột rõ ở viewport hẹp.
- Row mở hồ sơ bằng click và bàn phím Enter/Space; thêm caption, focus state và nhãn form.
- Giữ loading/error/empty state, debounce search, lọc trạng thái và phân trang.

## Kiểm tra

- `frontend npm run test`: PASS — 1 test file, 6/6 tests.
- Tại thời điểm agent Màn 2 kiểm tra, `frontend npm run build` bị BLOCKED bởi lỗi khi đó ở `frontend/src/pages/SettingsPage.tsx:65` (`Spread types may only be created from object types`); agent Màn 2 không sửa Màn 10 theo boundary.
- Sau khi node Màn 10 hoàn tất, build frontend chung đã PASS theo `docs/ui/handoff_m10_frontend.md`; mismatch thời điểm kiểm tra này được ghi để không nhầm lỗi tạm thời với trạng thái cuối.
- Chưa có screenshot thật/DOM browser evidence trong lượt này; không tạo screenshot giả.

## Blocker

- API `GET /api/bids` hiện chỉ trả `project_name`, `customer_name`, `status`, `submission_deadline`, `customer_language`, `locked`, `updated_at`; chưa có các field cần cho mục tiêu, deal stage, tổng giá/currency và created date.
- API hiện chưa có query filter theo deal stage.
- Chi tiết gap được ghi tại `docs/ui/api_gaps.md`.

## Handoff status

**Frontend Màn 2 hoàn tất với BLOCKED acceptance:** UI và test của phạm vi đã hoàn thành; các cột/filter thiếu dữ liệu vẫn chờ API contract. Build frontend chung sau khi Màn 10 hoàn tất đã PASS; tester vẫn cần kiểm tra Preview bằng evidence thật khi browser khả dụng.
