# Đặc tả Slice — M6 Đính kèm file và ma trận đáp ứng

| Thuộc tính | Giá trị |
|---|---|
| Tên tài liệu | Đặc tả milestone M6 — Đính kèm, đọc file và đánh giá requirement |
| Phiên bản | 1.0 |
| Ngày | 2026-10-10 |
| Trạng thái | Sẵn sàng cho bước Build |
| Vai trò | Solution Architect |
| Nguồn | `AGENTS.md`, `docs/05_roadmap/roadmap.md` §8, `docs/04_architecture/` (5 file), `docs/slices/M5/spec.md`, `docs/slices/M5/handoff_to_build.md`, `docs/03_requirements/srs.md` FR-002..006, FR-020..021 |

> Mọi số trong tài liệu này là giới hạn contract hoặc dữ liệu test giả lập, không phải số liệu khách hàng hay báo giá.
> `docs/05_roadmap/handoff_to_build.md` không tồn tại trong workspace; handoff nền gần nhất được dùng là
> `docs/04_architecture/handoff_to_dev.md` và handoff M5.

## 1. Phạm vi

### 1.1 Slice này giao

M6 là vertical slice từ hồ sơ đã tạo ở M2/M5 đến ma trận đáp ứng có thể kiểm tra:

1. Upload tối đa 10 file, mỗi file không quá 20 MB; chấp nhận RFP/tài liệu PDF, DOCX, TXT/MD,
   Excel/CSV requirement, dữ liệu mẫu và `.xls` theo contract. Backend tự đoán loại, lưu loại đã đoán,
   cho presales đổi loại trước khi parse.
2. Đọc bằng code, không giao việc đọc cấu trúc file cho LLM:
   - trích text PDF/DOCX/TXT/MD và tạo bản tóm tắt bị giới hạn ký tự;
   - đọc toàn bộ sheet của XLSX/XLSM/CSV/.xls;
   - tự nhận diện dòng tiêu đề và mapping mã, nội dung, ưu tiên, phân loại;
   - hỗ trợ mapping thủ công và parse lại;
   - sinh mã `REQ-xxx` khi thiếu mã hoặc cột mã là công thức; mã duy nhất trên toàn hồ sơ;
   - báo lỗi cụ thể, không tạo requirement giả khi parse thất bại.
3. Profile dữ liệu mẫu gồm số dòng, kiểu cột, tỷ lệ ô trống và cột nghi PII; sinh gợi ý
   `low|medium|high`, cho phép presales chỉnh.
4. Hiển thị trước khi chạy AI: số requirement đọc được, trạng thái từng file, mapping từng sheet,
   lỗi parse và profile dữ liệu. Chỉ `confirmed=true` mới được chạy pipeline phân tích.
5. Bước đánh giá requirement gọi LLM theo lô không quá 40 dòng; mỗi kết quả có đúng một mã,
   một rating `◎|○|△|×`, cờ phụ `needs_clarification` (hiển thị `要確認`) và ghi chú tiếng Việt.
6. Code kiểm tra tập mã đầu vào và tập mã đầu ra: không thiếu, không thừa, không trùng; retry
   output lỗi tối đa 2 lần, sau đó cảnh báo liệt kê mã lỗi cho người duyệt.
7. Ma trận đáp ứng hiển thị trên web, giữ `batch_no`, hướng giải pháp tại thời điểm đánh giá và
   đánh dấu đánh giá cũ khi hướng giải pháp thay đổi. Requirement `要確認` được nối với máy hỏi M2
   và được đánh giá lại sau khi có câu trả lời.
8. Nạp hồ sơ mẫu đầy đủ (text + RFP + Excel requirement giả lập) để demo M6.

### 1.2 Không thuộc M6

- Không xuất lại đúng template Excel của khách hoặc ghi cột đánh giá/nghi chú vào file gốc; đó là
  M7 và phải giữ nguyên định dạng/ công thức khi export.
- Không xuất Word/PDF/Excel estimate và không triển khai PowerPoint.
- Không tính effort, man-day, lịch, giá, tỉ giá hoặc dự phòng; M6 chỉ tạo dữ liệu requirement,
  profile và đánh giá. Không cho LLM sinh bất kỳ con số nghiệp vụ nào.
