# Handoff Màn 9 — Quy trình & phê duyệt

## Boundary

- Vai trò: frontend-dev, Đợt 3.
- Chỉ sửa tab `Quy trình & phê duyệt` và tài liệu API gap liên quan.
- Không sửa backend, không chạm Màn 2, Màn 7, Màn 8, Màn 10 hoặc final-flow/reviewer.
- Không dùng git command.

## Đã làm

- Thay `frontend/src/pages/ApprovalsPage.tsx` từ một thẻ quyết định chung thành ba thẻ:
  - `Duyệt kỹ thuật`: hướng giải pháp, tổng effort, cảnh báo WBS, câu hỏi còn mở, nhận xét, `Duyệt kỹ thuật`, `Yêu cầu sửa`.
  - `Duyệt giá`: tổng giá, so với ngân sách, dự phòng/mô hình hợp đồng, nhận xét, `Duyệt giá`, `Từ chối`.
  - `Lịch sử & phiên bản`: timeline changelog theo `bid_id` và trạng thái thiếu dữ liệu phiên bản gửi khách.
- Bỏ hoàn toàn lựa chọn và nhãn `Bỏ qua` khỏi UI.
- Dùng đúng API hiện có:
  - `approveTech` và `approvePrice` cho quyết định;
  - `getBid`, `getEffort`, `getEvaluations`, `getQuestions`, `getQuotation`, `getSchedule` cho tóm tắt;
  - `getHistory` cho lịch sử;
  - `unlockBid` cho thao tác mở khóa hiện có.
- Duyệt giá bị khóa cho tới khi trạng thái hồ sơ là đã duyệt kỹ thuật; backend vẫn là nơi kiểm tra gate cuối.
- Cảnh báo WBS lấy từ `schedule.warning`; câu hỏi còn mở lấy từ các question chưa có answer.
- Khi history có event `approve_tech` hoặc `approve_price`, thẻ tương ứng hiển thị người duyệt và thời điểm.
- Nhận xét từ chối/yêu cầu sửa bắt buộc ở UI; trạng thái loading và lỗi hiển thị theo từng query/mutation.
- Thêm gap vào `docs/ui/api_gaps.md`:
  - chưa có contract danh sách phiên bản proposal gửi khách;
  - history chưa hỗ trợ lọc trực tiếp theo `bid_id`.
- Không bịa phiên bản, timestamp, người duyệt hoặc số liệu giá/effort.

## Kiểm chứng

- `frontend`: `npm run build` — PASS.
- `frontend`: `npm run test` — PASS, 6/6 tests.
- Preview rebuild bằng `podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d` — services backend/frontend ở trạng thái `Up`.
- Preview health — PASS: backend trả `status=ok`, database `ok`, `llm_provider=mock`.
- Preview API kiểm tra:
  - `GET /api/bids/96` — `waiting_tech_approval`, dữ liệu hồ sơ hợp lệ;
  - `GET /api/bids/96/quotation` — trả tổng giá và model;
- `GET /api/bids/96/evaluations` — trả solution direction/warnings;
- `GET /api/bids/96/schedule` — trả `warning` cảnh báo lịch/WBS;
- `GET /api/history` — trả changelog, frontend lọc theo hồ sơ;
- `GET /api/bids/96/questions` được tích hợp để đếm câu hỏi còn mở.
- Kiểm tra cuối sau thay đổi — `npm run build` PASS; `npm run test` PASS, 6/6 tests.
- Không có browser screenshot/runtime click evidence trong step này; handoff không tạo ảnh giả. Việc đối chiếu trực quan 1440×900 thuộc node tester theo workflow.

## Known limitations

- Backend chưa trả danh sách phiên bản proposal gửi khách, nên thẻ phiên bản hiển thị trạng thái unavailable minh bạch.
- Backend history chưa có `bid_id` filter, nên frontend tải history chung rồi lọc theo hồ sơ.
- `ApprovalsPage` hiển thị trong khung tab dùng chung; không thêm tiêu đề trang lồng kiểu cổng duyệt cũ.

## Handoff status

**Màn 9 frontend complete for this boundary.** Bàn giao cho node tester kiểm tra Preview trực quan và hành vi nút; dừng tại đây.
