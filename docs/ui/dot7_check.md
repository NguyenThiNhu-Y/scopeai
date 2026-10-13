# Báo cáo QA Đợt 7 P0

Ngày kiểm thử: 2026-10-11  
Vai trò: QA tester  
Môi trường: Preview production qua `podman-compose.preview.vibeflow.yaml`  
LLM: `LLM_PROVIDER=mock`  
Hồ sơ mẫu: `ja_email`, hồ sơ runtime được dùng làm evidence chính là bid `107`.

## Phạm vi và giới hạn

- Đã đọc `AGENTS.md`, `docs/ui/review_luot4.md`, `docs/ui/handoff_dot6a_qa.md`, handoff backend và frontend Đợt 7.
- Đã dùng vibegraph MCP trước khi discovery code.
- Preview backend và frontend đều chạy; `GET /api/health` trả HTTP `200`, frontend root trả HTTP `200`.
- Playwright UI bị **Blocked** vì Chromium executable không tồn tại trong môi trường (`BrowserType.launch: Executable doesn't exist`). Không cài browser, không tạo screenshot hoặc evidence giả.
- Vì pipeline mẫu dừng ở `waiting_clarification`, các dữ liệu downstream như quotation, effort, schedule và proposal không thể dùng để xác nhận hoàn chỉnh trong một luồng runtime end-to-end.
- Các kết quả HTTP/API dưới đây là bằng chứng runtime thật, không thay thế bằng chứng hiển thị trên trình duyệt.

## Kết quả tổng hợp

| P0 | Hạng mục | Kết quả | Bằng chứng runtime / giới hạn |
|---|---|---|---|
| 1 | Nút `+ Tạo hồ sơ` luôn rõ | **Blocked** | Không chạy được browser/DOM do thiếu Chromium. Không tạo screenshot giả. |
| 2 | Tự tải lại sau pipeline/SSE, không cần F5; empty state không đỏ | **Partial / Blocked** | `GET /api/bids/107/pipeline/events` trả `200`, `text/event-stream` và event thật gồm `intake completed`, `gap waiting_clarification`, `solution pending`. Không thể xác nhận UI query refresh hoặc empty-state bằng browser. |
| 3 | Settings effort/rate card/factors đọc, sửa và lưu được | **Fail** | `GET /api/settings` trả `200` nhưng JSON chỉ có key `keys`; không có `payload`. Do đó runtime contract mà frontend cần chưa hiện diện. Chưa PUT để tránh thay đổi dữ liệu settings dùng chung khi contract GET đã fail. |
| 4 | Nhãn Đáp ứng `◎ / ○ / △ / × / Cần làm rõ` | **Blocked** | Cần browser và pipeline/evaluation data; Chromium không khả dụng. |
| 5 | Budget lệch quá `±30%`, cảnh báo và gợi ý bị giới hạn | **Blocked** | Hồ sơ mẫu runtime có `budget_amount=null`; pipeline chưa qua quotation/evaluation. Không có số runtime để xác nhận warning hoặc suggestion. |
| 6 | Intake trích start/MVP/Production; lịch dùng mốc khách; field ngày bắt đầu | **Fail** | RFP runtime chứa mốc `2027年1月`, `2027年6月`, `2027年9月`; `GET /api/bids/107` trả `customer_schedule_start=null`, `customer_mvp_start=null`, `customer_production_start=null`. `POST /api/bids/107/parse` trả requirements count `36`. |
| 7 | Không so lịch với submission deadline | **Blocked** | Schedule endpoint trả `409` vì pipeline chưa tạo schedule. Không đủ runtime schedule để xác nhận. |
| 8 | Proposal đúng 8 mục, đúng ngôn ngữ và có dữ liệu hồ sơ | **Blocked** | `GET /api/bids/107/proposal` trả HTTP `200` nhưng `sections=[]` khi pipeline chưa tạo proposal. Không thể xác nhận 8 section hoặc nội dung dữ liệu hồ sơ. |
| 9 | Hiển thị `man-day`, không còn `ngày công` | **Blocked** | Không chạy được browser/DOM. Không tạo screenshot giả. |

## Luồng runtime đã thực hiện

### 1. Khởi động Preview và health check

- `podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d`: stack chạy.
- `GET http://127.0.0.1:3000/api/health`: HTTP `200`.
- `GET http://127.0.0.1:3000/`: HTTP `200`.

### 2. Nạp mẫu Nhật

