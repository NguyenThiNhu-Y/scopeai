# Handoff mục B — Frontend

## Phạm vi

Chỉ nối giao diện tab **Quy trình & phê duyệt** với các API backend đã có; không sửa backend hay component dùng chung.

## Thay đổi

- `frontend/src/api/client.ts`: thêm client cho Bid/No-bid (`GET/PUT bid-qualification`), deal stage (`PUT deal-stage`), và proposal versions (`GET/POST versions`, `PUT sent`).
- `frontend/src/api/types.ts`: thêm kiểu `DealStage`, `BidQualification`, tiêu chí và `ProposalVersion`; bổ sung `deal_stage` vào `Bid`.
- `frontend/src/pages/ApprovalsPage.tsx`: hiển thị tiêu chí/trọng số/điểm gợi ý, nhấn mạnh gợi ý chỉ tham khảo; nhập người xác nhận và xác nhận Bid/No-bid; chọn/lưu deal stage; tạo version theo chuỗi backend và đánh dấu đã gửi; có loading/error và invalidate query sau mutation.

## Kiểm tra

- `npm test -- --run`: suite hiện có 12/14 pass; 2 test cũ không liên quan bị fail ở WBS/Settings do thay đổi concurrent trong workspace.
- `npm run build`: chưa qua vì lỗi TypeScript có sẵn ngoài phạm vi tại `frontend/src/pages/SettingsPage.tsx:38` (`current` implicit any). Không có lỗi được báo từ phần B trước lỗi này.

## Lưu ý

- Không tự tính quyết định Bid/No-bid ở frontend; quyết định chỉ được lưu sau thao tác người dùng.
- Chuỗi version 1.0 → 1.1 → 2.0 do backend quyết định, frontend chỉ gọi API và refetch danh sách.
