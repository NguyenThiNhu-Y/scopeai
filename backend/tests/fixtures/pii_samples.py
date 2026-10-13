"""Bộ mẫu PII — 100% GIẢ LẬP (BR-06). Không dùng tên/địa chỉ thật.

Phân bố (spec §6): 15 email, 15 SĐT VN, 15 SĐT Nhật, 5 văn bản hỗn hợp,
5 mẫu âm (không phải SĐT — không được che nhầm). Tổng 55 mẫu ≥ 50.
"""

# Emails (15)
EMAIL_SAMPLES = [
    'minh.nguyen@example.com',
    'tanaka.hanako@example.co.jp',
    'sales@congtyabc.vn',
    'MINH.NGUYEN@EXAMPLE.VN',
    'john.doe+tag@gmail.com',
    'thu.ha@sub.domain.example.net',
    'info@example.jp',
    'liên hệ qua email ngoc.le@example.com.vn',
    '連絡先: tanaka.hanako@example.co.jp まで',
    'a.b_c@example.org',
    'first.last-2@example.io',
    'contact@example.vn',
    'メール: sato.taro@example.co.jp',
    'hoa.tran@example.com',
    'phong.ban@example.jp',
]

# SĐT Việt Nam (15)
VN_PHONE_SAMPLES = [
    '0912345678',
    '(+84)912345678',
    '0084912345678',
    '091-234-5678',
    '0912 345 678',
    '0281234567',
    '028 1234 567',
    'SĐT: 0912345678',
    '091.234.5678',
    '0901234567',
    'Liên hệ anh Minh 0912345678 nhé',
    '0961234567',
    '0987654321',
    '0935 881 772',
    '0978 553 664',
]

# SĐT Nhật Bản (15)
JP_PHONE_SAMPLES = [
    '03-1234-5678',
    '08012345678',
    '09012345678',
    '07012345678',
    '0081 3 1234 5678',
    '03 1234 5678',
    '電話: 03-1234-5678',
    '06-1234-5678',
    '050-1234-5678',
    '03-9876-5432',
    '03-3344-5566',
    '06-7788-9900',
    '08055443322',
    '連絡先: 09099887766 です',
    '06-1122-3344',
]

# Văn bản hỗn hợp (5)
MIXED_SAMPLES = [
    'Khách hàng ABC: email sales@abc.jp, SĐT 0912345678, fax 03-1234-5678',
    '連絡先: tanaka@example.co.jp, 03-1234-5678, 0084912345678',
    'Anh Minh (minh.nguyen@example.com, 0912 345 678) và bà Tanaka (tanaka.hanako@example.co.jp, 08012345678)',
    'Email: info@example.vn — Điện thoại VN: 0281234567 — Điện thoại JP: 03-1234-5678',
    'お問い合わせ: support@example.co.jp または 09012345678 (日本) / 0912345678 (ベトナム)',
]

# Mẫu âm — không che (5)
NEGATIVE_SAMPLES = [
    'Hạn nộp: 12/05/2026',
    'Số lượng: 1,234,567 dòng',
    'Mã yêu cầu: REQ-001',
    'Ngân sách dự kiến: 50000000 JPY',
    'Phiên bản 2.0.1',
]

# Email/SĐT lẫn trong THÂN EMAIL tiếng Việt + tiếng Nhật (M2 — NFR-002, ≥ 10 mẫu)
EMAIL_BODY_SAMPLES = [
    # Thân email tiếng Việt (5)
    'Kính gửi anh Minh, email liên hệ minh.nguyen@example.com, điện thoại 0912345678. Trân trọng.',
    'Chào chị Hoa, tôi gửi báo giá qua thu.ha@example.com.vn, cần trao đổi gọi 0281234567 nhé.',
    'Xin chào, tôi là Ngọc (ngoc.le@example.com.vn). Anh chị vui lòng liên hệ 0912 345 678 để xác nhận.',
    'Phòng kinh doanh: sales@congtyabc.vn — hotline 0901234567 (giờ hành chính).',
    'Chúng tôi cần xác nhận đơn hàng, vui lòng gửi email cho phong.ban@example.jp hoặc gọi 0935 881 772.',
    # Thân email tiếng Nhật (5)
    'お世話になっております。ご連絡先: tanaka.hanako@example.co.jp、電話番号: 03-1234-5678 です。',
    'ご担当者様、資料を info@example.co.jp 宛にお送りください。ご不明点は 09099887766 まで。',
    '田中です。メール: sato.taro@example.co.jp、携帯: 08012345678 にご連絡ください。',
    '請求書に関するお問い合わせは support@example.co.jp、または 06-1234-5678 へお願いします。',
    '株式会社デモ商事（仮名・架空）の担当: tanaka.hanako@example.co.jp / 03-9876-5432。',
]

POSITIVE_SAMPLES = (
    EMAIL_SAMPLES
    + VN_PHONE_SAMPLES
    + JP_PHONE_SAMPLES
    + MIXED_SAMPLES
    + EMAIL_BODY_SAMPLES
)
ALL_SAMPLES = POSITIVE_SAMPLES + NEGATIVE_SAMPLES
