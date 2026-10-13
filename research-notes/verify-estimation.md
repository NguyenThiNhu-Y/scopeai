# Xác minh (REFUTE): "Cone of uncertainty 0.25x–4.0x (Boehm 1981); McKinsey/Oxford 2012: 5.400+ dự án IT, vượt ngân sách trung bình 45%; PMBOK WBS: quy tắc 100% và work package 8–80 giờ"

Người xác minh: subagent VERIFIER (adversarial)
Ngày hoàn thành: 2026-10-09
Ngôn ngữ: Tiếng Việt (theo yêu cầu báo cáo cuối)

---

## TÓM TẮT PHÁN QUYẾT

| Phần | Nội dung claim | Phán quyết |
|---|---|---|
| 1 | Cone of uncertainty, ước lượng sớm 0.25x–4.0x (Boehm 1981) | **CONFIRMED** (có sắc thái: Boehm gọi là "Funnel Curve", số liệu mang tính chủ quan; tên "cone of uncertainty" do McConnell đặt) |
| 2 | McKinsey/Oxford 2012: 5.400+ dự án IT, vượt ngân sách trung bình 45% | **CONFIRMED** (đúng nguyên văn nguồn chính; kèm cảnh báo phương pháp luận) |
| 3a | PMBOK WBS: quy tắc 100% | **CONFIRMED** (có trong PMBOK Guide 4th ed. và là một mục riêng trong PMI Practice Standard for WBS) |
| 3b | PMBOK WBS: work package 8–80 giờ | **REFUTED** (KHÔNG có trong PMBOK Guide 4th ed. — đã grep toàn văn; không có trong PMI Practice Standard for WBS 2nd ed.; là heuristic truyền miệng, phổ biến qua sách ôn thi PMP) |
| 4 | Bằng chứng mâu thuẫn về độ chính xác ước lượng | **TÌM THẤY NHIỀU** (Little 2006, Jørgensen 2004, Flyvbjerg & Budzier 2011, Bossavit 2013) |

---

## PHẦN 1 — Cone of uncertainty của Boehm (0.25x–4.0x) — **CONFIRMED**

**Số liệu 0.25x–4.0x ở giai đoạn sớm nhất là chính xác và được gán đúng cho Boehm 1981.**

- Wikipedia ("Cone of uncertainty", bản sửa 18/08/2026) dẫn trực tiếp Boehm 1981: "Research in the software industry on the cone of uncertainty stated that in the beginning of the project life cycle (i.e. before gathering of requirements) estimates have in general an uncertainty of factor 4 on both the high side and the low side. This means that the actual effort or scope can be 4 times or 1/4 of the first estimates." — chú thích dẫn [Boehm 1981], tr. 311. Nguồn: https://en.wikipedia.org/wiki/Cone_of_uncertainty
- BudgetOverrun.com tái dựng bảng "Reproduced from Boehm B. (1981). Software Engineering Economics. Prentice Hall. Figure 21-1": Initial concept 0.25x–4.0x (spread 16x); Approved product definition 0.50x–2.0x; Requirements specification 0.67x–1.5x; Product design 0.80x–1.25x; Detailed design 0.90x–1.10x; Accepted product 1.0x. Nguồn: https://budgetoverrun.com/cone-of-uncertainty (truy cập 2026-10-09)
- Steve McConnell (Construx, trích từ *Software Estimation*, 2006): "Estimates created at Initial Concept time can be inaccurate by a factor of 4x on the high side or 4x on the low side (also expressed as 0.25x, which is just 1 divided by 4). The total range from high estimate to low estimate is 4x divided by 0.25x, or 16x." Nguồn: https://www.construx.com/books/the-cone-of-uncertainty/

**Sắc thái làm yếu claim (quan trọng cho phần "refute"):**
1. **Boehm không gọi nó là "cone of uncertainty"** — ông gọi là "Funnel Curve". Wikipedia: "Boehm referred to the concept as the 'Funnel Curve'". Cái tên "cone of uncertainty" xuất hiện lần đầu trong *Software Project Survival Guide* của Steve McConnell (1997). Vậy claim "(Boehm 1981)" về con số là đúng, nhưng thuật ngữ "cone of uncertainty" không phải của Boehm.
2. **Số liệu của Boehm là chủ quan (subjective), không phải từ tập dữ liệu lớn**: Wikipedia ghi rõ "Boehm's initial quantification of the effects of the Funnel Curve were subjective" — chỉ sau đó Boehm và đồng nghiệp tại USC mới áp dữ liệu Không quân Mỹ và NASA để kiểm chứng mô hình. Đây là điểm yếu nhất của claim: con số 0.25x–4.0x là phán đoán chuyên gia của Boehm, không phải kết quả thống kê.
3. **Cone mô tả "best case accuracy" của estimator giỏi** (McConnell), không phải mức sai số điển hình — các dự án kém kiểm soát có thể giữ độ bất định rộng đến tận khi bàn giao ("Cloud of Uncertainty").

