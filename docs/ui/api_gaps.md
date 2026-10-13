# API Gaps — Đợt 2

## Màn 3 Tổng quan

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
| Evaluation chưa có 3 điểm khả thi (dữ liệu/kỹ thuật/giá trị) | `/api/bids/92/evaluations` chỉ có `solution_direction`, `warnings`, `items`, `stats` | Không render được 3 thanh điểm ở Tổng quan và Giải pháp | Backend/schema bổ sung output có cấu trúc điểm và khuyến nghị |
| Rủi ro chưa có mức độ/type/mitigation | `solution_direction.risks_vi` chỉ là mảng chuỗi | Không render được cột mức độ màu và cách giảm thiểu | Backend trả danh sách risk object có `severity`, `type`, `description`, `mitigation` |
| Hướng giải pháp chưa có confidence và hướng bị loại | Response chỉ có `direction`, `reason_vi`, `risks_vi`, `architecture_notes_vi` | Không render đủ thẻ Hướng giải pháp | Backend/schema bổ sung `confidence` và `rejected_directions` |
| Solution chưa có giả định và khả thi có cấu trúc | Response không có `assumptions_vi`, `feasibility` (3 điểm + khuyến nghị) | Không render được giả định và 3 thanh điểm khả thi ở Màn 5 | Backend/schema bổ sung các field tùy chọn, không để frontend suy diễn |
| Rủi ro chưa có object đầy đủ | Response chỉ có `risks_vi` là mảng chuỗi | Chưa render được mức độ, loại và cách giảm thiểu theo từng dòng | Backend trả `risks[]` gồm `severity`, `type`, `description`, `mitigation` |

## Ghi chú tích hợp

- Quotation, questions, effort, WBS và schedule đã có endpoint và trả dữ liệu trên Preview.
- M3-06 đã được xử lý ở frontend: `BidDetailPage` gọi schedule và hiển thị số task WBS/ngày kết thúc trong thẻ `Effort & kế hoạch`.
- File này chỉ ghi dữ liệu/API thiếu hoặc chưa đủ cấu trúc; không bịa giá trị để làm đầy UI.

## Màn 4 Yêu cầu & câu hỏi

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
| Question chưa có `topic` và `blocking` | `Question` chỉ có `impact`, `round_no`, `reason_vi`, `status` | UI chưa thể hiển thị chủ đề và badge Chặn đúng contract | Backend/schema bổ sung field; frontend hiện nhãn ảnh hưởng và không bịa badge Chặn |
| Chưa có endpoint xuất/nhập Q&A sheet | `client.ts` chỉ có questions/answers và export requirement | Hai nút Q&A được hiển thị disabled, chưa thể thao tác thật | Backend thêm export/import Q&A theo round, schema và quyền kiểm tra file |
| Sample preview không chấp nhận `sample_key` đang dùng | Preview log: `GET /api/bids/sample/preview?sample_key=...` trả `400 Bad Request`, trong khi preview không truyền key trả `200 OK` | Không thể hoàn tất luồng kiểm tra hồ sơ mẫu tiếng Nhật từ UI | Backend/Preview cung cấp sample key hợp lệ hoặc cập nhật fixture; không in giá trị key nếu là secret |
| Route pipeline được gọi trong flow nhưng không tồn tại | Preview log: `GET /api/bids/83/pipeline` trả `404 Not Found` | Không thể đọc trạng thái pipeline theo route này; phải dùng contract route hiện có | Backend xác nhận route chuẩn hoặc cập nhật frontend/tester theo route chính thức |

- Màn 4 đã dùng dữ liệu intake, questions và attachments hiện có; không tạo dữ liệu giả cho các gap trên.

## Màn 6 Kế hoạch & báo giá

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
 | Chưa có API cập nhật mô hình hợp đồng và tiền tệ | Đã bổ sung `PUT /api/bids/{id}/quotation`, validate contract model/currency/contingency/onsite và tính lại bằng code | Frontend cần nối PUT để cho chọn Trọn gói/T&M/ODC hoặc VND/JPY/USD | Frontend tích hợp endpoint; không còn gap backend |
 | Thiếu khoảng giá và số theo giai đoạn đầy đủ | Backend đã trả `totals.by_phase` và `totals.phase_man_days`; khoảng effort chuẩn vẫn nằm ở `/effort` | Khoảng min–max cần frontend ghép với effort response, không suy diễn từ quotation | Frontend dùng hai contract hiện có; khoảng giá chi tiết vẫn là gap nếu cần riêng trong quotation |
 | Thiếu chênh lệch ngân sách theo phần trăm và phạm vi | Đã bổ sung `budget.scope=bid_budget` và `difference_percent`; giá trị chỉ có khi hồ sơ có budget | Có thể render bảng khi budget tồn tại; hồ sơ không có budget phải hiện unavailable | Frontend tích hợp field; không còn gap backend |
 | Thiếu onsite có thể chỉnh sửa | `PUT /api/bids/{id}/quotation` nhận `onsite_percent` trong khoảng 0..1 và lưu vào quotation snapshot | Frontend cần nối PUT; giá trị mặc định vẫn do rate card | Frontend tích hợp endpoint; không còn gap backend |
 | Chưa có ma trận giai đoạn × loại công việc | `ScheduleResponse.work_breakdown` đã trả man-day theo phase × role và total, tính từ task WBS | Contract hiện phân loại theo role, chưa có work-type riêng trong WBS | Frontend dùng phase × role; work-type khác role vẫn là gap contract |