- Không thay đổi engine WBS, quotation, approval, price gate hoặc settings YAML của M5/M8.
- Không thêm auth server, queue, vector DB, lưu trữ đám mây hay dịch vụ OCR ngoài stack đã chốt.
- Không gửi file nhị phân hoặc toàn văn RFP vào LLM; chỉ gửi context đã chuẩn hóa, mask PII và
  tóm tắt nằm trong giới hạn cấu hình.

## 2. Frozen API contract subset

Nguồn duy nhất là `docs/04_architecture/api_contract.md`; slice này không tự thêm endpoint và
không sửa contract frozen.

### 2.1 Upload — `POST /api/bids/{id}/attachments`

Request `multipart/form-data`, field `file` (binary), query `file_type` tùy chọn. Backend tự đoán
nếu không truyền `file_type`.

Response `201`:

```json
{
  "id": 10,
  "filename": "requirements.xlsx",
  "file_type": "requirement",
  "detected_type": "requirement",
  "size_bytes": 204800,
  "parse_status": "pending"
}
```

Lỗi phải dùng envelope chuẩn: `FILE_TOO_LARGE` khi quá 20 MB, `TOO_MANY_FILES` khi quá 10 file,
`INVALID_FILE_TYPE` với phần mở rộng không được chấp nhận. Loại hợp lệ ở tầng nghiệp vụ là
`rfp|requirement|sample_data`.

### 2.2 Danh sách file — `GET /api/bids/{id}/attachments`

Response `200`:

```json
{
  "items": [
    {
      "id": 10,
      "filename": "requirements.xlsx",
      "file_type": "requirement",
      "size_bytes": 204800,
      "parse_status": "ok",
      "parse_error": null,
      "sheet_mappings": []
    }
  ]
}
```

`parse_status` là `pending|ok|error`; lỗi parse phải có `parse_error` hành động được.

### 2.3 Đổi loại/mapping — `PUT /api/bids/{id}/attachments/{attachment_id}`

Request:

```json
{
  "file_type": "requirement",
  "sheet_mappings": [
    {
      "sheet_name": "Requirements",
      "sheet_kind": "requirement",
      "col_map": {
        "code": "番号",
        "content": "機能要件",
        "priority": "区分",
        "category": "大分類"
      }
    }
  ]
}
```

Response `200` trả attachment đã cập nhật và reset `parse_status=pending` khi mapping thay đổi.
Không cho chỉnh mapping sau khi hồ sơ đã khóa; dùng `409 STATE_CONFLICT`.

### 2.4 Đọc file — `POST /api/bids/{id}/parse`

Request `{}` và dùng mapping đã lưu. Response `200`:

```json
{
  "requirements": {"count": 235, "no_requirement_file": false},
  "attachments": [
    {"id": 10, "filename": "requirements.xlsx", "status": "ok"},
    {"id": 11, "filename": "broken.pdf", "status": "error", "error": "Không đọc được PDF — file hỏng"}
  ],
  "sample_profile": {
    "row_count": 1200,
    "columns": [{"name": "email", "type": "string", "empty_pct": 5, "pii_suspected": true}],
    "readiness_suggestion": "low"
  },
  "column_mapping_confirmed": false
}
```

Parse lỗi nặng trả `422 PIPELINE_ERROR` với chi tiết theo file. Không có Excel requirement thì
`no_requirement_file=true`, không tạo ma trận và UI phải hiển thị đúng thông báo đó.

### 2.5 Xác nhận — `PUT /api/bids/{id}/parse/confirm`

Request `{ "data_readiness": "medium", "confirmed": true }`. `data_readiness` là
`low|medium|high`; `confirmed=true` là điều kiện để start pipeline. Response `200` trả bid,
status vẫn `draft`.

### 2.6 Ma trận — `GET /api/bids/{id}/evaluations`

Response `200` giữ đúng contract §7.1:

