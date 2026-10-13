# Biên bản review: Presales Bidding Assistant (sau Quality Gate G4)

| Mục | Nội dung |
|---|---|
| Sản phẩm | Presales Bidding Assistant (build trên VibeFlow) |
| Phiên bản review | Sau mốc M8 và Quality Gate G4 |
| Ngày review | 10/10/2026 |
| Người review | `<Họ tên>` (vai trò: Presales lead / Reviewer kỹ thuật) |
| Phạm vi | Toàn bộ backend, frontend, bảng chuẩn, dữ liệu mẫu, tài liệu `docs/quality/` |
| Phương pháp | Đọc code theo luồng nghiệp vụ; chạy lại bộ test backend; đối chiếu với SRS, AGENTS.md và kỳ vọng của một hồ sơ dự thầu cho khách Nhật |

## 1. Kết luận

**Chưa đạt để demo. Cần sửa các mục mức Nghiêm trọng (R-01 → R-08) trước khi chạy lại Quality Gate.**

Khung sản phẩm được dựng tốt và đúng hướng thiết kế. Tuy nhiên toàn bộ kiểm thử đang dựa trên LLM giả lập (mock): mock luôn trả dữ liệu đúng định dạng nên test xanh, trong khi logic nghiệp vụ và prompt của các bước AI còn mỏng. Sản phẩm chưa được chạy với LLM thật và chưa được kiểm thử trên trình duyệt.

## 2. Điểm làm tốt

- Kiến trúc rõ ràng: FastAPI + React, một cổng LLM duy nhất có chế độ mock, cấu hình qua biến môi trường.
- Tiến độ từng bước hiển thị realtime (SSE); luồng hỏi làm rõ có dừng và chạy tiếp.
- WBS 3 cấp sửa được trên web; tổng và lịch tự tính lại; lịch có xét ngày nghỉ.
- Trang Cài đặt sửa bảng chuẩn có kiểm tra hợp lệ, có lịch sử thay đổi; hồ sơ đã duyệt giữ nguyên số liệu (snapshot).
- Cổng duyệt giá hoạt động; có kiểm tra tự động "LLM không sinh con số".

## 3. Phát hiện

Mức độ: **Nghiêm trọng** = chặn việc dùng thật · **Cao** = con số hoặc nghiệp vụ sai · **Trung bình** = chất lượng đầu ra và trải nghiệm.

### 3.1 Nghiêm trọng

| ID | Hạng mục | Mô tả | Vị trí | Đề xuất |
|---|---|---|---|---|
| R-01 | Cổng LLM | Khi dùng LLM thật, hệ thống không gửi cấu trúc JSON (schema) cho model, nên model phải tự đoán tên trường và các bước sẽ sai định dạng. Lỗi từ provider (JSON hỏng, 429, 5xx) không được thử lại | `llm/openai_compat_client.py`, `llm/gateway.py` | Gửi schema trong system message, thử lại cả lỗi provider, thêm script chạy thử trọn luồng với LLM thật |
| R-02 | Đầu vào | Nội dung file RFP đính kèm (PDF/DOCX) không được đưa vào bước phân tích; AI chỉ đọc ô email | `pipeline/steps/b1_intake.py` | Đưa văn bản đã trích (đã che thông tin cá nhân, có giới hạn độ dài) vào bước phân tích và bước hỏi làm rõ |
| R-03 | Proposal | Bước viết proposal chỉ nhận ngôn ngữ khách, không có yêu cầu, giải pháp, WBS, rủi ro, nên proposal chung chung | `pipeline/steps/b6_proposal.py` | Truyền đủ ngữ cảnh; đặt dòng `{{QUOTATION}}` cho phần giá để code điền sau duyệt |
| R-04 | Chọn giải pháp | Bước chọn giải pháp chỉ đọc email thô, không dùng kết quả phân tích và câu trả lời làm rõ | `pipeline/steps/b4_solution.py` | Truyền kết quả phân tích, câu hỏi/câu trả lời, tóm tắt requirement; bắt buộc nêu lý do loại từng hướng |
| R-05 | Đánh giá requirement | Bước đánh giá chạy trước khi chọn giải pháp (không biết hướng giải pháp); prompt chỉ một câu; mỗi lô lại gửi toàn bộ requirement | `services/evaluation_service.py` | Chạy sau bước chọn giải pháp; mỗi lô chỉ gửi requirement của lô; định nghĩa rõ ◎/○/△/× |
| R-06 | Đọc file Excel | Tiêu đề bắt buộc ở dòng 1, cột nội dung phải đặt đúng tên cố định. File 別紙1 thực tế (có sheet bìa, tiêu đề ở dòng 3, cột `要件内容`) sẽ đọc ra 0 requirement | `parsers/excel.py`, `parsers/requirements.py` | Tự tìm dòng tiêu đề trong 10 dòng đầu, nhận diện cột theo từ khóa đa ngôn ngữ, bỏ qua sheet bìa |
| R-07 | Phạm vi MVP | Chưa có chức năng điền ○/△/× và ghi chú vào đúng file Excel requirement của khách, dù đã chốt trong MVP | (chưa có) | Ghi vào file gốc, giữ định dạng, không ghi đè cột 備考 của khách |
| R-08 | Kiểm thử | 2 test đang fail; báo cáo Quality Gate "toàn bộ PASS" đã lỗi thời. Nguyên nhân: phần đăng nhập/phân quyền được thêm dở dang, trái luật 9 của AGENTS.md | `tests/test_bids.py`, `tests/test_pipeline_sse.py` | Gỡ phần xác thực (ngoài phạm vi MVP), sửa test, ghi GATE-01 là "chấp nhận rủi ro" |

