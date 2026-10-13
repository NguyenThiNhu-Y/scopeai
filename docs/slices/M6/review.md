# Review — Slice M6: Đính kèm và ma trận đáp ứng

| Thuộc tính | Giá trị |
|---|---|
| Slice | M6 — Đính kèm, đọc file và đánh giá requirement |
| Ngày review | 2026-10-10 |
| Vai trò | Senior Reviewer |
| Phạm vi | Backend, frontend và tài liệu M6 sau remediation |
| Phương pháp | Đối chiếu `AGENTS.md`, `spec.md`, `test_report.md`, `fix_log.md`; discovery bằng vibegraph MCP; đọc trực tiếp các file M6 hiện hành |

## Tóm tắt

Các acceptance test file-level đã được bổ sung và các automated gate được ghi nhận PASS trong `fix_log.md`. Tuy nhiên review phát hiện các sai lệch contract còn ảnh hưởng trực tiếp đến an toàn upload, điều kiện chạy pipeline, tính trung thực của ma trận và trải nghiệm mapping. Vì vậy M6 chưa sẵn sàng merge/approval.

## Findings

### HIGH — Filename upload cho phép thoát khỏi thư mục `DATA_DIR/uploads`

- **Vị trí:** `backend/app/services/attachment_service.py:14-16`
- **Bằng chứng:** Tên file từ `UploadFile.filename` được ghép trực tiếp vào `Path("data/uploads") / str(bid_id) / f"{len(data)}_{filename}"` rồi `write_bytes()`; không dùng `basename`, allowlist tên, hoặc kiểm tra resolved path.
- **Tác động:** Filename chứa path traversal hoặc absolute path có thể khiến binary được ghi ra ngoài thư mục upload dự kiến, vi phạm yêu cầu lưu trữ an toàn của M6 và tạo rủi ro ghi đè file ứng dụng. Đây là input không tin cậy ở boundary upload.
- **Cách sửa cụ thể:** Chuẩn hóa tên bằng `Path(filename).name`, từ chối tên rỗng/không hợp lệ, tạo tên server-side bằng UUID hoặc id sau insert, rồi kiểm tra `resolved_path.is_relative_to(upload_root.resolve())` trước khi ghi. Thêm API test với `../`, separator Windows và absolute filename.

### HIGH — Upload không validate `file_type` theo enum contract

- **Vị trí:** `backend/app/api/routers/attachments.py:10-12`, `backend/app/services/attachment_service.py:12-16`
- **Bằng chứng:** Query parameter `file_type` là `str | None`; service lưu nguyên giá trị này khi có mặt. Chỉ endpoint PUT dùng `Literal["rfp", "requirement", "sample_data"]` trong `AttachmentUpdate`.
- **Tác động:** Client có thể tạo attachment với loại bất kỳ, không thuộc `rfp|requirement|sample_data`; parse sẽ bỏ qua loại lạ nhưng vẫn có thể trả trạng thái `ok`, làm sai contract và khiến file không được xử lý như người dùng mong đợi. Đây cũng là đường bypass validation giữa API và service.
- **Cách sửa cụ thể:** Dùng enum/Literal chung ở request schema và service boundary; reject loại không hợp lệ bằng envelope `INVALID_FILE_TYPE` trước khi ghi file. Bổ sung test upload cho loại lạ, loại rỗng và loại hợp lệ.

### HIGH — M6 B1 vẫn gửi toàn bộ `request_content` cho LLM, không dùng summary giới hạn/persist parse

- **Vị trí:** `backend/app/pipeline/steps/b1_intake.py:37-47`
- **Bằng chứng:** B1 lấy `bid.request_content`, chỉ mask PII rồi đưa toàn bộ vào `build_intake_prompt`. Luồng này không đọc attachment đã parse, không áp dụng giới hạn `RFP_SUMMARY_MAX_CHARS`, và không persist `attachments_status`, `requirement_count`, `no_requirement_file` hoặc `sample_profile` trong `output_json` theo M6 §3.1.
- **Tác động:** Vi phạm giới hạn dữ liệu gửi LLM và contract M6; RFP lớn có thể vượt context, còn LLM có thể nhận toàn văn thay vì context chuẩn hóa. Kết quả intake cũng không cung cấp bằng chứng persist tối thiểu cho file/profile/requirement count.
- **Cách sửa cụ thể:** Lấy text từ parser, mask trước khi tạo summary, cắt theo cấu hình tối đa, và chỉ gửi summary/context chuẩn hóa qua gateway. Ghép output deterministic từ parse/profile với `rfp_summary`, persist đầy đủ các field M6 và thêm test capture prompt cho giới hạn ký tự cùng output JSON.

### HIGH — Confirm gate chỉ kiểm tra `data_readiness`, không kiểm tra parse thành công và trạng thái attachment

