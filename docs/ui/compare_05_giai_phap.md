# QA Compare — Màn 5 Giải pháp

Ngày kiểm tra: 2026-10-11  
Môi trường: Preview qua `podman-compose.preview.vibeflow.yaml`, `LLM_PROVIDER=mock`, viewport mục tiêu `1440x900`  
Vai trò: QA tester, Đợt 2, Màn 5

## Kết luận

**CHANGES REQUIRED — chưa đạt acceptance runtime.**

Các suite backend liên quan đến M5, frontend build và frontend tests đều đạt. Tuy nhiên chưa thể xác nhận đầy đủ giao diện tab Giải pháp trên browser vì Chromium không có executable trong môi trường. Ngoài ra sample bid tiếng Nhật tạo được nhưng pipeline không thể bắt đầu, nên các dữ liệu solution/effort runtime không thể kiểm tra end-to-end.

Không tạo screenshot giả. Frontend-dev đã sửa accessibility trong `frontend/src/pages/BidDetailPage.tsx`; tester không sửa source trong lần kiểm tra runtime.

## Bằng chứng môi trường

| Hạng mục | Kết quả | Evidence / ghi chú |
|---|---|---|
| Preview frontend/backend | PASS | `podman-compose ... ps` cho thấy stack đang chạy |
| API health | PASS | HTTP `200`; `status=ok`, `database=ok`, `llm_provider=mock` |
| Sample bid tiếng Nhật | PASS | Tạo được sample bid; `customer_language=ja`, `display_currency=JPY` |
| Pipeline sample | BLOCKED | `POST /api/bids/{id}/pipeline/start` trả `409`; bid vẫn `draft`, steps vẫn `skipped` |
| Solution/effort/quotation runtime | BLOCKED | `/effort` và `/quotation` trả `409` do pipeline chưa chạy |
| Browser / Playwright | BLOCKED | Chromium executable/headless shell không khả dụng |
| Screenshot thật | Chưa có | Không tạo ảnh thay thế hoặc ảnh giả |

## Ma trận kiểm tra

| TC-ID | Kiểm tra | Expected result | Actual result | Kết quả | Mức độ | Đã sửa | Evidence / ghi chú |
|---|---|---|---|---|---|---|
| M5-QA-01 | Mở Preview và health/sample Nhật | UI render; health OK; sample trả bid id | Health và sample đạt; browser không chạy được | BLOCKED | CAO | Chưa xác nhận | API health/sample đạt; thiếu browser evidence |
| M5-QA-02 | Hướng giải pháp | Tên hướng, confidence, lý do, hướng bị loại, giả định | Không thể xác nhận runtime; API thiếu các field mở rộng | BLOCKED | CAO | Có một phần | `docs/ui/api_gaps.md`; pipeline sample bị 409 |
| M5-QA-03 | Khả thi và rủi ro | 3 thanh điểm, khuyến nghị, risk có màu/loại/mô tả/giảm thiểu | Frontend đã bổ sung semantics cho thanh điểm và nhãn accessible cho severity; không thể xác nhận runtime vì structured feasibility/risk metadata chưa có | BLOCKED | CAO | Có một phần | Không có browser screenshot/DOM; API gap |
| M5-QA-04 | Effort do code tính | Effort backend-owned, công thức và bảng hệ số hiển thị | Không thể xác nhận trên sample vì `/effort` trả 409 | BLOCKED | CAO | Có một phần | Component có bảng hệ số; runtime chưa kiểm tra được |
| M5-QA-05 | Nút rà soát | Nút `Rà soát hướng giải pháp` ở đầu thẻ hướng giải pháp | Chưa thể xác nhận bằng browser | BLOCKED | TB | Chưa xác nhận | Chromium không khởi động được |
| M5-QA-06 | Loading/rỗng/lỗi | Có trạng thái minh bạch, không bịa dữ liệu | Chưa thể xác nhận bằng browser; pipeline 409 là blocker runtime | BLOCKED | TB | Có một phần | Có state trong code; không có DOM/runtime screenshot |
| M5-QA-07 | Responsive mục tiêu 1440x900 | Không tràn chữ, bố cục đúng ảnh mẫu | Chưa chạy được viewport; không có thay đổi layout trong lần sửa này | BLOCKED | TB | Chưa xác nhận | Chromium executable thiếu |
| M5-QA-08 | Console/network | Không có lỗi frontend ngoài lỗi đã biết | Không thể thu console/network | BLOCKED | TB | Chưa xác nhận | Browser unavailable |

## Acceptance checks

