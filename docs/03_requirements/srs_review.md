# SRS Review — Presales Bidding Assistant

| Thuộc tính | Giá trị |
|---|---|
| Tài liệu được review | `docs/03_requirements/srs.md` (phiên bản 1.0, Draft) |
| Tài liệu đối chiếu | `docs/01_idea.md`, `docs/02_research.md`, `AGENTS.md`, `docs/03_requirements/handoff_to_review.md` |
| Ngày review | 2026-10-09 |
| Reviewer | Senior reviewer (code + document review) |
| Kết quả | **Cần sửa trước khi approve** — 18 MUST-FIX, 18 SHOULD-FIX, 5 OUT-OF-SCOPE |

---

## 1. Phương pháp và phạm vi

Review SRS dưới **hai góc nhìn** như yêu cầu:

1. **Kỹ sư presales kỳ cựu** — luồng nghiệp vụ có thực tế không: vòng làm rõ, duyệt nội bộ, versioning, tái ước lượng sau khi có câu trả lời, các luồng rẽ (reject, hủy, hết hạn).
2. **Khách hàng Nhật khó tính** — hồ sơ có qua nổi vòng review RFP Nhật không: đáp ứng từng requirement đúng thang ◎/○/△/×, lịch khớp mốc khách, giá so với ngân sách, giả định và phạm vi loại trừ rõ ràng, báo giá đúng quy ước 見積書.

Ngoài ra rà các yêu cầu mơ hồ / không kiểm thử được / mâu thuẫn nội bộ / thiếu edge case.

**Quy ước phân loại:**
- **MUST-FIX** — mâu thuẫn nội bộ, phá vỡ mục tiêu sản phẩm, hoặc thiếu yêu cầu nghiệp vụ cốt lõi khiến hồ sơ không qua nổi review khách Nhật / không triển khai được.
- **SHOULD-FIX** — mơ hồ, khó kiểm thử, hoặc thiếu chi tiết cần làm rõ trước khi implement.
- **OUT-OF-SCOPE** — đã đúng là ngoài MVP, ghi nhận rủi ro cho roadmap.

---

## 2. Điểm mạnh (giữ nguyên)

- **BR-01..BR-13 viết dạng kiểm tra được** — mỗi BR có cách kiểm tra cụ thể; đây là điểm hiếm có của một SRS.
- **Cổng giá (FR-043, BR-05)** và **bất biến hồ sơ đã duyệt (FR-061, BR-11)** — đúng tinh thần governance "ringi-ready".
- **±20% là cảnh báo, không phải cổng chặn (BR-12)** — xử lý đúng rủi ro "bảng chuẩn là chân lý" trong `docs/01_idea.md` mục Rủi ro.
- **Retry có giới hạn (≤ 2) + degrade thành cảnh báo (BR-02)** — chống retry-loop tốn token.
- **Dấu vết tính toán (FR-033)** — truy được mọi con số về bảng chuẩn + hệ số.
- **26 user stories Given/When/Then phủ đủ mọi FR Must have** — hiếm khi đầy đủ đến vậy.
- **Ma trận truy vết (mục 12)** đầy đủ; **MoSCoW (mục 8.1)** rõ ràng.

---

## 3. MUST-FIX

### M1 — Thang đánh giá thiếu ◎ và đặt "cần làm rõ" làm mức chính — mâu thuẫn với glossary và research

- **Tham chiếu:** FR-020, FR-021, US-008, mục 10 (bảng "Đánh giá requirement"), Mermaid 4.2, BR-13, glossary mục 11.
- **Vấn đề:** FR-020 định nghĩa thang đánh giá là `{○, △, ×, cần làm rõ}` — 4 mức chính, **thiếu ◎** và đưa "cần làm rõ" thành mức đáp ứng. Trong khi đó glossary mục 11 (đúng theo `docs/02_research.md` §1.3) ghi thang thực tế của khách Nhật là **4 ký hiệu ◎/○/△/×**, còn 要確認 chỉ là **nhãn phụ**. SRS tự mâu thuẫn: glossary nói một đằng, FR nói một nẻo.
- **Góc nhìn khách Nhật:** bảng đáp ứng thiếu ◎ và có mức "cần làm rõ" đứng ngang hàng ○/△/× sẽ bị chấm là sai quy ước 機能要件一覧; ◎ là mức phân biệt "đáp ứng bằng tính năng chuẩn vượt mong đợi" — thứ vendor Nhật dùng để tối đa hóa ô "○以上".
- **Đề xuất rewrite:**
  - FR-020: "AI phải đánh giá từng requirement với thang chính **{◎, ○, △, ×}** (◎ = đáp ứng bằng tính năng chuẩn vượt mong đợi, ○ = đáp ứng bằng tính năng chuẩn, △ = đáp ứng một phần/có điều kiện, × = không đáp ứng). Ngoài ra AI có thể gắn **nhãn phụ 'cần làm rõ' (要確認)** cho requirement chưa đủ thông tin để đánh giá — nhãn này không thay thế thang chính."
  - Cập nhật đồng bộ: FR-021, US-008, mục 10, Mermaid 4.2, BR-13, ma trận truy vết.

### M2 — BR-01.3 mâu thuẫn với FR-050 (AI soạn proposal)

- **Tham chiếu:** BR-01 mục 9 vs FR-050 mục 5.
- **Vấn đề:** BR-01.3 viết *"không có đường dẫn nào cho LLM output đi thẳng vào tài liệu gửi khách"*. Hiểu theo nghĩa đen thì cấm AI soạn proposal — nhưng FR-050 yêu cầu proposal do AI soạn thảo (đúng định vị "AI phân tích và soạn thảo"). Đây là lỗi diễn đạt gây mâu thuẫn nội bộ.
- **Đề xuất rewrite:** BR-01.3 → *"không có đường dẫn nào cho **con số** (man-day, giá, ngày lịch) từ LLM output đi thẳng vào tài liệu gửi khách; văn bản do AI soạn là hợp lệ nhưng mọi con số phải do code điền."*

