# Đặc tả giao diện — Trợ lý dự thầu

## 1. Phạm vi và nguyên tắc

Giao diện là workspace nội bộ cho một presales engineer xử lý hồ sơ từ RFP đến proposal. UI dùng tiếng Việt; nội dung khách hàng và proposal giữ ngôn ngữ khách (`vi`, `en`, `ja`). API hiện tại là nguồn dữ liệu duy nhất cho số liệu; frontend không tự tính effort, man-day, lịch hoặc giá.

Không triển khai authentication/authorization. `X-Actor` chỉ là thông tin audit theo phạm vi MVP. Không hiển thị giá trong tài liệu xuất cho khách trước khi duyệt; màn hình báo giá nội bộ luôn hiển thị số để manager duyệt.

### Phạm vi ảnh tham chiếu

Đặc tả này đối chiếu các ảnh chuẩn `01_tao_ho_so.png` đến `10_cai_dat.png` trong `docs/ui_reference/`. Tại thời điểm viết đặc tả, `docs/ui_current/` chưa có bộ ảnh hiện tại đầy đủ; việc so sánh pixel/runtime phải được thực hiện ở bước kiểm thử trực quan và ghi vào `docs/ui/ui_compare.md`, không coi là đã hoàn tất trong bước đặc tả.

## 2. Design tokens

| Token | Giá trị sáng | Giá trị tối | Dùng cho |
|---|---|---|---|
| `accent` | `#3b78c2` | `#78a9df` | CTA, tab active, link |
| `accent-strong` | `#255a94` | `#9bc4ef` | hover/focus |
| `accent-soft` | `#eaf2fb` | `#203852` | nền selected/chip |
| `page` | `#f4f6f8` | `#111827` | nền app |
| `surface` | `#ffffff` | `#1f2937` | card/sidebar |
| `line` | `#dde4ee` | `#334155` | viền/divider |
| `ink` | `#17212b` | `#edf2f7` | chữ chính |
| `muted` | `#697586` | `#aab6c5` | chữ phụ |
| `success` | `#16805c` | `#66c99b` | hoàn tất/đáp ứng |
| `warning` | `#b7791f` | `#e7bd65` | cần xác nhận |
| `danger` | `#c44d5c` | `#ef8790` | lỗi/không đáp ứng |

Font Inter, thân 14px, line-height 1.45. Bo góc 8–12px. Không gradient, glow hoặc hiệu ứng trang trí. Focus ring phải nhìn thấy; tôn trọng `prefers-reduced-motion`.

## 3. App shell

- Sidebar cố định rộng 208–240px trên desktop, thu gọn ở mobile.
- Logo hiện tại và tên **Trợ lý dự thầu**; không dùng tên sản phẩm của ảnh tham chiếu.
- Nút chính `+ Tạo hồ sơ`.
- Menu: `Hồ sơ`, `Đánh giá` (có thể route tới danh sách/ma trận), `Cài đặt`.
- Chân menu: `LLM: mock|thật`, nút sáng/tối.
- Nội dung chính nền xám nhạt, card trắng, viền mảnh; layout tối đa khoảng 1180px.

## 4. Trang Tạo hồ sơ và Danh sách

### Tạo hồ sơ `/` và `/bids/new`

Hero ngắn: tên chức năng, mô tả một câu, textarea lớn cho email/RFP. Bên dưới có `Nạp mẫu tiếng Nhật`, `Nạp mẫu tiếng Việt`, đính kèm file, các trường metadata và CTA `Tạo hồ sơ`. Loading, lỗi server và validation hiển thị ngay tại form.

### Danh sách `/bids`

Header `Hồ sơ`, CTA `+ Tạo hồ sơ`, tìm kiếm/lọc trạng thái, bảng/card danh sách gồm dự án, khách hàng, hạn nộp, trạng thái tiếng Việt, giá nếu có. Trạng thái không được hiển thị raw như `waiting_price_approval`.

### Cài đặt `/settings`

