import type { SolutionDirection } from '../api/types';

export const SOLUTION_DIRECTION_LABELS: Record<SolutionDirection, string> = {
  none: 'Không cần AI',
  traditional_ml: 'ML truyền thống',
  rag: 'RAG',
  agent: 'Agent',
  fine_tune: 'Fine-tune',
};

const DIRECTIONS = Object.keys(SOLUTION_DIRECTION_LABELS) as SolutionDirection[];

interface Props {
  value: SolutionDirection;
  onChange: (direction: SolutionDirection) => void;
  disabled?: boolean;
}

export default function SolutionDirectionSelector({ value, onChange, disabled = false }: Props) {
  return (
    <fieldset disabled={disabled}>
      <legend className="text-sm font-semibold text-slate-900">Chọn hướng giải pháp</legend>
      <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {DIRECTIONS.map((direction) => (
          <label
            key={direction}
            className={`flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-3 text-sm transition-colors ${
              value === direction
                ? 'border-blue-500 bg-blue-50 text-blue-900'
                : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
            }`}
          >
            <input
              type="radio"
              name="solution-direction"
              value={direction}
              checked={value === direction}
              onChange={() => onChange(direction)}
              className="h-4 w-4 accent-blue-600"
            />
            <span>{SOLUTION_DIRECTION_LABELS[direction]}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