### M3 — Thiếu ràng buộc "người duyệt giá ≠ người tạo hồ sơ" — vai trò chọn tay phá vỡ governance

- **Tham chiếu:** mục 3 (giả định MVP), FR-042, BR-05.
- **Vấn đề:** MVP giả định "vai trò chọn/chỉ định thủ công trong giao diện". Nếu presales tự chọn được vai trò manager thì anh ta tự duyệt giá hồ sơ của mình → cổng giá (BR-05) và câu chuyện "ringi-ready" (mục 2.4) vô nghĩa.
- **Góc nhìn presales:** trong công ty thật, người duyệt giá luôn khác người làm hồ sơ; đây là nguyên tắc tách nhiệm (segregation of duties).
- **Đề xuất rewrite:** bổ sung vào mục 3 hoặc FR-042: *"Hệ thống phải chặn việc người tạo hồ sơ tự duyệt giá hồ sơ đó. Trong MVP (vai trò chọn thủ công), giao diện phải gán người duyệt khác người tạo và hiển thị cảnh báo nếu vi phạm."*

### M4 — Không có FR cho phép mở lại hồ sơ đang dở / danh sách hồ sơ

- **Tham chiếu:** FR-010.3 (trạng thái "Chờ làm rõ") — thiếu FR tương ứng.
- **Vấn đề:** pipeline tạo trạng thái "Chờ làm rõ" nhưng không FR nào cho phép presales quay lại mở hồ sơ đó để trả lời câu hỏi. Không có danh sách hồ sơ (dashboard) thì presales không quay lại được hồ sơ đang dở — luồng nghiệp vụ đứt giữa chừng. Lịch sử hồ sơ là out-of-scope (§8.2.5), nhưng "mở lại hồ sơ hiện tại" là nhu cầu tối thiểu, không phải lịch sử.
- **Đề xuất rewrite:** thêm **FR-007 (Must have):** *"Hệ thống phải có danh sách hồ sơ hiển thị tên, khách hàng, trạng thái, hạn nộp; presales phải mở lại được hồ sơ ở bất kỳ trạng thái nào (Nháp, Chờ làm rõ, Chờ duyệt…) để tiếp tục làm việc."* Kèm user story US-027.

### M5 — Thiếu luồng từ chối duyệt (reject)

- **Tham chiếu:** UC-06, UC-07, FR-042, NFR-009.
- **Vấn đề:** duyệt kỹ thuật và duyệt giá chỉ có luồng "bấm duyệt → chuyển trạng thái". Không định nghĩa: manager **không** duyệt thì hồ sơ về trạng thái nào, có bắt buộc ghi lý do không, proposal xuất ra thế nào. Governance 2 cấp mà thiếu luồng reject là lỗ hổng.
- **Đề xuất rewrite:** bổ sung vào FR-042 (và FR-041): *"Khi người duyệt không duyệt, hệ thống phải yêu cầu ghi lý do từ chối, chuyển hồ sơ về trạng thái 'Bị từ chối duyệt' (kèm lý do hiển thị), và cho phép presales chỉnh sửa rồi gửi lại duyệt. Hồ sơ bị từ chối vẫn xuất được proposal với placeholder `[Presales điền]`."* Cập nhật NFR-009 danh sách trạng thái.

### M6 — Không khóa hồ sơ sau khi duyệt giá — mâu thuẫn FR-041 vs FR-042/061

- **Tham chiếu:** FR-041 (sửa WBS bất kỳ lúc nào) vs FR-042/FR-061 (hồ sơ đã duyệt giữ nguyên số).
- **Vấn đề:** sau khi duyệt giá, presales/AI developer vẫn có thể sửa WBS → code tự tính lại giá → phá vỡ "đã duyệt giá giữ nguyên số". FR-061 chỉ chống thay đổi do đổi bảng chuẩn, không chống thay đổi do sửa WBS.
- **Đề xuất rewrite:** bổ sung FR-042: *"Sau khi duyệt giá, hồ sơ chuyển trạng thái 'Đã duyệt giá' và bị **khóa**: mọi thay đổi WBS/effort/giá phải mở khóa (ghi lý do) và yêu cầu duyệt lại giá. Thay đổi chỉ được áp dụng sau khi được duyệt lại."*

### M7 — "2 cấp duyệt" không phải là cổng bắt buộc trong FR

- **Tham chiếu:** mục 2.4.4 (cam kết "2 cấp duyệt"), FR-041, FR-044, NFR-009.
- **Vấn đề:** positioning cam kết "2 cấp duyệt" nhưng FR không bắt buộc: hồ sơ có thể nhảy thẳng từ "Chờ duyệt kỹ thuật" sang "Chờ duyệt giá" mà không cần AI developer duyệt (UC-06 chỉ là use case, không phải cổng). NFR-009 có trạng thái "Chờ duyệt kỹ thuật" nhưng không FR nào yêu cầu phải đi qua.
- **Đề xuất rewrite:** bổ sung vào FR-044 (kiểm tra trước khi duyệt giá): *"Hồ sơ chỉ được chuyển sang 'Chờ duyệt giá' khi đã hoàn tất duyệt kỹ thuật (trạng thái 'Đã duyệt kỹ thuật') hoặc presales xác nhận bỏ qua duyệt kỹ thuật kèm lý do — quyết định này phải được ghi log."*

### M8 — Master schedule không dùng hạn nộp (deadline)

