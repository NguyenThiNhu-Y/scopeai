# Kiểm tra Đợt 6a

Ngày kiểm tra: 2026-10-11  
Vai trò: QA tester  
Môi trường: Preview qua `podman-compose.preview.vibeflow.yaml`, `LLM_PROVIDER=mock`; code sau sửa review Dot 6a  
Hồ sơ Nhật dùng để kiểm tra dữ liệu hiện có: bid `97`, khách `株式会社デモ商事（仮名・架空）`, ngôn ngữ `ja`.

## Tóm tắt sau sửa

| Nhóm | Kết quả | Ghi chú |
|---|---|---|
| Báo giá hiện có | PASS một phần | Có số liệu thật và lock sau duyệt; chưa chứng minh được các mô hình/tùy chọn mới trên Preview |
| Lịch hiện có | PASS một phần | Có ngày bắt đầu/kết thúc và Gantt data; thiếu các trường go/no-go và mốc MVP/Production theo intake |
| Q&A Excel | PASS code/test; Preview chưa hoàn tất | Route tồn tại trong source mới; workbook có cột mã, vòng và cột trả lời màu vàng; chưa có browser/file evidence hoàn chỉnh |
| Email khách | PASS code/test; Preview chưa hoàn tất | Route tồn tại trong source mới; chưa hoàn tất walkthrough Copy trên Preview |
| Automated frontend tests | PASS | 9 tests passed; đã bổ sung `waitFor` để hết warning query undefined/act của test Q&A |
| Frontend type-check/build | PASS | Cả hai lệnh pass |
| Browser walkthrough | BLOCKED/PARTIAL | Preview backend phục vụ API 200 cho bid 104; chưa có browser walkthrough hoàn chỉnh trong môi trường hiện tại |

## Đối chiếu đầy đủ yêu cầu gốc

| Yêu cầu gốc | Kết quả QA | Bằng chứng hoặc thiếu sót |
|---|---|---|
| Chọn Trọn gói / T&M / ODC | BLOCKED/PARTIAL | Chỉ quan sát được `fixed_price`; chưa có bằng chứng runtime cho T&M và ODC |
| Chọn VND / JPY / USD | BLOCKED/PARTIAL | Chỉ quan sát được JPY trên bid 97 |
| Dự phòng, onsite, price-to-win -50..+200 | BLOCKED/PARTIAL | Response có dự phòng 20% và onsite 0.1; chưa kiểm thử chỉnh sửa hoặc giới hạn price-to-win |
| T&M thanh toán theo tháng, ODC = FTE × tháng | BLOCKED | Chưa có bằng chứng runtime/UI |
| So sánh ngân sách và gợi ý điều chỉnh | BLOCKED | `budget=null`, không thể tính chênh lệch |
| Tính lại bằng code, khóa sau duyệt | PARTIAL/PASS | Đã thấy tổng code-computed và `locked=true` trên bid đã duyệt; chưa kiểm thử thao tác UI trước/sau duyệt |
| Go/no-go sau PoC mặc định 10 ngày làm việc | BLOCKED | Thiếu các trường go/no-go trong schedule runtime |
| Ngày MVP/Production theo kế hoạch khách | BLOCKED | Thiếu các trường intake và ngày sớm nhất trong schedule runtime |
| Form lịch có ba ô và Gantt có khoảng nghỉ | BLOCKED | Browser blocked; API chỉ có task dates, không phải bằng chứng UI Gantt |
| Q&A export `.xlsx` theo ngôn ngữ khách, cột trả lời vàng | PASS code/test; Preview chưa hoàn tất | Export mới có mã câu hỏi, `Vòng`/`ラウンド`, câu hỏi, lý do, trả lời; ô trả lời màu vàng; test pass |
| Q&A import, gộp trả lời, tiếp tục pipeline | PASS code/test; Preview chưa hoàn tất | Import giới hạn 5 MB/200 dòng, đối chiếu mã + vòng, bỏ qua dòng trống/cũ/sai và trả warnings; test pass |
| Email mock theo ngôn ngữ khách, điền tên khách/người gửi | PASS code/test; Preview chưa hoàn tất | Structured `EmailDraft`, mock gateway, mask PII và code điền identity; test pass |
| Email sửa được và Copy | PASS source/test UI; Preview chưa hoàn tất | UI có textarea chỉnh sửa và Copy; chưa có browser evidence thực tế |

## Bằng chứng dữ liệu thật

### TC-6A-01 — Báo giá hồ sơ Nhật

Endpoint đã gọi: `GET /api/bids/97/quotation`.

- Mô hình hiện tại: `fixed_price`.
- Tiền tệ: `JPY`.
- Dự phòng: `20.0%`.
- Onsite trong response: `0.1`.
- Tổng PoC: `1,259,622 JPY`.
- Tổng MVP: `4,765,449 JPY`.
- Tổng Production: `2,060,735 JPY`.
- Subtotal/grand total: `8,085,806 JPY`.
- Budget: `null`, vì vậy không có số chênh ngân sách thực để ghi nhận.

