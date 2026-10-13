# Handoff Đợt 10 — Frontend

Ngày: 12/10/2026. Chạy SAU backend (256 backend tests pass). Frontend: **14 vitest pass** (11 cũ + 3 mới cho E.1), **build tsc + vite sạch**.

## Tóm tắt thay đổi

### C — Câu hỏi theo vòng (phần giao diện)
- `ClarifySection.tsx`: **hiện ĐỦ MỌI câu hỏi theo từng vòng** (bỏ bộ lọc `visibleRounds` trước đây làm mất câu vòng 2). Mỗi vòng một khối; vòng đang chờ trả lời hiện textarea, vòng đã xong hiện "✓ đã hoàn tất" + câu trả lời, vòng chưa mở hiện "chưa mở".
- `api/types.ts`: thêm `round_two_reason_vi?: string | null` vào `QuestionsResponse` (backend đã trả).
- `BidDetailPage.tsx`: truyền `roundTwoReason` vào ClarifySection; hiển thị hộp "Vòng 2: <lý do>" khi có câu vòng 2 chờ trả lời.

### E.1 — Thẻ KPI
- `lib/format.ts`: thêm `coveragePercent(stats)` = **(◎ + ○) / stats.evaluated** (tổng ĐÃ ĐÁNH GIÁ), trả `null` khi chưa đánh giá; thêm `COVERAGE_DISPLAY_KEYS = ['◎','○','△','×','cần làm rõ']`; thêm `SOLUTION_LABELS` dùng chung.
- `BidDetailPage.tsx`: thẻ Requirement = `số requirement · % đáp ứng` (bỏ đọc `stats.pass` không tồn tại và bỏ cộng `total`/`evaluated` vào mẫu số). Thẻ "Đáp ứng yêu cầu" ở Tổng quan chỉ hiện ◎ ○ △ × Cần làm rõ (không hiện total/evaluated).
- Unit test mới trong `App.test.tsx`: 3 test cho `coveragePercent` (94% với ◎19 ○15/36; 0%; null khi chưa đánh giá; không phụ thuộc total).

### E.2 — Tự tải lại
- Sau khi gửi câu trả lời (`handleAnswersSubmitted`): invalidate **mọi** query (`bid/attachments/evaluations/effort/quotation/schedule/questions/proposal/wbs/history` + `bids`) — trước đây chỉ refetch bid + questions.
- **Poll mỗi 3 giây** khi `bid.status === 'analyzing'` (invalidate bid/questions/evaluations) — trạng thái và tab tự cập nhật kể cả khi mất SSE.
- **Gate effort/quotation/schedule**: chỉ gọi khi `pipelineAdvanced` (bid tồn tại và status không ∈ draft/analyzing/waiting_clarification) → **hết lỗi 409 trên console** khi mở hồ sơ đang chạy. Áp dụng ở **BidDetailPage**, **BidPlanTab** (quotation/schedule/wbs) và **ApprovalsPage** (effort/quotation/schedule).

### E.3 — Sidebar
- Nút "+ Tạo hồ sơ" **luôn** `bg-[var(--brand)] text-white`, kể cả khi active (bỏ nhánh `--brand-strong` làm mất chữ).

### E.4 — WBS sửa trong dòng
- `WbsTreeTable.tsx` viết lại hoàn toàn: tên task = input, giai đoạn = select, vai trò = select, man-day = input **ngay trong dòng**; **mã + tên cùng một dòng**; "+ Thêm task" ở **cuối mỗi nhóm** (cấp 1 → task cấp 2, cấp 2 → lá cấp 3), "+ Thêm nhóm cấp 1" ở cuối bảng; **MỘT nút "Lưu thay đổi"** gom toàn bộ thay đổi (add/update/remove) → PUT /wbs **một lần**; validate (mã trùng, thiếu tên/vai trò/man-day ≤ 10); "Hủy thay đổi" reset.
- `WbsPage.tsx`: bỏ luồng editor cũ (✎ / WbsRowEditor), bỏ nút "＋ Thêm task" đầu trang; dùng bảng mới; sau lưu hiển thị `recalculated.schedule` (tổng + lịch tự tính lại).
- `BidPlanTab.tsx`: **bỏ nút "Mở trình sửa đầy đủ"**; dùng bảng sửa trong dòng trực tiếp; `saveWbs.onSuccess` cập nhật `savedSchedule` + query schedule từ `recalculated.schedule`.
- Xóa `WbsRowEditor.tsx` (không còn dùng).

