# VERIFY: Japanese bid requirement-marking convention (○/△/×) + "30-50% US proposals eliminated" statistic

Memo by: verifier subagent (adversarial refutation)
Date: 2026-10-09
Status: COMPLETE

## Tóm tắt phán quyết (VN)
- **(1) Quy ước đánh dấu ○/△/× trong hồ sơ dự thầu phần mềm Nhật: CONFIRMED.** Tìm thấy mẫu chính thức của thành phố Hofu (機能要件確認書, xlsx): "○：標準仕様で対応可能 / △：代替案またはカスタマイズにより対応可能 / ×：対応不可能". Thành phố Choshi dùng thang 4 ký hiệu ◎/○/△/× (機能評価表, 様式7). △ có được dùng thật. Điểm trừ nhỏ: thang thực tế còn có ◎, và tên biểu mẫu đa dạng (機能要件確認書 / 機能評価表 / 要件充足表).
- **(2) Số liệu "30-50% hồ sơ Mỹ bị loại vì không tuân thủ": KHÔNG TÌM THẤY / UNVERIFIED.** Không nguồn sơ cấp nào (Shipley, GAO) mang con số này; blog chính thức của Shipley về compliance không có tỷ lệ phần trăm nào. Hiện tượng bị loại vì không tuân thủ là có thật (FAR 52.215-1, GAO RiverNorth B-423274.2/3), nhưng con số 30-50% không kiểm chứng được.
- **(3) Bắt buộc theo đúng biểu mẫu khách hàng (mẫu bắt buộc): CONFIRMED cho bảng đối chiếu yêu cầu, có sắc thái.** Bảng trả lời yêu cầu là biểu mẫu cố định do chính quyền phát hành (điền vào file Excel của họ, nộp lại đúng định dạng). Nhưng 企画提案書 (phần tự luận) thường là 任意様式 (tự do) kèm giới hạn trang/bố cục bắt buộc.

## Claim under refutation
"In Japanese software bids, vendors respond to requirement lists (機能要件一覧 / 要件充足表) by marking each requirement with ○ (fully satisfied) / △ (partially) / × (not satisfied) symbols, and that '30-50% of US government proposals are eliminated for non-compliance before scoring.'"

## Sub-point 1: ○/△/× marking convention in Japanese procurement — EVIDENCE SO FAR (strong, primary)

### CONFIRMED (primary source): Hofu City (防府市, Yamaguchi), 機能要件確認書 (Form 3), .xlsx template
- URL: https://www.city.hofu.yamaguchi.jp/uploaded/attachment/120690.xlsx (downloaded 2026-10-09; template is for a cloud document-management system procurement)
- The sheet header states verbatim:
  - "○：標準仕様で対応可能" (○ = satisfiable with standard specifications)
  - "△：代替案またはカスタマイズにより対応可能（具体的な代替案及び必要な経費を備考欄に記載すること。）" (△ = satisfiable via alternative proposal or customization; describe the alternative and cost in remarks)
  - "×：対応不可能" (× = cannot satisfy)
  - Instruction: "下記の機能要件項目について、対応欄に回答すること。" (answer in the 対応/response column for each functional requirement item)
- Table structure: 項目 | № | 機能要件項目 | 要求レベル (必須/要望) | 対応 | 備考 — 235 rows of functional requirements.
- This is EXACTLY the ○/△/× convention claimed, in a real municipal procurement template. Note the sheet is titled 機能要件確認書 (requirement confirmation sheet), not 要件充足表 — same genre.

### CONFIRMED (primary source): Choshi City (銚子市, Chiba), 機能評価表 (様式7), プロポーザル実施要領 (Reiwa 8 / 2026)
- URL: https://www.city.choshi.chiba.jp/content/000068784.pdf (downloaded 2026-10-09; electronic approval & document management system design/build, published Reiwa 8 May 2026)
- Page 6-7 of the PDF, section 8(1)ウ 機能評価表（様式７）, states verbatim:
  - "対応可否欄に、次の区分に応じ記号を記入すること。"
  - "◎：標準機能により対応可"
  - "○：標準機能による代替運用が提案可"
  - "△：カスタマイズにより対応可"
  - "×：対応不可"
  - Footnote: "対応可否欄に「○」を記入する場合にあっては備考欄に代替運用の方法を、「△」を記入する場合にあっては備考欄にカスタマイズの内容及びその費用について記入すること。"