- **Tham chiếu:** FR-001 (nhập hạn nộp) vs FR-034 (lịch tính từ WBS × số người + ngày bắt đầu + buffer).
- **Vấn đề:** hạn nộp được nhập ở FR-001 nhưng không được dùng ở FR-034. Với khách Nhật, lịch phải khớp mốc khách và kết thúc trước hạn nộp; nếu lịch vượt hạn nộp mà không ai biết là lỗi nghiệp vụ nghiêm trọng.
- **Đề xuất rewrite:** bổ sung FR-034: *"Code phải so sánh ngày kết thúc với hạn nộp của hồ sơ; nếu ngày kết thúc > hạn nộp, hệ thống phải hiển thị **cảnh báo vượt hạn nộp** và gợi ý điều chỉnh (tăng số người, giảm buffer, hoặc báo presales thương lượng lại hạn)."*

### M9 — Proposal thiếu mục "Giả định và Phạm vi không bao gồm" (前提条件 / スコープ外)

- **Tham chiếu:** FR-050.2 (danh sách nội dung proposal).
- **Vấn đề:** FR-050.2 liệt kê: bối cảnh, giải pháp, WBS/effort, lịch, báo giá, rủi ro — **thiếu mục giả định và phạm vi không bao gồm**. `docs/02_research.md` §1.4: ghi rõ スコープ外 là quy ước bắt buộc của 見積書/提案書 Nhật — *"ghi rõ cái không có sẽ đỡ tranh cãi về sau"*. Ngoài ra FR-011.2 tạo ra các câu trả lời "giả định" nhưng không FR nào đưa chúng vào tài liệu gửi khách.
- **Đề xuất rewrite:** bổ sung FR-050.2: *"Proposal phải có mục **'Giả định (前提条件)'** — tự động tổng hợp từ các câu trả lời giả định (FR-011.2) và hệ số đã chọn (FR-031) — và mục **'Phạm vi không bao gồm (スコープ外)'** — các hạng mục khách yêu cầu nhưng không nằm trong báo giá (ví dụ: ×, △ có điều kiện)."*

### M10 — Báo giá thiếu quy ước 見積書: thuế, thời hạn hiệu lực, làm tròn yen, 内訳

- **Tham chiếu:** FR-040 vs glossary mục 11 (見積書).
- **Vấn đề:** glossary cam kết các quy ước 見積書 (税抜/税込, 見積有効期限, 内訳, giá yen tròn sạch — theo `docs/02_research.md` §1.4) nhưng **không FR nào yêu cầu chúng**. FR-040 chỉ có: đơn giá theo vai trò, offshore/onsite, overhead, tỉ giá, dự phòng, chi phí vận hành.
- **Góc nhìn khách Nhật:** báo giá thiếu 見積有効期限 hoặc không rõ 税抜/税込 bị coi là thiếu chuyên nghiệp; giá không tròn yen là dấu hiệu "quy đổi từ USD" — bị chấm điểm thấp.
- **Đề xuất rewrite:** bổ sung FR-040:
  - *"Báo giá phải có **thời hạn hiệu lực (見積有効期限)** — mặc định 30 ngày, cấu hình được."*
  - *"Báo giá phải thể hiện rõ **税抜/税込** (thuế tiêu dùng Nhật 10% cấu hình được); với khách Nhật giá chính là giá chưa thuế (税抜)."*
  - *"Với khách Nhật, tổng giá phải được **làm tròn thành số yen tròn sạch** (quy tắc làm tròn cấu hình) kèm dấu phân tách hàng nghìn."*
  - *"Báo giá phải có cấu trúc **内訳**: ngoài gom nhóm hạng mục dễ đọc (ví dụ '認証機能：5人日'), trong phân rã chi tiết theo vai trò."*

### M11 — "Ngân sách khách" không có FR nhập liệu

- **Tham chiếu:** FR-042.1 (hiển thị "báo giá, ngân sách khách, chênh lệch").
- **Vấn đề:** màn hình duyệt giá hiển thị ngân sách khách nhưng không FR nào định nghĩa ngân sách khách được nhập ở đâu, ai nhập, có bắt buộc không. Nếu không có dữ liệu thì màn hình hiển thị gì?
- **Đề xuất rewrite:** bổ sung FR-042: *"Presales phải nhập được **ngân sách khách** (tùy chọn, đơn vị tiền tệ theo ngôn ngữ khách) ở bước tạo hồ sơ hoặc trước khi gửi duyệt giá. Khi không có ngân sách, màn hình duyệt chỉ hiển thị báo giá và bỏ cột chênh lệch."*

### M12 — Không giới hạn số vòng hỏi làm rõ

- **Tham chiếu:** FR-010.1 ("tối đa 7 câu **trong một vòng dừng**").
- **Vấn đề:** không giới hạn số vòng. Presales trả lời 7 câu → AI chạy tiếp → lại thiếu thông tin → lại hỏi 7 câu → vòng lặp nghiệp vụ vô hạn, đặc biệt nguy hiểm với khách Nhật có hạn nộp cứng.
- **Đề xuất rewrite:** bổ sung FR-010.4: *"Số vòng hỏi tối đa là **2**. Sau vòng 2, hệ thống không hỏi thêm mà bắt buộc presales tự trả lời theo giả định rõ ràng (FR-011.2) để pipeline tiếp tục."*

### M13 — ±20% so với điểm nào trong dải min–max — không kiểm thử được

- **Tham chiếu:** FR-030.2 (dải min–max) vs FR-032.3 (tổng effort khớp ±20%).
- **Vấn đề:** effort là dải min–max; "tổng effort WBS khớp bảng chuẩn ±20%" so với **điểm nào** — min? max? giữa dải? Không định nghĩa thì không viết được unit test.
- **Đề xuất rewrite:** FR-032.3 → *"Tổng effort WBS phải nằm trong khoảng [min, max] của bảng chuẩn sau khi nhân hệ số; ngoài khoảng này là cảnh báo. Điểm tham chiếu để hiển thị mức lệch là **giữa dải (midpoint)**."* (Hoặc chọn quy ước khác nhưng phải định nghĩa.)

