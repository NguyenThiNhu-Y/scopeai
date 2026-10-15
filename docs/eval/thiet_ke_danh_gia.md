# Thiết kế: đánh giá độ tin cậy và thư viện case study

Upload file này vào project VibeFlow thành `docs/eval/thiet_ke_danh_gia.md`. Mọi agent đọc file này trước khi làm Đợt 12–13.

## 1. Mục tiêu

Trả lời câu hỏi: **WBS, effort và master schedule do hệ thống tạo ra đáng tin tới đâu?** Trả lời ở hai tầng:

| Tầng | Câu hỏi | Ai dùng | Khi nào |
|---|---|---|---|
| **Độ tin cậy từng hồ sơ** | Hồ sơ này nên tin ước lượng tới đâu, cần soi chỗ nào? | Presales, người duyệt kỹ thuật | Mỗi lần mở hồ sơ, khi duyệt |
| **Đánh giá offline** | Cả hệ thống ước lượng đúng tới đâu so với đáp án? Prompt mới tốt hơn hay tệ hơn? | AI engineer | Khi đổi prompt, đổi model, trước khi phát hành |

Nguồn dữ liệu chung là **thư viện case study**: các dự án đã làm, có effort và thời gian **thực tế**.

## 2. Nguyên tắc (bổ sung cho AGENTS.md)

1. **Độ tin cậy do code tính, không do LLM tự chấm.** LLM không sinh điểm, không sinh %, không sinh con số nào.
2. **Không hiện % giả chính xác.** Hiện mức **Cao / Trung bình / Thấp** kèm danh sách lý do kiểm chứng được.
3. **Không tự sửa con số.** So sánh với case study chỉ để **cảnh báo**; effort và giá vẫn tính từ bảng chuẩn như cũ.
4. **Ít dữ liệu thì nói ít dữ liệu.** Dưới 2 case tương tự thì trạng thái "Chưa đủ dữ liệu tham chiếu", không kết luận.
5. **Giữ đơn giản.** Không vector DB. Tìm case tương tự bằng lọc thuộc tính và điểm tương đồng tính bằng code.
6. **Dữ liệu giả lập.** Case study trong repo đều giả lập, ghi rõ "(giả lập)". Không tên công ty thật.

## 3. Thư viện case study

### 3.1 Lưu trữ
- Giữ cơ chế hiện có: settings key `case_studies` (YAML dạng list, có phiên bản, sửa trên web tạo phiên bản mới).
- Giá trị mặc định nạp từ `backend/app/reference/case_studies.yaml` (gộp 2 file dữ liệu mẫu ở cuối mục 3.2), thay cho mẫu 1 dòng hiện tại trong `OPTIONAL_DEFAULTS`. File WBS mẫu copy vào `backend/app/reference/case_studies_wbs/` và nạp như file đính kèm mặc định.

### 3.2 Schema một case study (kiểm tra bằng Pydantic khi lưu và khi import)

| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `id` | str, duy nhất | ✓ | vd `cs_none_crm_jp` |
| `title` | str | ✓ | có hậu tố "(giả lập)" với dữ liệu mẫu |
| `industry` | str | ✓ | |
| `market` | `jp` / `vn` / `other` | ✓ | |
| `customer_language` | `ja` / `vi` / `en` | ✓ | |
| `direction` | `none` / `traditional_ml` / `rag` / `agent` / `fine_tune` | ✓ | cùng tập với hướng giải pháp |
| `requirement_count` | int ≥ 1 | ✓ | |
| `factors` | list key trong `factors.yaml` | | để tham khảo |
| `year` | int | | |
| `public` | bool | ✓ | true thì được trích vào proposal |
| `summary` | str | ✓ | |
| `estimated_man_day` | `{poc, mvp, production}` số ≥ 0 | | ước lượng lúc chào thầu |
| `actual_man_day` | `{poc, mvp, production}` số ≥ 0 | ✓ để dùng so sánh | effort thực tế |
| `actual_duration_weeks` | `{poc, go_no_go, mvp, production}` | | thời gian thực tế |
| `team_peak` | `{pm, ba, brse, ai_engineer, backend, frontend, qa, infra}` | | số người lúc cao điểm |
| `lessons_vi` | list str | | bài học |
| `tech` | list str | | công nghệ đã dùng |
| `bid_outcome` | `{result: won/lost, bid_month, contract_model: {poc, mvp, production}, win_reason_vi / lost_reason_vi}` | | kết quả chào thầu |
| `wbs_file` | str | | đường dẫn file WBS Excel của dự án (xem 3.4) |

