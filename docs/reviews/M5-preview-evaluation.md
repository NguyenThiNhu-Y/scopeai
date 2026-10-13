# Đánh giá Preview M5 — hồ sơ mẫu CRM Nhật

| Thuộc tính | Kết quả |
|---|---|
| Ngày đánh giá | 2026-10-10 |
| Hồ sơ | `#81` — CRM, dữ liệu giả lập, khách hàng Nhật |
| Môi trường | Preview production mode, `LLM_PROVIDER=mock` |
| Phạm vi | Pipeline hỏi đáp, WBS, lịch, báo giá, proposal và cổng duyệt |
| Cách kiểm tra | Gọi API qua Preview proxy; đối chiếu spec M5 và AGENTS.md |

## 1. Cách chạy hồ sơ mẫu

- Preview chạy thành công với backend/frontend đều `Up`; health trả `200`, database `ok`, `llm_provider=mock`.
- Tạo hồ sơ mẫu bằng `POST /api/bids/sample`, nhận hồ sơ `#81`, ngôn ngữ khách `ja`, trạng thái ban đầu `draft`.
- Pipeline được khởi chạy bằng `POST /api/bids/81/pipeline/start` và dừng đúng ở `waiting_clarification` sau vòng hỏi đầu tiên.
- Hồ sơ tạo 5 câu hỏi tiếng Nhật. Gửi đủ câu trả lời giả lập ở vòng 1, pipeline tạo tiếp 5 câu hỏi tương tự ở vòng 2; gửi tiếp vòng 2 thì pipeline chạy đến `waiting_tech_approval`.
- Không có real LLM call; Preview dùng mock theo cấu hình. Không ghi lại hoặc lặp lại dữ liệu liên hệ trong hồ sơ mẫu ở báo cáo này.

## 2. Đánh giá WBS

### Kết quả quan sát

- `GET /api/bids/81/wbs` trả `200`.
- WBS có 3 cấp, 3 phase `poc/mvp/production`, tổng effort `57.6` man-day.
- Phân bổ phase: PoC `12.0`, MVP `30.0`, Production `15.6`.
- Check backend trả:
  - `deviation_pct=0.0`, `within_20pct=true`;
  - `pm_qa_ok=true`;
  - `cycle_free=true`;
  - `leaf_max_man_day=6.0`, `leaf_within_limit=true`.
- Trace cho biết hướng `rag`, factor khách Nhật `1.2`, range `45.6–69.6`; số effort xuất hiện ở response do code tính, không phải output có quyền ghi số của LLM.

### Đánh giá

**Đạt về cấu trúc và kiểm tra M4/M5 đầu vào.** WBS đủ 3 cấp, có PM/QA, task lá dưới giới hạn và dependency không vòng. Tuy nhiên WBS mock vẫn ở mức khung; chưa chứng minh trace requirement → task cho hồ sơ CRM. Do M6 chưa có ma trận requirement đầy đủ, mục này phải được ghi là deferred, không coi là coverage đầy đủ.

## 3. Đánh giá lịch

### Kết quả quan sát

- `GET /api/bids/81/schedule` ban đầu trả `409` vì schedule chưa được persist; đây là state guard phù hợp khi pipeline chưa có lịch.
- Gửi `PUT /api/bids/81/schedule` với lịch Nhật, start date `2026-10-12` và team allocation giả lập, API trả `200`.
- Backend tính end date `2026-12-31`, áp dụng lịch Nhật và ngày nghỉ `2026-11-03`.
- Các mốc thanh toán mặc định là `20/20/30/30`; mốc cuối có due date `2027-01-10`.
- Bid có submission deadline `2026-12-15`; response đặt `deadline_violation=true` và cảnh báo cần tăng người hoặc giảm phạm vi.

### Đánh giá

**Đạt về tính minh bạch của phép tính, nhưng hồ sơ mẫu chưa khả thi về deadline.** App không che giấu vi phạm hạn nộp, đây là hành vi đúng với rule “ask instead of guess”. Tuy nhiên proposal/customer-facing không nên được coi là sẵn sàng khi lịch vẫn trễ deadline. Presales cần điều chỉnh headcount/phạm vi và tính lại trước khi duyệt kỹ thuật/giá.

## 4. Đánh giá báo giá

### Kết quả quan sát

