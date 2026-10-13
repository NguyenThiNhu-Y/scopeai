# Kiểm tra Đợt 11

Ngày kiểm tra: 2026-10-12

## Automated checks

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| Frontend TypeScript/Vite build | Đạt | `frontend: npm run build` hoàn tất sạch sau sửa contract |
| Frontend unit tests | Đạt | `frontend: npm test -- --run`: 14/14 tests passed sau sửa contract |
| Backend Dot 9 regression | Đạt | `backend: python3 -m pytest -q tests/test_dot9_backend.py`: 7 passed |
| Backend full suite | Đạt | `backend: pytest -q`: toàn bộ test pass; chỉ có cảnh báo deprecation của `httpx`/`starlette` |

## Ma trận test case

| TC-ID | Phạm vi và kỳ vọng chính | Kết quả | Bằng chứng / giới hạn |
|---|---|---|---|
| TC-A01 | Mở Cài đặt và thấy đúng 5 tab tiếng Việt | Blocked | Không chạy được browser; API xác nhận đủ 5 key settings |
| TC-A02 | Công ty: sửa tên công ty và quy tắc đặt tên file, lưu lại | Blocked | Không chạy được thao tác UI; API key `company` có trong response, chưa mutation để tránh thay đổi fixture |
| TC-A03 | Template: hiển thị mẫu Word/Excel, mẫu có sẵn và trạng thái hợp lệ; sửa/lưu | Blocked | API key `templates` có trong response; chưa xác nhận từng trường hoặc thao tác UI |
| TC-A04 | Nội dung chuẩn: chuyển vi/en/ja, sửa và lưu từng nội dung | Blocked | API key `standard_content` có trong response; chưa kiểm tra UI theo từng ngôn ngữ |
| TC-A05 | Case study: thêm/sửa/xóa và lưu lại | Blocked | Không chạy được browser; không tạo screenshot hoặc mutation giả |
| TC-A06 | Tiêu chí Bid/No-bid: tổng khác 100 báo lỗi, tổng 100 lưu được | Pass qua API | Tổng 101 trả HTTP 400; payload 30/40/30 trả HTTP 200 |
| TC-B01 | Hiển thị criteria, weight, suggestion và giữ suggestion ở trạng thái tham khảo | Pass qua API | Criteria 30/40/30; suggestion `source=analysis`, `status=review`; chưa kiểm tra render UI |
| TC-B02 | Chọn và lưu deal stage hợp lệ | Pass qua API | `qualified` trả HTTP 200 và được lưu; UI chưa kiểm tra |
| TC-B03 | Tạo version theo chuỗi 1.0 → 1.1 → 2.0 | Pass qua API | Ba POST liên tiếp trả đúng version; UI chưa kiểm tra |
| TC-B04 | Đánh dấu đã gửi, hiển thị ngày gửi và ghi chú | Pass qua API | PUT trả `sent=true`, có `sent_at`, `sent_note=QA Đợt 11`; UI chưa kiểm tra |
| TC-C01 | Chưa chọn ngôn ngữ thì không cho soạn proposal | Blocked | Không chạy được browser; code đã được kiểm tra qua `ProposalPage` |
| TC-C02 | Chuyển vi/en/ja đổi toàn bộ nội dung, thiếu bản dịch hiện nút dịch | Blocked | API tạo được `en` đủ section; chưa kiểm tra hành vi render/fallback trên UI |
| TC-C03 | Dịch proposal khi thiếu bản dịch | Pass qua API | POST translate `en` trả HTTP 200 và đủ section trong `translations.en` |
| TC-C04 | Mở tài liệu A4 có bìa, mục lục, nội dung và in được | Đạt một phần | API trả metadata A4/cover/TOC/printable; code có overlay/CSS print; chưa mở trang và chưa thao tác in do thiếu browser |

Quy ước: `Pass qua API` chỉ chứng minh contract/backend path của chức năng; không thay thế kiểm thử trực quan trên browser.

## Đối chiếu yêu cầu