Case thiếu `actual_man_day` (ví dụ thua thầu) vẫn lưu được, dùng cho bài học chào thầu và proposal, nhưng không dùng để so sánh effort hay đánh giá.

Dữ liệu mẫu gồm hai file, gộp lại khi nạp mặc định:
- `docs/eval/case_studies_gia_lap.yaml`: 8 case chung. Bỏ `cs_rag_maintenance_jp_vn` vì trùng chủ đề với bộ Tokai.
- `docs/eval/du_an_cu_tokai/case_studies_tokai.yaml`: 6 dự án liên quan bộ demo Tokai Minato, có WBS Excel.

### 3.3 Nhập và xuất
- `GET /api/settings/case_studies/template`: tải file Excel mẫu, 1 dòng = 1 case, cột theo schema (các trường lồng tách cột: `actual_poc`, `actual_mvp`, `actual_production`…).
- `POST /api/settings/case_studies/import` (multipart: `.xlsx`, `.csv`, `.yaml`), tham số `mode=preview|save`:
  - `preview`: trả danh sách dòng hợp lệ và lỗi theo từng dòng (số dòng, tên cột, lý do), không lưu.
  - `save`: gộp theo `id` (trùng thì ghi đè), lưu thành phiên bản settings mới, ghi changelog.
- Che PII trong `summary` và `lessons_vi` khi import, giống mọi đầu vào khác.

### 3.4 File WBS của dự án cũ
- Mỗi case có thể đính kèm 1 file WBS Excel, lưu ở `data/case_studies/<id>/`, đường dẫn ghi vào `wbs_file`.
- Định dạng theo bộ mẫu `docs/eval/du_an_cu_tokai/wbs/*.xlsx`:
  - sheet `WBS`: cột Mã, Hạng mục (VI), 作業項目 (JA), Giai đoạn, Vai trò, Man-day ước lượng, Man-day thực tế, Chênh lệch, Requirement liên quan, Ghi chú; mã 3 cấp `1`, `1.1`, `1.1.01`;
  - các sheet `Thông tin dự án`, `Tổng hợp`, `Lịch thực tế`, `Bài học`.
- Code đọc file bằng parser Excel sẵn có. Kiểm tra tổng man-day thực tế theo giai đoạn khớp `actual_man_day` (lệch > 1 man-day thì cảnh báo, không chặn).
- `POST /api/settings/case_studies/{id}/wbs` để tải file lên; `GET` cùng đường dẫn để tải về.
- Tính "điểm nóng": task có man-day thực tế vượt ước lượng > 30%, dùng ở mục 4b và để hiển thị.

### 3.5 Bài học chào thầu (tùy chọn nếu kịp)
Trong Bid/No-bid, hiện các case **cùng hướng giải pháp và thị trường** đã `lost`, kèm `lost_reason_vi`, để người quyết định tham khảo. Chỉ hiển thị, không tự đổi điểm.

## 4. Truy vết requirement → WBS

Hiện `wbs_items` không biết task nào phục vụ requirement nào. Bổ sung:

