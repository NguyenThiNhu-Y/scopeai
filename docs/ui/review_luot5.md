# Review lượt 5: sau Đợt 7, 8, 9

Ngày review: 12/10/2026. Code: `code_vibeflow/scopeai` (bản đồng bộ mới nhất). Ảnh: `vibeflow/ui_v5/`.

Cách kiểm: chạy test, chạy app với `LLM_PROVIDER=mock`, đi luồng trên trình duyệt (mẫu Nhật → Phân tích → trả lời câu hỏi → mở từng tab), gọi API để đối chiếu số liệu.

- Test: backend **245 passed**, frontend **11 passed**, build TypeScript sạch.
- Luồng chính chạy hết tới "Chờ duyệt kỹ thuật"; số liệu effort, WBS, báo giá nhất quán giữa các tab.

## 0. Lưu ý trước tiên: Đợt 9 mới xong phần backend

- Chỉ có `docs/ui/handoff_dot9_backend.md`. Không có `dot9_check.md` hay `dot9_review.md`.
- File frontend mới nhất sửa lúc 11/10 22:50. Không có màn nào gọi API mới của Đợt 9 (Bid/No-bid, phiên bản, dịch proposal).
- Khả năng 1: workflow dừng sau bước backend. Khả năng 2: đồng bộ về máy chưa đủ.
- **Việc cần làm:** mở VibeFlow kiểm tra. Nếu frontend Đợt 9 đã làm mà chưa đồng bộ, đồng bộ lại rồi báo để review lại. Nếu chưa làm, chạy Đợt 10 bên dưới.

## 1. Trạng thái các mục Đợt 7 (P0)

| # | Mục | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | Nút "+ Tạo hồ sơ" ở menu luôn rõ | **Chưa** | Trên trang Tạo hồ sơ, nút vẫn là ô trắng mất chữ (nền trong suốt, chữ trắng). Ảnh `01_tao.png` |
| 2 | Tab tự tải lại khi pipeline xong | **Chưa** | Hồ sơ mới: API đã "Chờ duyệt kỹ thuật", nhưng trang vẫn "Đang phân tích" và tab Giải pháp vẫn "Chưa có hướng giải pháp" sau 20 giây. Ảnh `16_giai_phap_wait20.png` |
| 3 | Cài đặt hiện đủ bảng | **Đạt** (3 bảng cũ) | Bảng effort, đơn giá, hệ số hiện đủ. Nhưng có thêm 5 tab chỉ ghi "v1", không tên, bấm vào trống (xem mục 3) |
| 4 | Nhãn thẻ Đáp ứng | **Chưa, nặng hơn** | Thẻ ghi "Cần làm rõ: 36", "Cần làm rõ: 36", "Cần làm rõ: 0", "Cần làm rõ: 2". Thẻ KPI "Requirement 36 · 0%" dù ◎19 ○15. Nguyên nhân: frontend đọc `stats.pass` không tồn tại và cộng cả `total`, `evaluated` vào tổng |
| 5 | Gợi ý giá khi lệch ngân sách | **Đạt phần lớn** | Có cảnh báo "lệch quá ±30%, kiểm tra phạm vi/effort". "Gợi ý điều chỉnh: 30%" chưa ghi tăng hay giảm |
| 6 | Trích mốc lịch khách | **Một phần** | Tiêu đề hiện "Bắt đầu dự án: 01/01/2027". Nhưng `customer_schedule_end` = 2027-01-01 (sai, RFP ghi 9/2027), MVP/Production = trống, **lịch vẫn bắt đầu 26/10/2026**. Ô "Ngày bắt đầu" đã có, đổi sang 04/01/2027 thì tính lại đúng |
| 7 | Bỏ so lịch với hạn nộp | **Đạt** (trên giao diện) | Không còn thấy cảnh báo hạn nộp |
| 8 | Proposal 8 mục theo tiếng Nhật | **Một phần** | Đủ 8 tiêu đề tiếng Nhật. Còn: mỗi mục lặp tiêu đề 2 lần; lẫn tiếng Việt ("Không dùng AIの方向で提案します", "MVPchưa có dữ liệu、本番chưa có dữ liệu"); mỗi mục chỉ 1 câu |
| 9 | "ngày công" → "man-day" | **Đạt** | |

