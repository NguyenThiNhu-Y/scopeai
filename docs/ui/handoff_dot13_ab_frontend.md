# HANDOFF NOTE — ĐỢT 13 · Bước frontend-dev (A, B)

## Đã làm

### Backend groundwork (chuẩn bị trước workflow — đã chạy 358 test backend, exit 0)
- `backend/app/schemas/api_schemas/confidence.py`: `AnalogCase` thêm `direction`, `market` (str|null) — bảng case tương tự hiện được cột Hướng/Thị trường.
- `backend/app/services/confidence_engine.py` `find_similar_cases`: trả kèm `direction`/`market` của từng case.
- `backend/app/api/routers/approvals.py`: thêm `GET /bids/{id}/approvals` → `{items:[{id,kind,status,approver,reason,decided_at,snapshot}]}` (snapshot = confidence lúc duyệt, §5.5).
- `backend/app/api/routers/settings.py`: thêm `GET /api/eval/reports/latest` (đọc JSON mới nhất trong `docs/eval/reports/`, 404 nếu chưa có) — cho mục E.

### A. Tổng quan — thẻ "Độ tin cậy ước lượng"
- `frontend/src/api/types.ts`: type `ConfidenceOut/ConfidenceSignal/AnalogCase/HistoryBiasOut/AnalogOut/ConfidenceLevel/SignalStatus` (khớp backend confidence.py).
- `frontend/src/api/client.ts`: hàm `getConfidence(id)` → GET /bids/{id}/confidence.
- `frontend/src/components/ConfidenceCard.tsx` (mới): huy hiệu Cao/Trung bình/Thấp (màu lục/vàng/đỏ), tối đa 3 lý do (ưu tiên fail → warn, hàm thuần `confidenceReasons`), link "Xem chi tiết ›" → tab Kế hoạch; gating `enabled` như effort/quotation.
- `frontend/src/pages/BidDetailPage.tsx`: render thẻ trong lưới Overview; thêm `'confidence'` vào mọi vòng invalidate (events.done, handleAnswersSubmitted, poll 3s khi analyzing); truyền `onNavigateTab={setTab}` cho BidPlanTab.

### B. Kế hoạch & báo giá
- `frontend/src/components/AnalogCompare.tsx` (mới): khối "So với dự án tương tự" — bảng case (tên, hướng, thị trường, số requirement, effort thực tế PoC/MVP/Production, tổng, số tuần); thanh so sánh từng giai đoạn (ước lượng = tổng WBS theo phase vs khoảng min–max thực tế của case); dòng "Sai lệch lịch sử" (hàm thuần `historyBiasText`); trạng thái "Chưa đủ dữ liệu tham chiếu" khi position=insufficient hoặc < 2 case.
- `frontend/src/components/WbsTreeTable.tsx`: thêm cột "Requirement" — chip mã tối đa 3 rồi "+n", hover (title) hiện nội dung requirement; sửa trong dòng qua ô nhập mã cách dấu phẩy + datalist gợi ý (chỉ task lá); `buildChanges` đưa `requirement_codes` vào op add/update (backend đã hỗ trợ); `changeCount` tính cả thay đổi mã.
- `frontend/src/components/BidPlanTab.tsx`: thêm `onNavigateTab` prop; query confidence + evaluations; invalidate `['confidence', bidId]` sau khi lưu WBS/lịch; render AnalogCompare; dòng "Truy vết: x/y requirement có task" + danh sách requirement chưa có task (bấm mã → tab Đáp ứng) qua component `TraceabilityLine`; truyền `requirementContents`/`availableRequirementCodes` cho WbsTreeTable.
- `frontend/src/lib/format.ts`: hàm thuần `signalStatusMeta(status)` (Đạt ✓ / Cảnh báo ⚠ / Lỗi ✕ / Không có dữ liệu –, fallback an toàn) + `MARKET_LABELS` (jp/vn/other).
- Sửa trong review: ConfidenceCard/AnalogCompare phân biệt `query.fetchStatus === 'idle'` (chưa bật query — hồ sơ draft) → hiện "Chưa có dữ liệu"/"Chưa đủ dữ liệu tham chiếu" thay vì treo "Đang tải…" vô hạn.

### F. Test frontend (phần A/B)
- `frontend/src/lib/format.test.ts` (mới): 7 test — `signalStatusMeta` đủ 4 trạng thái + fallback, `MARKET_LABELS`.
- `frontend/src/App.test.tsx`: mock `getConfidence`; fixture `CONFIDENCE_LOW` (7 tín hiệu, analog 2 case, history_bias); 3 test ConfidenceCard (Thấp + ≤ 3 lý do + link Xem chi tiết; Cao + summary; Trung bình). Cập nhật fixture WBS thêm `requirement_codes`.

## Kiểm chứng
- `cd frontend && npm run test` → **PASS (25) FAIL (0)** (trước đây 16 test — thêm 9).
- `cd frontend && npm run build` (tsc -b && vite build) → **OK** (exit 0, dist/assets/index-*.js ~393 kB).
- Backend: 358 test pass (chạy `python -m pytest` programmatic, exit 0) — groundwork không phá vỡ gì.
- Không dùng git (tree đang untracked như Đợt 12). Không chạy preview (tester lo).

## Lưu ý cho bước sau (frontend-dev C/D/E)
- Đã có sẵn trong code chung: `getConfidence` + types confidence (client.ts/types.ts), `signalStatusMeta` (format.ts) — **dùng lại, đừng duplicate**.
- `getConfidence` dùng chung queryKey `['confidence', bidId]` giữa ConfidenceCard/AnalogCompare/ApprovalsPage — tận dụng cache.
- Backend đã có `GET /bids/{id}/approvals` (snapshot) và `GET /api/eval/reports/latest` cho mục C và E.
- File dùng chung đã sửa: client.ts (chỉ thêm), types.ts (chỉ thêm), format.ts (chỉ thêm), App.test.tsx (thêm mock + test). Không xóa phần của tôi.