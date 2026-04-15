'use client';

import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MetricCard } from '@/components/MetricCard';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api, type Overview, type Transaction, type RecurringOccurrence, type Budget } from '@/lib/api';
import { filterVisibleTransactions } from '@/lib/curve';
import { cn } from '@/lib/utils';

function money(value: string | number) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export default function HomePage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [calendar, setCalendar] = useState<RecurringOccurrence[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const now = new Date();
    let cancelled = false;
    (async () => {
      const settle = async <T,>(p: Promise<T>, fallback: T, label: string): Promise<T> => {
        try {
          return await p;
        } catch (err) {
          console.error(`Dashboard: ${label} falló`, err);
          if (!cancelled) setError((prev) => prev ?? `${label}: ${(err as Error).message}`);
          return fallback;
        }
      };
      const [o, t, c, b] = await Promise.all([
        settle(api.overview(), null, 'overview'),
        settle(api.transactions(), [] as Transaction[], 'transactions'),
        settle(api.recurringCalendar(), [] as RecurringOccurrence[], 'calendar'),
        settle(api.budgets(now.getMonth() + 1, now.getFullYear()), [] as Budget[], 'budgets'),
      ]);
      if (cancelled) return;
      setOverview(o);
      setTransactions(filterVisibleTransactions(t));
      setCalendar(c);
      setBudgets(b);
      setLoading(false);
    })();
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div className="max-w-[1440px] mx-auto">
        <Topbar title="Dashboard" subtitle="Cargando..." />
        <div className="flex items-center justify-center py-20 text-muted-foreground">Cargando datos...</div>
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="max-w-[1440px] mx-auto">
        <Topbar title="Dashboard" subtitle="No se pudieron cargar los datos." />
        <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
          Error al cargar el dashboard{error ? `: ${error}` : ''}.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Dashboard" subtitle="Vision general del mes, proximos cargos y actividad reciente." />

      <div className="grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-4">
        <MetricCard label="Ingresos mes" value={money(overview.booked_income_month)} tone="positive" />
        <MetricCard label="Gastos mes" value={money(overview.booked_expense_month)} tone="negative" />
        <MetricCard label="Neto mes" value={money(overview.net_month)} tone={Number(overview.net_month) >= 0 ? 'positive' : 'negative'} />
        <MetricCard label="Proximos recurrentes" value={money(overview.recurring_due_upcoming)} />
        <MetricCard label="Cuentas" value={`${overview.account_count}`} hint={`${overview.transaction_count} movimientos`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1.15fr_0.85fr] gap-4 mt-4">
        {/* Recent transactions */}
        <PageSection title="Actividad reciente" subtitle="Ultimos movimientos registrados.">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fecha</TableHead>
                <TableHead>Concepto</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead className="text-right">Importe</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.slice(0, 10).map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell className="whitespace-nowrap">{tx.booked_at ? tx.booked_at.slice(0, 10) : '\u2014'}</TableCell>
                  <TableCell>{tx.merchant_clean || tx.merchant_raw || '\u2014'}</TableCell>
                  <TableCell>{tx.category_name ? <Badge variant="outline">{tx.category_name}</Badge> : <span className="text-muted-foreground">\u2014</span>}</TableCell>
                  <TableCell className={cn('text-right font-medium', Number(tx.amount) >= 0 ? 'text-success' : 'text-destructive')}>{money(tx.amount)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </PageSection>

        <div className="grid gap-4">
          {/* Budget progress */}
          {budgets.length > 0 && (
            <PageSection title="Presupuestos" subtitle="Progreso del mes actual.">
              <div className="grid gap-2.5">
                {budgets.slice(0, 4).map((b) => {
                  const pct = Number(b.amount_limit) > 0 ? (Number(b.spent) / Number(b.amount_limit)) * 100 : 0;
                  const barColor = pct > 100 ? 'bg-destructive' : pct > 80 ? 'bg-yellow-500' : 'bg-success';
                  return (
                    <div key={b.id} className="px-3.5 py-3 rounded-xl border border-border bg-white/[0.02]">
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          {b.category_color && <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: b.category_color }} />}
                          <span className="text-sm font-medium">{b.category_name}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">{money(b.spent)} / {money(b.amount_limit)}</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-white/[0.06] overflow-hidden">
                        <div className={cn('h-full rounded-full transition-all', barColor)} style={{ width: `${Math.min(pct, 100)}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </PageSection>
          )}

          {/* Upcoming payments */}
          <PageSection title="Proximos pagos" subtitle="Calendario financiero esperado.">
            <div className="grid gap-2.5">
              {calendar.slice(0, 5).map((occ) => (
                <div key={occ.id} className="flex justify-between items-center gap-3 px-3.5 py-3 rounded-xl border border-border bg-white/[0.02]">
                  <div className="grid gap-1">
                    <strong>{occ.expected_date}</strong>
                    <span className="text-muted-foreground text-sm">Pago recurrente esperado</span>
                  </div>
                  <div className="font-medium">{occ.expected_amount ? money(occ.expected_amount) : '\u2014'}</div>
                </div>
              ))}
              {calendar.length === 0 && (
                <div className="text-center text-muted-foreground py-4 text-sm">Sin pagos pendientes</div>
              )}
            </div>
          </PageSection>
        </div>
      </div>
    </div>
  );
}
