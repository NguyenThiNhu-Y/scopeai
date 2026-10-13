# Handoff — Solution Architect → Build (M3 Hướng giải pháp + effort)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev, Cloud/Infra (bước tiếp theo) |
| Ngày | 2026-10-10 |
| Nguồn | `docs/slices/M3/spec.md`, `docs/04_architecture/` (4 file), `docs/05_roadmap/roadmap.md` §5, `docs/slices/M2/spec.md`, `AGENTS.md` |

## 1. Deliverables bắt buộc

1. Tạo bảng chuẩn `effort.yaml` và `factors.yaml` với số **giả lập đã được BA/PM phê duyệt**, đủ 5 hướng × 3 phase và các hệ số M3; có version/cap.
2. Tạo `SolutionProposal` schema và fixture mock qua gateway duy nhất; schema không có man-day/effort/giá/ngày hay số tính toán.
3. Tạo `FactorEngine` và `EffortEngine` thuần code, deterministic, unit-test được; cap chỉ áp dụng tại một nơi.
4. Tạo service/model/router cho `POST /api/bids/{id}/solution` và `GET /api/bids/{id}/effort`; giữ đúng contract frozen.
5. Kích hoạt B4 trong pipeline sau M2; đổi hướng phải tính lại bằng code, không gọi LLM; evaluations cũ phải có warning stale direction.
6. Tạo UI chọn hướng + effort breakdown + trace panel; FE chỉ render số từ API và gọi `/api/...` root-relative.
7. Chạy toàn bộ acceptance commands trong `spec.md` §5, kiểm tra Preview và ghi test evidence.

## 2. Luật không được vi phạm

- Không tự phát minh số liệu nghiệp vụ. Nếu YAML chưa được phê duyệt, dừng ở fixture/schema/engine contract và báo blocker.
- Không để LLM sinh hoặc sửa số effort. B4 chỉ trả hướng, lý do, rủi ro, ghi chú kiến trúc.
- Không gọi LLM trong `EffortEngine`, `FactorEngine`, endpoint effort hoặc thao tác đổi hướng.
- Mọi output LLM qua `LLMClient.complete_with_retry`, retry tối đa 2, test/CI dùng `LLM_PROVIDER=mock`.
- Không tính lại số ở frontend; không hardcode `http://localhost` trong `frontend/src`.
- Không triển khai WBS/schedule/quotation/approval/export của milestone sau.

## 3. Contract cần khóa trong implementation

- `direction`: `none | traditional_ml | rag | agent | fine_tune`.
- `POST /api/bids/{id}/solution` response có `direction`, `effort_recalculated`, `warnings`.
- `GET /api/bids/{id}/effort` trả `factors`, `factor_product`, `cap`, `by_phase`, `midpoint_total`, `trace` theo `api_contract.md` §8.0.
- Error envelope chuẩn; chưa chọn hướng → `409 STATE_CONFLICT`; hồ sơ không tồn tại → `404 NOT_FOUND`.
- Hướng hiển thị/giải thích bằng tiếng Việt; số liệu hiển thị phải có trace.
- Contract hiện chưa có request field cho việc bật/tắt factor. Không tự thêm `factors` vào `POST /solution`; dùng context hồ sơ/reference để tính. Nếu acceptance bắt buộc toggle thủ công, dừng và tạo ADR sửa `api_contract.md` trước khi implementation.

## 4. Test gate

```bash
cd backend && pytest -q tests/test_effort.py
cd backend && pytest -q tests/test_factors.py
cd backend && pytest -q tests/test_solution_direction.py
cd backend && pytest -q tests/test_trace.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_llm_schema_no_numbers.py
make test
cd backend && pytest -q
cd frontend && npm run build
make quality-gate
```

Preview phải chứng minh: đề xuất thuộc tập 5 hướng; effort theo 3 phase; hệ số có reason và cap; trace mở được; đổi hướng tính lại không gọi LLM; refresh vẫn giữ dữ liệu.

## 5. Handoff tiếp theo

Sau khi build/test M3 hoàn tất, ghi test report và chuyển cho role Test/Review. Nêu rõ version YAML đã dùng, các số giả lập đã được ai phê duyệt, mọi test còn thiếu và blocker để M4 dùng effort range làm đầu vào WBS. Không bắt đầu triển khai M4 trong bước này.

**Task Slice Spec M3 complete. Awaiting prompt for the next role.**
