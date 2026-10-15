# Ghi chú thay đổi — Xuất file (Word / Excel / PDF / PowerPoint / Q&A) — 2026-10-15

Phạm vi: sửa các lỗi review phần xuất hồ sơ và thêm xuất PowerPoint (.pptx).
Kết quả kiểm tra: backend `pytest` **388 passed** (Python 3.11, `PYTHONUTF8=1`).
Frontend: không chạy được `npm ci` trên máy này (registry trả 403), nên chưa chạy `vitest`/`vite build`;
các file TS đã sửa không có lỗi type trong editor.

## 1. File thêm mới

| File | Nội dung |
|---|---|
| `backend/app/exporters/common.py` | Nhãn vi/en/ja dùng chung, định dạng tiền theo tiền tệ, nhãn phase/role/hợp đồng, helper cấp WBS, tổng man-day task lá, tổng hợp theo phase, danh sách tuần cho Gantt |
| `backend/app/exporters/xlsx_style.py` | Style Excel dùng chung: header, viền, độ rộng cột, tô màu dòng cha/tổng, ô trả lời vàng, màu phase |
| `backend/app/exporters/proposal_pptx.py` | **Xuất PowerPoint 16:9**: bìa, nội dung, các section (tự chia slide), giả định/ngoài phạm vi, tổng hợp effort, Gantt vẽ bằng shape sửa được (thanh theo phase, mốc thanh toán hình thoi, vạch hạn khách), báo giá có cổng giá |
| `backend/tests/test_export_pptx_and_api.py` | Test PPTX, endpoint `.pptx`, bundle 4 file, Word/Excel không phụ thuộc PDF, giá đã duyệt được định dạng, Q&A sheet có hướng dẫn + import đọc đúng sheet |
| `docs/EXPORT_CHANGES_2026-10-15.md` | File ghi chú này |

## 2. File sửa

### Backend

| File | Thay đổi |
|---|---|
| `backend/app/exporters/proposal_docx.py` | Viết lại: khổ A4, font theo ngôn ngữ (Yu Gothic cho ja), header công ty/dự án + footer số trang (trừ trang bìa), bìa có "御中" cho ja, **mục lục là field TOC thật** (có sẵn nội dung để PDF vẫn hiển thị), gạch đầu dòng trong section, mục **Giả định / Ngoài phạm vi**, báo giá theo phase khi đã duyệt, **Phụ lục A – WBS & effort**, **Phụ lục B – Lịch tổng thể + mốc thanh toán** |
| `backend/app/exporters/estimate_xlsx.py` | Viết lại 5 sheet. **WBS**: phân cấp, phase, vai trò, requirement, `SUM` + `SUMIF` theo phase. **Báo giá**: dòng theo vai trò + overhead/contingency/vận hành/điều chỉnh, `SUM` khớp đúng `grand_total`, theo phase, mốc thanh toán (công thức `ROUND`), định dạng tiền tệ. **Lịch Gantt**: cột theo tuần, tô màu theo phase, mốc thanh toán ◆ và hạn khách ▲. **Q&A**: nhãn dễ đọc thay enum, cột trả lời vàng. **Tóm tắt**: công thức tham chiếu sang tổng WBS/Báo giá |
| `backend/app/exporters/pdf.py` | Bản PDF dự phòng (khi không có LibreOffice): font Unicode TTF nếu có, font CID tiếng Nhật có sẵn của reportlab, giữ heading/bullet/bảng/ngắt trang theo đúng thứ tự |
| `backend/app/exporters/filename.py` | Ngày trong tên file = **ngày xuất thực tế** (bỏ `2026-10-10` cố định); thêm `content_disposition()` (ASCII + `filename*=UTF-8''`) |
| `backend/app/services/export_service.py` | **Chỉ sinh file được yêu cầu** (tải Word/Excel/PPTX không còn gọi chuyển PDF); dùng `assumptions_phrased` / `scope_out_phrased` (trước đây luôn là `[]`); giá định dạng theo tiền tệ; **chưa duyệt giá thì loại bỏ mọi số tiền khỏi dữ liệu** trước khi render; truyền lịch, mốc thanh toán, hạn khách, tên công ty; bundle gồm 4 file theo thứ tự cố định |
| `backend/app/services/settings_service.py` | Thêm `get_optional_setting()`; template mặc định ghi đúng là "Mẫu trung tính (sinh bằng code)" thay vì tên file không tồn tại |
| `backend/app/api/routers/exports.py` | Thêm `GET /api/bids/{id}/exports/proposal.pptx`; bundle 4 file; dọn code (`json` import, bỏ `__import__`); `requirements.xlsx` dùng header an toàn cho tên file tiếng Nhật (trước đây có thể lỗi header) |
| `backend/app/api/routers/questions.py` | Q&A sheet: style header/cột/wrap, cố định dòng tiêu đề, **khóa sheet trừ cột Trả lời**, thêm sheet hướng dẫn theo ngôn ngữ khách, tên file theo quy tắc chung, ghi `export_logs` (`qa_xlsx`); import ưu tiên sheet `Q&A` |
| `backend/requirements.txt` | Thêm `python-pptx` |
| `backend/tests/test_export_excel_formulas.py` | Cập nhật theo layout mới + test Gantt tuần/mốc, báo giá khớp tổng, Q&A, WBS rỗng |
| `backend/tests/test_export_price_gate.py` | Cập nhật layout mới + test không lộ giá ở Excel/PPTX khi chưa duyệt |
| `backend/tests/test_export_word.py` | Thêm test TOC field, bullet, header, phụ lục, giá đã duyệt có tiền tệ |
| `backend/tests/test_export_headers.py` | Kiểm tra `Content-Disposition` hỗ trợ tên Unicode |

