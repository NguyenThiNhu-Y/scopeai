# Test Cases — M2 Phân tích yêu cầu + hỏi làm rõ (Acceptance)

| Thuộc tính | Giá trị |
|---|---|
| Milestone | M2 — Phân tích yêu cầu + hỏi làm rõ |
| Chuẩn template | IPA (mặc định — không có template/chuẩn được chỉ định) |
| Định dạng | Markdown |
| Nguồn | `docs/slices/M2/spec.md` §5(b)/(c), `docs/slices/M2/handoff_to_test.md`, `AGENTS.md` |
| Môi trường | Preview podman-compose (origin :5173, proxy `/api` → backend :8000), `LLM_PROVIDER=mock` |
| Ngày | 2026-10-09 |

## Legend trường

| Field | Ý nghĩa |
|---|---|
| TC-ID | `TC-M2-NN` — định danh duy nhất |
| 機能名 / Function | Chức năng kiểm thử |
| 画面 / Screen | Màn hình / endpoint |
| 観点 / Viewpoint | 正常系 / 準正常系 / 異常系 / 境界値 / Security |
| テスト項目 / Test Item | Mô tả ngắn |
| 事前条件 / Precondition | Trạng thái trước khi thực hiện |
| テスト手順 / Procedure | Các bước thao tác cụ thể |
| 期待結果 / Expected Result | Kết quả mong đợi (kiểm chứng được) |
| 備考 / Notes | Ghi chú thêm |

---

## A. Tạo hồ sơ (BidNewPage)

### TC-M2-001: Form tạo hồ sơ hiển thị đầy đủ

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-001 |
| **機能名** | Tạo hồ sơ (FR-001) |
| **画面** | `/bids/new` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Form đầy đủ trường + hint 30 ký tự + 2 nút nạp mẫu |
| **事前条件** | Mở app, preview đang chạy (mock LLM) |
| **テスト手順** | 1. Vào `/bids/new` 2. Quan sát form |
| **期待結果** | 1. Có 7 trường: Tên dự án*, Tên khách hàng*, Hạn nộp*, Ngôn ngữ khách* (vi/en/ja), Nội dung yêu cầu* (textarea), Ngân sách (tùy chọn), Đơn vị tiền tệ (tùy chọn) 2. Hint "tối thiểu 30 ký tự" + bộ đếm ký tự 3. Có 2 nút "Nạp mẫu tiếng Nhật" / "Nạp mẫu tiếng Việt" 4. Nút "Tạo hồ sơ" |
| **備考** | spec §5(b) bước 1 |