### 3.2 Cao

| ID | Hạng mục | Mô tả | Vị trí | Đề xuất |
|---|---|---|---|---|
| R-09 | Bảng effort | Số liệu quá nhỏ: hướng RAG cả 3 giai đoạn chỉ 38–58 man-day, không phù hợp RFP doanh nghiệp | `reference/effort.yaml` | Hiệu chỉnh số giả lập sát thị trường cho dự án quy mô vừa, team offshore VN |
| R-10 | Hệ số effort | Hệ số được nhận diện bằng cách dò chuỗi trong email: hầu như email nào có chữ "yêu cầu"/"要件" cũng bị cộng hệ số "nhiều requirement"; có chữ "lớn"/"triệu" thì cộng "dữ liệu lớn" | `services/factor_engine.py` | Lấy từ kết quả phân tích và số requirement thực tế (ngưỡng đặt trong YAML); hiển thị lý do từng hệ số |
| R-11 | Báo giá | Khách Nhật bị tính toàn bộ theo đơn giá onsite; overhead PM 10% vẫn cộng dù WBS đã có task PM (tính hai lần); chưa chia theo giai đoạn | `services/quotation_engine.py` | Đơn giá pha trộn offshore/onsite theo tỉ lệ; bỏ overhead trùng; chia PoC/MVP/Production |
| R-12 | Ngân sách khách | Chênh lệch với ngân sách khách đã được tính nhưng không hiển thị trên giao diện | `pages/QuotationPage.tsx` | Hiển thị ngân sách, giá chào và % chênh lệch |

### 3.3 Trung bình

| ID | Hạng mục | Mô tả | Vị trí | Đề xuất |
|---|---|---|---|---|
| R-13 | Word proposal | Mục lục cố định 3 dòng, không có phụ lục WBS/lịch, giá in dạng số thô | `exporters/proposal_docx.py` | Bìa, mục lục, đủ mục proposal, phụ lục; định dạng tiền tệ |
| R-14 | Excel ước tính | Sheet WBS chỉ có mã/tên/man-day; sheet báo giá chỉ một ô | `exporters/estimate_xlsx.py` | Thêm giai đoạn, vai trò, công thức tổng theo giai đoạn; báo giá theo vai trò × giai đoạn |
| R-15 | Dữ liệu mẫu | Chỉ 5 requirement tiếng Việt, dùng chung cho cả mẫu tiếng Nhật; không có file RFP | `sample_data/` | Bộ mẫu tiếng Nhật hư cấu đầy đủ: email, RFP .docx, 別紙1 khoảng 30–40 dòng |
| R-16 | Giao diện | Hiển thị mã trạng thái thô (`waiting_tech_approval`, `fixed_price`); luồng trải trên nhiều trang rời | `pages/*.tsx` | Nhãn tiếng Việt; trang hồ sơ dạng tab |

