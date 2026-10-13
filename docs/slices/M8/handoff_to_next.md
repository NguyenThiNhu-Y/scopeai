# Handoff M8 — Hoàn thiện

## Đã triển khai

- `GET /api/settings` và `PUT /api/settings/{key}` cho `effort`, `rate_card`, `factors`.
- Override bảng chuẩn hợp lệ được lưu trong DB, tăng version và ghi `update_reference` vào audit log.
- Validate YAML và validate toàn vẹn: đủ direction × phase, min ≤ max, đủ rate offshore/onsite,
  `factor_cap > 1`; lỗi giữ nguyên dữ liệu cũ.
- Effort mới đọc override qua `load_effort(session)` và factors mới đọc override qua
  `load_factors(session)`; quotation mới đọc rate card override. `ReferenceSnapshot` của hồ sơ
  đã tính vẫn giữ nguyên nên hồ sơ đã duyệt không bị đổi số liệu.
- `GET /api/history` lọc theo khách hàng và trạng thái, hiển thị audit log liên kết với hồ sơ.
- Frontend có trang Cài đặt editor YAML, trạng thái loading/error, thông báo tiếng Việt, trang
  Lịch sử có tìm/lọc/rỗng/lỗi, navigation responsive và nút đổi sáng/tối.
- Preview bổ sung Caddy để proxy một origin `/api/*` tới backend.

## Kiểm chứng

- Backend M8: `7 passed` với `tests/test_settings.py`, `tests/test_settings_integrity.py`,
  `tests/test_audit_log.py`.
- Frontend: `npm test -- --run`: `6 passed`.
- Frontend: `npm run build`: pass.
- Frontend: `npm run type-check`: pass.
- Preview container backend/frontend/proxy đều đang Up; `/api/settings` và `/api/history` trả 200
  khi gọi trực tiếp trong backend container.

## Lưu ý còn lại

- Preview hiện dùng SQLite bind mount và backend có trạng thái health `starting` trong lúc startup
  dù server đã trả health 200; đây là healthcheck hiện có, không chặn luồng M8.
- Bộ test toàn repo qua wrapper output-compactor đôi lúc trả thông báo sai `No tests collected`;
  nhóm test M8 đã được chạy bằng pytest output nguyên bản và pass.
