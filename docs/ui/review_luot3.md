# Review lượt 3 (sau 3 đợt `/workflow`) và việc còn lại

> Toàn bộ chạy với LLM giả (`LLM_PROVIDER=mock`), không cần LLM key.

Ngày review: 11/10/2026. Cách review: chạy bản `code_vibeflow/scopeai` trên máy, đi luồng bằng trình duyệt như người dùng thật: Tạo hồ sơ → "Dùng bộ này" (mẫu Nhật) → Phân tích → trả lời 2 vòng câu hỏi → tới "Chờ duyệt kỹ thuật"; chụp 12 màn ở 1440×900 (thư mục `ui_v3/`).

## 1. Kết luận

**Tiến bộ rõ, khoảng 70% so với mục tiêu.** Luồng chính đã chạy trơn và số liệu đã nhất quán. Phần còn lại tập trung ở 3 nhóm:
1. **Nhiều chỗ hiện câu kỹ thuật "Backend chưa cung cấp…"** vì dữ liệu chưa có (mock chưa đủ, một số API chưa có).
2. **Lỗi định dạng và hiển thị nhỏ nhưng dễ thấy:** số `378.00000000000006`, onsite `0.1%`, nhãn "Khác" lặp lại, mã thô `customer_jp`, ngày giờ vỡ định dạng.
3. **Dữ liệu mẫu chưa đủ "thật":** 36 requirement nhưng chỉ 6 nội dung lặp lại, cả 36 đều ○, vòng hỏi 2 lặp y câu vòng 1, CRM mà vẫn đề xuất RAG.

## 2. Đã đạt (kiểm chứng trên máy)

| Hạng mục | Kết quả |
|---|---|
| Test | Backend **209 passed**, frontend **6 passed**, type-check sạch |
| Luồng Tạo hồ sơ | "Dùng bộ này" điền form + hiện 3 file; bấm **Phân tích** một lần là tự tạo hồ sơ, tải file, đọc file, chạy pipeline, chuyển sang trang hồ sơ |
| Câu hỏi làm rõ | Banner dẫn tới tab câu hỏi; trả lời trên giao diện, pipeline tự chạy tiếp; hiện vòng hỏi, lý do, loại ảnh hưởng |
| Đọc requirement | 36 requirement từ `ja_requirements.xlsx` (sheet bìa, header dòng 3) |
| Báo giá | ¥8.085.806 = PoC 1.259.622 + MVP 4.765.449 + Production 2.060.735 (**khớp**); có ký hiệu yên |
| Effort | RAG: PoC 55–83, MVP 207–304, Production 83–138 (MVP lớn nhất, hợp lý); bảng hệ số có lý do |
| Lịch | Tự tạo: 26/10/2026 → 30/04/2027, 18 task, có Gantt |
| Khung trang hồ sơ | Đầu trang gọn (breadcrumb, meta, KT/Giá, tổng giá, 3 nút), thanh tiến trình mảnh, 7 tab, tab Đáp ứng có số đếm |
| Proposal | Render Markdown, nhãn "[Presales điền]" màu vàng, thẻ tải 6 loại file |
| Duyệt | 3 thẻ: Duyệt kỹ thuật (có tóm tắt), Duyệt giá (khóa tới khi duyệt KT), Lịch sử |
| Cài đặt | Có tab Bảng effort / Đơn giá / Hệ số, "Xem YAML thu gọn" |

## 3. Việc còn lại

### 3.1 Lỗi hiển thị và định dạng (frontend, sửa nhanh)

