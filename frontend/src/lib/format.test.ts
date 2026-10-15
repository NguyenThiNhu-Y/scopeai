import { describe, expect, it } from 'vitest';
import { signalStatusMeta, MARKET_LABELS } from './format';

describe('signalStatusMeta — map nhãn tín hiệu độ tin cậy (Đợt 13, F.1)', () => {
  it('pass → Đạt với biểu tượng ✓ và tone pass', () => {
    const meta = signalStatusMeta('pass');
    expect(meta.label).toBe('Đạt');
    expect(meta.icon).toBe('✓');
    expect(meta.tone).toBe('pass');
  });

  it('warn → Cảnh báo với biểu tượng ⚠ và tone warn', () => {
    const meta = signalStatusMeta('warn');
    expect(meta.label).toBe('Cảnh báo');
    expect(meta.icon).toBe('⚠');
    expect(meta.tone).toBe('warn');
  });

  it('fail → Lỗi với biểu tượng ✕ và tone fail', () => {
    const meta = signalStatusMeta('fail');
    expect(meta.label).toBe('Lỗi');
    expect(meta.icon).toBe('✕');
    expect(meta.tone).toBe('fail');
  });

  it('na → Không có dữ liệu với biểu tượng – và tone na', () => {
    const meta = signalStatusMeta('na');
    expect(meta.label).toBe('Không có dữ liệu');
    expect(meta.icon).toBe('–');
    expect(meta.tone).toBe('na');
  });

  it('giá trị lạ fallback về Không có dữ liệu (không hiện mã thô)', () => {
    const meta = signalStatusMeta('unknown_status');
    expect(meta.label).toBe('Không có dữ liệu');
    expect(meta.tone).toBe('na');
  });
});

describe('MARKET_LABELS — nhãn thị trường case study', () => {
  it('map jp/vn/other sang nhãn tiếng Việt', () => {
    expect(MARKET_LABELS.jp).toBe('Nhật Bản');
    expect(MARKET_LABELS.vn).toBe('Việt Nam');
    expect(MARKET_LABELS.other).toBe('Khác');
  });
});