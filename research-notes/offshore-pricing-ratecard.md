# Định giá trong offshore phần mềm Việt Nam – Nhật Bản (Vietnam–Japan software offshore pricing)

*Memo nghiên cứu — research subagent (deep-research harness). Ngày: 2026-10-09.*
*Ngôn ngữ: tiếng Việt. Mọi số liệu đều có nguồn inline (URL). Các con số "man" = vạn yên (10.000 JPY)/tháng.*

---

## 1. Mô hình hợp đồng (contract models): 請負 (fixed-price) vs 準委任 (T&M/quasi-mandate) vs hybrid

### 1.1 Hai kiểu tính chi phí cơ bản

Bài tổng hợp của [Linnoedge (2026-06-17)](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/) chia chi phí offshore thành 2 kiểu theo hình thức hợp đồng:

- **Lab-type (ラボ型, tương đương 準委任 / quasi-mandate / T&M)**: tính theo người-tháng (人月) — *tháng × số người × thời gian*. Trả phí cố định hàng tháng theo số người làm việc (không phụ thuộc sản phẩm hoàn thành). Không có trách nhiệm hoàn thành (完成責任) thuộc về bên đặt hàng. Phù hợp khi spec còn thay đổi, dự án trung–dài hạn, sản phẩm cần nuôi dưỡng. Ưu điểm: ngân sách dễ đọc, hóa đơn ít bị đội khi thay đổi yêu cầu.
- **Fixed-price (受託 / 請負)**: báo giá trọn gói cho một deliverable; bên nhận thầu chịu trách nhiệm hoàn thành. Phù hợp khi spec đã chốt, dự án ngắn hạn, phạm vi tách rõ. Nhược điểm: mỗi lần thay đổi spec là phát sinh báo giá thêm.

Tiêu chí chọn (theo Linnoedge): "spec của mình có còn động không" — còn động thì lab-type, đã chốt thì fixed-price. Bài [Enlyt (2026-05-18)](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection) cũng phân chia tương tự: 受託型 hợp khi "cái muốn làm đã rõ ràng" (ví dụ landing page, màn hình quản trị nội bộ); ラボ型 hợp với dịch vụ to C cần cải tiến liên tục (EC, app thành viên, LINE mini app).

### 1.2 Chi tiết pháp lý: 準委任 vs 請負 trong offshore

