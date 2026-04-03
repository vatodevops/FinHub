import { MetricCard } from '../components/MetricCard';
import { PageSection } from '../components/PageSection';
import { Topbar } from '../components/Topbar';
import { api } from '../lib/api';

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
    <main className="page">
      <Topbar title="Dashboard" subtitle="Visión general del mes, próximos cargos y actividad reciente." />

      <section className="grid cards">
        <MetricCard label="Ingresos mes" value={money(overview.booked_income_month)} tone="positive" />
        <MetricCard label="Gastos mes" value={money(overview.booked_expense_month)} tone="negative" />
        <MetricCard label="Neto mes" value={money(overview.net_month)} tone={Number(overview.net_month) >= 0 ? 'positive' : 'negative'} />
        <MetricCard label="Próximos manuales" value={money(overview.planned_expense_upcoming)} />
        <MetricCard label="Próximos recurrentes" value={money(overview.recurring_due_upcoming)} />
        <MetricCard label="Cuentas / instituciones" value={`${overview.account_count} / ${overview.institution_count}`} hint={`${overview.transaction_count} movimientos`} />
      </section>

      <div className="grid cols-2" style={{ marginTop: 16 }}>
        <PageSection title="Actividad reciente" subtitle="Últimos movimientos registrados en el sistema.">
          <table className="table">
            <thead><tr><th>Fecha</th><th>Concepto</th><th>Canal</th><th>Estado</th><th>Importe</th></tr></thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id}>
                  <td>{tx.booked_at ? tx.booked_at.slice(0, 10) : '—'}</td>
                  <td>{tx.merchant_clean || tx.merchant_raw || '—'}</td>
                  <td>{tx.channel}</td>
                  <td><span className="badge">{tx.status}</span></td>
                  <td className={Number(tx.amount) >= 0 ? 'positive' : 'negative'}>{money(tx.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </PageSection>

        <div className="section-stack">
          <PageSection title="Próximos pagos" subtitle="Calendario financiero esperado.">
            <div className="list">
              {recurringCalendar.slice(0, 5).map((occ) => (
                <div key={occ.id} className="list-item row-between">
                  <div className="stack-xs">
                    <strong>{occ.expected_date}</strong>
                    <span className="muted small">Pago recurrente esperado</span>
                  </div>
                  <div>{occ.expected_amount ? money(occ.expected_amount) : '—'}</div>
                </div>
              ))}
            </div>
          </PageSection>

          <PageSection title="Manuales próximos" subtitle="Gastos que metes tú a mano.">
            <div className="list">
              {manualItems.slice(0, 4).map((item) => (
                <div key={item.id} className="list-item row-between">
                  <div className="stack-xs">
                    <strong>{item.name}</strong>
                    <span className="muted small">{item.expected_date || 'Sin fecha'} · {item.kind}</span>
                  </div>
                  <div>{money(item.amount)}</div>
                </div>
              ))}
            </div>
          </PageSection>
        </div>
      </div>
    </main>
  );
}
