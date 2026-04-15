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
  LogOut,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';

const items = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/accounts', label: 'Cuentas', icon: Wallet },
  { href: '/transactions', label: 'Transacciones', icon: ArrowLeftRight },
  { href: '/budgets', label: 'Presupuestos', icon: PiggyBank },
  { href: '/scheduled', label: 'Pagos programados', icon: CalendarClock },
  { href: '/reports', label: 'Informes', icon: BarChart3 },
  { href: '/settings/sessions', label: 'Sesiones', icon: ShieldCheck },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="bg-linear-to-b from-sidebar to-[#0a1020] border-r border-sidebar-border p-5 sticky top-0 h-screen max-lg:static max-lg:h-auto flex flex-col">
      <div className="flex items-center gap-3 mb-6 px-2 py-1.5">
        <div className="w-10 h-10 grid place-items-center rounded-xl bg-linear-to-b from-[#7aaeff] to-[#4779ff] text-[#07111f] font-black">
          F
        </div>
        <div>
          <div className="font-extrabold text-foreground">FinHub</div>
          <div className="text-muted-foreground text-sm">Workspace financiero</div>
        </div>
      </div>

      <nav className="grid gap-1.5 flex-1">
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

      <div className="mt-6 border-t border-border pt-4">
        <div className="px-3 py-2 rounded-xl bg-white/[0.03] border border-border">
          <div className="flex items-center gap-3">
            {user?.picture_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={user.picture_url}
                alt={user.full_name || user.email}
                className="w-9 h-9 rounded-full object-cover border border-border"
                referrerPolicy="no-referrer"
              />
            ) : (
              <div className="w-9 h-9 rounded-full bg-accent/20 flex items-center justify-center text-sm font-medium text-foreground">
                {(user?.full_name || user?.email || '?').slice(0, 1).toUpperCase()}
              </div>
            )}
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium text-foreground truncate">{user?.full_name || 'Usuario'}</div>
              <div className="text-xs text-muted-foreground truncate">{user?.email}</div>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-accent/8 transition-colors text-sm"
          >
            <LogOut className="w-4 h-4" />
            Cerrar sesion
          </button>
        </div>
      </div>
    </aside>
  );
}
