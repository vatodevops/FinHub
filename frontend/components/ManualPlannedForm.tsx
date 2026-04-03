'use client';

import { useState } from 'react';
import { api } from '../lib/api';

export function ManualPlannedForm() {
  const [name, setName] = useState('Peluquería');
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
    <div className="panel">
      <h3>Nuevo gasto manual</h3>
      <div className="form-inline">
        <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre" />
        <input className="input" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Importe" />
        <input className="input" type="date" value={expectedDate} onChange={(e) => setExpectedDate(e.target.value)} />
        <select className="select" value={kind} onChange={(e) => setKind(e.target.value)}>
          <option value="recurring">recurrente</option>
          <option value="one_off">puntual</option>
        </select>
        <button className="button" disabled={busy} onClick={submit}>{busy ? 'Guardando...' : 'Crear'}</button>
      </div>
      <div className="small muted" style={{ marginTop: 10 }}>Útil para peluquería, efectivo, pagos informales y otros gastos fuera de banco/tarjeta.</div>
      {done ? <div className="small" style={{ marginTop: 10 }}>{done}</div> : null}
    </div>
  );
}
