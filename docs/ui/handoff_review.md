# Handoff: Review — UI và frontend/backend

## Trạng thái

Hoàn tất review và đã tạo `docs/ui/ui_review.md`. Verdict là **CHANGES REQUIRED**.
Không sửa source code theo đúng vai trò reviewer.

## Findings chính

- Critical: `frontend/src/pages/ProposalPage.tsx:25-30` gọi `useMemo` sau conditional
  return, vi phạm Rules of Hooks và có thể làm Proposal crash khi query chuyển trạng thái.
- High: Browser E2E/screenshot bị BLOCKED do thiếu Chromium; chưa có bằng chứng runtime.
- High: `backend/app/services/attachment_service.py:11-15` đọc toàn bộ upload vào RAM trước
  khi kiểm tra giới hạn, tương ứng GATE-02.
- High: `frontend/src/api/client.ts:131-137` làm mất `code/details` của lỗi export,
  tương ứng GATE-11.
- High: `frontend/src/pages/BidDetailPage.tsx:204-274` chưa đủ header/actions theo UI spec.
- High: `frontend/src/components/PipelineProgress.tsx:8-18` dùng lại trạng thái B3/B4 cho
  B5/B7, có thể báo completed sai.
- High: Quality Gate tổng thể vẫn NO-GO vì GATE-02/03/04 còn mở và GATE-15 E2E bị BLOCKED.

## Phạm vi đã xác nhận

- GATE-01 đúng phạm vi MVP: `Chấp nhận rủi ro: ngoài phạm vi MVP`.
- Không có auth server; `X-Actor` chỉ dùng cho audit log.
- API frontend dùng root-relative `/api`.
- Price gate tĩnh phù hợp: quotation nội bộ hiển thị số, proposal trước duyệt dùng
  `[Presales điền]`.
- Bằng chứng tự động được ghi nhận trong handoff: backend 198 passed, frontend 6 tests,
  build PASS; chưa có browser verification.
- R-08 đã được đối chiếu: không thêm auth server; GATE-01 là `Chấp nhận rủi ro: ngoài
  phạm vi MVP`; `X-Actor` chỉ phục vụ audit log.

## Handoff

Reviewer đã ghi đầy đủ file, dòng và cách sửa trong `docs/ui/ui_review.md`. Bước tiếp theo
cần xử lý các finding và chạy lại browser/Quality Gate; reviewer dừng tại workflow boundary.
