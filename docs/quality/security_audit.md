# Báo cáo audit bảo mật

Nguồn: `docs/sec-audit/report-20261010_000000.md`, chuẩn hóa về thư mục quality để dùng trong quality gate.

## Tóm tắt

- Critical: 0
- High: 2
- Medium: 4
- Low: 2
- Đánh giá tổng thể: High risk

## Findings

| ID | Severity | CWE/OWASP | Vị trí | Tóm tắt | Khuyến nghị |
|---|---|---|---|---|---|
| FINDING-001 | HIGH | CWE-862/CWE-639; A01/API1 | `backend/app/api/deps.py:13-43`, `bids.py:53-73`, `attachments.py:10-16`, `settings.py:18-23`, `exports.py:26-36` | Identity dựa trên header do caller kiểm soát; thiếu object-level authorization | Dùng authentication dependency đã xác thực, tenant/owner predicate cho mọi truy vấn, không tin header/body làm identity authoritative |
| FINDING-002 | HIGH | CWE-400; API4 | `backend/app/api/routers/attachments.py:10-12`, `backend/app/services/attachment_service.py:14-15` | Đọc toàn bộ multipart body vào RAM trước khi giới hạn kích thước | Đọc bounded chunks, giới hạn proxy/server body và quarantine file |
| FINDING-003 | MEDIUM | CWE-209; A05 | `backend/app/services/parse_service.py:13-31` | Parser exception có thể làm lộ path/thư viện/nội dung khách hàng | Log chi tiết phía server; trả thông báo cố định và correlation ID |
| FINDING-004 | MEDIUM | CWE-209; A05 | `backend/app/llm/openai_compat_client.py:71-89`, `gateway.py:69-79`, `evaluation_service.py:14-15` | Raw provider/schema exception đi qua API hoặc state persisted | Chuẩn hóa lỗi, không trả raw exception; log server-side |
| FINDING-005 | MEDIUM | CWE-1427/CWE-20; LLM Prompt Injection | `backend/app/llm/prompts/b1_intake.py:12-39`, `b2_gap.py:25-47`, `openai_compat_client.py:57-68` | Nội dung RFP chưa được tách rõ khỏi instruction | Dùng delimiter/system message, đánh dấu dữ liệu không tin cậy, giới hạn kích thước và human review |
| FINDING-006 | MEDIUM | CWE-359; A02 | `backend/app/privacy/mask.py:14-34`, `gateway.py:21-29`, `openai_compat_client.py:57-58` | PII masking regex chưa đầy đủ và không tập trung tại gateway | Centralize sanitization đệ quy và thêm canary tests độc lập provider |
| FINDING-007 | LOW | CWE-942; A05 | `backend/app/main.py:35-40` | CORS wildcard cho mọi origin/method/header | Dùng allowlist theo môi trường và giới hạn methods/headers |
| FINDING-008 | LOW | CWE-434/CWE-22 | `backend/app/parsers/detect.py:3-7`, `backend/app/services/attachment_service.py:16-27` | Kiểm tra upload chủ yếu dựa trên extension; storage tương đối | Dùng tên opaque, quarantine không public, content/signature validation và parser limits |
