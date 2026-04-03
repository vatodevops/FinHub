'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const items = [
  { href: '/', label: 'Dashboard', icon: '◫' },
  { href: '/accounts', label: 'Cuentas', icon: '◩' },
  { href: '/transactions', label: 'Transacciones', icon: '↹' },
  { href: '/calendar', label: 'Calendario', icon: '◷' },
  { href: '/manual', label: 'Gastos manuales', icon: '✎' },
  { href: '/connections', label: 'Conexiones', icon: '◎' },
  { href: '/investments', label: 'Inversiones', icon: '◈' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">F</div>
        <div>
          <div className="brand-title">FinHub</div>
          <div className="brand-subtitle">Workspace financiero</div>
        </div>
      </div>

      <nav className="nav">
        {items.map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className={`nav-item ${active ? 'active' : ''}`}>
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