- **LLM schema** `WbsTaskItem`: thêm `requirement_codes: list[str]` (tối đa 8), chỉ trên task lá. Đây là phân loại, không phải con số; test `test_llm_schema_no_numbers` vẫn phải pass.
- **Prompt B5**: truyền danh sách requirement gọn (mã + 80 ký tự đầu + category), tối đa 150 dòng; yêu cầu mỗi task lá ghi mã requirement nó thực hiện; requirement nào chưa rõ thì để trống, không đoán.
- **Code**: bỏ mã không tồn tại (ghi vào `notes`), lưu `requirement_codes` (JSON, nullable) vào `wbs_items`; migration bổ sung cột giống cách các đợt trước.
- **Sửa tay**: `WbsTaskIn` và bảng WBS cho sửa `requirement_codes`; sửa xong tính lại truy vết.
- **Mock**: fixture B5 gán mã requirement cho task lá theo category (FR → backend/frontend, NFR → infra/qa, đều theo vòng tròn). Requirement đang "cần làm rõ" thì **không** gán (chưa đủ thông tin để lập kế hoạch). Với mẫu Nhật: 34/36 được truy vết, 2 mục cần làm rõ hiện trong danh sách "chưa có task".

## 4b. Gợi ý cấu trúc WBS từ dự án tương tự (tùy chọn nếu kịp)

- Khi chạy B5, lấy case tương tự nhất (mục 5.4) có `wbs_file`, đọc **tên nhóm và tên task** (không lấy con số), truyền vào prompt thành "Cấu trúc tham khảo từ dự án tương tự". Kèm tối đa 5 "điểm nóng" dạng chữ, ví dụ "OCR tài liệu scan: thực tế vượt ước lượng".
- LLM vẫn chỉ trả cấu trúc và trọng số. Code vẫn gán man-day từ bảng chuẩn.
- Ghi vào trace WBS: `structure_hint_case_id`, để người duyệt biết WBS đã tham khảo dự án nào.
- Tín hiệu mới `hotspot_coverage` (thông tin, không ảnh hưởng mức): các điểm nóng của dự án tương tự đã có task tương ứng trong WBS mới chưa, so khớp theo từ khóa.

## 5. Độ tin cậy từng hồ sơ

### 5.1 Service và API
- `backend/app/services/confidence_engine.py`: hàm thuần, đầu vào là dữ liệu hồ sơ đã có (intake, questions, evaluations, WBS check, schedule, effort, case studies), đầu ra là dict. Không gọi LLM.
- `GET /api/bids/{id}/confidence` → `ConfidenceOut`:

```json
{
  "level": "high | medium | low",
  "level_label_vi": "Cao | Trung bình | Thấp",
  "summary_vi": "2 cảnh báo: WBS thấp hơn dự án tương tự; thiếu mốc Production của khách",
  "signals": [
    {"key": "traceability", "label_vi": "Truy vết requirement", "status": "pass|warn|fail|na",
     "detail_vi": "34/36 requirement có task", "data": {"covered": 34, "total": 36, "uncovered": ["FR-024", "NFR-005"]}}
  ],
  "analog": {
    "cases": [{"id": "...", "title": "...", "similarity": 0.86, "requirement_count": 34,
               "actual_man_day": {"poc": 31, "mvp": 142, "production": 62}, "actual_total": 235,
               "actual_duration_weeks": {...}}],
    "actual_total_range": [235, 266], "estimate_total": 210.0, "effort_midpoint": 241.5,
    "position": "below|inside|above|insufficient",
    "history_bias": {"direction": "none", "median_actual_over_estimate": 1.07, "case_count": 3}
  },
  "thresholds_version": 1,
  "case_studies_version": 2
}
```

- Ngưỡng nằm trong `backend/app/reference/confidence.yaml` (có phiên bản, sửa được trong Cài đặt như các bảng chuẩn khác).

### 5.2 Các tín hiệu

