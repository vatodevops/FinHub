'use client';

import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MonthlyCalendar } from '@/components/MonthlyCalendar';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { api, type RecurringSeries, type RecurringOccurrence, type ManualPlannedItem } from '@/lib/api';
import { type CalendarItem } from '@/components/MonthlyCalendar';
import { cn } from '@/lib/utils';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

const RECURRENCE_LABELS: Record<string, string> = {
  weekly: 'Semanal',
  monthly: 'Mensual',
  bimonthly: 'Bimensual',
  quarterly: 'Trimestral',
  yearly: 'Anual',
  irregular: 'Irregular',
};

export default function ScheduledPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth());
  const [year, setYear] = useState(now.getFullYear());
  const [series, setSeries] = useState<RecurringSeries[]>([]);
  const [calendar, setCalendar] = useState<RecurringOccurrence[]>([]);
  const [manualItems, setManualItems] = useState<ManualPlannedItem[]>([]);
  const [addOpen, setAddOpen] = useState(false);
  const [addQuickOpen, setAddQuickOpen] = useState(false);
  const [quickDate, setQuickDate] = useState('');
  const [deleteTarget, setDeleteTarget] = useState<RecurringSeries | null>(null);
  const [deleteCalItem, setDeleteCalItem] = useState<CalendarItem | null>(null);

  // Add series form
  const [name, setName] = useState('');
  const [recType, setRecType] = useState('monthly');
  const [dayOfMonth, setDayOfMonth] = useState('');
  const [amount, setAmount] = useState('');
  const [nextDate, setNextDate] = useState('');

  // Quick add form
  const [quickName, setQuickName] = useState('');
  const [quickAmount, setQuickAmount] = useState('');
  const [quickKind, setQuickKind] = useState('one_off');

  function refresh() {
    api.recurringSeries().then(setSeries);
    api.recurringCalendar().then(setCalendar);
    api.manualPlannedItems().then(setManualItems);
  }

  useEffect(() => { refresh(); }, []);

  function prevMonth() {
    if (month === 0) { setMonth(11); setYear(y => y - 1); }
    else setMonth(m => m - 1);
  }

  function nextMonth() {
    if (month === 11) { setMonth(0); setYear(y => y + 1); }
    else setMonth(m => m + 1);
  }

  const calendarItems: CalendarItem[] = [
    ...calendar.map((occ) => ({
      id: `rec-${occ.id}`,
      rawId: occ.id,
      date: occ.expected_date,
      title: 'Pago recurrente',
      amount: occ.expected_amount,
      kind: 'recurring' as const,
      status: occ.status,
    })),
    ...manualItems.filter((item) => item.expected_date).map((item) => ({
      id: `man-${item.id}`,
      rawId: item.id,
      date: item.expected_date!,
      title: item.name,
      amount: item.amount,
      kind: 'manual' as const,
      status: item.status,
    })),
  ];

  function handleDayClick(date: string) {
    setQuickDate(date);
    setQuickName('');
    setQuickAmount('');
    setQuickKind('one_off');
    setAddQuickOpen(true);
  }

  async function handleQuickAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!quickName.trim() || !quickAmount) return;
    await api.createManualPlannedItem({
      name: quickName.trim(),
      amount: parseFloat(quickAmount),
      expected_date: quickDate,
      kind: quickKind,
      status: 'planned',
    });
    setAddQuickOpen(false);
    refresh();
  }

  async function handleCalItemDelete() {
    if (!deleteCalItem) return;
    if (deleteCalItem.kind === 'manual' && deleteCalItem.rawId) {
      await api.deleteManualPlannedItem(deleteCalItem.rawId);
    }
    // For recurring occurrences we delete the whole series if needed
    // For now we only support deleting manual items from the calendar
    setDeleteCalItem(null);
    refresh();
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    await api.createRecurringSeries({
      name: name.trim(),
      recurrence_type: recType,
      typical_day_of_month: dayOfMonth ? parseInt(dayOfMonth) : null,
      amount_mean: amount ? parseFloat(amount) : null,
      next_expected_date: nextDate || null,
    });
    setName(''); setRecType('monthly'); setDayOfMonth(''); setAmount(''); setNextDate('');
    setAddOpen(false);
    refresh();
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await api.deleteRecurringSeries(deleteTarget.id);
    setDeleteTarget(null);
    refresh();
  }

  const totalMonthly = series
    .filter(s => s.recurrence_type === 'monthly' && s.amount_mean)
    .reduce((sum, s) => sum + Number(s.amount_mean), 0);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Pagos programados" subtitle="Calendario de pagos recurrentes y cargos esperados." />

      {/* Summary */}
      {series.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Series activas</div>
            <div className="text-2xl font-bold mt-1 text-foreground">{series.length}</div>
          </div>
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Gasto mensual recurrente</div>
            <div className="text-2xl font-bold mt-1 text-destructive">{money(String(totalMonthly))}</div>
          </div>
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Proximos vencimientos</div>
            <div className="text-2xl font-bold mt-1 text-foreground">{calendar.length}</div>
          </div>
        </div>
      )}

      {/* Month nav + Calendar */}
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-3">
          <button onClick={prevMonth} className="px-3 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <button onClick={nextMonth} className="px-3 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          </button>
        </div>
        <MonthlyCalendar
          items={calendarItems}
          year={year}
          monthIndex={month}
          onDayClick={handleDayClick}
          onItemDelete={(item) => setDeleteCalItem(item)}
        />
      </div>

      {/* Series table */}
      <PageSection
        title="Series recurrentes"
        subtitle="Pagos que se repiten de forma periodica."
        action={
          <button
            onClick={() => setAddOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent text-white font-medium hover:bg-accent/90 transition-colors text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Añadir serie
          </button>
        }
      >
        {series.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <p className="text-lg">No hay series recurrentes</p>
            <p className="text-sm mt-1">Añade tus pagos recurrentes como alquiler, suscripciones, seguros, etc.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Frecuencia</TableHead>
                <TableHead>Dia</TableHead>
                <TableHead>Proxima</TableHead>
                <TableHead className="text-right">Importe</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {series.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium">{s.name}</TableCell>
                  <TableCell><Badge variant="outline">{RECURRENCE_LABELS[s.recurrence_type] || s.recurrence_type}</Badge></TableCell>
                  <TableCell>{s.typical_day_of_month || '\u2014'}</TableCell>
                  <TableCell>{s.next_expected_date || '\u2014'}</TableCell>
                  <TableCell className="text-right text-destructive font-medium">{s.amount_mean ? money(s.amount_mean) : '\u2014'}</TableCell>
                  <TableCell>
                    <button onClick={() => setDeleteTarget(s)} className="text-muted-foreground hover:text-destructive transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </PageSection>

      {/* Add dialog */}
      {addOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setAddOpen(false)} />
          <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-md mx-4 shadow-2xl">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">Nueva serie recurrente</h2>
            </div>
            <form onSubmit={handleAdd} className="p-6 grid gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Nombre *</label>
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Ej: Alquiler, Netflix, Gimnasio..." className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors" autoFocus />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Frecuencia</label>
                  <select value={recType} onChange={(e) => setRecType(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors">
                    <option value="monthly">Mensual</option>
                    <option value="weekly">Semanal</option>
                    <option value="quarterly">Trimestral</option>
                    <option value="yearly">Anual</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Dia del mes</label>
                  <input type="number" min="1" max="31" value={dayOfMonth} onChange={(e) => setDayOfMonth(e.target.value)} placeholder="1-31" className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Importe estimado</label>
                  <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Proximo pago</label>
                  <input type="date" value={nextDate} onChange={(e) => setNextDate(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors" />
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setAddOpen(false)} className="px-4 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors text-sm">Cancelar</button>
                <button type="submit" className="px-4 py-2 rounded-xl bg-accent text-white font-medium hover:bg-accent/90 transition-colors text-sm">Crear</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="Eliminar serie"
        message={`Se eliminara la serie "${deleteTarget?.name}" y todos sus vencimientos.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />

      <ConfirmDialog
        open={!!deleteCalItem}
        title="Eliminar pago"
        message={`Se eliminara "${deleteCalItem?.title}" del ${deleteCalItem?.date}.`}
        onConfirm={handleCalItemDelete}
        onCancel={() => setDeleteCalItem(null)}
      />

      {/* Quick add from calendar click */}
      {addQuickOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setAddQuickOpen(false)} />
          <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-sm mx-4 shadow-2xl">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">Nuevo pago — {quickDate}</h2>
            </div>
            <form onSubmit={handleQuickAdd} className="p-6 grid gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Nombre *</label>
                <input
                  type="text"
                  value={quickName}
                  onChange={(e) => setQuickName(e.target.value)}
                  placeholder="Ej: Peluqueria, Dentista, Seguro..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                  autoFocus
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Importe *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={quickAmount}
                    onChange={(e) => setQuickAmount(e.target.value)}
                    placeholder="0.00"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Tipo</label>
                  <select
                    value={quickKind}
                    onChange={(e) => setQuickKind(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
                  >
                    <option value="one_off">Puntual</option>
                    <option value="recurring">Recurrente</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setAddQuickOpen(false)} className="px-4 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors text-sm">
                  Cancelar
                </button>
                <button type="submit" className="px-4 py-2 rounded-xl bg-accent text-white font-medium hover:bg-accent/90 transition-colors text-sm">
                  Añadir
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
