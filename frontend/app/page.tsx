import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MetricCard } from '@/components/MetricCard';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export default async function HomePage() {
  const [overview, transactions, recurringCalendar, manualItems] = await Promise.all([
    api.overview(),
    api.transactions(),
    api.recurringCalendar(),
    api.manualPlannedItems(),
  ]);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Dashboard" subtitle="Vision general del mes, proximos cargos y actividad reciente." />

      <div className="grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-4">
        <MetricCard label="Ingresos mes" value={money(overview.booked_income_month)} tone="positive" />
        <MetricCard label="Gastos mes" value={money(overview.booked_expense_month)} tone="negative" />
        <MetricCard label="Neto mes" value={money(overview.net_month)} tone={Number(overview.net_month) >= 0 ? 'positive' : 'negative'} />
        <MetricCard label="Proximos manuales" value={money(overview.planned_expense_upcoming)} />
        <MetricCard label="Proximos recurrentes" value={money(overview.recurring_due_upcoming)} />
        <MetricCard label="Cuentas / instituciones" value={`${overview.account_count} / ${overview.institution_count}`} hint={`${overview.transaction_count} movimientos`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1.15fr_0.85fr] gap-4 mt-4">
        <PageSection title="Actividad reciente" subtitle="Ultimos movimientos registrados en el sistema.">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fecha</TableHead>
                <TableHead>Concepto</TableHead>
                <TableHead>Canal</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Importe</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell>{tx.booked_at ? tx.booked_at.slice(0, 10) : '\u2014'}</TableCell>
                  <TableCell>{tx.merchant_clean || tx.merchant_raw || '\u2014'}</TableCell>
                  <TableCell>{tx.channel}</TableCell>
                  <TableCell><Badge variant="outline">{tx.status}</Badge></TableCell>
                  <TableCell className={cn(Number(tx.amount) >= 0 ? 'text-success' : 'text-destructive')}>{money(tx.amount)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </PageSection>

        <div className="grid gap-4">
          <PageSection title="Proximos pagos" subtitle="Calendario financiero esperado.">
            <div className="grid gap-2.5">
              {recurringCalendar.slice(0, 5).map((occ) => (
                <div key={occ.id} className="flex justify-between items-center gap-3 px-3.5 py-3 rounded-xl border border-border bg-white/[0.02]">
                  <div className="grid gap-1">
                    <strong>{occ.expected_date}</strong>
                    <span className="text-muted-foreground text-sm">Pago recurrente esperado</span>
                  </div>
                  <div>{occ.expected_amount ? money(occ.expected_amount) : '\u2014'}</div>
                </div>
              ))}
            </div>
          </PageSection>

          <PageSection title="Manuales proximos" subtitle="Gastos que metes tu a mano.">
            <div className="grid gap-2.5">
              {manualItems.slice(0, 4).map((item) => (
                <div key={item.id} className="flex justify-between items-center gap-3 px-3.5 py-3 rounded-xl border border-border bg-white/[0.02]">
                  <div className="grid gap-1">
                    <strong>{item.name}</strong>
                    <span className="text-muted-foreground text-sm">{item.expected_date || 'Sin fecha'} &middot; {item.kind}</span>
                  </div>
                  <div>{money(item.amount)}</div>
                </div>
              ))}
            </div>
          </PageSection>
        </div>
      </div>
    </div>
  );
}
