# Handoff — Build → Test (M5)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Backend Dev + Frontend Dev + Main coordinator |
| Cho | Test/Review |
| Ngày | 2026-10-10 |
| Slice | M5 Proposal + báo giá + cổng duyệt |

## Đã triển khai

- Backend có quotation engine đọc `backend/app/reference/rate_card.yaml`, snapshot reference, totals theo role, overhead, contingency, tax, rounding và trace.
- Backend có B6 proposal schema/gateway mock, proposal draft GET/PUT, approval tech/price, checks, lock và manager unlock.
- Frontend có màn hình Báo giá, Proposal editor và Cổng duyệt; API dùng `/api/...`, không hardcode host.
- Danh tính duyệt được gửi qua `X-Role`/`X-User`; backend chặn sai vai trò: `ai_developer` cho tech, `manager` cho price/unlock.
- Price gate trả `placeholder` trước khi duyệt giá; sections proposal không nhận số tiền/man-day từ client.

## Cách chạy

```bash
make test
make quality-gate
make preview
```

Preview dùng `podman-compose.preview.vibeflow.yaml`, frontend proxy `/api` tới backend và `LLM_PROVIDER=mock`.
Không dùng LLM thật trong test/CI.

## Kiểm tra cần thực hiện

1. Nạp hồ sơ mẫu, chạy pipeline tới WBS/schedule, mở Báo giá và kiểm tra trace/rate card.
2. Mở Proposal, xác nhận có Giả định/Rủi ro, trước duyệt có `[Presales điền]` và không lộ tiền.
3. Duyệt kỹ thuật bằng `X-Role: ai_developer`, sau đó duyệt giá bằng `X-Role: manager`.
4. Xác nhận tự duyệt, sai vai trò, reject thiếu lý do và check fail đều bị chặn bằng error envelope tiếng Việt.
5. Sau price approval xác nhận `price_approved`, `locked=true`, snapshot; unlock chỉ nhận manager có reason.
6. Sửa proposal section, tải lại và xác nhận nội dung được giữ.

## Known gaps

- Bộ test acceptance riêng được nêu trong `spec.md` (`test_pricing.py`, `test_approval.py`, `test_proposal_pipeline.py`, ...) chưa được tạo đầy đủ; test cần bổ sung hoặc đánh dấu gap rõ ràng.
- Quotation hiện đang dùng offshore và FX mặc định VND/VND; cần kiểm tra/hoàn thiện các biến thể onsite và quy đổi budget JPY/USD theo fixture M5.
- Cần xác minh end-to-end thực tế trên Preview, đặc biệt dữ liệu M4 đủ WBS/schedule và việc render số sau price approval.

## Verification result

- `cd backend && pytest -q`: PASS, 139 tests.
- `make quality-gate`: PASS, gồm backend tests, frontend build, BR-10 và BR-06 guards.
- `cd frontend && npm run type-check`: PASS.
- `cd frontend && npm run build`: PASS.
- Preview compose: cả `backend` và `frontend` ở trạng thái Up.
- Preview health: `200 OK`, database `ok`, `llm_provider=mock`.
- Preview route smoke đã xác nhận frontend được phục vụ và `/api/health` đi qua proxy; chưa hoàn tất thao tác UI đầy đủ qua browser cho toàn bộ luồng approval.

## Contract reconciliation

- Endpoint paths khớp `docs/slices/M5/spec.md` và `docs/04_architecture/api_contract.md`.
- Body `by` vẫn tồn tại để tương thích contract nhưng authorization/audit lấy từ headers.
- Không thêm endpoint ngoài frozen contract.

**M5 Build complete. Awaiting Test/Review.**
