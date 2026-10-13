# Review Đợt 3 — Đối chiếu tài liệu và bằng chứng

Ngày review: 2026-10-11  
Vai trò: reviewer (code/document review)  
Phạm vi: đối chiếu mục 3 của `docs/ui/review_ui_tung_man.md` với các `compare_*.md`, `final_check.md`, `api_gaps.md` và handoff Đợt 3.

## Kết luận

**CHANGES REQUIRED**

Chưa đủ điều kiện PASS/DONE. Các tài liệu có bằng chứng API, source và build/test khá đầy đủ, đồng thời không bịa screenshot hay dữ liệu. Tuy nhiên acceptance của Đợt 3 yêu cầu Preview browser, screenshot thật ở `1440x900` và `1280x800`, kiểm tra click/DOM/console, cùng một flow Nhật liên tục từ tạo hồ sơ đến duyệt giá. Các điều kiện này chưa được chứng minh.

## Findings

### CAO

| ID | Finding | Evidence | Điều kiện đóng |
|---|---|---|---|
| D3-R-01 | Chưa có browser evidence cho toàn bộ UI Đợt 3. Không có screenshot thật, DOM assertion, click/download/clipboard hoặc console evidence. | `final_check.md:11,32-35`; `handoff_dot3_final_tester.md:39-53`; các compare Màn 2–10 đều ghi Chromium unavailable. | Chạy lại Preview với Chromium khả dụng ở `1440x900` và `1280x800`; lưu screenshot thật vào `docs/ui_v3/final/`; kiểm tra các thao tác và console, cập nhật final report bằng kết quả thực tế. |
| D3-R-02 | Acceptance flow không chạy trên một hồ sơ duy nhất. Bid `#98` dừng ở `waiting_clarification`; approval được xác nhận trên bid `#97` đã chuẩn bị từ trước. | `final_check.md:6-13,25-30`; `handoff_dot3_final_tester.md:27-37`. | Tạo một bid Nhật mới, trả lời đủ câu hỏi, tiếp tục pipeline, duyệt kỹ thuật rồi duyệt giá trên chính bid đó; ghi status và response thật. |
| D3-R-03 | Màn 6 còn các yêu cầu chức năng chưa hoàn tất, không chỉ bị chặn bởi browser: chọn model/currency và onsite editable chưa được nối đầy đủ trong compare; thiếu work-type matrix; chưa có collapse/filter phase, inline edit/save chung và vẫn còn effort card trùng. | `compare_06_ke_hoach.md:15-25,49-53`; yêu cầu gốc tại `review_ui_tung_man.md:284-292`. | Hoặc hoàn thiện đúng các mục M6-01, M6-02, M6-07, M6-09, M6-10, M6-11, hoặc cập nhật scope/contract được phê duyệt; sau đó kiểm tra lại trên Preview/browser. |

### TRUNG BÌNH

| ID | Finding | Evidence | Điều kiện đóng |
|---|---|---|---|
| D3-R-04 | Tài liệu Màn 7 bị drift về contract `note_language`: `api_gaps.md` và handoff backend ghi đã bổ sung query `note_language`, nhưng `compare_07_dap_ung.md` vẫn nói endpoint chưa nhận lựa chọn ngôn ngữ và yêu cầu backend bổ sung. | `api_gaps.md:42-50`; `handoff_backend_dot3.md:15-18,55-60`; `compare_07_dap_ung.md:37,44-50`. | Tester/frontend xác nhận request thực tế có truyền `note_language`; cập nhật `compare_07_dap_ung.md` và final report theo contract hiện tại, hoặc ghi rõ nếu frontend chưa tích hợp nên gap chỉ còn ở integration. |
| D3-R-05 | Các gap contract vẫn ngăn nghiệm thu đầy đủ: proposal translation, proposal versions, Q&A `topic`/`blocking` và import/export, bid `target`; một số compare còn ghi route/sample-key blocker cũ cần được phân loại lại theo flow mới. | `api_gaps.md:19-28,51-67,69-76`; `final_check.md:71-77`; `compare_04_yeu_cau.md:66-71`; `handoff_backend_dot3.md:33-38`. | Backend chốt schema/endpoint và frontend tích hợp, hoặc giữ unavailable minh bạch nhưng ghi rõ các mục này là ngoài acceptance hiện tại. Xác nhận lại sample/route blocker bằng flow đang dùng trước khi giữ làm blocker. |
| D3-R-06 | Một số compare ghi “source/API đạt” nhưng đồng thời chưa có runtime browser evidence. Điều này phù hợp với hạn chế đã nêu, nhưng cần tránh dùng “Pass” không điều kiện khi tổng hợp acceptance. | `compare_03_tong_quan.md:27-38,61-66`; `compare_09_quy_trinh_duyet.md:16-25,78-88`; `compare_10_cai_dat.md:22-31`. | Chuẩn hóa nhãn tổng hợp thành `PASS source/API, browser BLOCKED` hoặc `CHANGES REQUIRED`; chỉ dùng `PASS` cho acceptance sau khi có evidence runtime tương ứng. |