Kết quả: **PASS một phần**. Số liệu tổng theo mô hình fixed price có thật và nhất quán với dữ liệu API. Chưa thể PASS đầy đủ yêu cầu Dot 6a vì chưa có bằng chứng runtime cho Trọn gói/T&M/ODC, VND/USD, price-to-win và bảng so sánh ngân sách.

### TC-6A-02 — Khóa sau duyệt giá

Endpoint đã gọi: `GET /api/bids/97`.

- `status`: `price_approved`.
- `locked`: `true`.
- `grand_total`: `8,085,806`.
- `currency`: `JPY`.

Kết quả: **PASS** cho trạng thái khóa sau duyệt ở hồ sơ mẫu hiện có. Chưa thực hiện thao tác UI thay đổi báo giá vì browser walkthrough bị blocked.

### TC-6A-03 — Lịch và khoảng nghỉ

Endpoint đã gọi: `GET /api/bids/97/schedule`.

- Ngày bắt đầu kế hoạch: `2026-10-26`.
- Ngày kết thúc: `2027-04-30`.
- `buffer_days`: `5`.
- `deadline_violation`: `true`.
- Dữ liệu task có các phase `poc`, `mvp`, `production` và ngày bắt đầu/kết thúc từng task.
- `go_no_go_start`, `go_no_go_end`: không có.
- Mốc khách `customer_mvp_start`, `customer_production_start`: không có.
- Ngày sớm nhất MVP/Production tương ứng: không có trường runtime để xác nhận.

Kết quả: **PASS một phần**. Có schedule data thật; chưa PASS yêu cầu khoảng go/no-go mặc định 10 ngày làm việc, mốc MVP/Production theo intake và Gantt thể hiện khoảng nghỉ.

## Q&A sheet

### TC-6A-04 — Xuất và mở file Q&A

Kết quả: **PASS code/test; Preview evidence BLOCKED**.

Source mới và test xác nhận endpoint export tạo workbook với:

- Mã câu hỏi.
- Vòng hỏi (`ラウンド` với mẫu Nhật).
- Câu hỏi/lý do theo contract.
- Cột trả lời được tô vàng.

Chưa có file tải xuống từ browser Preview để ghi nhận evidence người dùng.

### TC-6A-05 — Nhập file đã điền và tiếp tục pipeline

Kết quả: **PASS code/test; Preview evidence BLOCKED**. Test bao phủ import một vòng,
file thiếu cột, mã câu hỏi sai, file quá 5 MB, quá 200 dòng và nhập lại file đã đóng.
Runtime/browser chưa hoàn tất luồng hai vòng để ghi số liệu evidence.

## Email gửi khách

### TC-6A-06 — Soạn email, sửa và Copy

Kết quả: **PASS code/test; Preview evidence BLOCKED**.

Source/test xác nhận email tiếng Nhật dùng mock, tên khách/người gửi do code điền,
và UI có chỉnh sửa/Copy. Chưa thể ghi nhận thao tác browser Preview hoàn chỉnh.

## Automated checks

- `backend`: focused Q&A regression → **PASS, 18 tests passed**; gồm schema cột vòng, import một vòng, import vòng hai, file cũ/sai mã, giới hạn 5 MB/200 dòng và file thiếu cột.
- `frontend`: `npm run test -- --run` → **PASS, 9 tests passed**.
- `frontend`: `npm run type-check` → **PASS**.
- `frontend`: `npm run build` → **PASS**.
- `backend`: full raw `pytest -q` → **PASS, 230 tests passed**. Các lần chạy qua wrapper báo `No tests collected` và không được dùng làm evidence.
- Backend logs xác nhận Preview phục vụ thành công các request API của bid 104, gồm bid/quotation/schedule/questions; đây không phải bằng chứng UI hoặc file tải xuống.


1. Preview stack đã rebuild với source mới; backend phục vụ API 200 cho bid `104`, nhưng service vẫn báo trạng thái `starting` khi kiểm tra cuối.
2. Chưa có browser walkthrough hoàn chỉnh; không tạo screenshot/file evidence giả và không khẳng định các thao tác UI chưa quan sát được.
3. Route Q&A export/import/email-draft đã có trong source mới và test; evidence Preview phải được tester chạy lại khi browser/runtime sẵn sàng.
4. Import Q&A hiện bắt buộc cột mã câu hỏi + vòng, giới hạn 5 MB/200 dòng, cảnh báo dòng bị bỏ qua và không submit lại câu đã đóng.


Đợt 6a **CHƯA ĐẠT đầy đủ QA acceptance**. Code và test cho Q&A vòng/giới hạn
upload, báo giá và email đã được cập nhật; frontend test/build pass. Tuy nhiên chưa
có browser evidence hoàn chỉnh cho mẫu Nhật: ba mô hình báo giá, đổi tiền tệ, điều
chỉnh giá/chênh ngân sách, Gantt, export/import hai vòng và Copy email. Không chuyển
sang đợt khác; cần chạy lại đúng walkthrough Preview khi browser/runtime sẵn sàng.
