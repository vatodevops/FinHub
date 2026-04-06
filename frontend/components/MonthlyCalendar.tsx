'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export type CalendarItem = {
  id: string;
  date: string;
  title: string;
  amount?: string | null;
  kind: 'recurring' | 'manual';
  status?: string;
  /** original ID without the rec-/man- prefix, for API calls */
  rawId?: string;
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

export function MonthlyCalendar({
  items,
  year,
  monthIndex,
  onDayClick,
  onItemDelete,
}: {
  items: CalendarItem[];
  year: number;
  monthIndex: number;
  onDayClick?: (date: string) => void;
  onItemDelete?: (item: CalendarItem) => void;
}) {
  const monthLabel = new Intl.DateTimeFormat('es-ES', { month: 'long', year: 'numeric' }).format(new Date(year, monthIndex, 1));
  const weekdays = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];
  const cells = buildMonthGrid(items, year, monthIndex);
  const todayIso = new Date().toISOString().slice(0, 10);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="capitalize">{monthLabel}</CardTitle>
        <CardDescription>
          Haz click en un dia para añadir un pago. Click en la X de un pago para eliminarlo.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-2 mb-2">
          {weekdays.map((day) => <div key={day} className="text-muted-foreground text-sm px-2 py-1 text-center">{day}</div>)}
        </div>
        <div className="grid grid-cols-7 gap-2">
          {cells.map((cell, idx) => (
            <div
              key={`${cell.iso || 'empty'}-${idx}`}
              onClick={() => cell.day && cell.iso && onDayClick?.(cell.iso)}
              className={cn(
                'min-h-[120px] p-2 rounded-xl border border-border bg-white/[0.02] grid gap-1.5 content-start transition-colors',
                !cell.day && 'opacity-20',
                cell.day && onDayClick && 'cursor-pointer hover:border-accent/30 hover:bg-accent/5',
                cell.iso === todayIso && 'border-accent/40 bg-accent/5',
              )}
            >
              {cell.day ? (
                <div className={cn('font-bold text-sm', cell.iso === todayIso ? 'text-accent' : 'text-foreground')}>
                  {cell.day}
                </div>
              ) : null}
              {cell.items.slice(0, 3).map((item) => (
                <div
                  key={item.id}
                  className={cn(
                    'rounded-lg p-1.5 text-xs border group relative',
                    item.kind === 'recurring' ? 'bg-accent/12 border-accent/20' : 'bg-success/10 border-success/15'
                  )}
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-start justify-between gap-1">
                    <div className="min-w-0">
                      <div className="font-bold truncate">{item.title}</div>
                      <div className="text-muted-foreground">{item.amount ? money(item.amount) : '\u2014'}</div>
                    </div>
                    {onItemDelete && (
                      <button
                        onClick={(e) => { e.stopPropagation(); onItemDelete(item); }}
                        className="flex-shrink-0 w-4 h-4 rounded-full flex items-center justify-center text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-destructive hover:bg-destructive/10 transition-all"
                        title="Eliminar"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {cell.items.length > 3 ? <div className="text-xs text-muted-foreground">+{cell.items.length - 3} mas</div> : null}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
