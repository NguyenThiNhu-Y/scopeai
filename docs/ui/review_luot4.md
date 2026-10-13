# Review lượt 4 (sau Đợt 4, 5, 6a) và kế hoạch sửa trước khi chạy LLM thật

> Chạy với LLM giả (`LLM_PROVIDER=mock`). Ảnh hiện tại: `ui_v4/`. Ảnh mẫu: `ui_reference/`.

Ngày review: 11/10/2026. Cách review: chạy bản `code_vibeflow/scopeai` trên máy (backend **226 passed**, frontend **9 passed**, type-check sạch), đi luồng bằng trình duyệt: Tạo hồ sơ → "Dùng bộ này" (CRM Nhật) → Phân tích → trả lời câu hỏi → Chờ duyệt kỹ thuật; đối chiếu API.

## 1. Đối chiếu nhận xét của người dùng

| # | Nhận xét | Kết quả kiểm | Ghi chú |
|---|---|---|---|
| 1 | Màn Tạo hồ sơ: bấm "+ Tạo hồ sơ" thì nút chuyển trắng | **Đúng** | Khi đang ở trang Tạo hồ sơ, nút ở menu thành ô trắng viền xanh, mất chữ (chữ trắng trên nền trong suốt) |
| 2 | Nội dung yêu cầu chưa có chỗ tải file, yêu cầu dài thì sao | **Đúng một phần** | Có khu "Tài liệu đính kèm" ở dưới, nhưng ô Nội dung yêu cầu không có nút "Lấy nội dung từ file" (.txt/.md/.docx/.pdf → đổ chữ vào ô); RFP dài vẫn phải dán tay |
| 3 | Ngân sách tự trích từ yêu cầu, tiền tệ tự quy đổi | **Đúng** | Backend đã trích được ngân sách ¥15,000,000 sau khi phân tích, nhưng màn Tạo hồ sơ vẫn bắt nhập tay và để trống khi nạp mẫu; tiền tệ không tự theo ngôn ngữ khách |
| 4 | Tổng quan chưa có card thống kê | **Đúng** | Không có hàng chỉ số nhanh (số requirement, % đáp ứng, số câu hỏi, man-day, giá, ngày kết thúc); trang Danh sách cũng chưa có thẻ thống kê (tổng hồ sơ, đang phân tích, chờ duyệt, đã duyệt) |
| 5 | Dùng "man-day" thay "ngày công" | **Đúng** | Còn "ngày công" ở Tổng quan, Kế hoạch, Duyệt |
| 6 | Tab câu hỏi có 2 vòng | **Đúng về trải nghiệm** | Thiết kế cho phép tối đa 2 vòng, nhưng mock luôn hỏi thêm vòng 2 dù đã trả lời "như dự kiến"; thẻ "Câu hỏi cần khách xác nhận" ở Tổng quan vẫn ghi "... và 3 câu khác" dù đã trả lời hết |
| 7 | Tab Giải pháp ngay sau khi trả lời câu hỏi báo "chưa có giải pháp", tải lại mới có | **Đúng (lỗi)** | Tab không tải lại dữ liệu khi pipeline xong; còn hiện khung đỏ "Chưa tải được effort" |
| 8 | Tab Giải pháp chưa có mock data | **Đúng một phần** | Đã có lý do, độ tin cậy (dạng chữ), giả định, hướng bị loại, khả thi (3 dòng chữ); **chưa có rủi ro**, ghi chú kiến trúc, điểm khả thi dạng số |
| 9 | "Effort do code tính" chưa giống ScopeAI | **Đúng** | Thiếu bảng chuẩn theo giai đoạn (min–max gốc), công thức "bảng chuẩn × hệ số", so với tổng WBS; hệ số hiện mã thô `customer_jp` |
| 10 | Kế hoạch thanh toán có vẻ không cần | **Hợp lý** | Mốc thanh toán là phần của báo giá trọn gói; nên thu gọn trong "Chi tiết báo giá", không chiếm chỗ chính |
| 11 | Gantt theo tuần, đừng theo ngày | **Đúng** | Gantt đang theo ngày, chỉ thấy ~3 tuần đầu; nhãn dòng là "PoC · PM 5,5 ngày công" thay vì tên task |
| 12 | WBS sửa ngay trong dòng (input, select), bỏ nút Sửa, nút Xóa thành icon, chữ canh trái + "...", thêm task đẹp hơn | **Đúng** | Bảng vẫn kiểu cũ: mã task xuống dòng, 3 nút mỗi dòng |
| 13 | Thiếu đếm số người mỗi vai trò (AI, BE, FE, PM...) | **Đúng** | Có `team_allocation` trong API nhưng giao diện chỉ ghi "đã có phân bổ nhân sự" |
| 14 | Thiếu chỉnh số người rồi tính lại | **Đúng** | Không có ô headcount theo vai trò |
| 15 | Thiếu master schedule chỉnh ngày bắt đầu | **Đúng một phần** | Có ô go/no-go, MVP/Production sớm nhất; **không có ô ngày bắt đầu dự án**, và lịch bắt đầu 26/10/2026 trong khi RFP ghi 「2027年1月に着手」 |
| 16 | Proposal: xem online, chọn ngôn ngữ trước khi soạn | **Đúng** | Chưa có chế độ xem dạng trang tài liệu; chưa chọn ngôn ngữ trước khi sinh proposal |
| 17 | Tab Phê duyệt còn đơn sơ | **Đúng** | Thiếu checklist Bid/No-bid, phiên bản gửi khách, giai đoạn deal, ghi chú khi duyệt hiện trong lịch sử |
| 18 | Cài đặt thiếu hết, thiếu template | **Đúng, và còn lỗi** | Bảng effort **trống** vì API `/api/settings` trả cấu trúc khác với giao diện mong đợi; chưa có template, logo, thông tin công ty, nội dung chuẩn, case study, tiêu chí Bid/No-bid |

