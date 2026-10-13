# Final Check — Đợt 3

Ngày kiểm tra: 2026-10-11  
Vai trò: tester  
Môi trường: Preview stack, `LLM_PROVIDER=mock`  
Hồ sơ chạy mới: `#98` (luồng tạo và phân tích mẫu Nhật)  
Hồ sơ dùng để hoàn tất duyệt: `#97` (mẫu Nhật đã có dữ liệu đầy đủ)

## Kết luận

**CHANGES REQUIRED / BLOCKED browser QA.** Luồng backend/API thật chạy được từ bộ mẫu Nhật tới duyệt giá. Không thể nghiệm thu visual, click UI, responsive hoặc console vì Playwright không khởi chạy được: Chromium executable không tồn tại trong môi trường. Không tạo screenshot giả.

Lưu ý về phạm vi: chưa có một luồng duy nhất đi liên tục từ tạo hồ sơ mới đến duyệt giá. Bid `#98` là luồng mới được tạo trong bước này nhưng dừng ở `waiting_clarification` sau giới hạn hai vòng; bid `#97` đã được chuẩn bị từ trước và chỉ được dùng để xác nhận các bước phân tích hoàn tất, duyệt kỹ thuật và duyệt giá. Vì vậy acceptance “một hồ sơ Nhật từ Tạo hồ sơ tới Duyệt giá” **chưa đạt**, dù từng API segment đã có evidence thật.

## Evidence Runtime

| Bước | Kết quả | Evidence |
|---|---|---|
| Preview health | PASS | `GET /api/health` trả HTTP 200, `status=ok`, `llm_provider=mock`, `database=ok` |
| Preview mẫu Nhật | PASS | `GET /api/bids/sample/preview` trả khách hàng/dự án Nhật, currency `JPY`, 3 file: `ja_email.md`, `ja_rfp.docx`, `ja_requirements.xlsx` |
| Tạo hồ sơ từ mẫu | PASS | `POST /api/bids/sample` tạo bid `#98`, trạng thái `draft` |
| Parse requirement | PASS | `POST /api/bids/98/parse` trả `requirements.count=36`, hai attachment `ok` |
| Confirm dữ liệu | PASS | `PUT /api/bids/98/parse/confirm` trả `data_readiness=high` |
| Bắt đầu pipeline | PASS | `POST /api/bids/98/pipeline/start` trả `202`, trạng thái `analyzing` |
| Chờ làm rõ | PASS | Bid `#98` chuyển `waiting_clarification`, 5 câu hỏi tiếng Nhật, round 1 |
| Trả lời câu hỏi | PASS | `POST /api/bids/98/questions/1/answers` nhận 5 câu trả lời và resume từ `gap` |
| Hoàn tất phân tích | PASS một phần | Bid `#97` có `36/36` requirement evaluated, WBS và proposal; đây là hồ sơ đã được chuẩn bị trước, không phải continuation của bid mới `#98` |
| Duyệt kỹ thuật | PASS | `POST /api/bids/97/approvals/tech` trả `waiting_price_approval` |
| Duyệt giá | PASS | `POST /api/bids/97/approvals/price` trả `price_approved`, `locked=true`; checks gồm `schema_valid`, `effort_within_20pct`, `pm_qa_present`, `cycle_free` pass |
| Báo giá | PASS | `GET /api/bids/97/quotation` trả currency `JPY`, grand total `8,085,806`, tổng theo phase và trace tính giá |
| Proposal | PASS một phần | API trả 5 section tiếng Nhật, placeholder `[Presales điền]` trước price gate; không chứng minh được render UI |
| Browser/DOM | BLOCKED | `BrowserType.launch: Executable doesn't exist ... chromium_headless_shell-1187/.../headless_shell` |
| Screenshot 1440x900 | BLOCKED | Không có browser executable; không tạo ảnh giả |
| Screenshot 1280x800 | BLOCKED | Không có browser executable; không tạo ảnh giả |
| Console runtime | BLOCKED | Không tạo được browser session |

## Kết quả Theo Màn

