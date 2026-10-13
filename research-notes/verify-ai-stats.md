# Xác minh: Thống kê thất bại dự án AI (Gartner 85%, CrowdFlower 60-80%, chi phí PoC vs production)

**Nhiệm vụ:** Kiểm tra đối nghịch tuyên bố: (a) dự án AI/data thất bại hoặc không đạt kỳ vọng với tỷ lệ cao (Gartner 2/2018: 85% dự án AI cho kết quả sai lầm; Heudecker 2016: 85% dự án data science thất bại), (b) chuẩn bị dữ liệu chiếm 60-80% thời gian dự án (khảo sát CrowdFlower 2016), (c) PoC rẻ hơn ~5-7 lần và nhanh hơn ~4 lần so với hệ thống AI production.

**Ngày xác minh:** 2026-10-09. **Phương pháp:** truy tìm nguồn gốc (press release gốc của Gartner, PDF khảo sát gốc của CrowdFlower, PDF báo cáo gốc MIT NANDA), đối chiếu chéo nguồn thứ cấp cùng thời, và tìm bằng chứng mới hơn.

---

## Tóm tắt phán quyết

| Luận điểm | Phán quyết |
|---|---|
| Gartner 2/2018: "85% dự án AI sẽ cho kết quả sai lầm" | **XÁC NHẬN (có điều chỉnh quan trọng)** — press release gốc 13/2/2018 có đúng câu này, nhưng đó là *dự báo* "qua năm 2022", về "erroneous outcomes do bias", không phải tỷ lệ thất bại đo được |
| Heudecker: "85% dự án data science thất bại" | **MỘT PHẦN BÁC BỎ** — con số 85% và người nói là thật, nhưng là **tháng 11/2017** (không phải 2016), nói về "big data projects", tweet gốc đã bị xóa |
| CrowdFlower 2016: chuẩn bị dữ liệu chiếm 60-80% thời gian | **MỘT PHẦN XÁC NHẬN / MỘT PHẦN BÁC BỎ** — 60% là đúng theo khảo sát gốc (nhưng là câu hỏi "tốn nhiều thời gian nhất", không phải % thời gian dự án đo được); **80% không hề nằm trong khảo sát** — chỉ xuất hiện khi cộng gộp "thu thập dữ liệu" (19%) vào "làm sạch" (60%), và chính báo cáo gán con số 80% cho một ước tính của NYT |
| Bằng chứng mới hơn về tỷ lệ thất bại | **HƯỚNG "thất bại/thất vọng cao" được ủng hộ, nhưng con số 85% đã lỗi thời** — Gartner 2024 tự dự báo chỉ 30% dự án GenAI bị bỏ sau PoC; MIT SMR/BCG 2019: 70% công ty báo tác động tối thiểu/không có; MIT NANDA 2025: 95% GenAI pilot không có tác động P&L đo được |
| PoC rẻ hơn 5-7x và nhanh hơn 4x | **KHÔNG XÁC MINH ĐƯỢC như một quy luật chung** — nguồn gốc là một bài blog của hãng gia công SlashDev (4/2026): PoC $5-15k/2-4 tuần vs production $25-100k+/8-16 tuần; tỷ lệ 5-7x/4x chỉ là số học suy ra từ dải giá của riêng một vendor, không có nghiên cứu độc lập nào xác nhận |

---

## Phần 1 — Press release Gartner tháng 2/2018: XÁC NHẬN (đúng nguyên văn, nhưng là dự báo, không phải tỷ lệ thất bại)