### M14 — Mô hình hợp đồng không ảnh hưởng công thức giá

- **Tham chiếu:** FR-040 (công thức giá) vs FR-042 (chỉnh mô hình hợp đồng fixed-price/lab-type/hybrid).
- **Vấn đề:** FR-042 cho đổi mô hình hợp đồng nhưng FR-040 công thức `Σ(man-day × đơn giá) + overhead + dự phòng` không có tham số mô hình hợp đồng. `docs/02_research.md` §2.5: fixed-price phải cộng contingency 15–30%, lab-type thì không. Đổi mô hình hợp đồng mà giá không đổi là vô nghĩa.
- **Đề xuất rewrite:** bổ sung FR-040: *"% dự phòng mặc định phải phụ thuộc mô hình hợp đồng: fixed-price 15–30%, lab-type 0–10%, hybrid theo cấu hình. Đổi mô hình hợp đồng ở FR-042 phải làm giá tự tính lại theo % dự phòng tương ứng."*

### M15 — Đọc file Excel requirement: thiếu xử lý nhiều sheet, cột 番号 là công thức, sinh mã nội bộ

- **Tham chiếu:** FR-003.2, FR-003.4.
- **Vấn đề:** RFP Nhật có nhiều 別紙/sheet (業務要求一覧, 非機能要求一覧, 帳票一覧…) — `docs/02_research.md` §1.2. FR-003.2 chỉ nói "tự nhận diện dòng tiêu đề và cột" — không nói xử lý nhiều sheet, bỏ sót sheet 非機能要求 = thiếu requirement (vi phạm mục tiêu 100%). Ngoài ra research §1.2 ghi nhận file thật có cột 番号 là công thức `=ROW()-1` và **không có chuẩn tên cột**; FR-003.2 yêu cầu cột "mã" nhưng file khách có thể không có cột mã.
- **Đề xuất rewrite:** bổ sung FR-003.2: *"Hệ thống phải đọc **tất cả sheet** của file Excel; presales phải gán loại cho từng sheet (sheet requirement / sheet khác). Mã requirement là **mã nội bộ do code sinh** (ví dụ REQ-001…) khi file khách không có cột mã hoặc cột số thứ tự là công thức; mapping cột 区分 (必須/任意) sang cột ưu tiên phải được presales xác nhận. Danh sách mã phải duy nhất toàn file (mọi sheet)."*

### M16 — Thiếu cơ chế resume sau lỗi pipeline (timeout, crash)

- **Tham chiếu:** FR-023, UC-04, NFR-001.
- **Vấn đề:** pipeline chạy nhiều bước LLM (đánh giá lô, WBS…). Nếu LLM timeout hoặc server crash giữa chừng, SRS không nói dữ liệu đã chạy được lưu không và presales chạy lại từ đâu. Chạy lại từ đầu = tốn token + mất thời gian demo (vi phạm S-01).
- **Đề xuất rewrite:** bổ sung FR-023: *"Mỗi bước pipeline hoàn thành phải được lưu (persist) ngay. Khi pipeline lỗi/timeout, hồ sơ giữ trạng thái bước cuối cùng và presales phải chạy lại được **từ bước bị lỗi**, không phải từ đầu."*

### M17 — Kiểm tra chất lượng tiếng Nhật chưa có FR đo được

- **Tham chiếu:** NFR-004 (chỉ nói "glossary thuật ngữ trong prompt và kiểm tra ngôn ngữ riêng").
- **Vấn đề:** tiếng Nhật là bãi đáp (beachhead) và là rủi ro cao nhất (`docs/01_idea.md` mục Rủi ro: "sai nghĩa requirement = mất uy tín"). NFR-004 nêu ý nhưng không có FR + tiêu chí chấp nhận đo được → không kiểm thử được.
- **Đề xuất rewrite:** thêm **FR-025 (Must have):** *"Với hồ sơ ngôn ngữ khách = ja, hệ thống phải chạy kiểm tra tiếng Nhật trước khi xuất tài liệu: (1) đối chiếu thuật ngữ với glossary trong prompt; (2) phát hiện văn bản lẫn tiếng Anh/ký tự Latin không đúng ngữ cảnh; (3) kiểm tra tên công ty/khách hàng đúng chính tả. Tiêu chí chấp nhận: với bộ mẫu 20 câu tiếng Nhật chuẩn, hệ thống phát hiện ≥ 90% lỗi ngôn ngữ cố ý chèn vào."*

### M18 — "Không sót requirement" khi khách không gửi file Excel — mâu thuẫn tiềm ẩn

- **Tham chiếu:** FR-003.3 vs FR-044, FR-021.
- **Vấn đề:** FR-003.3 cho phép bỏ qua bảng đáp ứng khi không có file Excel; nhưng FR-044 (kiểm tra trước duyệt) yêu cầu "không sót requirement" và FR-021 kiểm tra mã đúng một lần. Khi không có file Excel thì danh sách requirement là gì và kiểm tra "không sót" áp dụng với cái gì?
- **Đề xuất rewrite:** bổ sung FR-044: *"Khi hồ sơ không có file Excel requirement (FR-003.3), kiểm tra 'không sót requirement' được bỏ qua và ghi rõ trong báo cáo kiểm tra: 'Khách không gửi file Excel requirement — bỏ qua bảng đáp ứng'."*

---

## 4. SHOULD-FIX

### S1 — "Giữ các quyết định đã duyệt" khi chạy lại từ bước WBS — mơ hồ

