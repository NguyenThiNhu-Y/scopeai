# Đánh giá Preview — M6 và đầu ra hồ sơ mẫu

| Thuộc tính | Giá trị |
|---|---|
| Slice | M6 — Đính kèm file và ma trận đáp ứng |
| Ngày | 2026-10-10 |
| Môi trường | Preview compose, `LLM_PROVIDER=mock`, backend/frontend `Up` |
| Hồ sơ | `POST /api/bids/sample`, bid `83`, sample mặc định `ja_email` |
| Phạm vi | Requirement matrix, pipeline, WBS, lịch, báo giá, proposal và AGENTS rules |

## 1. Tóm tắt chạy Preview

Preview khởi động thành công bằng `podman-compose`:

- Backend và frontend đều ở trạng thái `Up`.
- `GET /api/health` trả `200`, `status=ok`, `database=ok`, `llm_provider=mock`.
- `POST /api/bids/sample` trả `201`, tạo bid `83`, trạng thái `draft`, tiền tệ hiển thị `JPY` và ngân sách `null`.
- Không thể chạy click-through bằng Playwright vì môi trường thiếu Chromium executable:
  `Executable doesn't exist at /home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`.

Sau khi gọi `PUT /api/bids/83/parse/confirm` với `confirmed=true`, pipeline vẫn được chấp nhận bởi API và chuyển sang `analyzing`. Kết quả sau đó:

```text
intake: completed
gap: waiting_clarification
evaluate: pending
solution: pending
wbs: pending
proposal: pending
ja_check: pending
```

Đây là hành vi dừng pipeline để hỏi làm rõ, không phải lỗi LLM hay lỗi tính số. Vì chưa trả lời câu hỏi làm rõ, các output WBS/lịch/báo giá chưa thể được đánh giá end-to-end.

## 2. Đánh giá các output

### 2.1 Requirement matrix

**Kết quả:** Không đạt acceptance M6 trong Preview.

`GET /api/bids/83/attachments` trả `{"items":[]}` và `GET /api/bids/83/evaluations` trả:

```json
{
  "solution_direction": null,
  "warnings": [],
  "items": [],
  "stats": {
    "total": 0,
    "evaluated": 0,
    "◎": 0,
    "○": 0,
    "△": 0,
    "×": 0,
    "needs_clarification": 0
  }
}
```

M6 yêu cầu nạp hồ sơ mẫu đầy đủ gồm text + RFP + Excel requirement giả lập, hiển thị số requirement trước AI và tạo ma trận sau khi parse/confirm. Sample hiện tại chỉ đọc một file text vào `Bid.request_content`; không tạo attachment, không parse workbook và không tạo requirement rows. Vì vậy `total=0` ở đây không chứng minh “hồ sơ không có requirement”, mà chứng minh sample Preview chưa cung cấp input M6.

### 2.2 WBS

**Kết quả:** Bị chặn đúng trạng thái, chưa có output để chấm chất lượng.

`GET /api/bids/83/wbs` trả `409 STATE_CONFLICT` với thông báo chưa có WBS. Pipeline dừng ở bước `gap` trước `solution` và `wbs`, nên chưa thể xác nhận:

- LLM có chỉ phân loại/cấu trúc hay bịa man-day không.
- `assign_man_days` có phân bổ đúng effort code tính từ reference YAML không.
- WBS có đủ ba cấp, dependency và semantic warning không.

### 2.3 Lịch

**Kết quả:** Bị chặn đúng trạng thái, chưa có output để chấm chất lượng.

`GET /api/bids/83/schedule` trả `409 STATE_CONFLICT` với thông báo chưa có lịch. Do chưa có WBS nên chưa thể đánh giá ngày bắt đầu/kết thúc, ngày làm việc, ngày lễ Nhật, buffer và cảnh báo deadline `2026-12-15`.

### 2.4 Báo giá

**Kết quả:** Bị chặn đúng trạng thái, chưa có output để chấm chất lượng.

`GET /api/bids/83/quotation` trả `409 STATE_CONFLICT` với thông báo chưa có WBS. Đây là chặn hợp lý ở trạng thái hiện tại. Không có bằng chứng Preview nào cho thấy LLM đã sinh effort, rate, FX hay price.

### 2.5 Proposal và price gate

**Kết quả:** Đạt kiểm tra placeholder ở trạng thái chưa duyệt.

`GET /api/bids/83/proposal` trả:

- `price_gate: "placeholder"`
- `quotation_markdown: "[Presales điền]"`
- các section ở trạng thái chờ proposal

Không thấy số tiền trong proposal chưa duyệt. Điều này phù hợp AGENTS rule 5: giá chưa được đưa vào customer-facing output trước khi human approval. Tuy nhiên chưa thể kiểm tra nhánh sau price approval vì pipeline chưa qua được clarification và chưa có quotation.

