# Báo cáo review chất lượng mã nguồn

## Review Summary

**Type**: Code Review  
**Files/Documents Reviewed**: Toàn bộ backend/frontend, `AGENTS.md` và tài liệu `docs/04_architecture/`  
**Overall Assessment**: **Needs Changes**

Phạm vi review đối chiếu 10 quy tắc trong `AGENTS.md`, API contract frozen, data model, architecture và LLM pipeline. Có các test cho nhiều luồng chính, nhưng hiện chưa nên phê duyệt vì có lỗi contract ở upload, rủi ro tiêu thụ bộ nhớ, cấu hình CORS quá rộng và một số dữ liệu export không khớp schema hiện hành.

## CRITICAL

Không phát hiện lỗi ở mức CRITICAL (không thấy hardcoded secret hoặc đường dẫn traversal có thể truy cập tùy ý trong phạm vi đã review).

## HIGH

### HIGH-01 — Mã lỗi file quá lớn sai API contract

- **Location**: `backend/app/services/attachment_service.py:15`
- **Category**: Bug / Consistency
- **Description**: Contract `api_contract.md §2` quy định `FILE_TOO_LARGE` trả HTTP **400**, nhưng code trả `ApiError(413, ...)`. Frontend và các client bám contract sẽ xử lý sai loại lỗi; acceptance test cho upload có thể thất bại.
- **Suggestion**: Đổi status thành 400 hoặc cập nhật contract qua ADR (khuyến nghị giữ contract frozen và đổi code). Bổ sung test kiểm tra cả status code, `error.code`, `details.max_bytes`.

### HIGH-02 — Upload đọc toàn bộ file trước khi áp giới hạn kích thước

- **Location**: `backend/app/api/routers/attachments.py:11-12`, `backend/app/services/attachment_service.py:15`
- **Category**: Security / Performance
- **Description**: `await file.read()` nạp toàn bộ multipart body vào RAM rồi mới kiểm tra 20 MB. Một hoặc nhiều request lớn có thể gây áp lực bộ nhớ trước khi bị từ chối, trái mục tiêu giới hạn upload của FR-002.2.
- **Suggestion**: Giới hạn kích thước ở boundary bằng cách đọc theo chunk với tổng byte tối đa `MAX_SIZE + 1`, dừng ngay khi vượt ngưỡng; giữ kiểm tra lại ở service. Cân nhắc lấy giới hạn từ config thay vì hằng số rải trong service.

### HIGH-03 — CORS wildcard trong mọi môi trường

- **Location**: `backend/app/main.py:35-40`
- **Category**: Security
- **Description**: `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]` luôn bật, trong khi architecture nêu rõ CORS phải thay đổi theo `APP_ENV`. Với deployment ngoài môi trường dev, bất kỳ origin nào cũng có thể gọi API; nếu sau này thêm credential/session thì cấu hình này trở thành rủi ro nghiêm trọng hơn.
- **Suggestion**: Chỉ cho phép wildcard ở development; production lấy allowlist từ cấu hình và giới hạn methods/headers cần thiết. Bổ sung test cấu hình theo `APP_ENV`.

## MEDIUM

### MEDIUM-01 — Dữ liệu schedule export không khớp contract `tasks[]`

- **Location**: `backend/app/services/export_service.py:37-40`
- **Category**: Bug / Consistency
- **Description**: API contract §8.4 lưu task với `task_code`, `start_date`, `end_date`, nhưng exporter đọc `week` và `name`. Vì vậy bảng schedule trong proposal/export có thể rỗng hoặc mất ngày/task name dù schedule đã được tính đúng.
- **Suggestion**: Dùng các field hiện hành (`start_date`, `end_date`, `task_code`, `phase`, `role`) để dựng dòng export; thêm test với `tasks_json` theo đúng mẫu contract và assert cả start/end date.

### MEDIUM-02 — Export log không theo data model frozen cho bundle

