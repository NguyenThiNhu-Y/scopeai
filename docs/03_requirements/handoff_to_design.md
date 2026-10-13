# Handoff — BA → Solution Architect & PM

| Thuộc tính | Giá trị |
|---|---|
| Từ | Business Analyst (bước revise SRS) |
| Cho | Solution Architect, Project Manager |
| Ngày | 2026-10-09 |
| Nguồn | `docs/03_requirements/srs.md` (v1.1), `docs/03_requirements/srs_review.md` (18 MUST-FIX + 18 SHOULD-FIX đã áp dụng) |

---

## 1. Phạm vi cuối cùng (MVP)

**29 FR** (27 cũ + **FR-007** danh sách/mở lại hồ sơ + **FR-025** kiểm tra tiếng Nhật), 11 NFR, 13 BR, 11 UC, 28 US. Tất cả FR đều **Must have** ngoại trừ FR-004 (Should have).

| Module | Nội dung | FR |
|---|---|---|
| A — Hồ sơ & tiếp nhận | Tạo hồ sơ, đính kèm/đọc file (nhiều sheet, mã nội bộ), xác nhận đầu vào, hồ sơ mẫu giả lập, **danh sách hồ sơ** | FR-001..007 |
| B — Hỏi làm rõ | Dừng & hỏi ≤ 7 câu, tối đa 2 vòng; trả lời trên web / giả định | FR-010, FR-011 |
| C — Phân tích | Đánh giá ◎/○/△/× (+ 要確認), mã đúng một lần, hướng giải pháp, tiến độ realtime + resume, **kiểm tra tiếng Nhật** | FR-020..023, FR-025 |
| D — Ước lượng | Effort từ bảng chuẩn (midpoint ±20%), hệ số có trần, WBS + PM/QA, dấu vết, master schedule (hạn nộp, nghỉ lễ) | FR-030..034 |
| E — Báo giá & duyệt | Báo giá 見積書-chuẩn, duyệt kỹ thuật (cổng), duyệt giá (khóa, từ chối, người duyệt ≠ người tạo), cổng giá, kiểm tra trước duyệt | FR-040..044 |
| F — Xuất hồ sơ | Proposal Word (Giả định + スコープ外), Excel có công thức, xuất bằng code | FR-050..052 |
| G — Bảng chuẩn | YAML + Cài đặt (validate toàn vẹn), bất biến hồ sơ đã duyệt | FR-060, FR-061 |

**Ngoài MVP (không làm):** Q&A sheet vòng, điền thẳng file khách, chạy lại từ bước tùy ý, PPTX/template riêng, lịch sử + nhân bản, phân tích .zip, AI trích RFP, gợi ý hồ sơ tương tự, vector DB, xác thực nâng cao. (Xem §8.2 SRS.)

---

## 2. Business rules then chốt (bắt buộc thiết kế phải tôn trọng)

1. **BR-01** — LLM không bao giờ xuất man-day/giá/ngày; mọi con số do code tính từ bảng chuẩn. Con số từ LLM không được có đường đi vào tài liệu gửi khách (văn bản AI soạn thì được).
2. **BR-02** — Output LLM JSON theo schema; retry ≤ 2; lỗi schema → fail rõ; lỗi ngữ nghĩa (mã trùng, ±20%) → cảnh báo.
3. **BR-03** — Một LLM gateway duy nhất, có mock; CI/test không gọi LLM thật.
4. **BR-04** — Hỏi thay vì đoán; ≤ 7 câu/vòng, ≤ 2 vòng; không tạo con số khi "Chờ làm rõ".
5. **BR-05** — Cổng giá: chưa duyệt → `[Presales điền]`.
6. **BR-11** — Hồ sơ đã duyệt giá bất biến + **khóa** (FR-042.4): mọi thay đổi phải mở khóa và duyệt lại.
7. **BR-12** — ±20% so với **midpoint** là cảnh báo; override phải ghi chú.
8. **BR-13** — Mỗi mã requirement đúng một lần trong kết quả đánh giá.
9. **Mới:** người duyệt giá ≠ người tạo hồ sơ (FR-042.2); cổng duyệt kỹ thuật trước duyệt giá hoặc bỏ qua kèm lý do (FR-044).

---

## 3. Rủi ro hàng đầu (design phải giải quyết)

