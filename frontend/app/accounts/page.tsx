'use client';

import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { AddAccountDialog } from '@/components/AddAccountDialog';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { api, Account } from '@/lib/api';
import { cn } from '@/lib/utils';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

const KIND_LABELS: Record<string, string> = {
  checking: 'Corriente',
  savings: 'Ahorro',
  credit_card: 'Tarjeta',
  investment: 'Inversion',
  cash: 'Efectivo',
};

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Account | null>(null);

  function refresh() {
    api.accounts().then(setAccounts);
  }

  useEffect(() => { refresh(); }, []);

  async function handleDelete() {
    if (!deleteTarget) return;
    await api.deleteAccount(deleteTarget.id);
    setDeleteTarget(null);
    refresh();
  }

  const totalBalance = accounts.reduce((sum, a) => sum + Number(a.balance || 0), 0);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Cuentas" subtitle="Bancos, tarjetas y todas tus fuentes de saldo." />

      {/* Summary cards */}
      {accounts.length > 0 && (
        <div className="grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-4 mb-4">
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Balance total</div>
            <div className={cn('text-2xl font-bold mt-1', totalBalance >= 0 ? 'text-success' : 'text-destructive')}>
              {money(String(totalBalance))}
            </div>
          </div>
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Cuentas activas</div>
            <div className="text-2xl font-bold mt-1 text-foreground">{accounts.filter(a => a.is_active).length}</div>
          </div>
          <div className="rounded-xl border border-border bg-white/[0.02] p-4">
            <div className="text-sm text-muted-foreground">Entidades</div>
            <div className="text-2xl font-bold mt-1 text-foreground">
              {new Set(accounts.map(a => a.institution_name).filter(Boolean)).size}
            </div>
          </div>
        </div>
      )}

      <PageSection
        title="Mis cuentas"
        subtitle="Todas las cuentas registradas en FinHub."
        action={
          <button
            onClick={() => setDialogOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent text-white font-medium hover:bg-accent/90 transition-colors text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            Añadir cuenta
          </button>
        }
      >
        {accounts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <p className="text-lg">No hay cuentas todavia</p>
            <p className="text-sm mt-1">Añade tu primera cuenta para empezar a gestionar tus finanzas.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Entidad</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Divisa</TableHead>
                <TableHead>IBAN</TableHead>
                <TableHead className="text-right">Saldo</TableHead>
                <TableHead className="w-[80px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accounts.map((acc) => (
                <TableRow key={acc.id}>
                  <TableCell className="font-medium">{acc.name}</TableCell>
                  <TableCell>{acc.institution_name || '\u2014'}</TableCell>
                  <TableCell><Badge variant="outline">{KIND_LABELS[acc.kind] || acc.kind}</Badge></TableCell>
                  <TableCell>{acc.currency}</TableCell>
                  <TableCell>{acc.iban_masked || '\u2014'}</TableCell>
                  <TableCell className={cn('text-right font-medium', Number(acc.balance || 0) >= 0 ? 'text-success' : 'text-destructive')}>
                    {acc.balance ? money(acc.balance) : '\u2014'}
                  </TableCell>
                  <TableCell>
                    <button
                      onClick={() => setDeleteTarget(acc)}
                      className="text-muted-foreground hover:text-destructive transition-colors"
                      title="Eliminar cuenta"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </PageSection>

      <AddAccountDialog open={dialogOpen} onClose={() => { setDialogOpen(false); refresh(); }} />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Eliminar cuenta"
        message={`Se eliminara la cuenta "${deleteTarget?.name}" y todas sus transacciones. Esta accion no se puede deshacer.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
