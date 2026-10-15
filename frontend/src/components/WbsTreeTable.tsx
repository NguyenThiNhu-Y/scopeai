import { useEffect, useId, useMemo, useRef, useState } from 'react';
import type { WbsChange, WbsItem, WbsPhase, WbsRole } from '../api/types';
import { PHASE_LABELS, ROLE_LABELS } from '../lib/format';
import { flattenTree } from '../lib/wbs';

const PHASES = Object.keys(PHASE_LABELS) as WbsPhase[];
const ROLES = Object.keys(ROLE_LABELS) as WbsRole[];

const inputClass =
  'w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:bg-slate-50 disabled:text-slate-400';

/** Một dòng đang chỉnh sửa (item có sẵn hoặc dòng mới thêm). */
interface DraftRow {
  key: string;
  task_code: string;
  name_vi: string;
  phase: WbsPhase;
  parent_code: string | null;
  role: WbsRole | null;
  man_day: number | null;
  is_new: boolean;
  is_leaf: boolean;
  requirement_codes: string[];
}

interface WbsTreeTableProps {
  items: WbsItem[];
  saving: boolean;
  /**
   * Gọi MỘT lần với toàn bộ thay đổi (add/update/remove) khi bấm "Lưu thay đổi".
   * Backend tính lại tổng man-day + lịch và trả recalculated.schedule.
   */
  onSaveChanges: (changes: WbsChange[], note?: string) => void;
  disabled?: boolean;
  /** Map mã requirement → nội dung (hover chip hiện nội dung). */
  requirementContents?: Record<string, string>;
  /** Danh sách mã requirement có thể gán (datalist gợi ý khi sửa). */
  availableRequirementCodes?: string[];
}

function toDraft(item: WbsItem): DraftRow {
  return {
    key: item.task_code,
    task_code: item.task_code,
    name_vi: item.name_vi,
    phase: item.phase,
    parent_code: item.parent_code,
    role: item.role,
    man_day: item.man_day,
    is_new: false,
    is_leaf: item.is_leaf,
    requirement_codes: item.requirement_codes ?? [],
  };
}

type DisplayRow =
  | { kind: 'item'; item: WbsItem; draft: DraftRow }
  | { kind: 'new'; draft: DraftRow; level: number }
  | { kind: 'add'; parentCode: string | null; label: string };

/**
 * Bảng WBS 3 cấp sửa TRỰC TIẾP trong dòng (Đợt 10, E.4):
 * - Tên task, giai đoạn, vai trò, man-day là input/select ngay trong row.
 * - Mã và tên cùng một dòng; "+ Thêm task" ở cuối mỗi nhóm.
 * - Một nút "Lưu thay đổi" cho cả bảng → PUT /wbs một lần.
 */