| Mục | Kết quả | Ghi chú bằng chứng |
|---|---|---|
| A. 5 tab Cài đặt tiếng Việt | Đạt có điều kiện | `SettingsPage.tsx` có đúng 5 nhãn; API đủ 5 key; chưa mở UI browser |
| A. Công ty: tên và quy tắc file | Đạt có điều kiện | `CompanyEditor` và key `company` đã xác định trong code/API; chưa kiểm tra thao tác nhập/lưu |
| A. Template Word/Excel, mẫu có sẵn, trạng thái hợp lệ | Đạt có điều kiện | `TemplatesEditor` và key `templates` đã xác định; chưa kiểm tra từng loại/trạng thái trên browser |
| A. Nội dung chuẩn vi/en/ja | Đạt có điều kiện | `ContentEditor` có selector ngôn ngữ; key `standard_content` đã xác định; chưa kiểm tra từng luồng UI |
| A. Case study CRUD | Đạt có điều kiện | `CaseStudiesEditor` có thêm, sửa, xóa; chưa chạy UI và chưa kiểm tra persist sau refetch |
| A. Sửa/lưu settings | Đạt có điều kiện | GET/PUT `/api/settings`, object/list payload, loading/error/success; UI mutation chưa được browser kiểm chứng |
| A. Tổng Bid/No-bid = 100 | Đạt có điều kiện | Frontend chặn lưu khi tổng khác 100; backend cũng kiểm tra; UI chưa chạy trực tiếp |
| B. Bid/No-bid approval | Đạt có điều kiện | Code/API có tiêu chí, trọng số, điểm gợi ý, người xác nhận, quyết định và nút Xác nhận; UI chưa kiểm chứng |
| B. Deal stage | Đạt có điều kiện | `updateDealStage` và chọn stage tiếng Việt; UI chưa kiểm chứng |
| B. Phiên bản 1.0 → 1.1 → 2.0 | Đạt có điều kiện | Backend tạo chuỗi; frontend tạo và refetch; UI chưa kiểm chứng |
| B. Ngày gửi và ghi chú | Đạt có điều kiện | API trả `sent_at`, `sent_note`; UI có input/hiển thị theo code nhưng chưa kiểm chứng browser |
| C. Chọn ngôn ngữ trước khi soạn | Đạt có điều kiện | Code không cho chỉnh sửa trước khi chọn ngôn ngữ; UI chưa kiểm chứng |
| C. Translations/fallback/dịch | Đạt có điều kiện | Code dùng `translations`, báo section thiếu và gọi `translateProposal`; UI fallback chưa kiểm chứng |
| C. Tài liệu A4 | Đạt một phần | Code có bìa, mục lục, nội dung, CSS in A4 và nút In tài liệu; metadata API đã kiểm chứng, nhưng chưa kiểm tra trực quan/thao tác in vì thiếu browser |
| Preview/API health | Đạt | Preview backend/frontend đang Up; `GET /api/health` trả `200`, database `ok`, `llm_provider=mock` |
| Preview settings contract | Đạt qua API | `GET /api/settings` trả đủ 5 key: `company`, `templates`, `standard_content`, `case_studies`, `bid_no_bid` |
| Preview version sent metadata | Đạt qua API | Tạo version `1.0`, `1.1`, `2.0`; đánh dấu `1.0` gửi trả HTTP 200 với `sent=true`, có `sent_at` và `sent_note` đúng payload |
| Preview/browser evidence | Bị chặn một phần | API đã kiểm chứng trên Preview; Playwright không khởi động được vì thiếu browser executable. Không tạo screenshot giả. |
| Preview health | Đạt | `GET /api/health` trả HTTP 200; `database=ok`, `llm_provider=mock`. |
| A. Settings API contract | Đạt một phần | `GET /api/settings` trả HTTP 200 và đủ 5 key Dot 9: `company`, `templates`, `standard_content`, `case_studies`, `bid_no_bid`; chưa thể kiểm tra thao tác trực tiếp trên UI do thiếu browser. |
| A. Bid/No-bid invalid total | Đạt | `PUT /api/bids/80/bid-qualification` với tổng 101 trả HTTP 400, message `Tổng trọng số Bid/No-bid phải bằng 100`; payload hiện tại được restore thành công HTTP 200. |
| B. Bid/No-bid suggestions | Đạt qua API | `GET /api/bids/80/bid-qualification` trả criteria 30/40/30 và suggestions có `source=analysis`, `status=review`; không tự có decision/confirmer. |
| B. Deal stage | Đạt một phần | `PUT /api/bids/80/deal-stage` với `qualified` trả HTTP 200 và giá trị được lưu. API schema không nhận `null`, nên stage rỗng ban đầu của fixture không thể khôi phục qua API; không đánh giá UI. |
| B. Version sequence and send metadata | Đạt qua API | Tạo trên bid 80 trả lần lượt `1.0`, `1.1`, `2.0`; đánh dấu `1.0` gửi trả HTTP 200 với `sent_at` và `sent_note=QA Đợt 11`; danh sách phản hồi đủ metadata. |
| C. Proposal translation | Đạt qua API | `GET /api/bids/80/proposal` trả `translations={}`; `POST /api/bids/80/proposal/translate` language `en` trả HTTP 200 và thêm đủ section `en`. |
| C. Proposal A4 metadata | Đạt qua API | Proposal response trả `document.page_size=A4`, `cover=true`, đủ `table_of_contents`, `printable=true`; không thể mở/kiểm tra giao diện in do thiếu browser. |

## Ghi chú

- Sau review, endpoint đánh dấu gửi nhận body `{note}` và lưu vào `proposal_versions.sent_note`.
- Database cũ được bổ sung migration nullable cho `sent_note` tương tự `sent_at`.
- Chỉnh sửa Proposal bị giới hạn ở ngôn ngữ gốc để không ghi đè nhầm bản dịch vì backend hiện không có endpoint cập nhật translation riêng.
- Kiểm thử API đã tạo dữ liệu bằng chứng trên bid fixture `80`: các version `1.0`, `1.1`, `2.0`, đánh dấu `1.0` đã gửi với ghi chú `QA Đợt 11`, và bản dịch `en`. Đây là dữ liệu mô phỏng, không phải số liệu khách hàng thật.
- Kiểm thử deal stage đã đặt bid `80` sang `qualified`; request khôi phục `null` bị backend từ chối HTTP 400 vì schema chỉ nhận 6 stage hợp lệ. Trạng thái này cần được reviewer cân nhắc khi reset fixture.
