# QA Compare — Màn 3 Tổng quan

## Phạm vi và môi trường

- Màn kiểm tra: tab `Tổng quan` của hồ sơ mẫu tiếng Nhật.
- Preview: stack `podman-compose.preview.vibeflow.yaml`, backend trả `llm_provider: mock`.
- Kích thước yêu cầu: `1440x900`.
- Hồ sơ quan sát qua API: `顧客管理システム（CRM）構築支援（サンプル・架空）`, ngôn ngữ `ja`, tiền tệ `JPY`, trạng thái `waiting_tech_approval`.
- Ảnh mẫu: `docs/ui_reference/03_tong_quan.png`.
- Ảnh hiện tại trước đó: `docs/ui_v2/03_tong_quan.png`.
- Không tạo ảnh giả.

## Giới hạn bằng chứng

Playwright/Chromium không khởi động được trong sandbox nên không có DOM, ảnh chụp màn hình hoặc kiểm tra tràn chữ bằng trình duyệt thật. Vì vậy bảng dưới đây kết hợp:

- API black-box thật từ Preview.
- Đối chiếu tĩnh với component `frontend/src/pages/BidDetailPage.tsx`.
- Ảnh tham chiếu và ảnh baseline đã có trong workspace.

Các nhận định về pixel, vị trí và chữ tràn được đánh dấu `Chưa xác minh` thay vì suy đoán.

## Bảng so sánh

| ID | Hạng mục | Loại | Kết quả thực tế / đối chiếu | Mức | Trạng thái |
|---|---|---|---|---|---|
| M3-01 | Lưới 2 cột và thẻ có `Chi tiết ›` | Thiếu/lệch | Component có 8 thẻ trong lưới responsive 2 cột ở desktop; mỗi thẻ có nút chuyển tab. | THẤP | Đạt theo code, chưa xác minh pixel |
| M3-02 | Mục tiêu và ràng buộc | Trạng thái | API có mục tiêu tiếng Việt và 2 ràng buộc; UI hiển thị mục tiêu cùng chip ràng buộc. | THẤP | Đạt |
| M3-03 | Hướng giải pháp | Thiếu | API trả hướng RAG và lý do 3 câu; UI hiển thị tên hướng, lý do và tối đa 2 rủi ro. Chưa có huy hiệu độ tin cậy hoặc danh sách hướng bị loại như yêu cầu. | TB | Blocked bởi API/schema; không bịa dữ liệu |
| M3-04 | Khả thi | Thiếu | UI hiện thông báo hướng dẫn, không hiển thị 3 thanh điểm dữ liệu/kỹ thuật/giá trị. API chưa trả cấu trúc điểm khả thi. | TB | Blocked bởi API/schema; không bịa dữ liệu |
| M3-05 | Rủi ro lớn nhất | Thiếu/lệch | API có 4 rủi ro trong `solution_direction.risks_vi`; UI hiển thị tối đa 3 rủi ro dạng danh sách, chưa có cột mức độ màu. | TB | Blocked bởi API/schema; không bịa dữ liệu |
| M3-06 | Effort và kế hoạch | Thiếu | API có effort, WBS endpoint và schedule với 18 task, ngày kết thúc `2027-04-30`; Tổng quan hiện hiển thị midpoint, khoảng theo giai đoạn, số task WBS và ngày kết thúc từ schedule. | TB | Đã sửa trong `frontend/src/pages/BidDetailPage.tsx`; chưa xác minh browser |
| M3-07 | Báo giá sơ bộ | Trạng thái | API trả quotation currency JPY, grand total `8,085,806`, dự phòng và vận hành/tháng; UI có tổng, dự phòng, vận hành/tháng, ngân sách/chênh lệch nếu có. Chưa xác minh bằng browser ở viewport yêu cầu. | THẤP | Đạt theo code/API, chưa xác minh pixel |
| M3-08 | Đáp ứng yêu cầu | Trạng thái | API trả 36 requirement, thống kê 36 `○`; UI ánh xạ nhãn và hiển thị badge đếm. | THẤP | Đạt theo API/code |
| M3-09 | Câu hỏi cần khách xác nhận | Trạng thái | Endpoint questions trả 10 câu hỏi, `rounds_used=2`; UI liệt kê tối đa 3 câu đầu và phần còn lại. Chưa xác minh browser rendering. | THẤP | Đạt theo API/code, chưa xác minh pixel |
| M3-10 | Yêu cầu gốc thu gọn | Thiếu/lệch | UI dùng `details`/`summary` và preview Markdown tối giản cho heading, đoạn văn và danh sách; chưa xác minh pixel/browser. | TB | Đã sửa trong `frontend/src/pages/BidDetailPage.tsx`; chưa xác minh browser |
| M3-11 | Khối thuộc tab Yêu cầu bị lặp | Trạng thái | Tổng quan không render `AttachmentUploader`, `FileParseReview`, `ClarifySection`; các component chỉ nằm trong tab Yêu cầu. | THẤP | Đạt theo code |
| M3-12 | Loading/rỗng/lỗi | Trạng thái | Query chính có loading/error ở màn con; các thẻ Tổng quan có empty state có hướng dẫn, không để một câu “Chưa có…” trơ trọi. | THẤP | Đạt theo code |
| M3-13 | Chữ tràn / bố cục 900px đầu màn | Tràn | Không thể xác minh vì Chromium không khởi động được. Không có ảnh/DOM mới để kết luận pixel. | TB | Blocked bởi môi trường kiểm thử |