### 3.4 Giao diện (kiểm thử trên trình duyệt, LLM giả lập)

Đã chạy app và chụp toàn bộ 14 màn hình (thư mục `ui_hien_tai/`), so với giao diện chuẩn mong muốn (thư mục `ui_reference/`).

**Nhận xét chung:** giao diện hiện tại là một chuỗi trang rời, mỗi trang một chức năng, trông như công cụ kỹ thuật nội bộ. Người dùng phải bấm qua 8 nút để xem đủ một hồ sơ, không có màn hình nào cho thấy "bức tranh toàn cảnh". Giao diện mong muốn là một **bàn làm việc của hồ sơ**: đầu trang gọn với trạng thái, thanh tiến trình 8 bước, các tab, và tab Tổng quan tóm tắt mọi thứ trên một màn hình.

| ID | Mức | Màn hình | Mô tả | Đề xuất |
|---|---|---|---|---|
| UI-01 | Nghiêm trọng | Hồ sơ mẫu | Nạp mẫu tiếng Nhật rồi phân tích: bước "Đánh giá mức đáp ứng" lỗi (`Không có fixture 'good' cho schema EvaluationBatch`), hồ sơ treo mãi ở "đang phân tích", giao diện không báo lỗi rõ ràng | Sửa mock; khi một bước lỗi thì hồ sơ chuyển "Lỗi", hiện thông báo và nút "Chạy lại từ bước này" |
| UI-02 | Nghiêm trọng | Báo giá | Trước khi duyệt giá, trang Báo giá **ẩn hoàn toàn số tiền**, nên manager không có gì để duyệt. Cổng giá chỉ nên áp dụng cho tài liệu gửi khách, không phải cho người dùng nội bộ | Luôn hiện báo giá đầy đủ cho người dùng nội bộ; chỉ proposal/file xuất ra mới thay bằng "[Presales điền]" |
| UI-03 | Nghiêm trọng | Toàn app | Bản mã nguồn tải về không build được: các trang Cài đặt, Lịch sử, Xuất file gọi hàm không có trong `api/client.ts`, `api/types.ts` (2 file này cũ hơn các trang) | Đồng bộ lại mã nguồn, chạy `npm run build` trên bản sạch |
| UI-04 | Cao | Chi tiết hồ sơ | Không có tab, không có tab Tổng quan; 8 nút điều hướng rời (Phân tích, Xem hướng giải pháp, Xem WBS…); nội dung email thô chiếm nửa trang | Trang hồ sơ dạng tab theo `ui_reference/03–09`; email gốc thu gọn mặc định |
| UI-05 | Cao | Chi tiết hồ sơ | Không có thanh tiến trình các bước nằm ngang; nhãn "Chưa triển khai ở M3" vẫn hiện trên bước đã hoàn tất | Thanh 8 bước ngang dưới tiêu đề, trạng thái đúng |
| UI-06 | Cao | Lịch | Lịch không tự tính sau khi có WBS; người dùng phải tự nhập headcount (mặc định 0) và ngày bắt đầu | Tự tính lịch mặc định ngay sau WBS (số người gợi ý theo effort); form chỉ để điều chỉnh |
| UI-07 | Cao | Proposal | Proposal là 5 ô nhập văn bản thô, mỗi ô một câu; không xem trước dạng tài liệu, không có tab ngôn ngữ, không có nút tải | Xem trước Markdown như tài liệu, nút Chỉnh sửa / Copy / Tải; tab Tiếng Việt / English / 日本語 |
| UI-08 | Trung bình | Cổng duyệt, Báo giá | Hiển thị mã thô: `waiting_price_approval`, `fixed_price`, `Việt Nar` (bị cắt chữ) | Nhãn tiếng Việt, huy hiệu màu; đầu trang có huy hiệu KT ✓ / Giá ✓ |
| UI-09 | Trung bình | WBS | Mã task bị xuống dòng (`WBS-001-` / `01-01`), cột thao tác chiếm chỗ; chưa có Gantt cạnh bảng | Mã ngắn kiểu 1.1.1, sửa trực tiếp trong ô, thanh tổng theo giai đoạn × vai trò, Gantt theo tuần |
| UI-10 | Trung bình | Toàn app | Trang chủ chỉ hiện trạng thái hệ thống, không phải nơi bắt đầu công việc; thiếu chế độ tối dễ thấy; chữ và khoảng cách chưa thống nhất | Trang chủ = Tạo hồ sơ (ô nhập lớn, bộ hồ sơ mẫu, đính kèm); bảng màu và font theo mục 3.5 |

