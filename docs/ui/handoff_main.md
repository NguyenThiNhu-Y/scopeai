# Handoff: Main — UI tabs, API mapping và regression reconciliation

## Trạng thái

Hoàn tất deliverables của bước Main. Frontend build/unit test và toàn bộ backend pytest
đã được xác minh bằng lệnh raw, không qua kết quả wrapper bị nén. Preview đang chạy với
LLM mock và health check trả HTTP 200.

## Đã triển khai

- Tích hợp tab hồ sơ trong `frontend/src/pages/BidDetailPage.tsx`:
  - Tổng quan
  - Yêu cầu & câu hỏi
  - Giải pháp
  - Kế hoạch & báo giá
  - Đáp ứng yêu cầu
  - Proposal & hồ sơ
  - Quy trình & phê duyệt
- Giữ trạng thái tab trên `?tab=`, kiểm soát tab không hợp lệ và giữ các deep-link legacy.
- Tích hợp đúng `BidPlanTab`, `ProposalPage`, `ApprovalsPage` và `RequirementMatrix`;
  nội dung file/pipeline không còn rơi vào các tab khác.
- Bổ sung nội dung kế hoạch, quotation nội bộ, phase/role effort, schedule/Gantt, WBS,
  filter ma trận và export requirement.
- Bổ sung preview/chỉnh sửa/copy/tải Markdown proposal, chọn ngôn ngữ và export cards.
- Bổ sung `payment_milestones` vào quotation response, frontend type và API contract.
- Giữ price gate: số tiền hiển thị cho người dùng nội bộ; tài liệu khách chưa duyệt dùng
  `[Presales điền]`.
- Giữ single-user MVP theo AGENTS.md: không thêm auth server; `X-Actor` chỉ phục vụ audit.
- Hòa giải backend fixtures/regressions:
  - fixture WBS `good` không còn tạo task lá vượt 10 man-day.
  - assertion effort dùng đúng bảng RAG hiện hành.
  - test override tạo độ lệch đủ vượt ngưỡng 20%.

## Verification

- Frontend `npm run build`: **PASS**.
- Frontend `npm run test -- --run`: **PASS — 6 tests**.
- Backend `python -m pytest -q`: **PASS — 198 passed** trong lần chạy trực tiếp hoàn chỉnh;
  output có ba nhóm tiến độ 36%/72%/100% và chỉ có cảnh báo deprecation của Starlette/httpx.
- Các lần gọi qua output wrapper hiển thị sai `No tests collected`; không dùng chúng làm
  bằng chứng và không có test nào bị bỏ qua trong lần chạy trực tiếp.
- Backend có cảnh báo deprecation của Starlette/httpx, không làm fail suite.
- Preview `podman-compose -f podman-compose.preview.vibeflow.yaml ps`: backend và frontend đều Up.
- Preview health `GET /api/health`: **HTTP 200**, `status=ok`, `llm_provider=mock`, `database=ok`.
- Audit cuối: chạy trực tiếp `python -m pytest -q`; kết quả cuối là toàn bộ suite pass,
  tương ứng **198 passed**.

## Completeness review

Đã rà soát lại theo `docs/ui/ui_spec.md` và sửa các điểm còn thiếu trong bước trước:

- Tab Kế hoạch & báo giá đã hiển thị nhãn tiếng Việt cho `contract_model` thay vì enum raw.
- Tab Kế hoạch & báo giá đã hiển thị các mốc thanh toán từ backend, gồm phần trăm và ngày đến hạn.
- Bộ lọc danh sách hồ sơ đã bao phủ các trạng thái chờ duyệt giá, đã duyệt giá, từ chối và lỗi.
- Trang Quy trình & phê duyệt đã dùng `BidStatusBadge`, không còn render raw status.
- Pipeline progress được đặt ở header workspace của hồ sơ, thay vì chỉ xuất hiện trong nội dung Tổng quan.
- Đã rà soát lại mapping pipeline: UI vẫn hiển thị đủ 8 chặng theo spec, với các chặng
  tổng hợp ánh xạ trạng thái từ 7 step keys hiện có của backend, không tạo endpoint hoặc
  thay đổi API contract.
- Đã sửa mapping để không còn dùng trùng `wbs` cho cả Kiến trúc & effort và WBS & timeline.
- Đã tách trạng thái hiển thị Proposal khỏi `ja_check` deferred; Proposal hoàn tất theo
  step `proposal` mà không chờ bước kiểm tra ngoài phạm vi MVP.
- Đã loại các nút điều hướng route rời khỏi header hồ sơ; thao tác chính đi qua tab workspace,
  còn deep-link legacy vẫn được giữ ở router.
- Loại bỏ bản PipelineProgress bị lặp trong tab Tổng quan; header workspace là nơi hiển thị duy nhất.
- Bổ sung `docs/ui/ui_compare.md` để ghi rõ các điểm đối chiếu tĩnh và các phần browser
  screenshot/E2E còn bị BLOCKED, không tuyên bố hoàn tất giả.

## Ghi chú / cần verify ở bước sau

- Browser E2E bị BLOCKED trước điều hướng vì thiếu executable Chromium
  `chromium_headless_shell-1187`; không có screenshot runtime nào được tạo.
- React Router vẫn in future-flag warnings (`v7_startTransition`, `v7_relativeSplatPath`).
- Cần kiểm thử trực quan các tab trên Preview và xác nhận các file export mở được.
- `docs/ui/ui_compare.md` đã ghi bảng đối chiếu 10 trang/tab ở 1440×900 và 1280×900,
  cùng trạng thái BLOCKED và nguyên nhân thiếu Chromium; không đánh dấu giả là PASS.
- `docs/quality/gate_summary.md` giữ `GATE-01 = Chấp nhận rủi ro: ngoài phạm vi MVP`;
  không coi unit/build là thay thế cho kiểm thử Preview/E2E.
- `docs/ui/ui_compare.md` đã cập nhật cột `Đã sửa` cho UI-04 đến UI-10; không còn mục
  CAO chưa xử lý trong phạm vi frontend/API của bước Main.

## Handoff

GATE-01 đã được gỡ khỏi phạm vi xác thực/phân quyền: `X-Actor` chỉ được dùng làm actor
caller-controlled cho audit log; không có authorization theo user và không thêm auth server.
Hai test R-08 liên quan single-user/SSE đã được giữ theo contract MVP và toàn bộ backend
pytest hiện pass. Preview sẵn sàng với LLM mock; bước tiếp theo cần kiểm thử trực quan/browser
E2E và xử lý các gate HIGH còn lại nếu workflow tiếp tục.
