import { MonthlyCalendar } from '../../components/MonthlyCalendar';
import { PageSection } from '../../components/PageSection';
import { Topbar } from '../../components/Topbar';
import { api } from '../../lib/api';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export default async function CalendarPage() {
  const [recurringSeries, recurringCalendar, manualItems] = await Promise.all([
    api.recurringSeries(),
    api.recurringCalendar(),
    api.manualPlannedItems(),
  ]);

  const now = new Date();
  const calendarItems = [
    ...recurringCalendar.map((occ) => ({
      id: `rec-${occ.id}`,
      date: occ.expected_date,
      title: 'Pago recurrente',
      amount: occ.expected_amount,
      kind: 'recurring' as const,
      status: occ.status,
    })),
    ...manualItems.filter((item) => item.expected_date).map((item) => ({
      id: `man-${item.id}`,
      date: item.expected_date!,
      title: item.name,
      amount: item.amount,
      kind: 'manual' as const,
      status: item.status,
    })),
  ];

  return (
    <main className="page">
      <Topbar title="Calendario" subtitle="Vista mensual real con lo que debería cobrarse o pagarse en cada día." />
      <div className="section-stack">
        <MonthlyCalendar items={calendarItems} year={now.getFullYear()} monthIndex={now.getMonth()} />

        <div className="grid cols-2">
          <PageSection title="Series recurrentes" subtitle="Patrones aprendidos o confirmados por el sistema.">
            <table className="table">
              <thead><tr><th>Serie</th><th>Frecuencia</th><th>Día</th><th>Próxima</th><th>Importe</th></tr></thead>
              <tbody>
                {recurringSeries.map((item) => (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>{item.recurrence_type}</td>
                    <td>{item.typical_day_of_month || '—'}</td>
                    <td>{item.next_expected_date || '—'}</td>
                    <td>{item.amount_mean ? money(item.amount_mean) : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </PageSection>

          <PageSection title="Agenda detallada" subtitle="Lista clásica debajo del calendario visual.">
            <table className="table">
              <thead><tr><th>Fecha</th><th>Tipo</th><th>Detalle</th><th>Importe</th></tr></thead>
              <tbody>
                {recurringCalendar.map((occ) => (
                  <tr key={occ.id}>
                    <td>{occ.expected_date}</td>
                    <td><span className="badge">recurrente</span></td>
                    <td>{occ.status}</td>
                    <td>{occ.expected_amount ? money(occ.expected_amount) : '—'}</td>
                  </tr>
                ))}
                {manualItems.map((item) => (
                  <tr key={item.id}>
                    <td>{item.expected_date || '—'}</td>
                    <td><span className="badge">manual</span></td>
                    <td>{item.name}</td>
                    <td>{money(item.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </PageSection>
        </div>
      </div>
    </main>
  );
}
