# Review Đợt 7 P0

Ngày review: 2026-10-11  
Vai trò: senior reviewer  
Phạm vi: review code, contract, tài liệu handoff và evidence runtime của Đợt 7.

## Verdict

**CHƯA SẴN SÀNG MERGE / APPROVAL.**

Implementation có nhiều regression test và frontend build/type-check pass theo handoff, nhưng evidence Preview chưa chứng minh được luồng end-to-end. Quan trọng hơn, code hiện tại còn một contract mismatch trực tiếp ở `/api/settings`, phù hợp với lỗi runtime đã ghi nhận. P0-6 cũng chưa đạt runtime dù đã có code extractor.

## Findings

### [Cao] P0-3: `/api/settings` vẫn không trả `payload`

- **Tham chiếu:** `backend/app/api/routers/settings.py:14-15`, `backend/app/schemas/api_schemas/settings.py:20-21`.
- `get_settings()` chỉ trả `{"keys": settings_service.list_settings(session)}`; `SettingsResponse` cũng chỉ khai báo `keys`.
- Frontend `SettingsPage` hiện vẫn khởi tạo từ `query.data.keys` và `yaml_preview` (không trực tiếp đọc `payload`), trong khi handoff frontend mô tả đã nối vào `payload`. Contract backend trong code cũng không có field `payload`. QA đã xác nhận runtime `GET /api/settings` HTTP `200` nhưng chỉ có `keys`, không có `payload`.
- **Ảnh hưởng:** P0-3 fail ở runtime; bảng effort/rate card/factors không thể được xác nhận là đọc đúng cấu trúc mới và CRUD chưa thể kiểm tra. HTTP `200` không làm contract đạt.
- **Khuyến nghị:** đồng bộ schema, router, service và frontend trên một response contract duy nhất; thêm API test kiểm tra payload đầy đủ của cả ba bảng và test PUT rồi GET lại dữ liệu đã lưu. Không nên giữ fallback YAML như cách che giấu mismatch khi contract mới là yêu cầu bắt buộc.

### [Cao] P0-6: extractor có trong code nhưng runtime không persist được mốc khách

- **Tham chiếu:** `backend/app/pipeline/steps/b1_intake.py:32-55,111-112`; `backend/app/pipeline/steps/b1_intake.py:58-145`.
- `_apply_customer_constraints()` được gọi sau LLM result và trước commit, đồng thời có regex cho budget/start/MVP/Production. Tuy nhiên QA runtime với RFP Nhật có các mốc `2027年1月`, `2027年6月`, `2027年9月`, trong khi `GET /api/bids/107` vẫn trả cả ba field mốc khách là `null`.
- **Ảnh hưởng:** lịch mặc định không thể dựa trên mốc khách trong luồng thật; P0-6 fail. `update_schedule()` chỉ fallback về `bid.customer_schedule_start` nếu field đã được persist (`backend/app/services/schedule_service.py:162`), nên null runtime sẽ dẫn đến fallback `date.today()`.
- **Khuyến nghị:** thêm fixture test đúng nội dung `ja_rfp.docx`/RFP runtime và assertion cả ba field sau pipeline; xác minh text được extractor đọc thực sự từ attachment. Không chấp nhận chỉ test regex với chuỗi đơn giản nếu sample runtime vẫn null.

### [Cao] Evidence chưa đủ để chấp thuận các P0 UI và downstream

- **Tham chiếu:** `docs/ui/dot7_check.md:14-16,20-30`; `docs/ui/handoff_dot7_qa.md:19-24`.
- Chromium không khả dụng nên P0-1, P0-4, P0-9 và phần DOM của P0-2 bị Blocked. Pipeline mẫu dừng ở `waiting_clarification`, nên P0-5, P0-7 và P0-8 không có dữ liệu downstream thật để kiểm tra.
- Đây là phân loại evidence đúng, không phải lỗi QA. Tuy nhiên theo `AGENTS.md:26-27`, feature chỉ được coi là done khi automated tests pass **và** chạy được trong Preview. Vì vậy không thể dùng handoff implementation hoặc unit tests để thay thế acceptance runtime.
- **Khuyến nghị:** chạy lại Preview bằng browser khả dụng, hoàn tất clarification hợp lệ, rồi ghi evidence cho quotation/schedule/proposal và DOM. Không tạo screenshot hoặc đánh dấu Pass dựa trên code.

### [Trung bình] SSE clarification không invalidate toàn bộ tab

- **Tham chiếu:** `frontend/src/pages/BidDetailPage.tsx:126-138`; `frontend/src/hooks/usePipelineEvents.ts:31-57`.
- Khi nhận `clarify`, trang chỉ invalidate `bid`, `questions`, và `evaluations`, sau đó tắt stream. Khi nhận `done`, mới invalidate effort, quotation, schedule, proposal, WBS, history, attachments và danh sách bids.
- Nếu `clarify` được coi là một lần pipeline kết thúc ở trạng thái chờ trả lời, các tab downstream có thể giữ cache cũ; nếu chỉ `done` mới là completion thì behavior này cần được ghi rõ trong acceptance contract. QA chưa thể phân định bằng browser.
- **Khuyến nghị:** xác định rõ event completion contract. Với event kết thúc mỗi pipeline phase, invalidate các query phụ thuộc phase đó; thêm test mô phỏng SSE `clarify` và `done` để chứng minh tab không cần F5.

### [Thấp] Handoff và source đang mô tả contract không đồng nhất

