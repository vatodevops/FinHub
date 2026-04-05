import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MonthlyCalendar } from '@/components/MonthlyCalendar';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api } from '@/lib/api';

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
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Calendario" subtitle="Vista mensual real con lo que deberia cobrarse o pagarse en cada dia." />
      <div className="grid gap-4">
        <MonthlyCalendar items={calendarItems} year={now.getFullYear()} monthIndex={now.getMonth()} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <PageSection title="Series recurrentes" subtitle="Patrones aprendidos o confirmados por el sistema.">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Serie</TableHead>
                  <TableHead>Frecuencia</TableHead>
                  <TableHead>Dia</TableHead>
                  <TableHead>Proxima</TableHead>
                  <TableHead>Importe</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recurringSeries.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{item.recurrence_type}</TableCell>
                    <TableCell>{item.typical_day_of_month || '\u2014'}</TableCell>
                    <TableCell>{item.next_expected_date || '\u2014'}</TableCell>
                    <TableCell>{item.amount_mean ? money(item.amount_mean) : '\u2014'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </PageSection>

          <PageSection title="Agenda detallada" subtitle="Lista clasica debajo del calendario visual.">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Detalle</TableHead>
                  <TableHead>Importe</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recurringCalendar.map((occ) => (
                  <TableRow key={occ.id}>
                    <TableCell>{occ.expected_date}</TableCell>
                    <TableCell><Badge variant="outline">recurrente</Badge></TableCell>
                    <TableCell>{occ.status}</TableCell>
                    <TableCell>{occ.expected_amount ? money(occ.expected_amount) : '\u2014'}</TableCell>
                  </TableRow>
                ))}
                {manualItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.expected_date || '\u2014'}</TableCell>
                    <TableCell><Badge variant="outline">manual</Badge></TableCell>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>{money(item.amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </PageSection>
        </div>
      </div>
    </div>
  );
}