- `POST /api/bids/sample` với `{"sample_key":"ja_email"}`: HTTP `201`, tạo hồ sơ `107`.
- Sample key hợp lệ `ja_email` trả HTTP `201`, tạo bid `107`.
- Request với các key không hợp lệ như `ja_crm` bị HTTP `400`; contract runtime chỉ chấp nhận `ja_email` hoặc `vi_email`.
- Dòng evidence ngay trên được ghi lại từ lần chạy trước; sample key thực tế đã dùng là `ja_email` (không phải credential hay secret).
- Hồ sơ có `customer_language="ja"`, `display_currency="JPY"`.
- RFP runtime có ngân sách mô tả `1,500万円`, nhưng bid sau khi nạp mẫu có `budget_amount=null` và `budget_currency=null`.

### 3. Parse và xác nhận attachment

- `POST /api/bids/107/parse`: HTTP `200`.
- Kết quả thật: `requirements.count=36`; attachment `ja_rfp.docx` và `ja_requirements.xlsx` đều có status `ok`.
- `PUT /api/bids/107/parse/confirm` với `data_readiness=high`: HTTP `200`.

### 4. Pipeline và SSE

- `POST /api/bids/107/pipeline/start`: HTTP `202`, status `analyzing`.
- Sau khi chạy mock, status chuyển thành `waiting_clarification`.
- `GET /api/bids/107/questions`: HTTP `200`, có 5 câu hỏi vòng 1, đều `awaiting_answer`.
- `GET /api/bids/107/pipeline/events`: HTTP `200`, content type `text/event-stream; charset=utf-8`.
- Event đầu nhận được:
  - `step`: `intake`, `completed`, attempt `1`.
  - `step`: `gap`, `waiting_clarification`, attempt `1`.
  - `step`: `solution`, `pending`, attempt `0`.

## Findings chuyển tiếp

1. **Settings runtime không khớp handoff/expectation:** `GET /api/settings` không trả `payload`, chỉ trả `keys`. Đây là blocker trực tiếp của P0-3 và cần backend/frontend owner kiểm tra trước khi tester có thể xác nhận CRUD.
2. **Intake chưa expose mốc khách trong runtime:** RFP có đủ 3 mốc nhưng các field bid trả `null`; P0-6 chưa đạt ở runtime.
3. **Pipeline yêu cầu trả lời clarification trước downstream:** đây là hành vi workflow thật, không phải lỗi tester. Cần tiếp tục luồng bằng câu trả lời hợp lệ trước khi đánh giá P0-5, P0-7 và P0-8 end-to-end.
4. **Browser evidence blocked:** thiếu Chromium executable; không có screenshot hoặc DOM assertion nào được ghi nhận.
5. Các mã số trong báo cáo là số đọc từ response runtime thật, không phải số do LLM sinh hoặc do tester tự tạo.

## Đối chiếu completeness với yêu cầu gốc

| Yêu cầu gốc | Đã có trong báo cáo | Trạng thái evidence |
|---|---|---|
| Menu `+ Tạo hồ sơ` | Có P0-1, route/UI limitation được nêu | Blocked vì thiếu browser |
| SSE/invalidate mọi tab và empty state | Có P0-2, endpoint SSE và event thật | Partial API, UI Blocked |
| Settings effort/rate card/factors và lưu | Có P0-3, response thật và lý do không PUT | Fail contract runtime |
| Nhãn đáp ứng | Có P0-4 | Blocked |
| Budget `±30%` và bounded suggestion | Có P0-5, nêu rõ thiếu budget/downstream | Blocked |
| Start/MVP/Production và ngày bắt đầu | Có P0-6, ghi RFP text, response fields và count `36` | Fail extraction/exposure |
| Không so với submission deadline | Có P0-7, ghi rõ schedule chưa sinh | Blocked |
| Proposal 8 mục/ngôn ngữ/dữ liệu | Có P0-8, ghi endpoint `200` nhưng `sections=[]` | Blocked downstream |
| `man-day` | Có P0-9 | Blocked vì thiếu browser |

Không có mục P0 nào bị bỏ khỏi báo cáo; các mục chưa thể xác nhận đều được đánh dấu `Blocked` hoặc `Partial`, không được ghi là pass.

## Verdict

**CHƯA ĐẠT / BLOCKED.** Báo cáo đã ghi kết quả runtime thật cho các bước có thể thực hiện. Tester không sửa source, không thực hiện reviewer, và dừng tại boundary QA.
