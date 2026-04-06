'use client';

import { useEffect, useState } from 'react';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { api, type Budget, type Category } from '@/lib/api';
import { cn } from '@/lib/utils';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

const MONTH_NAMES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

export default function BudgetsPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [addOpen, setAddOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Budget | null>(null);

  // Add form state
  const [newCatId, setNewCatId] = useState('');
  const [newAmount, setNewAmount] = useState('');

  function refresh() {
    api.budgets(month, year).then(setBudgets);
  }

  useEffect(() => {
    refresh();
    api.categories().then(setCategories);
  }, [month, year]);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!newCatId || !newAmount) return;
    await api.createBudget({
      category_id: newCatId,
      amount_limit: parseFloat(newAmount),
      month,
      year,
    });
    setNewCatId('');
    setNewAmount('');
    setAddOpen(false);
    refresh();
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await api.deleteBudget(deleteTarget.id);
    setDeleteTarget(null);
    refresh();
  }

  const totalBudget = budgets.reduce((s, b) => s + Number(b.amount_limit), 0);
  const totalSpent = budgets.reduce((s, b) => s + Number(b.spent), 0);
  const usedCategories = new Set(budgets.map(b => b.category_id));
  const availableCategories = categories.filter(c => !usedCategories.has(c.id));

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Presupuestos" subtitle="Controla tus limites de gasto mensuales por categoria." />

      {/* Month selector */}
      <div className="flex items-center gap-3 mb-4">
        <button onClick={() => { if (month === 1) { setMonth(12); setYear(y => y - 1); } else setMonth(m => m - 1); }} className="px-3 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <span className="text-lg font-semibold text-foreground">{MONTH_NAMES[month - 1]} {year}</span>
        <button onClick={() => { if (month === 12) { setMonth(1); setYear(y => y + 1); } else setMonth(m => m + 1); }} className="px-3 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>

      {/* Summary */}
      {budgets.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Presupuestado</div>
            <div className="text-2xl font-bold mt-1 text-foreground">{money(String(totalBudget))}</div>
          </div>
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Gastado</div>
            <div className={cn('text-2xl font-bold mt-1', totalSpent > totalBudget ? 'text-destructive' : 'text-foreground')}>{money(String(totalSpent))}</div>
          </div>
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Disponible</div>
            <div className={cn('text-2xl font-bold mt-1', totalBudget - totalSpent >= 0 ? 'text-success' : 'text-destructive')}>
              {money(String(totalBudget - totalSpent))}
            </div>
          </div>
        </div>
      )}

      <PageSection
        title="Presupuestos del mes"
        subtitle="Define limites de gasto por categoria y controla tu progreso."
        action={
          <button
            onClick={() => setAddOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent text-white font-medium hover:bg-accent/90 transition-colors text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Añadir presupuesto
          </button>
        }
      >
        {budgets.length === 0 && !addOpen ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <p className="text-lg">No hay presupuestos para {MONTH_NAMES[month - 1]}</p>
            <p className="text-sm mt-1">Añade presupuestos por categoria para controlar tus gastos.</p>
          </div>
        ) : (
          <div className="grid gap-3">
            {budgets.map((b) => {
              const pct = Number(b.amount_limit) > 0 ? (Number(b.spent) / Number(b.amount_limit)) * 100 : 0;
              const barColor = pct > 100 ? 'bg-destructive' : pct > 80 ? 'bg-yellow-500' : 'bg-success';
              return (
                <div key={b.id} className="rounded-xl border border-border bg-white/[0.02] p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {b.category_color && <div className="w-3 h-3 rounded-full" style={{ backgroundColor: b.category_color }} />}
                      <span className="font-medium text-foreground">{b.category_name || 'Sin categoria'}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground">
                        {money(b.spent)} / {money(b.amount_limit)}
                      </span>
                      <button
                        onClick={() => setDeleteTarget(b)}
                        className="text-muted-foreground hover:text-destructive transition-colors"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                      </button>
                    </div>
                  </div>
                  <div className="w-full h-2.5 rounded-full bg-white/[0.06] overflow-hidden">
                    <div className={cn('h-full rounded-full transition-all', barColor)} style={{ width: `${Math.min(pct, 100)}%` }} />
                  </div>
                  <div className="text-xs text-muted-foreground mt-1 text-right">{pct.toFixed(0)}%</div>
                </div>
              );
            })}
          </div>
        )}
      </PageSection>

      {/* Add budget inline dialog */}
      {addOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setAddOpen(false)} />
          <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-sm mx-4 shadow-2xl">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">Nuevo presupuesto</h2>
            </div>
            <form onSubmit={handleAdd} className="p-6 grid gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Categoria *</label>
                <select
                  value={newCatId}
                  onChange={(e) => setNewCatId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
                >
                  <option value="">Seleccionar...</option>
                  {availableCategories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Limite mensual *</label>
                <input
                  type="number"
                  step="0.01"
                  value={newAmount}
                  onChange={(e) => setNewAmount(e.target.value)}
                  placeholder="300.00"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                />
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
        title="Eliminar presupuesto"
        message={`Se eliminara el presupuesto de "${deleteTarget?.category_name}".`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