| ID | Màn | Lỗi | Sửa |
|---|---|---|---|
| L3-01 | Kế hoạch | Ngày công hiện `378.00000000000006 ngày` | Làm tròn 1 chữ số, định dạng số |
| L3-02 | Kế hoạch | Onsite hiện `0.1%` (giá trị là tỉ lệ 0,1 = 10%) | Nhân 100 hoặc thống nhất đơn vị với backend |
| L3-03 | Tổng quan | Thẻ Đáp ứng yêu cầu hiện "Khác: 36, Khác: 36, Khác: 0…" | Map đúng nhãn ○ / △ / × / Cần làm rõ / Tổng |
| L3-04 | Giải pháp, Kế hoạch | Mã hệ số thô `customer_jp`, `many_requirements`; cột thành phần `rag` | Hiện nhãn tiếng Việt ("Khách Nhật", "Nhiều requirement", "RAG") |
| L3-05 | Duyệt | Ngày giờ vỡ: `11T10:15:19.213594/10/2026` | Định dạng `dd/MM/yyyy HH:mm` |
| L3-06 | Đầu trang | Thanh tiến trình tràn ngang, mất bước Đáp ứng và Proposal | Cho xuống dòng hoặc rút gọn tên bước, luôn thấy đủ |
| L3-07 | Đầu trang | Nút "Chạy lại" là nút xanh lớn ngay dưới đầu trang | Đổi thành nút phụ nhỏ cạnh thanh tiến trình |
| L3-08 | Đầu trang | Bước "Khả thi & rủi ro" báo Hoàn tất nhưng không có dữ liệu khả thi | Hoặc backend trả dữ liệu (xem 3.2), hoặc đổi nhãn bước cho đúng |
| L3-09 | Kế hoạch | Thẻ effort lặp lại (đã có ở tab Giải pháp) | Chỉ giữ một dòng tóm tắt |
| L3-10 | Kế hoạch | Gantt theo **ngày**, khung chỉ thấy ~3 tuần đầu, phần lớn task nằm ngoài khung | Thang **tuần** cho cả 6 tháng, cuộn ngang, có mốc thanh toán |
| L3-11 | Kế hoạch | Bảng WBS vẫn kiểu cũ: mã task xuống dòng, 3 nút mỗi dòng | Cây thu gọn, tab giai đoạn, sửa trong ô, nút hiện khi rê chuột |
| L3-12 | Danh sách | Bảng tràn ngang (cột Hạn nộp bị cắt); "Tổng giá: Chưa có dữ liệu" dù hồ sơ đã có giá | Co cột, lấy giá từ API (xem 3.2) |
| L3-13 | Cài đặt | **Bảng effort trống** (chỉ có tiêu đề cột, không có dòng nào) | Đọc dữ liệu từ `GET /api/settings`, hiện đủ hướng × giai đoạn |
| L3-14 | Tạo hồ sơ | Dòng mô tả ghi **"ScopeAI sẽ tự chạy phân tích"** (sai tên sản phẩm) | Đổi thành "Trợ lý dự thầu" hoặc bỏ tên |
| L3-15 | Tạo hồ sơ | Nút "+ Tạo hồ sơ" ở menu vẫn mờ khi đang ở trang này | Luôn rõ màu, chỉ đổi nền "đang chọn" |
| L3-16 | Tạo hồ sơ | Thẻ mẫu ghi "RFP trợ lý AI bảo trì nhà máy Nhật" nhưng nội dung là CRM | Đổi tiêu đề thẻ cho khớp nội dung |
| L3-17 | Mọi màn | Câu kỹ thuật hiển thị cho người dùng: "Backend chưa cung cấp…", "khi API cung cấp", "Chỉ đọc vì backend chưa có API…" | Không bao giờ hiện chữ "backend/API"; dùng trạng thái rỗng nghiệp vụ, hoặc ẩn thẻ khi chưa có dữ liệu |
| L3-18 | Console | 3 lỗi 409 khi mở trang hồ sơ | Không gọi API khi biết trước trạng thái chưa đủ; xử lý 409 im lặng |

### 3.2 Thiếu dữ liệu / API (backend + mock)

| ID | Thiếu | Ảnh hưởng | Sửa |
|---|---|---|---|
| B3-01 | Giải pháp không có độ tin cậy, giả định, các hướng bị loại, khả thi (3 điểm), rủi ro | Thẻ Giải pháp, Tổng quan (Khả thi, Rủi ro) trống | Thêm vào schema bước solution (hoặc bước khả thi riêng) và mock trả đủ |
| B3-02 | Báo giá chỉ đọc, không đổi mô hình hợp đồng / tiền tệ / dự phòng / onsite | Không chỉnh được giá trước khi duyệt | API cập nhật tùy chọn báo giá (tính lại bằng code), khóa khi đã duyệt giá |
| B3-03 | Ngân sách khách không được trích từ RFP (RFP ghi 1,500万円 税別, lịch 2027/1–2027/9) | "Chưa có ngân sách khách", không so sánh được | Intake trích ngân sách + mốc lịch của khách (mock đọc đúng từ RFP mẫu); báo giá trả so sánh |
| B3-04 | Danh sách hồ sơ thiếu mục tiêu, giai đoạn deal, tổng giá | Bảng danh sách nhiều ô "Chưa có dữ liệu" | Bổ sung trường vào API danh sách |
| B3-05 | Chưa có xuất/nhập Q&A sheet | Nút bị khóa | Endpoint xuất Q&A sheet (ngôn ngữ khách) và nhập câu trả lời |
| B3-06 | Chưa có danh sách phiên bản gửi khách | Thẻ Lịch sử thiếu phiên bản | Endpoint tạo/đánh dấu phiên bản (1.0, 1.1…) |
| B3-07 | Cảnh báo "Lịch kết thúc sau hạn nộp hồ sơ" | **Sai nghiệp vụ**: hạn nộp là hạn nộp hồ sơ thầu, không phải hạn dự án | Bỏ cảnh báo này; thay bằng so với mốc lịch của khách (B3-03) |
| B3-08 | Proposal: tiêu đề mục tiếng Việt ("Giới thiệu", "Tổng quan giải pháp"…) ghép với nội dung tiếng Nhật; chỉ 5 mục; giả định 1 dòng | Tài liệu gửi khách Nhật trộn tiếng Việt | Tiêu đề mục theo ngôn ngữ khách (はじめに…リスク), đủ 8 mục, giả định/対象外 3–5 ý |

