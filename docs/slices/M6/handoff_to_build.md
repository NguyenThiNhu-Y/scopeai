# Handoff — Solution Architect → Build (M6 Đính kèm và ma trận đáp ứng)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev |
| Ngày | 2026-10-10 |
| Nguồn | `docs/slices/M6/spec.md`, `docs/04_architecture/`, `docs/05_roadmap/roadmap.md` §8, `docs/slices/M5/handoff_to_build.md`, `AGENTS.md` |

## 1. Deliverables bắt buộc

1. Bám nguyên văn các endpoint M6 trong `api_contract.md` §3.4–§3.7, §4.1–§4.2 và §7.1; không
   thêm endpoint ngoài contract.
2. Implement upload multipart với giới hạn 10 file/bid, 20 MB/file, detect loại, đổi loại và
   mapping sheet/cột; enforce giới hạn ở backend, không chỉ ở UI.
3. Implement parser code cho PDF/DOCX/TXT/MD/XLSX/XLSM/CSV/.xls; đọc toàn bộ sheet, nhận diện
   header/cột, hỗ trợ mapping tay, báo lỗi rõ và không sinh dữ liệu giả khi parse fail.
4. Implement requirement persistence với mã nội bộ duy nhất `REQ-xxx` trên toàn hồ sơ; formula
   `番号` không được dùng nguyên xi làm mã; giữ sheet/row/source columns để truy vết.
5. Implement sample profile và readiness suggestion bằng rule-based code; mask PII và giới hạn
   RFP summary trước mọi lời gọi LLM.
6. Implement B3 evaluation batch ≤40: schema `extra=forbid`, rating `◎|○|△|×`, nhãn `要確認`,
   note tiếng Việt, context toàn bộ mã, retry tối đa 2, warning thiếu/thừa/trùng.
7. Persist từng batch và cho phép resume; nối `要確認` với máy hỏi M2; giữ hướng giải pháp trên
   từng evaluation để phát hiện đánh giá theo hướng cũ.
8. Cập nhật mẫu giả lập đầy đủ (RFP + Excel hai sheet + sample data) và UI upload/review/confirm/
   matrix. FE chỉ render response, không tự parse/gán mã/tính hoàn tất.
9. Duy trì các bảo vệ M5: price gate, locked guard, quotation/approval không bị gọi lại hoặc
   ghi đè bởi M6.
10. Chạy toàn bộ acceptance commands trong `spec.md` §5.1 và click-through Preview trước khi
    chuyển Test/Review.

## 2. Contract không được phá vỡ

- `PUT /parse/confirm` là hàng rào bắt buộc: thiếu `confirmed=true` thì pipeline không chạy.
- Không có Excel requirement: `no_requirement_file=true`, UI ghi đúng thông báo và không hiển thị
  matrix; tuyệt đối không tự tạo requirement từ tóm tắt RFP.
- `GET /evaluations` phải phản ánh `total`, `evaluated`, `stats`, `warnings`; không giấu mã thiếu.
- Errors dùng envelope chuẩn và message tiếng Việt: `FILE_TOO_LARGE`, `TOO_MANY_FILES`,
  `INVALID_FILE_TYPE`, `PIPELINE_ERROR`, `STATE_CONFLICT`.
- Header `X-Role`/`X-User` là authoritative cho audit; body `by` không được dùng để giả mạo actor.
- Frontend gọi root-relative `/api`; không hardcode host/localhost.

## 3. Luật bắt buộc

- Parser, profile, mapping, mã requirement, count và uniqueness là code deterministic.
- LLM không sinh man-day, giá, ngày, tỉ giá hoặc mã requirement; LLM chỉ rating/note/clarification.
- Mọi LLM call qua gateway duy nhất; test/CI dùng `LLM_PROVIDER=mock`; retry bounded ≤2.
- Tài liệu gửi LLM là summary giới hạn ký tự và đã mask email/SĐT; không log API key.
- Fixture và sample đều fictional, ghi rõ “DỮ LIỆU GIẢ LẬP”.
- Không thêm queue/vector DB/auth server/dịch vụ đọc file ngoài stack đã chốt.

## 4. Test gate

```bash
cd backend && pytest -q tests/test_file_reader.py
cd backend && pytest -q tests/test_excel_multisheet.py
cd backend && pytest -q tests/test_internal_req_code.py
cd backend && pytest -q tests/test_data_profile.py
cd backend && pytest -q tests/test_evaluation_batches.py
cd backend && pytest -q tests/test_unique_req_codes.py
cd backend && LLM_PROVIDER=mock pytest -q tests/test_evaluation_retry.py
cd backend && pytest -q
cd frontend && npm run build
make test
make quality-gate
```

Fixture chính phải chứng minh: 235 dòng → ít nhất 6 batch, mỗi batch ≤40; hai sheet có namespace
mã duy nhất; formula `番号` sinh mã nội bộ; parse fail không tạo row; mock thiếu/trùng/thừa mã
retry tối đa 2 rồi warning; chưa confirm không chạy evaluation.

## 5. Preview evidence cần bàn giao

1. Nạp hồ sơ mẫu đầy đủ và thấy file giả lập.
2. Detect/đổi loại, upload thứ 11 bị từ chối nhưng 10 file trước còn nguyên.
3. Parse hai sheet, sửa mapping, thấy count và mã unique.
4. Thấy profile sample và readiness có thể chỉnh.
5. Chưa confirm bị chặn; confirm xong pipeline hiển thị progress batch ≤40.
6. Matrix hiển thị đủ rating, `要確認`, note và warning thiếu/thừa/trùng.
7. `要確認` đi qua câu hỏi M2 và đánh giá lại; đổi solution direction tạo cảnh báo hướng cũ.
8. Hồ sơ không có Excel hiển thị thông báo và ẩn matrix.
9. M5 price gate/quotation vẫn nguyên vẹn; M6 không sinh hoặc lộ số tiền.

## 6. Handover tiếp theo

Sau Build, chuyển Test/Review cùng test report, danh sách file, migration/model note, kết quả
commands, ảnh Preview và các warning còn mở. Bàn giao cho M7: requirements/evaluations đã persist,
`source_cols`, `batch_no`, `solution_direction`, trạng thái `needs_clarification` và warning
missing/extra codes. Không triển khai export trong bước M6.

**Task Slice Spec M6 complete. Awaiting prompt for the next role.**
