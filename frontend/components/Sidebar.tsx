'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Wallet,
  ArrowLeftRight,
  PiggyBank,
  CalendarClock,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const items = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/accounts', label: 'Cuentas', icon: Wallet },
  { href: '/transactions', label: 'Transacciones', icon: ArrowLeftRight },
  { href: '/budgets', label: 'Presupuestos', icon: PiggyBank },
  { href: '/scheduled', label: 'Pagos programados', icon: CalendarClock },
  { href: '/reports', label: 'Informes', icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="bg-linear-to-b from-sidebar to-[#0a1020] border-r border-sidebar-border p-5 sticky top-0 h-screen max-lg:static max-lg:h-auto">
      <div className="flex items-center gap-3 mb-6 px-2 py-1.5">
        <div className="w-10 h-10 grid place-items-center rounded-xl bg-linear-to-b from-[#7aaeff] to-[#4779ff] text-[#07111f] font-black">
          F
        </div>
        <div>
          <div className="font-extrabold text-foreground">FinHub</div>
          <div className="text-muted-foreground text-sm">Workspace financiero</div>
        </div>
      </div>

      <nav className="grid gap-1.5">
        {items.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-muted-foreground transition-colors duration-150',
                active
                  ? 'bg-accent/12 text-foreground border border-accent/18'
                  : 'border border-transparent hover:bg-accent/8 hover:text-foreground'
              )}
            >
              <Icon className="w-[18px] h-[18px] opacity-90" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