## 2. Trạng thái các mục Đợt 8 (P1)

| Mục | Kết quả | Ghi chú |
|---|---|---|
| Nhân sự theo vai trò, tính lại lịch | **Đạt một phần** | Sửa được số người theo vai trò. Thử qua API: Backend 3 → 1 người thì ngày kết thúc 27/05 → 06/07/2027, tức đã tính lại đúng. Chưa chia theo giai đoạn |
| Master schedule | **Đạt phần lớn** | Có ngày bắt đầu, buffer, lịch nghỉ, go/no-go, nút "Lưu & tính lại lịch". Ô mốc khách MVP/Production vẫn "Chưa có dữ liệu" |
| Gantt theo tuần | **Đạt** | Theo tuần, cuộn ngang, có vùng go/no-go. Lỗi logic: xem N1, N2 |
| WBS sửa ngay trong dòng | **Chưa** | Vẫn nút ✎ và "+ Con". Bấm ✎ chỉ tô dòng, không mở ô sửa nào (0 input). Tên task rơi xuống dòng dưới mã. Vẫn có nút "Mở trình sửa đầy đủ" |
| Thanh toán thu gọn vào báo giá | **Đạt** | |
| Tạo hồ sơ: nhập file, bỏ ngân sách, tiền tệ theo ngôn ngữ | **Đạt** | Có nút "Nhập file"; chọn mẫu Nhật thì tự chọn JPY |
| Thẻ KPI Tổng quan | **Có, nhưng sai số** | % đáp ứng = 0% (xem mục 1.4) |
| Thẻ thống kê Danh sách | **Có, chưa đúng** | Hồ sơ "Chờ duyệt kỹ thuật" không được đếm ở thẻ nào ("Đang xử lý 0"). Bảng tràn ngang, cột Hạn nộp bị cắt |
| Vòng hỏi 2 chỉ khi cần | **Chưa** | Mock vẫn luôn hỏi vòng 2. `round_two_reason_vi` = trống. Câu hỏi không có số vòng (`round` = trống), nên giao diện ghi "Vòng 2/2" mà chỉ hiện 5 câu vòng 1. **Câu vòng 2 bị mất khỏi màn hình** dù thẻ ghi 6/6 |
| Rủi ro và điểm khả thi | **Chưa** | "Chưa có rủi ro được ghi nhận", thẻ "Rủi ro lớn nhất" trống, không có điểm khả thi 1–5 |
| Bảng effort có hệ số và lý do | **Đạt một phần** | Có hệ số, giá trị, lý do tiếng Việt. Thiếu cột tổng WBS và % lệch (WBS 210 so với effort 241,5) |

## 3. Đợt 9 (phần giao diện chưa có)

| Mục | Hiện trạng |
|---|---|
| Cài đặt: Công ty, Template, Nội dung chuẩn, Case study, Bid/No-bid | Backend đã có dữ liệu. Giao diện hiện 5 nút "v1" không tên, bấm vào trống |
| Bid/No-bid ở tab Duyệt | Không có trên giao diện. **API `GET /bid-qualification` lỗi 500** khi hồ sơ chưa có tiêu chí (schema bắt buộc ít nhất 1 tiêu chí) |
| Giai đoạn deal | Có cột và bộ lọc ở Danh sách. Không có chỗ đổi giai đoạn trong hồ sơ, nên luôn "Chưa phân loại" |
| Phiên bản gửi khách 1.0 → 1.1 → 2.0 | Chỉ có dòng "Chưa có phiên bản gửi khách". Không có nút tạo phiên bản hay đánh dấu đã gửi |
| Proposal: chọn ngôn ngữ, xem online, dịch | Có 3 nút Tiếng Việt / English / 日本語, nhưng chỉ đổi tiêu đề; chọn "Tiếng Việt" vẫn hiện nội dung tiếng Nhật. Không có "Xem dạng tài liệu" (A4, bìa, mục lục) hay nút dịch |

