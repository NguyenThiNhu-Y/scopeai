# Review Đợt 11

Ngày: 2026-10-12

## Kết luận

**Đạt có điều kiện.** Các yêu cầu frontend A/B/C đã được triển khai và blocker contract về ngày gửi/ghi chú đã được sửa. Build, unit test frontend, backend Dot 9 và API Preview đều pass. QA đã hoàn tất phần API; kiểm chứng trực quan trên browser vẫn Blocked vì môi trường thiếu browser executable. Chưa nên gọi là pass hoàn toàn do thiếu test UI Đợt 11 và còn các rủi ro trung bình được ghi dưới đây.

## Findings đã xử lý

| Finding | Xử lý |
|---|---|
| `ProposalVersionOut` thiếu `sent_at` | Đã thêm `sent_at` nullable vào schema và frontend type |
| Không có ghi chú khi đánh dấu gửi | Đã thêm `sent_note` model/schema, request body, Changelog note, input và hiển thị UI |
| Translation dùng fetch trực tiếp | Đã thêm `translateProposal` vào API client dùng envelope lỗi chung |
| History tải toàn bộ rồi lọc client | Đã truyền `bid_id` vào `getHistory` |
| Có thể sửa ngôn ngữ dịch nhưng PUT ghi đè bản gốc | Đã khóa chỉnh sửa khi ngôn ngữ khác ngôn ngữ gốc |

## Verification

- `frontend npm run build`: pass sau sửa contract.
- `frontend npm test -- --run`: 14/14 pass sau sửa contract.
- `backend python3 -m pytest -q tests/test_dot9_backend.py`: 7 passed.
- `backend pytest -q`: toàn bộ backend suite pass; chỉ còn cảnh báo deprecation `httpx`/`starlette`.
- Preview `GET /api/health`: HTTP 200, database `ok`, `llm_provider=mock`.
- Preview `GET /api/settings`: trả đủ 5 key Đợt 11.
- Preview tạo và gửi version: HTTP 200, trả `sent_at` và `sent_note` đúng dữ liệu kiểm tra.
- Preview Bid/No-bid invalid total: HTTP 400 khi tổng là 101; payload 30/40/30 được restore.
- Preview tạo version: trả đúng chuỗi `1.0 → 1.1 → 2.0`.
- Preview translation: thiếu `en` được tạo qua endpoint dịch, HTTP 200 và đủ section.
- Preview proposal document: `page_size=A4`, `cover=true`, có table of contents và `printable=true`.
- Preview deal stage: stage hợp lệ `qualified` lưu HTTP 200; schema không cho khôi phục `null` về trạng thái rỗng ban đầu.
- Browser automation/screenshot: bị chặn vì Playwright báo thiếu browser executable; không tạo screenshot giả.

## Findings còn lại

| Mức | Finding | Bằng chứng | Đề xuất |
|---|---|---|---|
| Trung bình | Chưa có test frontend tự động cho các acceptance path chính của Đợt 11 | `frontend/src/App.test.tsx` chưa có test cho `SettingsPage`, `ApprovalsPage` hoặc `ProposalPage` | Thêm test component/integration cho validation tổng 100, refetch sau save, advisory suggestion, version/send-note và translation fallback |
| Trung bình | Nút `Xác nhận` dùng `decision` state mặc định là `bid`; chưa hydrate quyết định hiện tại | `frontend/src/pages/ApprovalsPage.tsx:111-113` gửi `decision` state và toàn bộ criteria; UI không hiển thị cảnh báo khi đã có decision | Hydrate state từ decision backend, hiển thị trạng thái hiện tại và yêu cầu xác nhận lại khi đổi decision |
| Thấp | A4 dialog chưa có focus management, đóng bằng Escape hoặc TOC anchor | `frontend/src/pages/ProposalPage.tsx:192-196` có `role=dialog` nhưng chỉ có nút Đóng; TOC chỉ là danh sách | Thêm focus vào dialog, xử lý Escape, `aria-labelledby` và anchor/id cho từng mục |
| Thấp | A4 TOC dựng từ `SECTION_KEYS` thay vì ưu tiên `document.table_of_contents` từ API | `frontend/src/pages/ProposalPage.tsx:195`; metadata API chỉ được ghi nhận trong QA | Dùng metadata API khi có, fallback sang section keys khi thiếu để tránh lệch thứ tự |

