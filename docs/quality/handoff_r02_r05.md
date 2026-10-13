# Handoff — R-02 đến R-05: pipeline context

## Đã thực hiện

- Intake/gap đưa nội dung RFP text từ file đính kèm vào context sau khi trích text và mask PII; tổng giới hạn khoảng 16.000 ký tự, chia đều theo file.
- Intake/gap đưa tối đa 40 requirement mẫu và tổng số requirement.
- Solution nhận intake, câu hỏi/câu trả lời, tóm tắt requirement và sample profile; prompt xét `none` trước và yêu cầu lý do loại từng hướng.
- Đổi thứ tự pipeline thành `intake → gap → solution → evaluate → wbs → proposal`.
- Evaluate nhận direction/architecture context và chỉ gửi requirement của batch hiện tại, tối đa 40 dòng.
- Prompt evaluate định nghĩa rõ `◎/○/△/×` và yêu cầu `note_vi` cụ thể.
- Proposal nhận context intake, clarification, solution, risk, WBS theo phase × role, schedule và coverage requirement.
- Proposal bắt buộc có `{{QUOTATION}}`; code thay bằng giá đã duyệt hoặc `[Presales điền]`.
- Thêm `backend/tests/test_pipeline_context.py`.

## Kiểm chứng

- Regression context + proposal schema: **4 passed**.
- Compile các module pipeline và smoke script: **PASS**.
- `python scripts/smoke_real_llm.py`: **FAIL có chủ đích** vì môi trường hiện tại chưa cấu hình `LLM_PROVIDER=openai_compat`; không gọi provider thật.
- Toàn bộ pytest cần đọc kết quả từ job chạy bằng Python module, vì wrapper `rtk` báo sai `No tests collected`.
