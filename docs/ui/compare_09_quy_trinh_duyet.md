# So sánh Màn 9 — Quy trình & phê duyệt

## Phạm vi và môi trường

- Vai trò: tester + frontend follow-up, Đợt 3.
- Môi trường: Preview local của project, `LLM_PROVIDER=mock`.
- Hồ sơ kiểm tra: hồ sơ mẫu Nhật `#97`, trạng thái cuối `waiting_tech_approval` sau parse/confirm, pipeline và trả lời 2 vòng câu hỏi.
- Kích thước mục tiêu: `1440×900` theo review UI.
- Ngày kiểm tra: 2026-10-11.
- Follow-up đã sửa một lỗi UI xác định được từ source: bỏ header lồng trong `ApprovalsPage`.

## Kết quả tổng hợp

| Hạng mục | Kết quả | Mức | Evidence / ghi chú | Đã sửa |
|---|---|---:|---|---|
| Ba thẻ độc lập | **Pass source; browser Blocked** | - | `ApprovalsPage` có `Duyệt kỹ thuật`, `Duyệt giá`, `Lịch sử & phiên bản`; chưa thể xác nhận layout trực quan vì Chromium không khởi chạy. | Có; giữ 3 thẻ và bỏ header lồng bên dưới. |
| Tóm tắt kỹ thuật | **Pass qua API** | - | Hồ sơ Nhật `#97`: solution direction `rag`, 36/36 requirements evaluated, effort midpoint `434.7`, schedule warning có giá trị, questions đã trả lời. | Có; giữ mapping API hiện tại. |
| Gate duyệt giá | **Pass qua API** | CAO | POST price approval trên hồ sơ Nhật `#97` trước technical approval trả HTTP `409`, mã `STATE_CONFLICT`, thông báo `Hồ sơ chưa qua duyệt kỹ thuật`. | Có; nút giá vẫn khóa trước duyệt kỹ thuật, backend vẫn là gate cuối. |
| Validation nhận xét | **Pass qua API; browser Blocked** | TB | Hồ sơ Nhật `#97`: POST technical rejection với nhận xét rỗng trả HTTP `400`, mã `VALIDATION_ERROR`, thông báo bắt buộc có lý do. Browser chưa xác nhận thuộc tính disabled/hiển thị lỗi. | Có; nút `Yêu cầu sửa` và `Từ chối` yêu cầu comment không rỗng. |
| Lịch sử duyệt | **API gọi được; browser Blocked** | TB | Frontend gọi `GET /api/history` rồi lọc theo `bid_id`; timeline hiển thị nhãn tiếng Việt thay vì action code; chưa có browser DOM evidence. | Có; giữ loading/error/empty, lọc theo hồ sơ và map action label. |
| Phiên bản gửi khách | **Gap minh bạch** | TB | Backend chưa có contract danh sách proposal versions; UI hiển thị unavailable thay vì bịa dữ liệu. | Không có thay đổi frontend cần thiết; chờ backend contract. |
| Nút `Bỏ qua` | **Pass source evidence; browser Blocked** | CAO | Source Màn 9 không còn lựa chọn/nhãn `Bỏ qua`. | Có; không thêm lại control này. |
| Loading / empty / error | **Pass source evidence; browser Blocked** | TB | Source có state cho bid, summary queries, history và mutation errors. | Có; giữ các state hiện có. |
| Console errors | **Blocked** | TB | Không thể khởi chạy Chromium để thu console runtime. | Chưa thể xác minh trong môi trường này; không bịa kết quả. |
| Ảnh đối chiếu | **Blocked** | TB | Playwright lỗi vì thiếu Chromium executable; không tạo screenshot giả. | Chưa thể xác minh trực quan; cần tester chạy lại với browser khả dụng. |

## Evidence API thực tế

### Hồ sơ và summary kỹ thuật

`GET /api/bids/97` trả trạng thái `waiting_tech_approval`, `locked=false`, `customer_language=ja`, `display_currency=JPY`.

Các endpoint summary trả dữ liệu:

