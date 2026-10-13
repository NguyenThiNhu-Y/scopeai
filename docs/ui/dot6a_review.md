# Review Đợt 6a

Ngày review: 2026-10-11  
Vai trò: Senior reviewer  
Phạm vi: backend, frontend, test và tài liệu của Đợt 6a; đối chiếu `AGENTS.md`, mục 5
`docs/ui/review_luot3.md`, API contract cập nhật và `docs/ui/dot6a_check.md`.

Phạm vi chức năng của bước này là bốn nhóm được yêu cầu trực tiếp trong workflow:
báo giá, lịch, Q&A sheet và email gửi khách. Các mục P1 khác của mục 5 như dịch
proposal, xuất PowerPoint, khả thi/kiến trúc không thuộc Dot 6a này và không được
dùng để suy ra verdict.

## Verdict

**CHANGES REQUIRED — code fixes applied; Preview acceptance remains incomplete**

Các sửa đổi trong bước này đã xử lý lỗi import Q&A theo mã + vòng, giới hạn file và
warning test frontend. Tuy nhiên chưa thể phê duyệt toàn bộ vì Preview chưa cung cấp
browser evidence hoàn chỉnh cho mẫu Nhật; verdict chỉ có thể đổi sau khi tester chạy
đủ walkthrough thực tế.

## Findings

### Coverage matrix

| Yêu cầu gốc | Source/test đã rà soát | Kết luận review |
|---|---|---|
| Trọn gói/T&M/ODC | `quotation_engine.calculate_quotation`, `QuotationSettingsIn`, `test_dot6a_backend_contract` | Có implementation/test; chưa có đủ Preview evidence |
| VND/JPY/USD | `QuotationSettingsIn`, FX trong `calculate_quotation`, `BidPlanTab.QuotationEditor` | Có validation/control; cần smoke Preview cả ba tiền tệ |
| Dự phòng, onsite, price-to-win -50..+200 | schema và control tại `BidPlanTab.tsx` | Có giới hạn code/UI; chưa chứng minh thao tác Preview |
| T&M theo tháng, ODC = FTE × tháng | payment plan trong `calculate_quotation`, test T&M/ODC | Có code/test; cần xác minh hiển thị Preview |
| So sánh ngân sách, % chênh lệch, gợi ý điều chỉnh | `quotation_to_out`, bảng ngân sách trong `BidPlanTab` | Có code/UI; dữ liệu mẫu QA đang thiếu budget nên chưa có evidence thật |
| Tính lại bằng code, khóa sau duyệt | `update_quotation_settings`, `ensure_unlocked`, `approval_service.price` | Có guard/test; chưa có walkthrough Preview trước/sau duyệt |
| Go/no-go mặc định 10 ngày làm việc | `ScheduleUpdateIn`, `update_schedule`, contract test | Có code/test; cần xác minh ngày thật trên Preview |
| Mốc MVP/Production theo intake | `Bid.customer_*`, `update_schedule`, contract test | Có code/test; cần xác minh intake mẫu và ngày sớm nhất |
| Form lịch ba ô, Gantt có khoảng nghỉ | `ScheduleMilestones`, `GanttChart` | Có UI/source; chưa có browser evidence |
| Q&A export ngôn ngữ khách, cột trả lời vàng | `export_questions`, backend test | Có code/test; chưa có file mở được từ Preview hiện hành |
| Q&A import, merge, resume pipeline | `import_questions`, `submit_answers`, backend test | Có luồng cơ bản nhưng có finding HIGH về nhiều vòng và MEDIUM về upload |
| Email mock, ngôn ngữ khách, tên do code điền | `email_draft`, `EmailDraft`, gateway/privacy tests | Có code/test; chưa có Preview evidence |
| Email sửa được và Copy | `BidDetailPage` handlers/UI | Có UI/source; chưa có browser evidence |

### 1. RESOLVED — Import Q&A nhiều vòng có thể thất bại khi nhập lại workbook đầy đủ

Trước khi sửa, `backend/app/api/routers/questions.py:64-86` chọn một `round_no`
cho toàn bộ workbook, nên file chứa đồng thời câu đã đóng và câu đang chờ không thể
được gộp an toàn.

**Đã sửa:** workbook có cột mã câu hỏi và vòng; import đối chiếu đúng cặp mã + vòng,
bỏ qua câu đã đóng/mã sai/ô trống và trả `warnings`; câu đang chờ chỉ được submit
một lần. Đã bổ sung test thiếu cột, mã sai, nhập lại và giới hạn.

### 2. RESOLVED — Import workbook chưa có giới hạn kích thước hoặc kiểm soát tài nguyên

Trước khi sửa, `backend/app/api/routers/questions.py:61-75` đọc toàn bộ upload vào
memory mà chưa có giới hạn riêng cho kích thước hoặc số dòng Q&A.

**Đã sửa:** đọc tối đa 5 MB, giới hạn 200 dòng, bắt lỗi workbook hỏng và trả thông
báo tiếng Việt. Giới hạn upload attachment hiện có không bị thay đổi.

### 3. RESOLVED IN DOCUMENTATION — Evidence QA trong `dot6a_check.md` không đồng bộ với source và test

Bản cũ của `docs/ui/dot6a_check.md:14-15, 84-110` ghi route Q&A export/import/email-draft
không tồn tại trong runtime. Trong source hiện tại, các route đã được khai báo tại:

- `backend/app/api/routers/questions.py:43-62` — export workbook theo ngôn ngữ khách,
  cột trả lời màu vàng.