## 4. Lỗi nghiệp vụ mới phát hiện

- **N1. MVP chạy ngay trong khoảng chờ go/no-go.** Khoảng chờ là 28/01 → 10/02/2027, nhưng task MVP đầu tiên bắt đầu 28/01. Lần chạy đầu cũng vậy: MVP bắt đầu 20/11/2026, đúng ngày bắt đầu khoảng chờ. API lại báo `earliest_mvp_start` = 25/01/2027, mâu thuẫn với chính lịch.
- **N2. Cả dự án chỉ chạy một task tại một thời điểm.**
  - Task nối đuôi nhau dù có 3 BE và 3 FE, nên lịch dài vô lý: 210 man-day thành khoảng 5 tháng.
  - ScopeAI cho các vai trò chạy song song trong cùng giai đoạn.
- **N3. Giải pháp và WBS mâu thuẫn nhau.**
  - Hướng giải pháp là "Không dùng AI", nhưng WBS có "Dựng mẫu RAG", "Huấn luyện mô hình", AI Engineer 32 man-day.
  - Nhân sự gợi ý cũng có 2 AI Engineer.
  - WBS và phân bổ nhân sự phải lấy theo hướng giải pháp.
- **N4. Báo giá hiển thị không khớp.**
  - Ô "Dự phòng (%)" hiện 0, trong khi thực tế là 20% (¥748,712).
  - "Tạm tính" bằng đúng tổng giá.
  - Ô ghi "Thuế đã gồm ¥4,941,501", trong khi chế độ là chưa gồm thuế.
  - Tab Kế hoạch ghi "Giá cố định", tab Duyệt ghi "Trọn gói".
  - Phụ phí BrSE ¥178,265 dù BrSE = 0 người.
- **N5. Trạng thái mâu thuẫn:** mọi bước ghi "Hoàn tất" nhưng trạng thái hồ sơ là "Đang phân tích" (đi kèm lỗi không tự tải lại).
- **N6. Tab Đáp ứng:**
  - Cột "Thành phần" hiện mã thô `none` ở cả 36 dòng.
  - Ghi chú chỉ lặp 3–4 câu mẫu.
- **Còn từ lượt 4:**
  - "Chạy lại" vẫn là nút xanh to nhất trang (X-06).
  - 3 lỗi 409 trên console khi mở hồ sơ đang chạy (X-08).
  - Đơn giá khoảng ¥17.000/man-day, thấp (X-09; là dữ liệu giả lập, chỉ cần ghi chú).

## 5. Ưu tiên trước khi chạy LLM thật (15/10)

| Mức | Việc | Lý do |
|---|---|---|
| P0 | N1, N2, N3, mốc lịch khách (1.6), % đáp ứng và nhãn (1.4), câu hỏi vòng 2 bị mất, tự tải lại (1.2), WBS ✎ không chạy, API Bid/No-bid lỗi 500, báo giá N4, nút sidebar (1.1) | Sai số liệu hoặc hỏng thao tác. Chạy LLM thật mà còn các lỗi này thì không đánh giá được chất lượng AI |
| P1 | Rủi ro và điểm khả thi, Proposal (tiêu đề lặp, lẫn tiếng Việt), thẻ Danh sách, cột "Thành phần", "Chạy lại" thành nút phụ | Ảnh hưởng ấn tượng khi demo |
| P2 | Giao diện Đợt 9: Cài đặt 5 tab, Bid/No-bid, phiên bản, xem proposal dạng tài liệu | Đẹp hồ sơ dự thi, không chặn luồng chính |

