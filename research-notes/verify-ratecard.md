# VERIFY: オフショア開発白書 2025 — bảng giá Việt Nam (40,1 / 50,0 / 59,0 / 71,4 万円) và tuyên bố "40-70% giá Nhật nội địa"

Ngày xác minh: 2026-10-09. Người xác minh: subagent phản biện (adversarial verification). Mục tiêu: bác bỏ hoặc xác nhận từng phần của claim.

## Tóm tắt phán quyết

| # | Luận điểm | Phán quyết |
|---|---|---|
| 1 | Con số 40,1 / 50,0 / 59,0 / 71,4 万円 (PG / SE / BrSE / PM) đúng như 白書2025 | **CONFIRMED** (khớp chính xác tại trang của chính nhà xuất bản + biểu đồ 白書 do SHIFT ASIA sao chép + bài phân tích của vfa-lab) |
| 2 | Dữ liệu mâu thuẫn từ khảo sát khác | **PARTIAL** — không có khảo sát nào bác bỏ hoàn toàn; vfa-lab ước tính "giá hợp lý" 2026 ~61万 (cao hơn ~20% so với 白書); các vendor khác đưa khoảng giá bao quanh số của 白書 |
| 3 | "Giá offshore Việt Nam ≈ 40-70% giá Nhật nội địa" | **PARTIAL / UNVERIFIED-as-exact-figure** — không nguồn nào nói chính xác "40-70%"; chính 白書 ghi mức giảm chi phí 31-50% (tức trả 50-69%); nhà xuất bản nói 1/3〜1/2 (33-50%); Luvina nói 60-70%. Dải 40-70% là ước lượng tổng hợp chấp nhận được nhưng KHÔNG phải con số của 白書 |
| 4 | Đơn vị: theo tháng/người, JPY, năm nào | **CONFIRMED** — 1人月 (person-month), JPY (万円), khảo sát 2025-08-01 → 2025-10-31, phát hành 2026-01-21 dưới tên "2025年版" |

---

## 1. Con số có khớp với bảng giá thật của 白書2025 không? — CONFIRMED

Con số trong claim khớp **chính xác từng chữ số** với bảng giá mà **chính nhà xuất bản** công bố, tại hai trang:

- [offshore-kaihatsu.com/faq/tanka.php](https://www.offshore-kaihatsu.com/faq/tanka.php) — "【2026年最新版】人気6カ国の単価比較" (cập nhật 2026-02-13): Việt Nam プログラマー **40,1万円 (+1,8%)**, シニアエンジニア **50,0万円 (+3,5%)**, ブリッジSE **59,0万円 (±0%)**, PM **71,4万円 (+2,0%)**. Chú thích cuối bảng: "* 1人月あたり / * 括弧内は昨対比 / * 出典：「オフショア開発白書（2025年版）」" (liên kết tới /offshore_hakusho_2025/).
- [offshore-kaihatsu.com/contents/vietnam/price-2026/](https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/) — trang giá Việt Nam, cùng bốn con số, cùng chú thích nguồn.

Hai nguồn độc lập khác tái hiện đúng bốn con số này và gán cho 白書2025:

- **SHIFT ASIA** (vendor lớn tại TP.HCM, bài 2026-01-30): bài "[2025年版『オフショア開発白書』から読み解く、オフショア開発の最新動向](https://shiftasia.com/ja/column/2025年版オフショア開発白書から読み解く最新動向/)" nhúng nguyên biểu đồ "国別平均単価" của 白書2025. Tôi đã tải ảnh biểu đồ về và OCR (tesseract, tiếng Nhật): "ベトナム 40.1(+1.8%) 50.0(+3.5%) 59.0(0%) 71.4(+2.0%)" — khớp tuyệt đối. Ảnh OCR lưu tại `/tmp/vibeflow/agent/verify-ratecard/hakusho2025_chart.png`.
- **vfa-lab / Vitalify Asia** (bài 2026-08-31, "[【2026年】ベトナムオフショア開発単価](https://vfa-lab.jp/media/vietnam-offshore-development-rates-2026/)"): tái hiện bảng "＜表1＞" đúng 40,1 (+1,8%) / 50,0 (+3,5%) / 59,0 (±0%) / 71,4 (+2,0%), ghi chú rõ "2025年末に公開…調査時点である2025年時点における単価" và dẫn nguồn [thông cáo chính thức của 白書2025](https://www.offshore-kaihatsu.com/news/articles/wp_2025/).

**Ai phát hành?** Thông cáo chính thức [news/articles/wp_2025](https://www.offshore-kaihatsu.com/news/articles/wp_2025/) (2026-01-21) xác nhận: 白書 do **オフショア開発.com (株式会社テクノデジタル / TECHNODIGITAL)** phát hành — phương pháp "インターネットリサーチ", đối tượng "オフショア開発会社・ITベンダー・SIer・委託企業（1,200社）", PDF A4 45 trang, miễn phí. Trang đích [offshore_hakusho_2025](https://www.offshore-kaihatsu.com/offshore_hakusho_2025/) (lưu trữ Wayback 2026-05-10) xác nhận mục lục có "【第3部】2. オフショア開発先の⼈⽉単価（職種別）" — tức 白書 thực sự chứa bảng đơn giá theo vai trò theo quốc gia.

**IPA thì sao?** Claim ghi "published by IPA or オフショア開発.com". Kiểm tra: IPA **không** phát hành オフショア開発白書. IPA phát hành ソフトウェア開発データ白書 (dữ liệu nội địa, nay nằm trong mục [archive](https://www.ipa.go.jp/archive/publish/wp-sd/wp-sd.html)) và [ソフトウェア動向調査](https://www.ipa.go.jp/digital/software-survey/software-engineering/software2025.html) — cả hai đều không có bảng đơn giá offshore theo quốc gia. Vậy nhà xuất bản đúng là オフショア開発.com (nhánh "or" của claim đứng vững).

**Sắc thái cần lưu ý (không bác bỏ claim nhưng cần ghi):**
- Cột thứ hai trong 白書 là **シニアエンジニア** (senior engineer), claim gọi là "SE" — gán nhãn hơi lệch nhưng cùng vai trò.
- Đây là **giá trung bình do chính các công ty offshore khai báo** trong khảo sát, không phải giá chào thực của từng vendor; nhiều trang vendor Nhật chép cùng một bảng 白書 nên các con số "thị trường" rất đồng nhất (điểm này chính các nguồn như Linnoedge đã cảnh báo).

## 2. Dữ liệu mâu thuẫn từ các khảo sát khác — PARTIAL

Không tìm thấy khảo sát nào đưa con số "khác hẳn" theo hướng thấp hơn nhiều; chiều mâu thuẫn chủ yếu là **cao hơn**:

- **vfa-lab (2026-08-31)**: tự tính từ lương trung bình IT (ITviec "VIETNAM IT SALARY & RECRUITMENT MARKET 2025-2026"), hệ số chi phí +29% (BHXH, thưởng Tết), SG&A ~45,7% (trung bình 5 công ty niêm yết Nhật làm offshore VN), ra **đơn giá hợp lý 2026 ≈ 61万/tháng** (TP.HCM 64万, Hà Nội 58万, Đà Nẵng 56万) — tức **cao hơn ~20%** so với mức 50万 (senior) của 白書. Bài viết giải thích chênh lệch do cạnh tranh ép giá giữa các vendor hướng Nhật (dẫn biên lợi nhuận giảm của Hybrid Technologies, Sun*, SHIFT...). Đây là mâu thuẫn đáng kể nhất: 白書 phản ánh giá giao dịch thực (thấp), còn chi phí cấu thành "công bằng" cao hơn.
- **Kaopiz** (bảng giá 2026, trích trong memo hiện có): BrSE 50–80万, PM 60–100万 — khoảng rộng bao quanh điểm 59,0/71,4 của 白書, không mâu thuẫn.
- **Linnoedge** (giá thực đang áp dụng 2026-07): Junior 40万–, Middle 55万–, Senior 70万–, PM/BrSE 60万– — cùng biên độ.

Kết luận: không có nguồn nào chứng minh con số 白書 sai kiểu "bịa"; có nguồn cho rằng 白書 **hạ thấp** mặt bằng giá hợp lý. Claim vẫn đứng.

## 3. "Giá offshore VN ≈ 40-70% giá Nhật nội địa" — PARTIAL (không phải con số của 白書)

Không tìm thấy bất kỳ nguồn nào nói chính xác cụm "40-70%". Các con số thực tế thu thập được:

- **Chính 白書2025** (mục "国内と比較した場合の…コストダウン比率", theo thông cáo + SHIFT ASIA): mức giảm chi phí phổ biến là **31〜50%** (31% số DN đạt 31-40%, 25% đạt 41-50%) → tức chi phí offshore = **50-69%** giá nội địa. Không phải 40-70%.
- **Nhà xuất bản** (trang giá VN): "日本国内の約1/3〜1/2" — tức **33-50%**.
- **Solashi** (2025-08-04): "ベトナムの人件費は、日本の1/2～1/3ほど" — 33-50%.
- **Luvina** (phân tích 白書2025, 2026-02): "国内相場の**6〜7割**で優秀なチームを迅速に構築できる" — tức **60-70%** — nằm trong nửa trên của dải claim.
- **Tự tính theo vai trò** với giá nội địa Nhật: theo [app-tatsujin](https://app-tatsujin.com/contract-development-man-month-rate-calculation-2025-2026/) (2026-05-13, dẫn Crexgroup/n-v-l/ICD), đơn giá nội địa 2025: Junior Tokyo 71万, Middle Tokyo 117万, Senior Tokyo 173万 (vùng thấp hơn: 56–133万). Tỷ lệ VN/nội địa: PG 40,1/71-117 = **34-56%**; SE 50,0/95-117 = **43-53%**; BrSE 59,0/~100-150 = **~40-60%**; PM 71,4/133-173 = **41-54%**. So với JUAS (trung bình ngành 117,5万, dẫn qua [chaki-study](https://chaki-study.com/unit-price-market/)): 40,1/117,5 = 34% đến 71,4/117,5 = 61%.

Tổng hợp: dải thực tế quan sát được là **~33-70%**, tùy vai trò và nguồn. Dải "40-70%" của claim nằm trong vùng chấp nhận được nhưng: (a) không phải con số do 白書 đưa ra, (b) bỏ sót mép dưới 33-40% mà chính nhà xuất bản và Solashi nêu. Nên trình bày lại là "khoảng 1/3 đến 2/3-7/10 giá Nhật, tùy vai trò" hoặc "giảm 31-50% theo chính 白書".

## 4. Đơn vị / tiền tệ / năm — CONFIRMED

- Đơn vị: **1人月 (person-month)**, tức một người làm một tháng (~160h), tính bằng **JPY** (万円).
- Niên đại: khảo sát thực hiện **2025-08-01 → 2025-10-31** (ghi trong 白書, dẫn lại bởi vfa-lab); 白書 phát hành **2026-01-21** mang tên "オフショア開発白書（2025年版）"; các trang bảng giá được nhà xuất bản gắn nhãn "2026年最新版" (cập nhật 2026-02-13) nhưng chú thích nguồn vẫn là 白書2025.
- Lưu ý: tỷ giá ảnh hưởng — vfa-lab ghi nhận VND tăng ~5,1% so với JPY trong 8 tháng đầu 2026, nên giá quy đổi 2026 có thể đã cao hơn con số 白書.

---

## Nguồn (URL + ngày truy cập)

1. https://www.offshore-kaihatsu.com/faq/tanka.php — bảng 6 nước, cập nhật 2026-02-13 (truy cập 2026-10-09)
2. https://www.offshore-kaihatsu.com/contents/vietnam/price-2026/ — giá Việt Nam, cập nhật 2026-02-13 (truy cập 2026-10-09)
3. https://www.offshore-kaihatsu.com/offshore_hakusho_2025/ — trang đích 白書2025 (502 trực tiếp; xem qua Wayback 2026-05-10)
4. https://web.archive.org/web/20260510141433/https://www.offshore-kaihatsu.com/offshore_hakusho_2025/ — phương pháp khảo sát 1.200 công ty, mục lục 45 trang
5. https://www.offshore-kaihatsu.com/news/articles/wp_2025/ — thông cáo phát hành 2026-01-21
6. https://shiftasia.com/ja/column/2025年版オフショア開発白書から読み解く最新動向/ — bài 2026-01-30, nhúng biểu đồ 白書 (đã OCR xác nhận số)
7. https://vfa-lab.jp/media/vietnam-offshore-development-rates-2026/ — bài 2026-08-31, tái hiện bảng + ước tính ~61万 + thời gian khảo sát
8. https://luvina.jp/offshore-development-whitepaper-2025-project-and-country-ranking/ — bài 2026-02, "国内相場の6〜7割"
9. https://solashi.com/media/8-reasons-why-customers-should-choose-vietnam-offshore-development/ — bài 2025-08-04, "1/2〜1/3"
10. https://app-tatsujin.com/contract-development-man-month-rate-calculation-2025-2026/ — bài 2026-05-13, đơn giá nội địa Nhật 2025 (71-173万)
11. https://www.ipa.go.jp/archive/publish/wp-sd/wp-sd.html và https://www.ipa.go.jp/digital/software-survey/software-engineering/software2025.html — xác nhận IPA không phát hành オフショア開発白書
12. https://chaki-study.com/unit-price-market/ — JUAS 117,5万 (tham chiếu)

## Ghi chú quy trình
- Ảnh biểu đồ 白書2025 tải về và OCR: `/tmp/vibeflow/agent/verify-ratecard/hakusho2025_chart.png` (không đưa vào workspace vì là tài liệu trung gian).
- Không tìm thấy bản PDF gốc của 白書 (cần form đăng ký tải); xác minh dựa trên trang chính thức của nhà xuất bản + 2 nguồn tái hiện độc lập — đủ để kết luận CONFIRMED cho phần số liệu.