Giữ ba nhóm bảng chuẩn `effort`, `rate_card`, `factors`; mỗi nhóm có phiên bản, nguồn `repo/db`, người cập nhật, preview YAML, validation lỗi và lịch sử thay đổi. Không hiển thị secret/provider key.

## 5. Trang chi tiết `/bids/:id`

### Header

1. Breadcrumb `Hồ sơ › #id`.
2. Tên dự án sửa tại chỗ; khách hàng; hạn nộp và `còn N ngày`; giai đoạn deal.
3. Badge trạng thái tiếng Việt, `KT ✓/–`, `Giá ✓/–`, số PII đã che, tổng giá chỉ khi quotation tồn tại.
4. Nút `Tải trọn bộ hồ sơ`, `Yêu cầu sửa`, `Duyệt`.

### Pipeline ngang

Các bước: Trích xuất yêu cầu → Câu hỏi làm rõ → Hướng giải pháp → Khả thi & rủi ro → Kiến trúc & effort → WBS & timeline → Đáp ứng yêu cầu → Proposal. Completed có ✓, running có spinner, failed có màu đỏ + lỗi + `Chạy lại từ bước này`, waiting clarification có trạng thái tạm dừng.

### Tabs và URL

| `tab` | Nhãn | Nguồn chính |
|---|---|---|
| `overview` | Tổng quan | `GET /api/bids/{id}`, `GET /api/bids/{id}/effort`, `GET /api/bids/{id}/quotation`, `GET /api/bids/{id}/evaluations`, `GET /api/bids/{id}/questions` |
| `requirements` | Yêu cầu & câu hỏi | `GET /api/bids/{id}/questions`, `POST /api/bids/{id}/questions/{round}/answers`, `GET /api/bids/{id}/evaluations`, `GET /api/bids/{id}/attachments`, `POST /api/bids/{id}/parse` |
| `solution` | Giải pháp | `GET /api/bids/{id}/solution`, `POST /api/bids/{id}/solution`, `GET /api/bids/{id}/effort` |
| `plan` | Kế hoạch & báo giá | `GET /api/bids/{id}/quotation`, `GET/PUT /api/bids/{id}/schedule`, `GET/PUT /api/bids/{id}/wbs` |
| `coverage` | Đáp ứng yêu cầu | `GET /api/bids/{id}/evaluations`, `GET /api/bids/{id}/exports/requirements.xlsx` |
| `proposal` | Proposal & hồ sơ | `GET/PUT /api/bids/{id}/proposal`, `GET /api/bids/{id}/exports/{proposal.docx,estimate.xlsx,proposal.pdf,bundle.zip,requirements.xlsx}` |
| `approval` | Quy trình & phê duyệt | `POST /api/bids/{id}/approvals/tech`, `POST /api/bids/{id}/approvals/price`, `POST /api/bids/{id}/unlock`, `GET /api/history`, SSE `/api/bids/{id}/pipeline/events` |

Route cũ `/bids/:id/solution`, `/wbs`, `/schedule`, `/quotation`, `/proposal`, `/approvals`, `/export` redirect/điều hướng tới `/bids/:id?tab=...` nhưng không làm hỏng deep link cũ. Nếu backend chưa có `GET /solution` riêng, tab phải hiển thị từ `GET /bids/{id}`/pipeline output và không tự tạo endpoint giả.

## 6. Tab Tổng quan

Lưới 2 cột card có `Chi tiết ›`:

- **Mục tiêu của khách:** objectives, chip constraints, bullet data/users, `+N ràng buộc khác`.
- **Hướng giải pháp:** direction, độ tin cậy, lý do, các hướng bị loại gạch ngang.
- **Khả thi:** ba thanh Data/Kỹ thuật/Giá trị; nếu backend chưa trả điểm thì empty state rõ ràng.
- **Rủi ro lớn nhất:** rủi ro severity cao nhất, màu danger, nguồn/ghi chú.
- **Effort & kế hoạch:** PoC/MVP/Production, task count, ngày kết thúc.
- **Báo giá sơ bộ:** tổng nội bộ, khoảng, dự phòng, budget difference.
- **Đáp ứng yêu cầu:** badge đếm `○/△/×/Cần làm rõ`.
- **Câu hỏi cần khách xác nhận:** 3 câu đầu + `và N câu khác`.

