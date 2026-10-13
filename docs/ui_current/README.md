# Ảnh UI runtime

Bộ ảnh được tạo trực tiếp từ Preview với LLM mock bằng Chromium bundled, bao phủ
tạo hồ sơ, danh sách hồ sơ và đủ 7 tab của hồ sơ mẫu tiếng Nhật ở hai viewport
`1440x900` và `1280x900`.

`runtime_report.json` là báo cáo kèm theo. Console và request thất bại đều rỗng;
các phản hồi 409 được phân loại riêng là state conflict dự kiến của mock data chưa
có output pipeline, không phải lỗi tải tài nguyên.
