# QA Compare — Màn 4 Yêu cầu & câu hỏi

Ngày kiểm tra: 2026-10-11  
Môi trường: Preview qua `podman-compose.preview.vibeflow.yaml`, LLM mock, viewport mục tiêu `1440x900`  
Vai trò: QA ban đầu; vòng frontend-dev sau đó xử lý các điểm frontend có thể sửa.

## Kết luận

**BLOCKED — chưa thể kết luận đạt bằng browser.** Preview backend/frontend đã khởi động, nhưng browser automation không thể chạy vì Chromium executable không có trong môi trường. Vì vậy không có screenshot thật trong `docs/ui_v3/` và không đánh dấu các kiểm tra giao diện là PASS dựa trên suy đoán.

Sau vòng sửa frontend-dev, các điểm có thể xử lý không cần contract mới đã được cập nhật: số thứ tự câu hỏi liên tục qua các vòng, nhãn `Vì sao hỏi` và trạng thái câu trả lời rõ hơn, file đính kèm hiển thị nhận diện/mapping khi backend trả về, và nút Q&A disabled có lý do cụ thể. Các mục cần `topic`, `blocking`, số requirement trong danh sách file hoặc endpoint xuất/nhập Q&A vẫn là blocker/API gap, không tự tạo dữ liệu.

## Bằng chứng môi trường

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Backend Preview | Có thể khởi động | `podman-compose ... ps`: backend `Up (starting)`; log có `Application startup complete` và Uvicorn trên `0.0.0.0:8000` |
| Frontend Preview | Có thể khởi động | `podman-compose ... ps`: frontend `Up`, publish `0.0.0.0:3000->3000/tcp` |
| API health | Có phản hồi | Backend log: `GET /api/health` trả `200 OK` |
| Sample preview | Có endpoint nhưng request có `sample_key` lỗi | Backend log: `GET /api/bids/sample/preview?sample_key=[REDACTED:env-sample_key]` trả `400 Bad Request` |
| Chromium/Playwright | Blocked | `browserType.launch`: executable Chromium không tồn tại tại cache Playwright |
| Screenshot thật | Chưa có | Không tạo ảnh giả; `docs/ui_v3/` chưa có evidence của Màn 4 |

## Ma trận kiểm tra

| TC-ID | Kiểm tra | Kỳ vọng theo prompt | Kết quả | Mức độ | Đã sửa | Evidence / ghi chú |
|---|---|---|---|---|---|---|
| M4-QA-01 | Mở hồ sơ mẫu tiếng Nhật và tab Yêu cầu & câu hỏi | Hồ sơ mở được, tab hiển thị đúng | BLOCKED | CAO | Có | Không chạy được browser; sample request có `400` khi truyền `sample_key` |
| M4-QA-02 | Kết quả phân tích yêu cầu | Có 6 nhóm mục tiêu/người dùng/dữ liệu/ràng buộc/ngân sách/thời hạn dạng 2 cột | BLOCKED | CAO | Có | UI đã có sáu trường dạng lưới 2 cột; chưa có DOM/screenshot thật |
| M4-QA-03 | Q&A theo vòng | Có round, số thứ tự, câu hỏi tiếng Nhật, lý do tiếng Việt, câu trả lời/ô nhập | BLOCKED | CAO | Có một phần | Đã sửa số thứ tự liên tục và nhãn `Vì sao hỏi`; `topic`/`blocking` là API gap; chưa có DOM/screenshot thật |
| M4-QA-04 | Câu hỏi đã trả lời | Danh sách vẫn hiển thị ngay cả khi tất cả đã trả lời, kèm trạng thái hoàn tất | BLOCKED | CAO | Có | Đã giữ danh sách và hiển thị câu trả lời/trạng thái; chưa có DOM/screenshot thật |
| M4-QA-05 | Badge Chặn/chủ đề | Chỉ hiển thị khi backend contract cung cấp; không bịa dữ liệu | NOT RUN | TB | Có blocker rõ | `docs/ui/api_gaps.md`: thiếu `topic` và `blocking`, nên không thêm badge giả |
| M4-QA-06 | File đính kèm | Hiển thị tên, loại, dung lượng, trạng thái đọc, lỗi parse và số requirement | BLOCKED | CAO | Có một phần | Đã bổ sung detected type và sheet mapping khi có; số requirement hiển thị ở kết quả đọc file/backend trả; chưa có DOM/screenshot thật |
| M4-QA-07 | Yêu cầu gốc | Markdown được render, thu gọn mặc định | BLOCKED | TB | Có từ trước | `details` đóng mặc định và renderer Markdown hiện có; chưa có DOM/screenshot thật |
| M4-QA-08 | Xuất/nhập Q&A | Nút hiện disabled và giải thích rõ khi endpoint chưa có | BLOCKED | TB | Có | Đã bổ sung mô tả lý do disabled và hướng thay thế trả lời trực tiếp; chưa có endpoint export/import Q&A |
| M4-QA-09 | Loading/rỗng/lỗi | Có trạng thái phù hợp, lỗi thật hiển thị rõ | BLOCKED | TB | Có từ trước | Các query/file/question states đã có loading, empty và error; chưa có browser runtime evidence |
| M4-QA-10 | Console/network | Không có lỗi frontend ngoài lỗi đã biết | BLOCKED | TB | Không thể thực hiện | Không khởi động được Chromium; không thể thu console/network |

