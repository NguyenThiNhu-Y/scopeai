# Handoff — Build -> Test/Review (M7 Xuất file bằng code)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Backend Dev + Frontend Dev + Build coordinator |
| Cho | Test/Review |
| Ngày | 2026-10-10 |
| Slice | M7 — Word, Excel, PDF, ZIP và Q&A |

## 1. Đã triển khai

- Backend có bốn endpoint root-relative dưới `/api/bids/{id}/exports/` cho DOCX, XLSX, PDF và ZIP.
- Word được sinh bằng code, có bìa, mục lục, section, giả định, ngoài phạm vi và price gate.
- Excel có các sheet `Tóm tắt`, `WBS`, `Báo giá`, `Lịch Gantt`, `Q&A`; tổng man-day và tổng báo giá dùng công thức `SUM`.
- PDF được chuyển từ DOCX bằng LibreOffice headless; compose gọi converter và trả lỗi tiếng Việt rõ ràng nếu image Preview chưa có LibreOffice/font CJK.
- ZIP chứa đúng ba artifact theo thứ tự ổn định; filename được normalize deterministic.
- Hồ sơ tiếng Nhật chạy ja-check; warning được trả qua `X-Ja-Check-Result` và không chặn tải.
- Export log lưu actor từ `X-Role`/`X-User`, price gate và ja-check; export không thay đổi trạng thái nghiệp vụ.
- Frontend có route `/bids/:id/export`, bốn nút tải, loading/success/error state và panel cảnh báo ja-check.

## 2. Cách chạy

```bash
make test
make quality-gate
make preview
```

Preview dùng mock LLM. Sau khi stack healthy, mở một hồ sơ mẫu Nhật đã chạy pipeline, vào `Xuất hồ sơ`, tải từng file và bundle.

## 3. Kiểm tra đã chạy

- `cd backend && pytest -q`: pass, 223 tests.
- `cd frontend && npm run type-check`: pass.
- `cd frontend && npm run build`: pass.
- `cd frontend && npm test -- --run`: pass, 6 tests.
- Preview compose: backend healthy, frontend running.

## 4. Test evidence cần bổ sung

- Kiểm tra trực tiếp nội dung DOCX/PDF/Excel/ZIP với fixture M7.
- Xác nhận image triển khai/Preview có LibreOffice headless và font Noto CJK trước khi kiểm thử PDF tiếng Nhật.
- Xác nhận hai lần export cùng input cho bytes và ZIP metadata deterministic.
- Xác nhận hồ sơ chưa duyệt không lộ số tiền thực trong cả bốn artifact.
- Xác nhận warning ja-check vẫn tải được file và export log không đổi trạng thái bid.

## 5. Known gaps

- Bộ test file-level M7 được nêu trong spec chưa có trong repository; suite hiện tại chưa thay thế đầy đủ các acceptance test đó.
- Chưa có browser click-through tự động trong bước Build; Test/Review cần kiểm tra UI và network trong Preview.
- Image Preview hiện tại không có LibreOffice headless/font CJK cài sẵn; PDF endpoint sẽ báo lỗi actionable cho đến khi image được bổ sung các dependency này.
- Lệnh `rtk pytest -q` báo không thu được test trong workspace; chạy trực tiếp `pytest -q` cho kết quả đúng.
- `make` không có trong agent runtime nên chưa chạy được `make test`/`make quality-gate`; đã chạy tương đương backend pytest và frontend type-check/build/test trực tiếp.

## 6. Contract notes

- Không thêm endpoint nhập Q&A hoặc PowerPoint.
- Frontend chỉ gọi `/api/...`, không tự sinh hoặc tính nội dung artifact.
- `X-Ja-Check-Result` chỉ là JSON URL-encoded warning header; các locale vi/en không chạy ja-check.

Task Build complete. Awaiting prompt for the next role.
