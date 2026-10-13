# Đánh giá Preview M4 — hồ sơ mẫu CRM

| Thuộc tính | Kết quả |
|---|---|
| Ngày đánh giá | 2026-10-10 |
| Hồ sơ | `#76` — CRM, dữ liệu giả lập, khách hàng Nhật |
| Môi trường | Preview production mode, `LLM_PROVIDER=mock` |
| Phạm vi | WBS, master schedule, hướng giải pháp/effort, báo giá, proposal/requirement response |

## 1. Cách chạy và dữ liệu đầu vào

- Preview stack khởi động thành công: backend và frontend đều `Up`; frontend được truy cập qua port preview `5173`.
- Tạo hồ sơ mẫu bằng `POST /api/bids/sample`, nhận hồ sơ `#76`.
- Pipeline dừng đúng ở bước làm rõ sau vòng 1. Gửi đủ 5 câu trả lời giả định ở vòng 1, rồi đủ 5 câu ở vòng 2. Pipeline hoàn tất các bước `intake`, `gap`, `solution`, `wbs` và chuyển hồ sơ sang `waiting_tech_approval`.
- Một lần gọi API đầu tiên dùng nhầm `round=1` thay vì `round_no=2`, backend trả `400 VALIDATION_ERROR` rõ ràng; không làm thay đổi trạng thái. Sau đó gửi đúng vòng 2 và chạy thành công.
- UI kiểm tra qua các route:
  - `/bids/76`
  - `/bids/76/solution`
  - `/bids/76/wbs`
  - `/bids/76/schedule`

## 2. Đánh giá WBS

### Kết quả quan sát

- WBS hiển thị đủ 3 cấp với tổng 27 item:
  - Nhóm cấp 1: PoC, MVP, Production.
  - Task cấp 2 và sub-task cấp 3.
- Tổng man-day: **57.6**.
- Phân bổ theo phase:
  - PoC: 12.0
  - MVP: 30.0
  - Production: 15.6
- Kiểm tra trên UI đều đạt:
  - Tổng effort trong ±20% midpoint: **Đạt**, midpoint 57.6, lệch 0%.
  - Mỗi phase có PM + QA: **Đạt**.
  - Phụ thuộc không vòng: **Đạt**.
  - Task lá ≤ 10 man-day: **Đạt**, lớn nhất 6.0.
- Man-day được backend tính từ effort/weight; output WBS của LLM không chứa man-day.
- Hướng giải pháp được hiển thị là **RAG** với lý do: dữ liệu phi cấu trúc cần truy vấn ngữ nghĩa.

### Điểm tốt

- Chất lượng cấu trúc phù hợp cho bản estimate sơ bộ: đủ PM/QA mỗi phase, có backend/frontend/AI/infra/BA/QA, và có một dependency minh họa `WBS-002-01-04 → WBS-002-01-02`.
- UI dễ kiểm tra: cột phase, role, man-day, dependency và các cờ kiểm tra hiển thị ngay trên cùng màn hình.
- Có guard rõ ràng cho task lá và override.

### Hạn chế

- Mock WBS mô tả CRM ở mức khung; chưa có các task cụ thể cho migration Excel, deduplication, audit/security, integration accounting/sales, backup/monitoring và UAT theo từng requirement. Vì vậy WBS phù hợp để minh họa M4, chưa đủ làm baseline proposal thực tế.
- Requirement response/traceability không được sinh trong M4; không có route/API `/requirements`, matrix hoặc bảng map requirement → WBS task.

## 3. Đánh giá lịch

Đã gửi:

```json
{
  "start_date": "2026-11-02",
  "buffer_days": 5,
  "working_calendar": "jp",
  "team_allocation": {
    "pm": 1, "ba": 1, "brse": 1, "ai_engineer": 1,
    "backend": 2, "frontend": 1, "qa": 1, "infra": 1
  },
  "payment_milestones": [
    {"name": "Kickoff", "percent": 20, "due_offset_days": 0},
    {"name": "MVP", "percent": 50, "due_offset_days": 30},
    {"name": "Bàn giao", "percent": 30, "due_offset_days": 60}
  ]
}
```

### Kết quả quan sát

- PUT và GET schedule đều trả **200**.
- Gantt có 18 task bars, ngày bắt đầu task do backend trả.
- Ngày nghỉ Nhật `2026-11-03` được áp dụng.
- Mốc thanh toán được tính đúng theo ngày lịch:
  - Kickoff: 2026-11-02
  - MVP: 2026-12-02
  - Bàn giao: 2027-01-01
