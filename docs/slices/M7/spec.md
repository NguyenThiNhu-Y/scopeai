# Đặc tả Slice — M7 Xuất file bằng code

| Thuộc tính | Giá trị |
|---|---|
| Tên tài liệu | Đặc tả milestone M7 — Kiểm tra tiếng Nhật và xuất Word/Excel/PDF/gói ZIP |
| Phiên bản | 1.0 |
| Ngày | 2026-10-10 |
| Trạng thái | Sẵn sàng cho bước Build |
| Vai trò | Solution Architect |
| Nguồn | `AGENTS.md`, `docs/05_roadmap/roadmap.md` §9, `docs/04_architecture/` (5 file), `docs/slices/M6/spec.md`, `docs/slices/M5/spec.md`, `docs/03_requirements/srs.md` FR-025/043/050–052 |

> Mọi tên khách, dự án và dữ liệu minh họa trong slice này là hư cấu. Các con số như giới hạn
> công thức, số câu fixture và mã phiên bản là ràng buộc kỹ thuật, không phải báo giá khách hàng.
> Handoff nền `docs/05_roadmap/handoff_to_build.md` không tồn tại; nguồn handoff được dùng là
> `docs/04_architecture/handoff_to_dev.md` và handoff M6.

## 1. Phạm vi

### 1.1 Slice này giao

M7 là vertical slice từ hồ sơ đã có proposal/WBS/schedule/quotation/evaluations của M5–M6 đến
các file tải xuống bằng code, deterministic:

1. Kiểm tra tiếng Nhật trước khi xuất hồ sơ `customer_language=ja`: rule-based đối chiếu glossary,
   phát hiện Latin không thuộc whitelist và kiểm tra đúng tên khách/công ty; có thể gọi LLM phụ trợ
   qua gateway duy nhất để đánh giá ngữ cảnh nghi ngờ. Cảnh báo không chặn xuất.
2. Xuất proposal Word `.docx` theo `customer_language` (vi/en/ja), template trung tính có bìa,
   mục lục, nội dung draft, mục giả định và phạm vi không bao gồm. Các trường số liệu do backend
   render từ nguồn đã persist.
3. Xuất Excel estimate `.xlsx` gồm WBS, tổng man-day, báo giá, lịch Gantt theo tuần và sheet
   `Q&A` để khách điền. Tổng man-day và tổng tiền là công thức Excel; file giữ cổng giá.
4. Xuất PDF `.pdf` từ proposal Word bằng công cụ đã chốt, có font CJK cho tiếng Nhật.
5. Cho tải từng file hoặc gói `.zip`; tên mọi file theo `<Khách>_<Dự án>_<Loại>_v<phiên bản>_<ngày>`.
   Chuỗi tên được chuẩn hóa an toàn và deterministic.
6. Ghi `export_logs` với loại file, kết quả ja-check, cổng giá, actor và thời điểm; không ghi secret
   hay đường dẫn nội bộ ra response.

### 1.2 Không thuộc M7

- Không cho LLM tính hoặc tự điền effort, man-day, ngày lịch, giá, tỷ giá, thuế hay công thức.
- Không sửa WBS, schedule, quotation, approval, price gate hay bảng chuẩn; M7 chỉ đọc các snapshot
  và kết quả M5–M6 để render.
- Không nhận Excel Q&A upload làm nguồn sự thật và không thêm endpoint nhập Q&A; presales nhập lại
  bằng máy hỏi M2 hiện có.
- Không xuất PowerPoint. Theo roadmap/SRS, PPTX ngoài MVP và không có endpoint contract.
- Không biến cảnh báo tiếng Nhật thành lỗi chặn; không gửi binary file hoặc toàn văn RFP vào LLM.
- Không thêm auth server, queue, vector DB, dịch vụ OCR, kho file cloud hoặc API ngoài contract.

## 2. Frozen API contract subset

Contract gốc là `docs/04_architecture/api_contract.md`; trong lúc soạn spec đã cập nhật contract
trước khi dùng endpoint mới: ghi chú reconcile M7, §10.4 bundle, §10.5 sheet Q&A và ánh xạ §12.

### 2.1 Draft proposal dùng lại từ M5