### 3.5 Chuẩn giao diện mong muốn (tham chiếu `ui_reference/`)

- **Bố cục:** menu trái gọn (Tạo hồ sơ nổi bật dạng nút, Hồ sơ, Đánh giá, Cài đặt; cuối menu: model LLM đang dùng và nút sáng/tối).
- **Đầu trang hồ sơ:** breadcrumb, tên dự án sửa tại chỗ, khách hàng, hạn nộp (còn N ngày), giai đoạn deal, huy hiệu trạng thái, KT/Giá, số thông tin cá nhân đã che, thời gian chạy, tổng giá (sau duyệt), giờ tiết kiệm; nút Tải trọn bộ hồ sơ / Yêu cầu sửa / Duyệt ở góc phải.
- **Thanh tiến trình 8 bước** nằm ngang; **7 tab:** Tổng quan · Yêu cầu & câu hỏi · Giải pháp · Kế hoạch & báo giá · Đáp ứng yêu cầu · Proposal & hồ sơ · Quy trình & phê duyệt. Tab lưu trên URL (`?tab=`).
- **Tab Tổng quan:** lưới thẻ 2 cột: Mục tiêu khách · Hướng giải pháp · Khả thi · Rủi ro lớn nhất · Effort & kế hoạch · Báo giá sơ bộ · Đáp ứng yêu cầu · Câu hỏi cần khách xác nhận; mỗi thẻ có "Chi tiết ›".
- **Màu và chữ:** xanh dương nhẹ (`#3b78c2`, nền nhấn `#eaf2fb`), font Inter, chữ thân 14px, nét mảnh; có chế độ tối; không hiệu ứng trang trí.
- **Kế hoạch & báo giá:** báo giá (mô hình hợp đồng, tiền tệ, dự phòng, so với ngân sách khách, theo giai đoạn, mốc thanh toán) → bảng man-day giai đoạn × vai trò → master schedule có tham số và Gantt → bảng WBS sửa được.

### 3.6 Tài liệu

Đã review khoảng 100 tài liệu do các agent viết: ý tưởng và nghiên cứu (`01_idea`, `02_research`, `research-notes/`), yêu cầu và lộ trình (`srs`, `srs_review`, `roadmap`), kiến trúc và tài liệu QA (`04_architecture/`, `slices/`, `quality/`, `sec-audit/`, `README`), có đối chiếu với code.

**Nhận xét chung:** tài liệu nhiều và có cấu trúc, nhưng **không phản ánh đúng sản phẩm**. Kiến trúc mô tả một pipeline có ngữ cảnh đầy đủ, còn code gửi rất ít dữ liệu cho LLM. Roadmap cho phép mọi mốc nghiệm thu chỉ bằng mock, nên tình trạng hiện tại là hệ quả mà chính tài liệu cho phép. SRS (87 KB) và roadmap (48 KB) quá dài so với một MVP, có thể cắt khoảng một nửa mà không mất yêu cầu nào.

**Điểm tốt:** SRS có cấu trúc chuẩn, quy tắc nghiệp vụ viết dạng kiểm thử được. Nghiên cứu có tự phản biện và đã bác được nhiều số liệu sai lan truyền trên mạng. File phân tích mẫu Excel 別紙 thật rất giá trị cho bộ đọc file. QA trung thực về phần E2E (ghi BLOCKED, không biến thành PASS).

#### Ý tưởng và nghiên cứu