- Ngày kết thúc: **2027-02-01**.
- Hạn nộp hồ sơ: **2026-12-15**.
- UI hiển thị cảnh báo: lịch vượt hạn nộp.
- Công thức schedule và dữ liệu by-role được hiển thị, giúp reviewer kiểm tra lại phép tính.

### Đánh giá nghiệp vụ

- Lịch hiện tại **không đạt deadline**: trễ khoảng 48 ngày so với hạn nộp.
- Đây là cảnh báo hữu ích, không bị che giấu; UI hướng dẫn tăng số người hoặc giảm phạm vi.
- Có thể điều chỉnh headcount và tính lại mà không gọi AI, đúng mục tiêu M4.
- Lịch đang là mô hình tuần tự theo phase/task. Với proposal thật, cần xác nhận thêm các task có thể chạy song song; nếu không, duration sẽ bảo thủ và có thể làm deadline trễ hơn cần thiết.

## 4. Đánh giá báo giá

- Không có endpoint `/api/bids/76/quotation`; request trả **404 Not Found**.
- UI hiển thị ngân sách là **“Không cung cấp”**.
- `budget_amount` và `budget_currency` vẫn là `null`.
- WBS response giữ `recalculated.quotation = null` theo phạm vi M4.

### Kết luận

Đây là hành vi **đúng với scope và price gate**: M4 không tính hoặc hiển thị báo giá trước khi có cơ chế duyệt giá của M5. Không phát hiện giá tự sinh từ LLM hoặc giá chưa được human approval.

## 5. Đánh giá proposal / bảng đáp ứng requirement

- Không có endpoint `/api/bids/76/proposal` hoặc `/api/bids/76/requirements`; cả hai trả **404 Not Found**.
- Pipeline step `proposal` vẫn ở trạng thái `pending` với ghi chú chưa triển khai ở M4.
- Hồ sơ có phần “Kết quả phân tích yêu cầu” và “Hướng giải pháp”, nhưng chưa có customer-facing proposal, compliance matrix hoặc bảng requirement response.
- Vì customer sample là tiếng Nhật, câu hỏi làm rõ được sinh bằng tiếng Nhật; phân tích nội bộ hiển thị tiếng Việt. Đây là điểm phù hợp với rule ngôn ngữ.

### Kết luận

Không thể đánh giá chất lượng proposal/requirement response như một deliverable M4 vì tính năng nằm ngoài phạm vi. Đây là khoảng trống cần bàn giao rõ sang M6/M7, không phải lỗi M4.

## 6. Kiểm tra rule và an toàn

- `WbsStructure` không chứa man-day, effort, price, amount hoặc date; số do code/reference table tính.
- LLM mock được dùng trong Preview; không có real LLM call trong lần đánh giá.
- Customer text mẫu ghi rõ dữ liệu giả lập. Prompt/context pipeline dùng dữ liệu đã mask PII theo test hiện có.
- Frontend dùng API base root-relative `/api`; không phát hiện hardcode localhost trong `frontend/src`.
- Không thấy secret/API key trong output hoặc log đánh giá.
- Error contract hoạt động: dùng sai clarification round trả 400 tiếng Việt và giữ nguyên trạng thái chờ làm rõ.

## 7. Kết luận tổng hợp

| Hạng mục | Đánh giá | Nhận xét |
|---|---|---|
| WBS | **Đạt M4** | 3 cấp, effort 57.6, PM/QA đủ, lá ≤10, không vòng |
| Lịch | **Đạt chức năng, cần xử lý cảnh báo** | Gantt/milestone đúng; baseline hiện tại vượt deadline |
| Báo giá | **Chưa có — đúng scope M4** | Bị chặn đúng bởi price gate; chờ M5 |
| Proposal | **Chưa có — đúng scope M4** | Step proposal pending; chờ M6/M7 |
| Requirement matrix | **Chưa có — gap bàn giao** | Chưa có route/field để trace requirement → WBS |

**Kết luận:** Preview M4 chạy được end-to-end đến WBS và schedule trên hồ sơ mẫu. Chất lượng WBS/schedule đáp ứng acceptance criteria M4; lịch cảnh báo deadline đúng và minh bạch. Báo giá và proposal không được sinh, phù hợp phạm vi M4 và price gate. Đề xuất ưu tiên tiếp theo là bổ sung traceability requirement → WBS trước khi dùng WBS này làm đầu vào cho proposal customer-facing.