## 3. Findings

### HIGH — Sample Preview không nạp đủ hồ sơ M6

- **Vị trí:** `backend/app/services/sample_service.py:51-78`
- **Bằng chứng runtime:** `POST /api/bids/sample` tạo một `Bid` từ `ja_email.md`; ngay sau đó `GET /api/bids/83/attachments` trả `items=[]`. Thư mục `sample_data/` chỉ có `ja_email.md` và `vi_email.md`, không có RFP/Excel/sample-data bundle.
- **Tác động:** Không thể thực hiện acceptance §1.1(8), TC-M6-001, TC-M6-006, TC-M6-008, TC-M6-010 và TC-M6-011 trên Preview. `total=0` của matrix không phản ánh năng lực parser/evaluator M6.
- **Cách sửa cụ thể:** Bổ sung bộ sample fictional gồm tối thiểu RFP, workbook requirement nhiều sheet và sample-data file; `load_sample()` phải tạo attachment rows/đường dẫn file tương ứng hoặc một fixture import service dùng cùng parser production. Thêm integration test assert sau `POST /bids/sample`: có attachment, parse được, requirement count > 0 và sample profile có columns.

### HIGH — Confirm gate cho phép chạy pipeline khi chưa parse attachment

- **Vị trí:** `backend/app/services/parse_service.py:32-36`; `backend/app/pipeline/orchestrator.py:115-132`
- **Bằng chứng:** Tôi gọi `PUT /api/bids/83/parse/confirm` khi bid chưa có attachment và chưa gọi parse; API trả `200`. Sau đó `POST /api/bids/83/pipeline/start` trả `202`.
- **Tác động:** Với hồ sơ M6 có attachment nhưng chưa parse, gate chỉ dựa vào `data_readiness`, không kiểm tra `parse_status=ok`, mapping confirmed hay parse error. Người dùng có thể xác nhận dữ liệu chưa được đọc, trái với M6 §2.5 và §3.1.
- **Cách sửa cụ thể:** Persist trạng thái parse-confirmed riêng; `confirm` phải yêu cầu parse result hiện hành, reject attachment `pending/error` và reject mapping chưa xác nhận. `_ensure_parse_confirmed()` phải kiểm tra cùng điều kiện ở DB trước khi start, không chỉ kiểm tra có `data_readiness`.

### HIGH — Intake gửi toàn văn request content thay vì context summary giới hạn của M6

- **Vị trí:** `backend/app/pipeline/steps/b1_intake.py:37-47`
- **Bằng chứng code path:** `run_intake()` lấy toàn bộ `bid.request_content`, mask PII rồi đưa trực tiếp vào prompt; không đọc output parser/attachment và không áp dụng `RFP_SUMMARY_MAX_CHARS` theo M6 §3.1.
- **Tác động:** Vi phạm contract “không gửi toàn văn RFP vào LLM”; customer text có thể chứa prompt injection, và RFP lớn có thể vượt giới hạn context. Runtime sample còn cho thấy `request_content` chứa email và số điện thoại fictional; việc mask phải được kiểm tra trên prompt thực tế, không chỉ unit test.
- **Cách sửa cụ thể:** Parser tạo summary deterministic giới hạn ký tự trước; mask PII trước khi gửi; chỉ gửi summary/context chuẩn hóa qua gateway. Lưu `attachments_status`, `requirement_count`, `no_requirement_file`, `sample_profile` và `rfp_summary` trong output step. Thêm integration test capture `MockLLMClient.last_prompt`, kiểm tra không có PII raw, không vượt max chars và customer text chứa chỉ thị giả không thể override system prompt.

### MEDIUM — Không có bằng chứng Preview cho các output số và luồng sau clarification

- **Vị trí:** `backend/app/pipeline/steps/b5_wbs.py:61-100`; `backend/app/services/schedule_engine.py:132-195`; `backend/app/services/quotation_engine.py:9-47`
- **Bằng chứng:** WBS, schedule và quotation đều bị 409 vì pipeline dừng ở `gap`; chưa trả lời questions và chưa chọn solution direction.
- **Tác động:** AGENTS rule 8 yêu cầu feature phải chạy được trong Preview, nhưng test_report chỉ có health/sample smoke và 12 UI case bị block bởi Chromium. Automated unit tests có thể chứng minh công thức cục bộ nhưng không chứng minh vertical slice M6/M5 chạy liên tục từ hồ sơ mẫu.
- **Cách sửa cụ thể:** Sau khi bổ sung sample bundle, chạy một scenario độc lập: parse → confirm → pipeline → trả lời clarification → chọn solution → WBS → schedule → quotation → proposal; lưu JSON response/screenshot và assert số effort/lịch/giá xuất phát từ engine/reference snapshot, không từ LLM. Nếu chủ ý dừng ở clarification, report phải đánh dấu rõ đây là scenario chưa hoàn tất thay vì coi Preview acceptance đã đạt.

