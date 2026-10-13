# Handoff — QA Màn 6 Kế hoạch & báo giá

Ngày: 2026-10-11  
Vai trò: tester / QA  
Trạng thái: **CHANGES REQUIRED / visual verification blocked**

## Phạm vi

- Kiểm tra Màn 6 theo `docs/ui/review_ui_tung_man.md`.
- Dùng Preview hiện có, hồ sơ mẫu tiếng Nhật hư cấu và `LLM_PROVIDER=mock`.
- Không sửa source code, không tạo screenshot giả, không kiểm tra các màn khác.

## Kết quả Preview/API

- Backend và frontend Preview đều chạy.
- `GET /api/health`: `200`.
- `GET /api/bids/sample/preview`: `200`.
- Hồ sơ ID `92` ở trạng thái `waiting_tech_approval`:
  - `/api/bids/92/quotation`: `200`, currency `JPY`, contract model `fixed_price`, có tổng tiền, contingency, by-role và 4 payment milestones.
  - `/api/bids/92/schedule`: `200`, có ngày bắt đầu, team allocation và task theo phase.
  - `/api/bids/92/wbs`: `200`, có các node PoC/MVP/Production.
  - `/api/bids/92/effort`: `200`, có factor và khoảng effort theo phase.
- Hồ sơ draft ID `94` trả `409` cho các API phụ thuộc pipeline; được coi là dữ liệu chưa đủ, không phải pass/fail UI.

## Browser evidence

- Đã thử khởi động Playwright Chromium với viewport `1440x900`.
- Bị Blocked: môi trường thiếu Chromium executable (`Executable doesn't exist ... chromium_headless_shell`).
- Không chụp được screenshot thật và không assert được DOM.
- Không tạo ảnh thay thế.

## Đối chiếu yêu cầu

Chi tiết nằm trong `docs/ui/compare_06_ke_hoach.md`.

- API/source evidence đạt cho currency, summary data hiện có, onsite value được backend trả về, payment milestones, role details, schedule và WBS data.
- Visual evidence bị Blocked cho toàn bộ layout, chữ tràn, collapse/filter, Gantt render và responsive behavior.
- M6-01, M6-02, M6-03, M6-04, M6-07, M6-09, M6-10, M6-11 vẫn Partial/Blocked do thiếu contract, budget data hoặc chưa triển khai inline behavior; không đánh dấu PASS.

## Handoff boundary

QA Màn 6 hoàn tất. Bước tiếp theo cần browser-capable verification và/hoặc backend-dev xử lý các API gaps trong `docs/ui/api_gaps.md`. Không sửa source trong bước này và không tiếp tục sang reviewer tổng.