## PHẦN 2 — Nghiên cứu McKinsey/Oxford 2012 (45%, 5.400 dự án) — **CONFIRMED**

**Cả hai con số đều đúng nguyên văn nguồn chính.**

- Trích từ chính PDF của McKinsey (xuất hiện trong nhiều kết quả tìm kiếm, gồm bản lưu trên mckinsey.com): "Our research, conducted in collaboration with the University of Oxford, suggests that half of all large IT projects—defined as those with initial price tags exceeding $15 million—massively blow their budgets. On average, large IT projects run 45 percent over budget and 7 percent over time, while delivering 56 percent less value than predicted." Nguồn: https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/delivering-large-scale-it-projects-on-time-on-budget-and-on-value (PDF: https://www.mckinsey.com/~/media/McKinsey/Business+Functions/McKinsey+Digital/Our+Insights/Delivering+large+scale+IT+projects+on+time+on+budget+and+on+value/...pdf)
- Academia.edu (bản đầy đủ 6 trang, trích abstract): "...emerged from research recently conducted on more than 5,400 IT projects by McKinsey and the BT Centre for Major Programme Management at the University of Oxford." Nguồn: https://www.academia.edu/8258165/
- Financial Times, 21/08/2012: "A cross-industry study of more than 5,400 IT projects by McKinsey and the Centre for Major Programme Management at the University of Oxford reveals that the average overspend can top 45 per cent..." Nguồn: https://www.ft.com/content/d34acf86-eba8-11e1-9356-00144feab49a
- Chi tiết bổ sung (từ bản tóm tắt nghiên cứu neocode.com và budgetoverrun.com): tác giả Michael Bloch, Sven Blumberg, Jürgen Laartz (McKinsey Business Technology Office), xuất bản tháng 10/2012; mỗi năm kéo dài thêm làm tăng vượt chi phí trung bình 15%; 17% dự án thất bại nghiêm trọng đe dọa sự tồn tại của công ty. Nguồn: https://www.neocode.com/blog/research-summary-delivering-large-scale-it-projects-on-time-on-budget-and-on-value-by-michael-bloch-sven-blumberg-jurgen-laartz-mckinsey-company-2012/

**Cảnh báo phương pháp luận (điểm trừ cho claim):**
- Đây là **white paper tư vấn, không qua bình duyệt (peer review)**; mẫu từ cơ sở dữ liệu nội bộ của McKinsey bổ sung dữ liệu Oxford Saïd — không phải mẫu ngẫu nhiên đại diện (budgetoverrun.com: "drawn from a McKinsey project database supplemented by Oxford Said Business School data").
- Lưu ý phân biệt: con số **1.471 dự án** thường bị trộn lẫn với nghiên cứu này thực ra là của **Flyvbjerg & Budzier, HBR 09/2011** ("Why Your IT Project May Be Riskier Than You Think") — mẫu 1.471 dự án, vượt chi phí trung bình 27%, 1/6 dự án "Black Swan" vượt trung bình 200%. Nguồn: https://hbr.org/2011/09/why-your-it-project-may-be-riskier-than-you-think và bản arXiv https://arxiv.org/abs/1304.0265
- Claim "average budget overrun of 45%" khớp chính xác với cách nói của chính nghiên cứu ("on average... run 45 percent over budget"). Không tìm thấy tài liệu nào nói con số 45% là sai; tuy nhiên đây là trung bình của mẫu phi ngẫu nhiên, nên không nên trình bày như chân lý thống kê phổ quát.

## PHẦN 3a — PMBOK: quy tắc 100% — **CONFIRMED**

- **PMBOK Guide 4th Edition (2008), mục 5.3.2.2 Decomposition** (toàn văn từ archive.org, đã grep): "The WBS represents all product and project work, including the project management work. The total of the work at the lowest levels must roll up to the higher levels so that nothing is left out and no extra work is completed. **This is sometimes called the 100% rule.**" Nguồn: https://archive.org/stream/PMBOKGuide/PMBOK+Guide_djvu.txt
- **PMI Practice Standard for Work Breakdown Structures, 2nd ed. (2006), mục 2.4 "The 100% Rule"** (toàn văn từ epdf.pub, đã grep): "The 100% rule (Haugan, 2002, p 17) is a core characteristic of the WBS. This rule states that the WBS includes 100% of the work defined by the project scope and captures ALL deliverables—internal, external, and interim—in terms of work to be completed, including project management... The rule applies at all levels within the hierarchy: the sum of the work at the 'child' level must equal 100% of the work represented by the 'parent'..." Nguồn: https://epdf.pub/practice-standard-for-work-breakdown-structures.html
- Ấn bản 3rd ed. (2019/2021) của Practice Standard cũng có mục "2.3.1 THE 100 PERCENT RULE" (theo mục lục). Nguồn: https://dokumen.pub/practice-standard-for-work-breakdown-structures-3nbsped-1628256192-9781628256192.html

## PHẦN 3b — PMBOK: work package 8–80 giờ — **REFUTED** (không có trong PMBOK)

**Kiểm tra toàn văn PMBOK Guide 4th Edition (2008)** (tải từ archive.org, 1.2MB, đã strip HTML và grep): chuỗi "8/80", "8-80", "80 hours", "forty hours" — **0 kết quả**. Mục Decomposition 5.3.2.2 chỉ nói "excessive decomposition can lead to non-productive management effort" mà không đưa ra quy mô giờ nào.

**Kiểm tra toàn văn PMI Practice Standard for Work Breakdown Structures 2nd ed. (2006)** (epdf.pub, 232K ký tự, đã grep): "8/80" — **0 kết quả**; mọi "80" chỉ là số trang trong index. Chuẩn này cũng không có quy tắc 8–80 giờ.

**Bản chất thực của quy tắc 8/80 — folklore của nghề, không phải quy định PMBOK:**
- Từ điển thuật ngữ sách ôn thi PMP (O'Reilly, "PMP Project Management Professional All-in-One Exam Guide"): "8/80 Rule: **A planning heuristic** for creating the WBS. This rule states that the work package in a WBS must take no more than 80 hours of labor and no fewer than 8 hours..." — được dạy như heuristic, không viện dẫn PMBOK. Nguồn: https://www.oreilly.com/library/view/pmp-project-management/9781260467444/gloss.xhtml
- Chính PMI (bài hội nghị Lukas, PMI Global Congress 2007): "A suggested rule of thumb is that each task should represent between 20 to 80 hours of work. **This is different from the 8/80 rule**, but the 8/80 rule tends to drive the project team to create an excessive number of tasks." — tác giả PMI coi 8/80 là quy tắc riêng biệt, thậm chí khuyến nghị 20–80 giờ thay vì 8–80. Nguồn: https://www.pmi.org/learning/library/common-scheduling-mistakes-avoid-7221
- Nhiều nguồn (Taskade, wbsgantt, monday.com...) mô tả 8/80 là "guideline, not a PMBOK requirement". Nguồn: https://www.taskade.com/wiki/project-management/work-breakdown-structure

**Phán quyết**: claim "PMBOK's WBS rules include... work packages sized 8-80 hours" là **SAI về mặt quy kết nguồn** — quy tắc 8–80 giờ không nằm trong PMBOK Guide (ít nhất các ấn bản 4–6) cũng không nằm trong PMI Practice Standard for WBS; nó là heuristic truyền miệng phổ biến qua sách luyện thi PMP và blog quản trị dự án. Nếu muốn trích nguồn chính xác, phải nói "heuristic phổ biến trong nghề (thường được dạy trong tài liệu ôn thi PMP)", không phải "PMBOK rule".

## PHẦN 4 — Bằng chứng mâu thuẫn về độ chính xác ước lượng — **TÌM THẤY NHIỀU**

1. **Little (2006) bác bỏ tiền đề chính của cone**: Todd Little, "Schedule Estimation and Uncertainty Surrounding the Cone of Uncertainty", *IEEE Software*, Vol. 23, No. 3, 05/2006 — dữ liệu từ Landmark Graphics cho thấy độ bất định **không giảm** theo tiến độ dự án: "the data shows that uncertainty remains constant throughout the project's life cycle". Nguồn: https://www.researchgate.net/publication/3248373 và https://www.toddlittleweb.com/pubs.html
2. **Jørgensen (2004) — tổng quan 30 năm nghiên cứu thực nghiệm**: Magne Jørgensen, "A Review of Studies on Expert Estimation of Software Development Effort", *Journal of Systems and Software* 70 (2004) 37–60. Kết luận: ước lượng chuyên gia là chiến lược phổ biến nhất (84% tại một công ty telecom lớn) nhưng **thiên lệch hệ thống về lạc quan thái quá** ("planning fallacy" — Kahneman & Tversky); các mô hình ước lượng làm giảm rủi ro vượt lớn. Nguồn: https://cms.simula.no/sites/default/files/publications/SE.4.Joergensen.2004.c.pdf và https://www.sciencedirect.com/science/article/pii/S0164121202001565
3. **Flyvbjerg & Budzier (2011)**: mẫu 1.471 dự án IT, vượt chi phí trung bình **27%** (thấp hơn 45% của McKinsey — cho thấy con số 45% không phải phổ quát), nhưng đuôi phân phối rất nặng: 1/6 dự án "Black Swan" vượt trung bình 200%. Nguồn: https://hbr.org/2011/09/why-your-it-project-may-be-riskier-than-you-think ; https://arxiv.org/abs/1304.0265
4. **Bossavit (2013)**: cuốn *The Leprechauns of Software Engineering* (Leanpub, 2013) truy vấn cơ sở thực nghiệm của nhiều "luật" kỹ nghệ phần mềm, trong đó có cone of uncertainty — cho rằng chúng thiếu dữ liệu gốc kiểm chứng. Nguồn: https://leanpub.com/leprechauns (được Wikipedia dẫn trong "Further reading").
5. Bản thân Wikipedia ghi Boehm's quantification là "subjective" (xem Phần 1) — điểm yếu cố hữu của con số 0.25x–4.0x.

---

## DANH SÁCH NGUỒN (URL + ngày truy cập)

1. Wikipedia — Cone of uncertainty (sửa 18/08/2026; truy cập 09/10/2026): https://en.wikipedia.org/wiki/Cone_of_uncertainty
2. BudgetOverrun.com — Boehm's Cone (truy cập 09/10/2026): https://budgetoverrun.com/cone-of-uncertainty
3. Construx — The Cone of Uncertainty (McConnell): https://www.construx.com/books/the-cone-of-uncertainty/
4. McKinsey — Delivering large-scale IT projects (Bloch, Blumberg, Laartz, 10/2012): https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/delivering-large-scale-it-projects-on-time-on-budget-and-on-value
5. Academia.edu — bản PDF nghiên cứu McKinsey: https://www.academia.edu/8258165/
6. Financial Times — 21/08/2012: https://www.ft.com/content/d34acf86-eba8-11e1-9356-00144feab49a
7. Neocode — tóm tắt nghiên cứu McKinsey: https://www.neocode.com/blog/research-summary-delivering-large-scale-it-projects-on-time-on-budget-and-on-value-by-michael-bloch-sven-blumberg-jurgen-laartz-mckinsey-company-2012/
8. BudgetOverrun.com — McKinsey-Oxford study: https://budgetoverrun.com/studies/mckinsey-large-it-projects
9. Archive.org — toàn văn PMBOK Guide 4th ed. (2008): https://archive.org/stream/PMBOKGuide/PMBOK+Guide_djvu.txt
10. epdf.pub — PMI Practice Standard for WBS 2nd ed. (2006): https://epdf.pub/practice-standard-for-work-breakdown-structures.html
11. dokumen.pub — Practice Standard for WBS 3rd ed. (2019): https://dokumen.pub/practice-standard-for-work-breakdown-structures-3nbsped-1628256192-9781628256192.html
12. O'Reilly — PMP All-in-One Exam Guide glossary (8/80 Rule): https://www.oreilly.com/library/view/pmp-project-management/9781260467444/gloss.xhtml
13. PMI — Lukas, "Common scheduling mistakes" (2007): https://www.pmi.org/learning/library/common-scheduling-mistakes-avoid-7221
14. Little, IEEE Software 05/2006: https://www.toddlittleweb.com/pubs.html ; https://www.researchgate.net/publication/3248373
15. Jørgensen 2004 (toàn văn PDF, Simula): https://cms.simula.no/sites/default/files/publications/SE.4.Joergensen.2004.c.pdf ; ScienceDirect: https://www.sciencedirect.com/science/article/pii/S0164121202001565
16. Flyvbjerg & Budzier, HBR 09/2011: https://hbr.org/2011/09/why-your-it-project-may-be-riskier-than-you-think ; arXiv: https://arxiv.org/abs/1304.0265

## GHI CHÚ PHƯƠNG PHÁP
- Không thể tải trực tiếp PDF McKinsey (mckinsey.com timeout) và PDF PMBOK 6th ed.; kết luận Phần 2 dựa trên trích dẫn nguyên văn từ chính PDF McKinsey xuất hiện trong nhiều nguồn độc lập (kể cả FT) + bản đầy đủ trên academia.edu; kết luận Phần 3 dựa trên toàn văn PMBOK 4th ed. + Practice Standard 2nd ed. (đã grep trực tiếp) và bản tóm tắt 6th ed. (4squareviews) không hề nhắc 8/80.
- Không tìm thấy nguồn xác nhận chi tiết "45% tính trên tập con 1.471 dự án" trong nghiên cứu McKinsey — mặc dù con số 1.471 xuất hiện trong nghiên cứu Flyvbjerg & Budzier cùng chủ đề; không khẳng định điều này.