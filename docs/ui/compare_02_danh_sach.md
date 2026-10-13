# So sánh Màn 2 — Danh sách hồ sơ

## Phạm vi và evidence

- Phạm vi: chỉ `frontend/src/pages/BidsPage.tsx`; không sửa Màn 10 hoặc các màn khác.
- Đã đối chiếu prompt Màn 2 trong `docs/ui/review_ui_tung_man.md` và contract hiện có của `GET /api/bids`.
- Evidence tự động: `frontend npm run test` — PASS, 6/6 tests.
- Chưa có screenshot/DOM runtime thật trong lượt này; không tạo ảnh giả. Preview/browser evidence cần tester chạy lại khi môi trường có Chromium.

## Bảng đối chiếu

| Mục | Kết quả | Mức độ | Ghi chú |
|---|---|---|---|
| Tên dự án + dòng mục tiêu | Đã sửa | TB | Tên dự án hiển thị một dòng; mục tiêu chỉ hiện hướng dẫn vì API list chưa có mục tiêu. |
| Khách hàng | Đã sửa | THẤP | Hiển thị không xuống dòng. |
| Giai đoạn deal | Chưa đủ contract | TB | Có cột và bộ lọc ở trạng thái unavailable, không bịa dữ liệu. |
| Trạng thái | Đã sửa | CAO | Badge có `shrink-0`, `whitespace-nowrap` ở ô bảng, không xuống dòng. |
| Tổng giá có tiền tệ | Chưa đủ contract | CAO | Cột hiển thị unavailable vì list API chưa trả quotation/grand total. |
| Hạn nộp cảnh báo ≤ 7 ngày | Đã sửa | CAO | Hiển thị ngày, số ngày còn lại; ngày quá hạn/≤7 ngày dùng màu cảnh báo. |
| Ngày tạo | Đã sửa một phần | THẤP | Contract list chỉ có `updated_at`; hiển thị ngày cập nhật và không gọi nhầm là ngày tạo. |
| Tìm kiếm | Đã giữ và cải thiện trình bày | THẤP | Search theo tên dự án/khách hàng qua API hiện có. |
| Lọc trạng thái | Đã giữ và cải thiện trình bày | THẤP | Các nhãn hiển thị tiếng Việt. |
| Lọc giai đoạn | Chưa đủ contract | TB | Control bị khóa, giải thích rõ lý do. |
| Bấm dòng mở hồ sơ | Đã sửa | CAO | Row có click, keyboard Enter/Space, focus-visible và role link. |
| Loading/error/empty | Đã giữ | CAO | Không thay đổi luồng trạng thái hiện có. |

## Blocker cần backend/API

`docs/ui/api_gaps.md` ghi thêm gap cho Màn 2: `BidListItem` cần mục tiêu, deal stage, ngày tạo và tổng giá/currency; endpoint list cần nhận filter deal stage. Frontend không suy diễn các giá trị này.