- **Tham chiếu:** FR-041.2, US-018.
- **Vấn đề:** chạy lại từ bước WBS nghĩa là WBS cũ bị thay; "giữ các quyết định đã duyệt" giữ cái gì?
- **Đề xuất:** FR-041.2 → *"Chạy lại từ bước WBS: giữ nguyên đánh giá requirement (FR-020) và hướng giải pháp (FR-022); chỉ tạo lại WBS, effort, lịch, giá."*

### S2 — Hệ số nhân do ai chọn?

- **Tham chiếu:** FR-031.
- **Vấn đề:** 8 hệ số liệt kê nhưng không nói ai bật/tắt. `docs/01_idea.md` mục Rủi ro: "hướng giải pháp và hệ số do AI chọn → con số chỉ đáng tin bằng đầu vào".
- **Đề xuất:** FR-031 → *"AI phải đề xuất bộ hệ số kèm lý do; presales/AI developer xác nhận hoặc chỉnh trước khi tính effort. Mặc định theo ngữ cảnh: khách Nhật → tự bật hệ số 'khách Nhật'; dữ liệu mẫu kém → gợi ý bật hệ số 'dữ liệu chưa sẵn sàng' (từ FR-004)."*

### S3 — Không có FR đổi hướng giải pháp sau khi AI đề xuất

- **Tham chiếu:** FR-022.
- **Vấn đề:** AI đề xuất 1 hướng; nếu AI developer không đồng ý thì sao? Không có luồng đổi hướng.
- **Đề xuất:** bổ sung FR-022: *"AI developer phải đổi được hướng giải pháp; khi đổi, code tính lại effort theo bảng chuẩn của hướng mới (không gọi lại AI phần đánh giá requirement)."*

### S4 — Đánh giá requirement gắn với hướng giải pháp chưa rõ

- **Tham chiếu:** FR-020, FR-022.
- **Vấn đề:** một requirement × với hướng A có thể thành ○ với hướng B. Đổi hướng giải pháp thì đánh giá cũ còn đúng không?
- **Đề xuất:** FR-020 → *"Đánh giá ○/△/× phải gắn với hướng giải pháp đang chọn; khi đổi hướng giải pháp (S3), hệ thống phải đánh giá lại hoặc hiển thị cảnh báo 'đánh giá theo hướng giải pháp cũ'."*

### S5 — Đơn vị tiền tệ của báo giá/Excel chưa định nghĩa

- **Tham chiếu:** FR-040, FR-051.
- **Vấn đề:** không nói báo giá xuất bằng tiền tệ nào. Khách Nhật nhận JPY, khách VN nhận VND.
- **Đề xuất:** FR-051 → *"Tiền tệ mặc định theo ngôn ngữ khách: ja → JPY, vi → VND, en → USD; cấu hình được ở cấp hồ sơ."*

### S6 — Thiếu thông tin công ty gửi thầu và điều khoản thanh toán (インボイス)

- **Tham chiếu:** FR-040, FR-050.
- **Vấn đề:** `docs/02_research.md` §1.4: khách Nhật chỉ trả bằng 請求書払い, cần mã 適格請求書発行事業者 (インボイス制度) — thiếu là bị loại âm thầm. SRS không có khái niệm thông tin công ty (tên, địa chỉ, mã số thuế, mã 適格請求書) trong cấu hình.
- **Đề xuất:** bổ sung vào FR-060 (bảng chuẩn): *"Cấu hình phải chứa thông tin công ty gửi thầu (tên, địa chỉ, mã số thuế, mã 適格請求書発行事業者 — giả lập trong MVP) và điều khoản thanh toán (payment terms); các trường này xuất vào proposal/見積書."*

### S7 — Không hỗ trợ .xls (Excel 97-2003)

- **Tham chiếu:** FR-002.1.
- **Vấn đề:** `docs/02_research.md` §1.4: mẫu 見積書 của Bộ Quốc phòng Nhật là .xls; chính quyền Nhật vẫn dùng .xls. Từ chối file .xls của khách là rủi ro.
- **Đề xuất:** FR-002.1 → cân nhắc hỗ trợ `.xls` hoặc ít nhất ghi rõ: *"File .xls được chấp nhận nhưng yêu cầu presales xác nhận chuyển đổi; nếu không hỗ trợ, thông báo rõ 'vui lòng lưu lại dưới dạng .xlsx'."*

### S8 — Tỉ giá: nguồn và ngày hiệu lực

- **Tham chiếu:** FR-040.
- **Vấn đề:** tỉ giá VND/JPY/USD trong rate card không nói lấy ở đâu, cập nhật thế nào, ngày áp dụng.
- **Đề xuất:** FR-040 → *"Tỉ giá là trường cấu hình có ngày hiệu lực; dấu vết tính toán (FR-033) phải ghi tỉ giá và ngày hiệu lực đã dùng."*

### S9 — Bộ test PII chuẩn chưa định nghĩa

- **Tham chiếu:** NFR-002 ("tỷ lệ che ≥ 99%").
- **Vấn đề:** không có bộ mẫu PII thì không kiểm thử được tỷ lệ 99%.
- **Đề xuất:** NFR-002 → *"Bộ test PII tối thiểu: 50 mẫu gồm email, số điện thoại VN (+84/0xx), số điện thoại Nhật (0X-XXXX-XXXX, +81), địa chỉ email lẫn trong văn bản tiếng Nhật. Tỷ lệ che ≥ 99% tính trên bộ này."*

### S10 — "Vài phút" không đo được

- **Tham chiếu:** NFR-001, mục 2.2.
- **Vấn đề:** "bản nháp trong vài phút" không có ngưỡng đo.
- **Đề xuất:** NFR-001 → *"Từ lúc presales bấm 'Phân tích' đến khi có bản nháp đầy đủ (kèm 1 vòng hỏi ≤ 7 câu đã trả lời) ≤ 15 phút với hồ sơ 235 requirement (môi trường demo, LLM thật)."*

