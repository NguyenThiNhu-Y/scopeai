# Handoff Màn 10 — Tester

## Trạng thái bàn giao

Frontend đã hoàn thành thay đổi source cho Màn 10 và cung cấp `docs/ui/compare_10_cai_dat.md`.

## Phạm vi cần kiểm tra

- Chạy Preview với `LLM_PROVIDER=mock`.
- Mở Cài đặt ở 1440×900 và responsive.
- Kiểm tra ba bảng effort, đơn giá, hệ số; sửa giá trị hợp lệ rồi lưu từng bảng.
- Kiểm tra lỗi min > max, đơn giá không dương, hệ số thiếu lý do; xác nhận không gọi PUT khi validation fail.
- Mở/thu gọn `Xem YAML thu gọn`, kiểm tra không có textarea chỉnh YAML.
- Ghi screenshot thật, DOM/click, network PUT và console nếu browser khả dụng.

## Giới hạn đã biết

- Chưa có screenshot/DOM/click/console evidence trong step frontend vì Chromium unavailable ở môi trường kiểm tra; không tạo ảnh giả.

## Files

- `frontend/src/pages/SettingsPage.tsx`
- `docs/ui/compare_10_cai_dat.md`
