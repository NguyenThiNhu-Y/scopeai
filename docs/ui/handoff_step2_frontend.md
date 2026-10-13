# Handoff Frontend Bước 2 — Khung trang hồ sơ

## Trạng thái

**IMPLEMENTED — build/test đạt; kiểm tra trực quan trên browser bị BLOCKED do môi trường thiếu Chromium.**

Đã triển khai đúng phạm vi khung trang hồ sơ. Không gọi LLM thật, không sửa logic backend và không tạo screenshot giả.

## Thay đổi

- `frontend/src/pages/BidDetailPage.tsx`
  - Gộp metadata vào đầu trang: breadcrumb, tên dự án, khách hàng, hạn nộp và số ngày còn lại, giai đoạn, trạng thái, KT/Giá và tổng giá có currency.
  - Thêm các nút hành động `Tải trọn bộ hồ sơ`, `Yêu cầu sửa`, `Duyệt`; nút tải đã nối `downloadExport(..., 'bundle')`, hai nút còn lại mở/điều hướng tới tab Quy trình & phê duyệt.
  - Bỏ thẻ 6 ô thông tin lớn khỏi đầu trang.
  - Đổi nút sau khi pipeline đã có step thành `Chạy lại`; trạng thái đang chạy vẫn hiển thị loading.
  - Hiển thị banner vàng khi hồ sơ chờ làm rõ và tự chuyển sang tab `Yêu cầu & câu hỏi` nếu còn câu chưa trả lời.
  - Thêm số câu hỏi chưa trả lời và số requirement vào thanh tab.
  - Chuyển khối file đính kèm và đọc/xác nhận dữ liệu ra khỏi Tổng quan, vào tab Yêu cầu & câu hỏi.
- `frontend/src/components/PipelineProgress.tsx`
  - Chuyển thành dòng tiến trình mảnh.
  - Chỉ render các step backend thực sự trả về, không tự tạo B4/B5 hoặc step pending giả.
  - Vẫn giữ badge loading, hoàn tất, lỗi, chờ làm rõ và nút chạy lại.
- `frontend/src/components/Sidebar.tsx`
  - Bỏ mục `Đánh giá` vì hiện chưa có trang tương ứng.
  - Giữ nút `+ Tạo hồ sơ` luôn nổi bật.

## Kiểm tra

- `frontend`: `npm run build` — **PASS**.
- `frontend`: `npm run test` — **PASS**, 1 test file, 6 tests.
- Preview rebuild bằng `podman-compose.preview.vibeflow.yaml` — services backend/frontend **Up**.
- `GET /api/health` — **HTTP 200**, database `ok`, `llm_provider: mock`.
- Frontend production preview build trong container — **PASS**.
- Preview được rebuild lại sau completeness review; health vẫn **HTTP 200** với LLM mock.

## Preview blocker

- Không có Chromium executable trong môi trường QA; không có binary thay thế trong PATH.
- Vì vậy chưa thể chụp screenshot thật hoặc xác nhận bằng browser các tiêu chí về chiều cao 900 px, banner click, điều hướng tab, console và accessibility runtime.
- Không tạo ảnh giả. Cần tester có browser chạy lại hồ sơ mẫu Nhật và cập nhật `docs/ui/compare_03_tong_quan.md` hoặc biên bản kiểm tra tương ứng.

## Đối chiếu tiêu chí Bước 2

| Tiêu chí | Kết quả |
|---|---|
| Đầu trang gọn, meta và hành động | Đã triển khai; browser verification BLOCKED |
| Dòng tiến trình mảnh, chỉ step backend thật | Đã triển khai; browser verification BLOCKED |
| Tab có số đếm | Đã triển khai; browser verification BLOCKED |
| Banner Chờ làm rõ và điều hướng câu hỏi | Đã triển khai; browser verification BLOCKED |
| Menu trái đúng trạng thái | Đã triển khai; browser verification BLOCKED |
| Trạng thái rỗng/lỗi không bịa dữ liệu | Giữ dữ liệu từ API và các trạng thái loading/error hiện có |
| Không còn bước `Bỏ qua` sai | Tiến trình lấy trực tiếp từ `pipeline_progress.steps`, không hard-code bước không tồn tại |

## Chuyển giao

Frontend Bước 2 hoàn tất ở mức source/build/test. Tester cần kiểm tra trực quan trên Preview khi có browser. Không thực hiện Bước 3 hoặc reviewer trong role này.
