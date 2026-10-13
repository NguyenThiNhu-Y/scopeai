# Đợt 1 — Review UI

## Phạm vi và workflow

Đợt 1 được đối chiếu với mục 3, mục 4, các tiêu chí “Xong khi” tương ứng trong
`docs/ui/review_ui_tung_man.md`, `AGENTS.md`, ảnh mẫu/ảnh hiện tại được nêu trong tài liệu,
và các handoff:

1. `frontend-dev`: Bước 1, Màn Tạo hồ sơ.
2. `tester`: luồng Preview `Dùng bộ này → Phân tích → Chờ làm rõ`.
3. `frontend-dev`: Bước 2, Khung trang hồ sơ.
4. `tester`: kiểm tra runtime/UI Bước 2.
5. `reviewer`: đối chiếu và kết luận.

Review này không sửa source code và không coi source inspection là bằng chứng thay thế cho
kiểm thử browser. Không gọi LLM thật và không sử dụng screenshot giả.

## Bằng chứng đã kiểm tra

### Checklist yêu cầu gốc

| Yêu cầu deliverable | Trạng thái | Bằng chứng |
|---|---|---|
| Có workflow tuần tự Bước 1 → tester → Bước 2 → tester → reviewer | **Đạt** | Mục “Phạm vi và workflow” ở trên và các handoff tương ứng. |
| Biên bản viết bằng tiếng Việt, có phạm vi và từng tiêu chí đạt/chưa đạt | **Đạt** | Các mục “Bằng chứng đã kiểm tra” và “Đối chiếu tiêu chí”. |
| Có kết quả build/test và Preview thật, không bịa số liệu | **Đạt một phần** | Build/test đã chạy trong reviewer; Preview/API lấy từ handoff tester; UI browser chưa có bằng chứng. |
| Có ảnh thật hoặc ghi rõ giới hạn khi không chụp được | **Đạt** | Đã ghi thiếu Chromium và không tạo screenshot giả. |
| Có rủi ro còn lại và kết luận rõ `PASS` hoặc `CHANGES REQUIRED` | **Đạt** | Mục “Giới hạn và rủi ro còn lại” và kết luận cuối biên bản. |
| Chỉ cập nhật tài liệu review/handoff, không sửa source | **Đạt** | Reviewer không thay đổi file trong `backend/` hoặc `frontend/`. |
| Không dùng git command | **Đạt** | Reviewer không thực hiện thao tác git. |

### Tài liệu

- `docs/ui/handoff_step1_frontend.md`: ghi các thay đổi Màn Tạo hồ sơ, build/test backend/frontend,
  và nêu rõ chưa tự nhận PASS Preview.
- `docs/ui/handoff_step1_tester.md`: API/runtime PASS; các tiêu chí thao tác UI và screenshot đều
  `BLOCKED` do thiếu Chromium.
- `docs/ui/handoff_step2_frontend.md`: ghi thay đổi khung trang, build/test PASS và giới hạn browser.
- `docs/ui/handoff_step2_tester.md`: API/runtime PASS; các tiêu chí DOM/click/viewport/screenshot đều
  `BLOCKED` do thiếu Chromium.

### Source và automated checks

- `frontend/src/pages/BidDetailPage.tsx`: có `downloadExport(bidId, 'bundle')`, các nút hành động,
  banner chờ làm rõ, tab có số đếm, chuyển file/parse review sang tab yêu cầu, và đổi sang `Chạy lại`
  khi đã có pipeline step.
- `frontend/src/components/PipelineProgress.tsx`: render từ `steps` backend trả về, không tự tạo B4/B5;
  nhãn `Bỏ qua` chỉ là mapping cho status `skipped`.
- `frontend/src/components/Sidebar.tsx`: `NAV_ITEMS` không còn mục `Đánh giá`, nút `+ Tạo hồ sơ` vẫn
  được làm nổi bật.
- `frontend npm run build`: **PASS** — Vite build thành công.
- `frontend npm run test`: **PASS** — 1 test file, 6 tests.
- Output test có React Router future flag warning, không có test failure.
- Reviewer không chạy lại toàn bộ backend `pytest`; các kết quả backend/API trong mục Preview/runtime
  là bằng chứng được ghi trong handoff tester và không được trình bày như một lần chạy mới của reviewer.

### Preview/runtime

