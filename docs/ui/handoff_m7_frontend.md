# Handoff — Frontend Màn 7 Đáp ứng yêu cầu

Ngày: 2026-10-11  
Vai trò: frontend-dev  
Trạng thái: **DONE — chờ tester kiểm tra Preview; còn API gap đã ghi nhận**

## Files đã sửa

- `frontend/src/components/RequirementMatrix.tsx`

## Đã triển khai

- Hàng bộ lọc có số đếm cho Tất cả, Đạt, Một phần, Không đạt và Cần làm rõ.
- Đánh giá hiển thị bằng badge màu; `◎` được tính cùng nhóm Đạt.
- Bảng có các cột Mã, Nội dung yêu cầu, Đánh giá, Thành phần và Ghi chú.
- Nút `Điền vào file Excel của khách` gọi export API hiện có, có trạng thái đang tạo file và thông báo lỗi tiếng Việt.
- Bổ sung nút `Tải bảng đáp ứng` và selector ngôn ngữ ghi chú theo yêu cầu UI; selector đang khóa có giải thích vì backend chưa nhận `note_language`.
- Empty state hướng dẫn người dùng đính kèm Excel tại tab Yêu cầu & câu hỏi, không bịa dữ liệu.
- Có trạng thái lọc rỗng và thuộc tính accessibility `aria-label` / `aria-pressed`.

## API gaps

- API gap mới đã ghi trong `docs/ui/api_gaps.md`: endpoint export chưa nhận `note_language`, nên selector hiện chưa làm thay đổi nội dung file.
- Không thêm dữ liệu mẫu hay giá trị suy diễn.

## Verification

- `npm run build`: PASS — TypeScript và Vite build thành công sau rà soát.
- `npm run test`: PASS — 1 test file, 6 tests passed sau rà soát.
- Preview/browser: chưa chạy trong node frontend; tester node tiếp theo chịu trách nhiệm kiểm tra Preview và ghi `docs/ui/compare_07_dap_ung.md`. Không tạo screenshot giả.

## Boundary

Chỉ sửa component Màn 7. Đã dừng tại boundary frontend-dev; không thực hiện tester, Màn 8, Màn 9 hoặc backend.
