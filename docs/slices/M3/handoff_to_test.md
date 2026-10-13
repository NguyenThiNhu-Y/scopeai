# Handoff — Build → Test (M3 Hướng giải pháp + effort)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Backend Dev + Frontend Dev + Build Coordinator |
| Cho | Test/Review |
| Ngày | 2026-10-10 |
| Slice | M3 |

## Cách chạy

1. Cài dependencies theo `README.md`.
2. Chạy backend tests: `cd backend && pytest -q`.
3. Chạy frontend tests/type-check/build: `cd frontend && npm test`, `cd frontend && npm run type-check`, `cd frontend && npm run build`.
4. Chạy acceptance tổng: `make test`.
5. Chạy Preview: `make preview` hoặc nút Preview trong VibeFlow. Preview dùng `podman-compose.preview.vibeflow.yaml`, frontend production và proxy root-relative `/api`.

## Đã xây dựng

- B4 `SolutionProposal` qua LLM gateway duy nhất, mock fixtures, schema strict và retry tối đa 2 lần.
- Năm hướng cố định: `none`, `traditional_ml`, `rag`, `agent`, `fine_tune`; backend lưu lựa chọn và cảnh báo hướng đánh giá cũ.
- Bảng chuẩn giả lập version 4 tại `backend/app/reference/effort.yaml` và hệ số tại `backend/app/reference/factors.yaml`.
- `FactorEngine` áp trần một lần; `EffortEngine` tính range theo PoC/MVP/Production, midpoint và trace bằng code, không gọi LLM.
- API M3: `POST /api/bids/{id}/solution`, `GET /api/bids/{id}/effort`, `GET /api/bids/{id}/evaluations`.
- UI tiếng Việt có chọn hướng, effort breakdown, factor reasons, trace, loading/empty/error/success states; không tính lại số ở frontend.
- Verification trong bước Build: `make test` pass, gồm 67 backend tests, 4 frontend tests và frontend production build; frontend type-check/build cũng pass.
- Preview đã chạy với hai service `workspace_backend_1` và `workspace_frontend_1`; `GET /api/health` trả HTTP 200 với `llm_provider=mock`; `GET /api/bids/72/effort` trả HTTP 409 `STATE_CONFLICT` đúng khi chưa chọn hướng.

## Known gaps / điểm cần kiểm tra

- Contract frozen chưa có request field để presales bật/tắt factor thủ công. Implementation lấy factor từ context hồ sơ/reference; không tự mở rộng API. Nếu acceptance yêu cầu toggle thủ công, cần ADR và cập nhật contract trước.
- Cần chạy acceptance end-to-end trên giao diện, đặc biệt luồng tạo/nạp sample → M2 → M3; smoke API đã xác nhận proxy `/api`, health và state-conflict envelope.
- Cần xác nhận các số giả lập trong YAML đã được BA/PM phê duyệt trước khi dùng cho hồ sơ thật.
- B4 độc lập đã triển khai; orchestration vẫn bảo toàn hành vi M2 pending theo regression constraints hiện có, cần Test/Review xác nhận trạng thái pipeline M3 trong Preview.

## Kịch bản smoke test

1. Nạp sample tiếng Nhật hoặc tạo hồ sơ hợp lệ, chạy pipeline M2 và hoàn tất câu hỏi làm rõ.
2. Mở trang **Rà soát hướng giải pháp**; xác nhận chỉ có 5 hướng cố định.
3. Chọn `RAG`, nhập lý do tiếng Việt và lưu; xác nhận effort hiển thị đủ 3 phase.
4. Mở trace; xác nhận version bảng, source, từng factor/reason, raw/capped product và formula.
5. Đổi sang hướng khác; xác nhận effort đổi theo YAML và không có request LLM cho phép tính số.
6. Refresh trang; xác nhận lựa chọn và effort vẫn lấy được từ backend.

Task Build M3 complete. Awaiting Test/Review.
