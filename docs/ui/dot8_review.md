# Review — Đợt 8

Ngày review: 2026-10-11  
Vai trò: senior reviewer  
Phạm vi: backend/frontend Đợt 8, `docs/ui/dot8_check.md`, handoff và evidence Preview  
Kết luận: **Chưa sẵn sàng approval/release**

## Căn cứ review

- Quy tắc repository trong `AGENTS.md`, đặc biệt no-invented-numbers, price gate, root-relative API và yêu cầu phải chứng minh bằng test + Preview.
- `docs/ui/review_luot4.md` mục 1 và yêu cầu Đợt 8.
- Handoff backend/frontend/QA Đợt 8.
- `docs/ui_current/runtime_report.json` và các screenshot runtime trong `docs/ui_current/`.
- Screenshot reference tương ứng: `docs/ui_reference/01_tao_ho_so.png`, `03_tong_quan.png`, `05_giai_phap.png`, `06_ke_hoach_bao_gia.png`.
- Screenshot current tương ứng trong `docs/ui_v4/`.
- Code graph của các symbol `ProposalPage`, `BidPlanTab`, `GanttChart`, `WbsTreeTable`, `BidNewPage`, `BidsPage`, `BidDetailPage` và `GET /api/bids`.
- Review dimensions: correctness/regression, API contract, security/privacy, performance, accessibility/usability, automated tests và Preview evidence.

## Findings

### F-01 — Critical: Proposal tab crash và render rỗng

- **File/line:** `frontend/src/pages/ProposalPage.tsx:51`.
- **Finding:** `sections[key].split('{{QUOTATION}}')` được gọi mà không kiểm tra section có tồn tại. Runtime report xác nhận `TypeError: Cannot read properties of undefined (reading 'split')`; tab Proposal không có heading và body rỗng ở cả viewport 1440 và 1280.
- **Impact:** Người dùng không thể xem proposal hoặc trạng thái lỗi rõ ràng; acceptance UI của Proposal fail và lỗi làm hỏng một tab customer-facing.
- **Evidence:** `docs/ui_current/runtime_report.json:110-117, 286-296`; `docs/ui/dot8_check.md`, TC `D8-UI-12`; screenshot `docs/ui_current/dot8_proposal_runtime.png`.
- **Required fix:** Chuẩn hóa/validate sections theo schema trước khi render, hoặc render trạng thái thiếu dữ liệu có heading và hướng dẫn rõ ràng. Bổ sung test với payload thiếu từng section và chạy lại Preview/browser evidence.

### F-02 — High: Frontend phụ thuộc `stats` nhưng backend không trả `stats`

- **Files/lines:** `backend/app/api/routers/bids.py:95-109`; `frontend/src/pages/BidsPage.tsx:90-97`; `frontend/src/api/types.ts:105-116`.
- **Finding:** Frontend đã đọc `data.stats` để hiển thị 5 thẻ, nhưng `list_bids()` chỉ trả `items` và `total`; schema frontend khai báo `stats` optional để che mismatch. Fallback chỉ đếm các item của trang hiện tại, còn “Đã gửi” luôn là `0` khi backend không trả field.
- **Impact:** Thống kê danh sách không đại diện cho toàn bộ hồ sơ khi có phân trang, và không thể đáp ứng chính xác yêu cầu tổng hồ sơ/đang phân tích/chờ duyệt/đã duyệt/đã gửi.
- **Evidence:** Code backend nêu trên; `docs/ui/dot8_check.md:31,54`; QA ghi rõ API chỉ trả `items` và `total`.
- **Required fix:** Chốt contract duy nhất: backend trả aggregate stats theo cùng quyền truy cập/filter, kèm test API; frontend không fallback sang count của page cho KPI toàn cục. Nếu “sent” chưa có status/model thì phải hiển thị unsupported rõ ràng, không hiển thị số `0` như dữ liệu thật.

### F-03 — High: Staffing chưa đáp ứng “theo vai trò theo giai đoạn”

