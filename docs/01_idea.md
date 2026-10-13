# 01. Ý tưởng — Web app hỗ trợ presales làm hồ sơ dự thầu

## Tóm tắt

Web app nội bộ giúp đội presales tạo hồ sơ dự thầu cho khách hàng Việt Nam và Nhật Bản: từ email + RFP + file Excel requirement của khách, AI phân tích và soạn thảo, **code tính số và kiểm tra**, con người duyệt trước khi gửi khách. Đầu ra là bộ hồ sơ gồm proposal Word (theo ngôn ngữ khách) và Excel ước tính (WBS, man-day, báo giá, lịch).

**Nguyên tắc cốt lõi:** *AI phân tích và soạn thảo, code tính số và kiểm tra, con người quyết định.*

- AI **không bao giờ tự bịa con số**: effort và giá luôn do code tính từ bảng chuẩn.
- Hệ thống **không bao giờ "tự học"** để thay đổi con số. Muốn đổi effort/đơn giá chuẩn, manager sửa bảng chuẩn ở trang Cài đặt — có chủ đích, có người chịu trách nhiệm.
- Khi thiếu thông tin, AI **dừng lại và hỏi** — không đoán bừa. Đây là điểm khác biệt cốt lõi so với chat AI thông thường.

## Điểm khác biệt

So với chat AI thông thường (dùng ChatGPT/Claude để viết proposal):

| Chat AI thông thường | App này |
|---|---|
| Bịa số liệu khi thiếu thông tin | Số do **code tính từ bảng chuẩn**, mọi con số truy được về công thức |
| Trả lời ngay cả khi thiếu thông tin | **Dừng lại, hỏi tối đa 7 câu** — không đoán bừa |
| Không ai chịu trách nhiệm cho con số | **2 cấp duyệt**; chưa duyệt giá thì proposal không có số tiền |
| Định dạng file AI tự dựng, khó kiểm soát | File xuất **bằng code** theo template; Excel giữ công thức để chỉnh tay |
| Không kiểm tra tính đầy đủ | Code kiểm tra: **không sót requirement**, tổng effort ±20%, đúng schema |
| Không nhớ lịch sử, mỗi lần hỏi lại từ đầu | Hồ sơ có trạng thái, có dấu vết tính toán, có thể nhân bản |

## Định vị sản phẩm

Ba hướng đã cân nhắc:

- **A. Copilot soạn thảo** — "bản nháp trong vài phút thay vì 1–2 ngày". Hấp dẫn nhưng dễ bị coi là wrapper chat AI; khác biệt mờ.
- **B. Công cụ ước lượng có trách nhiệm (governance)** — "số liệu đáng tin cậy: truy được về bảng chuẩn, có người duyệt, không bịa". Chơi đúng 3 điểm khác biệt tự nhiên của sản phẩm.
- **C. Chuyên biệt thị trường Nhật** — 別紙1, tiếng Nhật, BrSE overhead, truy vết requirement nghiêm ngặt. Sâu nhưng hẹp.

**Chọn B, dùng C làm bãi đáp (beachhead).** Lý do: cả ba điểm khác biệt (không bịa số, hỏi lại, người duyệt) đều nói về **lòng tin và kiểm soát**, không phải tốc độ hay ngôn ngữ. Khách Nhật soi kỹ từng requirement — chính là nơi câu chuyện "đáng tin cậy" có giá trị cao nhất, nên demo tiếng Nhật vừa là minh chứng vừa là thị trường mở đầu.

## Bối cảnh (Why now)

- Hiện tại presales mất **1–2 ngày** để ra được bản nháp hồ sơ dự thầu.
- Số liệu effort/giá phụ thuộc **kinh nghiệm cá nhân** và dễ sai.
- Khách Nhật **soi rất kỹ từng requirement** — không thể sót hoặc bịa.
- Mục tiêu: có bản nháp đầy đủ trong **vài phút**, để presales dành thời gian cho việc chỉnh sửa và chiến lược giá.

Bối cảnh triển khai: **bài thi nội bộ** — không được dùng dữ liệu công ty hay dữ liệu khách thật. Mọi số liệu là **giả lập nhưng sát mặt bằng thị trường** (team offshore Việt Nam làm cho khách VN/Nhật), ghi rõ "giả lập" trong file. App phải thiết kế để sau này công ty thay bằng số thật **mà không cần sửa code**.

## Người dùng và vai trò

