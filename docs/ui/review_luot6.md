# Review lượt 6: sau Đợt 12–13 (độ tin cậy, case study, eval)

Ngày review: 14/10/2026. Code: `code_vibeflow/scopeai` bản đồng bộ mới nhất. Ảnh: `vibeflow/ui_v6/` (`ja_*` là mẫu CRM tiếng Nhật, `tk_*` là mẫu Tokai).

Cách kiểm:
- Chạy test.
- Chạy app với `LLM_PROVIDER=mock`, đi luồng mẫu CRM tiếng Nhật trên trình duyệt.
- Chạy mẫu Tokai bằng **file thật** của bộ demo (`scopeai/samples/rfp_tokai_minato`: 41 requirement, 600 sự cố).
- Gọi API để đối chiếu số liệu.

**Kết quả chung:**
- Test: backend **358 passed**, frontend **28 passed**, build sạch.
- Phần lớn Đợt 12–13 **chạy đúng thiết kế**: API độ tin cậy, 7 tín hiệu, so với dự án tương tự, sai lệch lịch sử, truy vết requirement, import case study, khóa duyệt khi mức Thấp, tab Đánh giá hệ thống.
- Biên bản tester `dot13_check.md` trung thực: ghi rõ phần Tokai bị BLOCKED.

**Nhưng bộ Tokai, dùng để quay video, chưa demo được.** Đây là ưu tiên số 1 trước 15/10.

## 1. Đã đạt (kiểm chứng lại trên máy)

| Hạng mục | Kết quả |
|---|---|
| Thẻ "Độ tin cậy ước lượng" ở Tổng quan | Hiện mức Thấp và 3 lý do, khớp API |
| So với dự án tương tự (CRM) | 2 case `cs_none_crm_jp` (0,92), `cs_none_booking_jp` (0,88), khoảng 235–266; sai lệch lịch sử 1,07 (3 case). Đúng dữ liệu đã thiết kế |
| Truy vết requirement | 34/36; cột Requirement trong WBS, hover hiện nội dung |
| Import case study | Tải mẫu, xem trước lỗi theo dòng, lưu tạo phiên bản mới (theo `dot13_check.md`) |
| Khóa duyệt khi mức Thấp | Bắt buộc nhận xét ≥ 10 ký tự, lưu snapshot mức độ tin cậy khi duyệt |
| Lịch (lỗi Đợt 10 đã sửa) | Bắt đầu từ mốc khách 01/01/2027; các vai trò chạy song song; MVP sau khoảng go/no-go; không còn AI Engineer cho hướng "Không dùng AI" |
| Thẻ Requirement 94%, câu hỏi 5/5, "Chạy lại" là nút phụ | Đã sửa |

## 2. Lỗi chặn demo Tokai (P0)

| # | Lỗi | Bằng chứng |
|---|---|---|
| T1 | **Trang Tạo hồ sơ chỉ có 2 bộ mẫu**, không có Tokai | Chỉ 2 nút "Dùng bộ này"; `SampleKey` ở frontend chỉ gồm `ja_email`/`vi_email` |
| T2 | **Tệp PDF manual bị đưa vào parser Excel** (D-1 tester đã báo) | `sample_service` khai báo PDF loại `sample_data` → "Không đọc được Excel". Đổi thành loại tài liệu (`rfp`) thì đọc được: thử trên máy, cả 4 tệp OK |
| T3 | **Bộ Tokai trên VibeFlow là tệp giả rút gọn**, không phải bộ demo thật | `fixtures/requirements_tokai_minato.xlsx` chỉ có 5 requirement, CSV 3 dòng, PDF 1,5 KB. Bộ thật có 41 requirement, 600 sự cố, PDF 148 KB, RFP 15 mục |
| T4 | **Đọc nhầm sheet bìa 表紙 thành requirement** | Với tệp thật: 46 requirement = 25 + 16 + **5 dòng của sheet 表紙** (hướng dẫn, lịch sử sửa đổi) |
| T5 | **Mất mã requirement của khách** | Requirement lưu mã nội bộ `REQ-001…`, không giữ `要件ID` của khách (`FR-QA-001`, `NFR-SEC-001`…). Khi điền bảng đáp ứng vào tệp khách và khi truy vết, phải dùng đúng mã khách |
| T6 | **Mock không có kịch bản Tokai** | Chạy Tokai bằng mock: mục tiêu "xây dựng hệ thống CRM", hướng "Không dùng AI", WBS là WBS CRM, so với case CRM. Truy vết 0/46 vì mock gán theo tiền tố `FR-`/`NFR-`. Nếu quay video bằng mock, Tokai sẽ hiện nội dung sai hoàn toàn |