```json
{
  "solution_direction": {"direction": "rag", "reason_vi": "...", "selected_by": "ai_developer", "selected_at": "..."},
  "warnings": [{"type": "missing_codes", "codes": ["REQ-099"], "message": "Thiếu 1 mã sau 3 lần thử"}],
  "items": [
    {
      "req_code": "REQ-001",
      "content": "...",
      "priority": "mandatory",
      "category": "...",
      "rating": "○",
      "needs_clarification": false,
      "note_vi": "",
      "solution_direction": "rag"
    }
  ],
  "stats": {"total": 235, "evaluated": 234, "◎": 20, "○": 150, "△": 40, "×": 24, "needs_clarification": 3}
}
```

Không được dùng `items` để che thiếu dữ liệu: `total` phải là số requirement code đã đọc và
`evaluated` phản ánh số bản ghi đánh giá hợp lệ. Cảnh báo thiếu/thừa/trùng phải nằm trong `warnings`.

### 2.7 Endpoint liên quan nhưng không mở rộng trong M6

`POST /api/bids/{id}/pipeline/start`, SSE `/pipeline/events`, `GET /questions` và
`POST /questions/{round}/answers` được dùng lại theo contract M2; M6 không đổi path, envelope,
trạng thái hay giới hạn vòng hỏi. `GET /api/bids/{id}` tiếp tục trả `no_requirement_file`,
`data_readiness` và `pipeline_progress`.

## 3. LLM steps chạm tới

### 3.1 B1 Intake — phần M6 là code trước LLM

Input code: attachment đã upload, loại file/mapping đã xác nhận, file trong `DATA_DIR`.

Output persist tối thiểu trong `pipeline_steps.output_json`:

```json
{
  "attachments_status": [{"attachment_id": 10, "filename": "requirements.xlsx", "status": "ok", "error": null}],
  "requirement_count": 235,
  "no_requirement_file": false,
  "sample_profile": {
    "row_count": 1200,
    "columns": [{"name": "email", "type": "string", "empty_pct": 5, "pii_suspected": true}],
    "readiness_suggestion": "low"
  },
  "rfp_summary": {"summary_vi": "...", "keywords": []}
}
```

Text RFP gửi B1 phải qua mask PII và giới hạn `RFP_SUMMARY_MAX_CHARS` (mặc định theo architecture
là 8.000). Bản tóm tắt không được là nguồn duy nhất để tạo requirement; requirement phải đến từ
parser code.

### 3.2 B3 Evaluate — schema output mỗi lô

Input mỗi lần gọi gồm: danh sách mã + tên **toàn bộ** requirement để giữ ngữ cảnh; lô hiện tại
không quá 40 dòng gồm mã, nội dung, ưu tiên, phân loại; hướng giải pháp hiện hành nếu có; tóm tắt
giả định đã xác nhận. Nội dung RFP không cần gửi lại nguyên văn.

Output JSON frozen:

```json
{
  "batch": [
    {
      "req_code": "REQ-001",
      "rating": "○",
      "needs_clarification": false,
      "note_vi": "Đáp ứng trong phạm vi hướng RAG đã chọn."
    }
  ]
}
```

Validation:

- `extra=forbid`; `rating` chỉ thuộc `◎|○|△|×`; `note_vi` không quá 200 ký tự.
- Mỗi mã trong lô xuất hiện đúng một lần; không nhận mã ngoài lô.
- Sau khi gộp, tập mã đánh giá phải bằng tập mã requirement đúng một lần.
- `needs_clarification=true` chỉ là nhãn phụ `要確認`, không thay thế rating.
- Vi phạm schema retry tối đa 2 rồi `422 PIPELINE_ERROR`; thiếu/thừa mã sau retry vẫn tiếp tục
  với cảnh báo rõ ràng theo contract, không được âm thầm bỏ qua.
- Không có trường man-day, effort, price, currency, date hoặc số liệu nghiệp vụ trong schema.

### 3.3 Mock responses bắt buộc

