'use client';

import { useState } from 'react';
import { api, type Account, type Category } from '@/lib/api';
import { cn } from '@/lib/utils';

const CHANNELS = [
  { value: 'card', label: 'Tarjeta' },
  { value: 'transfer', label: 'Transferencia' },
  { value: 'direct_debit', label: 'Domiciliacion' },
  { value: 'cash', label: 'Efectivo' },
  { value: 'income', label: 'Ingreso' },
  { value: 'other', label: 'Otro' },
];

export function AddTransactionDialog({
  open,
  onClose,
  accounts,
  categories,
}: {
  open: boolean;
  onClose: () => void;
  accounts: Account[];
  categories: Category[];
}) {
  const [accountId, setAccountId] = useState('');
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [isExpense, setIsExpense] = useState(true);
  const [bookedAt, setBookedAt] = useState(new Date().toISOString().slice(0, 10));
  const [categoryId, setCategoryId] = useState('');
  const [channel, setChannel] = useState('card');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  function reset() {
    setAccountId('');
    setDescription('');
    setAmount('');
    setIsExpense(true);
    setBookedAt(new Date().toISOString().slice(0, 10));
    setCategoryId('');
    setChannel('card');
    setError('');
  }

  function handleClose() {
    reset();
    onClose();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!accountId || !description.trim() || !amount) {
      setError('Cuenta, descripcion e importe son obligatorios');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const numAmount = parseFloat(amount);
      await api.createTransaction({
        account_id: accountId,
        description: description.trim(),
        amount: isExpense ? -Math.abs(numAmount) : Math.abs(numAmount),
        booked_at: bookedAt || null,
        category_id: categoryId || null,
        channel,
      });
      handleClose();
    } catch {
      setError('Error al crear la transaccion');
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={handleClose} />
      <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-lg mx-4 shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Nueva transaccion</h2>
          <button onClick={handleClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid gap-4">
            {/* Type toggle */}
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setIsExpense(true)}
                className={cn('flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors border', isExpense ? 'bg-destructive/15 border-destructive/30 text-destructive' : 'border-border text-muted-foreground')}
              >
                Gasto
              </button>
              <button
                type="button"
                onClick={() => setIsExpense(false)}
                className={cn('flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors border', !isExpense ? 'bg-success/15 border-success/30 text-success' : 'border-border text-muted-foreground')}
              >
                Ingreso
              </button>
            </div>

            {/* Account */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Cuenta *</label>
              <select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
              >
                <option value="">Seleccionar cuenta...</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>{acc.name}</option>
                ))}
              </select>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Descripcion *</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Ej: Mercadona, Netflix, Nomina..."
                className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                autoFocus
              />
            </div>

            {/* Amount + Date */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Importe *</label>
                <input
                  type="number"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Fecha</label>
                <input
                  type="date"
                  value={bookedAt}
                  onChange={(e) => setBookedAt(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
                />
              </div>
            </div>

            {/* Category + Channel */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Categoria</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
                >
                  <option value="">Sin categoria</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Canal</label>
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
                >
                  {CHANNELS.map((ch) => (
                    <option key={ch.value} value={ch.value}>{ch.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button type="button" onClick={handleClose} className="px-4 py-2.5 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors">
              Cancelar
            </button>
            <button
              type="submit"
              disabled={submitting}
              className={cn('px-5 py-2.5 rounded-xl font-medium transition-colors bg-accent text-white hover:bg-accent/90', submitting && 'opacity-50 cursor-not-allowed')}
            >
              {submitting ? 'Creando...' : 'Crear transaccion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
