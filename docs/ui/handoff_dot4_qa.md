# Handoff — QA Đợt 4 backend, mock và dữ liệu mẫu

Ngày: 2026-10-11  
Vai trò: tester/QA

## Trạng thái

**CHANGES REQUIRED**

## Deliverables

- Báo cáo kiểm tra runtime và pytest: `docs/ui/dot4_check.md`.
- Báo cáo review acceptance: `docs/ui/dot4_review.md`.

## Verification thật

- `podman-compose -f podman-compose.preview.vibeflow.yaml exec -T backend python -m pytest -q`: **PASS**, toàn bộ test được thu thập trong container chạy qua, không có failure; output đạt 100%. Wrapper không in tổng số test nên không ghi số lượng suy đoán.
- Preview mock tạo mẫu Nhật và parse thành công 36 requirement.
- Pipeline hợp lệ với `data_readiness=high` đi tới `waiting_clarification` và sinh 5 câu vòng 1.

## Blockers chuyển giao

- Sample Bid vẫn có budget/lịch metadata null dù RFP có `1,500万円` và lịch 2027.
- Runtime OpenAPI thiếu GET solution và trả 405, không khớp source workspace.
- Evaluation chưa hoàn tất, chưa kiểm chứng được phân bố rating và vòng 2.
- Quotation chưa thể tính vì thiếu WBS; bid list chưa có tổng giá.
- Chưa có evidence runtime cho Q&A lifecycle, proposal versions, price gate và export artifacts.
- Test source xác nhận fixture 36 mã FR/NFR và nội dung unique, nhưng endpoint parse trong smoke không trả rows để QA tái tính uniqueness độc lập; vì vậy chỉ ghi `PASS source`, không ghi runtime PASS.

QA không sửa source theo vai trò được giao và không tạo bằng chứng giả. Bước tiếp theo cần xử lý implementation/Preview drift rồi chạy lại acceptance với mock.

**HANDOFF — QA Đợt 4 complete; dừng tại đây.**