| Fixture | Dùng để kiểm chứng |
|---|---|
| `evaluate_batch_good` | 40 mã hợp lệ, mỗi mã đúng một lần, có đủ các rating |
| `evaluate_batch_with_clarification` | Một số dòng có `needs_clarification=true`, vẫn có rating |
| `evaluate_batch_missing_code` | Thiếu một mã; retry và cảnh báo cuối cùng |
| `evaluate_batch_duplicate_code` | Trùng mã; retry và warning không-sót |
| `evaluate_batch_unknown_code` | Mã ngoài lô; retry rồi warning |
| `evaluate_bad_schema` | Thiếu field/field lạ/rating sai; retry ≤ 2 rồi lỗi rõ |

Tất cả fixture là tiếng Việt/Nhật hư cấu, không có email, số điện thoại, API key hay tên thật.
Mọi gọi LLM đi qua `LLMClient`; parser, profile, mapping, uniqueness check và UI edit không gọi LLM.

## 4. Công việc Backend và Frontend

### 4.1 Backend — file-level

| File | Hành động | Nội dung bắt buộc |
|---|---|---|
| `backend/app/models/attachment.py` | Tạo | ORM `attachments`, giới hạn kích thước/loại ở service, mapping JSON, parse status/error |
| `backend/app/models/requirement.py` | Tạo | ORM requirement, source sheet/row, `UNIQUE(bid_id, internal_code)` |
| `backend/app/models/evaluation.py` | Tạo | ORM evaluation, `UNIQUE(bid_id, requirement_id)`, rating, clarification, batch |
| `backend/app/models/__init__.py` | Cập nhật | Import ba model để metadata tạo đủ bảng |
| `backend/app/schemas/api_schemas/attachment.py` | Tạo | upload/list/update/parse/confirm response theo §2 |
| `backend/app/schemas/api_schemas/evaluation.py` | Tạo/cập nhật | item, warning, stats, evaluations response; enum rating |
| `backend/app/schemas/llm_schemas/evaluation.py` | Tạo | schema B3 `extra=forbid`, không có trường số nghiệp vụ |
| `backend/app/parsers/detect.py` | Tạo | extension + magic bytes, đoán `rfp|requirement|sample_data`, không tin extension đơn độc |
| `backend/app/parsers/pdf.py` | Tạo | trích text, lỗi rõ, không gọi LLM |
| `backend/app/parsers/docx.py` | Tạo | trích text DOCX, lỗi rõ |
| `backend/app/parsers/text.py` | Tạo | TXT/MD, encoding lỗi hành động được |
| `backend/app/parsers/excel.py` | Tạo | XLSX/XLSM/CSV, mọi sheet, header/cột, formula/công thức, mapping |
| `backend/app/parsers/xls.py` | Tạo | đọc `.xls` bằng xlrd; lỗi hướng dẫn lưu `.xlsx` |
| `backend/app/parsers/sample_profile.py` | Tạo | profile kiểu cột, empty %, PII suspicion, readiness rule-based |
| `backend/app/parsers/requirements.py` | Tạo | chuẩn hóa row, sinh `REQ-xxx`, duy nhất toàn bid, trace sheet/row |
| `backend/app/services/attachment_service.py` | Tạo | quota 10/20MB, lưu file, detect, đổi loại/mapping, locked guard, audit |
| `backend/app/services/parse_service.py` | Tạo | parse deterministic, lưu requirements/profile, reset khi mapping đổi, confirm guard |
| `backend/app/services/evaluation_service.py` | Tạo | chia lô ≤40, merge, uniqueness check, retry/warning, đánh giá lại sau clarify |
| `backend/app/api/routers/attachments.py` | Tạo | POST/GET/PUT attachment |
| `backend/app/api/routers/parse.py` | Tạo | POST parse, PUT parse/confirm |
| `backend/app/api/routers/evaluations.py` | Cập nhật/tạo | GET evaluations đầy đủ M6, không phá response tối thiểu M3 |
| `backend/app/pipeline/steps/b1_intake.py` | Cập nhật | gọi parse/profile và tạo summary giới hạn; persist output |
| `backend/app/pipeline/steps/b3_evaluate.py` | Tạo | gateway, schema, batch, persist từng batch, retry ≤2 |
| `backend/app/pipeline/orchestrator.py` | Cập nhật | gọi B3 đúng sau gap; không chạy nếu parse chưa confirm; resume giữ batch đã hoàn tất |
| `backend/app/services/sample_service.py` | Cập nhật | mẫu đầy đủ gồm file requirement; mọi dữ liệu ghi `giả lập` |
| `backend/tests/fixtures/*` | Tạo | workbook nhiều sheet, header lệch, formula 番号, RFP, sample CSV, fixture LLM |
| `backend/tests/test_*.py` | Tạo | test theo §5; không gọi LLM thật |