Các finding trên là rủi ro từ code review; browser hiện không khả dụng nên không kết luận đây là lỗi runtime.

## Giới hạn còn lại

- Chưa thể xác nhận thao tác trực quan CRUD cả 5 tab Settings, fallback từng section, chọn ngôn ngữ trước khi soạn, nút dịch, trang A4 và thao tác in vì browser executable không khả dụng.
- Không có screenshot runtime; đây là giới hạn môi trường, không phải bằng chứng giao diện pass.
- Fixture bid `80` hiện có dữ liệu QA: versions `1.0/1.1/2.0`, version `1.0` đã gửi với ghi chú `QA Đợt 11`, translation `en`, deal stage `qualified`.

## Ma trận kết luận

| Phạm vi | Kết luận review | Trạng thái kiểm chứng |
|---|---|---|
| A. Settings: 5 tab, company, template, standard content, case study, Bid/No-bid | Đạt có điều kiện | Code/API đã đối chiếu từng nhóm; UI CRUD, từng trường Word/Excel/vi-en-ja và responsive chưa kiểm chứng |
| B. Quy trình, Bid/No-bid, deal stage, version | Đạt có điều kiện | API đã kiểm chứng; cần test UI và xử lý rủi ro decision state |
| C. Proposal, translation, A4/print | Đạt có điều kiện | API/code đã đối chiếu; browser/print chưa kiểm chứng |
| Regression/build | Đạt | Frontend 14/14, build sạch, backend full suite pass theo checklist |

Không có finding mức Critical/High và không thấy mã thô hoặc thông tin bí mật bị đưa vào UI trong phạm vi đã đọc. Kết quả phê duyệt cuối cùng vẫn phụ thuộc kiểm thử browser thật.

## Đối chiếu đầy đủ với yêu cầu gốc

| Yêu cầu gốc | Đã có trong deliverable | Thiếu hoặc giới hạn |
|---|---|---|
| A. Công ty: tên và quy tắc đặt tên file | Có `CompanyEditor`, key `company`, và TC-A02 | Chưa kiểm chứng nhập/lưu trên browser |
| A. Template: Word/Excel, mẫu có sẵn, trạng thái hợp lệ | Có `TemplatesEditor`, key `templates`, và TC-A03 | Chưa kiểm chứng từng loại mẫu/trạng thái trên browser |
| A. Nội dung chuẩn vi/en/ja | Có `ContentEditor`, selector ngôn ngữ, và TC-A04 | Chưa kiểm chứng chuyển ngôn ngữ và persist trên browser |
| A. Case study thêm/sửa/xóa | Có `CaseStudiesEditor` và TC-A05 | Chưa kiểm chứng CRUD/refetch trên browser |
| A. Bid/No-bid tổng 100 | Có validation code, API evidence, và TC-A06 | Chưa kiểm chứng thông báo UI |
| B. Criteria, weight, suggestion advisory, confirmer, Xác nhận | Có code/API evidence và TC-B01 | Chưa kiểm chứng UI; còn finding decision state ở trên |
| B. Deal stage | Có code/API evidence và TC-B02 | API không reset được `null`; UI chưa kiểm chứng |
| B. Version 1.0 → 1.1 → 2.0, sent date/note | Có code/API evidence và TC-B03/TC-B04 | UI chưa kiểm chứng |
| C. Chọn ngôn ngữ trước khi soạn | Có code evidence và TC-C01 | UI chưa kiểm chứng |
| C. translations, fallback, nút dịch | Có code/API evidence và TC-C02/TC-C03 | UI chưa kiểm chứng từng section |
| C. A4, bìa, mục lục, in | Có code/CSS/API evidence và TC-C04 | Browser print chưa kiểm chứng; còn finding accessibility/TOC |