- **Location**: `backend/app/api/routers/exports.py:20`, `backend/app/models/export_log.py:11`
- **Category**: Consistency / Maintainability
- **Description**: Endpoint bundle ghi kind `bundle_zip`, trong khi `data_model.md §15` chỉ mô tả `proposal_docx`, `estimate_xlsx`, `proposal_pdf`; contract M7 lại yêu cầu bundle. Hiện không có enum/constraint nên dữ liệu audit có thể không đồng nhất và các truy vấn lịch sử dễ bỏ sót bundle.
- **Suggestion**: Chốt contract/model bằng ADR: thêm `bundle_zip` vào model/data model và các schema/audit query, hoặc log bundle theo quy ước đã có. Thêm test kiểm tra log sau khi tải bundle.

### MEDIUM-03 — Export filename dùng ngày hardcode

- **Location**: `backend/app/exporters/filename.py:12-14`
- **Category**: Bug / Correctness
- **Description**: `export_date="2026-10-10"` mặc định khiến mọi file export luôn mang ngày cố định, không phản ánh ngày sinh file và sẽ sai ngay khi chạy sau ngày này. Contract quy định tên file có ngày export deterministic, không phải ngày compile cố định.
- **Suggestion**: Tạo ngày từ clock/UTC tại thời điểm export và truyền rõ vào `export_filename`; nếu cần reproducibility cho test, cho phép test truyền ngày cố định. Bổ sung test đổi ngày.

### MEDIUM-04 — `downloadExport` làm mất mã lỗi và details

- **Location**: `frontend/src/api/client.ts:130-136`
- **Category**: Error handling
- **Description**: Wrapper `request` parse đủ `code` và `details`, nhưng `downloadExport` chỉ đọc `message`. Các lỗi `STATE_CONFLICT`, `NOT_FOUND`, `CHECK_FAILED` từ export không còn metadata để UI hiển thị hành động phù hợp.
- **Suggestion**: Dùng helper parse lỗi chung cho cả JSON request và binary download, hoặc ít nhất parse `code`/`details` giống `request`. Thêm test response lỗi JSON của endpoint download.

### MEDIUM-05 — Lộ thông tin lỗi nội bộ từ parser

- **Location**: `backend/app/services/parse_service.py:15` (vùng `except Exception`), được trả qua `backend/app/api/routers/parse.py`
- **Category**: Security / Error handling
- **Description**: `a.parse_error = str(exc)` có thể chứa path server, tên thư viện hoặc chi tiết nội bộ. Giá trị này đi vào response parse, trái yêu cầu lỗi tiếng Việt, hành động được và nguyên tắc không lộ thông tin nội bộ.
- **Suggestion**: Log exception server-side với correlation/id attachment; trả message đã chuẩn hóa theo loại lỗi (file hỏng, định dạng không đọc được) và chỉ đưa chi tiết an toàn vào `details`.

### MEDIUM-06 — `create_bid` không lấy identity chung và dễ lệch audit convention

- **Location**: `backend/app/api/routers/bids.py:65-73`
- **Category**: Architecture / Consistency
- **Description**: Router đọc riêng `X-User`, trong khi các endpoint nhạy cảm dùng `get_identity`. Contract quy định cặp `X-Role`/`X-User` là nguồn audit authoritative; cách đọc riêng này bỏ qua validation/chuẩn hóa chung của `get_identity` và không nhất quán với phần còn lại.
- **Suggestion**: Inject `Identity` và dùng `identity.user` cho `created_by`; giữ behavior mặc định `presales/anonymous`. Thêm test header whitespace/role không hợp lệ và kiểm tra created_by.

## LOW

### LOW-01 — Router attachments khó review và thiếu type/error boundary

- **Location**: `backend/app/api/routers/attachments.py:8-16`
- **Category**: Code Quality / Maintainability
- **Description**: Nhiều route và statement nằm trên một dòng, không có return annotation; helper `out` chỉ là alias một dòng. Điều này làm giảm khả năng phát hiện lỗi contract và không theo style của các router khác.
- **Suggestion**: Format mỗi route thành block rõ ràng, thêm type cho dependency/return, đổi `out` thành tên mô tả (`to_attachment_out`). Đây là cleanup, không cần thay đổi behavior.

### LOW-02 — `jsonPost` nhận `unknown` nhưng không bảo vệ giá trị không serializable

