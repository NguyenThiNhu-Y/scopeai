# Handoff — M3-01..M3-05 dữ liệu mẫu và mock

## Phạm vi

- Đã thay 36 dòng trong `sample_data/ja_requirements.xlsx` bằng requirement CRM Nhật riêng biệt.
- Mã requirement dùng `FR-001..FR-027` và `NFR-001..NFR-009`; nội dung bao phủ khách hàng, hoạt động, tìm kiếm, di trú Excel, báo cáo, tích hợp, quyền, hiệu năng, bảo mật, sao lưu và vận hành.
- Mock LLM phân loại `EvaluationBatch` theo nội dung, trả nhiều mức `◎/○/△` và ghi chú riêng từng requirement.
- Mock solution nhận diện CRM/dữ liệu có cấu trúc, chọn `none` và giải thích loại RAG/agent/ML/fine-tune.
- Mock intake đọc context RFP có ngân sách/lịch và trả ghi chú tương ứng; không đưa số tính effort/giá vào output schema.
- Mock vòng hỏi thứ hai trả câu hỏi vận hành khác vòng đầu; service lọc câu hỏi trùng lặp ở mọi vòng.
- Factor `many_requirements` chỉ bật khi có số lượng requirement thực tế (`None` không còn bị coi là 0/đoán từ text).

## File đã sửa/thêm

- `sample_data/ja_requirements.xlsx`
- `backend/app/llm/mock_client.py`
- `backend/app/services/clarify_service.py`
- `backend/app/services/factor_engine.py`
- `backend/tests/test_m3_sample_and_mock.py`

## Không sửa

- Không sửa frontend.
- Không gọi LLM thật.
- Không đụng file chung của nhánh B3 ngoài `mock_client.py`; thay đổi mock là additive ở `_content_fixture`, dễ cherry-pick/merge. Nếu B3 cũng sửa cùng file, ưu tiên giữ registry fixture hiện có và ghép riêng hàm phân loại + nhánh `EvaluationBatch`.

## Kiểm thử

- BLOCKER: môi trường hiện tại không có package pytest (`pytest: command not found`, `python3 -m pytest`: `No module named pytest`), nên chưa thể chạy test liên quan.
- Đã kiểm tra workbook bằng openpyxl: 36 requirement, mã FR/NFR duy nhất, nội dung duy nhất.
- Không chạy lặp test quá 2 lần; đã thử lệnh pytest trực tiếp và module sau khi phát hiện thiếu runtime.

## Tự review

- Schema LLM vẫn giữ `extra="forbid"`; số ngân sách/lịch chỉ nằm trong RFP context và ghi chú intake.
- Dữ liệu mẫu là giả lập, không thêm tên khách hàng thật.
- Cần role kế tiếp cài/khởi tạo dependency test của backend rồi chạy focused tests và full acceptance; đây là blocker môi trường, không phải failure logic đã quan sát.

DONE — có blocker kiểm thử cụ thể: thiếu pytest trong runtime.