| # | Rủi ro | Mức | Yêu cầu liên quan |
|---|---|---|---|
| R1 | **Chất lượng tiếng Nhật** — sai nghĩa requirement = mất uy tín với khách Nhật (beachhead) | Cao | FR-025 (kiểm tra trước xuất), NFR-004 |
| R2 | **Latency/cost LLM** — 235 requirement, lô ≤ 40 → ≥ 6 lô + retry; ngân sách ≤ 15 phút/bản nháp | Cao | FR-020, FR-023, NFR-001, NFR-003 |
| R3 | **Đọc file Excel thật** — nhiều sheet, cột 番号 là công thức, merge cell, không có cột mã | Cao | FR-003.2/.4/.6 |
| R4 | **Toàn vẹn con số** — effort/giá phải truy về bảng chuẩn; đổi bảng chuẩn không đổi hồ sơ đã duyệt | Cao | FR-033, FR-061, BR-11 |
| R5 | **Khóa hồ sơ sau duyệt** — sửa WBS sau duyệt phải mở khóa + duyệt lại (tránh phá bất biến) | Trung bình | FR-042.4, FR-061 |
| R6 | **Resume pipeline** — timeout/crash giữa chừng phải chạy lại từ bước lỗi | Trung bình | FR-023 |
| R7 | **Segregation of duties** — vai trò chọn tay nhưng phải chặn tự duyệt | Trung bình | FR-042.2, mục 3 |

---

## 4. Câu hỏi mở — design phải quyết định

1. **Lưu trữ bảng chuẩn:** FR-060 nói "file YAML trong repo" nhưng sửa trên web — cần quyết định: bảng chuẩn runtime nằm ở DB/file nào, repo là nguồn mặc định? Cơ chế lưu từ trang Cài đặt (ghi file, snapshot, rollback)?
2. **Persist pipeline (FR-023):** cơ chế lưu từng bước và resume — schema DB cho trạng thái bước, dữ liệu trung gian (đánh giá lô, WBS)? Cần giữ bao lâu?
3. **Snapshot WBS (FR-041.2):** lưu snapshot dạng gì (bản sao JSON?), hiển thị khác biệt trước/sau ở mức nào?
4. **Khóa hồ sơ (FR-042.4):** khóa ở tầng dữ liệu hay chỉ UI? Ai được mở khóa? Audit log khi mở khóa?
5. **Real-time tiến độ (FR-023):** polling hay SSE/WebSocket? (SRS chỉ yêu cầu cập nhật ≤ 5 giây.)
6. **Kiểm tra tiếng Nhật (FR-025):** dùng LLM (gọi lại gateway) hay rule-based + LLM kết hợp? Chi phí thêm bao nhiêu lần gọi?
7. **Excel xuất có công thức (FR-051):** thư viện sinh .xlsx giữ công thức; PDF từ Word tiếng Nhật — font kanji, chuyển đổi bằng gì?
8. **Tiền tệ:** web nội bộ hiển thị giá bằng tiền tệ nào khi hồ sơ có tỉ giá đa chiều? (FR-051 quy định tiền tệ xuất theo ngôn ngữ khách.)
9. **Trần hệ số (FR-031):** giá trị trần mặc định ban đầu là bao nhiêu (cấu hình, cần số giả lập hợp lý)?
10. **Overhead PM 10% / BrSE 15% (FR-040):** áp dụng trên phần nào (toàn bộ man-day hay chỉ phần offshore)? Cần số giả lập cụ thể trong bảng chuẩn.

---

## 5. Ghi chú cho PM

- **Milestone gợi ý:** (1) Nền tảng: hồ sơ + đọc file + danh sách hồ sơ (FR-001..007); (2) Pipeline AI: hỏi làm rõ + đánh giá + hướng giải pháp + resume (FR-010..023, FR-025); (3) Ước lượng: effort/WBS/schedule (FR-030..034); (4) Báo giá + duyệt + khóa (FR-040..044); (5) Xuất + bảng chuẩn (FR-050..061).
- **"Done" = test tự động pass + chạy được trong Preview** (BR-08). Mọi phép tính phải có unit test với dữ liệu mẫu (NFR-006).
- **Demo S-01:** trọn luồng với hồ sơ mẫu tiếng Nhật ≤ 10 phút — cần bộ hồ sơ mẫu giả lập chất lượng (FR-006) và dữ liệu giả lập sát mặt bằng thị trường, ghi rõ "giả lập".
- **Bộ test PII** (NFR-002) và **bộ mẫu tiếng Nhật** (FR-025) cần được xây sớm ở milestone 1–2.
- **Câu hỏi mở mục 4** nên chốt trước khi bắt đầu milestone 1–2; các mục 7–10 ảnh hưởng milestone 3–4.

---

**Task BA Revise complete. Awaiting prompt for the next role.**