### S11 — Lịch làm việc (nghỉ lễ VN/Nhật) chưa rõ

- **Tham chiếu:** FR-034, glossary (man-day).
- **Vấn đề:** lịch cho khách Nhật phải trừ ngày nghỉ lễ Nhật; SRS không nói lịch làm việc dùng lịch nào.
- **Đề xuất:** FR-034 → *"Master schedule phải tính trên lịch làm việc cấu hình (nghỉ lễ VN và/hoặc Nhật); mặc định theo ngôn ngữ khách (ja → lịch Nhật)."*

### S12 — Template trung tính chưa định nghĩa vị trí

- **Tham chiếu:** FR-050.
- **Vấn đề:** "template trung tính (bìa, header/footer, logo)" — logo của ai, template nằm ở đâu?
- **Đề xuất:** FR-050 → *"Template trung tính là asset trong repo (thư mục templates/), có thể thay thế bằng template công ty ở bản sau; logo là placeholder trung tính."*

### S13 — Validate toàn vẹn bảng chuẩn khi lưu

- **Tham chiếu:** FR-060.
- **Vấn đề:** validate cú pháp nhưng không validate đầy đủ: nếu bảng effort thiếu tổ hợp (hướng giải pháp × giai đoạn) thì AI đề xuất hướng đó sẽ lỗi runtime.
- **Đề xuất:** FR-060 → *"Validate khi lưu phải kiểm tra toàn vẹn: mọi tổ hợp hướng giải pháp × giai đoạn đều có min–max; mọi vai trò trong rate card đều có đơn giá offshore và onsite; trần hệ số > 1."*

### S14 — Không có snapshot WBS trước khi chạy lại

- **Tham chiếu:** FR-041.2.
- **Vấn đề:** chạy lại từ bước WBS làm mất WBS cũ — không so sánh được trước/sau. `docs/02_research.md` §3.2: "no version control, no audit trail" là điểm yếu bị chỉ trích.
- **Đề xuất:** FR-041.2 → *"Trước khi chạy lại từ bước WBS, hệ thống phải lưu snapshot WBS hiện tại để so sánh trước/sau (tối thiểu hiển thị khác biệt về tổng man-day và danh sách task)."*

### S15 — Không có FR sửa văn bản proposal trong web trước khi xuất

- **Tham chiếu:** FR-050; mục 3 (presales "soạn thảo").
- **Vấn đề:** bảng vai trò nói presales "soạn thảo" nhưng không FR nào cho sửa văn bản proposal trong web (chỉ sửa WBS). Nếu không, presales phải sửa trong Word sau khi xuất — mất dấu vết.
- **Đề xuất:** FR-050 → *"MVP cho phép presales sửa các trường văn bản chính của proposal (mở đầu, tổng quan giải pháp, kết luận) trong web trước khi xuất; phần còn lại sửa sau khi xuất Word. Quyết định này phải được ghi rõ để tránh hiểu lầm."*

### S16 — "Chi phí vận hành/tháng" tính vào tổng hay tách riêng?

- **Tham chiếu:** FR-040.
- **Vấn đề:** chi phí vận hành (hosting/LLM, đáng kể với RAG — `docs/02_research.md` §2.4) không nói tính vào tổng báo giá hay ghi riêng.
- **Đề xuất:** FR-040 → *"Chi phí vận hành/tháng được hiển thị tách riêng trong 内訳 và có cấu hình 'tính vào tổng' hay 'ghi riêng'."*

### S17 — Ngữ cảnh giữa các lô đánh giá

- **Tham chiếu:** FR-020 (lô ≤ 40).
- **Vấn đề:** requirement liên quan nhau nằm khác lô → đánh giá thiếu nhất quán (một requirement △ ở lô 1, lô 2 lại ○).
- **Đề xuất:** FR-020 → *"Mỗi lô gửi LLM phải kèm danh sách tên/mã toàn bộ requirement (hoặc tóm tắt) để giữ ngữ cảnh; kết quả các lô được gộp và kiểm tra nhất quán theo FR-021."*

### S18 — Requirement "cần làm rõ" được đánh giá lại sau vòng hỏi chưa rõ

- **Tham chiếu:** FR-020, FR-010/011.
- **Vấn đề:** sau khi presales trả lời câu hỏi, các requirement mang nhãn 要確認 có được đánh giá lại không?
- **Đề xuất:** FR-020 → *"Requirement mang nhãn 'cần làm rõ' phải được đánh giá lại sau khi presales trả lời vòng hỏi; nếu vẫn chưa đủ thông tin, giữ nhãn và hiển thị trong proposal như giả định."*

---

## 5. OUT-OF-SCOPE (ghi nhận cho roadmap)

### O1 — Điền ◎/○/△/× vào đúng file Excel của khách (giữ format)

- **Tham chiếu:** §8.2.2; `docs/02_research.md` §5.2.
- **Ghi nhận:** đây là khác biệt cạnh tranh #2 của sản phẩm và là "luật chơi" bắt buộc của khách Nhật (điền ngay trong file khách gửi). MVP chỉ hiện bảng trên web — chấp nhận được cho demo nhưng **không phải là sản phẩm bán được cho khách Nhật**. Nên đưa lên roadmap gần nhất sau MVP.

### O2 — Q&A sheet vòng với khách

- **Tham chiếu:** §8.2.1; `docs/02_research.md` §1.1 (質問記入票).
- **Ghi nhận:** văn hóa Nhật kỳ vọng câu hỏi gửi qua file/biểu mẫu và câu trả lời công bố cho mọi nhà thầu. MVP chỉ trả lời trên web → presales phải tự chuyển câu hỏi ra file thủ công. Rủi ro demo với khách Nhật; ghi nhận để roadmap.

### O3 — Lịch sử hồ sơ + nhân bản

