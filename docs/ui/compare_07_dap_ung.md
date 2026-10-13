# Đối chiếu Màn 7 — Đáp ứng yêu cầu

Ngày kiểm tra: 2026-10-11  
Vai trò: tester  
Môi trường: Preview stack, `LLM_PROVIDER=mock`, viewport yêu cầu `1440x900` chưa thể khởi chạy browser

## Kết luận

**BLOCKED một phần — frontend follow-up đã hoàn tất các lỗi có thể sửa và xác nhận bằng code**

API của hồ sơ mẫu tiếng Nhật `#92` trả đủ 36 requirement và endpoint export trả file XLSX thật. Tuy nhiên browser Playwright không khởi chạy được vì môi trường thiếu Chromium executable, nên chưa có bằng chứng DOM, thao tác nút, screenshot 1440x900 hoặc console runtime. Không đánh dấu các phần UI đó là Pass khi chưa quan sát được trong browser.

Các mục CAO/TB còn lại trong bảng bên dưới đều được giữ ở trạng thái `BLOCKED` vì thiếu browser evidence hoặc phụ thuộc API gap; không có lỗi CAO/TB nào đã được xác nhận bằng code mà chưa xử lý trong follow-up này.

## Bằng chứng runtime

| Hạng mục | Kết quả | Evidence |
|---|---|---|
| Preview health | PASS | `GET http://127.0.0.1:3000/api/health` trả `200`, `status=ok`, `llm_provider=mock`, `database=ok` |
| Hồ sơ Nhật có dữ liệu | PASS | `GET /api/bids/92/evaluations` trả `stats.total=36`, `evaluated=36`, `○=36`, `△=0`, `×=0`, `needs_clarification=0`; nội dung requirement là tiếng Nhật |
| API export bảng đáp ứng | PASS | `GET /api/bids/92/exports/requirements.xlsx` trả `200`, `content-type` XLSX, `content-disposition=ja_requirements.xlsx`, `content-length=7514`; file được nhận diện Microsoft Excel 2007+ |
| SPA route / HTML shell | PASS | `GET /bids/92?tab=evaluations` trả `200 text/html`, HTML shell có title `Trợ lý dự thầu`; đây không phải bằng chứng DOM sau khi React render |
| Browser DOM / thao tác UI | BLOCKED | Playwright không tạo được browser context vì thiếu Chromium: `Executable doesn't exist ... chromium_headless_shell-1187/.../headless_shell` |
| Screenshot thật 1440x900 | BLOCKED | Không thể chụp vì browser không khởi chạy; không tạo ảnh giả |
| Console runtime | BLOCKED | Không có browser session để thu console |

## Đối chiếu với ảnh mẫu và prompt Màn 7

| Tiêu chí | Trạng thái | Mức độ | Evidence / nhận xét | Đã sửa |
|---|---|---|---|---|
| Hàng lọc Tất cả / Đạt / Một phần / Không đạt / Cần làm rõ có số đếm | BLOCKED | TB | Component hiện có các bộ lọc và API có dữ liệu 36 mục; chưa xác minh render và click trên browser | Đã giữ bộ lọc và bổ sung kiểm tra accessibility; browser blocker còn |
| Bảng gồm mã, nội dung, đánh giá, thành phần, ghi chú | BLOCKED | TB | API có mã, nội dung, rating, note; chưa xác minh DOM/bố cục/chữ tràn | Đã thêm `caption` và `scope=col`; bố cục vẫn cần browser |
| Requirement tiếng Nhật hiển thị đúng | BLOCKED | TB | API trả nội dung tiếng Nhật; chưa xác minh font, encoding và layout ở 1440x900 | Không có lỗi code xác nhận; cần browser |
| Badge màu cho đánh giá | BLOCKED | TB | API trả 36 rating `○`; chưa quan sát badge thực tế | Không đổi vì component đã có mapping màu; cần browser |
| Nút `Điền ○/△/× vào file Excel của khách` | BLOCKED | CAO | Endpoint export hoạt động qua API, nhưng chưa xác minh nút xuất hiện, loading, download và lỗi khi click | Đã khớp nhãn prompt, thêm `aria-label`, trạng thái `aria-busy/status`, và giữ object URL đến tick tiếp theo; click UI vẫn cần browser |
| Nút `Tải bảng đáp ứng` | BLOCKED | CAO | Component có nút và endpoint export hoạt động, nhưng chưa xác minh click UI; hai nút hiện dùng cùng endpoint `GET /api/bids/{id}/exports/requirements.xlsx` | Đã hiển thị trạng thái tạo file nhất quán và nhãn accessibility; click UI vẫn cần browser |
| Chọn ngôn ngữ ghi chú | BLOCKED / API GAP | TB | Selector trong component đang disabled; backend chỉ chọn theo `customer_language`, chưa nhận `note_language` theo `docs/ui/api_gaps.md` | Giữ disabled, bỏ state không có tác dụng; không giả lập API |
| Empty state khi không có requirement | BLOCKED | TB | Component có thông điệp hướng dẫn đính kèm Excel; chưa kiểm tra bằng browser với hồ sơ không có dữ liệu | Không đổi; cần browser |
| Loading khi export | BLOCKED | TB | Component có trạng thái `Đang tạo file…`; chưa quan sát được khi click | Đã bổ sung `role=status`, `aria-live` và `aria-busy`; cần browser |
| Error khi export lỗi | BLOCKED | TB | Component có `role=alert` và thông báo tiếng Việt; chưa tạo được lỗi UI để xác minh | Giữ xử lý lỗi hiện có; cần browser |
| Chữ tràn / responsive ở 1440x900 | BLOCKED | THẤP | Không có browser screenshot | Chưa thể kết luận |
| Console errors | BLOCKED | CAO | Không thể thu console do thiếu Chromium | Chưa thể kết luận |

## API/contract gaps cần giữ nguyên

- Export endpoint hiện là `GET /api/bids/{id}/exports/requirements.xlsx`, không nhận lựa chọn ngôn ngữ từ frontend.
- Graph/source evidence: `requirements_xlsx` gọi `render_requirement_workbook(session, bid_id, bid.customer_language)`; ngôn ngữ được lấy từ hồ sơ, không từ selector frontend.
- API export đã được kiểm tra với hồ sơ `#92`, không phải bằng chứng rằng cả hai nút UI có hành vi riêng biệt.
- Không sửa code trong node tester và không đánh dấu selector ngôn ngữ là hoạt động.
- Cần backend bổ sung `note_language` và test cho `vi` / `en` / `ja` trước khi frontend có thể bật selector.

## Verification sau frontend follow-up

- `frontend`: `npm run build` PASS (`tsc -b && vite build`).
- `frontend`: `npm run test` PASS, 1 test file và 6 tests passed.
- Không có browser session nên chưa thể kết luận DOM, click thật, download từ UI, screenshot 1440x900, responsive hoặc console runtime.
- Không tạo screenshot giả và không đánh dấu các mục browser-dependent là Pass.

## Blocker và hành động tiếp theo

1. Cung cấp Chromium executable cho môi trường Preview/browser testing, sau đó chạy lại Màn 7 ở viewport `1440x900`.
2. Dùng hồ sơ Nhật `#92` để xác minh DOM, bộ lọc, badge, hai nút export, loading/error và console.
3. Kiểm tra riêng empty state bằng một hồ sơ không có requirement.
4. Không tạo screenshot thay thế khi browser chưa chạy được.
