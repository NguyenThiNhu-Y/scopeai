import type { WbsItem, WbsPhase } from '../api/types';

/** Thứ tự hiển thị giai đoạn: poc → mvp → production (spec M4 §3.3). */
export const PHASE_ORDER: Record<WbsPhase, number> = { poc: 0, mvp: 1, production: 2 };

/** Map parent_code → danh sách item con (đã sắp xếp theo phase → sort_order → mã). */
export function buildChildrenMap(items: WbsItem[]): Map<string | null, WbsItem[]> {
  const map = new Map<string | null, WbsItem[]>();
  for (const item of items) {
    const key = item.parent_code ?? null;
    const bucket = map.get(key) ?? [];
    bucket.push(item);
    map.set(key, bucket);
  }
  for (const bucket of map.values()) {
    bucket.sort((a, b) => {
      const pa = PHASE_ORDER[a.phase] ?? 0;
      const pb = PHASE_ORDER[b.phase] ?? 0;
      if (pa !== pb) return pa - pb;
      if (a.sort_order !== b.sort_order) return a.sort_order - b.sort_order;
      return a.task_code.localeCompare(b.task_code);
    });
  }
  return map;
}

/** Duyệt cây theo thứ tự hiển thị (cha trước, con sau, đệ quy theo level). */
export function flattenTree(items: WbsItem[]): WbsItem[] {
  const children = buildChildrenMap(items);
  const out: WbsItem[] = [];
  const visit = (parentCode: string | null) => {
    for (const item of children.get(parentCode) ?? []) {
      out.push(item);
      visit(item.task_code);
    }
  };
  visit(null);
  return out;
}

/** Mã của item + toàn bộ hậu duệ (dùng để chặn chọn cha tạo vòng cây). */
export function getDescendantCodes(code: string, items: WbsItem[]): Set<string> {
  const children = buildChildrenMap(items);
  const result = new Set<string>([code]);
  const visit = (parentCode: string) => {
    for (const item of children.get(parentCode) ?? []) {
      result.add(item.task_code);
      visit(item.task_code);
    }
  };
  visit(code);
  return result;
}

/** Item có phải hậu duệ của candidate hay không (dùng khi đổi cha). */
export function isDescendantOf(code: string, candidateParent: string, items: WbsItem[]): boolean {
  return getDescendantCodes(candidateParent, items).has(code);
}