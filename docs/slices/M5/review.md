# Review — Slice M5: Proposal, báo giá và cổng duyệt

| Thuộc tính | Giá trị |
|---|---|
| Slice | M5 — Proposal + báo giá + cổng duyệt |
| Ngày review | 2026-10-10 |
| Vai trò | Senior Reviewer |
| Phạm vi | Backend, frontend và tài liệu M5 sau remediation |
| Phương pháp | Đối chiếu `AGENTS.md`, `spec.md`, `test_report.md`, `fix_log.md`; discovery bằng vibegraph MCP |

## Tóm tắt

Các acceptance command và build được ghi nhận là PASS trong `fix_log.md`, nhưng review phát hiện các sai lệch chức năng còn tồn tại so với contract frozen M5. Các vấn đề dưới đây cần được sửa trước khi merge.

## Findings

### HIGH — Engine chưa thực hiện contract đa tiền tệ, FX và so sánh ngân sách

- **Vị trí:** `backend/app/services/quotation_engine.py:17-33`, đặc biệt dòng 19, 27-30; `backend/app/services/quotation_engine.py:38`
- **Bằng chứng:** Engine luôn chọn `rates[role]["offshore"]`, không chọn onsite theo hồ sơ; ghi `fx_rate_value=1.0`; `quotation_to_out` trả `pair="VND/VND"`; budget luôn có `difference=None` và không quy đổi; grand total chỉ làm tròn theo một `rounding.unit`.
- **Tác động:** Không đáp ứng M5 §1.1, §2.1 và acceptance §5.2 cho VND/JPY/USD, FX có ngày hiệu lực, yen rounding và chênh lệch ngân sách. UI có thể hiển thị một báo giá hình thức nhưng không phản ánh tiền tệ hoặc ngân sách khách.
- **Cách sửa cụ thể:** Đưa currency/onsite-offshore/FX date vào input hoặc nguồn bid đã frozen; chọn đúng rate card entry và FX snapshot; tính budget difference trong cùng currency quy đổi; lưu `fx_rate` và pair thực tế trong snapshot; dùng quy tắc rounding/tax theo currency và bổ sung test cho VND, JPY, USD, FX khác ngày, onsite và budget có/không có.

### HIGH — Sau khi duyệt giá, proposal không được code render bảng giá vào draft

- **Vị trí:** `backend/app/services/proposal_service.py:17-18, 20-26`; `frontend/src/pages/ProposalPage.tsx:17`; `frontend/src/pages/QuotationPage.tsx:15-16`
- **Bằng chứng:** `to_out` chỉ trả `price_gate` là `approved|placeholder`; không ghép quotation/schedule server-side vào sections. Proposal page chỉ render năm textarea và `PriceGateNotice`; chỉ `QuotationPage` hiển thị `grand_total` khi bid đã `price_approved`.
- **Tác động:** Vi phạm M5 §1.1, §2.5 và §5.2: yêu cầu “code điền bảng giá khi đã duyệt giá”, nhưng proposal vẫn không có bảng giá chính thức sau approval. Price gate hiện chỉ là cờ UI, không phải renderer customer-facing hoàn chỉnh.
- **Cách sửa cụ thể:** Tách sections do người dùng chỉnh khỏi các block server-rendered; khi `price_approved`, backend render/ghép bảng quotation và các số liệu schedule từ snapshot vào output proposal; khi chưa approved, render đúng `[Presales điền]` và loại bỏ toàn bộ block số tiền. Thêm test API trước/sau approval và reload để chứng minh không lộ số tiền trước gate.

### HIGH — Pre-approval checks trong approval service không dùng bộ check M5 đầy đủ

- **Vị trí:** `backend/app/services/approval_service.py:12-16`
- **Bằng chứng:** `_checks` chỉ kiểm tra `total` có khác 0 để gắn `effort_within_20pct`, và `items` có tồn tại để gắn `pm_qa_present`; nó không gọi `check_engine.check_wbs`, không tính deviation ±20%, không kiểm tra PM/QA theo phase, cycle hoặc leaf limit. Check `schema_valid` luôn là `pass`.
- **Tác động:** `price()` ở `backend/app/services/approval_service.py:30-34` có thể cho duyệt giá đối với WBS sai schema, lệch quá ±20%, thiếu PM/QA hoặc có lỗi cấu trúc nếu vẫn có item và man-day. Điều này làm mất ý nghĩa của `CHECK_FAILED` và trái M5 §1.1, §2.3, §5.3.
- **Cách sửa cụ thể:** Dùng một check engine duy nhất, chuyển WBS đã persist sang `check_engine.check_wbs` và map từng kết quả thành `checks_report`; phân biệt `fail` với `warning`; chỉ cho approved khi không có fail. Bổ sung regression tests cho effort lệch, thiếu PM, thiếu QA, cycle/schema invalid và case warning M6.

### MEDIUM — Snapshot reference chưa đảm bảo bất biến theo approval và dễ tạo nhiều quotation ngoài ý muốn

- **Vị trí:** `backend/app/services/quotation_engine.py:31-34`; `backend/app/api/routers/quotation.py:11-15`; `backend/app/services/approval_service.py:33-35`
- **Bằng chứng:** Mỗi lần `calculate_quotation` đều tạo `ReferenceSnapshot` mới và quotation mới. GET quotation khi chưa có row cũng tính và persist; approval lại tính thêm một quotation. `quotation_to_out` trả `rate_card_version: 1` hard-code thay vì lấy version từ snapshot.
- **Tác động:** Có thể phát sinh nhiều quotation/snapshot cho cùng một bid, trace không phản ánh version thực tế, và khó xác định snapshot nào là giá đã được manager duyệt. Test hiện tại chỉ chứng minh reference snapshot được giữ, chưa chứng minh approved quotation là bản bất biến duy nhất.
- **Cách sửa cụ thể:** Tách “preview calculation” khỏi “persist approved quotation”; chỉ tạo snapshot khi có nghiệp vụ cần lưu, gắn quotation/approval cụ thể với snapshot và trả version từ payload. Thêm test gọi GET nhiều lần, approval, unlock/re-approval và kiểm tra snapshot/quotation lineage.