Press release gốc tồn tại và tôi đã đọc trực tiếp trên gartner.com: **["Gartner Says Nearly Half of CIOs Are Planning to Deploy Artificial Intelligence"](https://www.gartner.com/en/newsroom/press-releases/2018-02-13-gartner-says-nearly-half-of-cios-are-planning-to-deploy-artificial-intelligence)**, Stamford, Conn., **13 tháng 2, 2018**. Câu trích nguyên văn nằm trong phần "Lesson 3: Plan for Knowledge Transfer":

> "Gartner predicts that through 2022, 85 percent of AI projects will deliver erroneous outcomes due to bias in data, algorithms or the teams responsible for managing them."

Câu này được đặt cạnh phát biểu của **Jim Hare**, research vice president tại Gartner ("Data is the fuel for AI..."). Như vậy tuyên bố trong đề bài ("Gartner Feb 2018: 85% of AI projects produce erroneous outcomes") **đúng về mặt tồn tại và nguyên văn** — "produce erroneous outcomes" là diễn đạt lại trung thực của "will deliver erroneous outcomes".

Tuy nhiên có **ba sắc thái quan trọng** mà bất kỳ trích dẫn nào cũng phải giữ:
1. Đây là một **dự báo** ("Gartner predicts") cho giai đoạn **"through 2022"**, không phải một tỷ lệ thất bại đã đo đạc.
2. Nội hàm là **"erroneous outcomes do bias trong dữ liệu, thuật toán hoặc đội ngũ quản lý"** — tức kết quả sai lệch do thiên kiến, **không phải "dự án thất bại"** theo nghĩa bị hủy/không lên production. Việc gộp hai khái niệm này là lỗi trích dẫn phổ biến nhất (xem phần 4).
3. Chính press release này cũng cho biết bối cảnh: chỉ **4% CIO đã triển khai AI** và 46% có kế hoạch — tức con số 85% là dự báo cho một giai đoạn AI còn rất sơ khai.

Một số nguồn thứ cấp gán sai ngày cho phát biểu này (ví dụ [Gender Toolkit BII](https://gendertoolkit.bii.co.uk/emerging-trends/tech-transformation/intelligence-of-everything/) ghi "Gartner (2016)... by 2022") — sai; nguồn gốc chính xác là press release 13/2/2018 nói trên.

## Phần 2 — Heudecker "85% dự án data science thất bại": MỘT PHẦN BÁC BỎ (sai năm, sai đối tượng, tweet gốc đã xóa)

Chuỗi sự kiện thực tế, tái dựng từ nguồn cùng thời:
- **15/9/2015** — press release gốc của Gartner **["Gartner Says Business Intelligence and Analytics Leaders Must Focus on Mindsets and Culture to Kick Start Advanced Analytics"](https://www.gartner.com/en/newsroom/press-releases/2015-09-15-gartner-says-business-intelligence-and-analytics-leaders-must-focus-on-mindsets-and-culture-to-kick-start-advanced-analytics)** (Egham, UK, người phát ngôn Lisa Kart, research director): *"Gartner predicts that, through 2017, 60 percent of big data projects will fail to go beyond piloting and experimentation, and will be abandoned."* Đây là con số 60% — gốc rễ của cả câu chuyện.
- **Tháng 11/2017** — Nick Heudecker (khi đó là Gartner analyst, sau này sang AWS) tweet rằng Gartner đã "too conservative" với ước tính 60%, tỷ lệ thực "closer to 85%". Tweet ID **928720268662530048** (được link trong [bài Digital News Asia, 16/4/2019](https://www.digitalnewsasia.com/insights/why-85-big-data-projects-fail), ID này tương ứng đầu tháng 11/2017). **Tweet đã bị xóa** — chính bài DNA ghi "Since then, the tweet Heudecker sent has been deleted."
- **10/11/2017** — [TechRepublic](https://www.techrepublic.com/article/85-of-big-data-projects-fail-but-your-developers-can-help-yours-succeed/) đưa tin cùng thời điểm: "A year ago, Gartner estimated that 60% of big data projects fail... According to Gartner analyst Nick Heudecker this week, Gartner was [too conservative]".

Phán quyết cho luận điểm "Heudecker 2016: 85% of data science projects fail": **con số 85% và người nói là có thật, nhưng năm sai (2017, không phải 2016)** và đối tượng gốc là **"big data projects"** — việc chuyển thành "data science projects" là diễn giải phổ biến trong văn liệu thứ cấp (vd [Curated SQL 10/2020](https://curatedsql.com/2020/10/05/reasons-data-science-projects-fail/), [Vyom Data Sciences](https://www.datasciences.in/blog?blogname=whydatascienceprojectsfail), [itnext.io](https://itnext.io/how-to-accurately-estimate-a-data-science-project-a-step-by-step-framework-472f97308543) ghi "Back in 2016... estimated"). Nguồn gốc chính (tweet) đã biến mất, chỉ còn chứng cứ gián tiếp đồng thuận của hai nguồn cùng thời (TechRepublic, DNA) — nên không thể xác minh nguyên văn, chỉ xác minh được nội dung và mốc thời gian.

## Phần 3 — CrowdFlower 2016 "chuẩn bị dữ liệu chiếm 60-80% thời gian": 60% ĐÚNG, 80% SAI NGUỒN

Tôi đã tải và đọc **báo cáo gốc**: [CrowdFlower 2016 Data Scientist Report (PDF)](https://www2.cs.uh.edu/~ceick/UDM/CFDS16.pdf) (bản sao công khai; bản chính thức tại figure-eight.com). Phần "How a Data Scientist Spends Their Day" trình bày **một câu hỏi lựa chọn đơn** "What data scientists spend the most time doing" với kết quả: **Cleaning and organizing data: 60%**, Collecting data sets: 19%, Mining data for patterns: 9%, Building training sets: 3%, Refining algorithms: 4%, Other: 5%. Báo cáo viết: "3 out of every 5 data scientists we surveyed actually spend the most time cleaning and organizing data" và "nearly 60% said they simply spent too much time doing it."

Hai lưu ý quan trọng:
1. **60% là tỷ lệ chọn "tốn nhiều thời gian nhất"** (categorical plurality), **không phải tỷ lệ phần trăm thời gian dự án đo được** — diễn đạt "chiếm 60% thời gian dự án" là phóng đại phương pháp luận của câu hỏi.
2. **Con số 80% không hề nằm trong khảo sát.** Chính báo cáo ghi: "a few years back, the New York Times estimated that up to 80% of a data scientist's time is spent doing this sort of work" — tức 80% đến từ [bài NYT tháng 8/2014](https://www.nytimes.com/2014/08/18/technology/for-big-data-scientists-hurdle-to-insights-is-janitor-work.html) ("spend from 50 percent to 80 percent of their time... collecting and preparing unruly digital data"), một ước tính phỏng vấn, không phải khảo sát. Con số 80% phổ biến trong văn liệu (vd [Forbes/Gil Press 23/3/2016](https://www.forbes.com/sites/gilpress/2016/03/23/data-preparation-most-time-consuming-least-enjoyable-data-science-task-survey-says/)) chỉ đứng vững nếu **cộng gộp "thu thập dữ liệu" (19%) vào "làm sạch" (60%)** ≈ 79-80% — chính [Leigh Dodds (31/1/2020)](https://blog.ldodds.com/2020/01/31/do-data-scientists-spend-80-of-their-time-cleaning-data-turns-out-no/) đã chỉ ra điều này và kết luận "it's a bullshit statistic": các khảo sát sau đó cho số thấp hơn nhiều — CrowdFlower 2017: **51%** (collecting/labeling/cleaning/organizing), Kaggle 2018: **~11% gathering + 15% cleaning**, Figure Eight 2019: 73.5% dành **≥25%** thời gian cho managing/cleaning/labeling.

Phán quyết: khoảng "60-80%" của đề bài **không đứng vững**: 60% đúng nhưng bị hiểu sai bản chất câu hỏi; 80% là **sai nguồn** (NYT 2014, không phải CrowdFlower 2016) và bị các khảo sát sau bác bỏ.

## Phần 4 — Bằng chứng mới hơn: hướng "thất bại cao" vẫn được ủng hộ, nhưng 85% là con số lỗi thời

Các nguồn chính (primary) tìm được:

- **Gartner, 29/7/2024** — press release gốc **["Gartner Predicts 30% of Generative AI Projects Will Be Abandoned After Proof of Concept By End of 2025"](https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025)** (Sydney; Rita Sallam, Distinguished VP Analyst): *"At least 30% of generative AI (GenAI) projects will be abandoned after proof of concept by the end of 2025, due to poor data quality, inadequate risk controls, escalating costs or unclear business value."* Cùng release cho biết chi phí triển khai GenAI dao động **$5-20 triệu**. Đây là dự báo mới nhất của chính Gartner về "bỏ dự án" — **thấp hơn hẳn 85%** và gắn trực tiếp với giai đoạn PoC.
- **Gartner, 19/10/2020** — theo trích dẫn trong [The Lindahl Letter (15/10/2021)](https://www.nelsx.com/p/do-most-ml-projects-fail) dẫn [press release Top Strategic Technology Trends 2021](https://www.gartner.com/en/newsroom/press-releases/2020-10-19-gartner-identifies-the-top-strategic-technology-trends-for-2021): "Gartner research shows only **53%** of projects make it from AI prototypes to production."
- **MIT SMR + BCG, "Winning With AI", 15/10/2019** — [trang báo cáo gốc](https://sloanreview.mit.edu/projects/winning-with-ai/), khảo sát **2.500+ giám đốc**: "Seven out of 10 companies surveyed report minimal or no impact from AI so far"; "Among the 90% of companies that have made some investment in AI, fewer than 2 out of 5 report business gains from AI in the past three years"; "40% of organizations making significant investments in AI do not report business gains." Đây là bằng chứng độc lập (không phải Gartner) cho thấy **phần lớn công ty chưa thu được giá trị từ AI** — ủng hộ hướng "underdeliver".
- **MIT Project NANDA, "The GenAI Divide: State of AI in Business 2025" (7/2025)** — [PDF báo cáo gốc](https://readwise-assets.s3.amazonaws.com/media/wisereads/articles/the-genai-divide-state-of-ai-i/v0.1_State_of_AI_in_Business_2025_Report.pdf), tôi đã tải và đọc: "Despite $30–40 billion in enterprise investment into GenAI... **95% of organizations are getting zero return**. Just 5% of integrated AI pilots are extracting millions in value"; "The 95% failure rate for enterprise AI solutions represents the clearest manifestation of the GenAI Divide." Lưu ý: đây là tỷ lệ **pilot không có tác động P&L đo được**, định nghĩa hẹp (báo cáo tự ghi chú định nghĩa "successfully implemented"), và có phê bình rằng "no measurable impact ≠ fail" ([Marketing AI Institute](https://www.marketingaiinstitute.com/blog/mit-study-ai-pilots)); đồng thời chính báo cáo cho thấy chatbot LLM generic có tỷ lệ pilot→implementation ~83%.

Tổng hợp: **hướng "dự án AI thường thất bại/không đạt kỳ vọng" được nhiều nguồn độc lập ủng hộ** (MIT SMR/BCG 2019, MIT NANDA 2025, Gartner 2020/2024), nhưng **con số cụ thể 85% là dự báo của Gartner 2018 về "erroneous outcomes do bias" qua 2022 — không nên trình bày như tỷ lệ thất bại hiện hành**; dự báo gần nhất của chính Gartner (2024) chỉ là 30% bị bỏ sau PoC. Cũng có cảnh báo về việc lạm dụng các con số kiểu này ([The Lindahl Letter](https://www.nelsx.com/p/do-most-ml-projects-fail) chỉ ra 85% thường bị trích sai ngữ cảnh).

## Phần 5 — "PoC rẻ hơn 5-7x và nhanh hơn 4x": KHÔNG XÁC MINH ĐƯỢC như quy luật chung

Truy vết nguồn gốc: tuyên bố này **không tìm thấy trong bất kỳ nghiên cứu độc lập nào** (đã thử nhiều cụm từ tìm kiếm: "5-7x cheaper", "7x cheaper production AI", "PoC vs production cost ratio" — chỉ ra các kết quả không liên quan về giá token LLM). Nguồn duy nhất khớp chính xác là **bài blog của hãng gia công AI SlashDev: ["AI Agent POC vs Production Build" (4/2026)](https://slashdev.io/answers/ai-agent-poc-vs-production-build)** — tôi đã đọc trực tiếp. Số liệu gốc của bài:

- PoC: **$5.000-$15.000, 2-4 tuần** (tính theo giá $50/giờ của SlashDev, 100-300 giờ)
- Production: **$25.000-$100.000+, 8-16 tuần**

Số học: 25.000/5.000 = **5x**; 100.000/15.000 ≈ **6,7x**; thời gian 16/4 = **4x** (và 8/2 = 4x). Vậy "5-7x rẻ hơn, 4x nhanh hơn" **là số học trung thực suy ra từ dải giá của bài viết** — nhưng: (1) đây là **dải giá của một vendor duy nhất** (bài mang tính marketing dịch vụ, không có phương pháp luận hay cỡ mẫu), (2) áp dụng cho **AI agent** cụ thể, không phải mọi hệ thống AI, (3) "cheaper" là so sánh dải chi phí, không phải đo lường đối chứng. Ghi chú nghiên cứu hiện có [ai-project-estimation.md](../research-notes/ai-project-estimation.md) đã trích nguồn này và diễn đạt đúng tinh thần ("PoC $5k-15k/2-4 tuần vs production $25k-100k+/8-16 tuần"), nhưng tuyên bố dạng "PoC rẻ hơn 5-7x và nhanh hơn 4x" **không nên trình bày như một sự thật chung** — phải gán nguồn SlashDev và nêu rõ phạm vi (AI agent, dải giá vendor).

---

## Danh sách nguồn

**Primary (đã đọc trực tiếp):**
- Gartner press release 13/2/2018 — https://www.gartner.com/en/newsroom/press-releases/2018-02-13-gartner-says-nearly-half-of-cios-are-planning-to-deploy-artificial-intelligence
- Gartner press release 15/9/2015 (60% big data) — https://www.gartner.com/en/newsroom/press-releases/2015-09-15-gartner-says-business-intelligence-and-analytics-leaders-must-focus-on-mindsets-and-culture-to-kick-start-advanced-analytics
- Gartner press release 29/7/2024 (30% GenAI abandoned) — https://www.gartner.com/en/newsroom/press-releases/2024-07-29-gartner-predicts-30-percent-of-generative-ai-projects-will-be-abandoned-after-proof-of-concept-by-end-of-2025
- CrowdFlower 2016 Data Scientist Report (PDF) — https://www2.cs.uh.edu/~ceick/UDM/CFDS16.pdf
- MIT SMR/BCG "Winning With AI" 15/10/2019 — https://sloanreview.mit.edu/projects/winning-with-ai/
- MIT Project NANDA "The GenAI Divide: State of AI in Business 2025" (PDF) — https://readwise-assets.s3.amazonaws.com/media/wisereads/articles/the-genai-divide-state-of-ai-i/v0.1_State_of_AI_in_Business_2025_Report.pdf
- SlashDev "AI Agent POC vs Production Build" 4/2026 — https://slashdev.io/answers/ai-agent-poc-vs-production-build

**Secondary (đã đọc trực tiếp):**
- Digital News Asia 16/4/2019 (Heudecker, tweet bị xóa) — https://www.digitalnewsasia.com/insights/why-85-big-data-projects-fail
- TechRepublic 10/11/2017 (Heudecker "this week") — https://www.techrepublic.com/article/85-of-big-data-projects-fail-but-your-developers-can-help-yours-succeed/
- Leigh Dodds 31/1/2020 (debunk 80%) — https://blog.ldodds.com/2020/01/31/do-data-scientists-spend-80-of-their-time-cleaning-data-turns-out-no/
- Forbes/Gil Press 23/3/2016 (CrowdFlower coverage) — https://www.forbes.com/sites/gilpress/2016/03/23/data-preparation-most-time-consuming-least-enjoyable-data-science-task-survey-says/
- KDnuggets 11/4/2016 (tóm tắt CrowdFlower) — https://www.kdnuggets.com/2016/04/crowdflower-2016-data-science-repost.html
- The Lindahl Letter 15/10/2021 (phê bình 85% + Gartner 53% 2020) — https://www.nelsx.com/p/do-most-ml-projects-fail
- NYT 18/8/2014 (nguồn gốc 80%) — https://www.nytimes.com/2014/08/18/technology/for-big-data-scientists-hurdle-to-insights-is-janitor-work.html
- Marketing AI Institute (phê bình định nghĩa MIT NANDA) — https://www.marketingaiinstitute.com/blog/mit-study-ai-pilots
- Curated SQL 5/10/2020 (trích dẫn Heudecker) — https://curatedsql.com/2020/10/05/reasons-data-science-projects-fail/

**Truy vấn đã thử không ra kết quả:** "5-7x cheaper 4x faster production AI" (nhiều biến thể) — không có nghiên cứu độc lập nào về tỷ lệ chi phí PoC/production; "Mateusz Kwasniak 85% source" — không truy cập được bài gốc.