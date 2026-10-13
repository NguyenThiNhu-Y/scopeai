# Handoff: Follow-up R-08 backend regressions

## Trạng thái

Chưa đạt: đã xử lý một phần tương thích session/fake và precedence validation, nhưng backend pytest vẫn còn lỗi. Không sửa frontend và không thêm authentication/authorization.

## Đã sửa

- `backend/app/services/reference_service.py`: chỉ đọc DB override khi session có `get()`, giữ fallback YAML cho fake session.
- `backend/app/services/factor_engine.py`: fake session dùng `query()` vẫn lấy được requirement count; fallback nội dung request chỉ dùng khi thiếu intake context.
- `backend/app/services/wbs_service.py`: validation cấu trúc/cycle không bị che bởi cap leaf của WBS cũ; task mới vẫn giữ giới hạn 10 man-day.
- `backend/app/services/check_engine.py`: leaf cap là cảnh báo, không kích hoạt semantic retry vì man-day do code phân bổ.
- `backend/app/services/approval_service.py`: leaf cap chuyển thành warning trong pre-approval report, không làm yếu các check schema/cycle/PM-QA.
- `docs/quality/gate_summary.md`: cập nhật trạng thái pytest theo bằng chứng thực tế.

## Kiểm chứng

- Lần chạy trực tiếp trước các thay đổi cuối: còn 8 failures trong nhóm regression tập trung.
- Lần chạy bắt buộc `python -m pytest -q backend/tests`/các lần gọi qua wrapper sau đó chỉ trả dòng: `Pytest: No tests collected`.
- `python -m compileall -q backend/app` đã chạy không có output lỗi.

## Còn tồn tại

- Effort reference/cap và fixture kỳ vọng chưa được thống nhất.
- Deadline schedule vẫn sai với headcount cao và deadline xa.
- Một số WBS fixture vẫn tạo leaf > 10, làm ảnh hưởng warning/approval và các test edit/snapshot.
- B5 rerun/mock call-count cần sửa riêng để semantic retry không gọi lại khi fixture hợp lệ.