**Lịch đề xuất:**
- 13/10: Đợt 10 (P0 + P1).
- 14/10: Đợt 11 (P2, làm tới đâu hay tới đó) và kiểm tay trên Preview.
- 15/10: chạy LLM thật.
- 16/10: đóng băng và nộp.

## 6. Prompt `/workflow`

Chuẩn bị: upload file này thành `docs/ui/review_luot5.md`, ảnh `ui_v5/` thành `docs/ui_v5/`.

### Đợt 10 (P0 + P1): sửa số liệu, lịch, thao tác hỏng
```
Đọc docs/ui/review_luot5.md (mục 1, 2, 4). Ảnh hiện tại docs/ui_v5/. Làm ĐỢT 10:
A. Lịch (backend-dev):
   1. Task MVP không được bắt đầu trước go_no_go_end; Production sau khi MVP xong (N1). Thêm test.
   2. Các vai trò trong cùng giai đoạn chạy song song; thời lượng task = man-day / số người của vai trò; giai đoạn kết
      thúc khi task cuối xong (N2). Thêm test: 210 man-day với PM3 BA1 AI2 BE3 FE3 QA2 Infra1 phải ngắn hơn rõ so với
      chạy tuần tự.
   3. Intake trích đủ mốc khách (bắt đầu, MVP, Production; RFP mẫu Nhật: 2027/1, 2027/6, 2027/9). Lịch mặc định bắt đầu
      từ mốc bắt đầu của khách; cảnh báo nếu MVP/Production trễ hơn mốc khách. Sửa customer_schedule_end đang sai.
B. Nhất quán giải pháp (backend-dev): WBS và gợi ý nhân sự lấy theo hướng giải pháp; hướng "Không dùng AI" không có task
   RAG/huấn luyện mô hình và không có AI Engineer (N3). Mock trả 4–6 rủi ro (loại, mức 1–5, mô tả, giảm thiểu) và điểm
   khả thi 1–5.
C. Câu hỏi (backend-dev + frontend-dev): mỗi câu có số vòng; vòng 2 chỉ khi còn thông tin chặn, kèm round_two_reason_vi;
   mock mẫu Nhật dừng ở vòng 1 nếu đã trả lời đủ. Giao diện hiện đủ mọi câu theo từng vòng (hiện đang mất câu vòng 2).
D. API Bid/No-bid: GET /bid-qualification trả 200 với tiêu chí mặc định từ Cài đặt khi hồ sơ chưa có (đang lỗi 500).
E. Frontend-dev:
   1. Thẻ "Requirement" = số requirement · % đáp ứng = (◎ + ○) / tổng đã đánh giá; thẻ Đáp ứng hiện đúng ◎ ○ △ × Cần làm
      rõ, không hiện total/evaluated (mục 1.4). Viết test cho hàm tính.
   2. Sau khi gửi câu trả lời và khi pipeline xong: trạng thái hồ sơ và mọi tab tự tải lại (invalidate query theo sự
      kiện, hoặc poll mỗi 3 giây khi status đang chạy). Không gọi API effort/quotation/schedule khi chưa có (bỏ lỗi 409).
   3. Nút "+ Tạo hồ sơ" ở menu: luôn nền xanh chữ trắng, kể cả khi đang ở trang Tạo hồ sơ.
   4. WBS: bỏ nút ✎ (hiện bấm không làm gì) và "Mở trình sửa đầy đủ"; tên task, vai trò, giai đoạn, man-day sửa trực
      tiếp trong dòng; mã và tên cùng một dòng; "+ Thêm task" cuối mỗi nhóm; một nút "Lưu thay đổi" cho cả bảng, lưu
      xong tổng và lịch tự tính lại.
   5. Báo giá: ô Dự phòng (%) hiện đúng giá trị đã lưu (20); Tạm tính = trước dự phòng; dòng thuế ghi đúng theo chế độ
      thuế; dùng một tên mô hình giá ở mọi tab; gợi ý ghi rõ "tăng/giảm x%".
   6. Proposal mock: mỗi mục một tiêu đề, không lặp; không lẫn tiếng Việt trong bản tiếng Nhật; mỗi mục 3–5 câu dùng dữ
      liệu hồ sơ (ngân sách, mốc lịch, số requirement, hướng giải pháp).
   7. Danh sách: hồ sơ "Chờ duyệt kỹ thuật/giá" được đếm ở thẻ "Chờ duyệt"; bảng không tràn ngang ở 1280px.
   8. Tab Đáp ứng: cột "Thành phần" hiện nhãn tiếng Việt hoặc "—", không hiện "none". "Chạy lại" thành nút phụ (viền).
Thứ tự: backend-dev (A, B, C phần API, D) → frontend-dev (C phần giao diện, E) → tester đi luồng mẫu Nhật trên Preview,
ghi docs/ui/dot10_check.md: với từng mục ghi số liệu thật (ngày bắt đầu/kết thúc lịch, ngày MVP đầu tiên so với
go_no_go_end, % đáp ứng, số câu hỏi từng vòng, mã HTTP bid-qualification) → reviewer ghi docs/ui/dot10_review.md.

Quy tắc: giữ LLM_PROVIDER=mock; tuân thủ AGENTS.md (LLM không sinh con số); nhãn tiếng Việt, không hiện mã thô; code dễ
đọc. Chạy mỗi lệnh test/build tối đa 2 lần; nếu output bị rtk rút gọn hoặc báo lạ thì đọc log trong [full output: ...] hoặc
chạy background. Không tạo ảnh hay bằng chứng giả; mục nào không kiểm được trên trình duyệt thì ghi rõ. Cho tôi xem kế hoạch trước khi chạy.
```

