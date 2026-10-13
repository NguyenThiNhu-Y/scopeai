# Handoff — Reviewer Đợt 7

Ngày: 2026-10-11  
Vai trò: senior reviewer  
Trạng thái: **DONE trong boundary reviewer; verdict CHƯA SẴN SÀNG MERGE / APPROVAL.**

## Deliverable

- `docs/ui/dot7_review.md`: review code, contract, regression, evidence runtime và completeness của đủ 9 P0.

## Phương pháp

- Đã đọc `AGENTS.md`, `docs/ui/review_luot4.md`, toàn bộ handoff Đợt 6a/Đợt 7 và `docs/ui/dot7_check.md`.
- Đã dùng vibegraph MCP trước discovery code.
- Đã đối chiếu các symbol chính: settings route/schema, intake milestone extraction, schedule fallback, proposal fact rendering, SSE/query invalidation và Sidebar.
- Không sửa source code, không chạy git, không tạo screenshot hoặc evidence giả.

## Findings chính

1. **Cao:** backend `/api/settings` và `SettingsResponse` vẫn chỉ trả `keys`; frontend source vẫn đọc `keys`/`yaml_preview` trong khi handoff mô tả `payload`; QA đã thấy đúng mismatch này trên Preview.
2. **Cao:** extractor mốc khách tồn tại nhưng runtime giữ `customer_schedule_start`, `customer_mvp_start`, `customer_production_start` là `null`; P0-6 chưa đạt.
3. **Cao:** browser bị block và pipeline dừng clarification, nên chưa đủ evidence để approve các P0 UI/downstream.
4. **Trung bình:** event `clarify` invalidate ít query hơn event `done`; cần chốt semantics và test rõ ràng để bảo đảm không cần F5.
5. **Thấp:** handoff backend/frontend đã ghi contract settings như đã hoàn thành nhưng source/runtime chưa đồng bộ.

## Verification boundary

- Không tự sửa các finding.
- Không thực hiện lại tester hoặc bắt đầu role khác.
- Không kết luận pass từ focused tests khi Preview chưa chứng minh acceptance.

Đã ghi review report và handoff này; dừng tại boundary reviewer.