## API gaps cần gom xử lý

- `evaluations`/pipeline chưa có cấu trúc điểm khả thi 3 chiều, mức độ rủi ro, độ tin cậy và danh sách hướng bị loại; cần backend hoặc schema output bổ sung trước khi UI có thể hiển thị đúng yêu cầu.
- Quotation, questions, effort, WBS và schedule đều có endpoint và trả dữ liệu trên Preview; M3-06 đã tích hợp schedule vào card Tổng quan. Các gap còn lại là schema evaluation thiếu dữ liệu trình bày nâng cao.

## Bằng chứng kiểm tra API

Các endpoint được gọi qua Preview tại `http://127.0.0.1:3000` cho hồ sơ `92`:

| Endpoint | Kết quả chính |
|---|---|
| `/api/health` | `status=ok`, `llm_provider=mock`, database `ok` |
| `/api/bids/sample/preview` | Mẫu Nhật có 3 file, ngôn ngữ `ja`, tiền tệ `JPY` |
| `/api/bids/92` | `waiting_tech_approval`, pipeline có intake/gap/solution/evaluate/wbs/proposal |
| `/api/bids/92/questions` | 10 câu hỏi, `rounds_used=2` |
| `/api/bids/92/evaluations` | 36 items, 36 đánh giá `○` |
| `/api/bids/92/effort` | Có khoảng effort theo 3 giai đoạn |
| `/api/bids/92/quotation` | JPY, grand total `8,085,806`, có dự phòng |
| `/api/bids/92/schedule` | 18 task, ngày kết thúc `2027-04-30` |

## Kết luận QA

- Preview/backend mock: **PASS có điều kiện**; health, sample preview và hồ sơ Nhật hoạt động qua API.
- Ảnh thật/DOM: **BLOCKED** do Chromium không khởi động trong sandbox; đây là giới hạn bằng chứng, không được coi là lỗi UI đã xác nhận.
- Chất lượng màn: **ĐẠT có blocker dữ liệu**; M3-06 và M3-10 đã được xử lý. M3-03/04/05 vẫn blocked bởi API/schema được ghi trong `docs/ui/api_gaps.md`.
- Frontend-dev đã xử lý các mục TB có thể sửa mà không bịa dữ liệu; không còn mục CAO. M3-13 vẫn là blocker TB do chưa có browser evidence, không phải lỗi đã được xác nhận trong UI.
