# Review — M7 Xuất file bằng code

## Phạm vi và căn cứ

- Đã đọc `AGENTS.md`, `docs/slices/M7/spec.md`, `docs/slices/M7/handoff_to_test.md`,
  `docs/slices/M7/test_report.md` và `docs/slices/M7/fix_log.md`.
- Đã review các exporter, export service, router export, ja-check và frontend download flow.
- Kết quả test trong report: 14 PASS, 0 FAIL, 2 BLOCKED. Hai blocker môi trường không thay thế
  cho review contract/code bên dưới.

## Findings

### HIGH — Proposal Word không xuất phụ lục WBS theo contract

- Vị trí: `backend/app/exporters/proposal_docx.py:6-18`
- `render_proposal()` chỉ render cover, mục lục dạng text, các section, assumptions, scope-out và
  quotation. Dữ liệu `data["wbs"]` được đưa vào service nhưng không bao giờ được render vào DOCX.
- Vi phạm phạm vi M7 §1.1 item 2 và acceptance §5.2 bước 2/§5.1: proposal phải có phụ lục WBS.
- Cách sửa cụ thể: thêm heading phụ lục WBS theo locale và bảng lấy trực tiếp từ `data["wbs"]`,
  gồm tối thiểu mã task, tên, phase/parent, role và man-day; các giá trị số phải lấy từ snapshot
  persisted, không tính hoặc sinh bởi LLM. Bổ sung assertion DOCX có các task trong fixture.

### HIGH — Export Word/Excel bị phụ thuộc ngoài ý muốn vào LibreOffice/PDF

- Vị trí: `backend/app/services/export_service.py:40`
- `artifacts()` luôn thực hiện `pdf = docx_to_pdf(word)` trước khi router chọn artifact. Vì vậy
  `GET .../proposal.docx` và `GET .../estimate.xlsx` cũng thất bại nếu LibreOffice/font CJK
  không có, dù hai endpoint này không cần PDF.
- Vi phạm contract §2.2/§2.3, trong đó Word và Excel là artifact độc lập; đồng thời trái với
  mục tiêu lỗi actionable chỉ áp dụng cho PDF. Đây cũng là nguyên nhân khiến môi trường Preview
  thiếu LibreOffice có thể làm hỏng các download không liên quan.
- Cách sửa cụ thể: tách render theo nhu cầu artifact hoặc cache DOCX rồi chỉ gọi
  `docx_to_pdf()` trong endpoint PDF/bundle. Bundle có thể yêu cầu PDF và báo lỗi rõ nếu converter
  thiếu, nhưng Word/Excel phải vẫn tải được độc lập.

### HIGH — Filename dùng ngày hard-code, không phải ngày export

- Vị trí: `backend/app/exporters/filename.py:12-14`
- `export_filename()` mặc định `export_date="2026-10-10"`; mọi export không truyền ngày sẽ mang
  ngày cố định, kể cả sau ngày milestone. Điều này không phản ánh `<ngày>` trong quy tắc tên file
  và tạo metadata sai cho audit/download.
- Cách sửa cụ thể: truyền ngày export do service xác định một lần cho toàn bộ artifact của cùng
  request, hoặc dùng `date.today().isoformat()` tại boundary service; giữ tham số explicit để test
  deterministic có thể cố định ngày. Không để ngày hiện tại được tính khác nhau giữa các artifact.

### MEDIUM — Excel Gantt không render mốc thanh toán và chỉ giữ dữ liệu tuần tối giản

- Vị trí: `backend/app/services/export_service.py:37-39`,
  `backend/app/exporters/estimate_xlsx.py:17-18`
- Service bỏ qua `Schedule.payment_milestones`, chỉ chuyển `tasks_json` thành `[week, name, ""]`.
  Exporter cũng chỉ tạo ba cột text, không đánh dấu payment milestone/deadline và không có biểu
  diễn thanh theo tuần. Vi phạm M7 §2.3 và acceptance §5.2 bước 4/§5.2 bước 8.