- **Vị trí:** `backend/app/services/parse_service.py:32-36`, `backend/app/pipeline/orchestrator.py:124-132`
- **Bằng chứng:** `confirm()` chấp nhận mọi `confirmed=true` và readiness hợp lệ mà không yêu cầu đã gọi parse, attachment `parse_status=ok`, hoặc mapping đã xác nhận. `_ensure_parse_confirmed()` chỉ kiểm tra có attachment và `bid.data_readiness`.
- **Tác động:** Người gọi API có thể xác nhận dữ liệu chưa đọc hoặc attachment đang `pending/error`, sau đó start pipeline. Điều này phá vỡ yêu cầu “chỉ confirmed=true mới chạy” theo nghĩa xác nhận dữ liệu đã review, và có thể cho pipeline chạy với requirement thiếu/không có dữ liệu hợp lệ.
- **Cách sửa cụ thể:** Khi confirm, yêu cầu parse đã hoàn tất; reject attachment pending/error và reject requirement file có lỗi nặng bằng `STATE_CONFLICT` hoặc `PIPELINE_ERROR` với chi tiết theo file. Gate pipeline phải kiểm tra cùng điều kiện từ DB, không dựa riêng vào `data_readiness`. Thêm test API confirm trước parse, sau parse lỗi và với mapping chưa xác nhận.

### HIGH — Warning mismatch evaluation không được persist/trả lại, còn `evaluated` bị tính sai

- **Vị trí:** `backend/app/services/evaluation_service.py:15-21`, `backend/app/pipeline/steps/b3_evaluate.py:41-44`, `backend/app/api/routers/evaluations.py:24-31`
- **Bằng chứng:** Khi thiếu/thừa/trùng mã, service chỉ append warning vào biến cục bộ rồi `continue`; không lưu warning. B3 suy ra `evaluated` bằng cách trừ tổng số mã trong warning. Endpoint GET luôn trả `warnings=[]` và tính `evaluated` từ số row persist.
- **Tác động:** Sau retry/mismatch, API có thể báo ma trận không có cảnh báo, không liệt kê mã lỗi như contract §2.6/§3.2, và stats/output giữa pipeline với GET không nhất quán. Người duyệt có thể hiểu sai rằng đánh giá đã hoàn tất hoặc không biết mã nào bị bỏ sót.
- **Cách sửa cụ thể:** Lưu warnings trong output của step hoặc bảng/JSON gắn với bid và đọc lại khi GET; tính `evaluated` từ evaluation rows hợp lệ, không suy ra bằng phép trừ warning. Bổ sung test missing/duplicate/unknown kiểm tra cả step output và GET response, gồm mã cảnh báo sau reload.

### HIGH — UI chưa cho xem/chỉnh mapping sheet và không hiển thị đầy đủ profile contract

- **Vị trí:** `frontend/src/components/FileParseReview.tsx:5-16`, `backend/app/schemas/api_schemas/attachment.py:16-20`
- **Bằng chứng:** `FileParseReview` chỉ hiển thị count, trạng thái file và `sample_profile.row_count/readiness_suggestion`; không render sheet mappings/col_map và không gọi `updateAttachment`. `ParseOut` cũng không trả mapping theo response contract.
- **Tác động:** Người dùng không thể sửa header/cột `content`, `priority`, `category` trên web rồi parse lại như M6 §1.2, §2.3 và acceptance TC-M6-007 yêu cầu. PII suspicion, kiểu cột và empty percentage cũng không được hiển thị, nên không đủ dữ liệu để xác nhận readiness.
- **Cách sửa cụ thể:** Trả mapping/error chi tiết trong ParseResult hoặc dùng list attachment đã có; render editor cho từng sheet và gọi PUT update trước khi parse lại. Hiển thị toàn bộ profile columns gồm type, empty %, `pii_suspected`; thêm component tests cho edit mapping, reset pending và parse lại.

### MEDIUM — Type detection chỉ tin extension, không kiểm tra magic bytes và không auto-detect sample data

- **Vị trí:** `backend/app/parsers/detect.py:3-7`
- **Bằng chứng:** `data` được nhận nhưng không được đọc; mọi `.xlsx/.xlsm/.csv/.xls` đều trả `requirement`, mọi định dạng text/PDF/DOCX đều trả `rfp`.
- **Tác động:** Vi phạm yêu cầu “extension + magic bytes” và khả năng đoán `sample_data`; file đổi đuôi hoặc nội dung không khớp vẫn được lưu/parse theo loại sai. Người dùng phải tự sửa loại và có thể không nhận được lỗi sớm.
- **Cách sửa cụ thể:** Kiểm tra signature/container tối thiểu cho PDF, ZIP Office, OLE `.xls` và nội dung text/CSV; trả lỗi rõ khi mismatch. Dùng header/heuristic deterministic để gợi ý requirement/sample_data, nhưng vẫn cho phép presales override.

