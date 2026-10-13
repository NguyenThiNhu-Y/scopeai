# QA Check — Đợt 8

Ngày kiểm thử: 2026-10-11  
Vai trò: QA / tester  
Môi trường: Preview compose, `LLM_PROVIDER=mock`  
Mẫu sử dụng: `ja_email` (dữ liệu giả lập tiếng Nhật)

## Tóm tắt

| Kết quả | Số lượng |
|---|---:|
| Pass | 7 |
| Fail | 1 |
| Blocked | 9 |
| Tổng | 17 |

Browser automation chạy được bằng Chromium bundled mà script QA đã hỗ trợ. Các screenshot runtime được lưu dưới `docs/ui_current/`.
Một lỗi runtime thật được phát hiện trên hồ sơ Nhật: `TypeError: Cannot read properties of undefined (reading 'split')` trong phần Proposal; tab Proposal render rỗng. Không sửa app source trong vai trò QA.

## Kết quả theo test case

| TC-ID | Phạm vi | Kết quả | Expected | Actual / bằng chứng |
|---|---|---|---|---|
| D8-API-01 | Tạo hồ sơ mẫu Nhật | **Pass** | Tạo được hồ sơ `ja_email`, ngôn ngữ `ja`, tiền tệ hiển thị JPY | `POST /api/bids/sample` trả `201`; bid `109`, `customer_language=ja`, `display_currency=JPY` |
| D8-API-02 | Đọc file mẫu | **Pass** | Parse được bộ file và đếm requirement | `POST /api/bids/109/parse` trả `200`; `requirements.count=36`, `no_requirement_file=false` |
| D8-API-03 | Xác nhận parse và bắt đầu pipeline | **Pass** | Confirm thành công; pipeline bắt đầu bằng `202` | `PUT /api/bids/109/parse/confirm` trả `200`; `POST /api/bids/109/pipeline/start` trả `202`, status `analyzing` |
| D8-API-04 | Vòng hỏi 1 có lý do chặn | **Pass** | Pipeline dừng khi thiếu thông tin; câu hỏi vòng 1 có lý do và trạng thái chờ trả lời | Hồ sơ chuyển `waiting_clarification`; `GET /api/bids/109/questions` trả `rounds_used=1`, 5 câu hỏi, mỗi câu có `reason_vi`, status `awaiting_answer` |
| D8-API-05 | State conflict trước khi đủ dữ liệu | **Pass** | Không hiển thị effort/quotation/schedule/WBS giả khi pipeline chưa qua vòng hỏi | API trả `409 STATE_CONFLICT` tương ứng: chưa chọn hướng giải pháp, chưa có WBS, chưa có lịch; `GET /evaluations` trả `evaluated=0` |
| D8-UI-01 | Tạo hồ sơ, giới hạn và tiền tệ | **Pass** | Trang có nút nhập file, giới hạn 200.000 ký tự, trường tiền tệ; chọn mẫu Nhật đặt tiền tệ JPY | DOM assertion pass; evidence: `docs/ui_current/dot8_create_runtime.png`, `docs/ui_current/dot8_create_ja_selected.png` |
| D8-UI-02 | Tổng quan KPI | **Blocked** | Hiển thị requirement/% đáp ứng, câu hỏi chưa trả lời, man-day, giá, ngày kết thúc, trạng thái duyệt | Chưa có hồ sơ hoàn tất để xác minh giá trị KPI; runtime sample đang chờ làm rõ |
| D8-UI-03 | Danh sách statistics | **Blocked** | Hiển thị tổng hồ sơ, đang phân tích, chờ duyệt, đã duyệt, đã gửi | Không chạy được browser; API hiện chỉ trả `items` và `total`, chưa có stats theo trạng thái |
| D8-UI-04 | Giải pháp risks/feasibility | **Blocked** | Hiển thị 4–6 risk có type/level/description/mitigation, điểm khả thi 1–5, lý do hệ số | Luồng Nhật dừng ở vòng hỏi 1 nên chưa tạo solution; chưa thể xác minh dữ liệu sau vòng hỏi |
| D8-UI-05 | Effort factor table | **Blocked** | Bảng phase, chuẩn min–max, hệ số có nhãn tiếng Việt/lý do, kết quả, tổng WBS, lệch % | Luồng chưa có effort vì state conflict; chưa có browser evidence |
| D8-UI-06 | Staffing theo role/phase và gợi ý theo effort | **Blocked** | Sửa headcount, có nút gợi ý, lưu và tính lại lịch bằng code | Chưa tới tab kế hoạch do pipeline chờ câu hỏi; browser không chạy được |
| D8-UI-07 | Master schedule và Gantt tuần | **Blocked** | Sửa ngày bắt đầu/buffer/go-no-go/mốc khách/ngày nghỉ; Gantt theo tuần, task label, marker | API chưa có lịch ở state hiện tại; browser không chạy được |
| D8-UI-08 | Inline WBS | **Blocked** | Sửa input/select inline, thêm task/group, xóa icon, lưu một lần và tính lại tổng/lịch | API chưa có WBS ở state hiện tại; browser không chạy được |
| D8-UI-09 | Payment detail và price gate | **Blocked** | Payment milestones nằm trong chi tiết báo giá; giá customer-facing bị khóa trước phê duyệt | Chưa có quotation do state conflict; browser không chạy được |
| D8-UI-10 | Vòng hỏi 2 điều kiện | **Blocked** | Chỉ xuất hiện nếu còn thông tin chặn sau vòng 1 và UI hiển thị lý do | Chỉ mới kiểm được vòng 1 bằng API; chưa gửi đáp án qua UI để tạo nhánh vòng 2 |
| D8-UI-11 | Kế hoạch tab render | **Pass** | Tab hiển thị khu vực nhân sự/lịch và cấu trúc công việc | DOM assertion pass; evidence: `docs/ui_current/dot8_plan_runtime.png` |
| D8-UI-12 | Proposal render | **Fail** | Tab Proposal phải hiển thị nội dung proposal hoặc trạng thái tải/lỗi rõ ràng | Body rỗng, không có heading; console có `TypeError ... undefined (reading 'split')`; evidence: `docs/ui_current/dot8_proposal_runtime.png`, `docs/ui_current/runtime_report.json` |