- KEY POINT for the refutation: Choshi uses a FOUR-symbol scale ◎/○/△/×, NOT ○/△/×. So the claim's "○/△/×" is one variant, but the ◎ tier (standard-function direct fit) is common too. △ (partial/customization) IS used — so the claim that "△ is used" is CONFIRMED; the claim that the convention is "○/△/× only" is INCOMPLETE (real-world scales include ◎/○/△/× and ○/△/× variants).
- Also: 機能評価表 must be submitted in Excel format on CD-R ("機能評価表（様式７）は、Excelファイル形式で保存したCD-R等の媒体についても併せて提出すること") — i.e., the vendor fills the CITY'S OWN spreadsheet and returns it. Scoring: 機能 category = 150 of 1,000 points, evaluated from 機能評価表; minimum threshold 60% of total points to be selected.

### Partial (primary): Matsusaka City (松阪市, Mie), 企画提案書（機能要件説明書）様式第2-2号, .doc
- URL: https://www.city.matsusaka.mie.jp/uploaded/attachment/28606.doc (downloaded 2026-10-09; childcare-support-system build/maintenance)
- Only a cover-sheet (declaration that vendor has checked the 実施要領/仕様書 and submits the 機能要件説明書). Confirms the term 機能要件説明書 exists as a form name; no marking legend in this file itself.

### CONFIRMED (vendor-side guide, secondary but expert): 自治体AIヤマトくんナレッジ 第116章 "仕様書と評価基準から組み立てる提案書｜章立てと要件充足表" (digital-supporter.net)
- URL: https://digital-supporter.net/mirai-ai/siyousho/teiansho-kousei-hyouka-kijun.html (updated 2026-10-09; author 村井宗明, former 文科省大臣政務官/AI engineer)
- Explicitly describes the 要件充足表 (requirement satisfaction table) as standard practice: "仕様書の必須要件は「要件充足表」で一つずつ対応を示し、満たしていないものがないことを確かめる" (mandatory requirements from the spec are shown one-by-one in a 要件充足表).
- Its worked example table has columns 項番 | 仕様書の要件 | 充足 | 対応の方法 | 提案書の該当箇所, with "○" in the 充足 column for each requirement — i.e., the ○ mark convention in the satisfaction table is exactly as claimed.
- Also: "発注者が要件確認書の様式を用意している場合は、その様式で提出します。" (if the ordering party provides a 要件確認書 form, submit using that form) — supports sub-point 3.
- And: "仕様書の必須要件を一つでも満たしていないと、失格や最低評価になることがあります。" (failing even one mandatory requirement can lead to disqualification or lowest evaluation).

### Verdict sub-point 1: CONFIRMED (with a precision)
The ○/△/× marking convention for responding to requirement lists is REAL and documented in primary municipal templates (Hofu: ○/△/× three-symbol scale; Choshi: ◎/○/△/× four-symbol scale) and in vendor guides (要件充足表 with ○). △ is definitely used (both Hofu and Choshi define △ for alternative/customization). The claim's "○/△/×" is one real variant; the fuller real-world scales also include ◎ (standard-function direct fit). Terms vary: 機能要件確認書 (Hofu), 機能評価表 (Choshi), 要件充足表 (guide), 機能要件説明書 (Matsusaka cover sheet) — all same genre. 対応可否 (Choshi) is the standard column name. I did not find "要確認" as a standard legend symbol in these sources.

## Sub-point 2: "30-50% of US government proposals eliminated for non-compliance" — NOT FOUND / UNVERIFIED

### The specific "30-50%" figure could NOT be substantiated from any primary or secondary source.
Queries tried (all returned nothing carrying the figure):
1. "Shipley Associates proposals rejected noncompliant percentage federal RFP" (rate-limited 429)
2. "proposals non-compliant percent rejected federal government contracting Shipley"
3. ""eliminated" proposals "non-compliance" OR "noncompliance" "before" evaluation percent Shipley study"
4. ""percent of proposals" rejected OR discarded compliance RFP government statistics"
5. ""noncompliant" OR "non-compliant" proposals "before" evaluation eliminated government contracting percentage"
6. "Shipley "compliance review" percent proposals fail eliminated"
7. ""half" OR "50%" OR "30%" proposals "compliance" "thrown out" OR "disqualified" OR "rejected" RFP statistics bid writing"

