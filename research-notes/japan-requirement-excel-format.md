# Cấu trúc và định dạng file Excel danh sách yêu cầu (要件一覧) trong mua sắm phần mềm tại Nhật Bản

Memo nghiên cứu — sub-question: cấu trúc/định dạng điển hình của các file Excel yêu cầu (別紙 / 機能要件一覧 / 要件定義書) trong quy trình mua sắm phần mềm ở Nhật, hàm ý cho việc phân tích tự động.

## 1. Bối cảnh: vị trí của 機能要件一覧 trong hồ sơ mời thầu

Trong mua sắm hệ thống thông tin của chính quyền địa phương Nhật Bản, danh sách yêu cầu chức năng (機能要件一覧) được soạn như một **phụ lục (別紙)** của 仕様書 (bản đặc tả kỹ thuật / specification) và được phát hành kèm theo hồ sơ mời thầu hoặc mời chào (プロポーザル). Nhà cung cấp phải điền vào cột trả lời (回答欄) cho từng dòng yêu cầu. Nguồn hướng dẫn về cách viết cho chính quyền địa phương ([digital-supporter.net — Chương 11 "Cách sắp xếp yêu cầu chức năng hệ thống"](https://digital-supporter.net/mirai-ai/siyousho/kinou-youken.html)) mô tả quy ước chuẩn: "機能要件は、仕様書の別紙として「機能要件一覧」の表を作り、事業者に対応できるかどうかを回答してもらうのが一般的" (yêu cầu chức năng thường được lập thành bảng "danh sách yêu cầu chức năng" làm phụ lục của spec, nhà thầu trả lời khả năng đáp ứng). Cùng trang này đưa ra ví dụ văn bản chuẩn trích trong spec: "本システムは、別紙9「機能要件一覧」に掲げる機能を備えること" và "(2) 機能要件一覧の「区分」欄が「必須」の要件は、すべて満たすこと。いずれかを満たさない場合は、本調達の要件を満たさないものとする" — tức yêu cầu đánh dấu 必須 (bắt buộc) mà không đáp ứng thì bị loại.

## 2. Cấu trúc cột của 機能要件一覧

### 2.1 Mẫu chuẩn được khuyến nghị (nguồn hướng dẫn)

Theo [digital-supporter.net](https://digital-supporter.net/mirai-ai/siyousho/kinou-youken.html), bảng 機能要件一覧 chuẩn gồm các cột:

| Cột | Ý nghĩa |
|---|---|
| 番号 | số hiệu yêu cầu, ví dụ 機-001, 機-002... |
| 大分類 | phân loại lớn (ví dụ 申請受付, 審査, 帳票, 管理) |
| 中分類 | phân loại trung (ví dụ オンライン申請, 進捗管理, 通知書, 権限, ログ) |
| 機能要件 | nội dung yêu cầu, viết dạng "〜できること" (có thể làm được gì), 1 dòng = 1 yêu cầu |
| 区分 | 必須 (bắt buộc) / 推奨 (khuyến nghị) / 参考 (tham khảo) |
| 回答 | ô nhà thầu điền: ◎ ○ △ □ × |
| 備考（代替手段等） | ghi chú / phương án thay thế |

Quy ước đánh dấu 区分: **必須** = không đáp ứng thì bị loại (失格); **推奨（任意）** = không đáp ứng không bị loại nhưng được cộng điểm trong chấm điểm tổng hợp; **参考** = chỉ thăm dò khả năng, không chấm điểm. Quy ước trả lời: **◎** = đáp ứng bằng chức năng chuẩn, **○** = đáp ứng bằng cấu hình tham số, **△** = đáp ứng bằng phương án thay thế (ghi cách làm vào 備考), **□** = cần tùy biến (customize, tính chi phí), **×** = không đáp ứng được.

### 2.2 Ví dụ thực tế từ thành phố Ureshino (嬉野市, tỉnh Saga) — file Excel thật

File **[別紙1 機能要件一覧表（エクセル）](https://www.city.ureshino.lg.jp/var/rev0/0043/0305/124829171924.xlsx)** (47KB, phát hành R6/2024 cho dự án 文書管理システム構築業務) đã được tải về và phân tích trực tiếp bằng openpyxl. Kết quả:

- **8 sheet**: `表紙` (bìa), `必須項目` (mục bắt buộc), `共通項目` (mục chung), rồi mỗi sheet là một nhóm nghiệp vụ: `ガイド、個別ﾌｫﾙﾀﾞ及び移替管理`, `保存箱及び引継管理`, `書庫及び廃棄管理`, `検索、印刷等管理`, `収受、起案、供覧`. → Cách tổ chức phổ biến: chia sheet theo phân loại nghiệp vụ, không gói hết vào một sheet.
- Cột của sheet `必須項目` và `共通項目`: `項番 | システム | 業務 | 機能 | 仕様内容 | 判定 | 備考` (7 cột). Các sheet nghiệp vụ khác bỏ cột システム: `項番 | 業務 | 機能 | 仕様内容 | 判定 | 備考` (6 cột). → **Các sheet trong cùng một workbook có thể có số cột/header khác nhau**.
- Cột 判定 (đánh giá) có **data validation kiểu dropdown list với danh sách "◎,○,△,×"** áp cho toàn bộ vùng dữ liệu (ví dụ F2:F16, F26:F38 trên sheet 必須項目) — giống hệt quy ước ◎○△× ở mục 2.1. Trong file phát hành, cột 判定 để trống (nhà thầu tự điền).
- Sheet 表紙 giải thích chú giải: "※判定欄について、下記の項目から選択してください。" với nội dung "◎：パッケージ内で実現可能 / ○：パッケージとは別で簡易な方法で実現可能（例 データを抽出し汎用ソフトウ…）" và "※機能要件に対し、追記したい場合は備考欄に記入してください。" → chú giải nằm ngay trong sheet bìa, không phải trong header.
- **项番 được sinh bằng công thức**: trên các sheet nghiệp vụ, ô 項番 chứa công thức `=ROW()-1` thay vì giá trị số; riêng sheet 必須項目 điền số nguyên 1..n. → Một parser đọc giá trị sẽ thấy công thức (hoặc cần engine tính toán).
- Sheet 表紙 có **ô gộp (merged cells)**: tiêu đề `嬉野市文書管理システム機能要件一覧` gộp A8:O8, ô ghi chú gộp E14:L14, E15:L15, E16:L16, A23:O23.
- Tên sheet lẫn **katakana bán phần (half-width)**: `ガイド、個別ﾌｫﾙﾀﾞ及び移替管理` — chữ ﾌｫﾙﾀﾞ là half-width katakana, gây khó khăn khi so khớp chuỗi.
- Có warning khi mở bằng openpyxl: "Print area cannot be set to Defined name: テーブル4[#All]" — file dùng **Excel Table (テーブル)** với defined name, một lớp phức tạp nữa.

### 2.3 Ví dụ thực tế từ làng Nakagawa (中川村, tỉnh Nagano) — file Excel thật thứ hai

File **[【別紙１】機能要件一覧表](https://www.vill.nakagawa.nagano.jp/uploaded/attachment/6306.xlsx)** (đã tải về, phân tích bằng openpyxl) cho thấy một biến thể phổ biến khác:

- **2 sheet**: `一覧表` và `記入要領` (sheet hướng dẫn cách điền — một đặc điểm hay gặp: hướng dẫn nằm ngay trong workbook).
- Cột của sheet 一覧表: `通番 | カテゴリ | 要件 | 要求区分 | 対応状況 | 備考` (6 cột). Lưu ý tên cột khác hẳn file Ureshino (通番 thay vì 項番, 要求区分 thay vì 区分, 対応状況 thay vì 判定) — **không có chuẩn tên cột thống nhất giữa các địa phương**.
- Cột 要求区分 phân loại **必須 (34 dòng) / 任意 (10 dòng)** trong file này — minh chứng trực tiếp cho quy ước đánh dấu 必須・任意.
- Cột 対応状況 có **data validation dropdown "◎,○,△,×"** (vùng E4:E45).
- Sheet 記入要領 ghi chú giải đầy đủ: ① yêu cầu 必須 là "絶対要件" (yêu cầu tuyệt đối) nhưng khả năng hiện thực được trả lời theo 4 mức: **◎** = hiện thực trong phạm vi kinh phí hợp đồng (không phân biệt chuẩn/option/customize), **○** = hiện thực bằng phương án thay thế trong kinh phí (ghi cách làm vào 備考), **△** = không hiện thực trong kinh phí nhưng làm được bằng customize riêng (phải nêu cả chi phí ước tính), **×** = không thể hiện thực (ghi lý do vào 備考). ② yêu cầu 任意 là "絶対要件ではない" (không bắt buộc), cùng thang 4 mức. ③ ghi chú khác: nếu chỉ một phần của yêu cầu không hiện thực được thì điền ×; nếu 備考 không đủ chỗ thì dùng phụ lục riêng (別紙、様式任意).

### 2.4 Ví dụ thành phố Oyama (小山市, Tochigi) — ghi chú

Kết quả tìm kiếm ban đầu cho thấy TP Oyama đăng tải `仕様書別紙2_機能要件一覧` (PDF 1.25MB) tại [trang thông báo 指名型プロポーザル](https://www.city.oyama.tochigi.jp/sangyou-sigoto/nyuusatsu-keiyaku/etc/page008426.html), xác nhận mô hình "別紙 + 機能要件一覧" phổ biến ở các thành phố. Tuy nhiên trang này hiện trả 404 khi truy cập lại (2026-10), nên chỉ dùng làm bằng chứng gián tiếp về sự tồn tại của mô hình, không trích nội dung.

## 3. 非機能要件一覧 (danh sách yêu cầu phi chức năng)

- Chuẩn ngành thực tế là **IPA 非機能要求グレード2018**: 6 đại mục (可用性 / 性能・拡張性 / 運用・保守性 / 移行性 / セキュリティ / システム環境・エコロジー), 35 trung mục, 118 tiểu mục, 238 metric; phân loại hệ thống theo 3 mô hình mức ảnh hưởng xã hội ([saas-magazine.com — bài phân tích cấu trúc sheet Excel theo IPA](https://saas-magazine.com/requirements-definition-document-sample-excel)). Đây là nguồn chính để thiết kế sheet 非機能要件 trong Excel.
- Đối với chính quyền địa phương, **デジタル庁/総務省 ban hành 「地方公共団体情報システム非機能要件の標準」** (bản 1.2, 2025-09) — tài liệu chính thức hiện hành; một bài tổng quan [remogu.jp](https://remogu.jp/c/non-functional-requirements-availability-freelance) dẫn theo đó liệt kê các vùng chính: 可用性, 性能・拡張性, セキュリティ, 運用・保守.
- Ví dụ thực tế về cấu trúc bảng 非機能要件一覧 của một thành phố: file [別紙３「仕様書 表２ 非機能要件一覧」対応表](https://www.city.niigata.lg.jp/business/norinsuisan/nogyoiinkai/propo20260401.files/09_ketteikijyun_besshi3.xlsx) của TP Niigata (R8/2026). Theo đoạn trích từ kết quả tìm kiếm, file có các cột `項番 | 大項目 | 小項目 | 必須／任意` (ví dụ dòng "信頼性 / システム監視基準 / 必須", "障害通知プロセス / 必須") — tức bảng 非機能要件 cũng dùng cấu trúc 項番 + phân cấp 大項目/小項目 + đánh dấu 必須／任意. Lưu ý: file hiện trả 404 khi tải lại trực tiếp nên cấu trúc này chỉ xác nhận qua snippet tìm kiếm, cần kiểm tra lại nếu dùng làm căn cứ chính.

## 4. 質問記入票 / 質問表 (phiếu hỏi đáp)

Trong quy trình mời thầu, nhà thầu gửi câu hỏi về spec qua **様式2「仕様書等に関する質問表」**. File thật của TP Ureshino ([様式2 仕様書等に関する質問表 .doc](https://www.city.ureshino.lg.jp/var/rev0/0043/0307/12482915226.doc), đã tải và chuyển đổi bằng LibreOffice) có cấu trúc:

- Phần đầu: 会社等名 (tên công ty), 担当部署/担当者, 電子メールアドレス, 電話, ファクス.
- Bảng câu hỏi lặp lại nhiều khối, mỗi khối gồm các cột: `№ | 資料名称 (tên tài liệu) | 該当頁 (trang liên quan) | 該当行 (dòng liên quan) | 該当項目 (mục liên quan) | 質問内容 (nội dung câu hỏi)`.
- Mục 【留意事項】: hạn nộp, phương thức nộp (email/FAX/bưu điện/trực tiếp), "質問項目が多い場合は，本様式を適宜複写して利用すること" (nếu nhiều câu hỏi thì copy thêm khối).
- Lưu ý kỹ thuật: file đuôi `.doc` nhưng thực chất là **DOCX (zip OOXML)** — chỉ chứa theme, không có word/document.xml đầy đủ theo chuẩn (bản chuyển đổi vẫn ra văn bản đúng).

## 5. Cấu trúc sheet chuẩn của một 要件定義書 (bộ tài liệu)

Theo [saas-magazine.com](https://saas-magazine.com/requirements-definition-document-sample-excel) (dẫn IPA), một workbook 要件定義書 chuẩn có **6–8 sheet**: (1) 表紙・改訂履歴 (bìa + lịch sử sửa đổi), (2) プロジェクト概要, (3) 業務要件 As-Is/To-Be, (4) 機能要件一覧 (các cột: 画面ID/機能ID/概要/権限/優先度/関連業務), (5) 外部I/F・データ要件, (6) 非機能要件, (7) 用語集・略語集, (8) チェックリスト. Ưu tiên yêu cầu dùng **MoSCoW** (Must/Should/Could/Won't) — tương ứng với 必須/推奨 trong bối cảnh Nhật.

Template thương mại miễn phí: [exia.co.jp 要件定義書サンプルExcel](https://exia.co.jp/bizroute/download/youken01) gồm các sheet 表紙・目次・機能一覧・画面一覧・インターフェース一覧・非機能要件・データ項目定義 — xác nhận lại bộ sheet chuẩn. [mes-dx.com](https://www.mes-dx.com/tools/requirements-template) phân phối template MES với 286 dòng yêu cầu (198 chức năng + 88 phi chức năng), phân loại MUST/SHOULD/COULD.

## 6. Các "quirk" định dạng phá vỡ parser ngây thơ (tổng hợp từ file thật)

1. **Merged cells** ở header và tiêu đề (bìa Ureshino gộp A8:O8, E14:L14, E15:L15, E16:L16, A23:O23).
2. **Multi-row / lệch header**: các sheet khác nhau có số cột khác nhau (7 vs 6 cột) trong cùng một file (Ureshino).
3. **Số hiệu yêu cầu là công thức** (`=ROW()-1`) chứ không phải giá trị (Ureshino, các sheet nghiệp vụ).
4. **Data validation dropdown** (◎,○,△,×) — tập giá trị hợp lệ nằm trong list ẩn của Excel, không xuất hiện trong ô.
5. **Chú giải nằm rải rác**: sheet bìa (Ureshino) hoặc sheet 記入要領 riêng (Nakagawa) giải thích ý nghĩa ◎○△× và 必須/任意 — parser muốn hiểu ngữ nghĩa phải đọc cả các sheet này.
6. **Tên sheet dùng half-width katakana** lẫn full-width (`ガイド、個別ﾌｫﾙﾀﾞ及び移替管理`).
7. **Excel Table / defined names** (warning print area khi mở bằng openpyxl — file Ureshino).
8. **Nhiều sheet theo nhóm nghiệp vụ** + sheet 表紙; sheet hướng dẫn điền (記入要領).
9. **Không có chuẩn tên cột thống nhất**: Ureshino dùng 項番/システム/業務/機能/仕様内容/判定/備考, Nakagawa dùng 通番/カテゴリ/要件/要求区分/対応状況/備考 — parser phải nhận diện cột theo ngữ nghĩa, không theo tên cột cứng.
10. **Cột trả lời để trống** trong file phát hành — parser không được giả định có dữ liệu; dữ liệu thật chỉ xuất hiện sau khi nhà thầu điền.
11. **Định dạng file lẫn lộn**: file đuôi `.doc` nhưng thực chất DOCX (質問表 Ureshino); file `.xls` nhị phân cũ vẫn tồn tại trên trang địa phương (ví dụ [pref.ibaraki.jp .xls](https://www.pref.ibaraki.jp/hokenfukushi/yobo/zukuri/yobo/documents/1-2yousiki1bessi.xls)); có nơi phát hành bản PDF song song bản Excel (Ureshino phát hành cả [PDF](https://www.city.ureshino.lg.jp/var/rev0/0043/0300/124829152428.pdf) lẫn xlsx).
12. **Nội dung nhiều dòng trong ô** (ví dụ ô 要件 chứa "\n" nhiều dòng, liệt kê trình duyệt) — cần giữ nguyên cấu trúc dòng khi trích xuất. (Chữ dọc 縦書き không quan sát thấy trong các file mẫu đã phân tích — các bảng yêu cầu đều trình bày ngang; nếu có, thường chỉ ở tài liệu Word, không nên coi là đặc điểm phổ biến của file Excel yêu cầu.)

## 7. Hàm ý cho việc phân tích tự động

Một parser "robust" cho loại file này cần: (a) đọc bằng thư viện đọc được cả công thức lẫn giá trị (hoặc tính công thức như `=ROW()-1`); (b) xử lý merged cells (lấy giá trị góc trên-trái, forward-fill xuống vùng gộp); (c) nhận diện dòng header theo ngữ nghĩa từ điển từ khóa (項番/通番/番号, 大分類/カテゴリ, 中分類, 機能要件/要件/仕様内容, 必須/任意/区分/要求区分, 判定/回答/対応状況, 備考) thay vì vị trí cột cố định; (d) đọc data validation để biết tập giá trị hợp lệ của cột trả lời; (e) quét mọi sheet (kể cả 表紙/記入要領) để gom chú giải; (f) chuẩn hóa Unicode (half-width ↔ full-width katakana) khi so khớp tên sheet/cột; (g) xử lý đa định dạng tệp (.xlsx/.xls/.doc/.docx/.pdf) và chọn nguồn ưu tiên (Excel trước, PDF dự phòng); (h) phân biệt yêu cầu 必須 (quyết định loại/điểm) với 任意/推奨 khi tổng hợp.

## 8. Khoảng trống dữ liệu (not found)

- **Bộ 別紙様式 của 「情報システムに係る政府調達等の標準ガイドライン」 (総務省)** — không tìm thấy bộ biểu mẫu 機能要件一覧/質問書 chuẩn quốc gia công khai dạng tải về trong các lượt tìm kiếm ("情報システムに係る政府調達等の標準ガイドライン 別紙様式", "デジタル・ガバメント推進標準ガイドライン 別紙様式 質問書"). Thực tế quan sát được là mỗi địa phương tự soạn biểu mẫu riêng (bằng chứng: Ureshino vs Nakagawa khác nhau hoàn toàn về tên cột). Cần kiểm tra thêm nếu luận điểm "có chuẩn quốc gia" được dùng.
- File 非機能要件一覧 của TP Niigata và trang Oyama hiện trả 404 khi tải lại — chỉ dùng được qua snippet tìm kiếm.

## Nguồn

- https://digital-supporter.net/mirai-ai/siyousho/kinou-youken.html (cập nhật 2026-10-09)
- https://www.city.ureshino.lg.jp/sangyo/nyusatsu/_24641/_31205.html (R6/2024) + file xlsx/doc đã tải về và phân tích
- https://www.vill.nakagawa.nagano.jp/uploaded/attachment/6306.xlsx (file đã tải về và phân tích)
- https://saas-magazine.com/requirements-definition-document-sample-excel (2026-06-10)
- https://remogu.jp/c/non-functional-requirements-availability-freelance
- https://www.city.niigata.lg.jp/business/norinsuisan/nogyoiinkai/propo20260401.files/09_ketteikijyun_besshi3.xlsx (chỉ qua snippet; hiện 404)
- https://www.city.oyama.tochigi.jp/sangyou-sigoto/nyuusatsu-keiyaku/etc/page008426.html (chỉ qua snippet; hiện 404)
- https://exia.co.jp/bizroute/download/youken01 ; https://www.mes-dx.com/tools/requirements-template
- https://www.digital.go.jp/procurement/manual (様式集 ZIP — chủ yếu biểu mẫu hợp đồng, ít liên quan)
- https://www.pref.ibaraki.jp/hokenfukushi/yobo/zukuri/yobo/documents/1-2yousiki1bessi.xls (ví dụ .xls cũ)

## Key claims

1. 機能要件一覧 là phụ lục (別紙) của 仕様書 trong mua sắm công ở Nhật; nhà thầu điền cột trả lời cho từng dòng yêu cầu — nguồn: digital-supporter.net.
2. Bộ cột điển hình: 番号(項番/通番) | 大分類(カテゴリ) | 中分類 | 機能要件(仕様内容) | 区分(必須/任意) | 回答(判定/対応状況) | 備考 — nguồn: digital-supporter.net + 2 file thật.
3. Đánh dấu 必須/任意 (hoặc 必須/推奨/参考): 必須 không đáp ứng = bị loại; 任意/推奨 = cộng điểm — nguồn: digital-supporter.net; file Nakagawa (34 必須 / 10 任意).
4. Cột trả lời dùng dropdown data validation với bộ ký hiệu ◎○△× (có nơi thêm □); ý nghĩa gắn với chi phí hợp đồng — nguồn: file Ureshino (list "◎,○,△,×"), file Nakagawa (chú giải đầy đủ trong sheet 記入要領).
5. Workbook thường nhiều sheet: 表紙 + các sheet theo nhóm nghiệp vụ (+ sheet 記入要領); sheet khác nhau có thể có số cột khác nhau — nguồn: file Ureshino (8 sheet), file Nakagawa (2 sheet).
6. Không có chuẩn tên cột quốc gia thống nhất; mỗi địa phương tự đặt tên (項番 vs 通番, 判定 vs 対応状況) — nguồn: đối chiếu 2 file thật.
7. Quirk kỹ thuật phổ biến: merged cells, số thứ tự là công thức =ROW()-1, half-width katakana trong tên sheet, Excel Table/defined names, cột trả lời để trống — nguồn: phân tích trực tiếp file Ureshino bằng openpyxl.
8. 非機能要件一覧 dựa trên IPA 非機能要求グレード2018 (6 đại mục/35 trung mục/118 tiểu mục/238 metric) hoặc デジタル庁 非機能要件の標準 (可用性/性能・拡張性/セキュリティ/運用・保守...); bảng thực tế có cột 項番/大項目/小項目/必須／任意 — nguồn: saas-magazine, remogu.jp, snippet file Niigata.
9. 質問記入票 (様式「仕様書等に関する質問表」) gồm phần thông tin công ty + bảng №/資料名称/該当頁/該当行/該当項目/質問内容 lặp lại nhiều khối — nguồn: file thật TP Ureshino.
10. Parser robust phải nhận diện cột theo ngữ nghĩa, đọc data validation, xử lý merged cells/formula, quét mọi sheet, chuẩn hóa Unicode, hỗ trợ đa định dạng tệp — tổng hợp mục 7.