# Handoff — Đợt 9 backend

Ngày: 2026-10-11  
Vai trò: backend-dev  
Phạm vi: nền tảng API Proposal, Bid/No-bid và Cài đặt cho Đợt 9

## Trạng thái

**DONE ở boundary backend.** Frontend, Preview/QA và reviewer chưa thực hiện trong bước này.

## Đã triển khai

- Proposal draft có ngôn ngữ hiện hành, bản dịch lưu theo `vi/en/ja`, metadata tài liệu A4 gồm bìa, mục lục và printable; thêm `POST /api/bids/{id}/proposal/translate`.
- Proposal version nhận ngôn ngữ, tạo phiên bản theo chuỗi `1.0`, `1.1`, `2.0`..., lưu `sent_at`; khi đánh dấu gửi khách ghi Changelog với phiên bản và ghi chú.
- Thêm model/schema/service/router Bid/No-bid tại `GET/PUT /api/bids/{id}/bid-qualification`: tiêu chí có trọng số tổng bằng 100, gợi ý nguồn `analysis`, người xác nhận và thời điểm xác nhận. Không để LLM sinh điểm hoặc số liệu.
- Settings response tiếp tục trả `payload` và bổ sung dữ liệu giả lập cho `company`, `templates`, `standard_content`, `case_studies`, `bid_no_bid`; template yêu cầu metadata `valid=true`, tiêu chí Bid/No-bid kiểm tra tổng trọng số. Tên công ty và case study đều giả lập.
- Approval/history hiện có ghi chú duyệt/từ chối; route gửi proposal bổ sung audit note. Trường `Bid.deal_stage` đã tồn tại và được giữ nguyên cho frontend nối vào.

## Files chính

- `backend/app/models/proposal_draft.py`
- `backend/app/models/proposal_version.py`
- `backend/app/models/bid_qualification.py`
- `backend/app/schemas/api_schemas/proposal.py`
- `backend/app/schemas/api_schemas/settings.py`
- `backend/app/schemas/api_schemas/bid_qualification.py`
- `backend/app/services/proposal_service.py`
- `backend/app/services/settings_service.py`
- `backend/app/services/bid_qualification_service.py`
- `backend/app/api/routers/proposal.py`
- `backend/app/api/routers/proposal_versions.py`
- `backend/app/api/routers/bid_qualification.py`
- `backend/app/core/db.py`
- `backend/app/api/routers/bids.py`
- `backend/app/models/__init__.py`
- `backend/app/api/routers/__init__.py`
- `backend/tests/test_dot9_backend.py`

## Verification

- `python3 -m pytest -q tests/test_dot9_backend.py` trong `backend/`: **7 passed**.
- Đã bổ sung test chuỗi phiên bản `1.0 → 1.1 → 2.0` và cập nhật deal stage có audit history.
- `python3 -m pytest -q tests/test_settings.py tests/test_dot9_backend.py tests/test_approval.py`: **12 passed**.
- `python3 -m pytest -q` trong `backend/`: **238 passed**.
- Có cảnh báo deprecation từ `httpx`/`starlette TestClient`, không làm fail suite.
- Không chạy Preview/browser ở boundary backend; không claim runtime UI pass.
- Không sửa frontend và không thực hiện tester/reviewer.

## Contract notes cho frontend

- Settings `GET /api/settings` trả `keys[]`; mỗi item có `key`, `payload`, `yaml_preview`. Các key Dot 9 có thể có payload dạng list (`case_studies`), frontend không nên giả định mọi payload là object.
- Proposal `document.table_of_contents` là danh sách key section; `translations` là map ngôn ngữ → section object. Backend lưu bản dịch được gửi lên; mock translation tự động chỉ sao chép nội dung hiện tại để không giả lập chất lượng dịch.
- `PUT /api/bids/{id}/bid-qualification` trả `suggestions` cần người review; backend không tự quyết định Bid/No-bid.
- `POST /api/bids/{id}/proposal/versions` nhận `{by, language?}`; `PUT /api/bids/{id}/proposal/versions/{version_id}/sent` đánh dấu gửi và ghi history.

## Giới hạn / follow-up

- Chưa có upload binary logo/template; backend hiện lưu metadata/template built-in và kiểm tra cấu trúc payload. Nếu UI cần upload thực, frontend/backend integration step phải nối vào attachment validation hiện có.
- Đã bổ sung SQLite schema reconciliation cho các cột Dot 9 nullable/default-safe trên database cũ; vẫn cần tester xác minh khởi động Preview thật.
- Cần tester xác minh response trên Preview và reviewer kiểm tra migration trên database đã tồn tại.

## DONE

Đã tự review backend, ghi handoff và dừng đúng boundary.