- Cách sửa cụ thể: giữ các trường tuần bắt đầu/kết thúc hoặc range từ schedule snapshot, tạo các
  cột tuần ổn định và đánh dấu ô task nằm trong range; thêm hàng/marker cho
  `payment_milestones` và deadline. Test phải assert milestone và ít nhất hai cột tuần có dữ liệu.

### MEDIUM — Ja-check phụ trợ không nhận đủ context để đánh giá context/name

- Vị trí: `backend/app/services/ja_check.py:24-29`
- LLM phụ trợ chỉ nhận chuỗi ghép từ `message_vi` của các issue và context
  `{"customer_language": "ja"}`. Nó không nhận section text, glossary hoặc customer name đã mask.
  Do đó `llm_context` không thể kiểm tra ngữ cảnh thực tế và rule name chỉ kiểm tra hai section
  cố định. Đây không phải lỗi PII leak, nhưng không đáp ứng đầy đủ mô tả B7 §3.1 về input chuẩn hóa.
- Cách sửa cụ thể: gửi context giới hạn, có delimiter rõ giữa dữ liệu hồ sơ và instruction, gồm
  section nghi ngờ, glossary và tên khách hàng sau masking; không gửi binary/toàn văn RFP. Bổ sung
  prompt-capture test kiểm tra PII được mask và context có các trường cần thiết.

### LOW — Router có code style và contract hygiene kém, làm tăng rủi ro bảo trì

- Vị trí: `backend/app/api/routers/exports.py:2,13-23,26-36`
- `Header` được import nhưng không dùng; router dùng `__import__("json")`, nhiều statement trên một
  dòng và endpoint chỉ là một dòng dài. Không trực tiếp tạo lỗ hổng hiện tại vì filename đã được
  normalize và actor lấy từ dependency, nhưng làm audit/error handling khó đọc và khó mở rộng.
- Cách sửa cụ thể: import `json` ở đầu file, bỏ import thừa, tách `_response` và các endpoint thành
  block chuẩn; giữ actor authoritative từ `get_identity()` và thêm test header `X-User`/fallback.

## Đối chiếu quy tắc AGENTS.md

- Rule 1 — Không bịa số: phần Excel dùng `SUM` và lấy man-day/quotation từ persisted data; chưa
  thấy LLM tính số trong export. Tuy nhiên cần bổ sung test cho WBS appendix và schedule snapshot.
- Rule 2/3 — Structured output và một gateway: ja-check gọi `complete_with_retry` qua gateway;
  các exporter không gọi provider trực tiếp. Coverage cần thêm test call-count ở boundary export.
- Rule 4 — Hỏi thay vì đoán: sheet Q&A đọc câu hỏi persisted; không thấy export tự trả lời.
- Rule 5 — Price gate: service dùng placeholder khi chưa approved; cần kiểm chứng đủ cả bốn
  artifact sau khi tách PDF dependency.
- Rule 6 — Privacy: ja-check gọi `mask_text`; cần test context đầy đủ sau khi sửa.
- Rule 7 — Ngôn ngữ: label section có vi/en/ja, nhưng Word vẫn dùng heading cố định `Quotation`
  và mục lục trộn ba ngôn ngữ; cần chuẩn hóa toàn bộ customer-facing labels theo locale.
- Rule 10 — Root-relative API: `frontend/src/api/client.ts:43,112-123` dùng `/api` và không
  hard-code localhost; điểm này PASS.

## Verdict

**CHANGES REQUIRED**

Có 3 finding HIGH liên quan trực tiếp contract và 2 finding MEDIUM về artifact/ja-check. Vì vậy
chưa thể phê duyệt M7 dù test hiện tại pass; test coverage đang bỏ sót các lỗi này.

Top findings cần xử lý trước khi review lại:

1. Bổ sung phụ lục WBS vào proposal Word.
2. Không để DOCX/XLSX phụ thuộc vào PDF converter; chỉ tạo PDF khi endpoint cần.
3. Thay ngày hard-code bằng ngày export nhất quán trong một request.

## Handoff

Reviewer không sửa code theo workflow. Hãy yêu cầu Developer áp dụng các finding trên, bổ sung
regression tests tương ứng, chạy lại acceptance và gửi lại cùng milestone để review lại.
