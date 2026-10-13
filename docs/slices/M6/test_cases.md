# Bộ test case IPA — M6 Đính kèm và ma trận đáp ứng

## Tổng quan

- Phạm vi: upload, parse, confirm, pipeline/evaluation và trạng thái không có requirement.
- Môi trường dự kiến: Preview, `LLM_PROVIDER=mock`, dữ liệu giả lập.
- Template: IPA mặc định vì không có template riêng được chỉ định; đầu ra Markdown.
- Quy ước: mọi ca UI cần context Playwright mới; không sửa dữ liệu ứng dụng để làm ca kiểm thử pass.

## Field legend

| Trường | Ý nghĩa |
|---|---|
| TC-ID | Mã ca duy nhất |
| Function / Screen | Chức năng và màn hình/API |
| Viewpoint | 正常系, 準正常系, 異常系, 境界値, Validation, Security hoặc Combination |
| Precondition | Điều kiện trước khi chạy |
| Procedure | Các bước thao tác cụ thể |
| Expected Result | Kết quả quan sát được |
| Notes | Trace tới spec/rule và evidence |

## Hồ sơ mẫu và attachment

### TC-M6-001: Nạp hồ sơ mẫu M6

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-001 |
| **Function / Screen** | Nạp hồ sơ mẫu / BidNewPage |
| **Viewpoint** | 正常系 |
| **Test Item** | Tạo hồ sơ M6 đầy đủ bằng dữ liệu giả lập |
| **Precondition** | Preview đang chạy; chưa có yêu cầu đăng nhập |
| **Procedure** | 1. Mở trang tạo hồ sơ. 2. Chọn “Nạp hồ sơ mẫu đầy đủ”. 3. Mở hồ sơ vừa tạo. |
| **Expected Result** | 1. Điều hướng tới bid mới ở trạng thái `draft`. 2. Có RFP và file requirement/sample giả lập. 3. Không xuất hiện giá, effort hoặc lịch được sinh từ LLM. |
| **Notes** | Spec §5.2 bước 1; AGENTS rule 1, 5, 6. |

### TC-M6-002: Upload ba file hợp lệ và nhận diện loại

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-002 |
| **Function / Screen** | Upload attachment / BidDetailPage |
| **Viewpoint** | 正常系 |
| **Test Item** | Upload PDF RFP, XLSX requirement và CSV sample |
| **Precondition** | Bid draft tồn tại; ba fixture giả lập hợp lệ, mỗi file nhỏ hơn 20 MB |
| **Procedure** | 1. Chọn ba file cùng một lần. 2. Chờ danh sách attachment cập nhật. |
| **Expected Result** | 1. Có đúng ba item. 2. Loại được nhận diện lần lượt là `rfp`, `requirement`, `sample_data`. 3. Hiển thị quota `3/10` và kích thước từng file. 4. `parse_status=pending`. |
| **Notes** | Spec §2.1, §5.2 bước 2. |

### TC-M6-003: Từ chối file thứ 11 nhưng giữ mười file trước

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-003 |
| **Function / Screen** | Upload attachment / BidDetailPage |
| **Viewpoint** | 境界値 |
| **Test Item** | Kiểm tra giới hạn số file 10/11 |
| **Precondition** | Bid có đúng 10 attachment hợp lệ |
| **Procedure** | 1. Chọn thêm file hợp lệ thứ 11. 2. Kiểm tra thông báo và danh sách. |
| **Expected Result** | 1. File thứ 11 bị từ chối với mã `TOO_MANY_FILES`. 2. Danh sách vẫn có đủ 10 file cũ. 3. Không tạo attachment thứ 11 trong API. |
| **Notes** | Spec §2.1, §5.2 bước 3. |