export default function WbsTreeTable({ items, saving, onSaveChanges, disabled = false, requirementContents = {}, availableRequirementCodes = [] }: WbsTreeTableProps) {
  const [drafts, setDrafts] = useState<Record<string, DraftRow>>({});
  const [removals, setRemovals] = useState<Set<string>>(new Set());
  const [errors, setErrors] = useState<string[]>([]);
  const counter = useRef(0);

  useEffect(() => {
    setDrafts(Object.fromEntries(items.map((item) => [item.task_code, toDraft(item)])));
    setRemovals(new Set());
    setErrors([]);
  }, [items]);

  const itemById = useMemo(() => new Map(items.map((item) => [item.task_code, item])), [items]);

  function updateField(key: string, patch: Partial<DraftRow>) {
    setDrafts((prev) => ({ ...prev, [key]: { ...prev[key], ...patch } }));
    setErrors([]);
  }

  function addTask(parentCode: string | null) {
    const parent = parentCode ? itemById.get(parentCode) : undefined;
    const isLeaf = (parent?.level ?? 0) >= 2;
    const key = `new-${++counter.current}`;
    setDrafts((prev) => ({
      ...prev,
      [key]: {
        key,
        task_code: '',
        name_vi: '',
        phase: parent?.phase ?? 'poc',
        parent_code: parentCode,
        role: null,
        man_day: null,
        is_new: true,
        is_leaf: isLeaf,
        requirement_codes: [],
      },
    }));
    setErrors([]);
  }

  function removeTask(key: string) {
    setDrafts((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
    setRemovals((prev) => new Set([...prev, key]));
    setErrors([]);
  }

  function resetDrafts() {
    setDrafts(Object.fromEntries(items.map((item) => [item.task_code, toDraft(item)])));
    setRemovals(new Set());
    setErrors([]);
  }

  function buildChanges(): WbsChange[] | null {
    const problems: string[] = [];
    const existingCodes = new Set(items.map((item) => item.task_code));
    const newCodes = new Set<string>();
    const changes: WbsChange[] = [];

    for (const draft of Object.values(drafts)) {
      if (draft.is_new) {
        const code = draft.task_code.trim();
        if (!code) {
          problems.push('Dòng mới cần nhập mã task.');
          continue;
        }
        if (existingCodes.has(code) || newCodes.has(code)) {
          problems.push(`Mã "${code}" đã tồn tại trong WBS.`);
          continue;
        }
        newCodes.add(code);
        if (!draft.name_vi.trim()) {
          problems.push(`Task "${code}" cần nhập tên công việc.`);
          continue;
        }
        if (draft.is_leaf) {
          if (!draft.role) {
            problems.push(`Task "${code}" (lá) bắt buộc chọn vai trò.`);
            continue;
          }
          if (draft.man_day == null || !Number.isFinite(draft.man_day) || draft.man_day <= 0) {
            problems.push(`Task "${code}" (lá) bắt buộc nhập man-day > 0.`);
            continue;
          }
          if (draft.man_day > 10) {
            problems.push(`Man-day của task "${code}" tối đa 10 (FR-032.1).`);
            continue;
          }
        }
        changes.push({
          op: 'add',
          task: {
            task_code: code,
            name_vi: draft.name_vi.trim(),
            phase: draft.phase,
            parent_code: draft.parent_code,
            role: draft.is_leaf ? draft.role : null,
            man_day: draft.is_leaf ? draft.man_day : null,
            weight: null,
            depends_on: [],
            requirement_codes: draft.is_leaf ? draft.requirement_codes : [],
          },
        });
        continue;
      }

      const original = itemById.get(draft.key);
      if (!original) continue;
      const fields: Extract<WbsChange, { op: 'update' }>['fields'] = {};
      if (original.name_vi !== draft.name_vi.trim()) fields.name_vi = draft.name_vi.trim();
      if (original.phase !== draft.phase) fields.phase = draft.phase;
      if (original.is_leaf) {
        if (original.role !== draft.role) fields.role = draft.role;
        if (original.man_day !== draft.man_day) fields.man_day = draft.man_day;
        if ((original.requirement_codes ?? []).join(',') !== draft.requirement_codes.join(',')) {
          fields.requirement_codes = draft.requirement_codes;
        }
      }
      if (Object.keys(fields).length > 0) {
        changes.push({ op: 'update', task_code: draft.key, fields });
      }
    }

    for (const code of removals) {
      changes.push({ op: 'remove', task_code: code });
    }

    if (problems.length > 0) {
      setErrors(problems);
      return null;
    }
    return changes;
  }

  function handleSave() {
    const changes = buildChanges();
    if (changes) onSaveChanges(changes);
  }

  const rows = flattenTree(items).filter((item) => !removals.has(item.task_code));

  const displayRows = useMemo<DisplayRow[]>(() => {
    const build = (parentCode: string | null): DisplayRow[] => {
      const children = rows.filter((item) => item.parent_code === parentCode);
      const newKids = Object.values(drafts).filter(
        (draft) => draft.is_new && draft.parent_code === parentCode,
      );
      const out: DisplayRow[] = [];
      for (const child of children) {
        const draft = drafts[child.task_code];
        if (!draft) continue;
        out.push({ kind: 'item', item: child, draft });
        out.push(...build(child.task_code));
      }
      out.push(...newKids.map((draft) => ({ kind: 'new', draft, level: (itemById.get(parentCode ?? '')?.level ?? 0) + 1 }) as DisplayRow));
      if (parentCode === null) {
        out.push({ kind: 'add', parentCode: null, label: '＋ Thêm nhóm cấp 1' });
      } else {
        const parent = itemById.get(parentCode);
        if (parent && parent.level <= 2) {
          out.push({ kind: 'add', parentCode, label: '＋ Thêm task' });
        }
      }
      return out;
    };
    return build(null);
  }, [rows, drafts, itemById]);

  const changeCount = useMemo(() => {
    const edits = Object.values(drafts).filter((draft) => {
      if (draft.is_new) return true;
      const original = itemById.get(draft.key);
      if (!original) return false;
      return (
        original.name_vi !== draft.name_vi.trim() ||
        original.phase !== draft.phase ||
        (original.is_leaf &&
          (original.role !== draft.role ||
            original.man_day !== draft.man_day ||
            (original.requirement_codes ?? []).join(',') !== draft.requirement_codes.join(',')))
      );
    }).length;
    return edits + removals.size;
  }, [drafts, removals, itemById]);

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full min-w-[880px] border-collapse text-left">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50">
            <th className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Mã & tên công việc</th>
            <th className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Giai đoạn</th>
            <th className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Vai trò</th>
            <th className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Man-day</th>
            <th className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Requirement</th>
            <th className="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Thao tác</th>
          </tr>
        </thead>
        <tbody>
          {displayRows.length === 0 && (
            <tr>
              <td colSpan={6} className="px-3 py-8 text-center text-sm text-slate-500">
                Chưa có task nào trong WBS.
              </td>
            </tr>
          )}
          {displayRows.map((row) => {
            if (row.kind === 'item') {
              return (
                <WbsItemRow
                  key={row.item.task_code}
                  item={row.item}
                  draft={row.draft}
                  updateField={updateField}
                  onRemove={() => removeTask(row.draft.key)}
                  requirementContents={requirementContents}
                  availableRequirementCodes={availableRequirementCodes}
                />
              );
            }
            if (row.kind === 'new') {
              return (
                <WbsNewRow
                  key={row.draft.key}
                  draft={row.draft}
                  level={row.level}
                  updateField={updateField}
                  onRemove={() => removeTask(row.draft.key)}
                  requirementContents={requirementContents}
                  availableRequirementCodes={availableRequirementCodes}
                />
              );
            }
            return (
              <AddTaskRow key={`add-${row.parentCode ?? 'root'}`} label={row.label} onClick={() => addTask(row.parentCode)} />
            );
          })}
          <tr className="border-t border-slate-200 bg-slate-50/70">
            <td colSpan={6} className="px-3 py-3">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-slate-500">
                  {changeCount > 0 ? `${changeCount} thay đổi chưa lưu` : 'Không có thay đổi nào.'}
                  {' · Lưu xong tổng man-day và lịch sẽ được tính lại bằng code.'}
                </p>
                <div className="flex items-center gap-2">
                  {changeCount > 0 && (
                    <button
                      type="button"
                      onClick={resetDrafts}
                      disabled={saving || disabled}
                      className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                    >
                      Hủy thay đổi
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={handleSave}
                    disabled={saving || disabled || changeCount === 0}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {saving ? 'Đang lưu…' : 'Lưu thay đổi'}
                  </button>
                </div>
              </div>
              {errors.length > 0 && (
                <ul role="alert" className="mt-2 space-y-1 text-xs text-red-700">
                  {errors.map((error) => <li key={error}>• {error}</li>)}
                </ul>
              )}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

function WbsItemRow({
  item,
  draft,
  updateField,
  onRemove,
  requirementContents,
  availableRequirementCodes,
}: {
  item: WbsItem;
  draft: DraftRow;
  updateField: (key: string, patch: Partial<DraftRow>) => void;
  onRemove: () => void;
  requirementContents: Record<string, string>;
  availableRequirementCodes: string[];
}) {
  const pad = { paddingLeft: `${(item.level - 1) * 1.5}rem` };
  return (
    <tr className="border-b border-slate-100 hover:bg-slate-50/60">
      <td className="px-3 py-2 align-top">
        <div className="flex items-center gap-2" style={pad}>
          <span className="shrink-0 font-mono text-xs font-medium text-slate-500">{item.task_code}</span>
          <input
            value={draft.name_vi}
            onChange={(event) => updateField(draft.key, { name_vi: event.target.value })}
            aria-label={`Tên công việc ${item.task_code}`}
            className={`${inputClass} min-w-0 flex-1`}
          />
        </div>
      </td>
      <td className="px-3 py-2 align-top">
        <PhaseSelect value={draft.phase} onChange={(phase) => updateField(draft.key, { phase })} />
      </td>
      <td className="px-3 py-2 align-top text-sm text-slate-700">
        {draft.is_leaf ? (
          <RoleSelect value={draft.role} onChange={(role) => updateField(draft.key, { role })} />
        ) : (
          <span className="text-slate-400">—</span>
        )}
      </td>
      <td className="px-3 py-2 align-top text-sm tabular-nums text-slate-700">
        {draft.is_leaf ? (
          <input
            type="number"
            min={0.5}
            max={10}
            step={0.5}
            value={draft.man_day ?? ''}
            onChange={(event) =>
              updateField(draft.key, { man_day: event.target.value === '' ? null : Number(event.target.value) })
            }
            aria-label={`Man-day ${item.task_code}`}
            className={`${inputClass} w-20 tabular-nums`}
          />
        ) : (
          (item.man_day ?? '—')
        )}
      </td>
      <td className="px-3 py-2 align-top">
        {draft.is_leaf ? (
          <RequirementCell
            codes={draft.requirement_codes}
            available={availableRequirementCodes}
            contents={requirementContents}
            onChange={(requirement_codes) => updateField(draft.key, { requirement_codes })}
          />
        ) : (
          <span className="text-slate-400">—</span>
        )}
      </td>
      <td className="px-3 py-2 align-top">
        <button
          type="button"
          onClick={onRemove}
          title={item.level < 3 ? 'Xóa task và toàn bộ sub-tree' : 'Xóa task'}
          className="rounded-md border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
        >
          <span className="sr-only">Xóa {item.task_code}</span>🗑
        </button>
      </td>
    </tr>
  );
}

function WbsNewRow({
  draft,
  level,
  updateField,
  onRemove,
  requirementContents,
  availableRequirementCodes,
}: {
  draft: DraftRow;
  level: number;
  updateField: (key: string, patch: Partial<DraftRow>) => void;
  onRemove: () => void;
  requirementContents: Record<string, string>;
  availableRequirementCodes: string[];
}) {
  const pad = { paddingLeft: `${(level - 1) * 1.5}rem` };
  return (
    <tr className="border-b border-blue-100 bg-blue-50/40">
      <td className="px-3 py-2 align-top">
        <div className="flex items-center gap-2" style={pad}>
          <input
            value={draft.task_code}
            onChange={(event) => updateField(draft.key, { task_code: event.target.value })}
            placeholder="Mã task"
            aria-label={`Mã task dòng mới ${draft.key}`}
            className={`${inputClass} w-28 shrink-0 font-mono`}
          />
          <input
            value={draft.name_vi}
            onChange={(event) => updateField(draft.key, { name_vi: event.target.value })}
            placeholder="Tên công việc"
            aria-label={`Tên công việc dòng mới ${draft.key}`}
            className={`${inputClass} min-w-0 flex-1`}
          />
        </div>
      </td>
      <td className="px-3 py-2 align-top">
        <PhaseSelect value={draft.phase} onChange={(phase) => updateField(draft.key, { phase })} />
      </td>
      <td className="px-3 py-2 align-top">
        {draft.is_leaf ? (
          <RoleSelect value={draft.role} onChange={(role) => updateField(draft.key, { role })} />
        ) : (
          <span className="text-sm text-slate-400">—</span>
        )}
      </td>
      <td className="px-3 py-2 align-top">
        {draft.is_leaf ? (
          <input
            type="number"
            min={0.5}
            max={10}
            step={0.5}
            value={draft.man_day ?? ''}
            onChange={(event) =>
              updateField(draft.key, { man_day: event.target.value === '' ? null : Number(event.target.value) })
            }
            placeholder="0.5–10"
            aria-label={`Man-day dòng mới ${draft.key}`}
            className={`${inputClass} w-20 tabular-nums`}
          />
        ) : (
          <span className="text-sm text-slate-400">—</span>
        )}
      </td>
      <td className="px-3 py-2 align-top">
        {draft.is_leaf ? (
          <RequirementCell
            codes={draft.requirement_codes}
            available={availableRequirementCodes}
            contents={requirementContents}
            onChange={(requirement_codes) => updateField(draft.key, { requirement_codes })}
          />
        ) : (
          <span className="text-sm text-slate-400">—</span>
        )}
      </td>
      <td className="px-3 py-2 align-top">
        <button
          type="button"
          onClick={onRemove}
          className="rounded-md border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
        >
          <span className="sr-only">Bỏ dòng mới</span>✕
        </button>
      </td>
    </tr>
  );
}

function AddTaskRow({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <tr className="border-b border-slate-100 bg-slate-50/40">
      <td colSpan={6} className="px-3 py-1.5">
        <button
          type="button"
          onClick={onClick}
          className="text-xs font-semibold text-blue-700 hover:text-blue-900"
        >
          {label}
        </button>
      </td>
    </tr>
  );
}

function PhaseSelect({ value, onChange }: { value: WbsPhase; onChange: (phase: WbsPhase) => void }) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value as WbsPhase)}
      className={`${inputClass} w-32`}
    >
      {PHASES.map((phase) => (
        <option key={phase} value={phase}>{PHASE_LABELS[phase]}</option>
      ))}
    </select>
  );
}

function RoleSelect({ value, onChange }: { value: WbsRole | null; onChange: (role: WbsRole | null) => void }) {
  return (
    <select
      value={value ?? ''}
      onChange={(event) => onChange((event.target.value || null) as WbsRole | null)}
      className={`${inputClass} w-36`}
    >
      <option value="">— Chọn vai trò —</option>
      {ROLES.map((role) => (
        <option key={role} value={role}>{ROLE_LABELS[role]}</option>
      ))}
    </select>
  );
}

/**
 * Ô "Requirement" trong WBS (thiet_ke_danh_gia.md §7): chip mã tối đa 3 rồi "+n",
 * hover hiện nội dung requirement; bấm ✎ để sửa (input mã cách nhau dấu phẩy,
 * datalist gợi ý mã có sẵn). Chỉ hiển thị trên task lá — backend chặn task nhóm.
 */
function RequirementCell({
  codes,
  available,
  contents,
  onChange,
}: {
  codes: string[];
  available: string[];
  contents: Record<string, string>;
  onChange: (codes: string[]) => void;
}) {
  const listId = useId();
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(codes.join(', '));

  function commit() {
    const parsed = text
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean);
    // Bỏ trùng, giữ thứ tự, tối đa 8 mã (khớp backend WbsTaskIn.max_length=8).
    const unique = Array.from(new Set(parsed)).slice(0, 8);
    onChange(unique);
    setText(unique.join(', '));
    setEditing(false);
  }

  if (editing) {
    return (
      <div className="flex items-center gap-1">
        <input
          value={text}
          onChange={(event) => setText(event.target.value)}
          onBlur={commit}
          onKeyDown={(event) => {
            if (event.key === 'Enter') commit();
            if (event.key === 'Escape') {
              setText(codes.join(', '));
              setEditing(false);
            }
          }}
          list={listId}
          aria-label="Mã requirement (cách nhau dấu phẩy)"
          className={`${inputClass} w-44 font-mono text-xs`}
          placeholder="FR-001, NFR-002"
        />
        <datalist id={listId}>
          {available.map((code) => <option key={code} value={code} />)}
        </datalist>
      </div>
    );
  }

  if (codes.length === 0) {
    return (
      <button type="button" onClick={() => { setText(''); setEditing(true); }} className="text-xs text-slate-400 hover:text-blue-600">
        + Gán
      </button>
    );
  }

  const shown = codes.slice(0, 3);
  const rest = codes.length - 3;
  return (
    <div className="flex flex-wrap items-center gap-1">
      {shown.map((code) => (
        <span key={code} title={contents[code] ?? code} className="rounded bg-blue-50 px-1.5 py-0.5 font-mono text-xs text-blue-700">
          {code}
        </span>
      ))}
      {rest > 0 && (
        <span title={codes.slice(3).join(', ')} className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600">
          +{rest}
        </span>
      )}
      <button
        type="button"
        onClick={() => { setText(codes.join(', ')); setEditing(true); }}
        aria-label="Sửa mã requirement"
        className="text-xs text-slate-400 hover:text-blue-600"
      >
        ✎
      </button>
    </div>
  );
}