### TC-M2-002: Tạo hồ sơ hợp lệ → 201 → chi tiết Nháp

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-002 |
| **機能名** | Tạo hồ sơ (FR-001) |
| **画面** | `/bids/new` → `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Happy path tạo hồ sơ với dữ liệu hợp lệ |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Điền Tên dự án "Hệ thống CRM ABC (giả lập)" 2. Khách hàng "Công ty XYZ (giả lập)" 3. Hạn nộp ngày hợp lệ 4. Ngôn ngữ khách `vi` 5. Nội dung yêu cầu ≥ 30 ký tự 6. Bấm "Tạo hồ sơ" |
| **期待結果** | 1. Điều hướng tới `/bids/{id}` 2. Trạng thái hiển thị "Nháp" 3. Nội dung yêu cầu hiển thị 4. Không có lỗi |
| **備考** | spec §5(b) bước 1–2 (phần hợp lệ) |

### TC-M2-003: Nội dung yêu cầu < 30 ký tự → lỗi tiếng Việt

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-003 |
| **機能名** | Validate tạo hồ sơ (FR-001.1) |
| **画面** | `/bids/new` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | `request_content` ngắn bị chặn |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Điền đủ các trường bắt buộc 2. Nội dung yêu cầu = "Ngắn quá" (8 ký tự) 3. Bấm "Tạo hồ sơ" |
| **期待結果** | 1. Lỗi tiếng Việt hiển thị (chứa "30 ký tự") 2. Không điều hướng, không tạo hồ sơ 3. (Server) `400 VALIDATION_ERROR` + `details.min_length=30` |
| **備考** | spec §5(b) bước 2 |

### TC-M2-004: Boundary 29 / 30 / 31 ký tự

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-004 |
| **機能名** | Validate độ dài `request_content` (FR-001.1) |
| **画面** | `/bids/new` + API |
| **観点** | 境界値 (Boundary) — 3-point |
| **テスト項目** | 29 ký tự → lỗi; 30 → OK; 31 → OK |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Nội dung yêu cầu đúng 29 ký tự → Tạo → ghi kết quả 2. Nội dung đúng 30 ký tự → Tạo → ghi kết quả 3. Nội dung đúng 31 ký tự → Tạo → ghi kết quả |
| **期待結果** | 1. 29 ký tự → lỗi "ít nhất 30 ký tự", không tạo 2. 30 ký tự → tạo thành công 3. 31 ký tự → tạo thành công |
| **備考** | 3-point rule (IPA) |

### TC-M2-005: Thiếu trường bắt buộc → lỗi

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-005 |
| **機能名** | Validate tạo hồ sơ (FR-001) |
| **画面** | `/bids/new` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Bỏ trống từng trường bắt buộc |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Để trống Tên dự án, điền đủ phần còn lại → Tạo 2. Để trống Tên khách hàng → Tạo 3. Để trống Hạn nộp → Tạo 4. Để trống Nội dung yêu cầu → Tạo |
| **期待結果** | Mỗi lần: lỗi tiếng Việt hiển thị cho trường thiếu; không tạo hồ sơ; không điều hướng |
| **備考** | — |

### TC-M2-006: XSS payload không chạy script

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-006 |
| **機能名** | Bảo mật đầu vào (Security) |
| **画面** | `/bids/new` → `/bids/{id}` |
| **観点** | Security (XSS) |
| **テスト項目** | Nội dung yêu cầu chứa `<script>` được hiển thị dạng text |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Nội dung yêu cầu = `<script>window.__xss=1</script>` + đủ 30 ký tự 2. Tạo hồ sơ 3. Mở chi tiết, kiểm tra `window.__xss` và nội dung hiển thị |
| **期待結果** | 1. Hồ sơ tạo được 2. Trang chi tiết hiển thị chuỗi `<script>` dạng text (React escape) 3. `window.__xss` undefined (script không chạy) |
| **備考** | React mặc định escape; kiểm chứng runtime |

### TC-M2-007: SQLi payload không gây lỗi

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-007 |
| **機能名** | Bảo mật đầu vào (Security) |
| **画面** | `/bids/new` + API |
| **観点** | Security (SQLi) |
| **テスト項目** | Payload `' OR 1=1 --` bị xử lý an toàn |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Tên dự án = `x' OR 1=1 --` 2. Điền đủ còn lại → Tạo |
| **期待結果** | 1. Tạo thành công (hoặc lỗi validate bình thường) 2. Không crash, không lộ dữ liệu lạ trong danh sách (parameterized query) |
| **備考** | SQLAlchemy parameterized |

### TC-M2-008: Ngân sách tùy chọn điền được

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-008 |
| **機能名** | Tạo hồ sơ (FR-001) |
| **画面** | `/bids/new` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Điền budget_amount + budget_currency |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Điền đủ trường bắt buộc 2. Ngân sách = 50000000, Đơn vị tiền tệ = JPY 3. Tạo hồ sơ |
| **期待結果** | 1. Tạo thành công 2. Chi tiết hiển thị ngân sách + đơn vị tiền tệ |
| **備考** | — |

---

## B. Hồ sơ mẫu giả lập (sample)

### TC-M2-009: Nạp mẫu tiếng Nhật

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-009 |
| **機能名** | Hồ sơ mẫu giả lập (FR-006) |
| **画面** | `/bids/new` → `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Nút "Nạp mẫu tiếng Nhật" tạo hồ sơ mẫu |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Bấm "Nạp mẫu tiếng Nhật" 2. Chờ điều hướng |
| **期待結果** | 1. Điều hướng tới `/bids/{id}` mới 2. Trạng thái "Nháp" 3. Nội dung email tiếng Nhật hiển thị 4. Có ghi chú "DỮ LIỆU GIẢ LẬP" |
| **備考** | spec §5(b) bước 3 |