| Vai trò | Việc họ làm |
|---|---|
| **Presales** | Tạo hồ sơ, nhập thông tin, đính kèm file, trả lời câu hỏi làm rõ, soạn thảo, xuất file gửi khách |
| **AI developer / kỹ sư** | Duyệt kỹ thuật: xem lại giải pháp, kiến trúc, rủi ro, WBS, effort. Sửa trực tiếp trên web (thêm/sửa/xóa task WBS, chỉnh man-day) — sửa xong code tự tính lại tổng, lịch, giá, **không gọi lại AI**. Nếu chưa ổn, ghi góp ý và yêu cầu AI chạy lại từ một bước cụ thể |
| **Manager / sales lead** | Duyệt giá: so sánh báo giá với ngân sách khách, chỉnh dự phòng, mô hình hợp đồng, rồi bấm duyệt. Cũng là người cập nhật bảng chuẩn ở trang Cài đặt |

AI **không review thay con người** — con người luôn là người quyết định cuối cùng.

## Luồng làm việc

### Bước 1 — Tạo hồ sơ mới (presales)
1. Nhập thông tin hồ sơ: tên dự án, khách hàng, hạn nộp.
2. **Dán email / nội dung yêu cầu của khách** vào ô nhập (bắt buộc).
3. Đính kèm tối đa **10 file**, mỗi file ≤ 20 MB:
   - RFP / tài liệu (`.pdf`, `.docx`, `.txt`, `.md`) → **code trích text**; AI chỉ đọc phần tóm tắt có giới hạn ký tự.
   - Excel/CSV danh sách requirement → **code tự nhận diện** dòng tiêu đề và các cột (mã, nội dung, ưu tiên, phân loại), ra danh sách requirement chính xác từng dòng. **Code đọc, không để AI trích xuất** — để chắc chắn không sót, không bịa.
   - Dữ liệu mẫu (`.csv`/`.xlsx`) → code phân tích profile: số dòng, kiểu cột, % trống, cột nghi chứa thông tin cá nhân → gợi ý mức sẵn sàng dữ liệu.
   - *(Sau MVP)* Source code `.zip` → code thống kê ngôn ngữ, framework.
   - Code **tự đoán loại file**, presales đổi lại được nếu sai.
4. Trước khi bấm **Phân tích**, web hiện kết quả đọc file: số requirement đọc được, file nào lỗi. Presales kiểm tra nhanh rồi mới chạy.

### Bước 2 — Hỏi lại khi thiếu thông tin (điểm khác biệt cốt lõi)
- Khi thiếu thông tin **ảnh hưởng tới giải pháp / effort / giá**, AI **dừng lại** và đưa **tối đa 7 câu hỏi làm rõ**.
- Câu hỏi viết bằng **ngôn ngữ khách** (vi/en/ja), kèm **lý do bằng tiếng Việt** cho presales.
- Presales trả lời trên web, **hoặc** xuất Q&A sheet gửi khách, khách điền rồi gửi lại, nhập lại vào web → AI chạy tiếp.
- **Không đoán bừa.**

### Bước 3 — Phân tích và soạn thảo (AI, có kiểm tra bằng code)
- AI đánh giá từng requirement (○ đáp ứng / △ một phần / × không / cần làm rõ) theo lô ≤ 40 dòng.
- Code kiểm tra: mỗi mã requirement xuất hiện **đúng một lần** — thiếu hoặc thừa thì AI phải làm lại.
- AI tạo WBS theo hướng giải pháp; **tổng effort phải khớp bảng chuẩn ±20%** (code kiểm tra).
- Output AI phải đúng schema; WBS phải đủ PM/QA mỗi giai đoạn.
- Phát hiện sai → AI làm lại, và **cảnh báo hiển thị cho người duyệt**.
- Tiến độ từng bước AI hiển thị **realtime trên web**.

Nếu khách **KHÔNG gửi file Excel requirement**: MVP bỏ qua bảng đáp ứng (ghi rõ trên web). *(Sau MVP:* AI trích requirement từ văn bản RFP, đánh dấu "AI trích – cần xác nhận"*.)*

### Bước 4 — Duyệt kỹ thuật (AI developer)
- Xem lại hướng giải pháp, kiến trúc, rủi ro, WBS, effort.
- Sửa trực tiếp trên web (thêm/sửa/xóa task WBS, chỉnh man-day) → code tự tính lại tổng, lịch, giá.
- Chưa ổn → ghi góp ý, yêu cầu AI chạy lại từ một bước cụ thể (ví dụ chạy lại từ bước WBS theo góp ý).

### Bước 5 — Duyệt giá (manager / sales lead)
- Xem báo giá so với ngân sách khách, chỉnh dự phòng, mô hình hợp đồng → bấm duyệt.
- **Chưa duyệt giá**: proposal gửi khách chỉ hiện `"[Presales điền]"`, **không hiện số tiền**.

### Bước 6 — Xuất file gửi khách
- Web chỉ là nơi làm việc nội bộ; khách nhận **file**, không xem qua link web.

## Đầu vào

Email / nội dung yêu cầu (dán vào, bắt buộc) + tối đa 10 file đính kèm (RFP, Excel/CSV requirement, dữ liệu mẫu). Có sẵn **1–2 bộ hồ sơ mẫu giả lập** (email + RFP + Excel requirement) nạp bằng một nút để demo nhanh.