### THẤP

| ID | Finding | Evidence | Điều kiện đóng |
|---|---|---|---|
| D3-R-07 | Không có thư mục `docs/ui_v3/final/` vì browser bị chặn. Đây là xử lý đúng theo quy tắc không tạo screenshot giả, nhưng deliverable ảnh của mục 4 chưa hoàn tất. | `final_check.md:32-35,79-84`; `handoff_dot3_final_tester.md:55-63`. | Tạo thư mục và bổ sung chỉ các ảnh chụp từ app thật khi browser khả dụng; không dùng ảnh API hoặc ảnh reference thay thế. |
| D3-R-08 | Full-flow evidence và per-screen evidence dùng nhiều bid (`#92`, `#97`, `#98`) giữa các compare, nên không thể coi là một baseline nhất quán cho mọi màn. | `compare_03_tong_quan.md:8,48-59`; `compare_07_dap_ung.md:19-22`; `final_check.md:6-13`. | Chọn một bid mới duy nhất cho rerun cuối, ghi rõ bid ID trong tất cả evidence runtime; dùng bid khác chỉ khi ghi rõ đó là evidence bổ sung, không thay acceptance flow. |

## Đối chiếu phạm vi mục 3

| Màn | Tài liệu/evidence | Đánh giá reviewer |
|---|---|---|
| 7 Đáp ứng yêu cầu | `compare_07_dap_ung.md`, `api_gaps.md`, handoff M7 | Source/API có tiến bộ và export endpoint có evidence; browser bị chặn. Có drift `note_language` cần sửa tài liệu/integration. Chưa PASS. |
| 8 Proposal & hồ sơ | `compare_08_proposal.md`, `api_gaps.md`, handoff M8 | Source có renderer/edit/download guard; browser bị chặn; translation chưa có contract. Chưa PASS. |
| 9 Quy trình & phê duyệt | `compare_09_quy_trinh_duyet.md`, `api_gaps.md`, handoff M9 | Approval gate và validation có API evidence; browser bị chặn; proposal versions còn blocker. Chưa PASS. |
| 2 Danh sách hồ sơ | `compare_02_danh_sach.md`, `api_gaps.md`, handoff M2/M10 | Có source/test evidence; field/API integration và browser chưa hoàn tất; target còn thiếu nguồn. Chưa PASS. |
| 10 Cài đặt | `compare_10_cai_dat.md`, handoff M2/M10 | Source/build/test evidence tốt; browser chưa xác minh layout/input/PUT. Chưa PASS. |
| Khung chung và các màn 1–6 | `compare_03` đến `compare_06`, `final_check.md` | Có nhiều mục đã sửa, nhưng Màn 6 còn yêu cầu chưa hoàn tất; visual/browser evidence thiếu trên toàn bộ phạm vi. Chưa PASS. |

## Evidence quality

