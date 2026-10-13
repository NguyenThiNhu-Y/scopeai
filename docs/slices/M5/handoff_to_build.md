# Handoff — Solution Architect → Build (M5 Proposal + báo giá + cổng duyệt)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev |
| Ngày | 2026-10-10 |
| Nguồn | `docs/slices/M5/spec.md`, `docs/04_architecture/` (đã reconcile), `docs/05_roadmap/roadmap.md` §7, `docs/slices/M4/spec.md`, `AGENTS.md` |

## 1. Deliverables bắt buộc

1. Tạo `rate_card.yaml` với số **giả lập có version**, đơn giá theo role/offshore/onsite, overhead,
   FX có ngày hiệu lực, tax/rounding, contingency theo contract và operating cost.
2. Tạo quotation engine thuần code, model/schema/router `GET /quotation`; tất cả totals, trace và snapshot
   phải truy ngược được về effective reference YAML.
3. Tạo B6 proposal schema/prompt/step và mock fixtures vi/en/ja; validate JSON, cấm tiền/man-day/ngày,
   retry tối đa 2; persist `proposal_drafts`.
4. Tạo `GET/PUT /proposal` để presales sửa văn bản trên web; không cho client ghi số liệu, giả định hoặc price gate.
5. Tạo pre-approval checks, tech approval, price approval, reject, unlock, audit và lock guard ở service layer.
6. Khi approve giá: snapshot quotation/reference, `price_approved`, `locked=true`; khi chưa approve hoặc reject:
   proposal phải dùng `[Presales điền]` và không lộ số tiền.
7. Cập nhật orchestrator để chạy B6 sau WBS; không làm B6 gọi trực tiếp ngoài LLM gateway.
8. Tạo UI quotation/proposal/approval với API root-relative `/api`; FE chỉ render, không tính giá/lịch.
9. Chạy đúng các acceptance commands trong `spec.md` §5 và smoke test Preview trước khi bàn giao Test/Review.

## 2. Contract phải khóa

- Bám `docs/04_architecture/api_contract.md` §8.5, §9.1–§9.3 và §10.0.
- Header `X-Role`/`X-User` là authoritative; không tin `by` trong body cho audit/authorization.
- `GET/PUT /proposal` chỉ nhận/ trả sections; assumptions/scope-out do server giữ; số liệu do code renderer.
- `GET /quotation` phải có totals, budget/difference tùy chọn, FX/date, valid_until, tax mode và trace.
- `POST /approvals/price` phải chặn người tạo, chạy checks trước, reject cần lý do, approve thì lock.
- `POST /unlock` chỉ manager, cần reason; mọi thay đổi sau unlock phải quay lại price approval.
- Error envelope chuẩn; thông báo tiếng Việt; không thêm endpoint ngoài contract khi chưa cập nhật contract/ADR.

## 3. Luật không được vi phạm

- Không để LLM sinh tiền, man-day, ngày, tỉ giá, thuế, dự phòng; không dùng output LLM làm nguồn số.
- Không gọi LLM trong quotation engine, check engine, approval, lock/unlock hay PUT proposal.
- Test/CI luôn `LLM_PROVIDER=mock`; không in/commit API key; dữ liệu mẫu hư cấu.
- Trước duyệt: không có số tiền dưới bất kỳ dạng currency + digits nào; dùng đúng `[Presales điền]`.
- Không tin client để bypass locked, tự duyệt hoặc tự gán approver khác.
- Không triển khai export Word/PDF/Excel, file attachment/matrix đầy đủ, settings YAML runtime trong M5.
- Không hardcode host/localhost trong frontend; không thêm hạ tầng nặng.

## 4. Test gate

```bash
cd backend && pytest -q tests/test_pricing.py
cd backend && pytest -q tests/test_pricing_mitsumorisho.py
cd backend && pytest -q tests/test_price_gate.py
cd backend && pytest -q tests/test_approval.py
cd backend && pytest -q tests/test_pre_approval_checks.py
cd backend && pytest -q tests/test_immutability_snapshot.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_schema.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_proposal_pipeline.py
cd backend && pytest -q
cd frontend && npm run build
make test
make quality-gate
```

Preview phải chứng minh: quotation trace; JPY/見積書; ngân sách có/không; proposal vi/en/ja có Giả định/Rủi ro;
chưa duyệt không có số tiền; sửa draft được; tech approval trước price approval; tự duyệt bị chặn; reject cần
lý do; approve khóa và snapshot; unlock cần manager/reason và duyệt lại.

## 5. Bàn giao tiếp theo

Sau Build, ghi test report và chuyển Test/Review. Nêu rõ version rate card, người phê duyệt số giả lập, kết quả
từng command, Preview evidence và blocker. Bàn giao cho M6 trạng thái kiểm tra requirement bị deferred; bàn giao
cho M7 proposal draft, quotation snapshot, price gate và dữ liệu cần cho exporters. Không bắt đầu M6/M7 trong bước này.

**Task Slice Spec M5 complete. Awaiting prompt for the next role.**
