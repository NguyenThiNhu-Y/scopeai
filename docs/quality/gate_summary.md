# Quality Gate Summary

## Phạm vi và nguồn

- `docs/quality/test_report.md`: kết quả test/backend/frontend/build và E2E.
- `docs/quality/code_review.md`: review chất lượng và contract.
- `docs/quality/security_audit.md`: audit bảo mật, chuẩn hóa từ `docs/sec-audit/report-20261010_000000.md`.

## Bảng phát hiện hợp nhất

Các phát hiện trùng giữa code review và security audit đã được gộp theo nguyên nhân gốc. Severity lấy mức cao hơn khi hai nguồn khác nhau.

| ID | Nguồn | Severity | File | Vấn đề | Hướng sửa |
|---|---|---|---|---|---|
| GATE-01 | Security + review | Chấp nhận rủi ro: ngoài phạm vi MVP | `backend/app/api/deps.py`; `backend/app/api/routers/{bids,attachments,settings,exports}.py` | MVP là công cụ nội bộ cho một người dùng, không triển khai authentication/phân quyền; `X-Actor` chỉ là thông tin caller-controlled để ghi audit log | Không thêm auth server theo AGENTS.md luật 9; nếu mở rộng thành nhiều người dùng thì phải thiết kế auth/authorization như một hạng mục riêng |
| GATE-02 | Security + review | HIGH | `backend/app/api/routers/attachments.py:10-12`; `backend/app/services/attachment_service.py:14-15` | Upload được đọc toàn bộ vào RAM trước khi giới hạn, gây uncontrolled resource consumption | Đọc theo chunk đến `MAX_SIZE + 1`, giới hạn proxy/body và quarantine file |
| GATE-03 | Review | HIGH | `backend/app/services/attachment_service.py:15` | `FILE_TOO_LARGE` trả HTTP 413 nhưng API contract yêu cầu 400 | Giữ contract frozen và đổi status code; thêm assertion status/code/details |
| GATE-04 | Review + security | HIGH | `backend/app/main.py:35-40` | CORS wildcard; architecture yêu cầu cấu hình theo môi trường | Dev mới wildcard; production dùng allowlist và methods/headers tối thiểu |
| GATE-05 | Security + review | MEDIUM | `backend/app/services/parse_service.py:13-31`; `backend/app/api/errors.py:16-39` | Parser/raw provider/schema exception có thể lộ nội bộ qua response hoặc persisted state | Log server-side với correlation ID; trả lỗi ổn định, không trả raw exception |
| GATE-06 | Security | MEDIUM | `backend/app/llm/prompts/{b1_intake,b2_gap}.py`; `backend/app/llm/openai_compat_client.py` | Customer document chưa được cô lập khỏi instruction, có prompt-injection exposure | Tách system/user messages, delimiter, untrusted-data instruction, size cap và kiểm tra deterministic |
| GATE-07 | Security | MEDIUM | `backend/app/privacy/mask.py`; `backend/app/llm/gateway.py`; `backend/app/llm/openai_compat_client.py` | PII masking regex chưa đầy đủ và không centralize | Sanitize đệ quy tại gateway, mở rộng loại PII, thêm provider-independent canary tests |
| GATE-08 | Review | MEDIUM | `backend/app/services/export_service.py:37-40` | Schedule exporter đọc `week`/`name` thay vì field contract `task_code`/`start_date`/`end_date` | Dùng schema hiện hành và test assert task/date trong export |
| GATE-09 | Review | MEDIUM | `backend/app/api/routers/exports.py:20`; `backend/app/models/export_log.py:11` | `bundle_zip` chưa được thống nhất trong frozen data model/audit enum | Cập nhật ADR/model/schema hoặc quy ước log bundle; thêm test audit log |
| GATE-10 | Review | MEDIUM | `backend/app/exporters/filename.py:12-14` | Export filename hardcode ngày `2026-10-10` | Dùng UTC clock tại thời điểm export; cho phép inject ngày trong test |
| GATE-11 | Review | MEDIUM | `frontend/src/api/client.ts:130-136` | `downloadExport` làm mất `code`/`details` của lỗi API | Dùng helper parse lỗi chung cho JSON và binary response |
| GATE-12 | Security | LOW | `backend/app/parsers/detect.py:3-7`; `backend/app/services/attachment_service.py:16-27` | Upload validation dựa chủ yếu trên extension, storage tương đối | Tên opaque, quarantine không public, signature validation, chống symlink và parser limits |
| GATE-13 | Review | LOW | `backend/tests/test_settings_integrity.py:22-28` | Test settings chỉ assert status, chưa assert envelope và rollback giá trị | Assert `error.code`, `details.errors` và GET sau invalid PUT |
| GATE-14 | Review | LOW | `frontend/src/api/client.ts:80-94,130-136` | Lặp logic parse lỗi giữa `request` và `downloadExport` | Tách helper `apiErrorFromResponse` dùng chung |
| GATE-15 | QA | HIGH | E2E TC-E2E-01..05 | E2E bị BLOCKED vì thiếu Chromium; không có bằng chứng runtime cho hành trình chính | Cài/enable browser runtime rồi chạy lại toàn bộ TC-E2E; không coi BLOCKED là PASS |

## Kiểm tra tự động

| Hạng mục | Kết quả |
|---|---|
| Backend pytest | PASS — `python3 -m pytest -q`: 263 tests passed |
| Frontend unit tests | PASS, 16 tests |
| Frontend build | PASS |
| Quality gate script | PASS — `bash scripts/quality_gate.sh` |
| E2E Playwright | BLOCKED trước điều hướng do thiếu Chromium executable |

## Verdict

**NO-GO cho Quality Gate tổng thể**

GATE-01 được **chấp nhận rủi ro: ngoài phạm vi MVP** theo phạm vi một người dùng; header `X-Actor` không phải cơ chế xác thực hay phân quyền.

Lý do bắt buộc: GATE-01 đã được chấp nhận rủi ro ngoài phạm vi MVP; các phát hiện HIGH khác (GATE-02, GATE-03, GATE-04) vẫn theo dõi và E2E Playwright chưa được chứng minh đầy đủ. Không được dùng kết quả unit/build để thay thế xác nhận runtime hoặc phê duyệt demo.

## Điều kiện tối thiểu để chuyển GO

1. Khắc phục hoặc chấp nhận có ghi nhận chính thức đối với toàn bộ HIGH; GATE-01 đã được chấp nhận rủi ro ngoài phạm vi MVP, các gate HIGH còn lại vẫn theo dõi.
2. Sửa các lỗi contract ảnh hưởng upload/export và CORS production.
3. Chạy lại TC-E2E-01..05 trong môi trường có Chromium và đạt PASS, bao gồm xác nhận price gate và mở được file export.