| ID | Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|---|
| D-01 | Nghiêm trọng | `01_idea` L75, `02_research` L50 | Coi ○/△/× là thang cố định. Thực tế mỗi khách tự định nghĩa trong sheet bìa hoặc 記入要領 (có khách dùng ◎ = trong giá, △ = tùy biến có tính phí). △ thường đi kèm chi phí, nên bảng đáp ứng phải nối với báo giá | Đọc chú giải từ file của khách và cho người dùng ánh xạ; △ có ghi chú chi phí do code tính |
| D-02 | Cao | `01_idea`, `02_research` | "Cần làm rõ / 要確認" không được phép xuất hiện trong file nộp khách; mục 必須 bỏ ngỏ có thể bị loại | Chỉ là trạng thái nội bộ; bắt buộc xử lý (hỏi khách trong 質問期間 hoặc đổi thành △ kèm 前提条件) trước khi xuất |
| D-03 | Cao | `02_research` L16/L118, `offshore-pricing-ratecard`, `effort-estimation-methods` | Mức giá offshore so với Nhật ghi bốn kiểu khác nhau (31–69%, 33–70%, 45–55%, 40–70%), có chỗ tính sai | Thống nhất một con số có nguồn; thêm đính chính vào các memo gốc |
| D-04 | Cao | `02_research` §2.5 | Nghiên cứu không ra được số liệu nào dùng thẳng cho bảng effort, hệ số hay đơn giá theo vai trò; "PM 10%, BrSE 15%" không có nguồn | Thêm bảng giả lập có ghi nguồn hoặc ghi rõ "giả định" |
| D-05 | Cao | toàn bộ nghiên cứu | Sản phẩm nhắm cả khách VN và khách tiếng Anh nhưng nghiên cứu gần như chỉ có thị trường Nhật | Bổ sung, hoặc thu hẹp phạm vi trong `01_idea` |
| D-06 | Cao | `02_research` L163, L177 | Nói quá: "không công cụ nào có cổng duyệt giá" (CPQ, PandaDoc đều có) | Viết lại điểm khác biệt: nối requirement → effort → giá, kèm cổng duyệt |
| D-07 | Trung bình | `02_research`, `ai-proposal-tools` | Một số số liệu từ nguồn yếu (blog, tài liệu marketing của vendor); vài chỗ tóm tắt còn giữ số đã bị bác ở phần thân | Xóa hoặc gắn nhãn nguồn yếu; đồng bộ phần tóm tắt |
| D-08 | Thấp | `research-notes/` | Trùng lặp nhiều (5 file cùng mô tả ○/△/×); `vn-offshore-bid-practice` có tên người thật | Đánh dấu memo đã được thay bằng `02_research`; bỏ tên người thật |

#### Yêu cầu và lộ trình