### TC-M2-010: Nạp mẫu tiếng Việt

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-010 |
| **機能名** | Hồ sơ mẫu giả lập (FR-006) |
| **画面** | `/bids/new` → `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Nút "Nạp mẫu tiếng Việt" tạo hồ sơ mẫu |
| **事前条件** | Trên `/bids/new` |
| **テスト手順** | 1. Bấm "Nạp mẫu tiếng Việt" |
| **期待結果** | 1. Điều hướng tới `/bids/{id}` mới 2. Nội dung tiếng Việt hiển thị 3. Có ghi chú "DỮ LIỆU GIẢ LẬP" |
| **備考** | spec §5(b) bước 12 (phần tạo) |

### TC-M2-011: sample_key không hợp lệ → 400

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-011 |
| **機能名** | Hồ sơ mẫu giả lập (FR-006) |
| **画面** | API `POST /api/bids/sample` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | `sample_key` lạ bị từ chối |
| **事前条件** | Backend reachable |
| **テスト手順** | 1. `POST /api/bids/sample` body `{"sample_key":"xyz"}` |
| **期待結果** | 1. `400 VALIDATION_ERROR` + `details.allowed` chứa `ja_email`, `vi_email` |
| **備考** | spec §2.1 |

---

## C. Pipeline + SSE + Chờ làm rõ

### TC-M2-012: Bấm Phân tích → tiến độ realtime 7 bước

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-012 |
| **機能名** | Pipeline M2 (FR-023) |
| **画面** | `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | SSE cập nhật tiến độ: intake → gap; 5 bước còn lại pending |
| **事前条件** | Hồ sơ mẫu tiếng Nhật ở trạng thái Nháp |
| **テスト手順** | 1. Bấm "Phân tích" 2. Quan sát tiến độ |
| **期待結果** | 1. `intake` hiển thị running → completed (≤ 5s) 2. `gap` hiển thị running 3. 5 bước còn lại (`evaluate`, `solution`, `wbs`, `proposal`, `ja_check`) hiển thị pending mờ "chưa triển khai ở M2" 4. Trạng thái hồ sơ chuyển "Đang phân tích" |
| **備考** | spec §5(b) bước 4; NFR-001 |

### TC-M2-013: Dừng Chờ làm rõ — câu hỏi tiếng Nhật + lý do tiếng Việt

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-013 |
| **機能名** | Hỏi làm rõ (FR-010) |
| **画面** | `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Gap sinh ≤ 7 câu hỏi đúng ngôn ngữ + badge |
| **事前条件** | Hồ sơ mẫu tiếng Nhật, vừa bấm Phân tích |
| **テスト手順** | 1. Chờ pipeline dừng 2. Quan sát phần câu hỏi |
| **期待結果** | 1. Trạng thái hồ sơ "Chờ làm rõ" 2. Hiển thị 1–7 câu hỏi bằng tiếng Nhật 3. Mỗi câu có lý do tiếng Việt (`reason_vi`) 4. Mỗi câu có badge mức ảnh hưởng (Giải pháp/Effort/Giá) 5. Nút "Phân tích" disabled + hint "Hãy trả lời câu hỏi làm rõ trước" |
| **備考** | spec §5(b) bước 5; BR-07, NFR-004 |

### TC-M2-014: Start pipeline khi đang analyzing → 409

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-014 |
| **機能名** | Guard pipeline (FR-023) |
| **画面** | API `POST /api/bids/{id}/pipeline/start` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Chạy đồng thời bị chặn |
| **事前条件** | Pipeline đang chạy (analyzing) |
| **テスト手順** | 1. Start pipeline 2. Start lại ngay lần 2 |
| **期待結果** | 1. Lần 2 → `409 STATE_CONFLICT` |
| **備考** | spec §2.1 |

### TC-M2-015: Start khi Chờ làm rõ → 409 CLARIFY_PENDING

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-015 |
| **機能名** | Guard pipeline (FR-010.3) |
| **画面** | API `POST /api/bids/{id}/pipeline/start` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Không chạy lại khi còn câu hỏi chưa trả lời |
| **事前条件** | Hồ sơ đang `waiting_clarification` |
| **テスト手順** | 1. `POST /pipeline/start` |
| **期待結果** | 1. `409 CLARIFY_PENDING` |
| **備考** | spec §2.1 |

---

## D. Trả lời câu hỏi

### TC-M2-016: Để trống 1 câu → nhắc trả lời câu thiếu

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-016 |
| **機能名** | Trả lời câu hỏi (FR-011.3) |
| **画面** | `/bids/{id}` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Submit thiếu câu bị chặn + highlight |
| **事前条件** | Hồ sơ `waiting_clarification`, có ≥ 2 câu hỏi |
| **テスト手順** | 1. Trả lời 1 câu, để trống câu khác 2. Bấm "Gửi trả lời" |
| **期待結果** | 1. Lỗi tiếng Việt "Vui lòng trả lời tất cả câu hỏi trước khi gửi" 2. Câu thiếu được highlight (viền đỏ) 3. Không gửi, pipeline không chạy |
| **備考** | spec §5(b) bước 6 |

### TC-M2-017: Trả lời theo giả định → nhãn

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-017 |
| **機能名** | Trả lời giả định (FR-011.2) |
| **画面** | `/bids/{id}` |
| **観点** | 準正常系 (Semi-normal) |
| **テスト項目** | Checkbox giả định được lưu + hiển thị nhãn |
| **事前条件** | Hồ sơ `waiting_clarification` |
| **テスト手順** | 1. Trả lời 1 câu, bật checkbox "Trả lời theo giả định" 2. Trả lời đủ các câu còn lại 3. Gửi trả lời 4. Chờ vòng sau (hoặc done) |
| **期待結果** | 1. Câu đã trả lời hiển thị nhãn "(giả định)" / "giả định — cần khách xác nhận" 2. API `GET /questions` trả `is_assumption=true` cho câu đó |
| **備考** | spec §5(b) bước 7 |

### TC-M2-018: Trả lời đủ → resume từ gap → Chờ duyệt kỹ thuật

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-018 |
| **機能名** | Resume pipeline (FR-011.3, FR-010.4) |
| **画面** | `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Trả lời đủ 2 vòng → gap completed → waiting_tech_approval; intake không chạy lại |
| **事前条件** | Hồ sơ `waiting_clarification` (mock sinh câu hỏi cả 2 vòng) |
| **テスト手順** | 1. Trả lời đủ vòng 1 → Gửi 2. Chờ vòng 2 xuất hiện, trả lời đủ → Gửi 3. Chờ pipeline xong |
| **期待結果** | 1. Sau vòng 1: pipeline resume từ `gap` (SSE chỉ thấy `gap` chạy lại, `intake` giữ completed) 2. Sau vòng 2: `gap` completed 3. Trạng thái hồ sơ "Chờ duyệt kỹ thuật" 4. Kết quả phân tích B1 hiển thị (mục tiêu/người dùng/dữ liệu/ràng buộc/ngân sách/thời hạn/ngôn ngữ phát hiện) |
| **備考** | spec §5(b) bước 8; FR-010.4 (sau vòng 2 không gọi LLM) |