- **Tham chiếu:** `docs/ui/handoff_dot7_backend.md:13`, `docs/ui/handoff_dot7_frontend.md:23-26`, đối chiếu source backend ở trên.
- Handoff backend nói `/api/settings` đã trả `payload`, còn source và Preview evidence chứng minh điều ngược lại. Đây là drift tài liệu/code làm giảm độ tin cậy của handoff.
- **Khuyến nghị:** sau khi sửa contract, cập nhật handoff bằng response mẫu đã kiểm chứng; không ghi DONE cho P0-3 trước khi runtime GET/PUT/GET pass.

## Đối chiếu 9 P0

| P0 | Kết quả review | Cơ sở |
|---|---|---|
| 1. `+ Tạo hồ sơ` | Chưa xác nhận | Source có style rõ tại `frontend/src/components/Sidebar.tsx:33-52`; browser blocked. |
| 2. SSE/invalidate và empty state | Partial, chưa chấp thuận | Có invalidate khi `done`, nhưng browser blocked; clarification invalidation hẹp hơn. |
| 3. Settings | **Fail** | Backend route/schema không có `payload`; runtime xác nhận mismatch. |
| 4. Nhãn đáp ứng | Chưa xác nhận | Handoff/source claim mapping; browser blocked. |
| 5. Budget guard | Chưa xác nhận runtime | Handoff/test claim; sample budget null và pipeline chưa tới quotation. |
| 6. Mốc khách/lịch bắt đầu | **Fail runtime** | Extractor tồn tại nhưng ba field runtime null. |
| 7. Không so với submission deadline | Chưa xác nhận runtime | Source schedule path không truyền deadline theo handoff; schedule endpoint runtime 409. |
| 8. Proposal 8 mục/dữ liệu dossier | Chưa xác nhận runtime | `run_proposal` có context/token replacement; proposal runtime `sections=[]`. |
| 9. `man-day` | Chưa xác nhận | Source/handoff claim; browser blocked. |

## Quy tắc nền tảng

- **LLM và số liệu:** không thấy finding mới về việc để LLM sinh số. Proposal prompt cấm số cụ thể và `_render_customer_facts()` thay token bằng dữ liệu code-owned (`backend/app/pipeline/steps/b6_proposal.py:12-32`). Cần runtime verification sau clarification.
- **Structured output:** handoff ghi schema validation/retry; chưa có browser evidence, nhưng không phát hiện regression trực tiếp trong scope review.
- **Privacy:** intake dùng `mask_text` trước prompt (`backend/app/pipeline/steps/b1_intake.py:74,89`); không phát hiện secret trong evidence. Sample key `ja_email` là public fixture key, không phải credential.
- **Frontend networking:** code path được mô tả dùng API root-relative; không phát hiện hardcoded localhost trong các symbol đã review.

## Residual risks

- Chưa biết liệu sau khi trả lời đủ 5 clarification, pipeline mock có tạo được quotation, schedule và proposal đúng contract hay không.
- Chưa có DOM/browser evidence cho menu, empty state, labels, proposal headings và `man-day`.
- Có nguy cơ test fixtures không đại diện cho attachment text thật của mẫu Nhật, đặc biệt với extractor milestone.
- Settings response contract có thể tiếp tục fail dù frontend tests pass nếu tests chỉ mock response `keys`.
- Cần kiểm tra price gate và placeholder proposal sau khi pipeline hoàn tất; review này không coi dữ liệu downstream chưa tồn tại là pass.

## Required follow-up before approval

1. Sửa và test contract `/api/settings` end-to-end, sau đó GET/PUT/GET trên Preview.
2. Sửa hoặc chứng minh extraction mốc Nhật bằng fixture giống runtime và xác nhận ba field đã persist.
3. Chạy browser với Chromium khả dụng, hoàn tất clarification, kiểm tra đủ 9 P0 trên Preview thật.
4. Bổ sung test cho event semantics của SSE và query invalidation sau `clarify`/`done`.
5. Cập nhật handoff sau khi evidence mới tồn tại; giữ verdict `BLOCKED` cho đến lúc đó.

## Deliverable Completeness Check

| Yêu cầu reviewer gốc | Đã đáp ứng | Evidence trong deliverable |
|---|---|---|
| Đọc `AGENTS.md`, `review_luot4.md`, `dot7_check.md` và handoff liên quan | Có | `handoff_dot7_reviewer.md:11-16`; report nêu rõ phạm vi và phương pháp. |
| Dùng vibegraph MCP trước code discovery | Có | `handoff_dot7_reviewer.md:14-15`; các finding có symbol/file/line đối chiếu. |
| Review theo severity, regression, contract, LLM-number/privacy | Có | `dot7_review.md:13-48`, `64-69`. |
| Kiểm tra completeness đủ 9 P0 | Có | `dot7_review.md:50-62`. |
| Đánh giá độ tin cậy evidence thật, không tạo evidence giả | Có | `dot7_review.md:30-35`, `handoff_dot7_reviewer.md:16`, `26-30`. |
| Verdict rõ ràng và residual risks | Có | `dot7_review.md:7-11`, `71-85`. |
| Ghi report reviewer và handoff rồi dừng đúng boundary | Có | Hai file deliverable này; không sửa source, không chạy role khác. |

Kết luận completeness: không còn thiếu deliverable reviewer nào theo yêu cầu gốc. Các mục chưa được approve là do blocker/evidence runtime đã được ghi rõ, không phải do bỏ sót trong report.
