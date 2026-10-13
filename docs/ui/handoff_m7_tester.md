# Handoff — Tester Màn 7 Đáp ứng yêu cầu

Ngày: 2026-10-11  
Vai trò: tester  
Trạng thái: **BLOCKED một phần — đã ghi compare, cần browser để hoàn tất UI evidence**

## Deliverables

- `docs/ui/compare_07_dap_ung.md`
- Không tạo screenshot giả trong `docs/ui_v3/`.

## Đã kiểm tra

- Preview stack đang chạy.
- `GET /api/health`: PASS; `LLM_PROVIDER=mock`, database OK.
- Hồ sơ mẫu tiếng Nhật `#92`: `GET /api/bids/92/evaluations` trả 36 requirement, đã đánh giá đủ 36, tất cả rating `○`.
- Export: `GET /api/bids/92/exports/requirements.xlsx` trả XLSX thật, HTTP 200, filename `ja_requirements.xlsx`, kích thước 7514 bytes.
- SPA route `/bids/92?tab=evaluations`: HTTP 200 và trả HTML shell; chưa coi đây là bằng chứng DOM sau render.
- Graph/source evidence xác nhận backend export lấy `bid.customer_language`, chưa nhận `note_language` từ UI.

## Blocker

- Playwright không khởi chạy vì thiếu Chromium executable (`chromium_headless_shell-1187/.../headless_shell`).
- Vì vậy chưa thể xác minh React DOM sau render, click filter/export, loading/empty/error trên UI, chữ tràn, screenshot 1440x900 hoặc console runtime.
- Không sửa app source theo vai trò tester.

## Findings cần chuyển tiếp

- Mức **CAO**: chưa có bằng chứng browser cho hai nút export và console; cần chạy lại sau khi browser khả dụng.
- Mức **TB**: selector ngôn ngữ ghi chú đang disabled do API chưa nhận `note_language`; gap đã ghi trong `docs/ui/api_gaps.md`.
- Mức **THẤP**: layout/responsive chưa thể kết luận vì không có screenshot thật.

## Boundary

Đã dừng ở QA Màn 7. Không sửa frontend, không làm Màn 8/Màn 9, không chạy full-flow hoặc reviewer.