- `GET /api/bids/81/quotation` trả `200` sau khi WBS có dữ liệu.
- API trả by-role, PM overhead, contingency `20%`, tax mode `tax_excluded`, trace và reference snapshot.
- Tổng hiện trả `grand_total=187572000`, nhưng currency/FX trả `VND/VND` với `fx_rate.value=1.0`, dù hồ sơ là khách Nhật.
- `budget=null` vì sample không có ngân sách số; vì vậy không có chênh lệch ngân sách để đánh giá.
- Việc gọi quotation trước khi WBS/schedule đầy đủ trả `409 STATE_CONFLICT`, phù hợp state guard.

### Findings

#### HIGH — Báo giá khách Nhật vẫn là VND/VND, không chứng minh JPY/FX/rounding

- **Bằng chứng runtime:** `GET /api/bids/81/quotation` trả `fx_rate.pair="VND/VND"`, `value=1.0`; bid có `customer_language="ja"` và UI contract yêu cầu chọn JPY cho khách Nhật.
- **Đối chiếu code:** `backend/app/services/quotation_engine.py:17-20, 27-30` luôn chọn rate offshore và dùng FX 1.0; `backend/app/services/quotation_engine.py:38` trả pair hard-code `VND/VND`.
- **Tác động:** Không đạt M5 §5.2.2 về tiền tệ JPY, BrSE overhead, FX ngày hiệu lực và rounding yen; số tổng hiện tại không thể dùng làm báo giá Nhật.
- **Cách sửa:** Chọn currency/onsite-offshore từ bid hoặc approval input, snapshot đúng FX pair/date và rounding theo currency; thêm Preview fixture Nhật có JPY để kiểm tra end-to-end.

#### HIGH — Không có budget comparison trong hồ sơ mẫu

- **Bằng chứng runtime:** bid sample có `budget_amount=null`, quotation trả `budget=null`.
- **Tác động:** Case “có ngân sách khách” chưa được đánh giá; chưa chứng minh `difference` chỉ xuất hiện khi có ngân sách và được quy đổi cùng FX snapshot.
- **Cách sửa:** Thêm một sample/fixture M5 có ngân sách JPY giả lập và một sample không có ngân sách; ghi expected difference và kiểm tra response/UI.

## 5. Đánh giá proposal và price gate

### Trước duyệt giá

- `GET /api/bids/81/proposal` trả `200`, `price_gate="placeholder"`, sections có nội dung, assumptions và scope-out.
- Không có số tiền trong proposal draft trước duyệt; price-gate notice hiển thị `[Presales điền]`.
- Proposal có thể sửa qua API mà không gọi LLM; đây là hành vi phù hợp contract.

### Sau duyệt kỹ thuật và duyệt giá

- Technical approval với `X-Role: ai_developer` trả `200`, chuyển sang `waiting_price_approval`.
- Price approval với `X-Role: manager` trả `200`, chuyển `price_approved`, `locked=true`, và checks report gồm cảnh báo `no_missing_requirement` deferred to M6.
- **Bất thường quan sát được:** sau approval, proposal chỉ đổi `price_gate` thành `approved`; sections vẫn là văn bản tiếng Việt và không có bảng giá/số liệu chính thức. `GET /api/bids/81/quotation` mới chứa tổng tiền.

#### HIGH — Proposal không theo ngôn ngữ khách Nhật và không chèn bảng giá sau approval

- **Bằng chứng runtime:** bid `#81` có `customer_language=ja`, nhưng proposal sections sau B6 là tiếng Việt (ví dụ introduction/solution/approach đều là văn bản tiếng Việt). Sau price approval, proposal vẫn không có bảng quotation; chỉ trả `price_gate="approved"`.
- **Đối chiếu code:** `backend/app/pipeline/steps/b6_proposal.py:15-17` chỉ đưa customer language vào prompt/context tối thiểu; `backend/app/services/proposal_service.py:17-18` chỉ trả cờ gate; `frontend/src/pages/ProposalPage.tsx:17` chỉ render textarea và notice.
- **Tác động:** Vi phạm M5 §3.2, §5.2.2, §5.2.7 và rule ngôn ngữ. `price_gate=approved` tạo cảm giác proposal đã sẵn sàng nhưng customer-facing document chưa có giá được code render.
- **Cách sửa:** Bảo đảm mock fixtures/LLM output theo `vi/en/ja` và validate language; backend renderer phải ghép bảng giá từ approved quotation snapshot sau gate, còn trước gate chỉ render placeholder. Thêm test API trước/sau approval và test tiếng Nhật trên fixture mẫu.

## 6. Đánh giá pre-approval checks và lock