### 3.3 Dữ liệu mẫu và mock

| ID | Vấn đề | Sửa |
|---|---|---|
| M3-01 | 36 requirement nhưng chỉ **6 nội dung** lặp lại theo khuôn ("…に関する業務要件を満たし、操作履歴を確認できること") | Viết 36 requirement khác nhau, sát một hệ CRM thật (quản lý khách hàng, lịch sử đối ứng, tìm kiếm, phân quyền, báo cáo, liên kết kế toán, di chuyển dữ liệu Excel, phi chức năng: hiệu năng, bảo mật, sao lưu…); có cột mã `FR-xxx` / `NFR-xxx` |
| M3-02 | Cả 36 requirement đều ○, ghi chú giống nhau | Mock đánh giá trộn ○/△/×/cần làm rõ theo nội dung, ghi chú cụ thể từng dòng |
| M3-03 | Vòng hỏi 2 lặp y 5 câu của vòng 1 | Vòng 2 chỉ hỏi điều còn thiếu sau câu trả lời (hoặc không hỏi nếu đủ); đúng luật "không hỏi lại điều đã trả lời" |
| M3-04 | Hệ CRM (dữ liệu có cấu trúc) mà mock luôn đề xuất **RAG** | Mock chọn hướng theo nội dung: CRM → "Không cần AI" hoặc ML truyền thống, có lý do loại RAG/agent |
| M3-05 | Kết quả phân tích yêu cầu là văn bản cố định, không lấy từ RFP (ngân sách, lịch) | Mock intake đọc từ email + RFP mẫu |

## 4. Kế hoạch sửa bằng `/workflow` (2 đợt)

Chuẩn bị: upload file này lên project thành `docs/ui/review_luot3.md`, ảnh `ui_v3/` thành `docs/ui_v3/`.

### Đợt 4: Dữ liệu, API và mock (backend trước)
Gõ `/` → **workflow**, dán:
```
Đọc docs/ui/review_luot3.md mục 3.2 và 3.3. Làm ĐỢT 4 (backend + mock + dữ liệu mẫu), chưa sửa giao diện:
1. backend-dev: B3-01 đến B3-08 (schema/API/logic). Mọi con số vẫn do code tính; LLM/mock chỉ trả phân loại và giải
   thích. Cập nhật docs/04_architecture/api_contract.md cho mọi endpoint/trường mới, kèm test.
2. backend-dev (song song với 1 nếu không đụng file chung): M3-01 đến M3-05 – viết lại sample_data (36 requirement khác
   nhau có mã FR/NFR, RFP CRM có ngân sách và lịch), làm mock trả dữ liệu theo nội dung hồ sơ.
3. tester: chạy toàn bộ pytest (background), rồi gọi API với bộ mẫu Nhật (LLM mock) để xác nhận: requirement có nội dung
   khác nhau; đánh giá có đủ ○/△/×/cần làm rõ; vòng 2 không lặp câu; hướng giải pháp hợp với CRM; intake có ngân sách
   1,500万円 và mốc lịch; báo giá so được với ngân sách; danh sách hồ sơ có tổng giá. Ghi docs/ui/dot4_check.md với số liệu thật.
4. reviewer: đối chiếu AGENTS.md (nhất là luật 1, 5) và mục 3.2–3.3, ghi docs/ui/dot4_review.md PASS/CHANGES REQUIRED.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; code dễ đọc, không nén nhiều lệnh
trên một dòng. Chạy mỗi lệnh test/build tối đa 2 lần; nếu output bị rtk rút gọn hoặc báo "No tests collected" thì đọc file
log trong [full output: ...] hoặc chạy dạng background command. Không tạo ảnh hay bằng chứng giả. Cho tôi xem kế hoạch trước khi chạy.
```
**Commit:** `Đợt 4: dữ liệu, API, mock`.