- **File/lines:** `frontend/src/components/BidPlanTab.tsx:41,76-86,123-128`; `frontend/src/api/types.ts:618-628`.
- **Finding:** UI chỉ giữ `staff: TeamAllocation` và gửi `team_allocation` tổng. Chính component ghi rõ “hợp đồng hiện chưa có phân bổ riêng theo phase”, trong khi acceptance Đợt 8 yêu cầu PM/BA/BrSE/AI/BE/FE/QA/Infra theo từng giai đoạn và chỉnh sửa được.
- **Impact:** Người dùng không thể điều chỉnh headcount theo PoC/MVP/Production; lịch được tính từ dữ liệu khác với màn hình yêu cầu và acceptance A-13/A-14 chưa đạt.
- **Required fix:** Hoặc triển khai đầy đủ `phase_team_allocation` trong shared frontend/backend contract và truyền qua PUT schedule, hoặc bỏ claim đã hoàn tất và đánh dấu feature unsupported. Thêm test kiểm tra thay đổi một role ở một phase chỉ ảnh hưởng dữ liệu/lịch tương ứng.

### F-04 — High: WBS chưa đúng yêu cầu inline editing và thao tác nhóm/task

- **Files/lines:** `frontend/src/components/WbsTreeTable.tsx:61-127,200-227`; `frontend/src/components/BidPlanTab.tsx:112-114`.
- **Finding:** Mỗi dòng vẫn có nút edit riêng (`✎`) và nút `+ Con`; editor là component row riêng được mở khi bấm nút. Đây không phải chỉnh trực tiếp trong dòng theo acceptance. Nút thêm cuối bảng là `＋ Thêm nhóm cấp 1`, không có dòng `+ Thêm task` cuối mỗi nhóm như yêu cầu. `BidPlanTab` còn có nút “Mở trình sửa đầy đủ”, tạo thêm một flow thay vì “lưu chung một lần” trong bảng kế hoạch.
- **Impact:** UX và workflow khác yêu cầu mục 12; người dùng phải mở editor riêng và lưu từng mutation, không thể chỉnh nhiều dòng rồi lưu chung.
- **Required fix:** Thiết kế state draft cho toàn bảng, input/select trực tiếp trong từng row, dòng thêm task trong từng group, nút thêm group, một thao tác save batch; bổ sung test UI cho edit/add/remove và tổng/lịch sau batch save. Nếu giữ editor riêng, phải ghi đây là deviation chưa đạt.

### F-05 — Medium: Bằng chứng Preview chưa bao phủ phần lớn acceptance P1

- **Evidence:** `docs/ui/dot8_check.md:30-40,51-57`; `docs/ui/handoff_dot8_qa.md:33-37`.
- **Finding:** 9 case bị `Blocked`, gồm KPI sau pipeline, solution risks/feasibility, effort factor table, staffing/recalculation, schedule/Gantt, WBS operations, payment detail/price gate và round two. Luồng Nhật dừng đúng ở `waiting_clarification`, nhưng chưa có flow trả lời câu hỏi để xác minh các phần downstream.
- **Impact:** Không đủ cơ sở nói Đợt 8 hoàn tất theo yêu cầu “done means proven”; test/build pass không thay thế runtime proof.
- **Required fix:** Tester chạy tiếp sample Nhật bằng câu trả lời thật và ghi từng acceptance với request/response hoặc DOM assertion. Các interaction chưa chạy phải giữ Blocked, không chuyển Pass bằng suy luận từ code.

### F-06 — Medium: Có regression/contract risk quanh dữ liệu solution cũ

- **Files/lines:** `docs/ui/handoff_dot8_backend.md:51-53`; `frontend/src/pages/BidDetailPage.tsx:590-595`; `frontend/src/pages/SolutionReviewPage.tsx:9,39-61`.
- **Finding:** Backend handoff cho biết `risks` có thể là object mới hoặc string cũ và `feasibility_score` có thể vắng. `BidDetailPage` có fallback object/string ở dòng 593, nhưng `SolutionReviewPage` vẫn dựng `FALLBACK_CHOICE` chỉ với `risks_vi` và không render structured risk/feasibility score. Đây là compatibility path chưa nhất quán; chưa thấy evidence/test UI cho cả hai shape; QA cũng chưa tới được solution vì state conflict.
- **Impact:** Có rủi ro render không ổn định hoặc hiển thị thiếu dữ liệu khi đọc bản ghi cũ, đặc biệt trong flow fallback mà frontend tuyên bố hỗ trợ.
- **Required fix:** Bổ sung fixture/test cho structured risk, legacy string và missing feasibility; UI phải hiển thị “chưa có dữ liệu” thay vì điểm/risk mặc định.

### F-07 — Low: Accessibility/usability còn lệch acceptance