- Technical approval đúng role chuyển trạng thái; price approval creator không được tự duyệt theo service contract.
- Price approval trả checks report có warning M6 thay vì giả pass requirement matrix; điểm này phù hợp với spec.
- Tuy nhiên checks runtime chỉ thể hiện `schema_valid`, `effort_within_20pct`, `pm_qa_present` và warning M6; cần regression test bằng WBS lệch effort/thiếu PM/QA/cycle để chứng minh fail thực sự chặn approval, không chỉ pass với sample tốt.
- Sau `price_approved`, bid trả `locked=true`; cần kiểm tra tiếp các PUT WBS/schedule sau lock và unlock manager trong một phiên acceptance riêng để xác nhận toàn bộ mutation guard.

## 7. Đối chiếu AGENTS.md

| Rule | Kết quả Preview |
|---|---|
| 1 — No invented numbers | WBS/lịch/báo giá có trace code-side; nhưng currency/FX runtime không đúng contract Nhật. |
| 2 — Structured LLM | Pipeline chạy mock; B6 output có schema, nhưng ngôn ngữ output không khớp hồ sơ. |
| 3 — One gateway | Không có bằng chứng Preview gọi real LLM; health xác nhận mock. |
| 4 — Ask instead of guess | Pipeline dừng hỏi thiếu dữ liệu; lịch vi phạm deadline được cảnh báo thay vì che giấu. |
| 5 — Price gate | Trước approval placeholder hoạt động; sau approval thiếu renderer bảng giá trong proposal. |
| 6 — Privacy | Sample được đánh dấu giả lập; không lặp PII trong báo cáo. Test mask có trong suite, nhưng Preview chưa cung cấp log/prompt để kiểm chứng trực tiếp. |
| 7 — Languages | Câu hỏi Nhật đúng; proposal sau B6 lại là tiếng Việt — không đạt. |
| 8 — Done means proven | Preview chạy được đến approval; các case JPY/budget/proposal renderer chưa proven. |
| 9 — Keep simple | Không quan sát thêm hạ tầng nặng trong Preview. |
| 10 — Root-relative API | API qua `/api` và proxy Preview hoạt động. |

## 8. Tổng kết

| Hạng mục | Đánh giá | Ghi chú |
|---|---|---|
| Pipeline hỏi đáp | **Đạt một phần** | Dừng đúng khi thiếu dữ liệu; vòng 2 lặp lại câu hỏi, cần xem lại UX/strategy. |
| WBS | **Đạt cấu trúc** | 3 cấp, 57.6 MD, checks tốt trên sample; requirement trace deferred M6. |
| Lịch | **Đạt chức năng, chưa đạt deadline** | Tính đúng ngày nghỉ/mốc và cảnh báo trễ deadline. |
| Báo giá | **Chưa đạt customer-ready** | Có totals/trace nhưng sai currency/FX cho khách Nhật và chưa test budget comparison. |
| Proposal | **CHƯA ĐẠT** | Sai ngôn ngữ khách Nhật; sau approval chưa chèn bảng giá code-side. |
| Approval/lock | **Đạt một phần** | Transition/lock/check warning hoạt động; cần negative checks và mutation guard đầy đủ. |

## Verdict

**CHANGES REQUIRED**

Top findings:

1. **HIGH:** Báo giá hồ sơ Nhật trả `VND/VND`, FX `1.0`, không chứng minh JPY/rounding/BrSE overhead.
2. **HIGH:** Proposal không theo ngôn ngữ `ja` và sau approval không có bảng giá được code render.
3. **HIGH:** Chưa có Preview evidence cho budget comparison; hồ sơ mẫu không có budget.
4. **MEDIUM:** Lịch mẫu kết thúc sau deadline; cần điều chỉnh trước khi coi hồ sơ ready.

Developer cần xử lý các finding HIGH, bổ sung fixture/test Preview tương ứng và chạy lại workflow review cho M5. Không nên tuyên bố M5 customer-ready trước khi proposal tiếng Nhật, price renderer sau approval, JPY/FX và budget comparison được chứng minh.

## Handoff Note

Đã hoàn tất đánh giá Preview M5 trên hồ sơ mẫu `#81`; không sửa code ứng dụng. Báo cáo được ghi tại `docs/reviews/M5-preview-evaluation.md`. Handoff cho Developer: sửa các finding HIGH, bổ sung kiểm thử/fixture cho JPY, budget, language và proposal sau price approval; sau đó chạy lại Preview acceptance.

**Task Review complete. Awaiting prompt for the next role.**