### Đợt 5: Hoàn thiện giao diện
Sau khi đợt 4 PASS. Gõ `/` → **workflow**, dán:
```
Đọc docs/ui/review_luot3.md mục 3.1. Làm ĐỢT 5 (frontend): sửa L3-01 đến L3-18, đồng thời hiển thị dữ liệu mới từ đợt 4
(độ tin cậy, hướng bị loại, khả thi, rủi ro; chỉnh tùy chọn báo giá; so với ngân sách khách; danh sách hồ sơ có giá,
giai đoạn deal; Q&A sheet; phiên bản gửi khách). Ảnh hiện tại ở docs/ui_v3/, ảnh mẫu ở docs/ui_reference/.
Tự soạn workflow:
1. frontend-dev A (tuần tự, vì cùng trang hồ sơ): L3-06, L3-07, L3-08, L3-17, L3-18 (khung) → L3-03 (Tổng quan) →
   L3-04 (Giải pháp) → L3-01, L3-02, L3-09, L3-10, L3-11 (Kế hoạch) → L3-05 (Duyệt) → proposal hiển thị tiêu đề theo ngôn ngữ khách.
2. Song song với A: frontend-dev B làm L3-12 (Danh sách), L3-13 (Cài đặt), L3-14, L3-15, L3-16 (Tạo hồ sơ) – các file riêng.
3. tester: đi trọn luồng Tạo hồ sơ (mẫu Nhật) → trả lời câu hỏi → duyệt kỹ thuật → duyệt giá → tải file, kiểm từng mục
   L3-xx, ghi docs/ui/dot5_check.md (mục nào đạt/chưa, bằng chứng thật).
4. frontend-dev A sửa các mục chưa đạt; reviewer ghi docs/ui/dot5_review.md PASS/CHANGES REQUIRED.

Quy tắc: giữ LLM_PROVIDER=mock; tuân thủ AGENTS.md; nhãn tiếng Việt, không hiện mã thô và không hiện chữ "backend/API"
cho người dùng; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi. Chạy npm run
build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log trong [full output: ...]
hoặc chạy dạng background command. Không tạo ảnh hay bằng chứng giả. Cho tôi xem kế hoạch trước khi chạy.
```
**Commit:** `Đợt 5: hoàn thiện giao diện`.

### Sau đợt 5
- Tự đi lại luồng trên Preview, đặc biệt: số ngày công, onsite %, Gantt 6 tháng, bảng Cài đặt có dữ liệu, proposal tiêu đề tiếng Nhật.
- Nếu muốn, gửi lại để review lượt 4 trước khi chụp ảnh "sau" cho slide.

---

## 5. So với bản ScopeAI tự dựng: chức năng còn thiếu

Đối chiếu bằng cách rà API và code của bản VibeFlow (ngày 11/10/2026). "Có một phần" = có dữ liệu hoặc nút nhưng chưa dùng được trọn vẹn.