### TC-M2-019: Gửi câu hỏi không thuộc vòng hiện tại → 400

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-019 |
| **機能名** | Trả lời câu hỏi (FR-011) |
| **画面** | API `POST /api/bids/{id}/questions/{round}/answers` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Câu hỏi vòng 1 gửi vào vòng 2 bị từ chối |
| **事前条件** | Hồ sơ đang ở vòng 2 (`rounds_used=2`) |
| **テスト手順** | 1. Gửi `answers` chứa `question_id` thuộc vòng 1 với `round=2` |
| **期待結果** | 1. `400 VALIDATION_ERROR` "Câu hỏi không thuộc vòng này" |
| **備考** | handoff known-gap #2 (đúng thiết kế) |

### TC-M2-020: Trả lời thiếu câu qua API → missing_ids

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-020 |
| **機能名** | Trả lời câu hỏi (FR-011.3) |
| **画面** | API `POST /api/bids/{id}/questions/{round}/answers` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Body thiếu câu → `details.missing_ids` |
| **事前条件** | Hồ sơ `waiting_clarification` vòng 1 (5 câu) |
| **テスト手順** | 1. Gửi `answers` chỉ 3/5 câu |
| **期待結果** | 1. `400 VALIDATION_ERROR` + `details.missing_ids` chứa 2 id còn thiếu |
| **備考** | spec §2.1 |

---

## E. Danh sách + mở lại hồ sơ

### TC-M2-021: Danh sách hiển thị + lọc + tìm

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-021 |
| **機能名** | Danh sách hồ sơ (FR-007) |
| **画面** | `/bids` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Bảng hiển thị đúng trạng thái; lọc status; tìm q |
| **事前条件** | Có ≥ 2 hồ sơ ở trạng thái khác nhau |
| **テスト手順** | 1. Vào `/bids` 2. Lọc theo status "Chờ duyệt kỹ thuật" 3. Tìm theo tên dự án |
| **期待結果** | 1. Bảng hiển thị tên dự án/khách hàng/trạng thái/hạn nộp/ngôn ngữ 2. Lọc status chỉ còn hồ sơ đúng trạng thái 3. Tìm q trả về hồ sơ khớp |
| **備考** | spec §5(b) bước 9 |

### TC-M2-022: Mở lại hồ sơ Chờ làm rõ — trả lời tiếp được

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-022 |
| **機能名** | Mở lại hồ sơ (FR-007.2) |
| **画面** | `/bids/{id}` |
| **観点** | 正常系 (Normal) |
| **テスト項目** | Câu hỏi chưa trả lời còn đó sau khi mở lại |
| **事前条件** | Có hồ sơ `waiting_clarification` |
| **テスト手順** | 1. Điều hướng tới hồ sơ Chờ làm rõ 2. Quan sát phần câu hỏi |
| **期待結果** | 1. Câu hỏi chưa trả lời hiển thị đầy đủ 2. Trả lời + Gửi được (pipeline resume) |
| **備考** | spec §5(b) bước 10 |

