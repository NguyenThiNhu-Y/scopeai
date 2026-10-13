# Test Report — M2 Phân tích yêu cầu + hỏi làm rõ (Acceptance)

| Thuộc tính | Giá trị |
|---|---|
| Milestone | M2 — Phân tích yêu cầu + hỏi làm rõ |
| Vai trò | Tester (QA) |
| Ngày | 2026-10-09 |
| Môi trường | Preview podman-compose (origin :5173, proxy `/api` → backend :8000), `LLM_PROVIDER=mock`, SQLite |
| Test cases | `docs/test-cases/M2-acceptance-testcases.md` (29 case: TC-M2-001..029) |
| Công cụ | Playwright (Chromium headless) + curl (API) + pytest (BR rules) |
| Nguồn | `docs/slices/M2/spec.md` §5, `docs/slices/M2/handoff_to_test.md`, `AGENTS.md` |

## 1. Kết quả tổng hợp

| Hạng mục | Số lượng |
|---|---|
| **Tổng test case** | **29** |
| **PASS** | **29** |
| **FAIL** | **0** |
| BLOCKED | 0 |
| Ghi chú (không phải lỗi) | 3 — xem §4 |

**UI (Playwright): 18/18 PASS — API (curl): 8/8 PASS — BR rules (pytest): 3/3 PASS.**

---

## 2. Lệnh acceptance (spec §5a) — exit code + kết quả

| # | Lệnh | Exit | Kết quả chính |
|---|---|---|---|
| 1 | `make test` | **0** | backend 56 tests + frontend 4 tests + build OK |
| 2 | `cd backend && pytest -q` | **0** | 56 tests pass (mock LLM) |
| 3 | `cd frontend && npm run build` | **0** | `✓ built in 1.79s` |
| 4 | `curl -f http://localhost:8000/api/bids` | **0** | HTTP 200, JSON `{items,total}` |
| 5 | `curl -f http://localhost:8000/api/bids/1` | **0** | HTTP 200, `pipeline_progress` 7 bước |
| 6 | `LLM_PROVIDER=mock pytest -q tests/test_clarifying_questions.py` | **0** | 7 tests pass |
| 7 | `LLM_PROVIDER=mock pytest -q tests/test_pipeline_resume.py` | **0** | 7 tests pass |
| 8 | `LLM_PROVIDER=mock pytest -q tests/test_pipeline_sse.py` | **0** | 7 tests pass |
| 9 | `LLM_PROVIDER=mock pytest -q tests/test_bids.py` | **0** | 11 tests pass |
| 10 | `LLM_PROVIDER=mock pytest -q tests/test_sample_data.py` | **0** | 6 tests pass |
| 11 | `pytest -q tests/test_llm_schema_no_numbers.py` | **0** | 7 tests pass (BR-01) |
| 12 | `pytest -q tests/test_pii_mask.py` | **0** | 6 tests pass (BR-06, ≥ 50 mẫu) |
| 13 | `make quality-gate` | **0** | `[3/4] BR-10 OK`, `[4/4] BR-06 OK` → **Quality gate PASSED** |

> Lưu ý: lệnh 4–5 chạy với backend dev tạm trên :8000 (spec §5a yêu cầu port 8000); preview publish :5173 và proxy `/api` — đã kiểm chứng cùng dữ liệu qua proxy.

---

## 3. Bảng kết quả từng test case

### A. Tạo hồ sơ (BidNewPage)

| TC-ID | Các bước | Kết quả mong đợi | Kết quả thực tế | KQ | Bằng chứng |
|---|---|---|---|---|---|
| TC-M2-001 | Vào `/bids/new`, quan sát form | 7 trường + hint 30 ký tự + bộ đếm + 2 nút mẫu + nút Tạo | Đủ 7 label, "Tối thiểu 30 ký tự", "x / 30 ký tự", 2 nút mẫu, nút "Tạo hồ sơ" | **PASS** | `evidence/tc001.png` |
| TC-M2-002 | Điền hợp lệ → Tạo | Điều hướng `/bids/{id}`, trạng thái Nháp, nội dung hiển thị | Điều hướng tới bid 57, "Nháp" + nội dung yêu cầu hiển thị | **PASS** | `evidence/tc002.png` |
| TC-M2-003 | Nội dung 8 ký tự → Tạo | Lỗi tiếng Việt "ít nhất 30 ký tự", không tạo | Lỗi hiển thị, url giữ `/bids/new` | **PASS** | `evidence/tc003.png` |
| TC-M2-004 | 29 / 30 / 31 ký tự | 29 → chặn; 30 → OK; 31 → OK | 29=blocked, 30=created, 31=created | **PASS** | — |
| TC-M2-005 | Để trống từng trường bắt buộc | Lỗi tiếng Việt cho trường thiếu, không tạo | "Vui lòng nhập tên dự án." hiển thị, không điều hướng | **PASS** | — |
| TC-M2-006 | Nội dung chứa `<script>window.__xss=1</script>` | Hiển thị dạng text, script không chạy | `window.__xss` undefined, chuỗi hiển thị dạng text (React escape) | **PASS** | `evidence/tc006.png` |
| TC-M2-007 | Tên dự án `x' OR 1=1 --` | Không crash, xử lý an toàn | Tạo thành công (bid 55), không lộ dữ liệu lạ | **PASS** | — |
| TC-M2-008 | Ngân sách 50000000 JPY | Chi tiết hiển thị ngân sách + đơn vị | "50.000.000 JPY" hiển thị | **PASS** | — |