Parse attachment gốc vào `DATA_DIR/uploads/`; không lưu binary trong SQLite. Đường dẫn file không
được trả ra client ngoài các field contract.

### 4.2 Frontend — file-level

| File | Hành động | Nội dung bắt buộc |
|---|---|---|
| `frontend/src/api/types.ts` | Cập nhật | Attachment, SheetMapping, ParseResult, SampleProfile, Requirement, Evaluation, warnings |
| `frontend/src/api/client.ts` | Cập nhật | multipart upload; list/update attachments; parse/confirm; get evaluations; không hardcode host |
| `frontend/src/pages/BidNewPage.tsx` | Cập nhật | chọn nhiều file, hiển thị quota 10/20MB, type detect và đổi loại |
| `frontend/src/pages/BidDetailPage.tsx` | Cập nhật | trạng thái đọc file, mapping, xác nhận trước pipeline |
| `frontend/src/components/AttachmentUploader.tsx` | Tạo | chọn/kéo file, lỗi từng file, không mất 10 file hợp lệ khi file thứ 11 bị từ chối |
| `frontend/src/components/FileParseReview.tsx` | Tạo | count, file status, sheet mapping, profile, readiness edit, confirm gate |
| `frontend/src/components/RequirementMatrix.tsx` | Tạo | hiển thị toàn bộ requirement, rating, 要確認, note, warning thiếu/thừa |
| `frontend/src/pages/SolutionReviewPage.tsx` hoặc trang chi tiết tương ứng | Cập nhật | link/section ma trận, cảnh báo đánh giá theo hướng cũ |
| `frontend/src/pages/BidDetailPage.tsx` | Cập nhật | khi không có Excel hiển thị “Khách không gửi file Excel requirement” và ẩn matrix |
| `frontend/src/App.tsx` | Cập nhật | route/section M6, giữ route M2–M5 |
| `frontend/src/components/PipelineProgress.tsx` | Cập nhật | hiển thị batch progress, retry/warning từ SSE nếu backend phát |
| `frontend/src/App.test.tsx` và test component mới | Tạo/cập nhật | mock API root-relative, kiểm tra confirm gate và matrix |

### 4.3 Contract chia sẻ Backend ↔ Frontend

- Backend là nguồn sự thật cho file status, count, mapping, mã, rating, stats và warnings; FE không
  tự đọc workbook, tự sinh mã hay tự đếm để quyết định hoàn tất.
- FE chỉ gửi file binary qua multipart và mapping/readiness/confirm theo contract; không gửi rating,
  evaluation hay số requirement để backend tin.
- Mọi request dùng `/api/...`, lỗi hiển thị message tiếng Việt từ envelope.
- Parse chưa `confirmed` thì nút “Phân tích” bị khóa cả ở UI và backend; UI không được coi disabled
  là hàng rào duy nhất.
- `X-Role`/`X-User` tiếp tục là header giả lập cho audit; không thêm auth.

## 5. Tiêu chí chấp nhận

### 5.1 Shell commands phải exit 0

Các lệnh sau là gate bắt buộc của M6 và phải chạy với dữ liệu giả lập, LLM mock:

```bash
cd backend && pytest -q tests/test_file_reader.py
cd backend && pytest -q tests/test_excel_multisheet.py
cd backend && pytest -q tests/test_internal_req_code.py
cd backend && pytest -q tests/test_data_profile.py
cd backend && pytest -q tests/test_evaluation_batches.py
cd backend && pytest -q tests/test_unique_req_codes.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_evaluation_retry.py
cd backend && pytest -q
cd frontend && npm run build
make test
make quality-gate
```

Test phải chứng minh cụ thể:

