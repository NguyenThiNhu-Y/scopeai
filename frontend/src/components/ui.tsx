import type { ReactNode } from 'react';

export function Card({ children, className = '', ...props }: { children: ReactNode; className?: string } & React.HTMLAttributes<HTMLElement>) {
  return <section className={`rounded-xl border border-[var(--line)] bg-[var(--surface)] p-5 ${className}`} {...props}>{children}</section>;
}

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'accent' }) {
  const tones = { neutral: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-100', success: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200', warning: 'bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-200', danger: 'bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-200', accent: 'bg-[var(--accent-soft)] text-[var(--accent-strong)]' };
  return <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${tones[tone]}`}>{children}</span>;
}

export function Stat({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return <div><dt className="text-xs font-medium text-[var(--muted)]">{label}</dt><dd className="mt-1 text-lg font-semibold tabular-nums text-[var(--ink)]">{value}</dd>{hint && <p className="mt-1 text-xs text-[var(--muted)]">{hint}</p>}</div>;
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <div role="status" className="rounded-xl border border-dashed border-[var(--line)] px-6 py-10 text-center"><h3 className="font-semibold text-[var(--ink)]">{title}</h3><p className="mx-auto mt-2 max-w-md text-sm text-[var(--muted)]">{description}</p>{action && <div className="mt-4">{action}</div>}</div>;
}

export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return <div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-100"><p>{message}</p>{onRetry && <button type="button" onClick={onRetry} className="mt-3 rounded-lg bg-[var(--danger)] px-3 py-1.5 font-semibold text-white">Thử lại</button>}</div>;
}

export function Spinner({ label = 'Đang tải' }: { label?: string }) {
  return <span role="status" className="inline-flex items-center gap-2 text-sm text-[var(--muted)]"><span aria-hidden="true" className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--line)] border-t-[var(--accent)]" />{label}</span>;
}

export function Table({ headers, children }: { headers: string[]; children: ReactNode }) {
  return <div className="overflow-x-auto rounded-xl border border-[var(--line)]"><table className="min-w-full divide-y divide-[var(--line)] text-left text-sm"><thead className="bg-[var(--accent-soft)]"><tr>{headers.map((header) => <th key={header} scope="col" className="whitespace-nowrap px-4 py-3 font-semibold text-[var(--ink)]">{header}</th>)}</tr></thead><tbody className="divide-y divide-[var(--line)] bg-[var(--surface)]">{children}</tbody></table></div>;
}