## Đối chiếu đầy đủ yêu cầu gốc

| Yêu cầu gốc | Phạm vi đã bao phủ | Kết luận QA |
|---|---|---|
| Kết quả phân tích yêu cầu dạng 2 cột với mục tiêu, người dùng, dữ liệu, ràng buộc, ngân sách, thời hạn | `M4-QA-02` | BLOCKED do thiếu browser evidence |
| Câu hỏi làm rõ theo vòng, số thứ tự, chủ đề, ngôn ngữ khách, lý do tiếng Việt, câu trả lời/ô nhập, badge Chặn, xuất/nhập Q&A | `M4-QA-03`, `M4-QA-04`, `M4-QA-05`, `M4-QA-08` | BLOCKED/NOT RUN; `topic`, `blocking`, export/import là API gaps đã ghi nhận |
| File đính kèm với tên, loại, trạng thái đọc, số requirement và nút thêm file | `M4-QA-06` | BLOCKED do thiếu browser evidence |
| Yêu cầu gốc render Markdown và thu gọn mặc định | `M4-QA-07` | BLOCKED do thiếu browser evidence |
| Quy tắc loading/rỗng/lỗi, mock, không bịa dữ liệu và ảnh thật | `M4-QA-09`, phần Bằng chứng môi trường và Ảnh/giới hạn | Đã ghi giới hạn; không tạo ảnh giả và không sửa source |

## Đối chiếu trạng thái sau vòng frontend-dev

| Nhóm kết quả | Trạng thái |
|---|---|
| Mục CAO còn lỗi frontend có thể sửa ngay | Không phát hiện qua code review tĩnh; các mục CAO còn `BLOCKED` chỉ vì chưa có browser evidence hoặc dữ liệu sample hợp lệ |
| Mục TB còn lỗi frontend có thể sửa ngay | Không phát hiện trong phạm vi contract hiện tại; M4-QA-05 và M4-QA-08 bị chặn bởi API gap |
| Mục cần tester chạy lại | M4-QA-01, 02, 03, 04, 06, 07, 09, 10 tại `1440x900` |
| Mục cần backend-dev | `topic`, `blocking`, endpoint export/import Q&A và cấu hình sample key hợp lệ |

## Phân loại hiện tại

- CAO: 5 mục (`M4-QA-01`, `M4-QA-02`, `M4-QA-03`, `M4-QA-04`, `M4-QA-06`); tất cả đang BLOCKED vì không có browser evidence hoặc sample data hợp lệ, không còn finding frontend có thể sửa được xác nhận bằng code review tĩnh.
- TB: 5 mục (`M4-QA-05`, `M4-QA-07`, `M4-QA-08`, `M4-QA-09`, `M4-QA-10`); `M4-QA-05` là NOT RUN do thiếu contract, các mục còn lại BLOCKED.
- THẤP: chưa phát hiện mục riêng; không suy diễn khi browser chưa chạy được.

Lưu ý: danh sách ID là nguồn đếm chính.

## API/contract gaps cần theo dõi

- Question contract hiện thiếu `topic` và `blocking`; không thể xác minh đầy đủ hai trường này trong UI.
- Chưa có endpoint xuất/nhập Q&A sheet; không thể kiểm tra thao tác thành công.
- Backend log cho thấy route `/api/bids/83/pipeline` trả `404`; cần xem xét nếu route này nằm trong luồng Preview của hồ sơ mẫu. Đây là bằng chứng runtime, không sửa trong bước QA này.
- Request sample preview có `sample_key` trả `400`; cần xác định cấu hình/key hợp lệ ở bước backend hoặc Preview setup. Không đọc hoặc in giá trị secret.

## Ảnh và giới hạn

- Không có ảnh mẫu được chép hoặc tái tạo.
- Không có ảnh “sau” giả.
- Không có browser screenshot vì Chromium executable không khả dụng trong sandbox.
- Cần chạy lại bộ này trong môi trường Preview có browser hỗ trợ trước khi phân loại PASS/FAIL theo pixel/DOM.

## Phạm vi thay đổi

- Không sửa `backend/` hoặc logic tính số.
- Vòng frontend-dev đã sửa các component Màn 4: `frontend/src/components/ClarifySection.tsx`, `frontend/src/components/AttachmentUploader.tsx`, `frontend/src/pages/BidDetailPage.tsx`.
- Đã chạy `npm run build` và `npm run test` trong `frontend/`: build thành công, 6/6 test pass.
