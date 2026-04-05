import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { cn } from '@/lib/utils';

type CalendarItem = {
  id: string;
  date: string;
  title: string;
  amount?: string | null;
  kind: 'recurring' | 'manual';
  status?: string;
};

function money(value?: string | null) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

function buildMonthGrid(items: CalendarItem[], year: number, monthIndex: number) {
  const firstDay = new Date(year, monthIndex, 1);
  const startWeekday = (firstDay.getDay() + 6) % 7;
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
  const cells: Array<{ day: number | null; iso?: string; items: CalendarItem[] }> = [];

  for (let i = 0; i < startWeekday; i++) cells.push({ day: null, items: [] });
  for (let day = 1; day <= daysInMonth; day++) {
    const iso = new Date(year, monthIndex, day).toISOString().slice(0, 10);
    cells.push({ day, iso, items: items.filter((item) => item.date === iso) });
  }
  while (cells.length % 7 !== 0) cells.push({ day: null, items: [] });
  return cells;
}

export function MonthlyCalendar({ items, year, monthIndex }: { items: CalendarItem[]; year: number; monthIndex: number }) {
  const monthLabel = new Intl.DateTimeFormat('es-ES', { month: 'long', year: 'numeric' }).format(new Date(year, monthIndex, 1));
  const weekdays = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];
  const cells = buildMonthGrid(items, year, monthIndex);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="capitalize">{monthLabel}</CardTitle>
        <CardDescription>Pagos recurrentes detectados + gastos manuales planificados</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-2 mb-2">
          {weekdays.map((day) => <div key={day} className="text-muted-foreground text-sm px-2 py-1">{day}</div>)}
        </div>
        <div className="grid grid-cols-7 gap-2">
          {cells.map((cell, idx) => (
            <div key={`${cell.iso || 'empty'}-${idx}`} className={cn('min-h-[128px] p-2.5 rounded-xl border border-border bg-white/[0.02] grid gap-2', !cell.day && 'opacity-25')}>
              {cell.day ? <div className="font-bold text-foreground">{cell.day}</div> : null}
              <div className="grid gap-1.5">
                {cell.items.slice(0, 3).map((item) => (
                  <div key={item.id} className={cn(
                    'rounded-lg p-2 text-xs border',
                    item.kind === 'recurring' ? 'bg-accent/12 border-accent/20' : 'bg-success/10 border-success/15'
                  )}>
                    <div className="font-bold mb-0.5">{item.title}</div>
                    <div className="text-muted-foreground">{item.amount ? money(item.amount) : '\u2014'}</div>
                  </div>
                ))}
                {cell.items.length > 3 ? <div className="text-sm text-muted-foreground">+{cell.items.length - 3} mas</div> : null}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