### MEDIUM — Parse chỉ trả profile của sheet mẫu đầu tiên và không bảo toàn mapping/error theo contract

- **Vị trí:** `backend/app/services/parse_service.py:18-19, 31`
- **Bằng chứng:** `prof` được cộng cho mọi sheet nhưng response chỉ trả `prof[0]`; attachment response chỉ có `id/filename/status/error`, không có mapping sheet. `column_mapping_confirmed` được suy ra bằng `bool(all_req)`, nên workbook có requirement tự động nhận diện vẫn bị coi là confirmed dù chưa có xác nhận mapping.
- **Tác động:** Nhiều sheet dữ liệu mẫu bị mất profile, UI không thể trình bày đầy đủ trạng thái parse/mapping, và cờ xác nhận không phản ánh hành động người dùng. Điều này làm acceptance với workbook nhiều sheet và manual mapping không đáng tin cậy.
- **Cách sửa cụ thể:** Trả profile theo attachment/sheet hoặc hợp nhất có quy tắc rõ; trả sheet mappings và lỗi hành động được; lưu một cờ mapping-confirmed riêng do update/confirm đặt, không suy ra từ số requirement.

## Đối chiếu AGENTS.md

- **Rule 1 — Không bịa số:** Không thấy LLM schema B3 chứa man-day/giá/ngày; batch/count được code tính. Tuy nhiên output B1 chưa persist đầy đủ count/profile M6.
- **Rule 2 — Structured LLM:** `EvaluationBatch` dùng `extra="forbid"` và gateway retry bounded; warning sau mismatch chưa được giữ lại.
- **Rule 3 — Một gateway:** Parser/profile không gọi LLM trực tiếp; B1/B3 dùng gateway, nhưng B1 đang gửi sai phạm vi context M6.
- **Rule 4 — Hỏi thay vì đoán:** Confirm gate yếu và mismatch bị che ở GET có nguy cơ cho pipeline/ma trận tiếp tục với dữ liệu chưa đủ.
- **Rule 5 — Price gate:** M6 không trực tiếp hiển thị giá; chưa phát hiện M6 code ghi đè price gate.
- **Rule 6 — Privacy:** Có `mask_text` cho B1, nhưng toàn văn request vẫn được gửi sau mask; cần giới hạn summary theo M6 và test prompt capture.
- **Rule 7 — Ngôn ngữ:** UI M6 dùng tiếng Việt, rating/note schema phù hợp; chưa đủ bằng chứng cho luồng clarify/re-evaluate sau `要確認`.
- **Rule 8 — Done proven:** Automated gates PASS theo fix log, nhưng 12 UI cases vẫn BLOCKED do Chromium và các lỗi contract nêu trên chưa có bằng chứng acceptance đầy đủ.
- **Rule 9 — Đơn giản:** Không phát hiện thêm queue/vector DB/auth server.
- **Rule 10 — Root-relative API:** `frontend/src/api/client.ts` dùng API base chung; không thấy hard-coded host trong phần M6 đã đọc.

## Test và bằng chứng đã xem

- `docs/slices/M6/spec.md`, `test_report.md`, `fix_log.md`, `handoff_to_review.md`.
- Backend M6: attachment/parse/evaluation services, routers, parsers, schemas, models, B1/B3/orchestrator.
- Frontend M6: API client/types, `AttachmentUploader`, `FileParseReview`, `RequirementMatrix`, `BidDetailPage`.
- Acceptance tests: parser, profile, uniqueness, batch, retry và integration gate.
- Vibegraph symbols/call paths: `attachment_service.add/update`, `parse_service.parse/confirm`, `evaluation_service.evaluate`, `complete_with_retry`, `run_intake`, `run_evaluate`, `_ensure_parse_confirmed`, `FileParseReview`, `RequirementMatrix`.

## Verdict

**CHANGES REQUIRED**

Không phát hiện CRITICAL, nhưng có 6 finding HIGH, trong đó upload path traversal là rủi ro bảo mật và các finding còn lại làm sai contract/độ tin cậy của M6. Developer cần xử lý toàn bộ HIGH trước khi merge/approval, sau đó chạy lại acceptance API/UI; 12 ca Playwright vẫn phải được rerun trong môi trường có Chromium.

## Handoff Note

Reviewer đã hoàn tất review M6. Deliverable là `docs/slices/M6/review.md`; không thay đổi code ứng dụng. Handoff cho Developer: ưu tiên sửa filename path traversal, validate upload type, summary/persist B1, confirm gate và warning evaluation; tiếp theo hoàn thiện mapping/profile UI và bổ sung regression tests. Sau remediation cần cập nhật `fix_log.md`, chạy lại `make test`/`make quality-gate` và rerun các UI case đang BLOCKED.

**Task Review complete. Awaiting prompt for the next role.**