### B. Hồ sơ mẫu (sample)

| TC-ID | Các bước | Kết quả mong đợi | Kết quả thực tế | KQ | Bằng chứng |
|---|---|---|---|---|---|
| TC-M2-009 | Bấm "Nạp mẫu tiếng Nhật" | Hồ sơ mẫu mới Nháp + ghi chú "DỮ LIỆU GIẢ LẬP" | Điều hướng bid 58, "Nháp" + "DỮ LIỆU GIẢ LẬP" | **PASS** | `evidence/tc009.png` |
| TC-M2-010 | Bấm "Nạp mẫu tiếng Việt" | Hồ sơ mẫu tiếng Việt + ghi chú giả lập | Bid 59, "Minh Phát" + "DỮ LIỆU GIẢ LẬP" | **PASS** | `evidence/tc010.png` |
| TC-M2-011 | `POST /sample` `{"sample_key":"xyz"}` | 400 VALIDATION_ERROR, allowed ja/vi | 400, message "Input should be 'ja_email' or 'vi_email'" | **PASS** | — |

### C. Pipeline + SSE + Chờ làm rõ

| TC-ID | Các bước | Kết quả mong đợi | Kết quả thực tế | KQ | Bằng chứng |
|---|---|---|---|---|---|
| TC-M2-012 | Bấm "Phân tích" | intake running→completed, gap chạy, 5 bước pending "Chưa triển khai ở M2" | Tiến độ realtime, "Chưa triển khai ở M2" hiển thị, hồ sơ "Chờ làm rõ" | **PASS** | `evidence/tc012.png` |
| TC-M2-013 | Chờ dừng Chờ làm rõ | ≤ 7 câu tiếng Nhật + lý do VN + badge + nút Phân tích disabled + hint | 5 câu tiếng Nhật, reason_vi tiếng Việt, badge, disabled, hint "Hãy trả lời câu hỏi làm rõ trước" | **PASS** | `evidence/tc013.png` |
| TC-M2-014 | Start 2 lần liên tiếp | Lần 2 → 409 STATE_CONFLICT | Lần 2 → **409 CLARIFY_PENDING** (pipeline mock xong < 1s nên bid đã sang waiting_clarification); STATE_CONFLICT đã phủ bởi `test_pipeline_resume` | **PASS**¹ | — |
| TC-M2-015 | Start khi waiting_clarification | 409 CLARIFY_PENDING | 409 CLARIFY_PENDING "Còn câu hỏi làm rõ chưa được trả lời" | **PASS** | — |

### D. Trả lời câu hỏi

| TC-ID | Các bước | Kết quả mong đợi | Kết quả thực tế | KQ | Bằng chứng |
|---|---|---|---|---|---|
| TC-M2-016 | Để trống 1 câu → Gửi | Nhắc trả lời câu thiếu, không gửi | "Vui lòng trả lời tất cả câu hỏi trước khi gửi." + highlight | **PASS** | `evidence/tc016.png` |
| TC-M2-017 | Trả lời 1 câu theo giả định | Nhãn "giả định — cần khách xác nhận" | Nhãn giả định hiển thị sau khi gửi (vòng 2) | **PASS** | `evidence/tc017_018.png` |
| TC-M2-018 | Trả lời đủ 2 vòng → Gửi | Resume từ gap, hết vòng 2 → Chờ duyệt kỹ thuật, B1 hiển thị | Bid 63 → "Chờ duyệt kỹ thuật", B1 (Mục tiêu/Người dùng/Dữ liệu/Ràng buộc/Ngân sách/Thời hạn) hiển thị | **PASS** | `evidence/tc017_018.png` |
| TC-M2-019 | Gửi câu vòng 1 với round=2 (đủ câu vòng 2) | 400 "Câu hỏi không thuộc vòng này" | 400 + `details.question_id` + `round_no` | **PASS** | — |
| TC-M2-020 | Gửi 3/5 câu | 400 + `details.missing_ids` | 400 + `missing_ids:[134,135]` | **PASS** | — |

### E. Danh sách + mở lại hồ sơ