### Đợt 11 (P2): hoàn thiện giao diện Đợt 9
```
Đọc docs/ui/review_luot5.md mục 3 và docs/ui/handoff_dot9_backend.md (API đã có). Làm ĐỢT 11, chỉ frontend, dùng API sẵn có:
A. Cài đặt: 5 tab có tên tiếng Việt: Công ty (tên, quy tắc đặt tên file), Template (Word/Excel: mẫu có sẵn, trạng thái
   hợp lệ), Nội dung chuẩn (theo ngôn ngữ vi/en/ja), Case study (danh sách, thêm/sửa/xóa), Tiêu chí Bid/No-bid (tiêu chí,
   trọng số, báo lỗi nếu tổng khác 100). Sửa và lưu được.
B. Tab Quy trình & phê duyệt: thẻ Bid/No-bid (tiêu chí, trọng số, điểm gợi ý từ phân tích, người xác nhận, nút Xác nhận;
   gợi ý chỉ để tham khảo); chọn giai đoạn deal; khu "Phiên bản gửi khách": nút "Tạo phiên bản" (1.0 → 1.1 → 2.0), "Đánh
   dấu đã gửi", danh sách phiên bản kèm ngày gửi và ghi chú.
C. Proposal: chọn ngôn ngữ trước khi soạn; nút ngôn ngữ đổi cả nội dung (dùng translations; chưa có bản dịch thì hiện nút
   "Dịch sang ..."); nút "Xem dạng tài liệu" mở trang A4 có bìa, mục lục, in được.
Thứ tự: frontend-dev (A ∥ B ∥ C nếu không đụng file chung) → tester ghi docs/ui/dot11_check.md → reviewer ghi
docs/ui/dot11_review.md.

Quy tắc: như Đợt 10.
```

## 7. Sau mỗi đợt
- Tự kiểm tay trên Preview các mục P0, đặc biệt: lịch MVP sau go/no-go, % đáp ứng, câu hỏi vòng 2, WBS sửa trong dòng.
- Đồng bộ code về máy để review lượt 6 trước ngày 15/10.