- `GET /api/bids/{id}/proposal` trả `sections`, `assumptions_phrased`, `scope_out_phrased`,
  `price_gate`, `editable`.
- `PUT /api/bids/{id}/proposal` chỉ nhận các trường văn bản `sections`; backend không tin số tiền,
  man-day, ngày hoặc trạng thái do client gửi. Lỗi dùng envelope chuẩn.

### 2.2 `GET /api/bids/{id}/exports/proposal.docx`

- Response `200`, content type Word Open XML, `Content-Disposition: attachment`.
- Với `ja`, chạy ja-check trước; header `X-Ja-Check-Result` chứa JSON URL-encoded gồm `pass|warning`
  và `issues[]`. Warning hiển thị trên UI nhưng không chặn tải.
- Chưa duyệt giá: mọi vùng tiền trong file là `[Presales điền]`; đã duyệt: render quotation snapshot.

### 2.3 `GET /api/bids/{id}/exports/estimate.xlsx`

- Response `200`, content type Excel Open XML.
- Workbook tối thiểu có các sheet `Tóm tắt`, `WBS`, `Báo giá`, `Lịch Gantt`, `Q&A` (tên sheet có
  thể bản địa hóa hạn chế nhưng phải ổn định trong cùng locale).
- Tổng man-day dùng `=SUM(...)`; tổng báo giá dùng công thức tương ứng. Backend không ghi cached
  result giả làm nguồn sự thật.
- `Lịch Gantt` lấy `schedule.tasks[]`, nhóm theo tuần và đánh dấu mốc thanh toán/hạn nộp.
- `Q&A` lấy từ bảng `questions`, các cột: mã câu hỏi, vòng, câu hỏi, lý do tiếng Việt, ảnh hưởng,
  trả lời, là giả định, trạng thái.

### 2.4 `GET /api/bids/{id}/exports/proposal.pdf`

- Response `200`, content type PDF.
- Sinh từ Word bằng LibreOffice headless; Preview phải có font Noto CJK cho hồ sơ Nhật.
- Nội dung và cổng giá phải giống bản Word của cùng lần render.

### 2.5 `GET /api/bids/{id}/exports/bundle.zip`

- Response `200`, content type ZIP.
- Gói proposal `.docx`, estimate `.xlsx`, proposal `.pdf`; nếu chưa có artifact thì backend sinh
  deterministic trước khi đóng gói.
- Entry không chứa file tạm, secret, absolute path hoặc dữ liệu ngoài hồ sơ.
- Tên ZIP và entry tuân theo quy tắc tên file; thứ tự entry ổn định để kiểm thử deterministic.

### 2.6 Quy tắc chung

- Tất cả path root-relative `/api`; lỗi theo envelope tiếng Việt.
- Header `X-Role`/`X-User` là actor cho audit; body không được giả mạo actor.
- Hồ sơ `locked=true` vẫn được export; export không mở khóa và không mutation nghiệp vụ.
- `GET /api/bids/{id}/exports/*` không gọi LLM, ngoại trừ một lượt ja-check phụ trợ khi cần và phải
  qua `LLMClient`/mock theo contract.

## 3. LLM steps touched

### 3.1 B7 ja-check

Input đã chuẩn hóa: nội dung các section sẽ xuất, glossary, tên công ty/khách hàng. Rule-based chạy
trước; chỉ các điểm nghi ngờ mới được gửi gateway, sau khi mask PII và giới hạn context.

Output frozen:

```json
{
  "result": "pass",
  "issues": [
    {
      "severity": "warning",
      "section": "solution_overview",
      "message_vi": "Thuật ngữ chưa khớp glossary.",
      "suggestion_ja": "用語を glossary の表記に合わせてください。",
      "source": "glossary"
    }
  ]
}
```

Validation: `pass` thì `issues=[]`; issue đủ `severity|section|message_vi|suggestion_ja|source`;
source thuộc `latin|glossary|name|llm_context`; LLM sai schema retry tối đa 2, sau đó bỏ qua
phần phụ trợ và giữ cảnh báo rule-based. Bộ 20 câu phải phát hiện ít nhất 90% lỗi cố ý.

