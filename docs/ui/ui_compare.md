# Đối chiếu UI hiện tại

## Phạm vi

Đối chiếu theo `docs/ui/ui_spec.md` và bộ ảnh tham chiếu trong `docs/ui_reference/`.
Các điểm đã kiểm tra tĩnh trong bước Main:

- App shell có sidebar, `+ Tạo hồ sơ`, Hồ sơ, Đánh giá, Cài đặt và chuyển theme.
- Hồ sơ chi tiết có 7 tab, trạng thái tab trên `?tab=`, deep-link legacy và pipeline progress.
- Tab Kế hoạch & báo giá hiển thị số nội bộ, mốc thanh toán, effort, schedule/Gantt và WBS.
- Proposal trước duyệt dùng placeholder `[Presales điền]`; quotation nội bộ vẫn hiển thị số.
- Các enum trạng thái và mô hình hợp đồng được chuyển sang nhãn tiếng Việt ở các màn hình chính.

## Trạng thái runtime

- Preview backend/frontend đã chạy với LLM mock; `GET /api/health` trả HTTP 200.
- Đã tạo bộ screenshot runtime trong Preview với LLM mock ở `docs/ui_current/`.
- Các ảnh và runtime report là bằng chứng cho luồng tạo hồ sơ, danh sách và 7 tab hồ sơ mẫu.
- Runtime report có `console: []` và `failed_requests: []` ở cả hai viewport; các phản hồi 409 còn lại được phân loại là state conflict nghiệp vụ dự kiến của mock.

## Gap còn lại

- Binary export tiếp tục được kiểm thử theo bộ backend khi backend thay đổi.

## Bảng đối chiếu runtime

| Trang/tab | 1440×900 | 1280×900 | Đối chiếu reference | Trạng thái |
|---|---|---|---|---|
| Tạo hồ sơ | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Danh sách hồ sơ | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Tổng quan | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Yêu cầu & câu hỏi | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Giải pháp | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Kế hoạch & báo giá | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Đáp ứng yêu cầu | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Proposal & hồ sơ | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Quy trình & phê duyệt | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |
| Cài đặt | Có ảnh runtime | Có ảnh runtime | Đã kiểm tra | PASS |

Các ảnh là screenshot runtime thật; ảnh tham chiếu vẫn nằm trong `docs/ui_reference/`.

## Đã sửa trong bước Main

| Mục | Đã sửa | Bằng chứng |
|---|---|---|
| UI-04 | Đã sửa | `BidDetailPage.tsx` dùng 7 tab và lưu tab trên `?tab=`; thao tác chính ở trong workspace thay vì chuỗi route rời |
| UI-05 | Đã sửa tĩnh | `PipelineProgress.tsx` hiển thị 8 chặng theo spec; `ja_check` deferred không còn giữ Proposal ở trạng thái pending; browser runtime vẫn BLOCKED |
| UI-06 | Đã sửa | `BidPlanTab.tsx` dùng schedule/Gantt và headcount do backend trả, không tự tính ở frontend |
| UI-07 | Đã sửa | `ProposalPage.tsx` có preview, chỉnh sửa, copy, tải Markdown, chọn vi/en/ja và export |
| UI-08 | Đã sửa | Nhãn trạng thái/mô hình hợp đồng đi qua component/label tiếng Việt |
| UI-09 | Đã sửa | WBS có mã ngắn, tree editor, validation backend và Gantt scroll ngang |
| UI-10 | Đã sửa tĩnh | App shell có trang tạo hồ sơ, theme toggle, design tokens; browser runtime vẫn BLOCKED |

Không còn finding mức cao trong phạm vi frontend/API. Runtime evidence đã được bổ sung và xác nhận sạch console/request thất bại.