| key | Tên hiển thị | Cách tính | pass | warn | fail |
|---|---|---|---|---|---|
| `input_completeness` | Đầu vào | Có: ngân sách, mốc bắt đầu khách, mốc MVP hoặc Production khách, file requirement; số câu hỏi chặn chưa trả lời | đủ 4, không còn câu chặn | thiếu 1–2 | thiếu ≥ 3 hoặc còn câu chặn |
| `wbs_checks` | Kiểm tra WBS | 4 cờ của CheckEngine | 4/4 | — | thiếu ≥ 1 |
| `schedule_checks` | Kiểm tra lịch | MVP bắt đầu ≥ hết go/no-go; Production sau MVP; kết thúc ≤ mốc khách (nếu có); không cảnh báo lịch | đạt hết | trễ mốc khách ≤ 2 tuần | sai thứ tự giai đoạn hoặc trễ > 2 tuần |
| `traceability` | Truy vết requirement | requirement có ≥ 1 task lá / tổng requirement | ≥ 95% | 80–95% | < 80% |
| `coverage_uncertainty` | Độ chắc của đánh giá đáp ứng | (△ + × + cần làm rõ) / tổng | ≤ 15% | 15–30% | > 30% |
| `analog` | So với dự án tương tự | Vị trí của tổng WBS so với khoảng effort thực tế của case tương tự (mở rộng ±10%) | trong khoảng | ngoài khoảng ≤ 20% | ngoài khoảng > 20% |
| `history_bias` | Sai lệch lịch sử | Trung vị (thực tế ÷ ước lượng) của case cùng hướng, cần ≥ 2 case | trong 0,9–1,1 | ngoài 0,9–1,1 | — |

Không có dữ liệu thì `na` kèm lý do (vd "Chưa đủ dữ liệu tham chiếu: 1 case cùng hướng").

### 5.3 Quy tắc ra mức (cố định, có test)
- **Thấp:** có `fail` ở tín hiệu quan trọng (`wbs_checks`, `schedule_checks`, `traceability`) **hoặc** tổng số `fail` ≥ 2.
- **Trung bình:** có ít nhất 1 `fail` khác, **hoặc** ≥ 2 `warn`.
- **Cao:** còn lại.
- `summary_vi` liệt kê tối đa 3 lý do quan trọng nhất (fail trước warn).

### 5.4 Tìm case tương tự
1. Lọc: cùng `direction`, có `actual_man_day`.
2. Điểm tương đồng (0–1), code tính:
   `0,4 × cùng market + 0,3 × (1 − min(|req_a − req_b| / max(req_a, req_b), 1)) + 0,2 × cùng ngôn ngữ khách + 0,1 × trùng từ khóa ngành/tiêu đề với tóm tắt intake`
3. Lấy tối đa 3 case có điểm ≥ 0,5, xếp giảm dần. Dưới 2 case thì `position = insufficient`.
4. Không nhân hệ số, không quy đổi quy mô: hiện số thực tế gốc kèm số requirement để người đọc tự đánh giá.

### 5.5 Gắn vào luồng duyệt
- Duyệt kỹ thuật hiện đầy đủ tín hiệu. Nếu mức **Thấp** thì bắt buộc nhập nhận xét (≥ 10 ký tự) mới duyệt được.
- Khi duyệt kỹ thuật, lưu kèm kết quả độ tin cậy và phiên bản `case_studies`, `confidence.yaml` vào bản ghi duyệt (snapshot), để sau này xem lại được vì sao đã duyệt.

## 6. Đánh giá offline (eval harness)

### 6.1 Cấu trúc
```
backend/eval/
  cases/            # golden case YAML (copy từ docs/eval/golden_cases.yaml, tách mỗi case 1 file)
  metrics.py        # hàm thuần tính chỉ số, có unit test
  run_eval.py       # chạy pipeline đầy đủ cho từng case, tự trả lời câu hỏi bằng answers trong case
  report.py         # ghi docs/eval/reports/eval_<YYYYMMDD_HHMM>_<provider>.md và .json
```
- Lệnh: `cd backend && python -m eval.run_eval [--case gc_crm_ja] [--repeat 1]`; thêm `make eval` (dùng `LLM_PROVIDER` hiện tại, mặc định mock).
- Test tự động **chỉ** chạy với mock: unit test cho `metrics.py` và 1 smoke test chạy 1 case. Không test nào gọi LLM thật.
- `--repeat N` (chỉ có ý nghĩa với LLM thật): chạy N lần, đo độ ổn định.