### 3.2 Các bước không gọi LLM

Word/Excel/PDF/ZIP, đặt tên file, mục lục, công thức SUM, Gantt theo tuần, sheet Q&A, price gate,
đọc quotation/schedule và ghi export log đều là code deterministic. `proposal_draft` đã có từ B6;
M7 không gọi lại B6 chỉ để xuất.

### 3.3 Mock responses bắt buộc

| Fixture | Mục đích |
|---|---|
| `ja_check_pass` | Văn bản Nhật hợp lệ, không issue |
| `ja_check_warning` | Có Latin/glossary/name issue; vẫn tải được |
| `ja_check_bad_schema` | Retry tối đa 2 rồi fallback rule-based |
| `ja_check_context_clean` | LLM phụ trợ không tự tạo số liệu |

Tất cả fixture tiếng Việt/Nhật hư cấu, không email, điện thoại, API key, tên công ty thật hay số
tiền khách hàng.

## 4. Backend và frontend tasks

### 4.1 Backend — file-level

| File | Hành động | Nội dung |
|---|---|---|
| `backend/app/services/ja_check.py` | Tạo/cập nhật | Rule Latin, glossary, tên; schema output; fallback và ngưỡng test |
| `backend/app/exporters/filename.py` | Tạo | Chuẩn hóa tên khách/dự án/loại/version/date, locale-independent |
| `backend/app/exporters/proposal_docx.py` | Tạo/cập nhật | Bìa, mục lục, section, assumptions/scope-out, price gate, locale |
| `backend/app/exporters/estimate_xlsx.py` | Tạo | Sheets WBS/quotation/Gantt/Q&A; SUM formulas; định dạng ổn định |
| `backend/app/exporters/pdf.py` | Tạo/cập nhật | DOCX→PDF, kiểm tra subprocess lỗi rõ, font CJK |
| `backend/app/exporters/bundle.py` | Tạo | Sinh/đọc 3 artifact, ZIP entry deterministic, không path leak |
| `backend/app/services/export_service.py` | Tạo | Orchestrate read-only render, ja-check, price gate, log export |
| `backend/app/api/routers/exports.py` | Tạo | 4 GET endpoints theo contract, streaming/download response |
| `backend/app/schemas/api_schemas/export.py` | Tạo | Metadata/header nội bộ, ja-check và filename types |
| `backend/app/models/export_log.py` | Cập nhật | Enum thêm `bundle_zip` nếu cần; tương thích migration |
| `backend/app/models/__init__.py` | Cập nhật | Đăng ký model/export metadata |
| `backend/app/main.py` hoặc router registry | Cập nhật | Mount exports router dưới `/api/bids/{id}/exports` |
| `backend/tests/test_japanese_check.py` | Tạo/cập nhật | 20 câu, recall ≥90%, fallback |
| `backend/tests/test_export_word.py` | Tạo | DOCX mở được, bìa/mục lục/section |
| `backend/tests/test_export_word_language.py` | Tạo | vi/en/ja đúng ngôn ngữ customer |
| `backend/tests/test_export_excel_formulas.py` | Tạo | SUM, sheets, Gantt tuần, Q&A |
| `backend/tests/test_export_deterministic.py` | Tạo | cùng input → bytes/entry order ổn định |
| `backend/tests/test_export_price_gate.py` | Tạo | chưa duyệt không lộ số tiền; đã duyệt render snapshot |
| `backend/tests/test_export_bundle.py` | Tạo | 3 file, tên đúng, không path/secret/tạm |
| `backend/tests/fixtures/m7_*` | Tạo | dữ liệu bid M5/M6 giả lập và 20 câu Nhật |

### 4.2 Frontend — file-level

