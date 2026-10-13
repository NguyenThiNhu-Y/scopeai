# Handoff — Review Đợt 5 frontend

Ngày: 2026-10-11  
Vai trò: senior reviewer

## Trạng thái

**DONE — đã review source frontend và tài liệu contract; verdict: CHANGES REQUIRED.**

## Phạm vi đã kiểm tra

- Đọc `AGENTS.md`, `docs/ui/review_luot3.md` mục 3.1 và 3.2–3.3,
  `docs/ui/dot5_check.md`, `docs/ui/handoff_dot5_frontend.md` và
  `docs/04_architecture/api_contract.md`.
- Dùng vibegraph MCP để xác định các component/page frontend và đọc source đúng symbol.
- Đối chiếu price gate, nhãn tiếng Việt, loading/empty/error states, root-relative API contract
  và các thay đổi Dot 5.
- Không sửa backend, không sửa frontend source, không gọi LLM thật và không dùng git.

## Findings cần xử lý

1. `frontend/src/pages/ProposalPage.tsx:49-53`: phần giả định/ngoài phạm vi dùng `language`
   thay vì `effectiveLanguage`, có thể trộn tiếng Việt với proposal khách Nhật/Anh.
2. `frontend/src/components/RequirementMatrix.tsx:171`: render trực tiếp `solution_direction`
   hoặc `category`, có thể làm lộ mã `rag`/mã nội bộ trên UI.
3. `frontend/src/pages/BidsPage.tsx:71-73`: đổi `dealStage` không reset phân trang, có thể tạo
   trạng thái trang rỗng không đúng dữ liệu.
4. `frontend/src/pages/BidDetailPage.tsx:479-481`: chỉ có xuất Q&A và trả lời trên màn hình;
   chưa có control nhập lại file Q&A. Các tài liệu cũ ghi export/import đầy đủ là không chính xác.
5. `frontend/src/pages/ApprovalsPage.tsx:196` và contract `api_contract.md:666-670`: proposal
   versions đã có contract nhưng frontend chưa tích hợp query/control để liệt kê, tạo hoặc đánh dấu
   phiên bản gửi khách; empty state hiện tại là trung thực nhưng chức năng còn thiếu.

 Chi tiết severity, acceptance runtime còn thiếu và verdict nằm trong `docs/ui/dot5_review.md`.
 API contract có proposal versions tại mục 10.0a; finding tương ứng là thiếu tích hợp frontend,
 không phải thiếu contract.

## Verification boundary

- Đây là review tĩnh và review tài liệu; không tạo bằng chứng Preview giả.
- `docs/ui/dot5_check.md` ghi nhận build pass và 7 frontend tests pass, nhưng chưa có walkthrough
  Preview đầy đủ nên acceptance runtime vẫn chưa được coi là PASS.

## DONE

- Đã cập nhật `docs/ui/dot5_review.md` với findings có file/dòng cụ thể.
- Đã sửa mâu thuẫn tài liệu về Q&A import để phản ánh đúng source hiện tại.
- Đã ghi handoff note này.
- Dừng tại boundary của vai trò reviewer.
