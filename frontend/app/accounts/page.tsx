import { PageSection } from '../../components/PageSection';
import { Topbar } from '../../components/Topbar';
import { api } from '../../lib/api';

export default async function AccountsPage() {
  const accounts = await api.accounts();

  return (
    <main className="page">
      <Topbar title="Cuentas" subtitle="Bancos, tarjetas, Curve y fuentes de saldo." />
      <PageSection title="Listado de cuentas" subtitle="Vista más parecida a una app financiera real, separada del dashboard.">
        <table className="table">
          <thead><tr><th>Nombre</th><th>Tipo</th><th>Divisa</th><th>IBAN</th><th>Activa</th></tr></thead>
          <tbody>
            {accounts.map((acc) => (
              <tr key={acc.id}>
                <td>{acc.name}</td>
                <td><span className="badge">{acc.kind}</span></td>
                <td>{acc.currency}</td>
                <td>{acc.iban_masked || '—'}</td>
                <td>{acc.is_active ? 'Sí' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </PageSection>
    </main>
  );
}