| File | Hành động | Nội dung |
|---|---|---|
| `frontend/src/api/client.ts` | Cập nhật | download helpers cho 4 endpoint, root-relative, filename từ header |
| `frontend/src/api/types.ts` | Cập nhật | `JaCheckResult`, export metadata, `ExportKind` |
| `frontend/src/pages/ExportPage.tsx` | Tạo/cập nhật | chọn từng file/gói ZIP, trạng thái đang tải/lỗi/thành công |
| `frontend/src/components/JaCheckPanel.tsx` | Tạo | pass/warning, issue tiếng Việt + gợi ý Nhật, không chặn |
| `frontend/src/components/ExportButtons.tsx` | Tạo | 4 action, disable đúng lúc, không hardcode host |
| `frontend/src/App.tsx` | Cập nhật | route Export và liên kết từ BidDetail |
| `frontend/src/test/m7Fixtures.ts` | Tạo | response/header giả lập, không số tiền thật |
| `frontend/src/pages/ExportPage.test.tsx` | Tạo | tải từng file, bundle, warning, lỗi actionable |

### 4.3 Contract chia sẻ

- Backend là nguồn sự thật cho nội dung, số liệu, trạng thái duyệt, ja-check và filename; FE chỉ gọi
  endpoint và lưu file tải xuống.
- FE không tự tạo `.docx/.xlsx/.pdf/.zip`, không tự tính SUM/Gantt, không parse binary để quyết định
  trạng thái price gate.
- FE hiển thị warning từ header/API theo tiếng Việt; customer-facing text trong file theo locale.
- Mọi request dùng `/api/...`; không có `http://localhost` trong client/export UI.

## 5. Tiêu chí chấp nhận

### 5.1 Shell commands phải exit 0

```bash
cd backend && pytest -q tests/test_japanese_check.py
cd backend && pytest -q tests/test_export_word.py
cd backend && pytest -q tests/test_export_word_language.py
cd backend && pytest -q tests/test_export_excel_formulas.py
cd backend && pytest -q tests/test_export_deterministic.py
cd backend && pytest -q tests/test_export_price_gate.py
cd backend && pytest -q tests/test_export_bundle.py
cd backend && pytest -q
cd frontend && npm run build
make test
make quality-gate
```

Các test phải chứng minh: Word mở được; vi/en/ja đúng locale; 20 câu Nhật đạt ≥90%; Excel có SUM,
Q&A và Gantt tuần; PDF tạo được; xuất hai lần deterministic; bundle có đúng ba artifact; tên đúng
quy tắc; chưa duyệt không có số tiền thực; export không gọi LLM ngoài ja-check mock phụ trợ.

### 5.2 Kịch bản thủ công trên Preview

1. Mở hồ sơ giả lập khách Nhật đã qua M5/M6, có proposal draft, WBS 3 cấp, quotation và schedule.
   Kỳ vọng màn hình Export hiển thị đúng các lựa chọn Word, Excel, PDF, ZIP.
2. Chọn Word. Kỳ vọng panel ja-check xuất hiện trước tải với `pass` hoặc warning; warning không chặn.
   File mở được, có bìa, mục lục, proposal tiếng Nhật, `前提条件`, `スコープ外`.
3. Cố ý sửa một section chứa thuật ngữ Latin/sai glossary rồi xuất lại. Kỳ vọng issue hiển thị rõ,
   file vẫn tải được; filename có khách/dự án/loại/version/ngày đã chuẩn hóa.
4. Mở Excel. Kỳ vọng có WBS, báo giá, lịch Gantt theo tuần và Q&A; thay man-day một dòng trong
   Excel thì ô tổng cập nhật theo `SUM`, không phải giá trị hard-code. Q&A có câu chưa trả lời để
   khách điền.
5. Xuất PDF. Kỳ vọng mở được, nội dung/locale tương ứng Word, chữ Nhật không bị ô vuông trong
   Preview có font CJK.
6. Xuất ZIP. Kỳ vọng tải được một gói có đúng Word/Excel/PDF, entry order ổn định và tên nhất quán;
   không có file tạm/absolute path.
7. Dùng hồ sơ chưa duyệt giá. Kỳ vọng cả Word/Excel/PDF/ZIP hiển thị `[Presales điền]` và không
   lộ số tiền thực; WBS/schedule vẫn được hiển thị theo contract nhưng không tự tạo giá.
8. Xuất cùng một hồ sơ hai lần. Kỳ vọng nội dung/cấu trúc/tên ổn định; export log ghi đủ loại, actor,
   price gate và ja-check.