### TC-M6-004: Từ chối file đúng ngưỡng và vượt ngưỡng kích thước

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-004 |
| **Function / Screen** | Upload attachment / API |
| **Viewpoint** | Boundary / Validation |
| **Test Item** | Kiểm tra 20 MB và 20 MB + 1 byte |
| **Precondition** | Bid draft; fixture có kích thước lần lượt 20 MB và 20 MB + 1 byte |
| **Procedure** | 1. Upload file đúng 20 MB. 2. Upload file 20 MB + 1 byte. |
| **Expected Result** | 1. File đúng giới hạn được tiếp nhận. 2. File vượt giới hạn bị từ chối với `FILE_TOO_LARGE`. 3. Không lưu file vượt giới hạn. |
| **Notes** | Spec §2.1, §5.2 bước 3. |

### TC-M6-005: Từ chối phần mở rộng không hỗ trợ và payload XSS trong tên file

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-005 |
| **Function / Screen** | Upload attachment / API và UI |
| **Viewpoint** | Validation / Security |
| **Test Item** | Kiểm tra extension không hợp lệ và hiển thị tên file an toàn |
| **Precondition** | Bid draft |
| **Procedure** | 1. Upload `payload.exe`. 2. Upload file có tên `<script>alert(1)</script>.txt`. 3. Quan sát DOM và response. |
| **Expected Result** | 1. `.exe` bị từ chối với `INVALID_FILE_TYPE`. 2. Tên file được encode như text, không chạy script. 3. Không phát sinh lỗi 500 hoặc attachment giả. |
| **Notes** | Spec §2.1; IPA Security XSS. |

## Parse, mapping và confirm gate

### TC-M6-006: Parse workbook hai sheet và sinh mã duy nhất

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-006 |
| **Function / Screen** | Parse review / FileParseReview |
| **Viewpoint** | 正常系 |
| **Test Item** | Đọc hai sheet requirement, trace source và formula `番号` |
| **Precondition** | Attachment XLSX hai sheet đã upload; có cột `番号` là công thức và dòng hợp lệ/lỗi |
| **Procedure** | 1. Bấm “Đọc file”. 2. Mở mapping từng sheet. 3. Kiểm tra requirement count và source row/sheet. |
| **Expected Result** | 1. Tất cả sheet được đọc. 2. Công thức không được dùng làm mã thật. 3. Mã nội bộ `REQ-xxx` duy nhất trên cả hai sheet. 4. Mỗi requirement có trace sheet/row. 5. Không tạo requirement cho dòng parse lỗi. |
| **Notes** | Spec §1.1, §5.1, §5.2 bước 4 và 6. |

### TC-M6-007: Sửa mapping và parse lại không nhân đôi dữ liệu

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-007 |
| **Function / Screen** | Mapping và parse lại / FileParseReview |
| **Viewpoint** | 準正常系 |
| **Test Item** | Đổi cột content/priority/category rồi parse lại |
| **Precondition** | Workbook có mapping tự động sai; parse lần đầu đã hoàn tất |
| **Procedure** | 1. Sửa mapping ba cột trên UI. 2. Bấm parse lại. 3. So sánh danh sách trước và sau. |
| **Expected Result** | 1. Attachment trở lại `pending` khi mapping đổi. 2. Nội dung/priority/category lấy từ cột mới. 3. Không có requirement cũ bị nhân đôi. 4. Tổng mã sau parse là tập duy nhất. |
| **Notes** | Spec §2.3, §5.2 bước 5. |

### TC-M6-008: Hiển thị profile dữ liệu mẫu và chỉnh readiness

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-008 |
| **Function / Screen** | Sample profile / FileParseReview |
| **Viewpoint** | 正常系 |
| **Test Item** | Kiểm tra row count, type, empty %, PII và readiness |
| **Precondition** | CSV sample giả lập có cột trống và cột email giả lập |
| **Procedure** | 1. Bấm “Đọc file”. 2. Mở phần profile. 3. Chọn readiness `medium`. |
| **Expected Result** | 1. Profile hiển thị row count, type, empty percentage và PII suspicion. 2. Có readiness suggestion `low|medium|high`. 3. Giá trị `medium` được giữ khi confirm. |
| **Notes** | Spec §1.1 bước 3-4, §2.5. |

