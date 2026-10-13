# Handoff — Frontend Màn 6 Kế hoạch & báo giá

Ngày: 2026-10-11  
Vai trò: frontend-dev  
Trạng thái: **CHANGES REQUIRED / PARTIAL**

## Files đã sửa

- `frontend/src/components/BidPlanTab.tsx`
  - Định dạng toàn bộ giá bằng currency backend, không còn mặc định VND.
  - Bổ sung bốn ô tóm tắt: tổng, dự phòng, ngày công và onsite.
  - Bổ sung bảng so ngân sách và bảng chi phí theo giai đoạn.
  - Giữ trạng thái thiếu dữ liệu minh bạch, không bịa khoảng, phần trăm hoặc số onsite.
  - Ghi rõ WBS trên tab là bản xem trước và dẫn sang trình sửa thật.
- `docs/ui/compare_06_ke_hoach.md`
  - Tài liệu đối chiếu được QA cập nhật sau kiểm tra Preview, gồm evidence API và giới hạn visual.
- `docs/ui/api_gaps.md`
  - Các gap M6 được ghi nhận để backend xử lý tập trung; không thêm giá trị giả.

## Yêu cầu đã đáp ứng ở frontend

- Currency của quotation được truyền vào mọi `formatAmount` trong Màn 6.
- Bốn ô số và hai bảng tổng hợp dùng dữ liệu response hiện có.
- Mốc thanh toán, chi tiết theo vai trò, Gantt, loading/empty/error state và WBS preview được giữ nguyên.
- Không gọi LLM thật, không hardcode API URL, không tự tính số nghiệp vụ.

## Chưa hoàn tất / blocker

- Chưa có endpoint cập nhật contract model/currency hoặc onsite percentage.
- Quotation chưa có quotation range, phase man-day/range, chênh lệch ngân sách theo phần trăm hay work-type matrix.
- WBS preview trên Màn 6 chưa inline edit/collapse/filter phase; trình sửa thật nằm ở route WBS riêng.
- Effort breakdown đầy đủ vẫn xuất hiện ở Màn 6, trong khi yêu cầu muốn chỉ giữ một dòng tóm tắt.
- Không có screenshot thật nếu Chromium không khả dụng; không tạo screenshot thay thế. Chi tiết blocker runtime nằm trong handoff QA.

## Verification

- `npm run build`: PASS (`tsc -b && vite build`, 111 modules transformed).
- `npm run test`: PASS (1 test file, 6 tests passed).
- Các warning React Router future flags và npm config không làm fail build/test.
- Preview/browser: chưa đánh dấu PASS khi chưa có evidence thật.

## Workflow boundary

Chỉ xử lý frontend Màn 6 và deliverables trực tiếp của màn này. Không sửa backend, không làm màn khác và không thực hiện reviewer tổng.
