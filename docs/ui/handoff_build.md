# Handoff — Đặc tả UI Trợ lý dự thầu

Đã hoàn tất bước đặc tả giao diện trước đó. Tài liệu chính: `docs/ui/ui_spec.md`.

## Deliverables

- Design tokens light/dark.
- App shell/sidebar và quy tắc nhãn tiếng Việt.
- Header hồ sơ, pipeline ngang, 7 tab lưu qua `?tab=`.
- Bố cục chi tiết cho Tổng quan, Kế hoạch & báo giá, Proposal & hồ sơ, Đáp ứng yêu cầu.
- API mapping hiện có và khoảng trống cần xác nhận.
- Quy tắc API root-relative, price gate, a11y và trạng thái request.
- Tiêu chí nghiệm thu desktop/mobile, screenshot và Preview.

## Giới hạn bước đặc tả trước đó

Phần đặc tả không viết application code. Bước frontend platform hiện tại đã triển khai nền tảng bên dưới; API contract ưu tiên giữ nguyên.

## Kiểm tra completeness

- Đã bao phủ UI-01 đến UI-03 và UI-04 đến UI-10 trong review G4 ở mức yêu cầu giao diện.
- Đã bao phủ các ảnh chuẩn 01–10 theo vai trò màn hình.
- `docs/ui_current/` hiện chưa có ảnh đối chiếu; đây là deliverable bắt buộc của bước tester, không phải deliverable của bước đặc tả.
- Endpoint export requirement, phase quotation fields và mapping solution cần được xác minh trong bước implementation; không được coi là đã có nếu code/API chưa cung cấp.

## Handoff — Frontend platform implementation

Đã triển khai nền tảng UI theo `docs/ui/ui_spec.md` trong phạm vi frontend:

- `frontend/src/index.css`: token sáng/tối theo palette đặc tả, semantic colors, focus ring và `prefers-reduced-motion`.
- `frontend/src/components/Sidebar.tsx`: app shell có `Trợ lý dự thầu`, `+ Tạo hồ sơ`, `Hồ sơ`, `Đánh giá`, `Cài đặt`, trạng thái `LLM: mock` và nút đổi theme.
- `frontend/src/components/ui.tsx`: primitive dùng chung `Card`, `Badge`, `Stat`, `Table`, `EmptyState`, `ErrorBox`, `Spinner` để các bước sau tái sử dụng.
- `frontend/src/components/PipelineProgress.tsx`: hiển thị pipeline ngang, responsive, giữ spinner/completed/failed/waiting qua `StepBadge`, có retry.
- `frontend/src/App.tsx`: route legacy `/solution`, `/wbs`, `/schedule`, `/quotation`, `/proposal`, `/approvals`, `/export` redirect về `/bids/:id?tab=...`; API không đổi.

## Verification

- `npm run build`: PASS.
- `npm run test`: PASS, 6 tests.
- Không thêm authentication/authorization server; `X-Actor` và xử lý GATE-01 thuộc backend/API step. `docs/quality/gate_summary.md` đã ghi đúng `Chấp nhận rủi ro: ngoài phạm vi MVP`.
- Frontend `npm run build` và `npm run test` đã pass. Preview/E2E chưa chạy trong step này.
- Đã chạy backend `python -m pytest -q` trong completeness audit: exit 1, còn 19 test fail ở approval, deadline, effort/factor, proposal approval và WBS/snapshot. Đây là blocker chưa được xử lý; không được báo toàn bộ hệ thống PASS.

## Completeness audit

- Đã đối chiếu lại task gốc: không thêm auth server; GATE-01 giữ mức `Chấp nhận rủi ro: ngoài phạm vi MVP`; `X-Actor` chỉ phục vụ audit.
- Đã sửa pipeline UI từ 7 lên 8 chặng theo review G4 và bỏ ghi chú milestone cũ `Chưa triển khai ở M3`.
- Tab hồ sơ có `role="tablist"`, `role="tab"`, `aria-selected` và URL state `?tab=`.
- Các phần backend pytest/R-08 không được thay đổi trong step frontend vì auth-only đã đúng và handoff backend phải xử lý riêng.

**Step frontend platform complete after completeness audit.**