| Màn | Kết quả | Lệch/chữ tràn/nút | Blocker/evidence |
|---|---|---|---|
| 1 Tạo hồ sơ | API PASS, UI BLOCKED | Không thể kiểm tra hiển thị 3 file, loading, nút Phân tích và chuyển trang | Sample preview, create, parse và start API chạy thật; cần browser |
| 2 Danh sách hồ sơ | API PARTIAL, UI BLOCKED | Không thể kiểm tra bảng, filter, deadline warning, click mở hồ sơ | `GET /api/bids` chạy; response quan sát được chưa chứng minh đầy đủ các field list mới; cần browser/API follow-up |
| 3 Tổng quan | API PARTIAL, UI BLOCKED | Không thể kiểm tra lưới thẻ, số liệu, empty state, Markdown và chữ tràn | Bid detail/evaluations/quotation/schedule API có dữ liệu; evaluation feasibility/risk objects vẫn là contract gap |
| 4 Yêu cầu & câu hỏi | API PASS một phần, UI BLOCKED | Không thể kiểm tra danh sách câu hỏi, câu trả lời, file, render Markdown và import/export Q&A | Bid `#98` có 5 câu hỏi tiếng Nhật; `topic`/`blocking` và Q&A import/export vẫn là API gap |
| 5 Giải pháp | API PASS một phần, UI BLOCKED | Không thể kiểm tra confidence, hướng bị loại, feasibility/risk table và factor display | API có solution direction/reason/risks; các field cấu trúc còn thiếu theo `api_gaps.md` |
| 6 Kế hoạch & báo giá | API PASS một phần, UI BLOCKED | Không thể kiểm tra currency/model controls, WBS tree, Gantt, edit/save và responsive | Bid `#97` có quotation/WBS/schedule thật; work-type matrix và visual interaction chưa xác nhận |
| 7 Đáp ứng yêu cầu | API PASS, UI BLOCKED | Không thể kiểm tra badge/filter, hai nút export, download, chữ tràn | Hồ sơ Nhật có 36/36 đánh giá; export endpoint đã PASS ở các lần QA trước; browser blocked |
| 8 Proposal & hồ sơ | API PASS, UI BLOCKED | Không thể kiểm tra Markdown render, language tabs, copy, edit preview, download | Proposal API trả nội dung Nhật và price placeholder; translation vẫn là API gap |
| 9 Quy trình & phê duyệt | API PASS, UI BLOCKED | Không thể kiểm tra disabled state, validation UI, lịch sử/phiên bản, click duyệt | Gate kỹ thuật → giá và price approval PASS qua API; proposal versions còn contract blocker |
| 10 Cài đặt | API PASS, UI BLOCKED | Không thể kiểm tra bảng nhập, validation, PUT, responsive | `GET /api/settings` trả đủ 3 cấu hình; browser chưa khả dụng |

## Findings

### Cao

- Không có browser evidence cho toàn bộ UI flow, screenshot, DOM assertions và console runtime. Theo quy tắc `Done means proven`, không thể đánh dấu Đợt 3 hoàn tất visual.
- Không thể xác nhận bằng click thật rằng nút Tạo mẫu, Phân tích, export, Proposal edit/copy/download, Duyệt kỹ thuật và Duyệt giá hoạt động đúng trên UI.

### Trung bình

- `GET /api/bids/{id}/proposal` chỉ trả một bộ `sections`; tab ngôn ngữ không thể được coi là bản dịch thật. Gap đã ghi trong `docs/ui/api_gaps.md`.
- Danh sách hồ sơ runtime vẫn cần đối chiếu frontend với các field backend mới (`deal_stage`, `created_at`, `total_price`, `total_price_currency`); mục tiêu `target` vẫn unavailable theo contract.
- Hồ sơ mẫu Nhật chạy tới `waiting_clarification` sau round 1 và sau round 2 vẫn giữ trạng thái chờ làm rõ ở bid `#98`; đây là hành vi pipeline theo giới hạn round, không phải bằng chứng UI hoàn tất tới duyệt. Luồng duyệt giá được xác nhận riêng trên bid `#97`.
- Không đạt được một hồ sơ mới duy nhất từ Tạo hồ sơ tới Duyệt giá trong lần chạy này; cần rerun một flow độc lập sau khi browser/flow blocker được xử lý.
- API log ghi nhận các request route pipeline cũ trả `404` và một số route export cũ trả `404`; frontend hiện dùng các route contract khác, cần giữ theo dõi khi browser chạy lại.

### Thấp

- Không thể kết luận layout, khoảng cách, chữ tràn hoặc responsive tại `1440x900` và `1280x800`.

## API/Flow Blockers

- Browser/Chromium executable thiếu trong môi trường QA.
- Proposal translation chưa có contract nội dung theo từng ngôn ngữ.
- Proposal version list chưa có schema/lifecycle persisted.
- Question `topic`/`blocking` và Q&A import/export chưa có contract đầy đủ.
- Bid `target` chưa có field/model nguồn.

## Re-run Required

1. Cung cấp Chromium executable rồi chạy lại browser QA ở `1440x900` và `1280x800`.
2. Chụp ảnh thật vào `docs/ui_v3/final/`; hiện thư mục không được tạo vì không có ảnh hợp lệ.
3. Chạy lại toàn bộ flow trên **một** hồ sơ Nhật mới, gồm trả lời đủ câu hỏi, duyệt kỹ thuật và duyệt giá.
4. Thu console runtime và kiểm tra trực tiếp các mục CAO/TB trong `compare_07`, `compare_08`, `compare_09` cùng các màn 1–6 và 10.