Cuối tab có accordion `Yêu cầu gốc của khách`.

## 7. Tab Kế hoạch & báo giá

Thứ tự bắt buộc:

1. Card báo giá: mô hình hợp đồng, tiền tệ, dự phòng, tổng, budget comparison, theo phase, mốc thanh toán, chi tiết role collapsible. Màn hình nội bộ luôn hiện số.
2. Bảng man-day phase × role.
3. Master schedule: tham số điều chỉnh, số người gợi ý từ backend, summary và Gantt theo tuần.
4. WBS tree editor: mã hiển thị ngắn `1`, `1.1`, `1.1.1`; tên dài có tooltip; sửa inline hoặc row editor; tổng/validation/lịch do backend trả.

Không tự tính fallback ở frontend. Nếu chưa có WBS/lịch, hiển thị EmptyState và CTA đúng bước.

## 8. Tab Proposal & hồ sơ

Đầu tab là card tải hồ sơ: Word, Excel ước tính, Excel requirement đã điền `○/△/×`, PDF, ZIP. Preview proposal dạng tài liệu/Markdown; tab ngôn ngữ `Tiếng Việt | English | 日本語`; nút `Chỉnh sửa`, `Copy`, `Tải .md`. Chế độ chỉnh sửa là 2 cột soạn/xem trước. `{{QUOTATION}}` được thay bởi bảng giá sau duyệt hoặc `[Presales điền]` trước duyệt.

## 9. Tab Đáp ứng yêu cầu

Filter pill có số đếm: `Tất cả`, `○`, `△`, `×`, `Cần làm rõ`. Bảng cột mã, nội dung, mức, ghi chú. Nút `Điền ○/△/× vào file của khách` gọi export requirement; không ghi đè cột `備考` của khách.

## 10. API mapping và khoảng trống

### Đã có thể dùng

- `GET /api/bids/:id`, `/questions`, `/evaluations`, `/effort`, `/quotation`, `/proposal`, `/wbs`, `/schedule`.
- `PUT /api/bids/:id/wbs`, `/schedule`, `/proposal`.
- `POST /api/bids/:id/pipeline/start`, `/rerun`, approvals.
- Binary exports proposal/estimate/pdf/bundle.

### Cần bổ sung hoặc xác nhận

- Export endpoint cho file requirement gốc đã điền (`requirements.xlsx`) và client `ExportKind` tương ứng.
- Response effort cần trace/factor reasons và phase totals đủ cho card overview.
- Response quotation cần `by_phase`, `onsite_percent`, budget difference và payment milestones nếu chưa có.
- UI dùng endpoint hiện có; không tạo auth endpoint/server.

## 11. Accessibility và trạng thái

Mọi request có loading, empty, error và retry. Button có accessible name; tab dùng `role=tablist/tab/tabpanel`, keyboard focus; table có header; màu không là tín hiệu duy nhất; tooltip tên dài dùng `title` và vẫn hiển thị text rút gọn.

## 12. Tiêu chí nghiệm thu UI

- Desktop 1440×900 và 1280×900 không làm vỡ header, tab, card grid, bảng hoặc Gantt; bảng/Gantt được scroll ngang có chủ đích.
- Mobile: sidebar thu gọn, card chuyển một cột, tab cuộn ngang, thao tác vẫn dùng được bằng bàn phím.
- Mọi enum hiển thị qua bảng nhãn tiếng Việt; không render trực tiếp status/contract enum từ API.
- Giá nội bộ hiển thị ở tab Kế hoạch & báo giá; proposal/export trước duyệt dùng `[Presales điền]`.
- Screenshot từng tab và trang chính được lưu dưới `docs/ui_current/`; `ui_compare.md` phải ghi chênh lệch theo ảnh reference và trạng thái sửa.
- `npm run build` và `npm run test` pass; Preview chạy được với LLM mock trước khi kết luận hoàn tất.
