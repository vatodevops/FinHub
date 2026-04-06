'use client';

import { useState } from 'react';
import { api, type Account } from '@/lib/api';
import { cn } from '@/lib/utils';

export function TransferDialog({
  open,
  onClose,
  accounts,
}: {
  open: boolean;
  onClose: () => void;
  accounts: Account[];
}) {
  const [fromId, setFromId] = useState('');
  const [toId, setToId] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('Transferencia entre cuentas');
  const [bookedAt, setBookedAt] = useState(new Date().toISOString().slice(0, 10));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  function handleClose() {
    setFromId('');
    setToId('');
    setAmount('');
    setDescription('Transferencia entre cuentas');
    setBookedAt(new Date().toISOString().slice(0, 10));
    setError('');
    onClose();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!fromId || !toId || !amount) {
      setError('Todos los campos son obligatorios');
      return;
    }
    if (fromId === toId) {
      setError('Las cuentas deben ser diferentes');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await api.createTransfer({
        from_account_id: fromId,
        to_account_id: toId,
        amount: parseFloat(amount),
        description: description.trim(),
        booked_at: bookedAt || null,
      });
      handleClose();
    } catch {
      setError('Error al crear la transferencia');
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={handleClose} />
      <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Transferencia entre cuentas</h2>
          <button onClick={handleClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Cuenta origen *</label>
              <select value={fromId} onChange={(e) => setFromId(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors">
                <option value="">Seleccionar...</option>
                {accounts.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Cuenta destino *</label>
              <select value={toId} onChange={(e) => setToId(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors">
                <option value="">Seleccionar...</option>
                {accounts.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Importe *</label>
                <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0.00" className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Fecha</label>
                <input type="date" value={bookedAt} onChange={(e) => setBookedAt(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Descripcion</label>
              <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors" />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <button type="button" onClick={handleClose} className="px-4 py-2.5 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors">Cancelar</button>
            <button type="submit" disabled={submitting} className={cn('px-5 py-2.5 rounded-xl font-medium transition-colors bg-accent text-white hover:bg-accent/90', submitting && 'opacity-50 cursor-not-allowed')}>
              {submitting ? 'Creando...' : 'Transferir'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