## Kiểm tra tự động

| Lệnh | Kết quả |
|---|---|
| `python3 -m pytest -q` trong `backend/` | **PASS**, toàn bộ test pass; còn cảnh báo Starlette/httpx deprecation |
| `npm test -- --run` trong `frontend/` | **PASS**, 11 tests passed |
| `npm run build` trong `frontend/` | **PASS**, `tsc -b && vite build` |
| `podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d` | **PASS**, backend/frontend chạy; frontend build production thành công |

## Vấn đề và giới hạn

1. Tab Proposal có lỗi runtime khi dữ liệu proposal thiếu section: `sections[key].split(...)` không chống `undefined`; tab render rỗng. Cần frontend-dev sửa và chạy lại browser test.
2. API `GET /api/bids` chỉ trả `items` và `total`, chưa có stats theo trạng thái; card thống kê Danh sách chưa thể chứng minh bằng API.
3. Luồng mẫu Nhật dừng đúng ở `waiting_clarification` sau vòng 1. Cần trả lời câu hỏi bằng browser/API để tiếp tục xác minh solution, effort, WBS, schedule và quotation.
4. Các tương tác sâu (import file thật, staffing save/recalculation, WBS add/edit/delete/save, payment collapse, price gate) chưa thực thi trong script này và được giữ là Blocked.
5. `docs/ui/dot8_review.md` là deliverable của role reviewer; đã được tạo sau bước QA và kết luận các case còn Blocked cùng lỗi Proposal runtime.

## Commands / evidence

- Preview: `podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d`
- Backend tests: `python3 -m pytest -q` từ `backend/`
- Frontend tests/build: `npm test -- --run`, `npm run build` từ `frontend/`
- API smoke test: chuỗi `POST /api/bids/sample` → `POST /parse` → `PUT /parse/confirm` → `POST /pipeline/start` và poll `GET /api/bids/{id}`.
- Browser QA: `PLAYWRIGHT_BROWSERS_PATH_EXECUTABLE=/opt/toolbox/amd64/playwright-browsers/chromium_headless_shell-1187/chrome-linux/headless_shell python3 scripts/ui_qa_playwright.py`.
- Targeted browser assertions: create/currency/plan/proposal, evidence `docs/ui_current/dot8_*.png`.
- Runtime inventory and console errors: `docs/ui_current/runtime_report.json`.
