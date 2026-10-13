# Review giao diện lượt 2 và kế hoạch sửa từng màn (trên VibeFlow)

> **Toàn bộ kế hoạch này chạy với LLM giả (`LLM_PROVIDER=mock`), không cần LLM key.** Kiểm chứng với LLM thật để sau.

Ngày review: 11/10/2026. Cách review: chạy bản `code_vibeflow/scopeai` (LLM mock), nạp hồ sơ mẫu tiếng Nhật, chạy pipeline tới "Chờ duyệt kỹ thuật", chụp 10 màn hình ở 1440×900. Ảnh hiện tại: `ui_v2/`. Ảnh mẫu: `ui_reference/`.

## 1. Nhận xét chung

**Tiến bộ so với lượt 1:** đã có trang hồ sơ dạng 7 tab, route cũ chuyển về tab, màu xanh dương nhẹ và font Inter, bảng chuẩn hiển thị trong Cài đặt, trang Proposal có thẻ tải file và tab ngôn ngữ, trang báo giá hiện số cho nội bộ, build sạch.

**Vẫn chưa ổn ở 3 tầng:**
1. **Khung trang hồ sơ chưa đúng mẫu:** chưa có đầu trang gọn kèm nút hành động; thẻ 6 ô thông tin và thẻ "Tiến độ phân tích" chiếm nửa màn hình đầu; nút "Phân tích" vẫn nổi bật khi đã phân tích xong; 3 bước B4, B5, B7 luôn ở trạng thái "Chờ".
2. **Nội dung các tab mỏng:** nhiều thẻ chỉ có một câu kiểu "Chưa có…"; tab Tổng quan lặp lại khối đính kèm, đọc file, kết quả phân tích ở bên dưới; proposal không render Markdown.
3. **Số liệu sai làm giao diện vô nghĩa (phải sửa trước):** xem mục 2.

## 2. Lỗi dữ liệu cần sửa trước khi chỉnh giao diện

