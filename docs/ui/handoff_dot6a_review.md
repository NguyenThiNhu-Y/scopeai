# Handoff Review Đợt 6a

Ngày: 2026-10-11  
Vai trò: Senior reviewer

## Deliverable

Đã cập nhật `docs/ui/dot6a_review.md` với verdict **CHANGES REQUIRED — code fixes applied; Preview acceptance remains incomplete**.

Review đã bổ sung coverage matrix cho toàn bộ yêu cầu trực tiếp của Dot 6a: ba mô
hình báo giá, ba loại tiền tệ, các tỷ lệ/price-to-win, T&M/ODC, ngân sách, price
gate, lịch/go-no-go/mốc khách/Gantt, Q&A export/import và email chỉnh sửa/Copy.
Các P1 ngoài phạm vi workflow này được đánh dấu rõ là không dùng để suy ra verdict.

## Findings chính

1. **RESOLVED:** Q&A workbook có mã + vòng; import bỏ qua dòng trống, câu đã đóng,
   mã sai và trả warnings; test hồi quy đã bổ sung.
2. **RESOLVED:** Q&A import giới hạn 5 MB/200 dòng và xử lý file hỏng với lỗi tiếng Việt.
3. **RESOLVED IN DOCS:** `dot6a_check.md` đã cập nhật theo source/test mới và tách
   code evidence khỏi Preview evidence.
4. **RESOLVED:** quotation fixture và `act`/`waitFor` đã loại bỏ warning Dot 6a; còn
   React Router future warnings ngoài phạm vi.

5. `render_requirement_workbook` là exporter workbook requirement gốc, khác với Q&A
   sheet Dot 6a; review đã ghi rõ không được dùng evidence của hai loại workbook
   thay thế cho nhau.

## Verification

- Backend focused Q&A run: `18 passed` ở lần chạy trực tiếp.
- Full backend raw run: `230 passed`.
- Frontend test: `9 passed`.
- Frontend build/type-check: pass.
- Preview backend đã rebuild; API bid 104 trả 200 cho quotation/schedule/questions,
  nhưng chưa có browser walkthrough đầy đủ.
- Đã sửa source/test trong bước này; không tạo evidence giả.

## Boundary

Bước review đã hoàn tất. Không triển khai các follow-up, không sửa source và không
chạy sang vai trò tester/backend/frontend tiếp theo.
