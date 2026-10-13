# Handoff — Đợt 6a frontend tab Yêu cầu & câu hỏi

Ngày: 2026-10-11  
Vai trò: senior frontend developer  
Phạm vi: mục Q&A sheet và email gửi khách của Đợt 6a.

## Trạng thái

**DONE — đã tích hợp UI, API client/types và test cho export/import Q&A cùng email nháp.**

## Đã triển khai

- `frontend/src/api/types.ts`
  - Thêm `EmailDraft` theo response endpoint email nháp.
- `frontend/src/api/client.ts`
  - Giữ export Q&A bằng request root-relative.
  - Thêm `importQuestions(id, file)` gửi file `.xlsx` tới `/api/bids/{id}/questions/import`.
  - Thêm `createEmailDraft(id)` gọi `/api/bids/{id}/questions/email-draft`.
- `frontend/src/pages/BidDetailPage.tsx`
  - Tab `Yêu cầu & câu hỏi` có nút `Xuất Q&A sheet`.
  - Hiển thị trạng thái `Đang xuất…` và khóa thao tác Q&A trong lúc tải file.
  - Có file picker `.xlsx` và nút `Nhập Q&A đã điền`; backend gộp câu trả lời và resume pipeline.
  - Có trạng thái đang nhập, lỗi nhập và refetch câu hỏi/hồ sơ sau khi nhập thành công.
  - Có nút `Soạn email gửi khách`.
  - Hiển thị trạng thái đang soạn và lỗi.
  - Form email sửa được cho người nhận, người gửi, tiêu đề và nội dung.
  - Có nút `Copy email`; nội dung copy gồm tiêu đề và thân email.
  - Không tự sinh số liệu, không gọi LLM trực tiếp từ frontend, dùng API root-relative.
- `frontend/src/App.test.tsx`
  - Bổ sung test gọi import Q&A, export Q&A và thao tác tạo draft email.
  - Kiểm tra draft trả về hiển thị dưới dạng trường chỉnh sửa được và có nút Copy.

## Verification

- `npm run test -- --run`: **9 tests passed**.
- `npm run type-check`: pass.
- `npm run build`: pass.
- Test đã kiểm tra client được gọi với đúng hồ sơ và file `.xlsx` cho import/export.
- Chỉ dùng mock API trong test; không gọi LLM thật.
- Chưa chạy Preview và chưa tạo screenshot/evidence giả. Tester phải kiểm tra luồng thật với mẫu Nhật.

## Lưu ý cho tester/reviewer

- Kiểm tra file xuất có đúng ngôn ngữ khách và cột trả lời tô vàng theo backend.
- Mở file đã điền, nhập lại qua file picker và xác nhận câu trả lời được gộp, pipeline tiếp tục từ bước làm rõ.
- Kiểm tra email mock dùng ngôn ngữ khách, tên khách/người gửi do code điền, nội dung sửa được và Copy hoạt động.
- Kiểm tra lỗi mạng hoặc file không hợp lệ hiển thị thông báo nghiệp vụ tiếng Việt.

## DONE

- Đã hoàn tất đúng boundary frontend tab Yêu cầu & câu hỏi.
- Chưa thực hiện tester Preview hoặc reviewer của Đợt 6a.
- Dừng tại boundary của vai trò.