## 3. Lỗi số liệu và hiển thị (P1)

| # | Lỗi | Bằng chứng |
|---|---|---|
| N1 | **WBS và effort dùng hệ số khác nhau** | Effort midpoint 241,5 (hệ số ×1,38 = Nhật 1,2 × nhiều requirement 1,15), nhưng WBS kiểm tra quanh midpoint **210** (chỉ ×1,2). Tokai: effort 289,8, WBS 252 (= 289,8 / 1,15). Hệ quả: WBS luôn "thấp hơn dự án tương tự" và lệch so với số effort hiển thị |
| N2 | **Mock WBS luôn có task lá > 10 man-day** | 9 task lá từ 11,3 đến 24 man-day → `leaf_within_limit` luôn fail → mức tin cậy **luôn Thấp** với mọi hồ sơ mock. Demo không thấy được mức Trung bình hay Cao |
| N3 | **Thẻ "Rủi ro lớn nhất" ở Tổng quan trống** | API solution trả 4 rủi ro và điểm khả thi 3/5, nhưng thẻ Tổng quan không hiện; thẻ "Khả thi" chỉ có câu chung chung |
| N4 | **Mã thô trong lý do độ tin cậy** | "Thiếu 1 kiểm tra WBS: **leaf_within_limit**"; "(**below**, lệch 0.7%)". Mức "lệch 0.7%" tính so với khoảng đã nới ±10% nên khó hiểu (210 thấp hơn 235 khoảng 11%) |
| N5 | **Đường dẫn báo cáo eval phụ thuộc thư mục chạy** (D-13-1) | `GET /api/eval/reports/latest` 404 nếu backend không chạy từ gốc repo |
| N6 | **App vẫn tên "Trợ lý dự thầu"** | Sidebar, tiêu đề tab. Slide đã đổi thành BidPilot |
| N7 | Mốc khách của Tokai | RFP có bảng Phase 2 (2027/4–9) và Phase 3 (2027/10~) nhưng intake chỉ lấy được PoC 2026/12 (mock). Kiểm lại khi chạy LLM thật |

## 4. Kết quả eval mock (tham khảo)
- Báo cáo `docs/eval/reports/eval_20261013_1753_mock.md`:
  - MAPE 21,4%;
  - 1/3 case nằm trong khoảng đáp án;
  - đúng hướng giải pháp 2/3 (Tokai sai do mock);
  - truy vết trung bình 64,8%.
- Đây chỉ là kiểm tra harness. Số có ý nghĩa phải chạy với LLM thật (15/10), sau khi sửa T5 và N1.

## 5. Kế hoạch còn lại

| Ngày | Việc |
|---|---|
| 14/10 tối | Upload bộ Tokai thật, chạy **Đợt 14** (P0 + N1–N6) |
| 15/10 | Kiểm tay trên Preview; gắn key LLM thật; chạy Tokai và `make eval` với LLM thật; **quay video bằng Tokai** |
| 16/10 | Cập nhật ảnh và số eval thật vào slide, nộp bài |

**Nếu không kịp chạy LLM thật:** Đợt 14 có mục E (mock Tokai) để video vẫn đúng nội dung khi chạy mock.

## 6. Chuẩn bị trước Đợt 14

Upload 4 tệp thật từ `scopeai/samples/rfp_tokai_minato/` lên VibeFlow vào `sample_data/rfp_tokai_minato/real/`, **giữ nguyên tên tiếng Nhật**:
- `RFP_設備保全ナレッジAI_v1.0.docx`
- `別紙1_要件一覧_v1.0.xlsx`
- `別紙2_故障履歴サンプル_2025-2026.csv`
- `別紙3_MC-850H_取扱説明書_保守編_抜粋.pdf`

Upload thêm file này thành `docs/ui/review_luot6.md`.

## 7. Prompt Đợt 14