## 2. Phát hiện thêm

| ID | Màn | Vấn đề | Mức |
|---|---|---|---|
| X-01 | Tổng quan | Thẻ Đáp ứng yêu cầu vẫn "Khác: 36, Khác: 19…" (nhãn sai) | Cao |
| X-02 | Kế hoạch | Ngân sách ¥15tr, giá ¥4,49tr → "Gợi ý điều chỉnh +233,91%". Gợi ý tăng giá 234% không hợp lý về nghiệp vụ; nên báo "giá thấp hơn ngân sách 70%: kiểm tra lại phạm vi/effort" và giới hạn gợi ý trong biên độ hợp lý | Cao |
| X-03 | Kế hoạch | Lịch không theo kế hoạch khách: RFP ghi 2027/1 bắt đầu, MVP 2027/6, Production 2027/9, nhưng "MVP/Production theo kế hoạch khách: Chưa có dữ liệu" (intake chưa trích mốc) | Cao |
| X-04 | Duyệt | Cảnh báo vẫn nhắc "vượt hạn nộp hồ sơ" (hạn nộp là hạn nộp thầu, không phải hạn dự án) | Cao |
| X-05 | Proposal | Mục "Giả định", "Ngoài phạm vi" vẫn tiêu đề tiếng Việt trong proposal tiếng Nhật; tiêu đề phụ lặp (はじめに / はじめに); chỉ 5 mục, nội dung chung chung không nhắc ngân sách, lịch, requirement của khách; còn tiêu đề lồng "PROPOSAL & HỒ SƠ · #1" | Cao |
| X-06 | Đầu trang | Nút "Chạy lại" vẫn là nút chính màu xanh lớn | TB |
| X-07 | Giải pháp / Kế hoạch | Thẻ effort xuất hiện ở cả 2 tab | TB |
| X-08 | Console | 3 lỗi 409 khi mở trang hồ sơ | TB |
| X-09 | Báo giá | Đơn giá offshore quy đổi khoảng ¥21.000/man-day (≈ ¥430.000/người-tháng), thấp so với mặt bằng offshore VN cho khách Nhật; nên rà lại rate card giả lập | Thấp |
| X-10 | Đầu trang | Thanh tiến trình hiện "Khả thi & rủi ro: Hoàn tất" nhưng không có rủi ro nào | Thấp |

**Ghi chú:** các mục L3-03, L3-04, L3-07, L3-09, L3-11, L3-13 trong `review_luot3.md` được Đợt 5 báo đã sửa nhưng **vẫn còn** trên bản chạy thật (X-01, X-06, X-07, mục 9, 12, 18 ở trên). Cần kiểm tay sau mỗi đợt.

## 3. Ưu tiên (hạn nộp 16/10)

| Ưu tiên | Nhóm | Mục |
|---|---|---|
| **P0: phải sửa** | Lỗi + nghiệp vụ sai | 1, 7, 18 (bảng trống), X-01, X-02, X-03, X-04, X-05, 5 (man-day), 15 (ngày bắt đầu) |
| **P1: làm tiếp** | Màn Kế hoạch (điểm nhấn demo) | 11, 12, 13, 14, 10, X-07 |
| **P1** | Tạo hồ sơ + Tổng quan | 2, 3, 4, 6 |
| **P1** | Giải pháp | 8, 9 |
| **P2** | Proposal + Duyệt | 16, 17 |
| **P2** | Cài đặt | 18 (template, logo, công ty, nội dung chuẩn, case study, Bid/No-bid) |