| ID | Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|---|
| S-01 | Nghiêm trọng | `srs.md` FR-032.1 (L524), `roadmap` L235 | WBS do AI tạo có trường "man-day", trái với BR-01 và AGENTS.md luật 1 (code đã làm đúng bằng trọng số, nhưng tài liệu sai) | Sửa: AI chỉ chia task và trọng số; code phân bổ man-day |
| S-02 | Nghiêm trọng | `roadmap` §3–10 | Mọi tiêu chí nghiệm thu đều chạy `LLM_PROVIDER=mock`; không mốc nào chạy LLM thật hay dùng RFP và file Excel cỡ thật; mục tiêu "demo ≤ 10 phút" không gắn với mốc nào | Mỗi mốc có AI thêm một kịch bản LLM thật với dữ liệu 30–40 dòng; thêm mốc cuối "Demo E2E" có đo thời gian |
| S-03 | Cao | `srs.md` §8.2 L1159 | Điền ○/△/× vào file của khách và Q&A sheet bị xếp "Won't" dù đã chốt trong MVP; review SRS có nhắc nhưng roadmap không có mốc nào | Thêm mốc riêng có tiêu chí nghiệm thu bằng file mẫu kiểu 別紙 |
| S-04 | Cao | `srs.md` FR-034 | So ngày kết thúc dự án với **hạn nộp hồ sơ** là sai nghiệp vụ; thiếu mốc giai đoạn của khách và khoảng go/no-go sau PoC | Thêm mốc của khách; cảnh báo khi lịch vượt mốc |
| S-05 | Cao | `srs.md` §8.1 | 28/29 yêu cầu chức năng là Must, MoSCoW mất tác dụng | Hạ các mục phụ (lọc, snapshot, khóa, thuế, .xls, PDF…) xuống Should |
| S-06 | Cao | `roadmap` §1 | Gọi là "lát cắt dọc" nhưng thực chất làm theo tầng: file Excel requirement đến M6 mới có, file tải về đầu tiên đến M7 (sau khoảng 70% công sức) | Lát cắt 1 phải đi trọn: email/Excel → đánh giá → effort → Word có ô giá chờ duyệt |
| S-07 | Cao | toàn bộ `docs/` | Không có wireframe, sơ đồ trang hay luồng màn hình; mỗi mốc chỉ ghi "UI: …" | Thêm một trang thiết kế màn hình (tham chiếu `ui_reference/`) trước khi build giao diện |
| S-08 | Trung bình | `srs.md` FR-023 vs §8.2.3; FR-032.3 | Mâu thuẫn: FR-023 bắt chạy tiếp từ bước lỗi nhưng §8.2.3 nói để sau; hai quy tắc chặn/cảnh báo effort chồng nhau | Chọn một quy tắc cho mỗi chỗ |
| S-09 | Trung bình | `srs_review` → `srs` | 36/36 nhận xét được áp dụng máy móc, không mục nào bị bác; vài bản sửa tự sinh lỗi mới và gây phình phạm vi (thuế, インボイス, khóa/mở khóa) | Reviewer và BA phải được phép bác nhận xét có lý do |
| S-10 | Thấp | `srs.md`, `roadmap` | Lặp nhiều (user story chép lại tiêu chí của FR; roadmap chép lại SRS); M7 vẫn ghi PowerPoint dù đã ngoài MVP | Rút gọn SRS còn khoảng 40 KB, roadmap khoảng 15 KB |

#### Kiến trúc và tài liệu QA (đối chiếu code)

| ID | Mức | Tài liệu | Vấn đề | Bằng chứng trong code |
|---|---|---|---|---|
| T-01 | Nghiêm trọng | `llm_pipeline` §0, §10; `architecture` L161 | Tài liệu nói "gọi LLM với JSON schema, retry ≤ 2", code không gửi schema và không retry lỗi JSON (cùng R-01) | `openai_compat_client.py` L64–68, `gateway.py` L65 |
| T-02 | Nghiêm trọng | `llm_pipeline` §2, §4, §7 | Tài liệu mô tả ngữ cảnh đầy đủ cho từng bước; code chỉ gửi email (intake), một câu (đánh giá), ngôn ngữ khách (proposal); câu trả lời làm rõ không đi tiếp (cùng R-02 → R-05) | `b1_intake.py` L41, `evaluation_service.py` L13, `b6_proposal.py` L15 |
| T-03 | Nghiêm trọng | `README` | Ghi "pipeline M2–M7 chạy được ngay" nhưng hồ sơ mẫu lỗi ở bước đánh giá; test né lỗi bằng một bản mock riêng (cùng UI-01) | `mock_client.py`, `tests/test_evaluation_batches.py` L14 |
| T-04 | Cao | `quality/final_verdict`, `fix_log` | Ghi "GATE-01 PASS, toàn bộ test pass" trong khi 2 test fail; phần xác thực vừa thêm vẫn cho người dùng ẩn danh đi qua | `api/deps.py` L64–66 |
| T-05 | Cao | `slices/M7/test_report` | Bảng tóm tắt ghi 16 ca (14 PASS), bảng chi tiết có 22 ca (6 BLOCKED); chưa có lần xuất file thành công nào được chứng minh | `test_report.md` L15, L28, L133 |
| T-06 | Cao | `slices/M7/review` → `README` | Cả 3 lỗi HIGH của review M7 vẫn còn trong code, nhưng README ghi M7 đã xong; mốc nào review cũng "CHANGES REQUIRED" mà không có vòng review lại | `exporters/filename.py` L12, `export_service.py` L43 |
| T-07 | Cao | `sec-audit` FINDING-001, `gate_summary` GATE-01 | Đánh giá thiếu xác thực là HIGH (CVSS 8.1), dù SRS §8.2 đã loại auth khỏi phạm vi và AGENTS.md luật 9 cấm; dẫn tới thay đổi làm dở gây hỏng test (cùng R-08) | `srs.md` L104, L1173 |
| T-08 | Cao | mọi review | Không review nào phát hiện T-01 → T-03; code review còn chấm luật 2 (JSON schema) "đạt"; review coi việc ẩn giá với manager là đúng (cùng UI-02) | `QuotationPage.tsx` L15–16 |
| T-09 | Cao | `srs` FR-031, `architecture` ADR #10 | Tài liệu nói AI đề xuất hệ số và presales xác nhận, đơn giá theo tỉ lệ onsite; code dò từ khóa và tính onsite theo tiền tệ; bước WBS bỏ qua bảng chuẩn đã sửa ở Cài đặt (cùng R-10, R-11) | `factor_engine.py`, `quotation_engine.py`, `b5_wbs.py` L61 |
| T-10 | Thấp | `README`, `api_contract`, `slices/` | README ghi "Milestone hiện tại: M7"; API contract ghi "FROZEN" nhưng có 9 ghi chú thay đổi; khoảng 25 file handoff lặp; M8 không có spec/test report/review; `requirements.txt` không cố định phiên bản thư viện | — |

