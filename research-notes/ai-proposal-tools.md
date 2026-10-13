# Memo nghiên cứu: Các công cụ viết đề xuất / trả lời RFP hỗ trợ bởi AI — tính năng, giá cả và điểm yếu đã được ghi nhận

**Người nghiên cứu:** Research subagent (deep-research harness)
**Ngày:** 2026-10-09
**Phạm vi:** Loopio, Responsive (RFPIO), Qvidian (Upland), PandaDoc, Arphie, Draftable, Writer, HyperWrite RFP Assistant, Microsoft Copilot, Google Gemini, ChatGPT custom GPTs. Kèm review G2/Capterra, phân tích khoảng trống (gap analysis) cho một sản phẩm bidding-estimation.

---

## 1. Bối cảnh thị trường

Thị trường phần mềm RFP/proposal được ước tính ~2,3 tỷ USD, tăng trưởng 12–16% CAGR ([Stargazy](https://stargazy.io/resources/the-rfp-is-a-growth-engine-how-to-use-ai-where-it-actually-matters)); một ước tính khác đưa ra con số 3,2 tỷ USD với CAGR 14,8% ([PlanMySaaS](https://www.planmysaas.com/ideas/ai-saas-ideas/ai-rfp-response-generator)). RFP ảnh hưởng tới khoảng 39% tổng doanh thu doanh nghiệp theo benchmark ngành ([Bidara research, dẫn qua Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)). Chi phí phần mềm AI RFP dao động từ dưới 500 USD/tháng cho công cụ nhẹ đến trên 50.000 USD/năm cho nền tảng enterprise ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)).

Hai "ông lớn" cũ là Loopio (2014) và Responsive/RFPIO (2015), sinh ra ở kỷ nguyên tiền-generative-AI, theo mô hình "thư viện nội dung" (content library) làm trung tâm; các công cụ AI-native như Arphie (2023) xây dựng quanh AI agents có nguồn tham chiếu, kiến thức công ty sống và phê duyệt con người ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)). Glean phân loại thị trường thành 7 nhóm: nền tảng work-AI với knowledge graph (Glean), nền tảng retrieval-first (Loopio/Responsive), công cụ generation-first, nền tảng chuyên chính phủ, nền tảng agentic, công cụ QA phân tích đề xuất, và công cụ soạn thảo nhẹ cho đội nhỏ ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)).

## 2. Từng công cụ