```
Đọc docs/ui/review_luot6.md (mục 2, 3) và docs/ui/dot13_check.md mục 9–10. Làm ĐỢT 14:

A. Bộ mẫu Tokai (backend + frontend):
   1. sample_service: key tokai_minato dùng 4 tệp thật trong sample_data/rfp_tokai_minato/real/ (giữ tên tiếng Nhật);
      tệp PDF khai báo là tài liệu (rfp), không phải sample_data; CSV là sample_data; xlsx là requirement.
      Bỏ thư mục fixtures/ rút gọn cũ (test nào dùng thì chuyển sang tệp thật).
   2. Trang Tạo hồ sơ: thêm bộ mẫu thứ 3 "RFP trợ lý AI bảo trì nhà máy (Nhật)", hiện đủ 4 tệp như 2 bộ cũ.
B. Parser requirement:
   1. Chỉ đọc sheet có cột mã requirement; bỏ sheet bìa/hướng dẫn (ví dụ 表紙). Tokai thật phải ra đúng 41 requirement
      (機能要件 25 + 非機能要件 16).
   2. Giữ mã requirement của khách (cột 要件ID / ID / No.) làm mã hiển thị và mã truy vết; mã nội bộ REQ-xxx chỉ dùng khi
      tệp không có cột mã. Bảng đáp ứng xuất ra tệp khách phải khớp đúng 要件ID.
C. Số liệu:
   1. WBS dùng cùng hệ số và cùng midpoint với effort engine (cả customer_jp và many_requirements); test: midpoint kiểm
      tra WBS = effort midpoint hiển thị.
   2. Mock WBS: tách task để mọi task lá ≤ 10 man-day; với mẫu CRM tiếng Nhật, kiểm tra WBS đạt 4/4.
D. Hiển thị:
   1. Thẻ Tổng quan "Rủi ro lớn nhất" hiện rủi ro mức cao nhất từ API solution (loại, mức, mô tả, giảm thiểu); thẻ
      "Khả thi" hiện điểm x/5 và lý do.
   2. Lý do độ tin cậy không hiện mã thô: leaf_within_limit → "có task lá vượt 10 man-day", pm_qa_ok → "thiếu PM/QA"...;
      below/above/inside → "thấp hơn / cao hơn / nằm trong"; % lệch tính so với khoảng thực tế gốc (không phải khoảng
      đã nới ±10%).
   3. GET /api/eval/reports/latest resolve đường dẫn theo vị trí file code, không theo thư mục chạy (D-13-1).
   4. Đổi tên hiển thị app thành "BidPilot" (sidebar, title, meta, README), dòng phụ "Trợ lý AI lập hồ sơ dự thầu".
      Không đổi tên package, biến, API.
E. Mock cho Tokai (để demo được khi chưa có LLM thật): khi bộ mẫu là tokai_minato, mock trả nội dung đúng hồ sơ:
   intake (trợ lý tri thức bảo trì, 3 nhà máy, 230 người dùng, Azure Japan East, PoC 3 tháng, ngân sách PoC 15M JPY,
   mốc PoC 2026/12, Phase 2 2027/4–9, Phase 3 2027/10), câu hỏi làm rõ về tỉ lệ PDF scan, mục tiêu độ chính xác và
   bộ 300 câu đánh giá, API ghi MAINTE-PRO, model khả dụng ở Japan East; hướng giải pháp RAG; rủi ro OCR và nghiệm
   thu độ chính xác; WBS RAG (OCR, chỉ mục, trả lời song ngữ Nhật–Việt, tìm sự cố tương tự) gắn đúng 要件ID; đánh giá
   đáp ứng theo 41 requirement. Mock CRM giữ nguyên.
Thứ tự: backend-dev (A1, B, C, D3, E) → frontend-dev (A2, D1, D2, D4) → tester chạy Preview với bộ Tokai từ trang
Tạo hồ sơ, ghi docs/ui/dot14_check.md với số liệu thật: số requirement và 3 mã đầu, trạng thái 4 tệp đính kèm, hướng
giải pháp, mức độ tin cậy và từng tín hiệu, các case tương tự (id, điểm), midpoint WBS so với effort, task lá lớn
nhất → reviewer ghi docs/ui/dot14_review.md.

Quy tắc: giữ LLM_PROVIDER=mock; không test nào gọi LLM thật; tuân thủ AGENTS.md (LLM không sinh con số); nhãn tiếng
Việt, không hiện mã thô; code dễ đọc. Chạy mỗi lệnh test/build tối đa 2 lần; nếu output bị rtk rút gọn thì đọc log
trong [full output: ...]. Không tạo ảnh hay bằng chứng giả; mục nào không kiểm được thì ghi rõ. Cho tôi xem kế hoạch
trước khi chạy.
```

## 8. Kiểm tay sau Đợt 14
1. Trang Tạo hồ sơ có bộ Tokai. Bấm Phân tích: 4 tệp đọc được, **41 requirement** mã `FR-QA-001…`.
2. Hướng giải pháp là **RAG**; case tương tự gồm các dự án Tokai (`cs_rag_mc_manual_aichi`, `cs_rag_fault_history_jp_vn`…); sai lệch lịch sử ở mức **cảnh báo** (khoảng 1,11).
3. Mẫu CRM: kiểm tra WBS 4/4; midpoint WBS bằng effort midpoint (241,5); mức tin cậy không còn luôn Thấp.
4. Thẻ "Rủi ro lớn nhất" có nội dung; lý do độ tin cậy không còn mã thô.
5. Sidebar ghi **BidPilot**.