- `backend/app/api/routers/questions.py:65-151` — import và resume pipeline.
- `backend/app/api/routers/questions.py:163-186` — email draft qua gateway/schema.

Test backend tương ứng cũng tồn tại và đã chạy pass trong focused run, gồm
`test_questions_export_is_customer_language_and_answer_column_is_yellow`,
`test_questions_import_merges_answers_and_resumes_pipeline` và
`test_customer_email_draft_is_structured_customer_language_and_editable`.

**Đã sửa tài liệu:** `dot6a_check.md` đã thay bản cũ bằng trạng thái code/test mới,
ghi rõ route đã có và tách riêng Preview/browser evidence chưa hoàn tất.

Lưu ý contract: `backend/app/exporters/requirements_xlsx.py:23-69`
(`render_requirement_workbook`) là đường xuất lại workbook requirement gốc với các
cột đánh giá, không thay thế endpoint Q&A Dot 6a mã + vòng + câu hỏi/lý do/trả lời tại
`backend/app/api/routers/questions.py:43-62`. Hai loại workbook phải được kiểm tra
riêng, không dùng evidence của loại này để kết luận cho loại kia.

### 4. RESOLVED — Test frontend có cảnh báo query undefined và cập nhật state ngoài `act`

Đã thêm quotation fixture mặc định, bọc thao tác import/export bằng `act`/`waitFor`.
Frontend test còn warning React Router future flags, nhưng đó là warning chuyển tiếp
của framework và không liên quan Dot 6a.

Các khuyến nghị về fixture quotation và `waitFor`/`act` đã được áp dụng; chỉ còn
React Router future warnings ngoài phạm vi Dot 6a.

## Đối chiếu chức năng

### Báo giá

- Có `PUT /api/bids/{id}/quotation`, schema giới hạn model `fixed_price|tm|odc`, tiền
  tệ `VND|JPY|USD`, contingency `0..100`, onsite `0..1` và price-to-win `-50..200`
  tại `backend/app/schemas/api_schemas/quotation.py:9-17`.
- Tính toán nằm trong code tại `calculate_quotation`, gồm blended rate, contingency,
  FX, payment plan T&M và FTE-tháng ODC; không thấy số effort/giá do schema LLM sinh.
- So sánh ngân sách, phần trăm chênh lệch và gợi ý điều chỉnh được tính trong
  `quotation_to_out:108-140`.
- `ensure_unlocked` được gọi trước khi cập nhật; approval giá đặt `locked=true` tại
  `approval_service.price:34-56`. Price gate export có test placeholder riêng.
- UI có control và trạng thái khóa tại `frontend/src/components/BidPlanTab.tsx:29-52,
  73-85`, nhãn tiếng Việt và API root-relative.
- Chưa có bằng chứng Preview hiện hành cho đủ ba model, ba currency và thao tác trước/
  sau approval; đây là gap evidence, không được suy ra từ unit test.

### Lịch

- Schema có mặc định go/no-go 10 ngày làm việc, các ngày MVP/Production sớm nhất và
  `gantt_break_interval` tại `backend/app/schemas/api_schemas/schedule.py:43-77`.
- `update_schedule:192-221` tính khoảng sau PoC và ngày sớm nhất theo lịch khách.
- UI hiển thị form khoảng nghỉ, các mốc và Gantt tại `BidPlanTab.tsx:57-59, 87-89`;
  `GanttChart.tsx:68-74, 132-165` render khoảng go/no-go nếu response có dữ liệu.
- Cần xác minh Preview với hồ sơ Nhật để chứng minh ngày thật và khoảng nghỉ trên UI.

### Q&A và email

- Export đúng ngôn ngữ khách, mã + vòng + câu hỏi/lý do/trả lời và fill vàng tại `questions.py:43-62`.
- Import đối chiếu mã + vòng, giới hạn 5 MB/200 dòng, bỏ qua dòng không hợp lệ có
  warning và không tạo trả lời trùng.
- Email dùng `EmailDraft` schema, gateway retry và `mask_text` trước khi gửi prompt;
  tên khách/người gửi được code điền tại `questions.py:163-186`.
- UI có export, import, nút soạn, vùng chỉnh sửa và Copy tại
  `frontend/src/pages/BidDetailPage.tsx:244-298, 540-543`.
- Chưa có Preview evidence hiện hành cho mở file `.xlsx`, màu ô, chỉnh sửa và Copy.

## Quality checks

- Focused backend Q&A tests: **18 passed** trong lần chạy trực tiếp; lần chạy qua wrapper
  trước đó báo `No tests collected`, nên không dùng output wrapper làm evidence pass.
- Full backend tests: **230 passed** trong lần chạy raw; wrapper vẫn báo `No tests collected`.
- Frontend tests: **9 passed**; không còn warning query undefined/act của Dot 6a,
  chỉ còn React Router future warnings.
- Frontend build/type-check: **PASS** qua `npm run build`.
- Không gọi LLM thật; các test dùng mock gateway và structured schema.
- Không dùng git command, không tạo screenshot/file evidence giả; source và test đã
  được sửa trong bước này theo đúng yêu cầu fix.
- Browser/Preview evidence vẫn cần tester chạy lại bằng runtime hiện hành; tài liệu QA
  hiện tại không đủ để thay thế bước đó.

## Required follow-up

1. Tester chạy lại Preview với mẫu Nhật và ghi số liệu thật cho ba mô hình, tiền tệ,
   điều chỉnh/chênh ngân sách, Gantt, Q&A hai vòng và email Copy.
2. Reviewer xác nhận lại sau khi browser evidence hoàn tất.
