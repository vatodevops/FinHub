'use client';

import { useEffect, useMemo, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api, type Account, type Category, type CurveDuplicateCandidate, type Transaction } from '@/lib/api';
import { filterVisibleTransactions } from '@/lib/curve';
import { cn } from '@/lib/utils';
import { AddTransactionDialog } from './AddTransactionDialog';
import { TransferDialog } from './TransferDialog';
import { ConfirmDialog } from './ConfirmDialog';
import { CurveDuplicatesPanel } from './CurveDuplicatesPanel';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export function TransactionsExplorer({
  transactions,
  categories,
  accounts,
  duplicateCandidates,
  onRefresh,
}: {
  transactions: Transaction[];
  categories: Category[];
  accounts: Account[];
  duplicateCandidates: CurveDuplicateCandidate[];
  onRefresh: () => void;
}) {
  const [query, setQuery] = useState('');
  const [channel, setChannel] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sourceType, setSourceType] = useState('all');
  const [rows, setRows] = useState(filterVisibleTransactions(transactions));
  const [busyTxId, setBusyTxId] = useState<string | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [transferOpen, setTransferOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Transaction | null>(null);

  useEffect(() => {
    setRows(filterVisibleTransactions(transactions));
  }, [transactions]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((tx) => {
      if (channel !== 'all' && tx.channel !== channel) return false;
      if (categoryFilter !== 'all') {
        if (categoryFilter === 'none' && tx.category_id) return false;
        if (categoryFilter !== 'none' && tx.category_id !== categoryFilter) return false;
      }
      if (sourceType !== 'all' && tx.source_type !== sourceType) return false;
      if (!q) return true;
      const blob = `${tx.merchant_clean || ''} ${tx.merchant_raw || ''} ${tx.description_raw || ''} ${tx.category_name || ''}`.toLowerCase();
      return blob.includes(q);
    });
  }, [rows, query, channel, categoryFilter, sourceType]);

  async function assignCategory(transactionId: string, categoryId: string) {
    setBusyTxId(transactionId);
    try {
      const updated = await api.updateTransactionCategory(transactionId, categoryId || null);
      setRows((prev) => prev.map((row) => (row.id === transactionId ? updated : row)));
    } finally {
      setBusyTxId(null);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await api.deleteTransaction(deleteTarget.id);
    setDeleteTarget(null);
    onRefresh();
  }

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle>Explorador de transacciones</CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setTransferOpen(true)}>Transferencia</Button>
              <Button onClick={() => setAddOpen(true)}>+ Transaccion</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_1fr_auto] gap-2.5">
            <Input placeholder="Buscar por merchant, descripcion o categoria" value={query} onChange={(e) => setQuery(e.target.value)} />
            <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="all">Todos los canales</option>
              <option value="card">Tarjeta</option>
              <option value="transfer">Transferencia</option>
              <option value="direct_debit">Domiciliacion</option>
              <option value="cash">Efectivo</option>
              <option value="income">Ingreso</option>
              <option value="other">Otro</option>
            </select>
            <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
              <option value="all">Todas las categorias</option>
              <option value="none">Sin categoria</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              <option value="all">Todos los origenes</option>
              <option value="bank">Banco</option>
              <option value="curve">Curve</option>
            </select>
            <Badge variant="outline" className="self-center">{filtered.length} filas</Badge>
          </div>
        </CardContent>
      </Card>

      <CurveDuplicatesPanel items={duplicateCandidates} />

      <Card>
        <CardContent className="pt-5">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Fecha</TableHead>
                <TableHead>Concepto</TableHead>
                <TableHead>Canal</TableHead>
                <TableHead>Origen</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead className="text-right">Importe</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((tx) => (
                <TableRow key={tx.id}>
                  <TableCell className="whitespace-nowrap">{tx.booked_at ? tx.booked_at.slice(0, 10) : '\u2014'}</TableCell>
                  <TableCell>{tx.merchant_clean || tx.merchant_raw || tx.description_raw || '\u2014'}</TableCell>
                  <TableCell><Badge variant="outline">{tx.channel}</Badge></TableCell>
                  <TableCell><Badge variant="outline">{tx.source_type}</Badge></TableCell>
                  <TableCell>
                    <select
                      className="flex h-8 w-full min-w-[120px] rounded-md border border-border bg-input px-2 py-1 text-sm text-foreground"
                      value={tx.category_id || ''}
                      disabled={busyTxId === tx.id}
                      onChange={(e) => assignCategory(tx.id, e.target.value)}
                    >
                      <option value="">Sin categoria</option>
                      {categories.map((category) => (
                        <option key={category.id} value={category.id}>{category.name}</option>
                      ))}
                    </select>
                  </TableCell>
                  <TableCell className={cn('text-right font-medium whitespace-nowrap', Number(tx.amount) >= 0 ? 'text-success' : 'text-destructive')}>
                    {money(tx.amount)}
                  </TableCell>
                  <TableCell>
                    <button
                      onClick={() => setDeleteTarget(tx)}
                      className="text-muted-foreground hover:text-destructive transition-colors"
                      title="Eliminar"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <AddTransactionDialog
        open={addOpen}
        onClose={() => { setAddOpen(false); onRefresh(); }}
        accounts={accounts}
        categories={categories}
      />
      <TransferDialog
        open={transferOpen}
        onClose={() => { setTransferOpen(false); onRefresh(); }}
        accounts={accounts}
      />
      <ConfirmDialog
        open={!!deleteTarget}
        title="Eliminar transaccion"
        message={`Se eliminara "${deleteTarget?.merchant_clean || deleteTarget?.description_raw || 'esta transaccion'}". Esta accion no se puede deshacer.`}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