### Frontend

| File | Thay đổi |
|---|---|
| `frontend/src/api/types.ts` | `ExportKind` thêm `'pptx'` |
| `frontend/src/api/client.ts` | Đường dẫn `/exports/proposal.pptx`; đọc tên file từ `filename*=UTF-8''` (giữ tên tiếng Nhật/Việt) |
| `frontend/src/components/ExportButtons.tsx` | Nút "Slide PowerPoint"; gói đầy đủ ghi "4 file" |
| `frontend/src/pages/SettingsPage.tsx` | Trang Cài đặt hiển thị cả template PowerPoint |

### Tài liệu

| File | Thay đổi |
|---|---|
| `docs/04_architecture/api_contract.md` | §10.4 bundle 4 file; §10.0b Q&A sheet; thêm §10.6 PPTX, §10.7 quy tắc chung; §12 cập nhật PowerPoint |
| `docs/05_roadmap/roadmap.md` | Ghi chú PowerPoint đã được đưa vào phạm vi |

## 3. File xóa

Không xóa file nào.

## 4. Còn hạn chế / chưa làm

- Tên task WBS chỉ có `name_vi` trong DB → file gửi khách en/ja vẫn hiển thị tên task tiếng Việt (cần thêm trường tên theo ngôn ngữ khách; không dịch bằng LLM lúc xuất).
- Sheet nội bộ trong `estimate.xlsx` vẫn dùng nhãn tiếng Việt (theo contract §10.5).
- Chưa có logo (chưa có asset/upload logo); header dùng tên công ty từ Cài đặt.
- Preview (`python:3.11-slim`) không có LibreOffice/font Unicode → PDF dùng bản dự phòng; tiếng Nhật hiển thị bằng font CID, chữ có dấu tiếng Việt cần cài `fonts-dejavu-core` (hoặc LibreOffice + `fonts-noto-cjk`) để hiển thị đầy đủ.
- Finding MEDIUM cũ về ngữ cảnh ja-check (`ja_check.py`) chưa xử lý — ngoài phạm vi lần này.
- Chưa kiểm tra trực quan trong app đang chạy (không có trình duyệt/Preview trong phiên này); `npm ci` bị chặn nên chưa chạy test/build frontend.
- Test `test_dot14_backend.py::test_tokai_pipeline_runs_end_to_end` đôi khi lỗi do thời gian khi chạy cả bộ (đã có từ trước, không liên quan phần xuất file).
