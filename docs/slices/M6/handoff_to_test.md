# Handoff — Build → Test/Review (M6 Đính kèm và ma trận đáp ứng)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Build / Parallel Dispatch Coordinator |
| Cho | Test / Review |
| Ngày | 2026-10-10 |
| Phạm vi | Backend + frontend M6, tích hợp pipeline B3 |

## 1. Đã triển khai

- Backend đã có upload/list/update attachment với giới hạn 10 file/hồ sơ và 20 MB/file.
- Parser code hỗ trợ TXT/MD, PDF, DOCX, XLSX/XLSM, CSV và xử lý `.xls` với lỗi hướng dẫn chuyển đổi.
- Có detect loại file, mapping sheet/cột, profile dữ liệu mẫu, sinh mã `REQ-xxx`, lưu source sheet/row và persistence requirement/evaluation.
- B3 evaluation dùng gateway LLM duy nhất, schema `extra=forbid`, batch tối đa 40, retry bounded và cảnh báo mismatch mã.
- Pipeline đã gọi bước evaluate sau gap khi hồ sơ có requirement và chặn start/rerun nếu attachment chưa được parse confirm.
- Frontend đã có uploader, parse review, confirm gate, requirement matrix, loading/error/empty/success states và SSE pipeline progress.
- Frontend dùng API root-relative `/api/...`; Preview stack proxy `/api` tới backend và dùng mock LLM.

## 2. Các file chính

- Backend: `backend/app/api/routers/attachments.py`, `parse.py`, `evaluations.py`
- Backend: `backend/app/services/attachment_service.py`, `parse_service.py`, `evaluation_service.py`
- Backend: `backend/app/parsers/`
- Backend: `backend/app/pipeline/orchestrator.py`, `backend/app/pipeline/steps/b3_evaluate.py`
- Frontend: `frontend/src/api/client.ts`, `frontend/src/api/types.ts`
- Frontend: `frontend/src/components/AttachmentUploader.tsx`, `FileParseReview.tsx`, `RequirementMatrix.tsx`
- Frontend: `frontend/src/pages/BidDetailPage.tsx`
- Preview: `podman-compose.preview.vibeflow.yaml`, `frontend/vite.preview.config.ts`

## 3. Kết quả kiểm thử đã chạy

Lệnh acceptance theo tên file trong spec chưa thể chạy nguyên văn vì các file test legacy như `tests/test_file_reader.py` chưa tồn tại trong workspace. Lệnh đó trả lỗi `file or directory not found`.

Các gate thực tế đã pass từ workspace root:

```text
make test
  backend: 158 passed
  frontend: 6 passed
  frontend build: passed

make quality-gate
  backend: 158 passed
  frontend type-check + build: passed
  BR-10 root-relative URL scan: OK
  BR-06 credential pattern scan: OK
  QUALITY GATE PASSED
```

Test tích hợp M6 riêng đã pass:

```text
pytest -q tests/test_m6_pipeline_integration.py tests/test_pipeline_resume.py tests/test_pipeline_sse.py
18 passed
```

Lưu ý: chạy `pytest -q` từ riêng thư mục `backend/` không thu thập test trong cấu hình hiện tại; phải chạy từ root hoặc dùng đúng test path theo repo.

## 4. Preview evidence

- Preview compose đang chạy với `backend` và `frontend` ở trạng thái `Up`.
- `GET /api/health` trả `status=ok`, database `ok`, `llm_provider=mock`.
- Frontend production preview trả HTML hợp lệ qua cổng proxy.
- Chưa có browser click-through evidence đầy đủ cho toàn bộ kịch bản upload/parse/evaluate; Test/Review cần thực hiện phần này.

## 5. Known gaps cần Test/Review kiểm tra

- Chưa có đủ các fixture/test file-level được nêu trong M6 spec, gồm fixture 235 dòng, workbook hai sheet, formula `番号`, retry missing/duplicate/unknown và các tên test acceptance cụ thể.
- `GET /evaluations` hiện tổng hợp warnings rỗng từ persistence; cần kiểm tra warning mismatch sau retry có được lưu và hiển thị đúng hay chưa.
- Resume từng batch, nối `要確認` với máy hỏi M2 và đánh giá lại sau clarification chưa được chứng minh đầy đủ end-to-end.
- Đường export Excel giữ định dạng gốc nằm ngoài M6 theo spec và chưa triển khai.
- Cần xác minh UI không hiển thị matrix khi không có requirement Excel và không làm ảnh hưởng price gate/quotation M5.

## 6. Đề nghị kiểm thử tiếp theo

1. Chạy click-through Preview với hồ sơ mẫu, upload file thứ 11, file quá 20 MB, parse hai sheet và sửa mapping.
2. Xác minh confirm gate ở cả UI và API, sau đó theo dõi SSE batch progress với batch không quá 40 dòng.
3. Kiểm tra response/error envelope, `total/evaluated/stats/warnings`, missing/extra/duplicate codes.
4. Regression M5: price gate, quotation, approval và không sinh số tiền từ M6.
5. Ghi test report và danh sách warning trước khi chuyển review/đóng milestone.

**Task Build complete. Awaiting prompt for the next role.**
