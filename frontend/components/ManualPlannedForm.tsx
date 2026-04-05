'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

export function ManualPlannedForm() {
  const [name, setName] = useState('Peluqueria');
  const [amount, setAmount] = useState('18');
  const [expectedDate, setExpectedDate] = useState('');
  const [kind, setKind] = useState('recurring');
  const [status, setStatus] = useState('planned');
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState<string | null>(null);

  async function submit() {
    setBusy(true);
    setDone(null);
    try {
      await api.createManualPlannedItem({
        name,
        amount,
        expected_date: expectedDate || null,
        kind,
        status,
        currency: 'EUR',
      });
      setDone('Gasto manual creado');
    } catch (err) {
      setDone(err instanceof Error ? err.message : 'Error creando gasto');
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle>Nuevo gasto manual</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_1fr_auto] gap-2.5">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre" />
          <Input value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Importe" />
          <Input type="date" value={expectedDate} onChange={(e) => setExpectedDate(e.target.value)} />
          <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="recurring">recurrente</option>
            <option value="one_off">puntual</option>
          </select>
          <Button disabled={busy} onClick={submit}>{busy ? 'Guardando...' : 'Crear'}</Button>
        </div>
        <p className="text-sm text-muted-foreground mt-2.5">Util para peluqueria, efectivo, pagos informales y otros gastos fuera de banco/tarjeta.</p>
        {done ? <p className="text-sm mt-2.5">{done}</p> : null}
      </CardContent>
    </Card>
  );
}