## 4. Nguyên nhân gốc (quy trình)

1. Tiêu chí nghiệm thu của các mốc chỉ kiểm tra "có endpoint, test pass" với mock, chưa có bước chạy thử với LLM thật.
2. Dữ liệu mẫu quá nhỏ nên không phát hiện được lỗi đọc file và lỗi con số.
3. Bước review của workflow đối chiếu luật hình thức (AGENTS.md), chưa đánh giá nội dung nghiệp vụ.
4. Một số bước viết code dùng model tốc độ cao, sinh code nén và prompt quá ngắn.
5. Quality Gate chưa được nêu rõ phạm vi MVP, nên đề xuất cả hạng mục trái nguyên tắc (xác thực người dùng).
6. Không có thiết kế giao diện (wireframe, ảnh mẫu) từ đầu; mỗi mốc tự thêm một trang mới nên giao diện thành chuỗi trang rời.
7. Review kết luận "CHANGES REQUIRED" nhưng không có vòng review lại, mốc sau vẫn được bắt đầu; tài liệu (README, báo cáo) không được cập nhật theo thực trạng.
8. Review tài liệu (SRS) áp dụng mọi nhận xét mà không phản biện, làm phạm vi phình ra ở phần phụ và thiếu ở phần tạo giá trị.

## 5. Điều kiện để chuyển sang "Đạt"

- [ ] Không còn phát hiện mức Nghiêm trọng (R-xx, UI-xx, D/S/T-xx); mức Cao đã sửa hoặc có lý do chấp nhận.
- [ ] README, SRS, llm_pipeline và báo cáo QA khớp với code hiện tại.
- [ ] Giao diện bám chuẩn mục 3.5, đối chiếu từng tab với ảnh trong `ui_reference/`.
- [ ] Toàn bộ test pass.
- [ ] Chạy trọn một hồ sơ mẫu tiếng Nhật với LLM thật, không lỗi.
- [ ] Kiểm thử thủ công trên Preview đạt toàn bộ checklist ở mục 6.
- [ ] Quality Gate chạy lại cho kết quả GO.

## 6. Checklist kiểm thử thủ công

- [ ] Nạp hồ sơ mẫu → hiển thị đúng số requirement (30–40), không phải 0.
- [ ] Phân tích → câu hỏi làm rõ bằng tiếng Nhật, lý do tiếng Việt → trả lời → pipeline chạy tiếp.
- [ ] Giải pháp có lý do loại các hướng khác; effort hiện công thức và lý do từng hệ số.
- [ ] WBS có PM/QA mỗi giai đoạn; sửa một task → tổng, lịch, giá tự cập nhật.
- [ ] Báo giá chia theo giai đoạn và so với ngân sách khách.
- [ ] Proposal tiếng Nhật bám đúng nội dung RFP; trước duyệt giá hiện "[Presales điền]", sau duyệt hiện bảng giá.
- [ ] Tải Word, Excel ước tính, Excel 別紙1 đã điền ○/△/×: mở được, nội dung đúng.