- **Location**: `frontend/src/api/client.ts:145-151`
- **Category**: Error handling
- **Description**: `JSON.stringify(body)` có thể trả `undefined` hoặc throw với dữ liệu vòng; type `unknown` làm helper trông an toàn hơn thực tế. Các caller hiện tại dùng payload phẳng nên chưa thấy lỗi, nhưng đây là abstraction dùng ở nhiều endpoint.
- **Suggestion**: Đổi input thành kiểu JSON request phù hợp hoặc bắt lỗi serialize và ném `ApiError` rõ ràng; thêm unit test payload không hợp lệ nếu helper vẫn giữ public scope.

### LOW-03 — Test settings chỉ kiểm tra status, chưa kiểm tra envelope và giữ giá trị cũ

- **Location**: `backend/tests/test_settings_integrity.py:22-28`
- **Category**: Testing gap
- **Description**: `test_factor_cap_must_be_above_one` chỉ assert HTTP 400. Nó chưa chứng minh `error.code=VALIDATION_ERROR`, có `details.errors`, và giá trị repo/override trước đó không bị thay đổi — các điểm contract §11.2 yêu cầu.
- **Suggestion**: Assert đầy đủ envelope và gọi `GET /api/settings` sau PUT để xác nhận invalid update không làm thay đổi effective setting.

### LOW-04 — Lặp logic xử lý lỗi giữa `request` và `downloadExport`

- **Location**: `frontend/src/api/client.ts:80-94` và `130-136`
- **Category**: Duplication
- **Description**: Hai hàm có cùng fallback message và parse JSON lỗi, nhưng behavior đã lệch như MEDIUM-04. Duplication này dễ tạo thêm sai khác ở các endpoint binary sau này.
- **Suggestion**: Tách helper `apiErrorFromResponse(response)` dùng chung, có thể đọc body JSON một lần và giữ status/code/details.

## Kiểm tra theo AGENTS.md rules 1–10

| Rule | Đánh giá |
|---|---|
| 1 — No invented numbers | Cơ bản tuân thủ: effort/quotation nằm ở service/code; cần giữ test export schedule để không làm mất số/ngày đã tính. |
| 2 — Structured LLM output | Có schema/retry ở pipeline; review này không thấy vi phạm trực tiếp trong các đường gọi đã kiểm tra. |
| 3 — One LLM gateway | Các export gọi `get_llm_client()` qua service; không thấy SDK gọi trực tiếp. |
| 4 — Ask instead of guess | Có state conflict/clarification flow và test tương ứng. |
| 5 — Price gate | `artifacts` dùng placeholder khi chưa approved; cần giữ test bundle/export cho cả bundle. |
| 6 — Privacy | Không phát hiện secret trong code; parser error cần chuẩn hóa để tránh lộ thông tin nội bộ. |
| 7 — Languages | Envelope lỗi và labels có hỗ trợ ngôn ngữ; cần kiểm tra export schedule/filename không làm mất nội dung. |
| 8 — Done means proven | Chưa xác nhận được `make test`: môi trường review không có lệnh `make` (lệnh kết thúc với `make: command not found`), vì vậy chưa có bằng chứng acceptance đầy đủ. |
| 9 — Keep it simple | Kiến trúc vẫn monolith/SQLite, không thấy hạ tầng nặng ngoài phạm vi. |
| 10 — Root-relative API | `API_BASE='/api'` đúng contract; không thấy hardcode localhost trong API client. |

## Positive Highlights

- Frontend API base là root-relative `/api`, phù hợp BR-10.
- `state_conflict` giữ đúng HTTP 409 và error code chuẩn; các route approval có kiểm tra role.
- `downloadExport` không tự diễn giải binary và có xử lý `Content-Disposition`/Japanese check.
- Attachment path có kiểm tra basename, sanitize tên file và kiểm tra `is_relative_to`, giúp giảm path traversal.
- Export bundle dùng timestamp ZIP cố định, hỗ trợ tính deterministic; test hiện có kiểm tra đúng ba artifact và không có path trong entry.
- Có test cho price gate, khóa hồ sơ, WBS cycle/PM/QA, retry và integrity của settings; nền tảng test tốt nhưng cần bổ sung các assertion nêu trên.