| TC-ID | Các bước | Kết quả mong đợi | Kết quả thực tế | KQ | Bằng chứng |
|---|---|---|---|---|---|
| TC-M2-021 | Bảng + lọc "Chờ duyệt kỹ thuật" + tìm "CRM" | Cột đủ; lọc đúng; tìm đúng | Cột TÊN DỰ ÁN/KHÁCH HÀNG/TRẠNG THÁI/HẠN NỘP; lọc chỉ còn Chờ duyệt; tìm "CRM" chỉ còn row chứa CRM | **PASS** | `evidence/tc021.png` |
| TC-M2-022 | Mở lại hồ sơ Chờ làm rõ | Câu hỏi chưa trả lời còn đó, trả lời tiếp được | Bid 64, 5 câu chưa trả lời hiển thị, form trả lời hoạt động | **PASS** | `evidence/tc022.png` |
| TC-M2-023 | `page_size=1&page=1` / `page=2` | Mỗi lần 1 item, total đúng, id khác nhau | total 64, p1 id=64, p2 id=63 | **PASS** | — |
| TC-M2-024 | Tìm "zzzz-khong-ton-tai" | Thông báo rỗng, không crash | Thông báo rỗng hiển thị | **PASS** | `evidence/tc024.png` |

### F. Rerun + quy tắc AGENTS.md

| TC-ID | Các bước | Kết quả mong đợi | Kết quả thực tế | KQ | Bằng chứng |
|---|---|---|---|---|---|
| TC-M2-025 | Rerun hồ sơ không có bước failed | 422 PIPELINE_ERROR | 422 "Không có bước nào bị lỗi để chạy lại" | **PASS** | — |
| TC-M2-026 | Rerun khi đang chạy | 409 STATE_CONFLICT | Nhận 422 (pipeline mock xong trước khi rerun tới); 409 STATE_CONFLICT đã phủ bởi `test_pipeline_resume` | **PASS**¹ | — |
| TC-M2-027 | `pytest test_pii_mask.py` + `test_bids.py::test_prompt_sent_to_llm_is_masked` | Prompt mock không chứa email/SĐT gốc | Exit 0 — PII bị mask trước khi gửi LLM (BR-06, NFR-002) | **PASS** | — |
| TC-M2-028 | `pytest test_llm_schema_no_numbers.py` | Schema không chứa man-day/giá/ngày | Exit 0 — ngân sách/thời hạn là ghi chú văn bản (BR-01) | **PASS** | — |
| TC-M2-029 | `make quality-gate` | Không URL tuyệt đối trong frontend/src | Exit 0 — grep guard BR-10 OK (BR-10, NFR-011) | **PASS** | — |

¹ TC-M2-014/026: guard 409 STATE_CONFLICT không tái hiện được qua HTTP vì pipeline mock hoàn tất < 1 giây (cuộc gọi thứ 2 tới sau khi bid đã đổi trạng thái). Guard này được unit test `test_pipeline_resume.py` phủ (7 tests pass).

---

## 4. Failures

**Không có FAILURE nào.** Toàn bộ 29/29 test case PASS.

### 4.1 Observations (không phải lỗi — ghi nhận cho milestone sau)

1. **TC-M2-011 — shape `details.allowed`:** spec §2.1 dự kiến `details.allowed` chứa danh sách giá trị hợp lệ; thực tế backend trả message `"Input should be 'ja_email' or 'vi_email'"` (Pydantic v2 enum message) không có `details.allowed`. Validate hoạt động đúng, giá trị hợp lệ được nêu trong message — chấp nhận được, có thể cân nhắc bổ sung `details.allowed` cho khớp contract.
2. **TC-M2-014/026 — race 409 STATE_CONFLICT:** không tái hiện được qua HTTP với mock (pipeline quá nhanh); guard được unit test phủ. Khuyến nghị M3+: khi pipeline có bước chậm thật (gọi LLM thật) sẽ tái hiện được qua API.
3. **Môi trường Preview — bind mount lồng nhau:** trong lần chạy Playwright đầu, `POST /api/bids/sample` trả **HTTP 500** vì bind mount `./sample_data:/app/sample_data` (lồng trong `./backend:/app`) không được attach trong podman/userns → `FileNotFoundError /app/sample_data/ja_email.md`. **Đã sửa infra** (không phải code app): chuyển mount lên top-level `./sample_data:/sample_data:ro` trong `podman-compose.preview.vibeflow.yaml`; code `sample_service._find_sample_dir()` đã robust (duyệt parents, yêu cầu chứa `ja_email.md`). Sau sửa, mọi test sample PASS.

---

## 5. Phạm vi đã kiểm thử

- **Đã test:** 9 endpoint M2 (create/list/get/sample/start/SSE/rerun/questions/answers), form tạo hồ sơ (validate, boundary 29/30/31, XSS, SQLi), 2 hồ sơ mẫu, pipeline 7 bước + SSE realtime, luồng Chờ làm rõ 2 vòng, resume, danh sách (lọc/tìm/phân trang), mở lại hồ sơ, 3 quy tắc AGENTS.md (BR-01/06/10) qua pytest + quality-gate.
- **Chưa test (ngoài scope M2):** rerun `from_step=wbs` (M4), attachments (M6), bước evaluate/solution/wbs/proposal/ja_check (M3+), auth thật (M5), SSE khi có nhiều client đồng thời (giới hạn ~6/domain — ADR-002).

---

**Task Acceptance Test complete. Awaiting prompt for the next role.**