## Đầu ra (bộ hồ sơ)

1. **Proposal Word (.docx)** — theo template công ty (bìa, header/footer, logo), ngôn ngữ khách (vi/en/ja). PDF chỉ là bản chuyển từ Word khi cần nộp.
2. **Slide PowerPoint (.pptx)** — bản tóm tắt thuyết trình: bối cảnh, giải pháp, kiến trúc, effort, lịch, báo giá, rủi ro. Sơ đồ và Gantt là **shape sửa được**, không phải ảnh chụp. *(Sau MVP)*
3. **Excel ước tính (.xlsx)** — WBS, tổng man-day, báo giá, master schedule; tổng là **công thức Excel** để presales chỉnh tay được.
4. **File Excel requirement của khách** (ví dụ 別紙1 với khách Nhật) — điền ○/△/× và ghi chú vào **đúng file khách gửi**, giữ nguyên định dạng.
5. **Q&A sheet (.xlsx)** — câu hỏi làm rõ gửi khách; khách điền câu trả lời, gửi lại, nhập lại vào web để AI chạy tiếp.

**Template:** công ty upload template riêng (Word/PowerPoint/Excel) ở trang Cài đặt; nếu chưa có thì dùng bộ template mẫu trung tính. *(Upload template riêng: sau MVP)*

**Tất cả file xuất ra bằng code, không để AI tự dựng định dạng.**

## Master schedule (trong MVP)

- Code tính từ WBS × số người mỗi vai trò, ngày bắt đầu, buffer.
- Có mốc thanh toán.
- Sửa WBS hoặc số người → lịch và giá **tự tính lại**.

## Bảng chuẩn (cấu hình, không nằm trong code)

Lưu dạng **file YAML trong repo**, sửa được trên trang Cài đặt (có validate). Người cập nhật: manager/presales lead. Mọi thay đổi chỉ áp dụng cho hồ sơ **tính lại sau đó**; hồ sơ **đã duyệt giá giữ nguyên số**.

### 1. Bảng effort chuẩn
- Man-day **min–max** theo hướng giải pháp (không cần AI / ML truyền thống / RAG / agent / fine-tune) × giai đoạn (PoC / MVP / Production).
- Hệ số nhân: on-premise, khách Nhật (tài liệu tiếng Nhật), dữ liệu chưa sẵn sàng, tuân thủ chặt, đa ngôn ngữ, cần OCR, dữ liệu lớn, nhiều requirement. **Tích hệ số có trần.**
- Công thức: `effort = bảng chuẩn × hệ số`. WBS do AI chia nhưng tổng phải khớp ±20%.

### 2. Bảng đơn giá (rate card)
- Đơn giá/ngày theo vai trò (PM, BA, BrSE, AI engineer, backend, frontend, QA, infra...), tách **offshore** và **onsite**.
- Overhead: PM ~10%, BrSE ~15% khi khách Nhật.
- Tỉ giá VND/JPY/USD, % dự phòng theo rủi ro, mốc thanh toán, chi phí vận hành/tháng.

## Tái sử dụng nhẹ (không có kho tri thức tự học)

Không embedding, không vector DB. Ba cách tái sử dụng đều làm bằng code đơn giản:

1. **(MVP) Dự án tham chiếu:** 4–6 dự án mẫu giả lập viết dạng Markdown trong thư mục knowledge base (bài toán, giải pháp, effort thực tế, bài học). AI đọc để giải thích và so sánh khi ước lượng, nhưng **KHÔNG được dùng để đổi con số** — số vẫn do code tính từ bảng chuẩn.
2. **(MVP) Trang Lịch sử hồ sơ:** tìm kiếm, lọc theo khách hàng/trạng thái/giai đoạn deal, mở lại hồ sơ cũ để xem hoặc **nhân bản** làm điểm bắt đầu.
3. *(Sau MVP) Gợi ý "hồ sơ tương tự":* code chấm điểm đơn giản (cùng hướng giải pháp, trùng từ khóa mục tiêu, cùng ngành, cùng ràng buộc, cùng ngôn ngữ khách), hiện tối đa 3 hồ sơ cũ để tham khảo WBS/báo giá. **Không tự áp số liệu sang hồ sơ mới.**

## Ràng buộc kỹ thuật

- **Che email / số điện thoại** trước khi gửi nội dung cho LLM.
- Giao diện web bằng **tiếng Việt**; nội dung gửi khách theo ngôn ngữ khách.
- Tiến độ từng bước AI hiển thị **realtime** trên web.
- **Unit test không bao giờ gọi LLM thật** — dùng mock.
- Số liệu luôn do code tính từ bảng chuẩn; AI không dựng định dạng file.

## Success đo được