### 6.2 Chỉ số mỗi case

| Chỉ số | Định nghĩa |
|---|---|
| `direction_ok` | Hướng giải pháp nằm trong `acceptable_directions` |
| `total_ape` | \|tổng WBS − trung điểm khoảng đáp án\| ÷ trung điểm |
| `total_in_expected` | Tổng WBS nằm trong khoảng đáp án |
| `interval_hit` | Khoảng [min, max] của effort engine giao với khoảng đáp án |
| `phase_share_error` | ½ × Σ \|tỉ trọng giai đoạn ước lượng − tỉ trọng đáp án\| |
| `traceability_pct` | Như tín hiệu `traceability` |
| `must_trace_ok` | Mọi mã trong `must_trace` đều có task |
| `checks_pass` | Số kiểm tra WBS + lịch đạt / tổng |
| `duration_weeks_error` | \|tổng tuần theo lịch − trung điểm tuần đáp án\| |
| `question_rounds`, `question_count` | Số vòng, số câu hỏi |
| `confidence_level` | Mức độ tin cậy hệ thống tự đưa ra |
| `llm_calls`, `seconds` | Số lần gọi LLM, thời gian chạy |
| `stability_cv` | (khi `--repeat` ≥ 2) hệ số biến thiên của tổng WBS giữa các lần |

### 6.3 Tổng hợp
MAPE (trung bình `total_ape`), tỉ lệ `total_in_expected`, tỉ lệ `interval_hit`, `direction_ok` %, trung bình `traceability_pct`, `checks_pass` %. Báo cáo ghi rõ **provider và model**; với mock, ghi chú: "Mock chỉ kiểm tra harness, không đo chất lượng AI".

### 6.4 Màn hình (tùy chọn nếu kịp)
- `GET /api/eval/reports/latest` đọc file JSON mới nhất trong `docs/eval/reports/`.
- Tab Cài đặt "Đánh giá hệ thống": bảng tổng hợp và bảng từng case, ghi provider, thời gian chạy.

## 7. Giao diện

| Nơi | Thêm gì |
|---|---|
| Tổng quan | Thẻ "Độ tin cậy ước lượng": huy hiệu Cao/Trung bình/Thấp, tối đa 3 lý do, link "Xem chi tiết" |
| Kế hoạch & báo giá | Khối "So với dự án tương tự": bảng case (tên, hướng, thị trường, số requirement, effort thực tế từng giai đoạn, tổng, số tuần) và thanh so sánh từng giai đoạn: ước lượng so với khoảng thực tế. Dòng "Sai lệch lịch sử: thực tế thường cao hơn ước lượng 7% (3 dự án cùng hướng)". Trạng thái "Chưa đủ dữ liệu tham chiếu" khi thiếu |
| Kế hoạch & báo giá (WBS) | Cột "Requirement" (chip mã, rút gọn, hover hiện nội dung); dòng "Truy vết: 34/36 requirement có task" và danh sách requirement chưa có task |
| Quy trình & phê duyệt | Trong Duyệt kỹ thuật: danh sách đủ tín hiệu (biểu tượng đạt/cảnh báo/lỗi, lý do); mức Thấp thì bắt buộc nhận xét |
| Cài đặt › Case study | Bảng danh sách (tên, hướng, thị trường, số requirement, tổng thực tế, công khai); form sửa đủ trường; nút "Tải file mẫu", "Nhập từ file" (xem trước, lỗi từng dòng, rồi lưu); đếm số case theo hướng giải pháp |
| Cài đặt › Ngưỡng độ tin cậy | Sửa ngưỡng trong `confidence.yaml` như các bảng chuẩn khác |

Nhãn tiếng Việt, không hiện mã thô (`none` → "Không dùng AI", `rag` → "Tra cứu theo tài liệu", `pass` → "Đạt"…).

## 8. Ngoài phạm vi
Vector DB; tự động hiệu chỉnh hệ số từ case study; LLM tự chấm độ tin cậy; dùng dữ liệu dự án thật.
