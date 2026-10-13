# Handoff — Đợt 5 frontend

Ngày: 2026-10-11  
Vai trò: parallel dispatch coordinator

## Trạng thái

**DONE — frontend source đã sửa các finding tái hiện được; build/test pass. Acceptance Preview vẫn cần tester xác nhận riêng.**

## Phạm vi đã hợp nhất

- Frontend A xử lý khung tiến trình, nút chạy lại, trạng thái rỗng/lỗi, danh sách hồ sơ,
  tiêu đề proposal theo ngôn ngữ khách hàng và các hiển thị tổng quan.
- Frontend B xử lý danh sách hồ sơ, bảng cài đặt effort, nhãn màn tạo hồ sơ, trạng thái nút
  tạo hồ sơ và tên bộ mẫu CRM.
- Coordinator reconciliation sửa các drift contract còn lại:
  - feasibility hiển thị dạng mô tả định tính, không còn UI điểm số;
  - hướng giải pháp dùng nhãn nghiệp vụ tiếng Việt;
  - thêm client xuất Q&A sheet theo endpoint hiện có; chưa có UI nhập lại file Q&A;
  - bỏ các câu hiển thị literal `backend/API` ở khu vực kế hoạch đã rà soát;
  - làm tròn ngày công và chuyển onsite ratio về phần trăm hiển thị;
  - evaluation type hỗ trợ rating `cần làm rõ`;
  - các field reliability/excluded directions khớp contract Đợt 4.
- Không sửa backend và không gọi LLM thật.
- Bổ sung xuất Q&A sheet và thay các literal kỹ thuật còn sót trong UI bằng nhãn nghiệp vụ;
  nhập lại file Q&A chưa được triển khai.
- Sửa `formatDate` để hiển thị đúng cả ngày và timestamp ISO theo dạng `dd/MM/yyyy HH:mm`, tránh vỡ định dạng ở lịch sử duyệt.
- Việt hóa nhãn giai đoạn deal trong bộ lọc và danh sách hồ sơ.
- Việt hóa các nhãn kế hoạch còn dùng thuật ngữ kỹ thuật tiếng Anh như "Master schedule" và "WBS tree editor".

## Verification

- Frontend tests: **7 passed**.
- Frontend production build: **PASS** (`tsc -b && vite build`).
- Frontend production build sau follow-up: **PASS** (`tsc -b && vite build`).
- Frontend tests sau follow-up: **7 passed** (`vitest run --run`), gồm regression test định dạng ngày và timestamp.
- Frontend build sau follow-up: **PASS** (`tsc -b && vite build`).
- Regression assertion cho trạng thái dịch vụ đã được cập nhật sau khi đổi nhãn hiển thị.
- Không tạo screenshot hoặc bằng chứng Preview giả.

## Việc còn lại cho bước sau

- `docs/ui/dot5_check.md` và `docs/ui/dot5_review.md` ghi rõ phần source đã pass và phần runtime chưa có evidence,
  không tạo bằng chứng giả.
- Proposal versions đã có trong contract nhưng frontend chưa tích hợp; nhập Q&A, chỉnh quotation
  và approval cũng cần được tester xác nhận trên runtime. Frontend chỉ hiển thị/điều khiển các
  contract đã tích hợp, không tự tạo dữ liệu.

## DONE

- Chỉ sửa frontend và tài liệu handoff; không sửa backend.
- Không cấu hình hoặc gọi LLM thật.
- Không dùng git và không tạo screenshot/evidence giả.