### MEDIUM — Endpoint sample tạo dữ liệu mới nhưng không có cơ chế reset/isolation cho đánh giá lặp lại

- **Vị trí:** `backend/app/api/routers/bids.py:54-62`; `backend/app/services/sample_service.py:64-77`
- **Bằng chứng:** Mỗi lần gọi sample tạo một `Bid` mới và commit; không có cleanup/reset trong Preview. Bài chạy đã tạo bid `83`, còn database Preview tiếp tục giữ state pipeline.
- **Tác động:** Scenario review lặp lại có thể đọc nhầm bid cũ, làm nhiễu tổng số hồ sơ và khiến kết quả phụ thuộc thứ tự chạy. Đây không phải data loss trong Preview, nhưng làm giảm tính tái lập của acceptance evidence.
- **Cách sửa cụ thể:** Thêm sample run identifier hoặc endpoint reset chỉ trong `APP_ENV=preview`, hoặc tạo fixture database/seed idempotent cho test. Báo cáo mỗi lần chạy phải ghi bid id và trạng thái ban đầu.

## 4. Đối chiếu AGENTS rules 1–10

- **Rule 1 — Không bịa số:** Không quan sát được WBS/schedule/quotation runtime vì pipeline dừng sớm. Code path được thiết kế để effort/schedule/price tính bằng engine; cần vertical evidence sau khi sample đầy đủ.
- **Rule 2 — Structured LLM:** `complete_with_retry` validate schema và retry bounded; chưa kiểm chứng end-to-end vì chỉ intake completed, các step sau pending.
- **Rule 3 — Một gateway/mock:** Preview dùng `llm_provider=mock`; không thấy real LLM call trong smoke run.
- **Rule 4 — Hỏi thay vì đoán:** Pipeline dừng ở `waiting_clarification`, đây là hành vi đúng; tuy nhiên sample thiếu requirement khiến flow không thể đánh giá đúng phạm vi M6.
- **Rule 5 — Price gate:** Đạt trong trạng thái hiện tại: proposal trả placeholder và không có số tiền chưa duyệt.
- **Rule 6 — Privacy:** Unit mask coverage tồn tại, nhưng B1 vẫn có đường gửi toàn `request_content`; cần capture prompt integration test.
- **Rule 7 — Ngôn ngữ:** UI/API sample có tiếng Việt nội bộ và sample khách hàng tiếng Nhật; chưa đánh giá proposal cuối vì chưa qua pipeline.
- **Rule 8 — Done means proven:** Chưa đạt cho M6 Preview: health/sample pass nhưng sample không đầy đủ, browser UI bị blocked, pipeline chưa đi qua matrix/WBS/schedule/quotation.
- **Rule 9 — Keep it simple:** Preview dùng backend/frontend compose đơn giản; không phát hiện hạ tầng thừa trong phạm vi chạy này.
- **Rule 10 — Root-relative API:** Frontend gọi qua các path `/api/...`; health smoke qua frontend preview thành công.

## 5. Kết luận và đề nghị

**Verdict: CHANGES REQUIRED**

Top findings:

1. **HIGH:** Sample fixture không có attachment RFP/Excel/sample-data, nên M6 matrix không thể chạy và các output downstream không thể đánh giá.
2. **HIGH:** Confirm gate chấp nhận dữ liệu chưa parse; đã tái hiện trực tiếp bằng API.
3. **HIGH:** B1 có nguy cơ gửi toàn văn customer text cho LLM, trái giới hạn summary và tăng rủi ro prompt injection/PII.
4. **MEDIUM:** Chưa có Preview evidence cho WBS, lịch và báo giá; proposal placeholder hiện tại là đúng price gate nhưng chưa phải proposal hoàn chỉnh.

Developer cần xử lý các finding HIGH, bổ sung sample bundle và regression/integration tests, sau đó rerun scenario end-to-end. Khi môi trường có Chromium, cần rerun TC-M6-001..012 bằng browser và ghi evidence. Nếu cần tiếp tục remediation, hãy yêu cầu Developer áp dụng các finding trong chat hoặc chạy lại workflow cho milestone M6.

## Handoff Note

Reviewer đã hoàn tất đánh giá Preview và ghi báo cáo tại `docs/reviews/M6-preview-evaluation.md`. Không thay đổi source code. Preview đã được chạy với mock LLM; health và sample endpoint pass, nhưng sample chưa đủ input M6 và pipeline dừng ở `waiting_clarification`. Handoff cho Developer: bổ sung sample attachment bundle, siết confirm gate, giới hạn/mask context B1 và thêm integration evidence cho matrix → WBS → schedule → quotation → proposal. Verdict hiện tại là **CHANGES REQUIRED**.
