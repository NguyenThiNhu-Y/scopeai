# Handoff Bước 1 — Màn Tạo hồ sơ

## Trạng thái

Đã triển khai màn Tạo hồ sơ và luồng phân tích một lần. Đã bổ sung các phần còn thiếu
trong lần review deliverable: file mẫu hiển thị ngay trong khu đính kèm, API contract
cho endpoint preview và test backend cho endpoint này. Chưa tự nhận PASS tiêu chí Preview
vì bước kiểm tra Preview thuộc tester kế tiếp trong workflow.

## Đã thay đổi

- `frontend/src/pages/BidNewPage.tsx`
  - Thay hai nút nạp mẫu tạo hồ sơ ngay bằng thẻ bộ hồ sơ RFP mẫu với nút **Dùng bộ này**.
  - Gọi preview bộ mẫu trước; khi chọn mẫu, form được điền sẵn và hiển thị danh sách file
    trước khi bấm Phân tích.
  - Có form thông tin hồ sơ, tự giữ ngôn ngữ mẫu, ngân sách và đơn vị tiền.
  - Thêm khu kéo thả/chọn file, giới hạn 10 file và 20 MB/file, kiểm tra phần mở rộng,
    phân loại file, đổi loại và xóa file.
  - Luồng Phân tích: tạo hồ sơ hoặc nạp mẫu → upload từng file → parse → confirm theo
    gợi ý readiness → start pipeline → chuyển tới trang hồ sơ.
  - Hiển thị tiến trình ngay trên nút, thông báo lỗi tiếng Việt, giữ form khi lỗi và cho
    phép thử lại; không tạo hồ sơ mới nếu request thất bại sau khi đã tạo hồ sơ.
- `frontend/src/api/client.ts`, `frontend/src/api/types.ts`
  - Thêm API/type cho preview bộ mẫu.
- `backend/app/services/sample_service.py`
  - Thêm metadata preview, gồm nội dung form và kích thước file mẫu.
- `backend/app/api/routers/bids.py`
  - Thêm endpoint xem trước bộ mẫu `GET /api/bids/sample/preview`.

## Kiểm tra tự động

- `frontend npm run build`: **PASS**.
- `frontend npm run test`: **PASS — 6 tests**.
- `backend python -m pytest -q backend/tests/test_bids.py`: **PASS — 13 tests**.
- Added coverage for preview metadata, all three Japanese sample files, no side-effect bid
  creation, and invalid sample keys.
- Lệnh thử `backend/tests/test_attachments.py` không chạy vì repository không có file test
  này; đây là giới hạn tên test, không phải test fail.

## Preview / bằng chứng

Chưa chạy Preview trong bước này; tester workflow phải kiểm tra trên Preview bằng bộ mẫu
Nhật. Vì vậy chưa có screenshot runtime và không tạo ảnh giả.

Endpoint preview đã được ghi vào `docs/04_architecture/api_contract.md`; bộ mẫu được hiển
thị trực tiếp trong khu **Tài liệu đính kèm** trước khi bấm Phân tích.

## Tiêu chí Xong khi cần tester xác nhận

`Dùng bộ này` (mẫu Nhật) → thấy 3 file → `Phân tích` → tự sang trang hồ sơ → đọc 36
requirement → pipeline tới `Chờ làm rõ` mà không bấm thêm nút nào.

## Ghi chú cho tester

- Bộ mẫu Nhật hiện có 3 file theo backend: `ja_email.md`, `ja_rfp.docx`,
  `ja_requirements.xlsx`.
- Khi chọn mẫu, frontend gọi preview; khi bấm Phân tích, frontend gọi `loadSample`, sau
  đó parse/confirm/start pipeline trên hồ sơ vừa tạo.
- Cần kiểm tra backend Preview đã chứa route preview mới và pipeline mock trả đúng 36
  requirement cùng trạng thái Chờ làm rõ.

## Kết thúc bước

Đã hoàn tất deliverables của frontend Bước 1 và dừng tại handoff. Không thực hiện Bước 2
hoặc vai trò tester/reviewer.