### TC-M6-009: Chặn phân tích trước khi confirm

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-009 |
| **Function / Screen** | Parse confirm và pipeline start |
| **Viewpoint** | 異常系 |
| **Test Item** | UI và backend cùng chặn pipeline khi chưa confirm |
| **Precondition** | Parse đã đọc requirement nhưng `confirmed=false` |
| **Procedure** | 1. Quan sát nút “Phân tích”. 2. Nếu gọi trực tiếp, POST `/api/bids/{id}/pipeline/start`. 3. Lấy evaluations. |
| **Expected Result** | 1. UI khóa nút hoặc hiển thị lý do. 2. Backend từ chối start với lỗi trạng thái phù hợp. 3. Không có evaluation. 4. Không có effort/giá/lịch mới. |
| **Notes** | Spec §2.5, §5.2 bước 7; AGENTS rules 1, 4, 5. |

## Evaluation và trạng thái không có requirement

### TC-M6-010: Chạy evaluation theo lô và hiển thị ma trận

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-010 |
| **Function / Screen** | Pipeline và requirement matrix |
| **Viewpoint** | 正常系 |
| **Test Item** | Đánh giá 235 requirement theo lô tối đa 40 |
| **Precondition** | Workbook 235 dòng đã parse và confirm; mock gateway bật |
| **Procedure** | 1. Chọn readiness. 2. Bấm confirm. 3. Bấm “Phân tích”. 4. Theo dõi SSE. 5. Mở matrix. |
| **Expected Result** | 1. Có ít nhất 6 batch. 2. Mỗi batch không quá 40 dòng. 3. Tổng requirement là 235. 4. Matrix có rating `◎|○|△|×`, note tiếng Việt, `要確認` nếu có. 5. `stats.total` và `evaluated` phản ánh dữ liệu thật. |
| **Notes** | Spec §3.2, §5.1 và §5.2 bước 8; AGENTS rules 1, 2, 3. |

### TC-M6-011: Cảnh báo thiếu/trùng/thừa mã sau retry

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-011 |
| **Function / Screen** | B3 evaluation / RequirementMatrix |
| **Viewpoint** | 異常系 |
| **Test Item** | Mock response missing, duplicate và unknown code |
| **Precondition** | Parse confirmed; chọn từng fixture mock lỗi |
| **Procedure** | 1. Chạy evaluation với fixture missing. 2. Lặp với duplicate. 3. Lặp với unknown. 4. Mở warnings. |
| **Expected Result** | 1. Mỗi fixture retry tối đa 2 lần. 2. Warning liệt kê đúng mã thiếu/thừa/trùng. 3. Không hiển thị trạng thái complete giả. 4. Không âm thầm bỏ record. |
| **Notes** | Spec §3.2, §3.3 và §5.2 bước 9. |

### TC-M6-012: Không có Excel requirement thì ẩn matrix

| Field | Content |
|---|---|
| **TC-ID** | TC-M6-012 |
| **Function / Screen** | Parse review / BidDetailPage |
| **Viewpoint** | 準正常系 |
| **Test Item** | Hồ sơ chỉ có RFP/sample data |
| **Precondition** | Bid draft không có attachment loại `requirement` |
| **Procedure** | 1. Upload hoặc dùng hồ sơ chỉ có RFP và sample CSV. 2. Bấm “Đọc file”. 3. Mở phần matrix. |
| **Expected Result** | 1. `no_requirement_file=true`. 2. UI hiển thị “Khách không gửi file Excel requirement”. 3. Requirement matrix bị ẩn. 4. Không tạo requirement/evaluation giả. |
| **Notes** | Spec §2.4 và §5.2 bước 12. |
