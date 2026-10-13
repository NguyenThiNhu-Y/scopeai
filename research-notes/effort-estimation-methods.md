# Ước lượng nỗ lực phần mềm và xây dựng WBS trong bối cảnh offshore Việt Nam – Nhật Bản

*Memo nghiên cứu — Researcher subagent. Mọi luận điểm đều kèm nguồn inline.*

---

## 1. Các phương pháp ước lượng phổ biến

### 1.1. Expert judgment (đánh giá chuyên gia)

Expert judgment là việc dựa vào kinh nghiệm của người có chuyên môn để ước lượng trực tiếp, không qua mô hình. Đây là phương pháp được dùng phổ biến nhất trong thực tế. Tài liệu tổng hợp nghiên cứu cho thấy expert judgment và mô hình thuật toán (algorithmic model) đạt độ chính xác **tương đương nhau** trong nhiều nghiên cứu, và khuyến nghị kết hợp cả hai để tăng độ chính xác ([ResearchGate – Actual effort and estimation accuracy](https://www.researchgate.net/figure/Actual-effort-and-estimation-accuracy_tbl3_4038460)). Điểm yếu chính là tính chủ quan và phụ thuộc cá nhân: cùng một dự án, người ước lượng khác nhau cho con số rất khác nhau, đặc biệt ở những đội chưa chuẩn hóa quy trình ước lượng ([Zenn/PasBase – 工数見積もりを勘で決めないための5手法](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Jørgensen (2007) là tác giả tham chiếu chính về so sánh expert-judgment vs parametric trong ước lượng phần mềm ([SlideServe – Reducing Estimation Uncertainty](https://www.slideserve.com/aulani/reducing-estimation-uncertainty-with-continuous-assessment-tracking-the-cone-of-uncertainty)).

### 1.2. Analogous estimation (ước lượng tương tự)

Analogous estimation dùng dữ liệu lịch sử của dự án tương tự đã hoàn thành để suy ra quy mô/nỗ lực của dự án mới, điều chỉnh theo khác biệt. Ưu điểm: ra số nhanh, phù hợp giai đoạn chào hàng/ước lượng sơ bộ; nhược điểm: độ chính xác phụ thuộc kinh nghiệm người ước lượng và chất lượng kho dữ liệu dự án cũ ([Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Ví dụ thực tế từ Nhật: có dự án "hệ thống đặt chỗ" 2 người × 3 tháng làm trước đây, dự án mới giống nhưng bỏ module thanh toán → ước lượng ngay "2 người × 2–2,5 tháng" ([Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Phương pháp này cũng là nền tảng của "reference class forecasting" được Flyvbjerg khuyến nghị để tránh lạc quan thái quá ([BudgetOverrun – Cone of Uncertainty](https://budgetoverrun.com/cone-of-uncertainty)).

### 1.3. Parametric estimation — COCOMO

COCOMO (Constructive Cost Model) là mô hình tham số dự đoán nỗ lực theo kích thước mã nguồn (KLOC) kết hợp các cost driver, có các biến thể Basic/Intermediate/Detailed và COCOMO II (do USC Center for Software Engineering phát triển, tài liệu chuẩn là *Software Cost Estimation with COCOMO II* của Boehm et al.) ([BOEHM CSSE – COCOMO II](https://boehmcsse.org/tools/cocomo-ii/), [msdbok – COCOMO II](https://msdbok.github.io/content/scope/estimates/cocomo.html)). Điểm mạnh: đơn giản, cho dự đoán tốt ở giai đoạn sớm; điểm yếu: độ chính xác phụ thuộc nhiều vào dữ liệu lịch sử và kém hiệu quả với dự án hiện đại/phức tạp (microservices, cloud, agile) ([GeeksforGeeks – Advantages and Disadvantages of COCOMO](https://www.geeksforgeeks.org/software-engineering/advantages-disadvantages-of-cocomo-model/), [DataCamp – COCOMO Model](https://www.datacamp.com/tutorial/cocomo-model)). Trong thực tế Nhật Bản, COCOMO được xếp vào nhóm "mô hình hệ số" dùng khi có kho dữ liệu năng suất nội bộ, còn FP và 類推見積 (analogous) là hai phương pháp phổ biến hơn trong đấu thầu ([LASSIC – 工数見積り技法を外注で精度向上](https://lassic.co.jp/media/column/effort-estimation-outsourcing/)).

### 1.4. Function Points (FP)

Function Point Analysis (FPA) đo kích thước chức năng của phần mềm dựa trên yêu cầu người dùng (chuẩn IFPUG: 5 loại chức năng — external input, external output, external inquiry, internal logical file, external interface file), độc lập với ngôn ngữ lập trình, nên đo được sớm trong vòng đời và giảm độ lệch giữa các lần đếm ([IFPUG MetricViews June 2023](https://ifpug.org/wp-content/uploads/2023/06/IFPUG_MetricViews_June_2023.pdf), [Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Lưu ý quan trọng: FP là thước đo kích thước, **không phải** mô hình ước lượng — muốn ra nỗ lực phải nhân với năng suất lịch sử (ví dụ 1 FP ≈ 0,5 người-ngày theo dữ liệu nội bộ) ([QualityPlusTech – Function Points are NOT an Estimating Model](https://qualityplustech.com/function-points-are-not-an-estimating-model/), [Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Điểm mạnh: chuẩn chung để so sánh giữa các vendor, dùng tốt cho dự án lớn; điểm yếu: chi phí học tập cao, cần người được đào tạo, và các phiên bản "rút gọn" (High-level FPA) có xu hướng **đánh giá thấp** kích thước phần mềm ([Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed), [ScienceDirect – Early and quick function points analysis](https://www.sciencedirect.com/science/article/pii/S0164121220302788)).

### 1.5. Story points (ước lượng tương đối trong Agile)

Story points là đơn vị tương đối đo nỗ lực/độ phức tạp/rủi ro của backlog item, không phải giờ; dùng kèm velocity để dự báo. Ưu điểm: khuyến khích hợp tác nhóm, giảm thiên kiến cảm xúc, cập nhật liên tục khi spec thay đổi; nhược điểm: chuẩn điểm khác nhau giữa các đội nên **không dùng để so sánh năng suất giữa đội**, và dùng trực tiếp làm dự báo lịch trình thì thiếu chính xác ([Atlassian – What are story points](https://www.atlassian.com/agile/project-management/estimation), [Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Có cả phê bình gay gắt rằng story points/velocity không dự đoán được những gì hoàn thành trong sprint cố định thời gian ([BlackLight Agile – Story Points and Velocity are Pseudoscience](https://blacklightagile.com/2026/07/17/story-points-and-velocity-are-pseudoscience/)).

### 1.6. Three-point estimation / PERT

Three-point estimation dùng ba giá trị — optimistic (O), most likely (M), pessimistic (P) — và công thức PERT chuẩn hóa: **(O + 4M + P) / 6** (beta distribution), kèm độ lệch chuẩn (P − O)/6 để tính xác suất hoàn thành ([ProjectManagementAcademy – A Three-Point Estimating Technique: PERT](https://projectmanagementacademy.net/resources/blog/a-three-point-estimating-technique-pert/), [PM Study Circle – Three-Point Estimation](https://pmstudycircle.com/three-point-estimation/)). Ưu điểm: giảm thiên kiến, gắn với quản trị rủi ro, cải thiện truyền thông; nhược điểm: tốn thời gian thu thập 3 giá trị cho từng task, vẫn phụ thuộc expert judgment, hiệu quả phụ thuộc chất lượng dữ liệu lịch sử ([PM Study Circle](https://pmstudycircle.com/three-point-estimation/)). Có biến thể triangular distribution (O+M+P)/3 ([Nulab – How 3-point estimating can improve project planning](https://nulab.com/learn/project-management/3-point-estimating/)).

### 1.7. T-shirt sizing

T-shirt sizing dùng cỡ áo (XS, S, M, L, XL, XXL) để ước lượng tương đối nhanh, không gắn giờ cụ thể — phù hợp ước lượng sơ bộ backlog/release, sau đó mới tách thành story points cho sprint planning ([Asana – T Shirt Sizing](https://asana.com/resources/t-shirt-sizing), [PremierAgile – T-Shirt Size Estimation in Agile](https://premieragile.com/t-shirt-size-estimation-in-agile/)). Điểm yếu nổi bật theo Mike Cohn (Mountain Goat Software): **không cộng dồn được** — không thể nói "xong trong 3 M, 4 L và 2 S"; vì vậy chỉ dùng để khởi động ước lượng tương đối, không thay thế story points/giờ ([Mountain Goat Software – Estimating with Tee Shirt Sizes](https://www.mountaingoatsoftware.com/agile/estimating-with-tee-shirt-sizes)).

### 1.8. Planning poker

Planning poker là kỹ thuật nhóm: mỗi thành viên giơ thẻ số (thường Fibonacci) riêng, mở đồng loạt, thảo luận outlier rồi chốt consensus — giảm thiên kiến neo và khuyến khích thảo luận ([Atlassian](https://www.atlassian.com/agile/project-management/estimation), [iamagile.io – Planning Poker vs Traditional Estimation](https://iamagile.io/blog/planning-poker-vs-traditional-estimation-methods)). Bằng chứng thực nghiệm: nghiên cứu của Moløkken-Østvold et al. (JSS 2008) cho thấy planning poker cho độ chính xác **tương đương** với tổng hợp ý kiến chuyên gia cá nhân, và chính xác hơn ước lượng nhóm không cấu trúc đối với task quen thuộc nhưng kém hơn với task lạ ([ACM DL – Using planning poker for combining expert estimates](https://dl.acm.org/doi/abs/10.1016/j.jss.2008.03.058), [PDF nghiên cứu](http://se16.unbox.org/resources/08planningPoker.pdf)). Nghiên cứu gần đây (Poženel et al., IJSEKE 2023/arXiv 2024) so sánh planning poker, bucket system và affinity estimation: độ chính xác **không khác biệt có ý nghĩa thống kê**, nhưng bucket system và affinity estimation nhanh hơn khoảng **một nửa thời gian** so với planning poker ([arXiv:2401.16152](https://arxiv.org/abs/2401.16152)).

### 1.9. Cách phối hợp theo giai đoạn (thực hành Nhật Bản)

Thực tế không dùng một phương pháp đơn lẻ mà phối hợp theo pha: **chào hàng/đề xuất ban đầu → analogous** (ưu tiên tốc độ); **đang làm rõ yêu cầu → analogous + parametric** (đưa khoảng ước lượng); **yêu cầu đã chốt → bottom-up (積み上げ)** từ WBS (ưu tiên độ giải trình); **dự án lớn/so sánh nhiều vendor → FP**; **agile → story points** ([Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Nguyên tắc xuyên suốt: ước lượng là "dự đoán kèm giả định" chứ không phải "giá trị cố định" — nên trình bày dạng khoảng ("với yêu cầu hiện tại: 50–70 người-ngày") và ghi rõ phạm vi, giả định, mục chưa xác định, hạn hiệu lực của báo giá ([Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)).

---

## 2. Văn hóa ước lượng man-day (人日) trong offshore Nhật – Việt

### 2.1. Cấu trúc báo giá chuẩn

Công thức nền tảng của mọi báo giá offshore Nhật Bản: **Giá trị dự toán = Đơn giá × Khối lượng công việc + Chi phí khác** (開発見積もり金額 ＝ 単価 × 工数 ＋ 諸費用) ([Vitalify Asia – オフショア開発の見積もり・算出方法を徹底解説](https://vfa-lab.jp/media/offshore-development-estimate-guide/)). Có hai loại đơn giá:
- **人月単価 (man-month rate)**: giá của 1 người làm trọn 1 tháng; phổ biến trong hợp đồng lab-type (準委任型). Mặc định **1 tháng = 20 ngày làm việc**; man-month rate là con số cố định, không đổi theo số ngày làm việc thực tế của từng tháng ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)).
- **人日単価 (man-day rate)**: giá theo ngày (giả định **8 giờ/ngày**); phổ biến trong hợp đồng 請負 (fixed-price). Man-day rate thường **cao hơn** man-month ÷ 20 vì nhà thầu gánh trách nhiệm hoàn thành (完成責任) và trách nhiệm sửa lỗi sau bàn giao (契約不適合責任) ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)).

Quy đổi man-month ra giờ có hai quy ước phổ biến trong công ty phần mềm Việt Nam: **160 giờ (20 ngày × 8h)** hoặc **176 giờ (22 ngày × 8h)**; quy ước nào cũng được, miễn là dùng nhất quán ở cả 3 khâu: ước lượng, chấm công, đối chiếu sau dự án ([CostDesk – Cách tính giá dự án phần mềm từ man month tới cost rate](https://blog.costdesk.co/tinh-gia-du-an-phan-mem/)).

### 2.2. Đơn giá theo vai trò (role-based rate)

Đơn giá được phân theo vai trò: Programmer, Senior Engineer, Bridge SE (BrSE), PM. Theo **オフショア開発白書2025年版** (Offshore Development White Paper 2025, của offshore-kaihatsu.com), giá trung bình tại Việt Nam: **Programmer 40,1万円, Senior Engineer 50万円, Bridge SE 59万円, PM 74万円/tháng**; so sánh Bangladesh: Programmer 33,8万円, Senior 52,5万円, Bridge SE 82,5万円 (hiếm kỹ sư tiếng Nhật nên đắt hơn Việt Nam), PM 72,5万円 ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)). Một nguồn khác (dựa trên 白書 bản cũ hơn) đưa ra: PM 65万円, BrSE 50万円, SE 45万円, PG 40万円, trung bình Việt Nam ~32万円/tháng — khác nhau do khác năm xuất bản của 白書 ([Wakka Inc. – オフショア開発の人月単価の目安](https://wakka-inc.com/blog/1859/)). Lưu ý đối chiếu: cùng một con số "giá Việt Nam" có thể chênh gấp đôi giữa các bài viết chỉ vì trích từ các năm khác nhau của 白書 ([ISSOH – オフショア開発の費用相場](https://www.issoh.co.jp/column/details/16271/)).

### 2.3. Hai kiểu hợp đồng và nơi chứa rủi ro

- **ラボ型 (lab-type / 準委任型)**: trả theo khối lượng vận hành hằng tháng (người × thời gian), không có trách nhiệm hoàn thành, đổi yêu cầu linh hoạt trong kỳ — hợp agile/dài hạn; rủi ro sai số ước lượng thuộc về khách hàng ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)).
- **請負型 (fixed-price)**: trả theo sản phẩm hoàn thành, nhà thầu chịu trách nhiệm hoàn thành; vì **không được phép đòi thêm tiền khi vượt** nên 工数 (khối lượng công việc) **đã bao gồm buffer rủi ro**; yêu cầu càng mơ hồ thì buffer càng dày và giá càng cao; đổi spec giữa chừng phải tái đàm phán ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)). Đúng với góc nhìn Việt Nam: với fixed-price, rủi ro sai số ước lượng thuộc về công ty phần mềm nên dự phòng phải dày hơn và là một dòng riêng, tách khỏi biên lợi nhuận ([CostDesk](https://blog.costdesk.co/tinh-gia-du-an-phan-mem/)).

### 2.4. Thực hành báo giá của công ty phần mềm Việt Nam

Bài phân tích chuyên sâu của CostDesk (tác giả Việt, 2026) mô tả quy trình báo giá điển hình: "đội kỹ thuật ước lượng 10 man-month, sales nhân với đơn giá quen dùng, cộng 20% dự phòng, gửi khách" — và chỉ ra lỗi hệ thống: đơn giá thường xuất phát từ **lương tháng × hệ số truyền miệng (2x, 2,5x)** hoặc **giá đối thủ trừ đi một chút**, thay vì từ cost rate thật; hệ quả là dự án "đúng ước lượng" vẫn lỗ. Giải pháp đề xuất: tính tổng chi phí sở hữu nhân sự/năm → cost rate trên giờ khả dụng (available hours) và giờ bán được (billable hours, trừ ghế trống ~15% và giờ nội bộ ~10%) → giá sàn = cost rate × (1 + tỷ lệ gián tiếp) ÷ (1 − biên mục tiêu); ví dụ senior lương 45 triệu/tháng → giá sàn 716.363 đồng/giờ với biên 25% ([CostDesk](https://blog.costdesk.co/tinh-gia-du-an-phan-mem/)). Bài viết cũng nhấn mạnh vòng đối chiếu sau dự án (so giờ thực với man-month đã báo theo từng hạng mục) là cách duy nhất để sửa hệ số ước lượng cho các lần sau ([CostDesk](https://blog.costdesk.co/tinh-gia-du-an-phan-mem/)).

### 2.5. Mức giá thị trường và chi phí ẩn

- Giá offshore ≈ **40–70% giá nội địa Nhật** ([Lucris – オフショア開発の費用相場と失敗回避](https://lucris.jp/2026/06/22/1748/)); năm 2026: offshore 30–60万円/tháng/engineer so với nội địa 80–120万円, khoảng cách đang thu hẹp dần ([ZenWeb Japan – オフショア開発の費用相場2026](https://zenweb.jp/blog/offshore-development-cost/)).
- Chi phí hay bị bỏ sót khi so sánh báo giá: chi phí học ban đầu (初期学習), thuế VAT (Việt Nam: hợp đồng phát triển phần mềm được hưởng thuế suất 0%), thuế khấu trừ tại nguồn (ví dụ Ấn Độ 20,42%, giảm còn 10% nếu có tờ khai hiệp định thuế), biến động tỷ giá (JPY từ ~110/USD xuống ~160/USD nên xu hướng chuyển sang hợp đồng ngoại tệ), tăng ca theo Luật Lao động Việt Nam (ngày thường 150%, Chủ nhật 200%, ngày lễ 300%, đêm ngày lễ 390%; đêm = 22:00–06:00 giờ Việt Nam), phí dịch vụ trung gian ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)).
- Kinh nghiệm thị trường: người có năng lực kém có thể tốn **1,5–2 lần công** cho cùng một việc, nên chọn vendor theo tổng chi phí chứ không theo đơn giá giờ ([Vitalify Asia](https://vfa-lab.jp/media/offshore-development-estimate-guide/)). BrSE chính là người chịu trách nhiệm "ước lượng effort" và báo cáo tiến độ cho khách Nhật trong quy trình offshore Việt–Nhật ([VTITech – BrSE dùng AI thế nào](https://en.vtitech.vn/brse-dung-ai-the-nao-bo-prompt-thuc-chien-ap-dung-ngay-vao-cong-viec/), [TechWorks – BrSE là gì](https://techworks.vn/blog/nhung-dieu-can-biet-de-tro-thanh-ky-su-cau-noi)).

---

## 3. Tiêu chuẩn xây dựng WBS theo PMBOK

### 3.1. Định nghĩa và mục đích

PMBOK định nghĩa WBS là "phân rã phân cấp hướng deliverable của toàn bộ công việc đội dự án phải thực hiện" — dùng để phân rã phạm vi, cải thiện ước lượng, kiểm soát thực thi và xác minh hoàn thành; công việc không nằm trong WBS thì không thuộc dự án ([workbreakdownstructure.com – PMBOK WBS](https://www.workbreakdownstructure.com/work-breakdown-structure-according-to-pmbok)). WBS hướng deliverable (danh từ, không phải hành động): "đặc tả XYZ" chứ không phải "viết đặc tả XYZ" ([workbreakdownstructure.com](https://www.workbreakdownstructure.com/work-breakdown-structure-according-to-pmbok)).

### 3.2. 100% Rule

Quy tắc 100%: cấp trên cùng của WBS là toàn bộ dự án; **mỗi cấp con phải biểu diễn đúng 100% công việc của cấp cha**, và WBS phải chứa toàn bộ nỗ lực của dự án — đồng thời **không chứa gì ngoài dự án**. Quy tắc này áp dụng ở mọi cấp, đảm bảo không sót việc và không thừa việc ([workbreakdownstructure.com – The 100% Rule](https://www.workbreakdownstructure.com/100-percent-rule-work-breakdown-structure)). Bản tiếng Việt giải thích tương tự: WBS đại diện cho tất cả công việc sản phẩm và dự án, bao gồm cả công việc quản lý dự án ([Atoha – WBS là gì](https://www.atoha.com/blogs/kien-thuc/wbs-la-gi)).

### 3.3. 8-80 Rule (quy mô work package)

Công việc được phân rã đến mức **work package** — mức thấp nhất có thể giao cho đội để ước lượng và kiểm soát. Hướng dẫn phổ biến (được nhắc trong ngữ cảnh PMBOK): work package lá không nhỏ hơn **8 giờ** và không lớn hơn **80 giờ (2 tuần)**; vượt 80 giờ là dấu hiệu phân rã chưa xong ([wbsgantt – How to Create a WBS: 5 Steps from the 100% Rule to 8/80](https://wbsgantt.com/insights/wbs-how-to), [note.com/Manabu Ikarashi – 8/80 Rule](https://note.com/manabu_ikarashi/n/ndaf2266fed84?hl=en), [PMP Guide – WBS Best Practices](https://www.pmp-guide.com/blog/wbs-work-breakdown-structure-best-practices)). Có thể điều chỉnh theo quy mô/độ phức tạp dự án ([BVOP – How to break down project deliverables](https://bvop.org/kb/workpackagebreakdown.html)). Cùng tinh thần: phân rã đến khi work package "có thể ước lượng dễ dàng" ([gratisexam PMP – 100% rule](https://www.gratisexam.com/pmi/pmp/PMI.PracticeTest.PMP.v2013-08-20.by.vasecop.1005q.pdf)).

### 3.4. Các nguyên tắc khác và mức WBS cho dự án phần mềm

Các nguyên tắc bổ sung: **mutual exclusivity** (các thành phần không trùng lặp), phân rã theo deliverable chứ không theo hoạt động/timeline ([Workamajig – WBS for Agencies](https://www.workamajig.com/blog/work-breakdown-structures-wbs)). Với dự án phát triển phần mềm, cấp 1 của WBS thường theo vòng đời: **Analysis → Design → Build → Test → Deploy** (kèm Project Management) ([LinkedIn – Work Breakdown Structure Made Easy](https://www.linkedin.com/pulse/20141016163821-38982905-work-breakdown-structure-made-easy)); mỗi pha lại phân rã theo module/feature xuống work package. Trong thực hành Nhật Bản, 積み上げ見積 (bottom-up) chính là ước lượng từ WBS: tách task rồi gán người-ngày từng task (ví dụ "đăng ký thành viên 5 người-ngày, chức năng đặt chỗ 8 người-ngày, màn hình quản trị 6 người-ngày, thông báo 3 người-ngày, test 4 người-ngày → tổng 26 người-ngày"), và **phải cộng thêm công thiết kế, dựng môi trường, quản lý dự án và buffer rủi ro** — tức là WBS cho dự án phần mềm không chỉ có build mà còn các hạng mục PM/QA/overhead ([Zenn/PasBase](https://zenn.dev/pasbase/articles/86ea6d4bee91ed)). Điều này khớp với khuyến nghị của PMBOK rằng WBS phải bao gồm cả công việc quản lý dự án ([Atoha](https://www.atoha.com/blogs/kien-thuc/wbs-la-gi)).

---

## 4. Cone of uncertainty — độ chính xác ước lượng theo giai đoạn

Barry Boehm công bố dữ liệu gốc năm 1981 trong *Software Engineering Economics* (ban đầu gọi là "Funnel Curve"): ước lượng ở giai đoạn concept ban đầu có thể lệch **~4 lần** theo cả hai hướng, thu hẹp về **~1,25 lần** khi có thiết kế chi tiết ([Construx – The Cone of Uncertainty](https://www.construx.com/books/the-cone-of-uncertainty/), [BudgetOverrun – Cone of Uncertainty](https://budgetoverrun.com/cone-of-uncertainty)). Bảng hệ số nhân gốc (Figure 21-1, Boehm 1981):

| Giai đoạn | Hệ số lạc quan (thấp) | Hệ số bi quan (cao) | Biên độ |
|---|---|---|---|
| Initial concept | 0,25x | 4,0x | 16x |
| Approved product definition | 0,50x | 2,0x | 4x |
| Requirements specification | 0,67x | 1,5x | 2,25x |
| Product design specification | 0,80x | 1,25x | 1,56x |
| Detailed design specification | 0,90x | 1,10x | 1,22x |
| Accepted product (delivery) | 1,0x | 1,0x | 0 (thực tế) |

(Nguồn bảng: [BudgetOverrun – Cone of Uncertainty](https://budgetoverrun.com/cone-of-uncertainty), trích Boehm 1981.)

Điểm mấu chốt thường bị hiểu sai: **cone không tự thu hẹp theo thời gian** — nó thu hẹp vì đội dự án chủ động giảm rủi ro và chốt yêu cầu; trên dự án quản lý kém, cone vẫn rộng như giai đoạn concept cho đến tận lúc bàn giao (lập luận của Laufer 1996 và McConnell 2006, *Software Estimation: Demystifying the Black Art*) ([BudgetOverrun](https://budgetoverrun.com/cone-of-uncertainty)). Cách thu hẹp nhanh: giải quyết các ẩn số rủi ro cao trước, chốt phạm vi kiểu MoSCoW, cấp ngân sách theo từng phase-gate, rolling-wave planning ([BudgetOverrun](https://budgetoverrun.com/cone-of-uncertainty)). Một minh họa thực dụng từ agile: ước lượng ban đầu "1 năm" có thể lệch ±4 lần — tức 3 tháng đến 4 năm ([Samuel Gerges – Agile Metric Estimation](https://gerges.org/agile-metric-estimation/)).

---

## 5. Thống kê ngành về sai số ước lượng / vượt ngân sách

- **Standish CHAOS 1994** (báo cáo gốc): chỉ **16,2%** dự án đúng hạn, đúng ngân sách, đủ phạm vi; 31,1% bị hủy; 52,7% tốn 189% chi phí ước tính ban đầu ([farasat.me – How Do You Scope a Project](https://www.farasat.me/blog/how-to-scope-a-project-so-it-doesnt-eat-you-alive), [Academia – The Standish Group Report](https://www.academia.edu/33504097/THE_STANDISH_GROUP_REPORT)).
- **CHAOS 2015**: 71% dự án phần mềm bị "challenged" (52%) hoặc "failed" (19%); CHAOS 2020 (bản trả phí, được trích dẫn): 31% thành công, 50% challenged, 19% failed ([BudgetOverrun – IT Project Budget Overruns](https://budgetoverrun.com/it-projects)). Quy mô là yếu tố dự báo mạnh nhất: CHAOS 2015 cho thấy 61% dự án nhỏ thành công so với chỉ 6% dự án cỡ "grand" ([BudgetOverrun – Project Success Rate by Size](https://budgetoverrun.com/project-size-success-rate)).
- **McKinsey–Oxford (2012)**: phân tích hơn **5.400 dự án IT lớn** (trên ~15 triệu USD) — trung bình **vượt ngân sách 45%**, vượt thời gian 7%, và chỉ đạt 56% giá trị dự kiến; 17% dự án IT lớn thất bại nghiêm trọng tới mức đe dọa sự tồn tại của công ty ([BudgetOverrun – IT Projects](https://budgetoverrun.com/it-projects), [McKinsey – Unlocking the potential of public-sector IT projects](https://www.mckinsey.com/industries/public-sector/our-insights/unlocking-the-potential-of-public-sector-it-projects)).
- **Flyvbjerg & Budzier (HBR 2011)**: 1.471 dự án IT — vượt trung bình **27%**, cứ 6 dự án thì 1 vượt trên 200% ("black swan") ([BudgetOverrun – Flyvbjerg & Budzier](https://budgetoverrun.com/studies/flyvbjerg-budzier-it-black-swans)). Flyvbjerg & Gardner (2023, *How Big Things Get Done*): 18% dự án IT vượt ngân sách hơn 50%, và nhóm này vượt trung bình **447%**; cơ sở dữ liệu 16.000 dự án của Flyvbjerg cho thấy dự án IT vượt trung bình 73% ([BudgetOverrun – IT Projects](https://budgetoverrun.com/it-projects)).
- Cảnh báo về thống kê lan truyền: con số "53.000 dự án công nghệ, 63% có chi phí ẩn/khuyết tật" **không truy ra được nguồn nghiên cứu công bố** — nó xuất hiện trong các slide AI-generated mà không có nguồn chính; các tập dữ liệu lớn đáng tin là CHAOS (50.000+ dự án), McKinsey–Oxford (5.400), Flyvbjerg (16.000) ([BudgetOverrun – 53,000 tech projects statistic](https://budgetoverrun.com/53000-tech-projects-statistic), [BudgetOverrun – IT Projects FAQ](https://budgetoverrun.com/it-projects)).

---

## Danh sách nguồn chính

1. BudgetOverrun.com – Cone of Uncertainty (Boehm 1981): https://budgetoverrun.com/cone-of-uncertainty (truy cập 2026-10)
2. BudgetOverrun.com – IT Project Budget Overruns: https://budgetoverrun.com/it-projects (2026-10)
3. BudgetOverrun.com – Flyvbjerg & Budzier: https://budgetoverrun.com/studies/flyvbjerg-budzier-it-black-swans
4. Vitalify Asia – オフショア開発の見積もり・算出方法: https://vfa-lab.jp/media/offshore-development-estimate-guide/ (2026-08-17)
5. CostDesk – Cách tính giá dự án phần mềm từ man month tới cost rate: https://blog.costdesk.co/tinh-gia-du-an-phan-mem/ (2026-09-14)
6. Zenn/PasBase – 工数見積もりを勘で決めないための5手法: https://zenn.dev/pasbase/articles/86ea6d4bee91ed (2026-07-24)
7. workbreakdownstructure.com – PMBOK WBS: https://www.workbreakdownstructure.com/work-breakdown-structure-according-to-pmbok
8. workbreakdownstructure.com – The 100% Rule: https://www.workbreakdownstructure.com/100-percent-rule-work-breakdown-structure
9. wbsgantt – 100% Rule to 8/80: https://wbsgantt.com/insights/wbs-how-to (2026-08)
10. Construx – The Cone of Uncertainty: https://www.construx.com/books/the-cone-of-uncertainty/
11. arXiv:2401.16152 – Agile Effort Estimation (Poženel et al.): https://arxiv.org/abs/2401.16152 (2024-01)
12. ACM DL – Moløkken-Østvold et al., planning poker: https://dl.acm.org/doi/abs/10.1016/j.jss.2008.03.058
13. BOEHM CSSE – COCOMO II: https://boehmcsse.org/tools/cocomo-ii/
14. GeeksforGeeks – COCOMO pros/cons: https://www.geeksforgeeks.org/software-engineering/advantages-disadvantages-of-cocomo-model/
15. IFPUG MetricViews 2023: https://ifpug.org/wp-content/uploads/2023/06/IFPUG_MetricViews_June_2023.pdf
16. Wakka Inc. – オフショア開発の人月単価: https://wakka-inc.com/blog/1859/
17. ZenWeb – オフショア開発の費用相場2026: https://zenweb.jp/blog/offshore-development-cost/ (2026-09-01)
18. Lucris – オフショア開発の費用相場: https://lucris.jp/2026/06/22/1748/ (2026-06-22)
19. McKinsey – Unlocking the potential of public-sector IT projects: https://www.mckinsey.com/industries/public-sector/our-insights/unlocking-the-potential-of-public-sector-it-projects
20. PM Study Circle – Three-Point Estimation: https://pmstudycircle.com/three-point-estimation/
21. Mountain Goat Software – T-shirt sizing: https://www.mountaingoatsoftware.com/agile/estimating-with-tee-shirt-sizes
22. Atlassian – Story points: https://www.atlassian.com/agile/project-management/estimation
23. Atoha – WBS là gì: https://www.atoha.com/blogs/kien-thuc/wbs-la-gi

---

## Key claims (xếp theo độ quan trọng)

1. Công thức báo giá chuẩn của offshore Nhật–Việt là "đơn giá × khối lượng công việc + chi phí khác", với hai loại đơn giá: man-month rate (mặc định 1 tháng = 20 ngày làm việc, dùng cho hợp đồng lab-type) và man-day rate (giả định 8 giờ/ngày, dùng cho hợp đồng fixed-price và thường cao hơn man-month ÷ 20 vì gánh trách nhiệm hoàn thành) — nguồn: Vitalify Asia.
2. Đơn giá được phân theo vai trò (Programmer/BrSE/SE/PM); theo オフショア開発白書2025, giá trung bình Việt Nam là Programmer 40,1万円, Senior 50万円, BrSE 59万円, PM 74万円/tháng; offshore nói chung bằng 40–70% giá nội địa Nhật.
3. Trong hợp đồng fixed-price (請負), khối lượng công việc đã bao gồm buffer rủi ro vì nhà thầu không được đòi thêm tiền khi vượt; yêu cầu càng mơ hồ thì buffer càng dày — đây là cơ chế trung tâm của văn hóa báo giá Nhật Bản.
4. Cone of uncertainty của Boehm (1981): ước lượng ở giai đoạn concept lệch 0,25x–4,0x (biên độ 16x), thu hẹp về 0,9x–1,1x khi có thiết kế chi tiết; cone chỉ thu hẹp khi đội chủ động giảm rủi ro, không tự thu hẹp theo thời gian.
5. Thống kê vượt ngân sách: McKinsey–Oxford 2012 (5.400 dự án IT lớn) trung bình vượt 45% ngân sách; Flyvbjerg & Budzier 2011 trung bình vượt 27% với 1/6 dự án vượt >200%; CHAOS 2015: 71% dự án challenged/failed; CHAOS 1994: chỉ 16,2% thành công.
6. WBS theo PMBOK: quy tắc 100% (mỗi cấp con = đúng 100% cấp cha, không sót không thừa), work package lá trong khoảng 8–80 giờ (8/80 rule), WBS hướng deliverable và phải bao gồm cả công việc quản lý dự án; WBS dự án phần mềm thường phân theo Analysis → Design → Build → Test → Deploy + PM.
7. Không có phương pháp nào vượt trội tuyệt đối: expert judgment và mô hình tham số đạt độ chính xác tương đương trong nghiên cứu; planning poker tương đương tổng hợp chuyên gia cá nhân (Moløkken-Østvold 2008), và bucket system/affinity estimation nhanh gần gấp đôi planning poker với độ chính xác không khác biệt (Poženel 2024).
8. Thực hành phối hợp phương pháp theo giai đoạn (Nhật Bản): analogous cho chào hàng, analogous + parametric khi làm rõ yêu cầu, bottom-up từ WBS sau khi chốt yêu cầu, FP cho dự án lớn/so sánh vendor, story points cho agile; ước lượng nên trình bày dạng khoảng kèm giả định, không phải giá trị điểm.
9. Lỗi báo giá phổ biến của công ty phần mềm Việt Nam: lấy lương × hệ số truyền miệng thay vì cost rate thật, gộp dự phòng với biên lợi nhuận, không có vòng đối chiếu giờ thực sau dự án; quy đổi man-month có hai quy ước 160h hoặc 176h và phải dùng nhất quán.
10. Cảnh báo nguồn: con số "53.000 dự án công nghệ, 63%..." không truy ra nguồn công bố; các tập dữ liệu đáng tin là CHAOS (50.000+), McKinsey–Oxford (5.400), Flyvbjerg (16.000).