### E.5 — Báo giá
- `QuotationSection`: thêm `useEffect` **đồng bộ state** `model`/`contingency` từ `quotation` khi tải xong → **ô "Dự phòng (%)" hiện đúng giá trị đã lưu (20)** (trước đây luôn 0 vì state khởi tạo trước khi data về).
- "Tạm tính (trước dự phòng)" = `totals.subtotal`; "Dự phòng" = `contingency_amount`; "Tổng chưa gồm thuế" = `tax_excluded`.
- Dòng thuế **theo tax_mode**: `tax_excluded` → "Thuế X%: <amount> · chưa gồm trong tổng giá"; `tax_included` → "Đã gồm thuế X% trong tổng giá" (không hardcode "Thuế đã gồm").
- "Gợi ý điều chỉnh" ghi rõ **"tăng X%" / "giảm X%"** theo dấu.
- `api/types.ts`: thêm `tax_amount`/`tax_percent` vào `QuotationResponse.totals`.
- **Tên mô hình giá nhất quán**: `ApprovalsPage` bỏ `CONTRACT_LABELS` riêng ('Trọn gói'/'T&M') → dùng chung `CONTRACT_MODEL_LABELS` từ `lib/format` ('Giá cố định'/...); `QuotationPage` hiện nhãn thay vì mã thô `q.contract_model`.

### E.6 — Proposal
- Backend đã sửa nội dung (không lặp tiêu đề, bản Nhật không lẫn tiếng Việt, 3–5 câu, placeholder đã thay bằng dữ liệu hồ sơ). Frontend `ProposalPage` render đúng — không cần đổi.

### E.7 — Danh sách
- `BidsPage.tsx`: thêm thẻ **"Chờ duyệt"** = `waiting_tech_approval` + `waiting_price_approval` (backend stats chưa có → tính từ items; lưu ý giới hạn trang). Lưới thẻ 6 cột.
- Bảng giảm `min-w-[920px]` → `min-w-[820px]`, cột Tên dự án `max-w-[220px]` → **không tràn ngang ở 1280px**, cột Hạn nộp không bị cắt.

### E.8 — Tab Đáp ứng
- `RequirementMatrix.tsx`: cột "Thành phần" dùng `SOLUTION_LABELS` (nhãn tiếng Việt), **`none` → "—"**, không hiện mã thô.
- `BidDetailPage.tsx`: nút **"Chạy lại" thành nút phụ** (viền trắng chữ xanh) khi đã chạy; nút "Phân tích" giữ nền xanh.

## File đã sửa (frontend)
- `src/lib/format.ts` (coveragePercent, COVERAGE_DISPLAY_KEYS, SOLUTION_LABELS)
- `src/api/types.ts` (round_two_reason_vi, tax_amount/tax_percent)
- `src/pages/BidDetailPage.tsx` (E.1, E.2, E.8, truyền roundTwoReason)
- `src/components/ClarifySection.tsx` (C — hiện đủ vòng)
- `src/components/Sidebar.tsx` (E.3)
- `src/components/WbsTreeTable.tsx` (E.4 — viết lại)
- `src/pages/WbsPage.tsx` (E.4)
- `src/components/BidPlanTab.tsx` (E.4, E.5)
- `src/pages/ApprovalsPage.tsx` (E.5 — CONTRACT_MODEL_LABELS)
- `src/pages/QuotationPage.tsx` (E.5 — nhãn mô hình)
- `src/pages/BidsPage.tsx` (E.7)
- `src/components/RequirementMatrix.tsx` (E.8)
- `src/components/WbsRowEditor.tsx` (đã xóa — không còn dùng)
- `src/App.test.tsx` (test E.1 + sửa test WBS dùng getByDisplayValue + bỏ onEditWbs)

## Kiểm tra
- `npm test`: **14 passed** (chạy 2 lần).
- `npm run build` (tsc + vite): **sạch** (chạy 2 lần; lần 1 lỗi TS `bid possibly undefined` ở `pipelineAdvanced` — đã sửa bằng `bid?.status ?? ''`).

## Lưu ý cho tester (bước kế tiếp)
- WBS: tên/vai trò/giai đoạn/man-day sửa trực tiếp trong dòng; "+ Thêm task" cuối mỗi nhóm; "Lưu thay đổi" gom 1 lần; sau lưu tổng man-day + lịch đổi (kiểm tra bằng cách sửa man-day 1 lá rồi lưu).
- Báo giá: ô "Dự phòng (%)" hiện 20 sau khi tải; "Tạm tính" ≠ tổng giá; dòng thuế theo chế độ; "Gợi ý điều chỉnh: giảm X%" khi giá cao hơn ngân sách.
- Câu hỏi: trả lời vòng 1 đủ → pipeline chạy tiếp, không có vòng 2 (mock dừng); trả lời chứa "未定" → có vòng 2 + lý do hiển thị.
- Thẻ KPI: Requirement "36 · 94%" (◎19 ○15 / 36 đã đánh giá).
- Danh sách: hồ sơ "Chờ duyệt kỹ thuật/giá" đếm ở thẻ "Chờ duyệt"; bảng không tràn ở 1280px.
- Tab Đáp ứng: cột "Thành phần" hiện nhãn Việt hoặc "—", không hiện "none".
- Console: không còn 409 khi mở hồ sơ đang chạy.