- workbook 235 dòng được chia thành ít nhất 6 lô, mỗi lô ≤ 40 và tổng đọc/đánh giá là 235;
- hai sheet requirement dùng cùng namespace mã và không trùng mã;
- formula `番号 = ROW()-1` không bị coi là mã thật; mã nội bộ được sinh;
- thiếu mã sau retry được cảnh báo; mã thừa/trùng cũng bị bắt;
- parse lỗi không tạo requirement;
- upload thứ 11 và file quá 20 MB bị từ chối;
- mock gateway chỉ được gọi bởi bước đánh giá/LLM, không bởi parser hoặc mapping.

### 5.2 Kịch bản thủ công trên Preview

1. Mở hồ sơ giả lập M6 từ nút “Nạp hồ sơ mẫu đầy đủ”. Kỳ vọng: hồ sơ có RFP và Excel giả lập,
   không có tên khách thật, trạng thái `draft`.
2. Tại khu vực đính kèm, upload một PDF/TXT RFP, một workbook requirement hai sheet và một CSV dữ
   liệu mẫu. Kỳ vọng: từng file được đoán loại; presales đổi được loại; quota hiển thị 3/10 và kích
   thước từng file.
3. Upload thêm file thứ 11. Kỳ vọng: file thứ 11 bị từ chối với `TOO_MANY_FILES`, mười file trước
   không mất. Thử file >20 MB ở fixture/Preview phù hợp: nhận `FILE_TOO_LARGE`.
4. Bấm “Đọc file”. Kỳ vọng: web hiển thị số requirement, trạng thái từng file, từng sheet, mapping
   cột, dòng lỗi nếu có, và profile sample gồm row count/type/empty %/PII suggestion.
5. Với workbook có mapping sai, sửa `content`, `priority`, `category` trên web rồi parse lại. Kỳ
   vọng: danh sách requirement đổi đúng theo mapping mới; không có bản ghi cũ bị nhân đôi.
6. Kiểm tra workbook có hai sheet và cột `番号` là công thức. Kỳ vọng: tất cả dòng hợp lệ được đọc,
   mã `REQ-xxx` duy nhất xuyên hai sheet, có trace sheet/row; không dùng chuỗi công thức làm mã.
7. Chưa bấm xác nhận, thử “Phân tích”. Kỳ vọng: UI khóa và backend từ chối; không có evaluation,
   không có số effort/giá/lịch được tạo.
8. Chọn readiness, bấm xác nhận rồi “Phân tích”. Kỳ vọng: pipeline chạy batch ≤40; SSE hiển thị
   batch hiện tại/tổng; ma trận có đủ `◎/○/△/×`, nhãn `要確認`, note tiếng Việt và stats.
9. Dùng mock lỗi thiếu một mã. Kỳ vọng: retry tối đa 2, sau đó matrix vẫn không giả vờ hoàn tất;
   warning liệt kê mã thiếu/thừa/trùng để người duyệt xử lý.
10. Chọn một requirement `要確認`, trả lời từ máy hỏi M2. Kỳ vọng: đánh giá được chạy lại, giữ
    `evaluated_after_round`; nếu vẫn thiếu thì nhãn vẫn còn.
11. Đổi hướng giải pháp ở M3. Kỳ vọng: matrix cũ được đánh dấu “đánh giá theo hướng cũ” hoặc được
    đánh giá lại theo contract; không tự tính lại quotation ở M6.
12. Tạo hồ sơ không có Excel requirement và parse. Kỳ vọng: hiển thị đúng “Khách không gửi file
    Excel requirement”, ẩn ma trận, không bịa requirement/evaluation.

### 5.3 Test các rule AGENTS.md liên quan M6

