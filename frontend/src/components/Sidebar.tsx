import { NavLink } from 'react-router-dom';
import { useState } from 'react';

interface NavItem {
  to: string;
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { to: '/bids/new', label: '+ Tạo hồ sơ' },
  { to: '/bids', label: 'Hồ sơ' },
  { to: '/settings', label: 'Cài đặt' },
];

export default function Sidebar() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'));
  function toggleTheme() {
    document.documentElement.classList.toggle('dark');
    setDark(document.documentElement.classList.contains('dark'));
  }
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-[var(--line)] bg-[var(--surface)] max-md:w-20">
      <div className="flex items-center gap-3 border-b border-[var(--line)] px-6 py-5">
         <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--brand)] text-sm font-bold text-white">
           ✦
        </span>
        <div className="max-md:hidden">
           <p className="text-sm font-semibold text-[var(--ink)]">Trợ lý dự thầu</p>
           <p className="text-xs text-[var(--muted)]">Workspace nội bộ</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4" aria-label="Menu chính">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            aria-label={item.to === '/bids/new' ? 'Tạo hồ sơ' : item.label}
            className={({ isActive }) => {
              const isCreate = item.to === '/bids/new';
              return [
                'block rounded-md px-3 py-2 text-sm font-medium',
                isCreate
                  ? 'mb-4 bg-[var(--brand)] text-white hover:opacity-90'
                  : isActive
                    ? 'bg-[var(--brand-soft)] text-[var(--brand)]'
                    : 'text-[var(--muted)] hover:bg-[var(--brand-soft)] hover:text-[var(--ink)]',
              ].join(' ');
            }}
          >
            <span className="max-md:hidden">{item.label}</span><span className="hidden max-md:inline" aria-hidden="true">{item.label.slice(0, 1)}</span>
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-[var(--line)] px-4 py-4 text-xs text-[var(--muted)]">
        <p className="mb-3"><span className="mr-2 inline-block h-2 w-2 rounded-full bg-emerald-500" />LLM: mock</p>
        <button type="button" onClick={toggleTheme} className="w-full text-left hover:text-[var(--brand)]">{dark ? '☀ Chế độ sáng' : '☾ Chế độ tối'}</button>
      </div>
    </aside>
  );
}