### What the primary sources DO say (checked directly):
- Shipley Associates' own blog post "Business Winning Tip: Compliance and Responsiveness" (https://www.shipleywins.com/blogs/compliance-and-responsiveness, © 2009–2026, fetched 2026-10-09) defines compliance vs responsiveness but contains NO percentage figure whatsoever. Attribution of "30-50%" to Shipley is NOT supported by Shipley's own published content.
- GovEagle blog "Disqualified by GovCon Compliance Errors?" (https://www.goveagle.com/blog/disqualified-govcon-compliance-errors, published 2026-04-27, updated 2026-09-26) documents that compliance disqualification is real and frequent in US federal contracting (FAR 52.215-1 late/non-conforming rejection; FAR 52.212-3 unsigned reps; page-limit/font violations; GAO case RiverNorth, Inc., B-423274.2/B-423274.3, Apr 18 2025, where a vendor was eliminated from a USDA FAR 8.4 competition for sub-12pt Times New Roman page numbers) — but again gives NO "30-50%" figure.
- The PHENOMENON (US proposals eliminated for non-compliance before scoring) is therefore well documented; the QUANTIFIED "30-50%" claim is not. No GAO report, no Shipley publication, no industry article with the figure surfaced in any of the 7 query formulations. It may circulate as training folklore, but I could not locate its primary origin.

### Verdict sub-point 2: REFUTED as stated / UNVERIFIED
The specific statistic "30-50% of US government proposals are eliminated for non-compliance before scoring" could not be traced to any primary source; the Shipley attribution is contradicted by Shipley's own blog (no figure); GAO debriefing data as a source was not found either. The underlying phenomenon is real (documented via FAR clauses and GAO decisions), so the claim is "real phenomenon, unsupported number" — the number should not be repeated as fact.

## Sub-point 3: Is responding in the customer's exact format mandatory (様式必須)? — CONFIRMED for the requirement table; NUANCED overall

Evidence:
- Hofu City: the 機能要件確認書 (様式3) is the CITY'S OWN xlsx template; instruction "下記の機能要件項目について、対応欄に回答すること" — vendor must fill the city's spreadsheet and return it. Mandatory format for the requirement-response table.
- Choshi City: 機能評価表 (様式7) is a distributed fixed form; must be submitted in Excel format on CD-R ("機能評価表（様式７）は、Excelファイル形式で保存したCD-R等の媒体についても併せて提出すること"). The 見積書 is 様式6 (fixed); the narrative 企画提案書 is 任意様式 (free format) but with a MANDATORY item order (10 numbered sections) and 50-page limit. 失格事項 (disqualification): late submission, false statements, unfair conduct, missing presentation.
- Matsumoto City (松本市, Nagano): 参加表明書 form lists "企画提案書（任意様式）" alongside fixed 様式第4/5/6号 forms (https://www.city.matsumoto.nagano.jp/uploaded/life/186172_646954_misc.docx, fetched via search 2026-10-09).
- Nagareyama City (流山市, Chiba): "本業務に対する提案書（任意様式 Ａ３版）" — free format but page size fixed (https://www.city.nagareyama.chiba.jp/_res/projects/default_project/_page_/001/051/027/1yousiki.docx).
- Vendor guide (digital-supporter.net 第116章): "発注者が要件確認書の様式を用意している場合は、その様式で提出します。" (when the ordering party provides a 要件確認書 form, submit using that form) and "様式で章立てが指定されていれば、それに従う" (follow the form's chapter structure if specified).

### Verdict sub-point 3: CONFIRMED (for the requirement-response table) with nuance
The specific thing the claim is about — the requirement-response table (機能要件確認書/機能評価表/要件充足表) — is indeed a customer-mandated format: the municipality distributes its own Excel/Word template and the vendor must fill it in and return it, often in the original file format. However, the broader statement "everything must be in the customer's exact format" is NOT universally true: the narrative 企画提案書 is frequently declared 任意様式 (free format), albeit with mandatory structure/page limits. So "mẫu bắt buộc" holds for the requirement table specifically, not for the whole proposal.

## Sources
- Hofu City 機能要件確認書 xlsx (様式3): https://www.city.hofu.yamaguchi.jp/uploaded/attachment/120690.xlsx (fetched 2026-10-09)
- Choshi City プロポーザル実施要領 PDF (Reiwa 8, May 2026): https://www.city.choshi.chiba.jp/content/000068784.pdf (fetched 2026-10-09)
- Matsusaka City 企画提案書（機能要件説明書）doc (様式第2-2号): https://www.city.matsusaka.mie.jp/uploaded/attachment/28606.doc (fetched 2026-10-09)
- digital-supporter.net 第116章 要件充足表 guide (updated 2026-10-09): https://digital-supporter.net/mirai-ai/siyousho/teiansho-kousei-hyouka-kijun.html (fetched 2026-10-09)
- Shipley Associates, "Business Winning Tip: Compliance and Responsiveness" (© 2009–2026): https://www.shipleywins.com/blogs/compliance-and-responsiveness (fetched 2026-10-09)
- GovEagle, "Disqualified by GovCon Compliance Errors?" (2026-04-27, upd. 2026-09-26): https://www.goveagle.com/blog/disqualified-govcon-compliance-errors (fetched 2026-10-09)
- Matsumoto City 参加表明書/様式 list docx: https://www.city.matsumoto.nagano.jp/uploaded/life/186172_646954_misc.docx (via search, 2026-10-09)
- Nagareyama City 様式集 docx: https://www.city.nagareyama.chiba.jp/_res/projects/default_project/_page_/001/051/027/1yousiki.docx (via search, 2026-10-09)