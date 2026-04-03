import { ManualPlannedForm } from '../../components/ManualPlannedForm';
import { PageSection } from '../../components/PageSection';
import { Topbar } from '../../components/Topbar';
import { api } from '../../lib/api';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export default async function ManualPage() {
  const items = await api.manualPlannedItems();

  return (
    <main className="page">
      <Topbar title="Gastos manuales" subtitle="Para cosas como peluquería, efectivo, pagos informales o previsiones tuyas." />
      <div className="section-stack">
        <ManualPlannedForm />
        <PageSection title="Listado manual" subtitle="Aquí aparecerán tus gastos creados a mano.">
          <table className="table">
            <thead><tr><th>Nombre</th><th>Fecha</th><th>Regla</th><th>Estado</th><th>Importe</th></tr></thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.expected_date || '—'}</td>
                  <td>{item.recurrence_rule || item.kind}</td>
                  <td><span className="badge">{item.status}</span></td>
                  <td>{money(item.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </PageSection>
      </div>
    </main>
  );
}