Gợi ý điều chỉnh lịch 5 ngày: thay Đợt 6b bằng **Đợt 7 (P0)** + **Đợt 8 (Kế hoạch, Tạo hồ sơ, Tổng quan, Giải pháp)**; **Đợt 9 (Proposal, Duyệt, Cài đặt)** làm nếu còn thời gian; slide PowerPoint, dịch proposal và sơ đồ kiến trúc của 6b gộp vào Đợt 9 hoặc bỏ. Chạy LLM thật ngày 15/10 giữ nguyên.

## 4. Prompt `/workflow`

Chuẩn bị: upload file này thành `docs/ui/review_luot4.md`, ảnh `ui_v4/` thành `docs/ui_v4/`.

### Đợt 7 (P0): sửa lỗi và nghiệp vụ
```
Đọc docs/ui/review_luot4.md mục 1, 2, 3. Làm ĐỢT 7 = các mục P0:
1. Nút "+ Tạo hồ sơ" ở menu luôn rõ (mục 1).
2. Tab Giải pháp và mọi tab tự tải lại dữ liệu khi pipeline xong (theo sự kiện SSE / invalidate query), không cần F5;
   không hiện khung đỏ khi chỉ là chưa có dữ liệu (mục 7).
3. Cài đặt: sửa lệch cấu trúc giữa GET /api/settings và giao diện; bảng effort, đơn giá, hệ số hiện đủ dữ liệu, sửa và lưu được (mục 18).
4. Thẻ Đáp ứng ở Tổng quan hiện đúng nhãn ◎ / ○ / △ / × / Cần làm rõ (X-01).
5. So ngân sách: khi giá lệch ngân sách quá ±30% thì cảnh báo "kiểm tra lại phạm vi/effort", gợi ý điều chỉnh giá chỉ trong
   khoảng -30%..+30% (X-02).
6. Intake trích mốc lịch khách (bắt đầu, MVP, Production) từ RFP; lịch mặc định bắt đầu theo mốc khách; form lịch có ô
   "Ngày bắt đầu dự án" (mục 15, X-03).
7. Bỏ mọi so sánh lịch dự án với hạn nộp hồ sơ; chỉ so với mốc khách (X-04).
8. Proposal: mọi tiêu đề mục theo ngôn ngữ khách (前提条件, 対象外...), bỏ tiêu đề phụ lặp, đủ 8 mục (はじめに, ご要件の理解,
   提案概要, 進め方, スケジュール, 体制, 前提条件・対象外, リスク), nội dung dùng dữ liệu hồ sơ (ngân sách, mốc lịch,
   số requirement, hướng giải pháp); mock trả đúng như vậy; bỏ tiêu đề lồng trong tab (X-05).
9. Đổi "ngày công" thành "man-day" ở mọi nơi hiển thị (mục 5).
Thứ tự: backend-dev (3, 5, 6, 7, 8) → frontend-dev (1, 2, 4, 9 và phần giao diện của 3, 6, 8) → tester đi luồng mẫu Nhật,
ghi docs/ui/dot7_check.md với số liệu thật cho từng mục → reviewer ghi docs/ui/dot7_review.md.

Quy tắc: giữ LLM_PROVIDER=mock; tuân thủ AGENTS.md (LLM không sinh con số); nhãn tiếng Việt, không hiện mã thô; code dễ
đọc. Chạy mỗi lệnh test/build tối đa 2 lần; nếu output bị rtk rút gọn hoặc báo lạ thì đọc log trong [full output: ...] hoặc
chạy background. Không tạo ảnh hay bằng chứng giả; mục nào không kiểm được trên trình duyệt thì ghi rõ. Cho tôi xem kế hoạch trước khi chạy.
```

