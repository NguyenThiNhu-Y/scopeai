# Handoff — GATE-01 MVP scope

## Trạng thái

Đã xử lý R-08 trong `docs/reviews/review_G4.md`.

## Thay đổi

- Gỡ kiểm tra authentication/object-level authorization và các role gate dở dang.
- Giữ actor do client gửi qua `X-Actor` chỉ để ghi audit log; `X-User` còn được đọc tạm để tương thích các test cũ.
- Không thêm auth server, đúng AGENTS.md luật 9 và phạm vi công cụ nội bộ một người dùng.
- Cập nhật `docs/quality/gate_summary.md`: GATE-01 = “Chấp nhận rủi ro: ngoài phạm vi MVP”.
- Cập nhật các test bị ảnh hưởng để kiểm tra hành vi một người dùng MVP.

## Verification

Lệnh `pytest -q`: **187 passed**.

## Ghi chú

GATE-02 trở đi không thuộc phạm vi thay đổi này; verdict tổng thể vẫn phụ thuộc các gate và E2E còn lại.