- **Tham chiếu:** §8.2.5.
- **Ghi nhận:** đúng là ngoài MVP, nhưng **M4** (mở lại hồ sơ đang dở) là nhu cầu tối thiểu không thể trì hoãn — phân biệt rõ "danh sách hồ sơ hiện tại" (cần trong MVP) với "lịch sử + nhân bản" (sau MVP).

### O4 — PPTX, template riêng, phân tích .zip, AI trích RFP, gợi ý hồ sơ tương tự, vector DB

- **Tham chiếu:** §8.2.4, §8.2.7, §8.2.8, §8.2.9, §8.2.10.
- **Ghi nhận:** đồng ý với việc loại khỏi MVP; không phản đối.

### O5 — Hỗ trợ "ringi-ready" sâu (tài liệu phê duyệt nội bộ khách, nemawashi)

- **Tham chiếu:** `docs/02_research.md` §1.6.
- **Ghi nhận:** proposal "ringi-ready" (tóm tắt 1 trang, logic phê duyệt rõ, kiểm soát rủi ro nhìn thấy được) là giá trị lớn cho khách Nhật nhưng ngoài MVP. Nên ghi vào roadmap.

---

## 6. Kết luận

SRS **chưa sẵn sàng để approve** ở phiên bản 1.0. Cấu trúc tốt, BR kiểm tra được, user stories đầy đủ — nhưng có **18 lỗi MUST-FIX**, trong đó nhiều lỗi là **mâu thuẫn nội bộ** (M1 thang đánh giá, M2 BR-01.3, M6 khóa hồ sơ, M7 2 cấp duyệt, M14 mô hình hợp đồng, M18 không-sót-requirement) và **thiếu yêu cầu cốt lõi cho khách Nhật** (M9 スコープ外, M10 quy ước 見積書, M15 nhiều sheet, M17 kiểm tra tiếng Nhật).

**Khuyến nghị xử lý:**
1. BA sửa các mục MUST-FIX (chủ yếu là bổ sung/điều chỉnh FR hiện có, không cần thay đổi kiến trúc).
2. Các SHOULD-FIX chốt quyết định trong vòng review tiếp theo (nhiều mục chỉ cần chọn 1 trong 2 phương án).
3. Sau khi sửa, chạy lại kiểm tra nhất quán: thang đánh giá, trạng thái hồ sơ, công thức giá, danh sách FR↔US↔BR↔NFR.

---

## 7. Tóm tắt (summary)

| Phân loại | Số lượng |
|---|---|
| **MUST-FIX** | **18** |
| **SHOULD-FIX** | **18** |
| **OUT-OF-SCOPE** | **5** |
| **Tổng** | **41** |

Danh sách MUST-FIX: M1 (thang ◎/○/△/×), M2 (BR-01.3), M3 (tách người duyệt), M4 (mở lại hồ sơ), M5 (luồng reject), M6 (khóa sau duyệt), M7 (cổng duyệt kỹ thuật), M8 (hạn nộp trong lịch), M9 (スコープ外), M10 (quy ước 見積書), M11 (ngân sách khách), M12 (giới hạn vòng hỏi), M13 (±20% điểm tham chiếu), M14 (mô hình hợp đồng → giá), M15 (nhiều sheet/mã nội bộ), M16 (resume sau lỗi), M17 (kiểm tra tiếng Nhật), M18 (không-sót khi thiếu Excel).

Danh sách SHOULD-FIX: S1 (giữ quyết định khi chạy lại), S2 (hệ số do ai chọn), S3 (đổi hướng giải pháp), S4 (đánh giá gắn hướng), S5 (tiền tệ), S6 (thông tin công ty/インボイス), S7 (.xls), S8 (tỉ giá), S9 (bộ test PII), S10 ("vài phút"), S11 (lịch nghỉ lễ), S12 (template), S13 (validate toàn vẹn bảng chuẩn), S14 (snapshot WBS), S15 (sửa proposal trong web), S16 (chi phí vận hành), S17 (ngữ cảnh lô), S18 (đánh giá lại 要確認).

**Task SRS Review complete. Awaiting prompt for the next role.**

---

## 8. Review resolution (BA — 2026-10-09)

Áp dụng toàn bộ MUST-FIX và SHOULD-FIX vào `srs.md` (phiên bản 1.1). Các OUT-OF-SCOPE ghi nhận cho roadmap, không áp dụng.