- **Files/lines:** `frontend/src/components/WbsTreeTable.tsx:211-227`; `frontend/src/pages/BidsPage.tsx:230-241`.
- **Finding:** Icon edit/delete có accessible name qua `sr-only`, nhưng dùng ký tự Unicode `✎`/`🗑` thay vì icon button nhất quán và chưa có `aria-label` trực tiếp/title cho edit. Danh sách dùng `<tr role="link" tabIndex=0>` để điều hướng, có thể gây trải nghiệm bàn phím/semantics không nhất quán so với link thật.
- **Impact:** Khó đoán thao tác, phụ thuộc screen-reader CSS và có thể không đáp ứng keyboard semantics chuẩn.
- **Required fix:** Dùng button/link semantics rõ ràng, `aria-label` trực tiếp, focus state và kiểm tra bằng accessibility/browser test.

## Acceptance coverage

| Nhóm | Trạng thái review | Căn cứ |
|---|---|---|
| A-13/A-14 staffing theo role/phase, gợi ý và recalc code | **Fail/partial** | F-03; code chỉ gửi `team_allocation` tổng; chưa có Preview evidence |
| A-11/A-15 master schedule, Gantt tuần, marker/mốc khách | **Partial, chưa chứng minh** | `GanttChart` có tuần/marker theo code; D8-UI-07 Blocked |
| A-12 WBS inline/batch editing | **Fail/partial** | F-04; UI còn edit flow riêng và mutation từng thao tác |
| A-10 payment trong quotation, price gate | **Chưa chứng minh** | D8-UI-09 Blocked; code có `PaymentTable` nhưng chưa runtime |
| B file import, limit, currency | **Partial** | D8-UI-01 Pass theo DOM; chưa kiểm import DOCX/PDF thật |
| C Overview KPI và list statistics | **Partial/fail** | KPI code có; list stats mismatch F-02; D8-UI-02/03 Blocked |
| D conditional round two/reason | **Backend covered, UI unproven** | Backend tests/handoff; D8-UI-10 Blocked |
| E structured risks/feasibility/factor table | **Backend covered, UI unproven** | Backend tests/handoff; D8-UI-04/05 Blocked |
| Proposal rendering | **Fail** | F-01; D8-UI-12 Fail |

## Automated checks reviewed

- Backend `python3 -m pytest -q`: **PASS**, có `StarletteDeprecationWarning` về httpx.
- Frontend `npm test -- --run`: **PASS**, 11 tests.
- Frontend `npm run build`: **PASS**.
- Preview compose: QA report ghi **PASS** cho việc khởi động production frontend/backend.
- Browser runtime: **không đạt release** vì Proposal crash và nhiều acceptance downstream còn Blocked.

## Security, performance và test review

- **Security/privacy:** Không phát hiện evidence của secret/API-key leakage trong các file đã review; frontend dùng API root-relative theo contract, và các response error/runtime evidence không chứa credential. Đây không phải security audit toàn hệ thống; upload/import và quyền truy cập đa người dùng chưa được kiểm thử runtime trong QA này.
- **Performance:** Không thấy vòng lặp hoặc phép tính nặng mới trong các path UI đã rà soát; Gantt tạo marker/week segments ở client theo khoảng lịch. Rủi ro chính là dữ liệu lớn WBS và fallback đếm stats theo page, đã được nêu ở F-02; chưa có profiling/performance budget evidence.
- **Automated tests:** Backend và frontend suites pass, nhưng thiếu frontend regression test cho payload Proposal thiếu section, thiếu contract test cho `GET /api/bids.stats`, và thiếu interaction tests cho staffing phase/WBS batch save. Các thiếu hụt này làm giảm độ tin cậy dù build xanh.

## Residual risks

- Chưa có browser evidence cho flow Nhật sau khi trả lời vòng 1, nên chưa xác nhận downstream API/UI đồng nhất.
- Chưa chứng minh price gate bằng thao tác customer-facing sau approval; không được suy ra từ code có placeholder.
- Chưa có regression test frontend cho payload proposal thiếu section, chính là payload gây crash.
- Handoff frontend nói đã có staffing theo role/phase nhưng code/handoff contract lại ghi backend chưa có phase allocation; cần thống nhất claim trước khi nghiệm thu.

## Decision

**Không approval Đợt 8 tại thời điểm review.** Cần xử lý tối thiểu F-01, F-02, F-03, F-04 và chạy lại QA downstream với evidence thật. Sau đó reviewer phải cập nhật lại finding status và acceptance table; không dùng screenshot hiện tại để suy diễn các case đang Blocked.