| Nhóm | Chức năng (ScopeAI có) | Bản VibeFlow | Ưu tiên |
|---|---|---|---|
| Báo giá | Đổi mô hình hợp đồng Trọn gói / T&M / ODC, tiền tệ, % dự phòng, % onsite | Có API sửa nhưng giao diện chỉ đọc; chưa có T&M/ODC thật | P1 |
| Báo giá | Điều chỉnh giá % (price-to-win) và so với ngân sách khách | Chưa có; ngân sách chưa trích từ RFP | P1 |
| Lịch | Khoảng go/no-go sau PoC, ngày bắt đầu giai đoạn theo kế hoạch khách | Chưa có | P1 |
| Hỏi khách | Xuất Q&A sheet theo ngôn ngữ khách, nhập lại câu trả lời | Chưa có (nút khóa) | P1 |
| Hỏi khách | Email nháp gửi khách (ngôn ngữ khách) | Chưa có | P1 |
| Proposal | Dịch proposal Việt / Anh / Nhật | Chưa có (tab chỉ đổi nhãn) | P1 |
| Xuất file | Slide PowerPoint theo ngôn ngữ khách (sơ đồ kiến trúc, Gantt sửa được) | Chưa có | P1 |
| Xuất file | Bộ bidding Excel 4 sheet (Q&A, WBS, Summary công thức SUMIFS, Master Schedule) | Có một phần (estimate.xlsx) | P2 |
| Phân tích | Bước khả thi & rủi ro có điểm, bước kiến trúc có thành phần + sơ đồ Mermaid | Chưa có (chỉ hướng giải pháp + effort) | P1 |
| Quy trình | Chạy lại từ một bước kèm góp ý của người review | Có một phần (có rerun, chưa chọn bước + góp ý) | P2 |
| Quy trình | Checklist Bid/No-bid có gợi ý tự động | Chưa có | P2 |
| Quy trình | Phiên bản gửi khách 1.0 → 1.1 → 2.0, đánh dấu đã gửi | Chưa có | P2 |
| Quản lý hồ sơ | Giai đoạn deal (Mới → Đã gửi → Thắng/Thua), cảnh báo hạn nộp | Có một phần (chưa có trong API danh sách) | P2 |
| Quản lý hồ sơ | Thống kê giờ tiết kiệm, tỉ lệ thắng; gợi ý hồ sơ tương tự | Chưa có | P3 |
| Chuẩn công ty | Template riêng (Word/PowerPoint/Excel), logo, quy tắc đặt tên file | Chưa có | P3 |
| Chuẩn công ty | Thư viện nội dung chuẩn, case study, dự án tham chiếu | Chưa có | P3 |
| Công cụ dev | Trang đánh giá chất lượng (eval), so sánh 2 phiên, Replay demo offline, cache LLM | Chưa có | P3 |
| LLM thật | Đã chạy thật với Opus, có cache để tiết kiệm | Chưa chạy thử với LLM thật | P2 (sau UI) |

**Gợi ý:** không cần làm lại toàn bộ. Cho bài thi, nhóm **P1** là đủ để bản VibeFlow kể được trọn câu chuyện presales (giá có điều chỉnh, lịch theo khách, hỏi khách bằng Q&A + email, proposal song ngữ, slide). P2 nếu còn thời gian; P3 bỏ qua.

### Đợt 6 (tùy chọn): bổ sung chức năng P1
Làm sau Đợt 5. Gõ `/` → **workflow**, dán:
```
Đọc docs/ui/review_luot3.md mục 5. Làm ĐỢT 6 = các chức năng ưu tiên P1, đủ backend + giao diện + test:
1. Báo giá: chọn Trọn gói / T&M / ODC, tiền tệ, % dự phòng, % onsite, % điều chỉnh giá (price-to-win); so với ngân sách
   khách; tính lại bằng code, khóa khi đã duyệt giá.
2. Lịch: khoảng go/no-go sau PoC (mặc định 10 ngày làm việc) và ngày bắt đầu sớm nhất của MVP/Production theo kế hoạch
   khách (lấy từ intake, sửa được).
3. Hỏi khách: xuất Q&A sheet (ngôn ngữ khách, cột trả lời tô vàng), nhập lại file đã điền; email nháp gửi khách
   (LLM viết, tên khách và người gửi do code điền).
4. Proposal: dịch Việt / Anh / Nhật khi bấm, lưu bản dịch; tiêu đề mục theo ngôn ngữ.
5. Phân tích: bước khả thi & rủi ro (3 điểm 1–5, danh sách rủi ro có mức độ) và bước kiến trúc (thành phần, sơ đồ Mermaid)
   hiển thị ở tab Giải pháp.
6. Xuất slide PowerPoint theo ngôn ngữ khách (bối cảnh, giải pháp, kiến trúc, effort, lịch, báo giá sau duyệt, rủi ro).
Mỗi chức năng: backend-dev → frontend-dev → tester kiểm trên Preview (LLM mock) → ghi docs/ui/dot6_check.md. Các chức năng
không đụng file chung có thể chạy song song. Kết thúc bằng reviewer ghi docs/ui/dot6_review.md.

Quy tắc: giữ LLM_PROVIDER=mock (mock phải trả dữ liệu đủ cho các bước mới); tuân thủ AGENTS.md (LLM không sinh con số;
giá chỉ ra tài liệu khách sau khi duyệt); nhãn tiếng Việt, không hiện mã thô; code dễ đọc. Chạy mỗi lệnh test/build tối
đa 2 lần; nếu output bị rtk rút gọn hoặc báo lạ thì đọc log trong [full output: ...] hoặc chạy background. Không tạo ảnh
hay bằng chứng giả. Cho tôi xem kế hoạch trước khi chạy.
```