Theo handoff tester:

- `GET /api/health`: HTTP 200, database `ok`, `llm_provider: mock`.
- `GET /api/bids/sample/preview`: HTTP 200, đúng 3 file Nhật:
  `ja_email.md`, `ja_rfp.docx`, `ja_requirements.xlsx`.
- Preview không tạo hồ sơ mới trong kiểm tra read-only.
- Hồ sơ mẫu `83`: `waiting_clarification`, có 5 câu hỏi `awaiting_answer`.
- `pipeline_progress` trả các step backend; không dùng endpoint `/api/bids/83/pipeline` bị 404 làm căn cứ UI.

## Đối chiếu tiêu chí

### Bước 1 — Màn Tạo hồ sơ

| Tiêu chí “Xong khi” | Verdict | Căn cứ |
|---|---|---|
| `Dùng bộ này` mẫu Nhật hiển thị 3 file | **BLOCKED** | API preview xác nhận 3 file; chưa có browser evidence cho thao tác và render UI. |
| Bấm `Phân tích` một lần | **BLOCKED** | Chưa click được trên Preview. |
| Tự chuyển sang trang hồ sơ | **BLOCKED** | Chưa có DOM/navigation evidence. |
| Đọc đúng 36 requirement | **BLOCKED** | Chưa chạy được luồng UI parse/pipeline. |
| Pipeline tự tới `Chờ làm rõ`, không bấm thêm | **BLOCKED** | Chưa theo dõi được browser runtime. |
| Loading/rỗng/lỗi/retry không tạo hồ sơ trùng | **BLOCKED** | Chưa thể tạo và quan sát các tình huống qua UI. |

**Kết quả Bước 1:** source/build/API có bằng chứng hỗ trợ, nhưng tiêu chí nghiệm thu chính vẫn
`BLOCKED`; chưa đạt “Xong khi”.

### Bước 2 — Khung trang hồ sơ

| Tiêu chí “Xong khi” | Verdict | Căn cứ |
|---|---|---|
| Ở 900 px thấy đầu trang, tiến trình, tab và ít nhất 2 thẻ | **BLOCKED** | Chưa đo/quan sát được viewport browser. |
| Có banner `Chờ làm rõ` dẫn tới câu hỏi | **BLOCKED** | API có trạng thái/câu hỏi; chưa click hoặc xác nhận tab/scroll đích. |
| Không còn bước `Bỏ qua` sai | **BLOCKED** | Source chỉ cho thấy cách render; chưa xác nhận rendered UI với dữ liệu Preview thật. |
| Tab có số đếm requirement/câu hỏi | **BLOCKED** | Chưa có DOM evidence. |
| Nút hành động và trạng thái pipeline hoạt động | **BLOCKED** | Chưa click/quan sát trên browser. |

**Kết quả Bước 2:** source/build/API có bằng chứng hỗ trợ, nhưng tiêu chí nghiệm thu trực quan và
tương tác vẫn `BLOCKED`; chưa đạt “Xong khi”.

## Giới hạn và rủi ro còn lại

- Playwright không khởi tạo được vì thiếu executable Chromium tại
  `/home/user/.cache/ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell`;
  không có binary thay thế khả dụng.
- Chưa có screenshot thật, DOM assertion, click evidence, console evidence hoặc accessibility runtime.
- Chưa thể xác nhận lỗi hiển thị, chữ tràn, bố cục 900 px, trạng thái rỗng/lỗi và retry qua browser.
- Các handoff tester hiện dùng verdict `CHANGES REQUIRED` để biểu thị thiếu bằng chứng nghiệm thu,
  không khẳng định source chắc chắn có bug.
- Cần chạy lại đúng luồng mẫu Nhật trên Preview bằng môi trường có browser, sau đó cập nhật hai handoff
  tester và biên bản này bằng bằng chứng thật.

## Kết luận

# CHANGES REQUIRED

Đợt 1 chưa thể phê duyệt `PASS`. Automated build/test và các kiểm tra API/runtime đạt, nhưng các tiêu
chí “Xong khi” cốt lõi của Bước 1 và Bước 2 yêu cầu thao tác/quan sát trên Preview, hiện đều bị BLOCKED
do thiếu Chromium. Không có cơ sở hợp lệ để tuyên bố toàn bộ Đợt 1 đã đạt.
