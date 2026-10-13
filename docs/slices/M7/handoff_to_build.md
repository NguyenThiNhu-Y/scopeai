# Handoff — Solution Architect → Build (M7 Xuất file bằng code)

| Thuộc tính | Giá trị |
|---|---|
| Từ | Solution Architect |
| Cho | Backend Dev, Frontend Dev, Cloud/Preview |
| Ngày | 2026-10-10 |
| Nguồn | `docs/slices/M7/spec.md`, `docs/04_architecture/`, `docs/05_roadmap/roadmap.md` §9, `docs/slices/M6/handoff_to_build.md`, `AGENTS.md` |

## 1. Deliverables bắt buộc

1. Bám contract M7 tại `api_contract.md` §10 và §12: Word, Excel, PDF, bundle ZIP; không thêm API
   nhập Q&A hoặc API PowerPoint.
2. Chạy ja-check rule-based trước export hồ sơ Nhật; LLM phụ trợ (nếu dùng) chỉ qua gateway/mock,
   retry tối đa 2, warning không chặn tải.
3. Sinh proposal Word deterministic theo vi/en/ja, có bìa, mục lục, `前提条件`/giả định và
   `スコープ外`/ngoài phạm vi; mọi số render từ backend, không từ client hay LLM.
4. Sinh Excel estimate có sheet WBS, báo giá, Gantt theo tuần và `Q&A`; tổng man-day/tổng tiền là
   công thức `SUM`, Q&A lấy từ câu hỏi đã persist để khách điền.
5. Sinh PDF từ Word bằng LibreOffice headless + font Noto CJK trong Preview.
6. Sinh ZIP gồm đúng Word/Excel/PDF, entry order/metadata deterministic, basename an toàn, không
   absolute path/file tạm/secret.
7. Áp dụng đúng price gate: chưa duyệt giá → `[Presales điền]` trong mọi artifact; không sửa
   quotation/WBS/schedule/status khi export; ghi `export_logs`.
8. FE có màn hình export, nút tải từng file/gói, panel ja-check warning và trạng thái loading/error;
   mọi request root-relative `/api`.

## 2. Contract không được phá vỡ

- `GET /api/bids/{id}/exports/proposal.docx`, `/estimate.xlsx`, `/proposal.pdf`, `/bundle.zip` trả
  binary đúng MIME và `Content-Disposition`.
- Header `X-Ja-Check-Result` chỉ là cảnh báo JSON URL-encoded; warning không biến thành HTTP fail.
- `estimate.xlsx` phải có Q&A sheet, nhưng nhập câu trả lời vẫn dùng máy hỏi M2; không tin dữ liệu
  client trong file export.
- Filename theo `<Khách>_<Dự án>_<Loại>_v<phiên bản>_<ngày>` sau normalize deterministic.
- Hồ sơ locked vẫn export; export không mở khóa. Errors theo envelope tiếng Việt khi trước khi
  render có lỗi resource/state.
- `X-Role`/`X-User` là actor authoritative cho audit; không dùng `by` từ body để giả mạo.

## 3. Luật bắt buộc

- Parser/exporter/filename/formula/Gantt/ZIP là code deterministic; LLM không sinh số nghiệp vụ.
- Không export số tiền trước approval; regression test phải kiểm tra nội dung file thực tế, không chỉ
  response metadata.
- B7 ja-check output phải structured; fixture bad schema retry ≤2 rồi fallback rule-based.
- Tất cả context LLM đã mask PII; fixture/sample fictional, ghi “DỮ LIỆU GIẢ LẬP”; không log key.
- Không gọi LLM cho Word/Excel/PDF/ZIP; chỉ ja-check phụ trợ, qua `LLMClient` duy nhất.
- Không thêm queue/vector DB/auth server/OCR service; không hardcode `localhost` ở FE.

## 4. Test gate

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

Fixture/gate phải chứng minh bộ 20 câu Nhật đạt ≥90%; Word/PDF mở được; Excel có `SUM`, Q&A và
Gantt theo tuần; bundle đúng 3 artifact; filename an toàn; hai lần export deterministic; chưa duyệt
không có số tiền; exporter không gọi LLM ngoài ja-check mock.

## 5. Preview evidence cần bàn giao

1. Hồ sơ Nhật: ja-check pass/warning hiển thị trước tải và warning vẫn cho tải.
2. Word có bìa/mục lục/locale/前提条件/スコープ外.
3. Excel có WBS, báo giá, Gantt tuần, Q&A; sửa man-day trong Excel làm SUM cập nhật.
4. PDF hiển thị tiếng Nhật không ô vuông trong image Preview.
5. ZIP có đúng Word/Excel/PDF, tên đúng, không path leak/file tạm.
6. Hồ sơ chưa duyệt: mọi artifact dùng `[Presales điền]`, không lộ số tiền thực.
7. vi/en: đúng ngôn ngữ tài liệu và không chạy ja-check.
8. Export log có kind, actor, price gate, ja-check; không thay đổi trạng thái nghiệp vụ.

## 6. Handover tiếp theo

Sau Build, chuyển Test/Review cùng danh sách file, migration/model note, test report, artifact mẫu
4 loại, kết quả kiểm tra formula/ZIP deterministic, ja-check report, price-gate evidence và ảnh
Preview. M8 nhận export logs/contract đã ổn định; không triển khai Settings hoặc PowerPoint trong
bước này.

**Task Slice Spec M7 complete. Awaiting prompt for the next role.**