| ID | Lỗi | Bằng chứng | Ảnh hưởng tới màn |
|---|---|---|---|
| D2-01 | **Bảng effort sai:** hướng RAG có PoC 40–60 lớn hơn MVP 20–30 và Production 12–18; các hướng khác lẫn số cũ và số mới | `backend/app/reference/effort.yaml`; tab Giải pháp hiện PoC 48–72, MVP 24–36 | Giải pháp, Kế hoạch, Tổng quan |
| D2-02 | **Báo giá cộng không khớp:** PoC 2.181.489 + MVP 2.099.163 + Production 2.099.163 = 6,38 triệu, nhưng tổng hiển thị 2.289.990; không có ký hiệu tiền tệ (thực tế là JPY) | `GET /api/bids/1/quotation` | Kế hoạch, Tổng quan |
| D2-03 | **Đọc requirement ra 0 dòng:** parser mới không còn đọc được file CSV mẫu (5 dòng) | `POST /parse` trả `requirements.count = 0` | Yêu cầu, Đáp ứng yêu cầu, Tổng quan |
| D2-04 | **Bộ mẫu tiếng Nhật chưa được thay:** vẫn là email CRM ngắn + CSV 5 dòng tiếng Việt, chưa có RFP .docx và Excel 別紙1 30–40 dòng (Bước 4 chưa xong hoặc chưa đồng bộ) | `sample_data/` | Mọi màn |
| D2-05 | **Lịch không tự tạo:** sau khi có WBS, master schedule vẫn "Chưa có lịch" | tab Kế hoạch | Kế hoạch, Tổng quan |
| D2-06 | **Thanh tiến trình có bước không tồn tại:** B4 Khả thi & rủi ro, B5 Kiến trúc & effort không có trong pipeline; B7 Đáp ứng yêu cầu luôn "Chờ" khi không có requirement (nên là "Bỏ qua") | tab nào cũng thấy | Đầu trang hồ sơ |
| D2-08 | **Dữ liệu mock quá mỏng:** nhiều thẻ trống ("Chưa có rủi ro", "Chưa có điểm khả thi", lý do giải pháp một câu, proposal một câu mỗi mục) vì mock chỉ trả dữ liệu tối thiểu. Không dùng LLM thật thì không thấy giao diện đầy đủ | `backend/app/llm/mock_client.py` | Tổng quan, Giải pháp, Yêu cầu, Proposal |
| D2-07 | **Proposal trộn ngôn ngữ:** tiêu đề mục tiếng Việt (## Giới thiệu) nhưng nội dung tiếng Nhật; mỗi mục chỉ một câu | tab Proposal | Proposal |

## 3. Review từng màn

### Màn 0: Khung trang hồ sơ (áp dụng cho mọi tab)
- Thiếu đầu trang gọn: breadcrumb "Hồ sơ › #1", tên dự án, dòng meta (khách hàng, hạn nộp "còn N ngày", giai đoạn deal, huy hiệu KT/Giá, tổng giá) và nút bên phải "Tải trọn bộ hồ sơ", "Yêu cầu sửa", "Duyệt".
- Thẻ 6 ô (hạn nộp, ngôn ngữ, ngân sách, người tạo, ngày tạo, mã) chiếm nhiều chỗ, nên gộp vào dòng meta.
- "Tiến độ phân tích" là một thẻ lớn; mẫu là một dòng tiến trình mảnh ngay dưới đầu trang.
- Nút "Phân tích" nên ẩn hoặc đổi thành "Chạy lại" khi đã chạy xong.
- Thanh tab thiếu số đếm: "Yêu cầu & câu hỏi (N)", "Đáp ứng yêu cầu (N)".
- Menu trái: nút "+ Tạo hồ sơ" bị mờ khi đang ở trang Tạo hồ sơ (trông như bị vô hiệu); mục "Đánh giá" không có trang tương ứng.

### Màn 1: Tạo hồ sơ (`ui_v2/01_tao_ho_so.png` ↔ `ui_reference/01_tao_ho_so.png`)
- Bố cục form ổn. Thiếu khu đính kèm file ngay khi tạo (hiện phải tạo xong mới đính kèm ở tab Tổng quan).
- Hai nút "Nạp mẫu" nên là thẻ "Bộ hồ sơ RFP mẫu" mô tả nội dung (email + RFP + Excel 別紙1).
- Dòng "Backend OK · LLM: mock" là thông tin kỹ thuật, nên bỏ (đã có ở chân menu).

### Màn 2: Danh sách hồ sơ (`02_danh_sach`)
- Thiếu cột tổng giá, giai đoạn deal, tiến độ; trạng thái bị xuống dòng.
- Thiếu lọc theo khách/giai đoạn và cảnh báo hạn nộp gần.

### Màn 3: Tổng quan (`03_tong_quan`)
- Đúng lưới 2 cột nhưng nội dung gần như rỗng: Khả thi "Chưa có điểm", Rủi ro "Chưa có", Đáp ứng "0 mục", Câu hỏi chỉ ghi "3 câu hỏi đầu và 7 câu khác" mà không liệt kê.
- Hướng giải pháp chỉ có một câu; thiếu độ tin cậy và các hướng bị loại.
- Báo giá không có ký hiệu tiền tệ, không có khoảng và dự phòng.
- **Bên dưới lặp lại** khối Đính kèm, Đọc file, Kết quả phân tích, Câu hỏi làm rõ, vốn thuộc tab Yêu cầu.

### Màn 4: Yêu cầu & câu hỏi (`04_yeu_cau`)
- Chỉ ghi "Đã trả lời tất cả câu hỏi làm rõ", không hiện danh sách câu hỏi (ngôn ngữ khách), lý do (tiếng Việt), câu trả lời, vòng hỏi.
- Thiếu kết quả phân tích yêu cầu dạng cấu trúc (đang nằm ở tab Tổng quan).
- Yêu cầu gốc hiện dạng văn bản thô có ký hiệu `#`, `##`; nên render Markdown và thu gọn mặc định.
- Thiếu khu file đính kèm và nút xuất/nhập Q&A sheet.

### Màn 5: Giải pháp (`05_giai_phap`)
- Thẻ hướng giải pháp sơ sài: thiếu độ tin cậy, các hướng bị loại kèm lý do, khả thi (3 điểm), rủi ro theo mức độ, sơ đồ kiến trúc.
- Thẻ effort hiển thị tốt nhưng lặp lại ở tab Kế hoạch; nên giữ ở đây và để tab Kế hoạch chỉ tóm tắt.
- Thiếu bảng hệ số kèm lý do (hiện chỉ "Hệ số ×1.2").

### Màn 6: Kế hoạch & báo giá (`06_ke_hoach`)
- Báo giá: thiếu nút chọn mô hình hợp đồng và tiền tệ, thiếu 4 ô số (tổng, dự phòng, ngày công, onsite), thiếu bảng so ngân sách, số theo giai đoạn sai (D2-02).
- Master schedule trống (D2-05); thiếu ma trận giai đoạn × loại công việc và Gantt hiển thị ngay.
- Bảng WBS: mã task bị xuống dòng (`WBS-001-` / `01-01`), mỗi dòng có 3 nút gây rối; nên dùng cây thu gọn được, chọn giai đoạn bằng tab, sửa trực tiếp trong ô, nút thêm/xóa hiện khi rê chuột.

### Màn 7: Đáp ứng yêu cầu (`07_dap_ung`)
- Trống do D2-03. Khi có dữ liệu cần: huy hiệu đếm ○/△/×/cần làm rõ có lọc, bảng mã / nội dung / đánh giá / ghi chú, nút "Điền vào file Excel của khách".

### Màn 8: Proposal & hồ sơ (`08_proposal`)
- Có thêm tiêu đề lớn "Proposal" lồng trong tab (thừa).
- Proposal hiển thị Markdown thô (`## Giới thiệu`), không render; tiêu đề mục sai ngôn ngữ (D2-07).
- Nút "Tải .md" lạc kiểu so với các thẻ tải file.
- Giả định / Ngoài phạm vi nên nằm trong thân proposal, không tách thẻ riêng.

### Màn 9: Quy trình & phê duyệt (`09_duyet`)
- Lặp tiêu đề trang ("Cổng duyệt · Hồ sơ #1", "Kiểm tra và duyệt") bên trong tab.
- Thiếu thông tin để quyết định: tóm tắt kỹ thuật (giải pháp, effort, cảnh báo WBS) và tóm tắt giá; thiếu lịch sử duyệt và phiên bản gửi khách.
- Lựa chọn "Bỏ qua" khó hiểu với người dùng.

### Màn 10: Cài đặt (`10_cai_dat`)
- Sửa YAML thô trong textarea, có nhãn kỹ thuật "M8 · Quản trị"; người dùng nghiệp vụ khó dùng.
- Nên là bảng nhập: effort (hướng × giai đoạn, min–max), đơn giá (vai trò × offshore/onsite), hệ số (tên, giá trị, lý do), có kiểm tra và nút lưu từng bảng.

---

## 4. Cách sửa trên VibeFlow

### Luồng đề xuất

```
Bước 0  Sửa dữ liệu D2-01 → D2-08            (!backend-dev)            ← đã làm, cần kiểm lại số liệu
Bước 1  Màn Tạo hồ sơ (Màn 1)                (!frontend-dev ± !backend-dev)
Bước 2  Khung trang hồ sơ (Màn 0)            (!frontend-dev)
Bước 3  Từng màn: 3 → 4 → 5 → 6 → 7 → 8 → 9 → 2 → 10  (#Presales UI Screen hoặc !frontend-dev)
Bước 4  Kiểm tra tổng (!tester + !reviewer)
```

Làm đúng thứ tự: Bước 0 trước, vì số sai thì giao diện đẹp cũng không thuyết phục. Bước 1 (màn Tạo hồ sơ) trước, vì nó đổi luồng vào app: đính kèm, đọc file và bắt đầu phân tích đều chuyển về màn này, nên trang hồ sơ và các tab phía sau phải theo luồng mới. Bước 2 trước Bước 3, vì mọi tab dùng chung khung.

### Chuẩn bị chung
- Upload `ui_v2/` lên project thành `docs/ui_v2/` (ảnh hiện tại) bên cạnh `docs/ui_reference/`.
- Upload file này lên `docs/ui/review_ui_tung_man.md`.
- Model: `GPT-5.6 Luna`. Mỗi bước một conversation mới.
- Mỗi lượt sửa màn: đính kèm **2 ảnh**: ảnh mẫu (`ui_reference/…`) và ảnh hiện tại (`ui_v2/…`) bằng **+ → Add files or photos**.
- Mọi prompt bên dưới đã kèm sẵn phần **Quy tắc** ở cuối: chỉ việc copy nguyên khối và dán.

### Bước 0: Sửa dữ liệu (agent `!backend-dev`)
```
Đọc docs/ui/review_ui_tung_man.md mục 2 (D2-01 đến D2-08) và sửa:
1. backend/app/reference/effort.yaml: viết lại toàn bộ cho nhất quán, giả lập sát thị trường dự án doanh nghiệp quy mô
   vừa, team offshore VN; với mọi hướng: MVP > PoC và MVP > Production (ví dụ RAG: PoC 40–60, MVP 150–220,
   Production 60–100). Thêm test kiểm tra quy tắc này cho mọi hướng.
2. Báo giá: tổng = tổng theo giai đoạn (đã gồm overhead, dự phòng) – thêm test; API trả currency và frontend định dạng
   tiền tệ (¥1,234,000 / 1.234.000 ₫).
3. Parser requirement: đọc được cả CSV có header ở dòng 1 lẫn Excel có sheet bìa và header ở dòng 3; test với cả hai.
4. sample_data: thay bộ mẫu tiếng Nhật đầy đủ (hư cấu, ghi 架空): email, RFP .docx có ngân sách và lịch dự kiến,
   Excel 別紙1 30–40 requirement (sheet bìa, header dòng 3, cột 対応可否 và 補足説明 trống); nút "Nạp mẫu tiếng Nhật"
   dùng bộ này.
5. Sau bước WBS tự tạo master schedule mặc định (ngày bắt đầu = thứ Hai gần nhất sau 2 tuần, số người gợi ý theo effort).
6. Danh sách bước pipeline trả về cho frontend chỉ gồm các bước thật; bước không có dữ liệu thì trạng thái "skipped".
7. Proposal: tiêu đề mục theo ngôn ngữ khách (ja: はじめに, 提案概要, 進め方, スケジュール, 体制, 前提条件, 対象外, リスク).
8. Giữ LLM_PROVIDER=mock (KHÔNG cấu hình LLM thật). Làm giàu backend/app/llm/mock_client.py để bộ mẫu tiếng Nhật cho ra
   dữ liệu đầy đủ như LLM thật, vẫn đúng schema và vẫn không chứa con số man-day/giá: intake đủ các trường; 5–7 câu hỏi
   làm rõ tiếng Nhật kèm lý do tiếng Việt; giải pháp có lý do 3–4 câu, độ tin cậy, 3–4 hướng bị loại kèm lý do, giả định;
   khả thi 3 điểm + 4–5 rủi ro có mức độ và cách giảm thiểu; đánh giá requirement trộn ○/△/×/cần làm rõ với ghi chú cụ thể;
   proposal tiếng Nhật 8 mục, mỗi mục 2–4 đoạn, có dòng {{QUOTATION}}. Có fixture cho mọi schema (kể cả EvaluationBatch).
Chạy toàn bộ pytest (background), báo số pass/fail thật.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```
**Xong khi:** với LLM mock, nạp mẫu tiếng Nhật → đọc ra 30–40 requirement; tab Đáp ứng có dữ liệu; tổng báo giá khớp tổng các giai đoạn; có lịch; các thẻ Tổng quan không còn "Chưa có…".

### Bước 1: Màn Tạo hồ sơ (làm trước, vì đổi luồng vào app)
Ảnh: `ui_reference/01_tao_ho_so.png`, `ui_v2/01_tao_ho_so.png`. Agent: `!frontend-dev` (thêm `!backend-dev` nếu cần endpoint mới).
```
Màn: trang Tạo hồ sơ. Mục tiêu: người dùng nhập yêu cầu và đính kèm MỌI tài liệu khách gửi ngay trên màn này,
bấm "Phân tích" một lần là hệ thống tự chạy hết, không phải sang trang hồ sơ để đọc file hay bấm thêm nút nào.

Bố cục từ trên xuống:
1. Thẻ "Bộ hồ sơ RFP mẫu": mô tả ngắn (email + RFP .docx + Excel 別紙1, dữ liệu giả lập) và nút "Dùng bộ này".
   Bấm vào thì ĐIỀN SẴN form và HIỆN 3 file mẫu trong khu đính kèm (chưa tạo hồ sơ, chưa phân tích).
   Làm tương tự cho mẫu tiếng Việt.
2. Thông tin hồ sơ: Tên dự án*, Tên khách hàng*, Hạn nộp, Ngôn ngữ khách* (tự gợi ý theo nội dung dán vào),
   Ngân sách + Đơn vị tiền (tùy chọn).
3. Nội dung yêu cầu* (email/RFP dán vào, tối thiểu 30 ký tự, đếm ký tự).
4. Khu "Tài liệu đính kèm": vùng kéo thả + nút "Chọn file"; tối đa 10 file, mỗi file ≤ 20 MB; nhận .pdf .docx .txt .md
   .xlsx .xls .csv .zip. Mỗi file một dòng: tên, dung lượng, loại tự nhận diện (RFP/tài liệu · Excel requirement ·
   Dữ liệu mẫu · Source code) có select để đổi, nút xóa, lỗi tiếng Việt nếu sai định dạng/quá cỡ.
5. Nút chính "Phân tích" (và "Hủy"). Khi bấm, hiện tiến trình ngay trên nút/khung: Tạo hồ sơ → Tải file (x/N) →
   Đọc file (số requirement đọc được) → Bắt đầu phân tích. Xong thì chuyển sang trang hồ sơ, tab Tổng quan,
   thấy tiến độ realtime. Nếu pipeline dừng để hỏi làm rõ thì trang hồ sơ hiện banner "Trả lời câu hỏi".
   Lỗi ở bước nào thì dừng, báo rõ bước đó, giữ nguyên dữ liệu đã nhập và có nút "Thử lại" (không tạo hồ sơ trùng).

Luồng gọi API: dùng các endpoint sẵn có theo thứ tự tạo hồ sơ → upload từng file → parse → confirm (tự xác nhận,
mức sẵn sàng dữ liệu lấy theo gợi ý của backend, mặc định "medium") → start pipeline. Nếu cần, backend-dev thêm một
endpoint gộp (multipart) để làm trọn trong một lần gọi; khi đó cập nhật api_contract.md và thêm test.
Bộ mẫu: có endpoint trả danh sách/tải file mẫu để frontend hiện trong khu đính kèm, hoặc tạo hồ sơ mẫu ở backend khi
bấm "Phân tích" — chọn cách đơn giản, nhưng người dùng phải THẤY các file mẫu trước khi bấm.
Trên trang hồ sơ: bỏ khối "Đính kèm hồ sơ" và "Đọc và xác nhận dữ liệu" khỏi tab Tổng quan; danh sách file chỉ còn
ở tab Yêu cầu & câu hỏi (chỉ xem, có nút thêm file + chạy lại khi cần).
Menu trái: nút "+ Tạo hồ sơ" luôn rõ màu kể cả khi đang ở trang này.

Kiểm tra tay trên Preview: "Dùng bộ này" (mẫu Nhật) → thấy 3 file → Phân tích → tự sang trang hồ sơ, đọc được
36 requirement, pipeline chạy tới "Chờ làm rõ" mà không bấm thêm nút nào. Ghi kết quả thật vào handoff; không tạo ảnh giả.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```
**Xong khi:** "Dùng bộ này" (mẫu Nhật) → thấy 3 file → bấm Phân tích → tự sang trang hồ sơ, đọc 36 requirement, pipeline chạy tới "Chờ làm rõ" mà không bấm thêm nút nào. Commit `UI: màn Tạo hồ sơ`.

### Bước 2: Khung trang hồ sơ (agent `!frontend-dev`)
Đính kèm: `ui_reference/03_tong_quan.png`, `ui_v2/03_tong_quan.png`.
```
Sửa KHUNG trang chi tiết hồ sơ (frontend/src/pages/BidDetailPage.tsx và component dùng chung) cho giống phần đầu ảnh
mẫu đính kèm, theo docs/ui/review_ui_tung_man.md "Màn 0":
1. Đầu trang gọn: breadcrumb "Hồ sơ › #id"; tên dự án (sửa tại chỗ); một dòng meta gồm khách hàng, hạn nộp kèm
   "còn N ngày" (đỏ khi ≤ 7 ngày), giai đoạn deal (select), huy hiệu trạng thái, huy hiệu "KT ✓/–" và "Giá ✓/–",
   tổng giá có ký hiệu tiền tệ nếu đã có. Bên phải: "Tải trọn bộ hồ sơ", "Yêu cầu sửa", "Duyệt" (nút chính, mở tab Quy trình).
2. Bỏ thẻ 6 ô thông tin (đưa vào dòng meta). Nút "Phân tích" chỉ hiện khi chưa chạy; đã chạy thì là "Chạy lại" dạng phụ.
3. Thay thẻ "Tiến độ phân tích" bằng một dòng tiến trình mảnh ngay dưới đầu trang: tên bước + dấu ✓ / spinner / đỏ
   (kèm nút chạy lại) / xám "Bỏ qua"; chỉ hiện các bước thật.
4. Thanh tab có số đếm: "Yêu cầu & câu hỏi (N câu hỏi)", "Đáp ứng yêu cầu (N requirement)".
5. Menu trái: nút "+ Tạo hồ sơ" luôn rõ màu; bỏ mục "Đánh giá" nếu chưa có trang.
6. Bỏ tiêu đề trang lồng bên trong các tab (ví dụ "Proposal", "Kiểm tra và duyệt").
7. Trạng thái bước lấy từ backend: chưa chạy = "Chưa chạy" (xám nhạt); đang chạy = spinner; xong = ✓; lỗi = đỏ + nút
   chạy lại; "Bỏ qua" CHỈ khi pipeline đã chạy qua bước đó mà không có dữ liệu. Ẩn bước không có trong pipeline.
8. Khi chờ làm rõ: banner vàng dưới đầu trang "AI cần bạn trả lời N câu hỏi để phân tích tiếp" + nút "Trả lời câu hỏi"
   (mở tab Yêu cầu & câu hỏi, cuộn tới câu chưa trả lời); mở hồ sơ đang chờ làm rõ thì tự chọn tab đó; tab có chấm vàng
   và số câu; bước B2 bấm được. Gửi câu trả lời xong pipeline tự chạy tiếp, không bắt bấm "Phân tích" lại.
9. Nút "Phân tích"/"Chạy lại" bị khóa thì luôn hiện lý do kèm nút dẫn tới việc cần làm. Hồ sơ chưa phân tích: các tab
   hiện trạng thái rỗng thân thiện, không hiện khung lỗi đỏ (chỉ hiện lỗi đỏ khi API trả lỗi thật).

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```
**Xong khi:** màn hình đầu (900 px) thấy được đầu trang, dòng tiến trình, thanh tab và ít nhất 2 thẻ nội dung; khi chờ làm rõ có banner dẫn tới câu hỏi; không còn bước "Bỏ qua" sai. Commit `UI: khung trang hồ sơ`.

### Bước 3: Sửa từng màn

**Cách A (khuyên dùng): tạo workflow nhỏ dùng lại cho mọi màn.** Trên Canvas, dựng `Presales UI Screen` gồm 3 node:

| Node | Agent | Model | Instructions |
|---|---|---|---|
| 1 `Sửa màn` | Frontend Dev | Mạnh | `Sửa đúng màn được nêu trong yêu cầu theo ảnh mẫu và ảnh hiện tại đính kèm, và theo mục tương ứng trong docs/ui/review_ui_tung_man.md. Chỉ sửa file của màn đó và component dùng chung cần thiết. Nếu thiếu dữ liệu từ API, ghi rõ vào docs/ui/api_gaps.md thay vì bịa dữ liệu. Giữ LLM_PROVIDER=mock. Tuân thủ AGENTS.md; nhãn tiếng Việt, không code nén; build + test tối đa 2 lần mỗi lệnh (đọc log rtk nếu output lạ).` |
| 2 `Chụp & so sánh` | Tester | Rẻ | `Chạy app trên Preview với hồ sơ mẫu tiếng Nhật (LLM mock). Nếu có trình duyệt thì chụp màn vừa sửa ở 1440×900 vào docs/ui_v3/; nếu không thì kiểm tra bằng API/DOM và ghi rõ là không có ảnh, KHÔNG tạo ảnh giả. Viết docs/ui/compare_<màn>.md: bảng so với ảnh mẫu (thiếu gì, lệch gì, chữ tràn, trạng thái rỗng/lỗi), mức CAO/TB/THẤP. Không sửa code.` |
| 3 `Sửa lần 2` | Frontend Dev | Mạnh | `Sửa mọi mục CAO và TB trong docs/ui/compare_<màn>.md, kiểm tra lại trên Preview, cập nhật cột "Đã sửa". Nếu không còn mục CAO thì ghi "Đạt" và dừng.` |

Mỗi màn: gõ `#` → **Presales UI Screen**, đính kèm 2 ảnh, dán prompt của màn ở dưới.

**Cách B (nhanh hơn):** gõ `!` → **frontend-dev**, đính kèm 2 ảnh, dán prompt của màn kèm đoạn đuôi chung.

#### Màn 3: Tổng quan
Ảnh: `ui_reference/03_tong_quan.png`, `ui_v2/03_tong_quan.png`
```
Màn: tab Tổng quan. Lưới 2 cột các thẻ có "Chi tiết ›" sang tab tương ứng:
- Mục tiêu của khách: đoạn mục tiêu, chip ràng buộc, 4–5 gạch đầu dòng, "+N ràng buộc khác".
- Hướng giải pháp: tên hướng + huy hiệu độ tin cậy + lý do 3–4 dòng + các hướng bị loại gạch ngang.
- Khả thi: 3 thanh điểm (dữ liệu, kỹ thuật, giá trị) + huy hiệu khuyến nghị; Rủi ro lớn nhất: 3 rủi ro, cột mức độ màu.
- Effort & kế hoạch: man-day từng giai đoạn, số task WBS, ngày kết thúc theo lịch.
- Báo giá sơ bộ: tổng có ký hiệu tiền tệ, khoảng min–max, dự phòng, chi phí vận hành/tháng.
- Đáp ứng yêu cầu: huy hiệu đếm ○/△/×/cần làm rõ.
- Câu hỏi cần khách xác nhận: liệt kê 3 câu đầu (ngôn ngữ khách) + "… và N câu khác".
- Cuối trang: "Yêu cầu gốc của khách" thu gọn.
XÓA khỏi tab này các khối Đính kèm, Đọc file, Kết quả phân tích, Câu hỏi làm rõ (chuyển sang tab Yêu cầu & câu hỏi).
Thẻ nào thiếu dữ liệu thì hiện trạng thái rỗng có hướng dẫn ngắn, không để một câu "Chưa có…" trơ trọi.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 4: Yêu cầu & câu hỏi
Ảnh: `ui_reference/04_yeu_cau_cau_hoi.png`, `ui_v2/04_yeu_cau.png`
```
Màn: tab Yêu cầu & câu hỏi, từ trên xuống:
1. Thẻ "Kết quả phân tích yêu cầu" (mục tiêu, người dùng, dữ liệu, ràng buộc, ngân sách, thời hạn) dạng 2 cột.
2. Thẻ "Câu hỏi làm rõ": từng câu gồm số thứ tự, chủ đề, câu hỏi (ngôn ngữ khách), "Vì sao hỏi" (tiếng Việt), câu trả lời
   (hoặc ô nhập khi đang chờ), huy hiệu "Chặn" nếu blocking; nhóm theo vòng hỏi. Nút "Xuất Q&A sheet" và "Nhập câu trả lời".
3. Thẻ "File đính kèm": danh sách file, loại, trạng thái đọc, số requirement đọc được; nút thêm file.
4. "Yêu cầu gốc của khách": render Markdown, thu gọn mặc định.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 5: Giải pháp
Ảnh: `ui_reference/05_giai_phap.png`, `ui_v2/05_giai_phap.png`
```
Màn: tab Giải pháp:
1. Thẻ "Hướng giải pháp": tên hướng, huy hiệu độ tin cậy, lý do, bảng các hướng bị loại kèm lý do, giả định.
2. Thẻ "Khả thi & rủi ro": 3 điểm khả thi có thanh, khuyến nghị; bảng rủi ro (mức độ màu, loại, mô tả, cách giảm thiểu).
3. Thẻ "Effort do code tính": giữ như hiện tại, thêm bảng hệ số (tên, giá trị, lý do) và công thức bảng chuẩn × hệ số.
4. Nút "Rà soát hướng giải pháp" đặt ở đầu thẻ 1, dạng nút phụ.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 6: Kế hoạch & báo giá
Ảnh: `ui_reference/06_ke_hoach_bao_gia.png`, `ui_v2/06_ke_hoach.png`
```
Màn: tab Kế hoạch & báo giá:
1. Thẻ "Chi phí dự kiến": góc phải có nút chọn mô hình (Trọn gói / T&M / ODC) và tiền tệ (VND/JPY/USD);
   4 ô số: tổng (kèm khoảng), dự phòng (sửa %), ngày công (WBS + quản lý), tỉ lệ onsite (sửa %);
   bảng "So với ngân sách khách" (phạm vi, ngân sách, giá của mình, chênh lệch %); bảng theo giai đoạn
   (giai đoạn, ngày công, chi phí, khoảng); mốc thanh toán; "Chi tiết theo vai trò" thu gọn. Mọi số có ký hiệu tiền tệ.
2. Thẻ "WBS & master schedule": ma trận giai đoạn × loại công việc (man-day, có tổng); form tham số lịch gọn một dòng;
   Gantt theo tuần hiển thị ngay; bảng WBS dạng cây thu gọn, chọn giai đoạn bằng tab, mã task không xuống dòng,
   sửa tên/man-day trực tiếp trong ô, nút thêm/xóa chỉ hiện khi rê chuột, có nút "Lưu thay đổi" chung.
3. Bỏ thẻ effort trùng (đã có ở tab Giải pháp), chỉ giữ một dòng tóm tắt.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 7: Đáp ứng yêu cầu
Ảnh: `ui_reference/07_dap_ung_yeu_cau.png`, `ui_v2/07_dap_ung.png`
```
Màn: tab Đáp ứng yêu cầu: hàng huy hiệu lọc (Tất cả N · ○ · △ · × · Cần làm rõ) có số đếm; bảng mã / nội dung /
đánh giá (huy hiệu màu) / thành phần / ghi chú; nút "Điền ○/△/× vào file Excel của khách" (chọn ngôn ngữ ghi chú)
và "Tải bảng đáp ứng". Khi không có file requirement: trạng thái rỗng hướng dẫn đính kèm Excel ở tab Yêu cầu.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 8: Proposal & hồ sơ
Ảnh: `ui_reference/08_proposal_ho_so.png`, `ui_v2/08_proposal.png`
```
Màn: tab Proposal & hồ sơ:
1. Hàng thẻ tải file (Word, Excel ước tính, PDF, Excel requirement đã điền, gói ZIP) đồng kiểu; "Tải .md" thành một thẻ
   cùng kiểu hoặc nút phụ trong thẻ proposal.
2. Thẻ proposal: tab ngôn ngữ (gốc / dịch), nút Copy, Chỉnh sửa; nội dung RENDER Markdown như tài liệu (tiêu đề,
   bảng, danh sách), nền giấy trắng; dòng {{QUOTATION}} hiện bảng giá hoặc "[Presales điền]" dạng nhãn vàng.
3. Chế độ Chỉnh sửa: 2 cột (soạn Markdown | xem trước), cảnh báo nếu xóa dòng {{QUOTATION}}.
4. Giả định / Ngoài phạm vi hiển thị trong thân proposal, bỏ 2 thẻ riêng ở dưới.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 9: Quy trình & phê duyệt
Ảnh: `ui_reference/09_quy_trinh_duyet.png`, `ui_v2/09_duyet.png`
```
Màn: tab Quy trình & phê duyệt, chia 3 thẻ:
1. "Duyệt kỹ thuật": tóm tắt để quyết định (hướng giải pháp, tổng effort, cảnh báo WBS, số câu hỏi còn mở),
   ô nhận xét, nút Duyệt / Yêu cầu sửa; hiện người duyệt và thời điểm khi đã duyệt.
2. "Duyệt giá": tổng giá, so với ngân sách, dự phòng, mô hình hợp đồng; ô nhận xét (bắt buộc khi từ chối);
   nút Duyệt giá / Từ chối; chỉ bật khi đã duyệt kỹ thuật.
3. "Lịch sử & phiên bản": dòng thời gian các lần duyệt, sửa, mở khóa; danh sách phiên bản gửi khách.
Bỏ lựa chọn "Bỏ qua".

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 2: Danh sách hồ sơ
Ảnh: `ui_reference/02_danh_sach_ho_so.png`, `ui_v2/02_danh_sach.png`
```
Màn: trang Hồ sơ: bảng cột tên dự án (kèm mục tiêu 1 dòng), khách hàng, giai đoạn deal, trạng thái (không xuống dòng),
tổng giá có tiền tệ, hạn nộp (đỏ khi ≤ 7 ngày), ngày tạo; tìm kiếm + lọc trạng thái + lọc giai đoạn; bấm dòng mở hồ sơ.

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

#### Màn 10: Cài đặt
Ảnh: `ui_reference/10_cai_dat.png`, `ui_v2/10_cai_dat.png`
```
Màn: trang Cài đặt: thay textarea YAML bằng bảng nhập có kiểm tra:
- Bảng effort: hàng = hướng giải pháp, cột = PoC/MVP/Production (min–max).
- Đơn giá: hàng = vai trò, cột = offshore/onsite (định dạng tiền), overhead PM/BrSE, tỉ giá.
- Hệ số: tên, giá trị, lý do, trần.
Mỗi bảng có nút Lưu, thông báo lỗi tiếng Việt khi sai; giữ chế độ "Xem YAML" thu gọn cho người cần. Bỏ nhãn "M8 · Quản trị".

Quy tắc: giữ LLM_PROVIDER=mock, không cấu hình hay gọi LLM thật; tuân thủ AGENTS.md; không đổi logic tính số trong backend trừ khi prompt yêu cầu; nhãn hiển thị tiếng Việt,
không hiện mã thô; code dễ đọc, không nén nhiều lệnh trên một dòng; mọi request có trạng thái loading/rỗng/lỗi.
Chạy npm run build và npm run test tối đa 2 lần mỗi lệnh; nếu output bị rtk rút gọn hoặc báo lạ thì đọc file log
trong [full output: ...] hoặc chạy dạng background command. Xong thì kiểm tra trên Preview với hồ sơ mẫu tiếng Nhật
và liệt kê ngắn những gì đã đổi. Chỉ lưu ảnh chụp từ app thật; nếu sandbox không chụp được thì ghi rõ, KHÔNG tạo ảnh giả.
```

### Bước 4: Kiểm tra tổng
1. `!tester`:
   ```
   Chạy hồ sơ mẫu tiếng Nhật (LLM mock) từ Tạo hồ sơ tới duyệt giá; chụp mọi màn ở 1440×900 và 1280×800 vào
   docs/ui_v3/final/; ghi docs/ui/final_check.md: màn nào còn lệch ảnh mẫu, chữ tràn, nút không hoạt động, lỗi console.
   ```
2. `!reviewer`: đối chiếu `docs/ui/review_ui_tung_man.md` (mục 3) và `final_check.md`, ghi kết luận PASS / CHANGES REQUIRED.
3. Tự đi lại trên Preview, commit `UI v3`, cập nhật ảnh "sau" cho slide.

## 5. Ước lượng và lưu ý
- Bước 0 + Bước 1: khoảng 1–2 giờ. Mỗi màn ở Bước 2: 20–40 phút (cách A tốn hơn cách B nhưng có ảnh so sánh).
- Theo dõi tab Context sau mỗi lượt; nếu agent chạy lặp một lệnh quá 2 lần thì bấm **Stop** và nhắc luật `rtk`.
- Nếu agent ghi vào `docs/ui/api_gaps.md`, gom lại và chạy một lượt `!backend-dev` bổ sung API trước khi làm tiếp các màn còn thiếu dữ liệu.
