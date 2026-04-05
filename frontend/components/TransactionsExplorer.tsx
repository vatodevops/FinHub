'use client';

import { useMemo, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api, type Category, type CurveDuplicateCandidate, type Transaction } from '@/lib/api';
import { cn } from '@/lib/utils';
import { CurveDuplicatesPanel } from './CurveDuplicatesPanel';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

function looksLikeCurveDuplicate(tx: Transaction) {
  const text = `${tx.description_raw || ''} ${tx.merchant_raw || ''}`.toUpperCase();
  return tx.source_type === 'bank' && (text.includes('CRV-') || text.includes('CURVE'));
}

export function TransactionsExplorer({
  transactions,
  categories,
  duplicateCandidates,
}: {
  transactions: Transaction[];
  categories: Category[];
  duplicateCandidates: CurveDuplicateCandidate[];
}) {
  const [query, setQuery] = useState('');
  const [channel, setChannel] = useState('all');
  const [sourceType, setSourceType] = useState('all');
  const [curveOnly, setCurveOnly] = useState(false);
  const [rows, setRows] = useState(transactions);
  const [busyTxId, setBusyTxId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((tx) => {
      if (channel !== 'all' && tx.channel !== channel) return false;
      if (sourceType !== 'all' && tx.source_type !== sourceType) return false;
      if (curveOnly && !looksLikeCurveDuplicate(tx)) return false;
      if (!q) return true;
      const blob = `${tx.merchant_clean || ''} ${tx.merchant_raw || ''} ${tx.description_raw || ''} ${tx.category_name || ''}`.toLowerCase();
      return blob.includes(q);
    });
  }, [rows, query, channel, sourceType, curveOnly]);

  async function assignCategory(transactionId: string, categoryId: string) {
    setBusyTxId(transactionId);
    try {
      const updated = await api.updateTransactionCategory(transactionId, categoryId || null);
      setRows((prev) => prev.map((row) => (row.id === transactionId ? updated : row)));
    } finally {
      setBusyTxId(null);
    }
  }

  return (
    <div className="grid gap-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle>Explorador de transacciones</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_auto_auto] gap-2.5">
            <Input placeholder="Buscar por merchant, descripcion o categoria" value={query} onChange={(e) => setQuery(e.target.value)} />
            <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="all">Todos los canales</option>
              <option value="card">Card</option>
              <option value="transfer">Transfer</option>
              <option value="direct_debit">Direct debit</option>
              <option value="other">Other</option>
            </select>
            <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
              <option value="all">Todos los origenes</option>
              <option value="bank">Bank</option>
              <option value="curve">Curve</option>
            </select>
            <Button variant={curveOnly ? 'default' : 'secondary'} onClick={() => setCurveOnly((v) => !v)}>
              {curveOnly ? 'Duplicados Curve: ON' : 'Duplicados Curve'}
            </Button>
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
                <TableHead>Merchant</TableHead>
                <TableHead>Descripcion</TableHead>
                <TableHead>Canal</TableHead>
                <TableHead>Origen</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Curve?</TableHead>
                <TableHead>Importe</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((tx) => {
                const curveDup = looksLikeCurveDuplicate(tx);
                return (
                  <TableRow key={tx.id}>
                    <TableCell>{tx.booked_at ? tx.booked_at.slice(0, 10) : '\u2014'}</TableCell>
                    <TableCell>{tx.merchant_clean || tx.merchant_raw || '\u2014'}</TableCell>
                    <TableCell>{tx.description_raw || '\u2014'}</TableCell>
                    <TableCell>{tx.channel}</TableCell>
                    <TableCell><Badge variant="outline">{tx.source_type}</Badge></TableCell>
                    <TableCell>
                      <select
                        className="flex h-8 w-full rounded-md border border-border bg-input px-2 py-1 text-sm text-foreground"
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
                    <TableCell>{curveDup ? <Badge variant="destructive">posible dup</Badge> : '\u2014'}</TableCell>
                    <TableCell className={cn(Number(tx.amount) >= 0 ? 'text-success' : 'text-destructive')}>{money(tx.amount)}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