### MEDIUM — Service-layer authorization cho technical approval không tự bảo vệ SoD

- **Vị trí:** `backend/app/api/routers/approvals.py:10-13`; `backend/app/services/approval_service.py:17-24`
- **Bằng chứng:** Router kiểm tra `identity.role == "ai_developer"`, nhưng service `tech()` nhận `actor: str` và không nhận/kiểm tra role. Các caller nội bộ hoặc test gọi service trực tiếp có thể ghi approval kỹ thuật với actor bất kỳ.
- **Tác động:** Contract nói danh tính authoritative lấy từ header và approval role phải được enforced. Enforcement chỉ ở HTTP route làm service dễ bị gọi sai trong pipeline/background code hoặc endpoint mới.
- **Cách sửa cụ thể:** Truyền `Identity` vào service hoặc kiểm tra role ở một authorization boundary dùng chung; giữ router chỉ làm dependency injection. Thêm test service-level cho actor không phải `ai_developer` và kiểm tra audit actor/role.

### LOW — Tài liệu acceptance còn mô tả blocker cũ sau remediation

- **Vị trí:** `docs/slices/M5/test_report.md:24-31, 44-49, 75-82`; đối chiếu `docs/slices/M5/fix_log.md:28-37, 41-55`
- **Bằng chứng:** `test_report.md` vẫn ghi 8 module test không collect và Preview trả 404, trong khi `fix_log.md` ghi các test đã bổ sung, route đã hoạt động và full suite 148 tests pass.
- **Tác động:** Người đọc không thể phân biệt trạng thái trước và sau fix; tài liệu M5 không phản ánh verification hiện tại và dễ dẫn tới quyết định sai.
- **Cách sửa cụ thể:** Giữ report QA làm historical record nhưng thêm mục “retest sau remediation” hoặc phụ lục liên kết tới `fix_log.md`, ghi rõ trạng thái cuối của từng TC-ID và các case UI còn BLOCKED do browser.

## Đối chiếu AGENTS.md

- **Rule 1 — No invented numbers:** Chưa đạt đầy đủ ở quotation engine vì FX/currency/onsite/budget đang bị hard-code hoặc bỏ qua.
- **Rule 2 — Structured LLM:** B6 dùng schema và bounded retry; chưa thấy lỗi HIGH trong phần đã review.
- **Rule 3 — One LLM gateway:** Luồng B6 đi qua `complete_with_retry`; quotation, approval và proposal edit không gọi LLM theo code đã kiểm tra.
- **Rule 4 — Ask instead of guess:** Approval checks yếu có nguy cơ cho qua dữ liệu không đủ thay vì chặn rõ ràng.
- **Rule 5 — Price gate:** Placeholder UI có, nhưng renderer chính thức sau approval còn thiếu.
- **Rule 6 — Privacy:** Gateway có `mask_text`; cần giữ test B6 cụ thể cho customer text/PII khi mở rộng prompt.
- **Rule 7 — Languages:** B6 truyền `customer_language`, nhưng review chưa có bằng chứng đủ cho renderer proposal sau approval trong cả `vi/en/ja`.
- **Rule 8 — Done means proven:** Automated checks pass theo fix log; các finding HIGH cho thấy acceptance chức năng chưa đủ chứng minh.
- **Rule 9 — Keep simple:** Không phát hiện queue/vector DB/auth server mới trong phạm vi review.
- **Rule 10 — Root-relative API:** Không phát hiện hard-coded localhost trong discovery M5; frontend client dùng API layer hiện có.

## Test và bằng chứng đã xem

- `docs/slices/M5/spec.md`: frozen API, acceptance commands và manual scenarios.
- `docs/slices/M5/test_report.md`: kết quả QA trước remediation, gồm 15 case UI BLOCKED do thiếu Chromium.
- `docs/slices/M5/fix_log.md`: retest sau remediation, 148 backend tests, frontend build, `make test`, `make quality-gate` PASS.
- Vibegraph symbols/call paths: `calculate_quotation`, `quotation_to_out`, `price`, `_checks`, `tech`, `unlock_bid`, `run_proposal`, `ProposalOutput`, `proposal_service.update`, `ProposalPage`, `QuotationPage`.

## Verdict

**CHANGES REQUIRED**

Không phát hiện CRITICAL, nhưng có 3 finding HIGH liên quan trực tiếp đến contract báo giá/approval và price gate. Chưa thể merge/approval cho M5 cho đến khi developer sửa các finding HIGH và bổ sung regression tests tương ứng. Các finding MEDIUM nên xử lý cùng vòng sửa vì ảnh hưởng auditability và tính bất biến của giá.

## Handoff Note

Reviewer đã hoàn tất document review M5. Deliverable là file này; không thay đổi code ứng dụng. Handoff cho Developer: xử lý các finding HIGH trước, sau đó chạy lại acceptance commands, thêm retest cho quotation currency/budget, proposal sau approval và pre-approval checks. Các case Playwright còn BLOCKED cần tiếp tục ghi nhận riêng do môi trường browser.

**Task Review complete. Awaiting prompt for the next role.**
