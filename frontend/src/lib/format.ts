import type { CustomerLanguage, WbsPhase, WbsRole, WorkingCalendar } from '../api/types';

/** Nhãn tiếng Việt cho ngôn ngữ khách (BR-07). */
export const LANGUAGE_LABELS: Record<CustomerLanguage, string> = {
  vi: 'Tiếng Việt',
  en: 'Tiếng Anh',
  ja: 'Tiếng Nhật',
};

/** Nhãn giai đoạn WBS (spec M4 §2.6). */
export const PHASE_LABELS: Record<WbsPhase, string> = {
  poc: 'PoC',
  mvp: 'MVP',
  production: 'Production',
};

/** Nhãn vai trò (bảng nhãn chung — spec M4 §2.6). */
export const ROLE_LABELS: Record<WbsRole, string> = {
  pm: 'PM',
  ba: 'BA',
  brse: 'BRSE',
  ai_engineer: 'AI Engineer',
  backend: 'Backend',
  frontend: 'Frontend',
  qa: 'QA',
  infra: 'Infra',
};

/** Nhãn lịch nghỉ (contract §8.4). */
export const WORKING_CALENDAR_LABELS: Record<WorkingCalendar, string> = {
  vn: 'Việt Nam',
  jp: 'Nhật Bản',
  both: 'Việt Nam + Nhật Bản',
};

export const CONTRACT_MODEL_LABELS = {
  fixed_price: 'Giá cố định',
  tm: 'Theo thời gian (T&M)',
  odc: 'Đội ngũ thuê ngoài (ODC)',
} as const;

/** Nhãn tiếng Việt cho hướng giải pháp (không hiện mã thô none/rag/...). */
export const SOLUTION_LABELS: Record<string, string> = {
  none: 'Không dùng AI',
  traditional_ml: 'Học máy truyền thống',
  rag: 'Tra cứu theo tài liệu',
  agent: 'Trợ lý nhiều bước',
  fine_tune: 'Tinh chỉnh mô hình',
};

/**
 * % đáp ứng = (◎ + ○) / tổng ĐÃ ĐÁNH GIÁ (stats từ GET /evaluations).
 * Trả null khi chưa có gì được đánh giá (không hiện "0%" gây hiểu lầm).
 */
export function coveragePercent(stats: Record<string, number>): number | null {
  const evaluated = stats.evaluated ?? 0;
  if (evaluated <= 0) return null;
  const done = (stats['◎'] ?? 0) + (stats['○'] ?? 0);
  return Math.round((done / evaluated) * 100);
}

/** Các khóa stats hiển thị trên thẻ Đáp ứng — loại total/evaluated khỏi giao diện. */
export const COVERAGE_DISPLAY_KEYS = ['◎', '○', '△', '×', 'cần làm rõ'] as const;

/** Định dạng ngày hoặc timestamp ISO thành "DD/MM/YYYY HH:mm" khi có giờ. */
export function formatDate(isoDate: string): string {
  const match = isoDate.match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/);
  if (!match) return isoDate;
  const [, year, month, day, hour, minute] = match;
  if (!hour || !minute) return `${day}/${month}/${year}`;
  return `${day}/${month}/${year} ${hour}:${minute}`;
}

/** Định dạng số tiền theo locale vi-VN. */
export function formatAmount(amount: number | null | undefined, currency = 'VND'): string {
  if (amount == null) return '—';
  const locale = currency === 'JPY' ? 'ja-JP' : currency === 'USD' ? 'en-US' : 'vi-VN';
  return new Intl.NumberFormat(locale, { style: 'currency', currency, maximumFractionDigits: 0 }).format(amount);
}

/** Định dạng effort mà không để lộ sai số floating-point sau khi cộng nhiều vai trò. */
export function formatManDay(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return '—';
  return new Intl.NumberFormat('vi-VN', {
    maximumFractionDigits: 1,
  }).format(Math.round((value + Number.EPSILON) * 10) / 10);
}