- Màn 6 đã render các field hiện có và hiển thị trạng thái thiếu dữ liệu; không tự suy diễn hoặc tạo số thay thế.

## Đợt 3 — Màn 7 Đáp ứng yêu cầu

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
| ~~Export requirement chưa nhận lựa chọn ngôn ngữ ghi chú từ frontend~~ | Đã bổ sung query `note_language` (`vi` / `en` / `ja`) cho `GET /api/bids/{id}/exports/requirements.xlsx`; renderer dùng ngôn ngữ được chọn và có test hồi quy | Frontend có thể truyền selector; nếu không truyền vẫn giữ hành vi theo ngôn ngữ khách | **Đã xử lý backend**; frontend cần truyền query khi nối selector |

- Màn 7 hiện có hai nút xuất dùng cùng endpoint hiện có: `Tải bảng đáp ứng` và `Điền vào file Excel của khách`.
- Backend đã giữ fallback theo `customer_language`; frontend cần truyền `note_language` khi selector được nối.

## Đợt 3 — Màn 8 Proposal & hồ sơ

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
| Proposal chưa có bản dịch nội dung theo từng ngôn ngữ | `GET /api/bids/{id}/proposal` chỉ trả một `sections`; không có `sections_by_language` hoặc endpoint dịch | UI giữ tab ngôn ngữ để đổi nhãn mục, nhưng không được giả vờ nội dung đã dịch | Backend trả nội dung theo ngôn ngữ khách hoặc bổ sung contract dịch; frontend khi đó mới hiển thị nội dung tương ứng |

- Màn 8 đã render đúng dữ liệu proposal hiện có và hiển thị rõ giới hạn của tab ngôn ngữ; không tạo bản dịch giả.

## Đợt 3 — Màn 9 Quy trình & phê duyệt

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
| Chưa có danh sách phiên bản proposal gửi khách | Contract `GET /api/bids/{id}/proposal` chỉ trả bản proposal hiện tại; không có version list hoặc trạng thái gửi khách; chưa có model persisted tương ứng | Thẻ Lịch sử & phiên bản chỉ hiển thị lịch sử changelog và trạng thái thiếu dữ liệu cho phần phiên bản | **Contract blocker**: cần quyết định schema/lifecycle phiên bản trước khi backend tạo endpoint; frontend tiếp tục unavailable, không suy diễn phiên bản |
| ~~History chưa lọc theo `bid_id` ở API~~ | Đã bổ sung query `bid_id` cho `GET /api/history`; có test đảm bảo không trả log của hồ sơ khác | Frontend có thể tải đúng lịch sử theo hồ sơ | **Đã xử lý backend**; frontend có thể truyền `bid_id` |

- Màn 9 dùng các contract hiện có cho bid status, evaluations, effort, schedule, questions, quotation, approvals và changelog history.
- Không dùng `skip` trong UI và không tạo dữ liệu tóm tắt thay thế khi API thiếu field.

## Đợt 3 — Màn 2 Danh sách hồ sơ

| Gap | Bằng chứng | Ảnh hưởng | Đề xuất xử lý |
|---|---|---|---|
| `BidListItem` thiếu mục tiêu, giai đoạn deal, ngày tạo và tổng giá/currency | Đã bổ sung nullable `deal_stage`, `created_at`, `total_price`, `total_price_currency`; tổng giá lấy từ quotation mới nhất đã tính bằng code. `target` vẫn chưa có field/model nguồn | Màn 2 có thể render các field đã có; mục tiêu tiếp tục unavailable, không bịa dữ liệu | **Đã xử lý một phần backend**: frontend nối các field mới; `target` là contract blocker cần nguồn dữ liệu rõ |
| ~~Chưa có filter giai đoạn deal~~ | Đã bổ sung `deal_stage` trong `POST /api/bids`, query `GET /api/bids` và lọc service; có test hồi quy | Frontend có thể dùng bộ lọc giai đoạn deal | **Đã xử lý backend**; frontend tích hợp query |

- Frontend Màn 2 hiện vẫn cần nối các field/query mới; mục tiêu chưa có nguồn dữ liệu nên tiếp tục hiển thị unavailable, không bịa.