- `GET /api/bids/97/evaluations`: hướng `rag`, `36` requirement được đánh giá, `0` câu cần làm rõ.
- `GET /api/bids/97/effort`: midpoint total `434.7`; các phase có khoảng effort và factor cho khách Nhật/nhiều requirement.
- `GET /api/bids/97/schedule`: có lịch bắt đầu `2026-10-26`, kết thúc `2027-04-30`, và warning lịch vượt hạn nộp.
- `GET /api/bids/97/questions`: hai vòng câu hỏi tiếng Nhật đã có câu trả lời, không còn câu hỏi mở.
- `GET /api/bids/97/quotation`: currency `JPY`, contract model, contingency và grand total `8,085,806`.
- `GET /api/history`: endpoint lịch sử được frontend lọc theo hồ sơ.


Gọi duyệt giá khi hồ sơ Nhật `#97` chưa duyệt kỹ thuật:

```text
HTTP 409
code: STATE_CONFLICT
message: Hồ sơ chưa qua duyệt kỹ thuật
```

Đây là bằng chứng gate backend hoạt động. Browser-level disabled state chưa được xác nhận do blocker Chromium.

## Browser blocker

Playwright không chạy được vì môi trường thiếu executable:

```text
BrowserType.launch: Executable doesn't exist at
/home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell
```

Do đó không có ảnh thật trong `docs/ui_v3/` và không có kết luận trực quan về pixel/layout, text overflow, click button hoặc console runtime. Không tạo ảnh placeholder.

## Đối chiếu với ảnh mẫu và phân loại

Không thể kết luận các sai lệch hình ảnh của `ui_reference/09_quy_trinh_duyet.png` so với Preview vì browser bị Blocked. Các điểm đã có evidence source/API được đánh giá như sau:

- **CAO:** gate duyệt giá được backend bảo vệ; không phát hiện đường bypass qua API; UI tiếp tục khóa nút trước technical approval.
- **CAO:** lựa chọn `Bỏ qua` đã được loại khỏi source Màn 9.
- **TB:** header lồng trong tab đã được loại khỏi `ApprovalsPage`; phần header chung còn lại do `BidDetailPage` quản lý.
- **TB:** action code trong timeline đã được map sang nhãn tiếng Việt; action không nhận diện được dùng nhãn trung tính `Thay đổi hồ sơ`.
- **TB:** phiên bản gửi khách chưa có backend contract; UI phải tiếp tục hiển thị unavailable minh bạch.
- **TB:** browser QA cho layout, nút, validation và console bị Blocked, cần chạy lại trong môi trường có Chromium; đây không phải lỗi frontend có thể chứng minh bằng source/API.
- **THẤP:** chưa có finding mới có thể kết luận bằng API.

## Đối chiếu yêu cầu follow-up

| Yêu cầu | Trạng thái | Evidence |
|---|---|---|
| Sửa mọi mục CAO/TB actionable thuộc frontend | **Đạt theo source/API** | Gate giá, `Bỏ qua`, comment validation, loading/empty/error, header lồng và nhãn lịch sử tiếng Việt đã được kiểm tra hoặc sửa; không có frontend fix còn lại được chứng minh bằng evidence hiện có. |
| Giữ đúng approval contract | **Đạt** | Không đổi endpoint, role, payload, trạng thái gate hoặc logic lọc history; build/test và API Preview vẫn đạt. |
| Không bịa dữ liệu / screenshot | **Đạt** | Version gap vẫn hiển thị unavailable; không có ảnh placeholder hoặc visual PASS giả. |
| Kiểm tra lại Preview | **Đạt một phần** | Preview health và hồ sơ Nhật `#97` đã kiểm tra; browser visual/click/console bị chặn bởi thiếu Chromium. |
| Không còn blocker có evidence | **Chưa đạt** | Blocker Chromium có evidence thực tế ở mục Browser blocker; backend version-list gap cũng còn trong contract. |

## Kết luận

**CHANGES REQUIRED / BLOCKED — chưa đủ điều kiện DONE theo acceptance của frontend follow-up.** Các mục CAO/TB actionable của frontend đã đạt theo source/API và Preview health; tuy nhiên vẫn còn blocker có evidence: Chromium thiếu executable nên chưa thể hoàn tất ảnh 1440×900, DOM/click và console check. Danh sách phiên bản proposal cũng vẫn chờ backend contract. Cần tester chạy lại browser QA trong môi trường có Chromium trước khi kết luận PASS/DONE.
