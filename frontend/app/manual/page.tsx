import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ManualPlannedForm } from '@/components/ManualPlannedForm';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api } from '@/lib/api';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export default async function ManualPage() {
  const items = await api.manualPlannedItems();

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Gastos manuales" subtitle="Para cosas como peluqueria, efectivo, pagos informales o previsiones tuyas." />
      <div className="grid gap-4">
        <ManualPlannedForm />
        <PageSection title="Listado manual" subtitle="Aqui apareceran tus gastos creados a mano.">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Regla</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Importe</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.expected_date || '\u2014'}</TableCell>
                  <TableCell>{item.recurrence_rule || item.kind}</TableCell>
                  <TableCell><Badge variant="outline">{item.status}</Badge></TableCell>
                  <TableCell>{money(item.amount)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </PageSection>
      </div>
    </div>
  );
}