| Rule | Test/kiểm tra bắt buộc | Assert |
|---|---|---|
| 1 — Không bịa số | `test_evaluation_batches.py`, schema B3, parse tests | LLM chỉ trả rating/note; không có man-day/giá/ngày; count/lô do code |
| 2 — JSON có schema | `test_evaluation_retry.py` | sai schema retry ≤2 rồi lỗi `PIPELINE_ERROR` rõ |
| 3 — Một gateway | gateway call-count test | B3 dùng `LLMClient`; parser/profile/mapping không gọi provider trực tiếp |
| 4 — Hỏi thay vì đoán | parse/confirm + clarify integration test | chưa confirm hoặc còn `要確認` thì dừng/đưa hỏi, không tự điền |
| 5 — Price gate | regression `test_price_gate.py` và Preview M5→M6 | M6 không làm lộ/ghi đè số tiền; proposal chưa duyệt vẫn placeholder |
| 6 — Privacy | `test_pii_mask.py` + prompt capture | RFP summary đã mask email/SĐT; fixture hư cấu; không log key |
| 7 — Ngôn ngữ | evaluation/clarify integration test | UI/lý do/note nội bộ tiếng Việt; câu hỏi dùng `customer_language` |
| 8 — Done proven | toàn bộ §5.1 + Preview §5.2 | automated tests và click-through đều pass |
| 9 — Đơn giản | dependency/review gate | không queue/vector DB/auth server/dịch vụ đọc file ngoài stack |
| 10 — Root-relative | frontend build/scan | mọi request M6 qua `/api`, không hardcode `localhost` |

## 6. Dữ liệu test và fixture

Tất cả dữ liệu phải ghi rõ `DỮ LIỆU GIẢ LẬP` và không chứa tên công ty, email, điện thoại hay thông tin
khách thật.

| Path | Nội dung |
|---|---|
| `samples/m6_rfp_fake.pdf` | RFP giả lập ngắn, có đoạn tiếng Việt/Nhật và PII giả để kiểm tra extraction/mask |
| `samples/m6_rfp_fake.docx` | RFP DOCX giả lập, cùng nội dung nghiệp vụ nhưng khác định dạng |
| `samples/m6_requirements_multisheet.xlsx` | Hai sheet requirement, header Nhật, cột `番号` là công thức, dòng hợp lệ và dòng lỗi |
| `samples/m6_requirements.csv` | CSV tối thiểu để kiểm tra auto header/mapping |
| `samples/m6_sample_data.csv` | Dữ liệu mẫu giả lập có cột trống và cột nghi PII để profile |
| `backend/tests/fixtures/m6_evaluation.py` | Good/missing/duplicate/unknown/bad-schema mock response |
| `backend/tests/fixtures/m6_parser_cases.py` | Expected row count, mapping, internal codes, profile và parse errors |
| `frontend/src/test/m6Fixtures.ts` | Response API giả lập cho upload/review/matrix; không chứa số giá |

Không cần thêm dữ liệu thật vào `data/uploads/`; runtime file phải được tạo trong thư mục data đã gitignore.

## 7. Rủi ro và bàn giao

| Rủi ro | Mức | Biện pháp/điều kiện bàn giao |
|---|---|---|
| Workbook merge cell/header nhiều dòng | Cao | không đoán im lặng; trả lỗi + cho mapping tay; fixture phải bao phủ |
| Công thức Excel không có cached value | Cao | đọc công thức/giá trị an toàn; sinh mã nội bộ khi cần |
| Parse `.xls` không thành công | Trung bình | thông báo “vui lòng lưu lại dưới dạng .xlsx”, không tạo requirement giả |
| LLM trả thiếu/trùng mã | Cao | validator tập hợp, retry ≤2, warning hiển thị; không báo complete giả |
| Requirement lớn làm tăng latency | Trung bình | batch ≤40, persist từng batch, SSE progress, resume batch chưa xong |
| Đổi hướng làm matrix cũ sai ngữ cảnh | Trung bình | lưu `solution_direction`, warning “theo hướng cũ” hoặc đánh giá lại có chủ đích |

Build phải bàn giao cho Test/Review: danh sách file thay đổi, schema DB, kết quả mọi command §5.1,
ảnh/evidence Preview, số batch của fixture 235 dòng, kết quả uniqueness và warning retry. M7 nhận
requirements/evaluations đã persist và contract export; không bắt đầu triển khai M7 trong slice này.

**Slice Spec M6 hoàn tất. Handoff cho Build ở `docs/slices/M6/handoff_to_build.md`.**
