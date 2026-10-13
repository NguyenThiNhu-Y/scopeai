# Handoff — Review M7 → Developer

## Kết quả

- Review đã hoàn tất tại `docs/slices/M7/review.md`.
- Verdict: **CHANGES REQUIRED**.
- Không sửa code trong vai trò Reviewer.

## Findings ưu tiên

1. `backend/app/exporters/proposal_docx.py:6-18`: thiếu phụ lục WBS trong proposal Word.
2. `backend/app/services/export_service.py:40`: mọi export đều gọi PDF converter, làm Word/Excel
   phụ thuộc LibreOffice ngoài contract.
3. `backend/app/exporters/filename.py:12-14`: ngày filename hard-code `2026-10-10`.
4. `backend/app/services/export_service.py:37-39` và `backend/app/exporters/estimate_xlsx.py:17-18`:
   Gantt chưa có thanh theo range tuần và mốc thanh toán.
5. `backend/app/services/ja_check.py:24-29`: context gửi ja-check phụ trợ chưa đủ section/glossary/name.

## Yêu cầu bàn giao lại

- Bổ sung regression tests cho từng finding, đặc biệt WBS appendix, độc lập DOCX/XLSX khi thiếu
  LibreOffice, ngày filename được cố định ở service boundary và payment milestones/Gantt.
- Chạy lại acceptance commands khả dụng và cập nhật test report/fix log.
- Sau đó yêu cầu chạy lại bước Review M7.