9. Kiểm tra hồ sơ `customer_language=vi` và `en`. Kỳ vọng không chạy ja-check tiếng Nhật, file
   customer-facing đúng locale, UI/lỗi vẫn tiếng Việt.

### 5.3 Test các rule AGENTS.md liên quan M7

| Rule | Test/kiểm tra | Assert |
|---|---|---|
| 1 — Không bịa số | `test_export_excel_formulas.py`, `test_export_price_gate.py` | Số lấy từ DB/code; SUM là formula; LLM không chứa tiền/man-day/ngày |
| 2 — JSON schema | `test_japanese_check.py` | ja-check mock sai schema retry ≤2 rồi fallback rõ |
| 3 — Một gateway | gateway call-count test | Chỉ ja-check phụ trợ dùng `LLMClient`; exporter không gọi provider trực tiếp |
| 4 — Hỏi thay vì đoán | `test_export_qna.py`/Preview | Q&A phản ánh câu hỏi chưa trả lời; không tự điền câu trả lời/giả định |
| 5 — Price gate | `test_export_price_gate.py` + Preview | Chưa duyệt mọi artifact dùng placeholder, không có số tiền |
| 6 — Privacy | prompt capture ja-check | Context đã mask PII; fixture fictional; không log API key |
| 7 — Ngôn ngữ | `test_export_word_language.py` | File theo vi/en/ja; UI và lỗi tiếng Việt |
| 8 — Done proven | toàn bộ §5.1 + Preview | Automated tests và click-through pass |
| 9 — Đơn giản | dependency/review gate | Không queue/vector DB/auth server/OCR service |
| 10 — Root-relative | scan frontend | Tất cả download qua `/api`, không hardcode localhost |

## 6. Test data

Tất cả ghi rõ `DỮ LIỆU GIẢ LẬP`, không tên thật/PII thật và không đặt API key.

| Path | Nội dung |
|---|---|
| `samples/m7_fake_bid.json` | Bid Nhật giả lập đã có proposal/WBS/schedule/quotation/evaluation |
| `samples/m7_fake_bid_vi.json` | Bid Việt giả lập cho locale và currency display |
| `samples/m7_fake_bid_en.json` | Bid Anh giả lập cho locale |
| `samples/m7_japanese_cases.json` | 20 câu Nhật: câu chuẩn và lỗi Latin/glossary/name cố ý |
| `backend/tests/fixtures/m7_export_expected.py` | expected sheets, formulas, filenames, price-gate assertions |
| `backend/tests/fixtures/m7_ja_check.py` | pass/warning/bad-schema mock fixtures |
| `frontend/src/test/m7Fixtures.ts` | mock API/header/download responses |

Không cần commit file runtime trong `data/exports/`; test tạo thư mục tạm riêng.

## 7. Rủi ro và bàn giao

| Rủi ro | Mức | Giảm thiểu/bàn giao |
|---|---|---|
| LibreOffice hoặc Noto CJK thiếu trong Preview | Cao | Infra xác nhận image trước smoke test; PDF failure phải báo hành động được |
| Excel formula bị thư viện ghi thành giá trị | Cao | assert cell bắt đầu bằng `=SUM(` và mở lại workbook kiểm tra |
| ZIP không deterministic do timestamp/entry order | Trung bình | chuẩn hóa metadata ZIP và thứ tự entry trong test |
| Filename có ký tự Unicode/path traversal | Cao | allowlist/normalize basename, test tên Nhật và ký tự `/\\:*?` |
| Proposal chưa duyệt lộ giá qua metadata/cache | Cao | render price gate ở service; test cả bytes và text extraction |
| Cảnh báo ja-check làm người dùng tưởng bị chặn | Trung bình | UI ghi rõ “Cảnh báo — vẫn có thể xuất”; test warning path |

Build phải bàn giao cho Test/Review: danh sách file thay đổi, kết quả mọi command, artifact mẫu của
4 loại, checksum hoặc cấu trúc entry deterministic, ảnh Preview, ja-check report, chứng cứ price gate
và log export. Không triển khai Settings/M8 hoặc PowerPoint trong slice này.

**Slice Spec M7 hoàn tất. Handoff cho Build ở `docs/slices/M7/handoff_to_build.md`.**