### Đợt 8 (P1): Kế hoạch, Tạo hồ sơ, Tổng quan, Giải pháp
```
Đọc docs/ui/review_luot4.md mục 1. Ảnh mẫu docs/ui_reference/ (06_ke_hoach_bao_gia, 03_tong_quan, 05_giai_phap,
01_tao_ho_so), ảnh hiện tại docs/ui_v4/. Làm ĐỢT 8:
A. Tab Kế hoạch & báo giá (frontend-dev, backend-dev khi cần API):
   - Bảng "Nhân sự dự kiến": số người theo vai trò (PM, BA, BrSE, AI, BE, FE, QA, Infra) theo giai đoạn, sửa được; nút
     "Gợi ý theo effort"; đổi số người → tính lại lịch bằng code (không gọi AI) (mục 13, 14).
   - Master schedule: ngày bắt đầu, buffer, go/no-go, mốc khách, ngày nghỉ trên một hàng gọn; Gantt THEO TUẦN cho cả dự án,
     nhãn dòng là tên task, cuộn ngang, đánh dấu mốc và khoảng go/no-go (mục 11, 15).
   - Bảng WBS sửa trực tiếp trong dòng: man-day là ô input số, vai trò là select, giai đoạn là select, tên task là input;
     bỏ nút "Sửa"; nút xóa là icon thùng rác; chữ canh trái, tên dài thì "..." và hover hiện đủ; mã task không xuống dòng;
     thêm task bằng một dòng trống cuối mỗi nhóm ("+ Thêm task") và nút "+ Thêm nhóm"; lưu chung một lần, tổng và lịch tự
     tính lại (mục 12).
   - Mốc thanh toán thu gọn vào "Chi tiết báo giá"; bỏ thẻ effort trùng (mục 10, X-07).
B. Tạo hồ sơ: trong ô Nội dung yêu cầu có nút "Lấy nội dung từ file" (.txt/.md/.docx/.pdf, đổ chữ vào ô, giới hạn ký tự rõ);
   bỏ ô ngân sách nhập tay (ghi chú "tự trích từ RFP sau khi phân tích, sửa được ở tab Kế hoạch"); tiền tệ mặc định theo
   ngôn ngữ khách (ja→JPY, vi→VND, en→USD), quy đổi qua lại ở tab Kế hoạch (mục 2, 3).
C. Tổng quan: hàng thẻ chỉ số (số requirement và % đáp ứng, câu hỏi đã/tổng, man-day, giá, ngày kết thúc, trạng thái duyệt);
   thẻ câu hỏi chỉ đếm câu chưa trả lời; trang Danh sách thêm thẻ thống kê (tổng hồ sơ, đang phân tích, chờ duyệt, đã duyệt,
   đã gửi) (mục 4, 6).
D. Vòng hỏi 2 chỉ xuất hiện khi còn thông tin chặn sau vòng 1; giao diện ghi lý do có vòng 2 (mục 6).
E. Giải pháp: mock trả 4–6 rủi ro (loại, mức 1–5, mô tả, giảm thiểu) và điểm khả thi 1–5; thẻ Effort theo kiểu bảng:
   giai đoạn | bảng chuẩn (min–max) | × hệ số | = kết quả | tổng WBS | lệch %; hệ số hiện nhãn tiếng Việt và lý do (mục 8, 9).
Thứ tự: backend-dev (API nhân sự, D, E) → frontend-dev A (tuần tự) ∥ frontend-dev B+C → tester đi luồng mẫu Nhật,
ghi docs/ui/dot8_check.md → reviewer ghi docs/ui/dot8_review.md.

Quy tắc: như Đợt 7.
```

### Đợt 9 (P2, nếu còn thời gian): Proposal, Duyệt, Cài đặt
```
Đọc docs/ui/review_luot4.md mục 1. Làm ĐỢT 9:
A. Proposal: chọn ngôn ngữ (vi/en/ja) trước khi soạn; nút "Xem dạng tài liệu" mở trang xem online (khổ A4, mục lục, bìa,
   in được); dịch sang ngôn ngữ khác khi bấm, lưu bản dịch (mục 16).
B. Quy trình & phê duyệt: checklist Bid/No-bid (tiêu chí có trọng số, gợi ý tự động từ kết quả phân tích, người xác nhận),
   giai đoạn deal, phiên bản gửi khách (1.0 → 1.1 → 2.0, đánh dấu đã gửi), lịch sử hiện ghi chú khi duyệt/từ chối (mục 17).
C. Cài đặt: thêm các tab Công ty (tên, logo upload, quy tắc đặt tên file), Template (Word/Excel/PowerPoint: dùng mẫu có sẵn
   hoặc upload template riêng có kiểm tra), Nội dung chuẩn (giới thiệu công ty, bảo mật, điều khoản theo ngôn ngữ),
   Case study, Tiêu chí Bid/No-bid; dữ liệu giả lập, không dùng tên công ty thật (mục 18).
D. Nếu kịp: xuất slide PowerPoint theo ngôn ngữ khách dùng template ở mục C.
Thứ tự: backend-dev → frontend-dev (A ∥ B ∥ C nếu không đụng file chung) → tester → reviewer (docs/ui/dot9_*.md).

Quy tắc: như Đợt 7.
```

## 5. Sau các đợt
- Tự kiểm tay trên Preview từng mục P0 (không dựa vào báo cáo "đã sửa").
- Nếu muốn, đồng bộ code về máy để review lượt 5 trước khi chạy LLM thật ngày 15/10.
