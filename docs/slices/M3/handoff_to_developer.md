# Handoff — Review → Developer (M3)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Senior Reviewer |
| Cho | Developer |
| Ngày | 2026-10-10 |
| Slice | M3 |

## Deliverables

- Review đầy đủ tại `docs/slices/M3/review.md`.

## Verdict

**CHANGES REQUIRED**

## Việc cần xử lý trước review lại

1. Chặn giả mạo `by` bằng cách dùng/kiểm tra `X-Role` và `X-User` ở `POST /api/bids/{id}/solution`; bổ sung API tests.
2. Chặn mọi mutation chọn hướng khi `Bid.locked=true`, trả `409 STATE_CONFLICT`; bổ sung regression test và assert state không đổi.
3. Trả stale-warning từ `GET /api/bids/{id}/evaluations` sau khi lựa chọn cũ bị supersede; bổ sung test cho đổi hướng và refresh/persistence.
4. Xem lại heuristic `many_requirements` và bổ sung positive/negative tests để tránh bật hệ số chỉ vì một từ khóa.
5. Chạy lại exact M3 acceptance commands, `pytest -q`, `make test`, frontend build và `make quality-gate` sau khi sửa.

## Ghi chú

- Không có CRITICAL finding.
- UI Playwright vẫn bị block bởi thiếu Chromium; giữ nguyên blocker và không báo UI PASS nếu chưa có browser evidence.
- Không dùng git command trong bước review.

Task Review complete. Awaiting Developer fixes and re-review.
