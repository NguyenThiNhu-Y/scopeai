# So sánh Màn 10 — Cài đặt

## Phạm vi và evidence

- Phạm vi: chỉ `frontend/src/pages/SettingsPage.tsx`; không sửa Màn 2 hoặc các màn khác.
- API giữ nguyên: `GET /api/settings` và `PUT /api/settings/{key}`. Payload lưu vẫn là YAML hợp lệ do frontend dựng từ các field hiện có.
- Browser screenshot/DOM runtime chưa thực hiện được trong step này vì môi trường trước đó ghi nhận Chromium unavailable; không tạo ảnh giả.

## Đối chiếu yêu cầu

| Hạng mục | Trước | Sau | Mức | Evidence |
|---|---|---|---:|---|
| Effort | Textarea YAML | Bảng hướng × PoC/MVP/Production, mỗi phase min/max | CAO | Source hiện render table và input có nhãn truy cập được |
| Đơn giá | Textarea YAML | Bảng vai trò × offshore/onsite; thêm overhead PM/BrSE và tỷ giá VND/JPY từ YAML hiện có | CAO | Source map đúng `rates`, `overhead`, `fx`; validation và YAML builder lưu cả các field này, không bịa field |
| Hệ số | Textarea YAML | Bảng tên, giá trị, lý do; field trần hệ số | CAO | Source map đúng `factors` và `factor_cap` |
| Validation | Backend chỉ báo lỗi sau khi submit | Chặn trước khi gọi API: số không âm/dương, min ≤ max, lý do bắt buộc | CAO | `validate()`; lỗi tiếng Việt qua `role=alert` |
| Lưu từng bảng | Nút lưu chung cho textarea | Nút `Lưu bảng này` theo tab, dùng API PUT hiện có | CAO | `updateSetting(selected, yaml, 'manager_web')` |
| Xem YAML | Luôn mở textarea dài | `details` “Xem YAML thu gọn”, chỉ đọc | TB | YAML preview hiển thị từ payload hiện tại sau khi dựng |
| Nhãn kỹ thuật | Có “M8 · Quản trị” | Đã bỏ | TB | Không còn trong SettingsPage |
| Responsive/accessibility | Bố cục sidebar + textarea | Tab điều hướng, bảng có caption sr-only, input/button có label/focus | TB | Source và Tailwind responsive overflow |

## Kiểm tra

- `frontend`: `npm run build` — PASS sau completeness audit.
- `frontend`: `npm run test -- --run` — PASS, 1 file / 6 tests.
- Review follow-up: đã sửa parser/YAML builder để đọc và lưu overhead PM/BrSE cùng tỷ giá VND/JPY; thêm validation cho các field này trước PUT.
- Chưa có screenshot thật hoặc console/DOM browser evidence do Chromium unavailable; không kết luận visual PASS.

## Kết luận

Source implementation đạt phạm vi Màn 10 và giữ API hiện có. Browser QA cần tester chạy lại trong môi trường có Chromium để xác nhận bố cục 1440×900, nhập liệu, validation trực tiếp và thông báo sau PUT.