| Check | Kết quả |
|---|---|
| Pricing suite (`tests/test_pricing.py`) | PASS |
| Mitsumorisho suite (`tests/test_pricing_mitsumorisho.py`) | PASS |
| Price gate (`tests/test_price_gate.py`) | PASS |
| Approval (`tests/test_approval.py`) | PASS |
| Pre-approval (`tests/test_pre_approval_checks.py`) | PASS |
| Snapshot immutability (`tests/test_immutability_snapshot.py`) | PASS |
| Proposal schema (`tests/test_proposal_schema.py`) | PASS |
| Proposal pipeline (`tests/test_proposal_pipeline.py`) | PASS |
| Full backend suite (`cd backend && pytest -q`) | PASS — 201 tests |
| Frontend build | PASS |
| Frontend test | PASS — 1 file, 6 tests |
| `make test` | BLOCKED — `make` không khả dụng trong môi trường |
| `make quality-gate` | BLOCKED — `make` không khả dụng trong môi trường |

## Mapping với test case acceptance

Các test case `TC-M5-001` đến `TC-M5-012` là acceptance shell checks của milestone Proposal/báo giá/phê duyệt; chúng không thay thế kiểm tra visual của tab Giải pháp. Kết quả thực tế được ghi lại như sau:

| Test case | Kết quả |
|---|---|
| `TC-M5-001` đến `TC-M5-008` | PASS — các suite pricing, Mitsumorisho, price gate, approval, pre-approval, snapshot, proposal schema và proposal pipeline |
| `TC-M5-009` | PASS — full backend, 201 tests |
| `TC-M5-010` | PASS — frontend build |
| `TC-M5-011` | BLOCKED — `make` không khả dụng |
| `TC-M5-012` | BLOCKED — `make` không khả dụng |
| `TC-M5-013` | BLOCKED một phần — health/sample API đạt, browser UI không chạy |
| `TC-M5-014` | BLOCKED — sample pipeline chưa chạy, quotation trả 409 |
| `TC-M5-015` đến `TC-M5-019` | Không thuộc phạm vi xác nhận visual Màn 5 trong lần chạy này; các backend proposal/approval suite liên quan đã PASS ở phần acceptance checks |

## Đối chiếu yêu cầu Màn 5

| Yêu cầu gốc | Kết luận QA |
|---|---|
| Hướng giải pháp có confidence, lý do, hướng bị loại và giả định | BLOCKED; contract backend chưa trả đầy đủ field |
| Khả thi gồm 3 điểm, thanh điểm và khuyến nghị | BLOCKED; không có structured feasibility runtime |
| Risk gồm severity màu, type, mô tả và mitigation | BLOCKED; không có structured risk metadata runtime |
| Effort do code tính, bảng hệ số và công thức | BLOCKED runtime vì pipeline/effort trả 409; không đánh dấu PASS từ code review |
| Nút `Rà soát hướng giải pháp` | BLOCKED vì browser không khả dụng |
| Loading/rỗng/lỗi và không bịa dữ liệu | BLOCKED vì thiếu DOM evidence; không phát hiện bằng chứng trái với nguyên tắc |
| Preview Nhật, mock LLM, 1440x900 | BLOCKED một phần: Preview/mock đạt, browser/viewport không chạy |

## API gaps và blocker cần xử lý

- `confidence` chưa có trong response solution.
- `rejected_directions` và lý do chưa có.
- `assumptions` chưa có.
- `feasibility` dạng cấu trúc gồm 3 điểm và recommendation chưa có.
- `risk` dạng cấu trúc gồm severity, type, description và mitigation chưa có.
- Sample pipeline start trả `409`, khiến solution/effort/quotation không thể kiểm tra end-to-end.
- Cần môi trường có Chromium executable để tester chạy lại DOM, screenshot, viewport và console/network.

## Ảnh và giới hạn

- Không có ảnh mẫu được tạo hoặc sao chép trong bước QA.
- Không có ảnh “sau” vì browser không khởi động được.
- Không được kết luận PASS visual dựa trên static code hoặc API health.
- Không sửa `backend/`; frontend-dev có sửa accessibility trong `frontend/src/pages/BidDetailPage.tsx`, tester không sửa source.

## Completeness audit

- Đã kiểm tra lại toàn bộ yêu cầu Màn 5 trong `docs/ui/review_ui_tung_man.md`.
- Đã sửa bảng ma trận để header, số cột và các dòng dữ liệu nhất quán.
- Đã bổ sung cột `Đã sửa` và mapping với `TC-M5-001` đến `TC-M5-019` để phân biệt acceptance shell checks với visual QA.
- Frontend-dev đã bổ sung semantics `progressbar` cho điểm khả thi, không tô thanh khi thiếu điểm, và nhãn accessible cho severity risk; thay đổi này chưa thay thế browser evidence.
- Kết luận vẫn là `CHANGES REQUIRED`; không có bằng chứng mới đủ để chuyển sang PASS.