- **Có thể tin cậy:** health Preview, `LLM_PROVIDER=mock`, API sample/parse/evaluation/WBS/schedule/quotation/approval được ghi bằng response thật; frontend build/test được ghi ở các compare/handoff.
- **Không đủ để nghiệm thu UI:** static source review, HTML shell, API response và build/test không thay thế DOM/render/click/console/screenshot.
- **Được xử lý đúng:** không tạo screenshot giả, không suy diễn field API thiếu, không gọi LLM thật, giữ các contract gap ở trạng thái unavailable/minh bạch.
- **Không thể xác nhận:** visual fidelity, text overflow, responsive, nút thực sự hoạt động trên browser, download/clipboard, console runtime và một flow liên tục duy nhất.

## Completeness audit theo task gốc

| Yêu cầu bắt buộc | Trạng thái | Evidence / ghi chú |
|---|---|---|
| Đọc `AGENTS.md`, `review_ui_tung_man.md`, `final_check.md` trước khi review | Đạt | Các tài liệu đã được đọc và dùng làm nguồn đối chiếu; yêu cầu reviewer được phản ánh trong phạm vi review. |
| Đối chiếu mục 3 với compare của Màn 7, 8, 9, 2, 10 và các màn liên quan | Đạt | Có ma trận Màn 7, 8, 9, 2, 10 và nhóm khung chung/Màn 1–6; compare Màn 3–6 được dùng để kiểm tra các blocker còn sót. |
| Đối chiếu `final_check.md`, `api_gaps.md` và handoff Đợt 3 | Đạt | Findings D3-R-01 đến D3-R-08 trích dẫn các tài liệu này; drift `note_language` được nêu riêng. |
| Review theo lỗi/rủi ro/evidence trước, không sửa code | Đạt | Findings được phân loại CAO/TB/THẤP; reviewer không sửa `backend/` hoặc `frontend/`. |
| Kết luận rõ PASS hoặc CHANGES REQUIRED | Đạt | Kết luận ở đầu và cuối tài liệu đều là **CHANGES REQUIRED**. |
| Ghi điều kiện đóng cho các mục còn thiếu | Đạt | Mỗi finding có cột `Điều kiện đóng`; phần tổng hợp có 6 điều kiện bắt buộc. |
| Tạo `docs/ui/dot3_review.md` và handoff reviewer | Đạt | Hai file deliverable tồn tại; handoff nêu boundary và trạng thái. |
| Không tạo screenshot giả, không bịa dữ liệu, không dùng LLM thật | Đạt theo evidence hiện có | Các tài liệu nguồn đều ghi browser blocker và không có screenshot giả; review chỉ đánh giá evidence, không bổ sung dữ liệu runtime. |
| Dừng tại boundary reviewer | Đạt | Handoff xác nhận không chạy tiếp tester/frontend/backend và không thực hiện thay đổi code. |

## Điều kiện đóng bắt buộc

1. Cung cấp Chromium cho Preview/browser testing và rerun toàn bộ màn 1–10 ở hai viewport yêu cầu.
2. Chụp screenshot thật, thu DOM/click/download/clipboard/console evidence và cập nhật các compare còn `BLOCKED`.
3. Rerun một hồ sơ Nhật mới duy nhất từ tạo hồ sơ, parse 36 requirement, trả lời clarification, hoàn tất pipeline, duyệt kỹ thuật đến duyệt giá.
4. Hoàn thiện hoặc chính thức loại khỏi acceptance các mục Màn 6 còn thiếu, đặc biệt inline edit/save, work-type matrix và chọn model/currency/onsite.
5. Đồng bộ `compare_07_dap_ung.md` với contract `note_language` hiện tại và rà lại các route/sample-key blocker còn hiệu lực.
6. Bổ sung quyết định/schema cho proposal translation, proposal versions, Q&A topic/blocking/import-export và bid target, hoặc ghi rõ chúng là contract blockers ngoài phạm vi release.

## Quyết định

**CHANGES REQUIRED.** Không có bằng chứng đủ để đánh dấu Đợt 3 PASS. Reviewer không sửa code; các finding trên là điều kiện đóng cho tester/frontend/backend tương ứng.
