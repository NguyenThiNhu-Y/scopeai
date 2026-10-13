# Review Đợt 5 — frontend

Ngày: 2026-10-11  
Phạm vi: L3-01..L3-18 và hiển thị dữ liệu Đợt 4

## Findings

1. **MEDIUM — Sai ngôn ngữ customer-facing ở proposal:** `frontend/src/pages/ProposalPage.tsx:49-53`
   dùng `language` để đặt tiêu đề phần giả định và ngoài phạm vi, trong khi các phần chính dùng
   `effectiveLanguage`. Khi hồ sơ khách là `ja` hoặc `en` nhưng người dùng chưa đổi tab ngôn ngữ,
   proposal có thể trộn tiêu đề tiếng Việt với nội dung theo hồ sơ khách. Cần dùng cùng một ngôn ngữ
   hiệu lực cho toàn bộ tiêu đề customer-facing.

2. **MEDIUM — Có thể lộ mã hướng giải pháp thô trong ma trận:**
   `frontend/src/components/RequirementMatrix.tsx:171` render trực tiếp
   `item.solution_direction || item.category`. Nếu backend trả `rag`, `traditional_ml` hoặc mã nội bộ,
   giao diện sẽ hiển thị mã thay vì nhãn nghiệp vụ tiếng Việt, vi phạm yêu cầu không hiện mã thô.
   Cần map hướng giải pháp và category qua bảng nhãn trước khi render, có fallback nghiệp vụ.

3. **LOW — Đổi bộ lọc deal stage không quay về trang đầu:**
   `frontend/src/pages/BidsPage.tsx:71-73` chỉ reset `page` khi `status` hoặc `debouncedQ` thay đổi,
   không bao gồm `dealStage`. Người dùng đang ở trang sau rồi đổi giai đoạn có thể nhận trang rỗng
   dù vẫn có hồ sơ phù hợp. Thêm `dealStage` vào dependency của effect reset trang.

4. **MEDIUM — Tài liệu trước ghi quá mức về Q&A import:**
   `frontend/src/pages/BidDetailPage.tsx:479-481` chỉ có nút `Xuất Q&A sheet` và nhãn
   `Trả lời trên màn hình`; không có control chọn/tải file Q&A đã điền để nhập lại. Vì vậy
   B3-05 mới được surfaced một phần, không được ghi là đã có export/import đầy đủ.

5. **Đã sửa:** một số màn còn literal kỹ thuật `backend/API`; đã thay bằng trạng thái nghiệp vụ
   hoặc mô tả trung tính.
6. **Đã sửa:** UI feasibility còn đọc score numeric cũ; đã chuyển sang mô tả định tính đúng contract
   Đợt 4.
7. **Đã sửa một phần:** đã có export Q&A và trả lời trên màn hình; import file Q&A chưa có control
   frontend tương ứng, nên không coi B3-05 là hoàn tất.
8. **Còn thiếu runtime evidence:** chưa có `dot5_check` Preview/browser evidence cho toàn bộ luồng
   mẫu Nhật, approval, export, timestamp và lỗi 409.
9. **Còn thiếu tích hợp frontend:** API contract đã mô tả proposal versions tại
   `docs/04_architecture/api_contract.md:666-670`, nhưng frontend chưa có query/control để liệt kê,
   tạo hoặc đánh dấu phiên bản gửi khách. UI hiện giữ empty state, không bịa danh sách phiên bản.
10. **Đã sửa follow-up:** timestamp được định dạng thống nhất, nhãn giai đoạn deal và các nhãn kế hoạch
   còn sót tiếng Anh đã được Việt hóa.

## Quality checks

- Không sửa backend.
- Không gọi LLM thật.
- Không phát hiện secret hoặc URL tuyệt đối trong frontend API client.
- Loading, empty và error states hiện diện ở các request chính đã rà soát; export action có trạng thái
  đang tạo/lỗi ở các màn đã kiểm tra.
- Build: **PASS** sau các chỉnh sửa follow-up.
- Frontend tests: **7 passed**, gồm regression test cho ngày và timestamp approval.

## Verdict

**CHANGES REQUIRED** — phần lớn source findings của Đợt 5 đã được xử lý và build/test đều pass,
nhưng còn năm finding source/tài liệu ở trên cần sửa trước khi phê duyệt. Ngoài ra chưa đủ bằng chứng
Preview/runtime để ghi `PASS` cho toàn bộ Đợt 5; các giới hạn runtime và proposal versions được
ghi rõ, không được coi là đã hoàn tất.