| Finding | Áp dụng? | Lý do / cách xử lý |
|---|---|---|
| M1 — Thang ◎/○/△/× + 要確認 | ✅ Áp dụng | Sửa FR-020, FR-021, US-008, BR-13, mục 10, Mermaid 4.2: thang chính {◎,○,△,×}, "cần làm rõ" là nhãn phụ. |
| M2 — BR-01.3 mâu thuẫn FR-050 | ✅ Áp dụng | Diễn đạt lại BR-01.3: chỉ cấm **con số** từ LLM đi thẳng vào tài liệu; văn bản AI soạn hợp lệ. |
| M3 — Người duyệt ≠ người tạo | ✅ Áp dụng | Thêm FR-042.2 + ghi chú mục 3: chặn tự duyệt giá. |
| M4 — Mở lại hồ sơ đang dở | ✅ Áp dụng | Thêm FR-007 (Must have) + UC-11 + US-027. |
| M5 — Luồng từ chối duyệt | ✅ Áp dụng | Thêm FR-041.4, FR-042.3, cập nhật NFR-009 (trạng thái "Bị từ chối duyệt"). |
| M6 — Khóa hồ sơ sau duyệt giá | ✅ Áp dụng | Thêm FR-042.4: khóa + mở khóa (ghi lý do) + duyệt lại. |
| M7 — Cổng duyệt kỹ thuật | ✅ Áp dụng | FR-044: bắt buộc qua duyệt kỹ thuật hoặc bỏ qua kèm lý do (ghi log). |
| M8 — Hạn nộp trong lịch | ✅ Áp dụng | FR-034: cảnh báo vượt hạn nộp + gợi ý điều chỉnh. |
| M9 — Giả định & スコープ外 | ✅ Áp dụng | FR-050.2: thêm mục Giả định (前提条件) + Phạm vi không bao gồm (スコープ外). |
| M10 — Quy ước 見積書 | ✅ Áp dụng | FR-040: 見積有効期限, 税抜/税込, làm tròn yen, 内訳. |
| M11 — Ngân sách khách | ✅ Áp dụng | FR-042.1: nhập ngân sách (tùy chọn); không có → bỏ cột chênh lệch. |
| M12 — Giới hạn vòng hỏi | ✅ Áp dụng | FR-010.4: tối đa 2 vòng, sau đó bắt buộc giả định. |
| M13 — Điểm tham chiếu ±20% | ✅ Áp dụng | FR-032.3: tham chiếu giữa dải (midpoint). |
| M14 — Mô hình hợp đồng → giá | ✅ Áp dụng | FR-040: % dự phòng theo mô hình hợp đồng (fixed 15–30%, lab 0–10%). |
| M15 — Nhiều sheet / mã nội bộ | ✅ Áp dụng | FR-003.2/.6: đọc tất cả sheet, sinh mã nội bộ, xử lý cột công thức, mapping 区分. |
| M16 — Resume sau lỗi | ✅ Áp dụng | FR-023: persist từng bước, chạy lại từ bước lỗi. |
| M17 — Kiểm tra tiếng Nhật | ✅ Áp dụng | Thêm FR-025 (Must have) + US-028. |
| M18 — Không-sót khi thiếu Excel | ✅ Áp dụng | FR-044: bỏ qua kiểm tra "không sót" khi không có file Excel, ghi rõ trong báo cáo. |
| S1 — Giữ quyết định khi chạy lại | ✅ Áp dụng | FR-041.2: giữ đánh giá requirement + hướng giải pháp; chỉ tạo lại WBS/effort/lịch/giá. |
| S2 — Hệ số do ai chọn | ✅ Áp dụng | FR-031: AI đề xuất kèm lý do, presales xác nhận/chỉnh. |
| S3 — Đổi hướng giải pháp | ✅ Áp dụng | FR-022 AC3: AI developer đổi hướng → tính lại effort. |
| S4 — Đánh giá gắn hướng | ✅ Áp dụng | FR-020 AC5: đổi hướng → đánh giá lại hoặc cảnh báo. |
| S5 — Tiền tệ | ✅ Áp dụng | FR-051: ja→JPY, vi→VND, en→USD, cấu hình ở cấp hồ sơ. |
| S6 — Thông tin công ty / インボイス | ✅ Áp dụng | FR-060: thêm thông tin công ty + payment terms (giả lập MVP). |
| S7 — .xls | ✅ Áp dụng | FR-002.1: chấp nhận .xls, chuyển đổi nội bộ hoặc báo rõ. |
| S8 — Tỉ giá ngày hiệu lực | ✅ Áp dụng | FR-040 AC6: tỉ giá có ngày hiệu lực, ghi trong dấu vết. |
| S9 — Bộ test PII | ✅ Áp dụng | NFR-002: bộ mẫu ≥ 50 (email, SĐT VN/Nhật, email lẫn tiếng Nhật). |
| S10 — "Vài phút" đo được | ✅ Áp dụng | NFR-001: ≤ 15 phút với hồ sơ 235 requirement. |
| S11 — Lịch nghỉ lễ | ✅ Áp dụng | FR-034: lịch làm việc cấu hình (nghỉ lễ VN/Nhật). |
| S12 — Template trung tính | ✅ Áp dụng | FR-050: asset trong `templates/`, thay thế được. |
| S13 — Validate toàn vẹn bảng chuẩn | ✅ Áp dụng | FR-060.2: mọi tổ hợp hướng × giai đoạn có min–max; đơn giá đủ; trần > 1. |
| S14 — Snapshot WBS | ✅ Áp dụng | FR-041.2: lưu snapshot trước khi chạy lại, hiển thị khác biệt. |
| S15 — Sửa proposal trong web | ✅ Áp dụng | FR-050: sửa trường văn bản chính trong web trước xuất. |
| S16 — Chi phí vận hành | ✅ Áp dụng | FR-040 AC7: tách riêng trong 内訳, cấu hình tính vào tổng/ghi riêng. |
| S17 — Ngữ cảnh lô | ✅ Áp dụng | FR-020 AC3: mỗi lô kèm danh sách mã/tên toàn bộ requirement. |
| S18 — Đánh giá lại 要確認 | ✅ Áp dụng | FR-020 AC4: đánh giá lại sau vòng hỏi; chưa đủ → giữ nhãn, hiển thị như giả định. |
| O1 — Điền file khách (giữ format) | ❌ Không áp dụng | Ngoài MVP (§8.2.2). Ghi nhận: đưa lên roadmap gần nhất — điểm bán chính cho khách Nhật. |
| O2 — Q&A sheet vòng với khách | ❌ Không áp dụng | Ngoài MVP (§8.2.1). Ghi nhận rủi ro demo khách Nhật. |
| O3 — Lịch sử + nhân bản | ❌ Không áp dụng | Ngoài MVP (§8.2.5). Riêng nhu cầu "mở lại hồ sơ" đã đưa vào MVP qua M4/FR-007. |
| O4 — PPTX/template riêng/zip/AI trích RFP/gợi ý tương tự/vector DB | ❌ Không áp dụng | Đồng ý ngoài MVP. |
| O5 — Ringi-ready sâu / nemawashi | ❌ Không áp dụng | Ngoài MVP. Ghi nhận cho roadmap. |