### 2.1 Loopio
Nền tảng quản lý phản hồi RFP thành lập 2014, xoay quanh Library (thư viện câu trả lời được quản trị) và Projects; gói Foundations/Enhanced/Enterprise, AI (tính năng "Magic" / Response Intelligence) tạo bản nháp từ nội dung đã phê duyệt kèm citations và confidence scores ([Arphie so sánh](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie), [Loopio](https://loopio.com/)). **Giá:** không công khai, chỉ qua sales; theo dữ liệu giao dịch Vendr (144+ hợp đồng), giá trị hợp đồng trung vị là **23.915 USD/năm** (khoảng 11.770–58.277 USD), gói vào cửa khoảng 15.000–20.000 USD/năm, tính theo ghế 1.000–3.500 USD/người/năm; add-on có thể đội chi phí thêm 15–40% ([Inventive AI](https://www.inventive.ai/blog-posts/loopio-pricing)). Không có free tier hay free trial ([Inventive AI](https://www.inventive.ai/blog-posts/loopio-pricing)). **Người mua:** đội proposal mid-market/enterprise có ngân sách 5–6 chữ số và người chuyên trách thư viện ([Inventive AI](https://www.inventive.ai/blog-posts/loopio-pricing)). **Điểm mạnh:** thư viện nội dung trưởng thành, hỗ trợ tốt (~9,7/10 trên G2), giao diện dễ học, workflow doanh nghiệp (multi-step review, SSO, audit) ([Inventive AI](https://www.inventive.ai/blog-posts/loopio-pricing)). **Điểm yếu:** xếp hạng G2 4,7 sao nhưng đọc kỹ 610+ review thì "Magic AI falls short on nuanced questions, the content library demands constant manual upkeep, and import issues create work the tool was supposed to remove" ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)); Loopio yêu cầu người dùng tự review và cập nhật thư viện câu trả lời ([1up](https://1up.ai/loopio-vs-responsive/)); chi phí ẩn "library tax" — lao động duy trì thư viện có thể cộng thêm 30–100% vào tổng chi phí sở hữu ([Inventive AI](https://www.inventive.ai/blog-posts/loopio-pricing)).

### 2.2 Responsive (formerly RFPIO)
Nền tảng "Strategic Response Management" thành lập 2015 với tên RFPIO, đổi tên tháng 7/2023 ([RocketDocs](https://rocketdocs.com/resources/blog/responsive-pricing)). Kết hợp Content Library với intake, projects, dashboard, reporting, access controls; AI cập nhật 7/2023–2026 gồm agents nhập tài liệu, viết bản nháp, truy cập kiến thức, phân tích bid, kèm TRACE Score và citations ([Arphie so sánh](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)). **Giá:** 4 nấc Lite/Emerging/Growth/Enterprise, tất cả báo giá qua sales; ước tính 6.500–28.000 USD/năm, ~499 USD/người/tháng, tính theo ghế nên chi phí leo thang khi thêm người ([AutoRFP](https://autorfp.ai/blog/responsive-rfpio-pricing), [Thalamus AI](https://thalamushq.ai/blogs/responsive-review)). **Người mua:** mid-market và enterprise có khối lượng RFP lớn, hệ sinh thái tích hợp rộng ([G2 pricing FAQ](https://www.g2.com/products/responsive-formerly-rfpio/pricing)). **Điểm mạnh:** 20+ tích hợp native, 75+ API, Profile Center chia sẻ tài liệu bảo mật/tin cậy ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)); 190 review trên Capterra ([Capterra](https://www.capterra.com/p/148054/Responsive/reviews/)). **Điểm yếu:** tìm kiếm nội dung vẫn dựa trên keyword thay vì semantic AI; giá không minh bạch; SSO nằm sau add-on trả phí; trình soạn thảo văn bản nghèo nàn — review viên Cristine C. trên G2: "The text editing console is super basic, making content formatting tedious. Tables are flat out impossible, no formatting functionality at all" ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)); bộ tính năng rộng gây cấu hình/phức tạp không cần thiết cho đội nhỏ ([Arphie](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).

### 2.3 Qvidian (Upland)
Phần mềm quản lý đề xuất và phản hồi RFP của Upland Software, dùng "suite of automation and collaboration tools along with generative AI" ([G2 Upland Qvidian](https://www.g2.com/products/upland-qvidian/reviews)); AI Assist "works with an organization's content to consistently deliver accurate, compliant, and responsive responses" ([Capterra Qvidian](https://www.capterra.com/p/6944/Qvidian-Proposal-Automation/)). Tính năng: content library trung tâm, AutoFill cho câu hỏi lặp lại, review workflow tự động điều phối ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)). **Giá:** không công khai, báo giá theo hợp đồng; được coi là rẻ hơn Loopio/Responsive ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc), [Thalamus AI](https://thalamushq.ai/blogs/qvidian-pricing)). **Điểm mạnh:** thư viện nội dung và khả năng tái sử dụng mạnh ([Revuo](https://www.revuo.ai/category/tender-management/qvidian)). **Điểm yếu:** là sản phẩm legacy được thêm AI sau — "On nuanced questions the AutoFill output needs heavy editing"; giao diện cũ, đường cong học tập dốc; review viên Sierra trên G2: "Hoping for the AI to be useful in a way that makes sense for our organization in the future" ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)).

### 2.4 PandaDoc
Nền tảng tự động hóa tài liệu (proposal, quote, contract) với e-signature, thanh toán, analytics theo dõi khách mở tài liệu, tích hợp CRM (HubSpot, Salesforce, Pipedrive) ([Jotform](https://www.jotform.com/ai/best-ai-document-generator/), [aiagentsquare](https://aiagentsquare.com/blog/ai-document-automation)). AI tạo proposal từ thông tin khách hàng và template ([aiagentsquare](https://aiagentsquare.com/blog/ai-document-automation)). **Giá:** từ ~19,49 USD/người/tháng, nhắm vào đội sales chứ không phải freelancer đơn lẻ ([MicroGaps](https://www.microgaps.com/gaps/2026-02-14-ai-proposal-generator)); trang giá chính thức liệt kê các gói Starter trở lên ([PandaDoc pricing](https://www.pandadoc.com/pricing/)). **Điểm yếu:** không phải công cụ RFP chuyên dụng — là công cụ tài liệu; các nhà phê bình gọi output là "a prompt-generated doc... Still a document, still siloed" ([Taskade](https://www.taskade.com/blog/ai-proposal-generators)); thiếu workflow trả lời RFP nhiều người.

### 2.5 Arphie
Công cụ AI-native thành lập 2023, xây quanh AI agents dùng nội dung đã phê duyệt và nguồn kiến thức sống (Google Drive, SharePoint, Confluence, Notion, Seismic, Highspot, Salesforce, Front, Slack), mỗi bản nháp hiển thị nguồn và confidence signal, có "human approval from day one" ([Arphie](https://www.arphie.ai/), [Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)). **Giá:** custom quote; mô hình định giá theo concurrent-projects với chi phí năm cao ([AutoRFP blog](https://autorfp.ai/blog/arphie-pricing)); có free trial ([Inventive](https://www.inventive.ai/blog-posts/arphie-pricing-features-reviews)). **Bảo mật:** SOC 2 Type II, mã hóa, pentest hằng năm, SAML SSO, thỏa thuận zero-data-retention với nhà cung cấp model ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)). **Khách hàng công bố:** OfficeSpace giảm thời gian RFP từ 20 giờ xuống 2 giờ; BillingPlatform đạt 90%+ độ chính xác bản nháp đầu tiên (số liệu do chính vendor công bố) ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)). **Điểm yếu:** vendor trẻ, lịch sử vận hành ngắn (chính Arphie thừa nhận) ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).

### 2.6 Draftable — tiền đề trong đề bài KHÔNG được xác nhận
Draftable (draftable.com) **không phải** công cụ viết đề xuất/AI RFP. Đây là công cụ so sánh tài liệu và redline (Word, PDF, PowerPoint) dùng cho review pháp lý và văn bản: "Document comparison and legal solutions built with lawyers" ([Draftable](https://www.draftable.com/)). Giá: Business 129 USD/người/năm, Legal 261 USD/người/năm ([Draftable pricing](https://www.draftable.com/pricing)). Nó được tích hợp cạnh các công cụ proposal (ví dụ workflow n8n nối Better Proposals với Draftable ([n8n](https://n8n.io/integrations/better-proposals/and/draftable/))) nhưng không sinh nội dung đề xuất. Đã thử 2 truy vấn khác nhau ("Draftable RFP AI response software pricing", "Draftable AI proposal writing RFP bid tool") — không tìm thấy bằng chứng nào cho việc Draftable là công cụ AI viết proposal.

### 2.7 Writer
Nền tảng generative AI toàn diện cho enterprise (nhà cung cấp model Palmyra), định vị "the enterprise AI agent platform trusted by Fortune 500", với Knowledge Graph (graph-based RAG), AI Guardrails, connectors Salesforce/Microsoft 365/Google Workspace ([writer.com](https://writer.com/), [Writer Knowledge Graph guide](https://writer.com/guides/graph-based-rag-starter-guide/)). Trả lời RFP là một use case nằm trong nền tảng ngang (horizontal), không phải sản phẩm RFP chuyên dụng; không tìm thấy giá công khai trong phạm vi tìm kiếm (định vị enterprise, báo giá).

### 2.8 HyperWrite RFP Assistant — không tìm thấy tài liệu chuyên biệt
HyperWrite là trợ lý viết AI của OthersideAI (thành lập 2020) với AutoWrite, TypeAhead, Custom Personas, và AI Personal Assistant tự động hóa tác vụ trình duyệt ([CostBench](https://costbench.com/software/ai-writing-tools/hyperwrite/)). **Giá:** free tier; Premium 19,99 USD/tháng; Ultra 44,99 USD/tháng ([HyperWrite FAQ](https://www.hyperwriteai.com/faq/how-much-does-hyperwrite-cost)); Ultra trả năm ~29 USD/tháng ([ToolRadar](https://toolradar.com/tools/hyperwrite/pricing)). Riêng "RFP Assistant" — không tìm thấy trang sản phẩm, tài liệu hoặc review độc lập nào về một sản phẩm mang tên đó; đã thử 2 truy vấn. Kết luận trung thực: chưa xác nhận được sự tồn tại/đặc điểm của "HyperWrite RFP Assistant" như một sản phẩm riêng; HyperWrite là công cụ viết đa dụng.

### 2.9 Microsoft Copilot
Copilot trong Word/Excel/Teams truy xuất dữ liệu công ty qua Microsoft Graph và soạn câu trả lời từ file SharePoint/OneDrive; Microsoft có hẳn scenario library "Respond to an RFP" cho đội sales ([Microsoft Adoption](https://adoption.microsoft.com/en-us/scenario-library/sales/respond-to-an-rfp/)). **Điểm yếu (được 1up — một đối thủ — ghi lại chi tiết):** không giao việc cho SME, không xây được answer library tái sử dụng, không điền chính xác vào bảng hỏi có cấu trúc (dropdown/checkbox), và không với tới được web portal của bên mua (SAP Ariba, Coupa, Whistic) ([1up](https://1up.ai/blog/microsoft-copilot-rfp-limitations)). Ngoài ra, Copilot trong Word có giới hạn xử lý độ dài văn bản và "should clearly warn you when part of the document has not been considered, rather than returning an answer that appears complete" ([Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/6016267/word-limitations-on-copilot)).

### 2.10 Google Gemini
Gemini Apps (bản tiêu dùng) thu thập hội thoại và lưu hoạt động tới 18 tháng mặc định ([Gemini Apps Privacy Notice](https://support.google.com/gemini/answer/13594961?hl=en)); bản trong Google Workspace giữ dữ liệu trong tổ chức, không chia sẻ ra ngoài khi chưa được phép ([Google Workspace Privacy Hub](https://knowledge.workspace.google.com/admin/generative-ai/generative-ai-in-google-workspace-privacy-hub)). Gemini được dùng để viết proposal qua prompt templates trong Google Docs ([proposal.biz](https://www.proposal.biz/blog/gemini-prompt-for-proposal-writing/)), nhưng không có workflow RFP chuyên dụng.

### 2.11 ChatGPT và custom GPTs cho proposals
ChatGPT có thể kết nối SharePoint/Google Drive, dùng Projects; tuy nhiên OpenAI tuyên bố rõ file library của ChatGPT "does not introduce external sharing or multiplayer collaboration" ([OpenAI help, dẫn qua 1up](https://1up.ai/blog/chatgpt-rfp-limitations)). Nghiên cứu "Lost in the Middle" (Liu et al., TACL) cho thấy độ chính xác của model giảm hơn 30% khi câu trả lời nằm giữa một ngữ cảnh dài — ảnh hưởng trực tiếp tới việc dán cả RFP 2.000 dòng vào chat ([arXiv 2307.03172](https://arxiv.org/abs/2307.03172), [1up](https://1up.ai/blog/chatgpt-rfp-limitations)). Bài học thực tế từ một người tự xây tool RFP bằng ChatGPT: "ChatGPT-style solutions can generate an answer, fast. What they can't do is ensure that the answer is current, approved, accurate, and something your team is willing to stand behind" — kèm ba bài học: mọi câu trả lời vẫn cần chuyên gia rà soát; AI chỉ tốt bằng kiến thức nền (content decay); hệ thống là điểm lỗi đơn lẻ, không có version control, audit trail hay governance ([Andrew Morari, LinkedIn](https://www.linkedin.com/pulse/i-built-in-house-rfp-tool-chatgpt-heres-what-learned-andrew-morari-qqbzc) — lưu ý tác giả nay làm tại Loopio nên có thiên kiến).

## 3. Điểm mạnh chung của nhóm công cụ chuyên dụng

- **Content library / answer bank:** Loopio, Responsive, Qvidian đều xoay quanh thư viện câu trả lời đã phê duyệt, tái sử dụng qua các bid ([Inventive](https://www.inventive.ai/blog-posts/loopio-pricing), [Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).
- **Collaboration và workflow:** gán câu hỏi cho SME, deadline, review nhiều bước, phê duyệt — ví dụ Loopio multi-step reviews, Responsive intake/reporting/permissions, Qvidian review routing ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie), [AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)).
- **AI hỗ trợ soạn thảo có nguồn:** các nền tảng hiện đại đều thêm citations + confidence scores (Loopio Response Intelligence, Responsive TRACE Score, Arphie confidence signals) ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).
- **Kết quả đo được:** công cụ RFP giúp giảm thời gian phản hồi 50–80% và tăng win rate theo tuyên bố vendor ([SparrowGenie](https://sparrowgenie.com/blog/rfp-software-tools)); "shredding" thủ công mất 4–8 giờ thì AI làm trong vài phút ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)).

## 4. Điểm yếu đã được ghi nhận (có nguồn)

### 4.1 Hallucination / câu trả lời sai
ChatGPT "will answer every question with the same confident tone, whether it knows the answer or not... When it does not know, it makes something up that reads perfectly" — có thể chèn chi tiết SOC 2 cũ hai năm hoặc một tích hợp bạn không có ([1up](https://1up.ai/blog/chatgpt-rfp-limitations)). AutogenAI (nền tảng viết đề xuất dài) bị chấm là "more prone to hallucination" so với cách tiếp cận có nguồn trích dẫn ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)). RAG có grounding làm giảm tỷ lệ hallucination hơn 40% so với LLM đa dụng ([CMARIX, dẫn qua Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)); chi phí hallucination AI ước tính 67,4 tỷ USD/năm ([FourDots, dẫn qua Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)). Hệ quả thực tế: "every single response has to be edited because of hallucinations" ([1up](https://1up.ai/blog/chatgpt-rfp-limitations)).

### 4.2 Thiếu grounding vào dữ liệu định giá/chi phí chuẩn của công ty
Không công cụ nào trong danh sách khảo sát có module ước lượng chi phí/nỗ lực (person-days, cost build-up, margin) — tìm kiếm "RFP proposal software cost estimation module" không trả về bất kỳ sản phẩm nào nối RFP với ước lượng chi phí (gap được xác nhận bằng chính sự vắng mặt của kết quả). Các công cụ tập trung vào *văn bản*: compliance matrix ánh xạ yêu cầu sang trạng thái tuân thủ chứ không sang chi phí ([AutoRFP compliance matrix](https://autorfp.ai/blog/compliance-matrix)); go/no-go dùng dữ liệu win-rate lịch sử chứ không phải mô hình giá ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)). Định giá bị bỏ lại cho con người và hệ thống khác (ERP/estimating).

### 4.3 Template rigidity / vấn đề định dạng
Người dùng Loopio gặp khó với import RFP phức tạp và "often cannot export back in the original buyer format" ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)); AutogenAI gặp khó import Excel/Word/PDF buộc copy-paste thủ công (review viên Dave E.: "I find the lack of integration with Word and PDF formats an inconvenience") ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)); Copilot "was not built to read that layout, place the right answer in the right cell, tick the correct box" — người dùng phải rà từng ô ([1up](https://1up.ai/blog/microsoft-copilot-rfp-limitations)); trình soạn thảo Responsive không làm nổi bảng ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)).

### 4.4 Bảo mật / quyền riêng tư (đưa RFP bảo mật vào LLM)
Đưa dữ liệu đề xuất chính phủ (Controlled Unclassified Information — CUI, giá chi tiết, thỏa thuận teaming) vào model công khai như ChatGPT "may be unlawful": vi phạm NIST SP 800-171 và DFARS 252.204-7012, có thể cấu thành cơ sở cho kiện False Claims Act, và trong trường hợp cực đoan là Espionage Act (18 U.S.C. §§ 793–794) ([Turingon/GovSignals, LinkedIn](https://www.linkedin.com/pulse/youre-uploading-proposal-data-chatgpt-you-may-breaking-law-mibef)). Gemini Apps bản tiêu dùng lưu hoạt động tới 18 tháng mặc định ([Google](https://support.google.com/gemini/answer/13594961?hl=en)). Đây là lý do các vendor RFP bán "zero-data-retention agreements with model providers" như một điểm bán hàng ([Arphie](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)) và khuyến nghị công cụ phải FedRAMP High/GovCloud cho GovCon ([Turingon](https://www.linkedin.com/pulse/youre-uploading-proposal-data-chatgpt-you-may-breaking-law-mibef)).

### 4.5 Chất lượng đa ngôn ngữ kém (đặc biệt tiếng Nhật)
Ở cấp độ model: LLM thiên vị dữ liệu tiếng Anh; script logographic (tiếng Nhật/Trung) bị token hóa kém hiệu quả hơn, độ chính xác và độ trôi chảy giảm rõ khi ra khỏi tiếng Anh, tỷ lệ bịa đặt cao hơn ([Black Seed USA](https://blackseedusa.com/multilingual-prompting-how-to-fix-non-english-llm-outputs)). Ở cấp độ sản phẩm: khả năng đa ngôn ngữ của Loopio chỉ nằm ở nấc Enhanced (không phải Foundations) ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)); AutoRFP quảng cáo "auto-translates output across more than 30 languages" như một điểm khác biệt — ngụ ý các đối thủ không làm tốt ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)). Thị trường Nhật có hệ sinh thái công cụ nội địa riêng (Mazrica Target, Gamma, v.v.) thay vì dùng các nền tảng phương Tây ([Mazrica](https://mazrica.com/product/businesslab/dx/ai-proposal-automation-tools/)) — bằng chứng gián tiếp rằng các công cụ Âu-Mỹ không chiếm ưu thế cho đề xuất tiếng Nhật.

### 4.6 Không đảm bảo truy vết yêu cầu (bỏ sót yêu cầu)
Việc "shredding" RFP 200 trang thành yêu cầu rời rạc là nơi AI hay bỏ sót; các công cụ QA/compliance mọc lên để vá lỗ hổng này — ví dụ RFPCheck quảng cáo "detect pricing inconsistencies, missing mandatory requirements, formatting problems" ([RFPCheck](https://www.rfpai.io/?lang=en)), compliance matrix "helps reduce missed requirements... disqualification risk" ([AutoRFP](https://autorfp.ai/blog/compliance-matrix)), RFP360 "detect compliance gaps... missing requirements" ([RFP360](https://www.rfp360.ai/response-evaluation/)). Sự tồn tại của cả một lớp công cụ QA riêng cho thấy các công cụ soạn thảo không tự đảm bảo bao phủ 100% yêu cầu — Glean cũng khuyến nghị chạy QA check trước khi nộp "catches errors that the drafting AI introduced" ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)).

### 4.7 Không có governance phê duyệt con người sẵn có
Tool RFP tự xây bằng ChatGPT không có "version control, no audit trail, and no governance over what was going in or coming out" ([Morari, LinkedIn](https://www.linkedin.com/pulse/i-built-in-house-rfp-tool-chatgpt-heres-what-learned-andrew-morari-qqbzc)). Arphie bán "human approval from day one" như điểm khác biệt — ngụ ý các đối thủ không có sẵn ([Arphie](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)). Glean khuyên doanh nghiệp "Governance guardrails... should be established before you extend AI drafting" — tức là công cụ không tự áp đặt ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)). Ngay cả ChatGPT cũng không có multiplayer collaboration trong file library ([OpenAI, dẫn qua 1up](https://1up.ai/blog/chatgpt-rfp-limitations)).

## 5. Review / bình luận analyst

- **G2 Loopio:** 4,7 sao, 610+ review; phàn nàn lặp lại: Magic AI yếu với câu hỏi tinh tế, thư viện phải bảo trì tay, lỗi import/export ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)); một G2 reviewer: "My only real challenge with Loopio is the seat-based pricing. This makes me think twice about expanding to internal teams" ([Inventive](https://www.inventive.ai/blog-posts/loopio-pricing)).
- **G2 Responsive:** khen import Excel ("game-changer"), chê trình soạn thảo ("Tables are flat out impossible") ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)).
- **G2 Qvidian:** AI "needs heavy editing", UI cũ ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)).
- **Reddit r/salesengineers:** practitioner thread nêu content-library upkeep, gợi ý trả lời không liên quan, yêu cầu định dạng gốc, phải kiểm tra lại output AI chung ([dẫn qua Arphie](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).
- **Phân tích vendor đối thủ (thiên kiến cần lưu ý):** Inventive AI gọi chi phí duy trì thư viện Loopio là "library tax" 30–100% ([Inventive](https://www.inventive.ai/blog-posts/loopio-pricing)); 1up liệt kê chi tiết giới hạn của Copilot và ChatGPT ([1up](https://1up.ai/blog/microsoft-copilot-rfp-limitations), [1up](https://1up.ai/blog/chatgpt-rfp-limitations)).
- **Gartner (bối cảnh):** dự báo hơn 40% dự án agentic AI sẽ bị hủy trước cuối 2027 ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)) — cảnh báo chung về độ chín của AI agent trong doanh nghiệp.

## 6. Gap analysis: điều mà sản phẩm bidding-estimation cần mà các công cụ này không làm

1. **Không công cụ nào nối yêu cầu RFP với ước lượng nỗ lực/chi phí.** Toàn bộ thị trường xoay quanh văn bản trả lời; compliance matrix ánh xạ yêu cầu → trạng thái tuân thủ, không phải yêu cầu → chi phí ([AutoRFP](https://autorfp.ai/blog/compliance-matrix)). Một sản phẩm bidding-estimation cần bản đồ yêu cầu → cost driver → person-days → giá chào.
2. **Không có mô hình giá/margin (price-to-win).** Go/no-go dùng win-rate lịch sử ([Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)) chứ không mô hình hóa xác suất thắng theo giá.
3. **Không tích hợp với dữ liệu định giá chuẩn của công ty** (rate cards, chi phí nhân công, catalog giá) — chính là khoảng trống grounding mà mục 4.2 nêu.
4. **Không có truy vết yêu cầu → chi phí để phát hiện "yêu cầu chưa được định giá"** — lớp công cụ QA hiện chỉ soi lỗi văn bản ([RFPCheck](https://www.rfpai.io/?lang=en)).
5. **Governance phê duyệt giá** không tồn tại trong bất kỳ công cụ nào khảo sát (mục 4.7).
6. **Đa ngôn ngữ (Nhật, CJK) vẫn là điểm yếu cấu trúc** của LLM nền ([Black Seed](https://blackseedusa.com/multilingual-prompting-how-to-fix-non-english-llm-outputs)) — sản phẩm mới cần pipeline dịch/glossary riêng.
7. **Kết luận:** một sản phẩm bidding-estimation cần kết hợp: (a) parsing yêu cầu + truy vết cam kết, (b) grounding vào dữ liệu chi phí/giá nội bộ, (c) mô hình ước lượng và margin, (d) governance phê duyệt con người, (e) chất lượng đa ngôn ngữ — năm điều mà không công cụ nào trong danh sách khảo sát làm trọn vẹn.

---

## Key claims

1. **Hallucination là điểm yếu được ghi nhận rộng rãi nhất:** ChatGPT và các LLM đa dụng "điền chỗ trống bằng phỏng đoán tự tin", mọi bản nháp đều phải sửa tay; RAG có grounding giảm hallucination >40% ([1up](https://1up.ai/blog/chatgpt-rfp-limitations), [Glean](https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026)).
2. **Không công cụ nào grounding vào dữ liệu định giá/chi phí chuẩn hay mô hình ước lượng nỗ lực** — toàn thị trường tập trung văn bản, compliance matrix chỉ ánh xạ yêu cầu→tuân thủ ([AutoRFP](https://autorfp.ai/blog/compliance-matrix)); đây là khoảng trống lớn nhất cho sản phẩm bidding-estimation.
3. **Chi phí ẩn lớn nhất của nhóm "library-led" (Loopio/Responsive/Qvidian) là bảo trì thư viện nội dung bằng tay** — "library tax" 30–100% TCO, thư viện cũ = AI trả lời sai nhanh hơn ([Inventive](https://www.inventive.ai/blog-posts/loopio-pricing), [AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc)).
4. **Bảo mật là rào cản pháp lý thực sự:** đưa CUI/giá chi tiết của đề xuất chính phủ vào LLM công khai có thể vi phạm NIST SP 800-171/DFARS và tạo cơ sở kiện False Claims Act ([Turingon, LinkedIn](https://www.linkedin.com/pulse/youre-uploading-proposal-data-chatgpt-you-may-breaking-law-mibef)).
5. **Không công cụ nào đảm bảo truy vết yêu cầu 100%** — tồn tại cả một lớp công cụ QA/compliance riêng (RFPCheck, RFP360) để vá "missing requirements" ([RFPCheck](https://www.rfpai.io/?lang=en), [RFP360](https://www.rfp360.ai/response-evaluation/)).
6. **Governance phê duyệt con người không có sẵn** ở công cụ đa dụng (ChatGPT: không audit trail, không multiplayer) và chỉ mới là điểm bán của Arphie ([Morari, LinkedIn](https://www.linkedin.com/pulse/i-built-in-house-rfp-tool-chatgpt-heres-what-learned-andrew-morari-qqbzc), [Arphie](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).
7. **Chất lượng đa ngôn ngữ (đặc biệt CJK/tiếng Nhật) yếu ở cấp model** do thiên vị dữ liệu tiếng Anh và token hóa script logographic ([Black Seed](https://blackseedusa.com/multilingual-prompting-how-to-fix-non-english-llm-outputs)); đa ngôn ngữ của Loopio chỉ ở nấc Enhanced ([Arphie blog](https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie)).
8. **Giá cả không minh bạch:** Loopio trung vị ~23.915 USD/năm (Vendr), Responsive ước tính 6.500–28.000 USD/năm, Qvidian/Arphie đều báo giá qua sales ([Inventive](https://www.inventive.ai/blog-posts/loopio-pricing), [AutoRFP](https://autorfp.ai/blog/responsive-rfpio-pricing)).
9. **Template rigidity phổ biến:** lỗi import/export định dạng gốc (Loopio, AutogenAI), không điền được bảng hỏi có cấu trúc (Copilot), trình soạn thảo không làm nổi bảng (Responsive) ([AutoRFP trên LinkedIn](https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc), [1up](https://1up.ai/blog/microsoft-copilot-rfp-limitations)).
10. **Tiền đề "Draftable là công cụ AI viết proposal" và "HyperWrite RFP Assistant" không được xác nhận:** Draftable là công cụ so sánh tài liệu; không tìm thấy tài liệu/review nào về RFP Assistant của HyperWrite ([Draftable](https://www.draftable.com/), [HyperWrite FAQ](https://www.hyperwriteai.com/faq/how-much-does-hyperwrite-cost)).

---

## Danh sách nguồn (URL + ngày truy cập 2026-10-09)

1. https://www.arphie.ai/blog/comparing-rfp-proposal-software-loopio-responsive-and-arphie
2. https://www.arphie.ai/
3. https://www.g2.com/products/arphie/reviews
4. https://autorfp.ai/blog/arphie-pricing
5. https://www.inventive.ai/blog-posts/arphie-pricing-features-reviews
6. https://coldiq.com/tools/arphie
7. https://www.hyperwriteai.com/faq/how-much-does-hyperwrite-cost
8. https://costbench.com/software/ai-writing-tools/hyperwrite/
9. https://toolradar.com/tools/hyperwrite/pricing
10. https://www.linkedin.com/pulse/i-built-in-house-rfp-tool-chatgpt-heres-what-learned-andrew-morari-qqbzc
11. https://stargazy.io/resources/the-rfp-is-a-growth-engine-how-to-use-ai-where-it-actually-matters
12. https://www.planmysaas.com/ideas/ai-saas-ideas/ai-rfp-response-generator
13. https://loopio.com/
14. https://www.responsive.io/glossary/compare/loopio-vs-qvidian
15. https://loopio.com/blog/qvidian-vs-loopio/
16. https://www.inventive.ai/blog-posts/qvidian-vs-loopio-vs-responsive
17. https://sparrowgenie.com/blog/rfp-software-tools
18. https://loopio.com/blog/8-responsive-alternatives/
19. https://www.inventive.ai/blog-posts/loopio-pricing
20. https://autorfp.ai/blog/loopio-pricing
21. https://autorfp.ai/blog/responsive-rfpio-pricing
22. https://thalamushq.ai/blogs/responsive-review
23. https://thalamushq.ai/blogs/qvidian-pricing
24. https://rocketdocs.com/resources/blog/responsive-pricing
25. https://www.g2.com/products/responsive-formerly-rfpio/pricing
26. https://www.capterra.com/p/148054/Responsive/reviews/
27. https://www.g2.com/products/upland-qvidian/reviews
28. https://www.capterra.com/p/6944/Qvidian-Proposal-Automation/
29. https://uplandsoftware.com/qvidian/
30. https://www.revuo.ai/category/tender-management/qvidian
31. https://www.pandadoc.com/pricing/
32. https://www.microgaps.com/gaps/2026-02-14-ai-proposal-generator
33. https://www.jotform.com/ai/best-ai-document-generator/
34. https://aiagentsquare.com/blog/ai-document-automation
35. https://www.taskade.com/blog/ai-proposal-generators
36. https://www.draftable.com/
37. https://www.draftable.com/pricing
38. https://n8n.io/integrations/better-proposals/and/draftable/
39. https://writer.com/
40. https://writer.com/guides/graph-based-rag-starter-guide/
41. https://adoption.microsoft.com/en-us/scenario-library/sales/respond-to-an-rfp/
42. https://1up.ai/blog/microsoft-copilot-rfp-limitations
43. https://1up.ai/blog/chatgpt-rfp-limitations
44. https://learn.microsoft.com/en-us/answers/questions/6016267/word-limitations-on-copilot
45. https://support.google.com/gemini/answer/13594961?hl=en
46. https://knowledge.workspace.google.com/admin/generative-ai/generative-ai-in-google-workspace-privacy-hub
47. https://www.proposal.biz/blog/gemini-prompt-for-proposal-writing/
48. https://arxiv.org/abs/2307.03172
49. https://www.linkedin.com/pulse/youre-uploading-proposal-data-chatgpt-you-may-breaking-law-mibef
50. https://www.linkedin.com/pulse/5-best-loopio-alternatives-2026-honest-side-by-side-autorfp-bh6cc
51. https://1up.ai/loopio-vs-responsive/
52. https://www.glean.com/perspectives/top-7-ai-tools-for-streamlining-rfp-responses-in-2026
53. https://autorfp.ai/blog/compliance-matrix
54. https://www.rfpai.io/?lang=en
55. https://www.rfp360.ai/response-evaluation/
56. https://blackseedusa.com/multilingual-prompting-how-to-fix-non-english-llm-outputs
57. https://mazrica.com/product/businesslab/dx/ai-proposal-automation-tools/
58. https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027
59. https://www.vendr.com/marketplace/loopio