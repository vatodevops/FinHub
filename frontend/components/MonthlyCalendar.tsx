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
  const weekdays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const cells = buildMonthGrid(items, year, monthIndex);

  return (
    <div className="panel">
      <div className="section-head">
        <div>
          <h2 style={{ textTransform: 'capitalize' }}>{monthLabel}</h2>
          <div className="muted small">Pagos recurrentes detectados + gastos manuales planificados</div>
        </div>
      </div>
      <div className="calendar-grid calendar-weekdays">
        {weekdays.map((day) => <div key={day} className="calendar-weekday">{day}</div>)}
      </div>
      <div className="calendar-grid">
        {cells.map((cell, idx) => (
          <div key={`${cell.iso || 'empty'}-${idx}`} className={`calendar-cell ${cell.day ? '' : 'is-empty'}`}>
            {cell.day ? <div className="calendar-day">{cell.day}</div> : null}
            <div className="calendar-events">
              {cell.items.slice(0, 3).map((item) => (
                <div key={item.id} className={`calendar-event ${item.kind}`}>
                  <div className="calendar-event-title">{item.title}</div>
                  <div className="calendar-event-meta">{item.amount ? money(item.amount) : '—'}</div>
                </div>
              ))}
              {cell.items.length > 3 ? <div className="small muted">+{cell.items.length - 3} más</div> : null}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