### TC-M2-023: Phân trang qua API

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-023 |
| **機能名** | Danh sách hồ sơ (FR-007) |
| **画面** | API `GET /api/bids` |
| **観点** | 境界値 (Boundary) |
| **テスト項目** | `page_size=1&page=2` trả đúng lát cắt + `total` |
| **事前条件** | Có ≥ 2 hồ sơ |
| **テスト手順** | 1. `GET /api/bids?page_size=1&page=1` 2. `GET /api/bids?page_size=1&page=2` |
| **期待結果** | 1. Mỗi lần 1 item, `total` = tổng số hồ sơ 2. Page 1 ≠ page 2 (id khác nhau) |
| **備考** | 3-point rule (IPA) |

### TC-M2-024: Danh sách rỗng → thông báo

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-024 |
| **機能名** | Danh sách hồ sơ (FR-007) |
| **画面** | `/bids` |
| **観点** | 準正常系 (Semi-normal) |
| **テスト項目** | Không có hồ sơ → thông báo rỗng |
| **事前条件** | Tìm q không khớp hồ sơ nào |
| **テスト手順** | 1. Vào `/bids` 2. Tìm q = "zzzz-khong-ton-tai" |
| **期待結果** | 1. Hiển thị thông báo rỗng (không crash) |
| **備考** | — |

---

## F. Rerun + quy tắc AGENTS.md (qua API)

### TC-M2-025: Rerun không có bước failed → 422

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-025 |
| **機能名** | Rerun pipeline (FR-023) |
| **画面** | API `POST /api/bids/{id}/rerun` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Không có bước failed → từ chối |
| **事前条件** | Hồ sơ không có bước failed (draft hoặc done) |
| **テスト手順** | 1. `POST /rerun` body `{"from_step":null}` |
| **期待結果** | 1. `422 PIPELINE_ERROR` (không có bước failed) |
| **備考** | spec §2.1 |

### TC-M2-026: Rerun khi đang chạy → 409

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-026 |
| **機能名** | Rerun pipeline (FR-023) |
| **画面** | API `POST /api/bids/{id}/rerun` |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Race rerun lúc analyzing bị chặn |
| **事前条件** | Pipeline đang chạy |
| **テスト手順** | 1. Start pipeline 2. `POST /rerun` ngay |
| **期待結果** | 1. `409 STATE_CONFLICT` |
| **備考** | spec §7 rủi ro race |

### TC-M2-027: BR-06 — PII bị mask trước khi gửi LLM

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-027 |
| **機能名** | Quy tắc Privacy (BR-06, NFR-002) |
| **画面** | Backend test + API |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Email/SĐT trong nội dung yêu cầu không xuất hiện ở prompt LLM |
| **事前条件** | `LLM_PROVIDER=mock` |
| **テスト手順** | 1. Chạy `pytest -q tests/test_pii_mask.py` (≥ 50 mẫu, tỷ lệ ≥ 99%) 2. Chạy `pytest -q tests/test_bids.py::test_prompt_sent_to_llm_is_masked` |
| **期待結果** | 1. Cả 2 test exit 0 — prompt mock không chứa email/SĐT gốc |
| **備考** | spec §5(c) rule 6 |

### TC-M2-028: BR-01 — schema LLM không chứa số man-day/giá/ngày

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-028 |
| **機能名** | Quy tắc No invented numbers (BR-01) |
| **画面** | Backend test |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | `IntakeExtraction` + `GapQuestions` không có trường số/ngày |
| **事前条件** | — |
| **テスト手順** | 1. Chạy `pytest -q tests/test_llm_schema_no_numbers.py` |
| **期待結果** | 1. Exit 0 — không trường man-day/giá/ngày; ngân sách/thời hạn là ghi chú văn bản |
| **備考** | spec §5(c) rule 1 |

### TC-M2-029: BR-10 — frontend không hardcode localhost

| Field | Content |
|---|---|
| **TC-ID** | TC-M2-029 |
| **機能名** | Quy tắc Frontend networking (BR-10) |
| **画面** | Source + quality-gate |
| **観点** | 異常系 (Abnormal) |
| **テスト項目** | Không URL tuyệt đối trong `frontend/src` |
| **事前条件** | — |
| **テスト手順** | 1. Chạy `make quality-gate` (grep guard BR-10) |
| **期待結果** | 1. Exit 0 — "frontend/src không chứa URL tuyệt đối" OK |
| **備考** | spec §5(c) rule 10 |

---

**Task Acceptance Test complete. Awaiting prompt for the next role.**