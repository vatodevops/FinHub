import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api } from '@/lib/api';

export default async function AccountsPage() {
  const accounts = await api.accounts();

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Cuentas" subtitle="Bancos, tarjetas, Curve y fuentes de saldo." />
      <PageSection title="Listado de cuentas" subtitle="Vista mas parecida a una app financiera real, separada del dashboard.">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nombre</TableHead>
              <TableHead>Tipo</TableHead>
              <TableHead>Divisa</TableHead>
              <TableHead>IBAN</TableHead>
              <TableHead>Activa</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {accounts.map((acc) => (
              <TableRow key={acc.id}>
                <TableCell>{acc.name}</TableCell>
                <TableCell><Badge variant="outline">{acc.kind}</Badge></TableCell>
                <TableCell>{acc.currency}</TableCell>
                <TableCell>{acc.iban_masked || '\u2014'}</TableCell>
                <TableCell>{acc.is_active ? 'Si' : 'No'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </PageSection>
    </div>
  );
}