Theo [offshore-kaihatsu.com (cập nhật 2024-12-03)](https://www.offshore-kaihatsu.com/contents/general/consignment.php):
- **準委任**: trách nhiệm hoàn thành thuộc về **bên đặt hàng** (発注者); bên nhận có thể dừng giữa chừng nếu bồi thường; linh hoạt thay đổi spec, trả theo thời gian/tài nguyên dùng; hợp cho dự án dài hạn, yêu cầu chưa chốt, nhiều dự án song song.
- **請負**: trách nhiệm hoàn thành thuộc **bên nhận thầu**; vendor thường ngại nhận 請負, và **"nếu làm 請負 thì giá sẽ đắt hơn"** (料金が割高) vì vendor phải cộng rủi ro vào giá.

### 1.3 Tỷ trọng thực tế: lab-type là xu hướng chủ đạo

- Theo [Kaopiz (2025-11-14)](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), 白書2025 ghi **ラボ型 chiếm 63% tổng hợp đồng**; bài [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection) dẫn cùng 白書2025 ghi **45% là lab-type (nhiều nhất)** và thời gian hợp tác "10 năm+" chiếm 44%. Hai con số lệch nhau (63% vs 45%) — cả hai đều tự nhận trích 白書2025; cần báo cáo kèm nguồn gốc và lưu ý độ tin cậy. Điểm chung: lab-type là hình thức phổ biến nhất, hợp tác dài hạn là chủ đạo.
- 白書2025 (qua Enlyt): 65% doanh nghiệp đang dùng offshore trả lời "sẽ mở rộng thêm", 0% có kế hoạch thu hẹp.

### 1.4 Hybrid (kết hợp)

Bài phân tích của [LeO Nguyen trên LinkedIn (2026-04-17)](https://www.linkedin.com/pulse/why-tm-vs-fixed-price-decision-could-make-break-your-next-leo-nguyen-3uffc) — tác giả là nhà điều hành offshore (bài liên kết tới kaopiz.com) — đề xuất mô hình hybrid: **pha discovery (khảo sát/định nghĩa yêu cầu) theo fixed-price + pha delivery theo T&M (Agile)**, hoặc T&M có trần NTE (not-to-exceed) để vừa linh hoạt vừa chặn chi phí. Bài cũng dẫn nghiên cứu 2017 trên International Journal of Project Management: hợp đồng fixed-price có tương quan thống kê với rủi ro thất bại dự án cao hơn T&M; ~90% dự án phần mềm hiện đại cần thay đổi scope đáng kể trong lúc chạy.

---

## 2. Rate card: bảng giá người-tháng (人月単価) theo vai trò — thị trường VN–JP

### 2.1 Bảng chuẩn ngành: オフショア開発白書 2025 (nguồn gốc: offshore-kaihatsu.com)

Nguồn gốc chính của các con số "thị trường" là **オフショア開発白書 (White Paper) 2025**, được công bố qua [offshore-kaihatsu.com — bảng so sánh 6 nước (cập nhật 2026-02-13)](https://www.offshore-kaihatsu.com/faq/tanka.php) và [trang giá Việt Nam 2026](https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/). Giá Việt Nam (1人月, JPY):

| Vai trò | 2025 (白書2025) | YoY |
|---|---|---|
| Programmer (PG) | **40,1 man** | +1,8% |
| Senior engineer | **50,0 man** | +3,5% |
| Bridge SE (BrSE) | **59,0 man** | ±0% |
| PM | **71,4 man** | +2,0% |

Xu hướng: PG Việt Nam ổn định (2023: 40,22 man → 2024: 39,4 → 2025: 40,1), trong khi trung bình 6 nước tụt từ 45,3 man (2024) xuống 34 man (2025) do Ấn Độ (-29,6%) và Philippines (-13,5%) giảm mạnh (nguồn: [offshore-kaihatsu.com tanka](https://www.offshore-kaihatsu.com/faq/tanka.php)).

⚠️ Lưu ý quan trọng từ [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/): hầu hết các công ty Nhật đều **trích cùng một 白書** nên các con số "thị trường" khá đồng nhất — đây là giá tham khảo, không phải giá thực của từng vendor.

### 2.2 Bảng giá chi tiết theo vai trò + cấp độ + tiếng Nhật (Kaopiz, 2026-05)

[Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/) công bố bảng giá riêng (dựa trên thực tế + 白書2025), cho thấy **trình độ tiếng Nhật (JLPT) là biến số chính làm đổi giá**:

| Vai trò | Cấp độ | JLPT | 人月単価 (man) |
|---|---|---|---|
| Frontend | Junior | N3 | 25–35 |
| Frontend | Senior | N2 | 35–50 |
| Backend | Junior | N3 | 30–40 |
| Backend | Senior | N2 | 40–60 |
| Fullstack | Middle | N3 | 35–50 |
| Fullstack | Senior | N2 | 45–65 |
| QA/Tester | Junior | none–N3 | 20–30 |
| QA/Tester | Senior | N3–N2 | 30–40 |
| QA Automation | Middle | N3 | 30–45 |
| QA Automation | Senior | N2 | 40–55 |
| **BrSE** | Senior | **N2–N1** | **50–80** |
| **PM** | Senior | **N2–N1** | **60–100** |
| Tech Lead | Senior | N2 | 50–80 |
| Architect | Expert | N2–N1 | 70–110 |

Điểm chốt: **giá tăng mạnh theo vai trò cần tiếng Nhật** (BrSE/PM/Architect); ngược lại, giảm yêu cầu tiếng Nhật ở vị trí implement/test là cách tối ưu chi phí.

### 2.3 Giá theo giờ (thị trường offshore nói chung, USD)

[Romulus Digital (2025-09-04)](https://romulus.digital/our-article/why-everyones-talking-about-it-outsourcing-vietnam-in-2025/): developer Việt Nam tính theo giờ — **junior $15–20/h, mid $20–30/h, senior $25–35/h**; giá thấp hơn tới **50% so với Ấn Độ/Philippines** (dẫn Dirox 2025); tiết kiệm lao động 30–70% so với Bắc Mỹ/Tây Âu. Lưu ý: đây là góc nhìn vendor (thiên vị), dùng để tham chiếu.

### 2.4 Rate card thực của một vendor Nhật–VN (Linnoedge)

[Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/) công bố giá thực đang dùng (2026-07): Junior 40 man–, Middle 55 man–, Senior 70 man–, **PM/BrSE 60 man–** (tháng, chưa thuế, "all-in" gồm quản lý + chất lượng + văn phòng). Ví dụ team 3 người (BrSE 60 + Middle 55 + Senior 70) = **185 man/tháng**. So sánh: tuyển nội địa Nhật ~70 man/tháng + chi phí tuyển 100–150 man.

### 2.5 Tính toán mẫu cho một dự án

[Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection) ví dụ: team 3 người (Senior 50,0 + PG 40,1 + BrSE 59,0) × 4 tháng ≈ **596 man** (~149 man/tháng) theo giá 白書2025.

---

## 3. So sánh Việt Nam vs Nhật Bản và các nước — mức chiết khấu điển hình

### 3.1 Bảng 6 nước (白書2025, qua [offshore-kaihatsu.com](https://www.offshore-kaihatsu.com/faq/tanka.php))

| Nước | PG | Senior | BrSE | PM |
|---|---|---|---|---|
| **Việt Nam** | **40,1** | **50,0** | **59,0** | **71,4** |
| Philippines | 37,2 | 47,5 | 60,5 | 63,5 |
| Ấn Độ | 37,5 | 45,0 | 60,0 | 67,5 |
| Bangladesh | 33,8 | 52,5 | 82,5 | 72,5 |
| Myanmar | 27,5 | 40,0 | 40,0 | 57,5 |
| Trung Quốc | 58,3 | 71,7 | 75,8 | 84,6 |

### 3.2 Việt Nam so với Nhật nội địa

- [offshore-kaihatsu.com (trang giá VN)](https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/): chi phí offshore Việt Nam = **khoảng 1/3 đến 1/2 chi phí làm tại Nhật** ("日本国内の約1/3〜1/2").
- [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/) (dẫn 秋霜堂 2026): PG nội địa Nhật ~70–90 man/tháng (mức trung cấp) — tức **giá VN (~40 man) ≈ 45–57% giá Nhật, chiết khấu ~45–55%**.
- [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection) dẫn 白書2025: mức giảm chi phí phổ biến khi offshore là **31–50%**.
- Điểm hòa vốn: offshore chỉ rẻ hơn tổng thể từ ~**12–15 người-tháng** (秋霜堂 2026, qua Linnoedge; ¥145 → 8–10, ¥175 → 18–20 người-tháng); TCO giảm thực tế chỉ 20–30%. Dự án quá nhỏ thì offshore lại đắt.

### 3.3 Vị thế Việt Nam

- Việt Nam giữ **43% thị phần đơn hàng offshore của doanh nghiệp Nhật** (白書2025, qua [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/) và [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection)).
- Không phải rẻ nhất (Myanmar/Bangladesh rẻ hơn) nhưng cân bằng: giá + tiếng Nhật + kinh nghiệm + chênh lệch múi giờ 2h ([Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).
- 白書2025 (qua Enlyt): yếu tố thành công số 1 của offshore là "giao tiếp", số 2 là "năng lực BrSE"; tiêu chí chọn vendor quan trọng nhất là "trình độ tiếng Nhật".

---

## 4. Vai trò BrSE (Bridge System Engineer) — cầu nối giao tiếp

### 4.1 BrSE là gì, tại sao tồn tại

- Định nghĩa chuẩn từ [offshore-kaihatsu.com](https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/): BrSE đứng giữa khách hàng Nhật và team phát triển nước ngoài, vượt rào cản ngôn ngữ–văn hóa–tập quán kinh doanh; **không chỉ là phiên dịch** mà còn có kiến thức kỹ thuật + kỹ năng quản lý, chịu trách nhiệm chất lượng và tiến độ.
- [TalentClip TIMES (2022-09-01)](https://www.talent-clip.jp/media/role-and-necessity-of-bridge-personnel-issues-in-overseas-expansion-and-tips-for-recruitinghuman-resources): BrSE là "bridge personnel" chuyên cho offshore — truyền đạt chính xác thiết kế/yêu cầu/issue sang team địa phương và gánh phần tổng hợp hai phía; 4 kỹ năng cần: ngôn ngữ, giao tiếp, hiểu văn hóa–thương mại hai nước, tư vấn.
- Vì sao tồn tại: rào cản ngôn ngữ/văn hóa là nguồn gốc chính của hiểu sai yêu cầu — mà theo CMU SEI (dẫn qua [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)), >50% nguyên nhân rework (vốn chiếm 40–70% ngân sách dự án) là "yêu cầu bị hiểu sai". BrSE là lớp phòng thủ chống lại chi phí này.

### 4.2 Chi phí BrSE — premium thực tế

- **Giá bán**: BrSE ~59 man/tháng (白書2025) — cao hơn PG (~40 man) **~47%** và cao hơn senior (~50 man) **~18%** (tự tính từ bảng 2.1). Bảng Kaopiz: BrSE 50–80 man, PM 60–100 man.
- **Giá vốn**: lương BrSE tại VN median **$1.630/tháng** (TopDev 2024-2025, dẫn qua [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)) ≈ 24,5 man (tỷ giá 150 JPY/USD).
- Trong rate card [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/): PM/BrSE (60 man) cao hơn middle (55 man) ~9%.
- **Về claim "BrSE cộng 10–20% premium"**: chưa tìm thấy nguồn trực tiếp nào nói BrSE cộng đúng 10–20% lên đơn giá. Số liệu thực cho thấy premium của BrSE so với developer dao động **~10–50% tùy bảng giá** (18% so với senior theo 白書; ~9% so với middle theo Linnoedge; BrSE 50–80 vs backend senior 40–60 theo Kaopiz). Con số "10–20%" chỉ nên dùng như ước lượng thô, chưa được xác nhận trực tiếp.
- BrSE có thể tính **phí riêng** ngoài đơn giá: theo [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), "通訳・BrSEの追加配置" (bố trí thêm BrSE/phiên dịch) là mục **thường tính phí riêng** khi dự án nhiều cuộc họp tiếng Nhật.

---

## 5. Cơ cấu chi phí, contingency, biên lợi nhuận

### 5.1 Công thức giá bán (sell price = cost stack)

[Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/): **人月単価 (giá bán 40–70 man) = lương VN (giá vốn) + quản lý (PM/direction) + văn phòng/tuyển dụng/đào tạo + hệ thống chất lượng (test/review) + lợi nhuận**. Vendor báo giá thấp bất thường thường "mỏng" lớp quản lý hoặc chất lượng. Tự suy ra từ dữ liệu: BrSE giá vốn ~24,5 man vs giá bán 59 man → hệ số nhân ~2,4×; PG giá vốn ~20 man (median $1.340) vs giá bán 40,1 man → ~2× (đây là suy luận từ 2 nguồn, cần thận trọng).

### 5.2 Contingency / dự phòng

- Theo [LeO Nguyen (LinkedIn, 2026-04)](https://www.linkedin.com/pulse/why-tm-vs-fixed-price-decision-could-make-break-your-next-leo-nguyen-3uffc): **hợp đồng fixed-price thường cộng contingency buffer 15–30%** trên chi phí kỳ vọng thực tế; nếu dự án chạy êm, khách trả thừa cho rủi ro không xảy ra. [Classic Informatics](https://www.classicinformatics.com/blog/fixed-price-vs-time-and-materials) xác nhận: báo giá fixed-price luôn bao gồm contingency buffer cho rủi ro scope mà vendor nhận gánh.
- [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/): 請負型 (fixed-price) "có xu hướng bị cộng thêm chi phí định nghĩa yêu cầu và risk buffer" (要件定義やリスクバッファが上乗せされやすい); ラボ型 giữ giá ổn định hơn.

### 5.3 Chi phí ẩn / TCO

- Chi phí thực có thể cao hơn đơn giá niêm yết **50–66%** (SmartDev 2026, dẫn qua [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).
- Khởi động: team offshore đạt 85% năng suất sau **4,6 tháng**; tháng đầu chỉ **40–50%** năng suất (SmartDev 2026, qua Linnoedge).
- Rework chiếm 40–70% ngân sách dự án; >50% do hiểu sai yêu cầu (CMU SEI, qua Linnoedge).
- 47% thất thoát outsourcing do mismatch năng lực, không phải giá (Accelerance 2024, qua [Romulus](https://romulus.digital/our-article/why-everyones-talking-about-it-outsourcing-vietnam-in-2025/)).
- Các khoản thường tính phí riêng (ngoài đơn giá): BrSE/phiên dịch bổ sung, hạ tầng cloud/VPN/thiết bị, test chuyên sâu (tải, bảo mật, E2E), overtime/短納期 ([Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection)).

### 5.4 Utilization & gross margin chuẩn ngành

**Không tìm thấy nguồn trực tiếp** công bố tỷ lệ utilization chuẩn hay gross margin chuẩn riêng cho vendor offshore VN–JP (đã thử các từ khóa tiếng Việt "biên lợi nhuận gộp công ty outsourcing", tiếng Nhật "オフショア 会社 粗利率 稼働率" — chỉ ra tài liệu tài chính chung). Ghi nhận là khoảng trống dữ liệu; các con số gần nhất có thể suy ra: hệ số nhân giá bán/giá vốn ~2–2,4× (mục 5.1) hàm ý gross margin thô ~50–60% trước chi phí quản lý — đây là suy luận, không phải số liệu công bố.

---

## 6. Tiền tệ & điều kiện thanh toán (請求・支払条件)

### 6.1 Đồng tiền hợp đồng & tỷ giá

- [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/) (dẫn TopDev 2024–2025): **điều kiện hợp đồng bằng JPY hay USD ảnh hưởng trực tiếp đến chi phí cuối cùng qua biến động tỷ giá** — đây là 1 trong 5 yếu tố chính tác động đơn giá.
- [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/) quy đổi lương VN sang JPY theo tỷ giá ~150 JPY/USD (bản EN dùng 160) — cho thấy tỷ giá là tham số nhạy cảm trong mọi phép tính.
- Điểm hòa vốn offshore thay đổi theo tỷ giá: ¥145 → 8–10 người-tháng, ¥175 → 18–20 người-tháng (秋霜堂 2026, qua [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).

### 6.2 Thuế & khấu trừ khi thanh toán quốc tế

[Linnoedge FAQ](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/) (Q7): giao dịch nước ngoài **về nguyên tắc không chịu thuế tiêu dùng Nhật** (国外取引は原則不課税), nhưng tùy nội dung dịch vụ có thể phát sinh **thuế thu nhập khấu trừ tại nguồn (源泉所得税)**; hiệp định tránh đánh thuế hai lần (VN–JP) có thể áp dụng — nên hỏi chuyên gia thuế quốc tế trước khi ký.

### 6.3 Thông lệ thanh toán Nhật Bản (áp dụng cho hợp đồng với vendor VN)

- Thông lệ phổ biến của Nhật: **月末締め翌月末払い** — chốt công cuối tháng, thanh toán cuối tháng sau (payment site ~30 ngày) ([zeimu.cloud, 2026-07-05](https://zeimu.cloud/kaisetsu/seikyu-invoice/shiharai-site)).
- Luật chống trả chậm: theo 下請法 (luật bảo vệ nhà thầu phụ) và フリーランス新法, thời hạn thanh toán tối đa **60 ngày** kể từ ngày nhận hàng/dịch vụ ([gyoumuitakukeiyakusho.com, 2023-08-13](https://www.gyoumuitakukeiyakusho.com/contract-payment-date-how-to-write/); [syncstar, 2026-07-04](https://outsourcing.syncstar.jp/blog/freelance-law-payment-deadline)).
- ⚠️ Chưa tìm thấy nguồn offshore-specific công bố điều khoản thanh toán chuẩn giữa khách Nhật và vendor VN (milestone %, kỳ hạn). Các nguồn trên là thông lệ chung của Nhật; cần coi là nền tảng, không phải xác nhận trực tiếp cho giao dịch VN–JP.

---

## 7. Nguồn dữ liệu lương & thị trường (để đối chiếu rate card)

- **TopDev "Vietnam IT Market Report 2024–2025 / Vietnam IT & Tech Talent Landscape"** — [trang báo cáo chính thức](https://topdev.vn/page/vietnam-it-market-reports/) (PDF EN/VI miễn phí). Dữ liệu dùng trong memo (median lương theo vai trò, 2.324 respondents; IT services market $2,07B 2024 → $3,2B 2028, CAGR 11,51%; ~560.000 nhân lực IT; 55–60k sinh viên tốt nghiệp/năm) được [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/) và [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/) trích dẫn.
- **Statista** (qua [LinkedIn pulse](https://www.linkedin.com/pulse/why-should-you-choose-work-vietnam-outsourcing-minh-châu-ivy--bevrc)): IT Services VN $2,07 tỷ (2024), riêng IT Outsourcing ~$0,70 tỷ.
- **BritCham Vietnam "IT&AI report" (2024-09)**: [PDF](https://britchamvn.com/wp-content/uploads/2024/10/ITAI-report-Sep-2024.pdf).
- **オフショア開発白書 2025** (nguồn gốc [offshore-kaihatsu.com](https://www.offshore-kaihatsu.com/faq/tanka.php) + [bản PDF 白書2025](https://41690687.fs1.hubspotusercontent-na2.net/hubfs/41690687/offshore/%E3%80%8E%E3%82%AA%E3%83%95%E3%82%B7%E3%83%A7%E3%82%A2%E9%96%8B%E7%99%BA%E7%99%BD%E6%9B%B8\(2025%E5%B9%B4%E7%89%88\)%E3%80%8F.pdf) — bảng giá 6 nước, thị phần 43%, tỷ trọng lab-type).
- JETRO "2023年度 海外進出日系企業実態調査": ~30% DN Nhật tại VN coi "tăng nhân công" là rủi ro kinh doanh (dẫn qua [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).

---

## 8. Key claims (xếp theo độ quan trọng)

1. **Giá người-tháng chuẩn ngành VN–JP 2025 (白書2025)**: PG 40,1 man, Senior 50,0 man, BrSE 59,0 man, PM 71,4 man — gần như mọi công ty Nhật đều trích cùng bảng này nên chỉ là giá tham khảo, không phải giá thực từng vendor ([offshore-kaihatsu.com](https://www.offshore-kaihatsu.com/faq/tanka.php), [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).
2. **Chiết khấu offshore VN so với Nhật ~45–55%** (giá VN ≈ 1/3–1/2 giá nội địa Nhật; PG VN 40 man vs Nhật 70–90 man); mức giảm chi phí phổ biến 31–50% ([offshore-kaihatsu.com](https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/), [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/), [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection)).
3. **Hai mô hình hợp đồng chính**: lab-type/準委任 (trả theo người-tháng, không có trách nhiệm hoàn thành, hợp spec còn động) và fixed-price/請負 (trọn gói, vendor chịu trách nhiệm hoàn thành, giá đắt hơn vì cộng risk buffer); lab-type đang là hình thức phổ biến nhất (63% theo Kaopiz / 45% theo Enlyt — cùng trích 白書2025 nhưng lệch nhau) ([Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/), [offshore-kaihatsu.com consignment](https://www.offshore-kaihatsu.com/contents/general/consignment.php), [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection)).
4. **Fixed-price thường cộng contingency buffer 15–30%** trên chi phí kỳ vọng; hybrid "fixed-price discovery + T&M delivery" hoặc T&M có trần NTE là giải pháp dung hòa ([LeO Nguyen/LinkedIn](https://www.linkedin.com/pulse/why-tm-vs-fixed-price-decision-could-make-break-your-next-leo-nguyen-3uffc), [Classic Informatics](https://www.classicinformatics.com/blog/fixed-price-vs-time-and-materials), [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/)).
5. **BrSE là vai trò cầu nối đặc thù VN–JP** (không chỉ phiên dịch mà quản lý chất lượng/tiến độ); giá bán 59 man (cao hơn PG ~47%, cao hơn senior ~18%), giá vốn lương VN chỉ ~$1.630/tháng; claim "premium 10–20%" chưa có nguồn trực tiếp xác nhận — premium thực tế dao động ~10–50% tùy bảng giá ([offshore-kaihatsu.com](https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/), [TalentClip](https://www.talent-clip.jp/media/role-and-necessity-of-bridge-personnel-issues-in-overseas-expansion-and-tips-for-recruitinghuman-resources), [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/), [Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/)).
6. **Giá bán = lương VN (giá vốn) + quản lý + văn phòng/tuyển dụng + chất lượng + lợi nhuận**; hệ số nhân giá bán/giá vốn ~2–2,4× (suy luận từ dữ liệu); vendor giá rẻ bất thường thường mỏng lớp quản lý/chất lượng ([Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).
7. **Chi phí ẩn làm TCO cao hơn đơn giá 50–66%**: khởi động chậm (tháng đầu 40–50% năng suất, 85% sau 4,6 tháng), rework 40–70% ngân sách, >50% do hiểu sai yêu cầu; offshore chỉ lời hơn nội địa từ ~12–15 người-tháng ([Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).
8. **Tiếng Nhật là biến số giá lớn nhất**: BrSE/PM/Architect (N2–N1) 50–100 man; junior/test không cần N2 chỉ 20–40 man; tiêu chí chọn vendor số 1 là trình độ tiếng Nhật (白書2025) ([Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection)).
9. **Đồng tiền hợp đồng (JPY/USD) ảnh hưởng trực tiếp chi phí qua tỷ giá**; thanh toán quốc tế VN–JP về nguyên tắc không chịu thuế tiêu dùng Nhật nhưng có thể bị khấu trừ thuế thu nhập (hiệp định VN–JP có thể tránh đánh thuế 2 lần); thông lệ thanh toán Nhật là chốt cuối tháng–trả cuối tháng sau (~30 ngày), trần 60 ngày theo luật ([Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), [Linnoedge FAQ](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/), [zeimu.cloud](https://zeimu.cloud/kaisetsu/seikyu-invoice/shiharai-site)).
10. **Việt Nam giữ 43% thị phần đơn hàng offshore của Nhật** (số 1), dù không rẻ nhất (Myanmar/Bangladesh rẻ hơn) — nhờ cân bằng giá + tiếng Nhật + kinh nghiệm + múi giờ 2h ([Kaopiz](https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/), [Enlyt](https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection), [Linnoedge](https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/)).

---

## 9. Danh sách nguồn (URL + ngày truy cập/đăng)

1. offshore-kaihatsu.com — "【2026年最新版】人気6カ国の単価比較" (cập nhật 2026-02-13): https://www.offshore-kaihatsu.com/faq/tanka.php
2. offshore-kaihatsu.com — "ベトナム | オフショア開発の人月単価相場" (cập nhật 2026-02-13): https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/
3. offshore-kaihatsu.com — "オフショア開発の準委任契約とは" (cập nhật 2024-12-03): https://www.offshore-kaihatsu.com/contents/general/consignment.php
4. Linnoedge — "ベトナムオフショア開発の費用・単価・相場【2026年版】" (2026-06-17): https://linnoedge.com/ja/vietnam-offshore-development-cost-guide/
5. Kaopiz — "ベトナムオフショア開発単価は？" (2025-11-14, cập nhật 2026-05-13): https://kaopiz.com/ja-news-vietnam-offshore-development-1-man-month-cost/
6. Enlyt — "ベトナムオフショア開発の費用相場・選び方完全ガイド" (2026-05-18): https://enlyt.co.jp/blog/vietnam-offshore-cost-and-selection
7. Romulus Digital — "IT Outsourcing Vietnam: Why Executives Call It the Smartest Bet" (2025-09-04): https://romulus.digital/our-article/why-everyones-talking-about-it-outsourcing-vietnam-in-2025/
8. LeO Nguyen (LinkedIn Pulse) — "Why the T&M vs. Fixed-Price Decision Could Make or Break Your Next Project?" (2026-04-17): https://www.linkedin.com/pulse/why-tm-vs-fixed-price-decision-could-make-break-your-next-leo-nguyen-3uffc
9. TalentClip TIMES — "ブリッジ人材の役割と必要性" (2022-09-01): https://www.talent-clip.jp/media/role-and-necessity-of-bridge-personnel-issues-in-overseas-expansion-and-tips-for-recruitinghuman-resources
10. TopDev — "Vietnam IT Market Reports" (trang chính thức, báo cáo 2024–2025): https://topdev.vn/page/vietnam-it-market-reports/
11. zeimu.cloud — "支払条件・支払サイト・締め日とは" (2026-07-05): https://zeimu.cloud/kaisetsu/seikyu-invoice/shiharai-site
12. gyoumuitakukeiyakusho.com — "契約書の支払期日・支払期限の書き方" (2023-08-13): https://www.gyoumuitakukeiyakusho.com/contract-payment-date-how-to-write/
13. Classic Informatics — "Fixed Price vs Time and Materials: Which to Pick": https://www.classicinformatics.com/blog/fixed-price-vs-time-and-materials
14. BritCham Vietnam — "IT&AI report" (2024-09): https://britchamvn.com/wp-content/uploads/2024/10/ITAI-report-Sep-2024.pdf
15. LinkedIn Pulse (Ivy Minh Chau) — "Why should you choose to work with Vietnam IT Outsourcing" (dẫn Statista): https://www.linkedin.com/pulse/why-should-you-choose-work-vietnam-outsourcing-minh-châu-ivy--bevrc

*Khoảng trống dữ liệu đã ghi nhận: (a) claim "BrSE premium 10–20%" chưa có nguồn trực tiếp; (b) utilization ratio & gross margin chuẩn ngành cho vendor offshore VN–JP không tìm thấy nguồn công bố; (c) điều khoản thanh toán offshore-specific (milestone %) không tìm thấy nguồn trực tiếp — chỉ có thông lệ chung của Nhật.*