- Demo trọn luồng với bộ hồ sơ mẫu **tiếng Nhật** trong **≤ 10 phút**.
- **100% requirement** trong file Excel được đánh giá (không sót).
- Mọi con số effort/giá **truy được về bảng chuẩn và công thức**.
- Proposal **không chứa số tiền** khi chưa duyệt giá.

## MVP (cốt lõi, phải có)

Xương sống chứng minh luận điểm "bản nháp trong vài phút, số không bịa, có người duyệt". Đề xuất cắt giảm so với bản đầu để demo ≤ 10 phút không bị vướng:

1. Nhập email/RFP + **code đọc Excel requirement** → danh sách requirement chính xác (presales xác nhận trước khi chạy).
2. AI đánh giá từng requirement (○/△/×/cần làm rõ, lô ≤ 40) + code kiểm tra mã duy nhất, không sót.
3. Bảng chuẩn YAML + **code tính** effort/giá (effort = bảng chuẩn × hệ số; rate card), hiển thị **dấu vết tính toán**.
4. **Hỏi lại tối đa 7 câu** — trả lời trên web, AI chạy tiếp. (Điểm khác biệt cốt lõi.)
5. WBS + effort + master schedule + báo giá → xuất **Excel có công thức**.
6. Proposal **Word** (template trung tính, ngôn ngữ khách).
7. Duyệt giá (chưa duyệt → proposal hiện `"[Presales điền]"`) + kiểm tra tự động trước khi duyệt.
8. 1–2 bộ hồ sơ mẫu giả lập (nạp 1 nút) + tiến độ từng bước realtime.

## Để sau (sau MVP)

- **Q&A sheet vòng với khách** — MVP chỉ trả lời trên web; xuất/nhập lại file Q&A để sau.
- **Điền ○/△/× vào đúng file Excel của khách** (giữ nguyên định dạng) — MVP chỉ hiện bảng đáp ứng trên web.
- **"Chạy lại từ bước cụ thể"** trong duyệt kỹ thuật — MVP: chạy lại từ bước WBS; cơ chế resume giữa pipeline để sau.
- **Slide PowerPoint (.pptx)** và **upload template riêng** của công ty.
- **Lịch sử hồ sơ + nhân bản**; **dự án tham chiếu** (4–6 mẫu Markdown) — giá trị thấp cho demo.
- **Phân tích source code `.zip`**; **AI trích requirement từ RFP** khi khách không gửi Excel (đánh dấu "cần xác nhận").
- **Gợi ý "hồ sơ tương tự"** (chấm điểm bằng code).
- Kho tri thức tự học / embedding / vector DB — **không bao giờ**.

## Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Bảng chuẩn là "chân lý": kiểm tra ±20% so với chính bảng đã sinh con số → vòng tròn, chỉ bắt lỗi hình thức | Cao | Coi ±20% là **cảnh báo**, không phải cổng chặn; giới hạn AI làm lại (≤ 2 lần), sau đó để người sửa |
| Chất lượng tiếng Nhật của LLM — demo chính là hồ sơ tiếng Nhật; sai nghĩa requirement = mất uy tín | Cao | Glossary thuật ngữ trong prompt; bắt buộc bước duyệt người; dự phòng: demo tiếng Việt + tiếng Nhật đơn giản |
| Parse Excel requirement của khách (merge cell, nhiều dòng tiêu đề, chú thích) — auto-detect dễ vỡ | Cao | MVP giới hạn mẫu chuẩn hóa + cho presales sửa mapping cột; báo lỗi rõ thay vì đoán |
| MVP quá to: 5 loại đầu ra + 2 cấp duyệt + cấu hình + lịch sử — thực chất là mini-product | Cao | Cắt theo mục "Để sau" ở trên |
| Vòng hỏi lại chặn tiến độ: khách không trả lời kịp hạn nộp | Trung bình | Cho presales tự trả lời theo "giả định rõ ràng" và đánh dấu; không bắt buộc chờ khách |
| "Code tính số" là ảo giác xác định: hướng giải pháp và hệ số do **AI chọn** → con số chỉ đáng tin bằng đầu vào | Trung bình | Hiển thị **dấu vết tính toán**: mỗi con số truy về bảng chuẩn + hệ số đã chọn |
| Người sửa WBS phá vỡ kiểm tra ±20% → mâu thuẫn tự do chỉnh vs cổng kiểm tra | Trung bình | Kiểm tra là cảnh báo; người duyệt override được nhưng phải ghi chú |
| Retry-loop tốn token/thời gian khi AI không qua kiểm tra | Trung bình | Unit test dùng mock LLM; giới hạn retry; degrade thành cảnh báo |
| Export file (giữ định dạng file khách, công thức Excel) lỗi vặt ngốn thời gian demo | Trung bình | Làm sớm, test bằng bộ mẫu thật từ đầu |