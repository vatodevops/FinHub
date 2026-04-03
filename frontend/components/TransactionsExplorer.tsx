'use client';

import { useMemo, useState } from 'react';

import { api, type Category, type CurveDuplicateCandidate, type Transaction } from '../lib/api';
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
    <div className="section-stack">
      <div className="panel">
        <h2>Explorador de transacciones</h2>
        <div className="form-inline" style={{ gridTemplateColumns: '2fr 1fr 1fr auto auto' }}>
          <input className="input" placeholder="Buscar por merchant, descripción o categoría" value={query} onChange={(e) => setQuery(e.target.value)} />
          <select className="select" value={channel} onChange={(e) => setChannel(e.target.value)}>
            <option value="all">Todos los canales</option>
            <option value="card">Card</option>
            <option value="transfer">Transfer</option>
            <option value="direct_debit">Direct debit</option>
            <option value="other">Other</option>
          </select>
          <select className="select" value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
            <option value="all">Todos los orígenes</option>
            <option value="bank">Bank</option>
            <option value="curve">Curve</option>
          </select>
          <button className={`button secondary ${curveOnly ? 'is-active' : ''}`} onClick={() => setCurveOnly((v) => !v)}>
            {curveOnly ? 'Duplicados Curve: ON' : 'Duplicados Curve'}
          </button>
          <div className="badge">{filtered.length} filas</div>
        </div>
      </div>

      <CurveDuplicatesPanel items={duplicateCandidates} />

      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Merchant</th>
              <th>Descripción</th>
              <th>Canal</th>
              <th>Origen</th>
              <th>Categoría</th>
              <th>Curve?</th>
              <th>Importe</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((tx) => {
              const curveDup = looksLikeCurveDuplicate(tx);
              return (
                <tr key={tx.id}>
                  <td>{tx.booked_at ? tx.booked_at.slice(0, 10) : '—'}</td>
                  <td>{tx.merchant_clean || tx.merchant_raw || '—'}</td>
                  <td>{tx.description_raw || '—'}</td>
                  <td>{tx.channel}</td>
                  <td><span className="badge">{tx.source_type}</span></td>
                  <td>
                    <select
                      className="select"
                      value={tx.category_id || ''}
                      disabled={busyTxId === tx.id}
                      onChange={(e) => assignCategory(tx.id, e.target.value)}
                    >
                      <option value="">Sin categoría</option>
                      {categories.map((category) => (
                        <option key={category.id} value={category.id}>{category.name}</option>
                      ))}
                    </select>
                  </td>
                  <td>{curveDup ? <span className="badge">posible dup</span> : '—'}</td>
                  <td className={Number(tx.amount) >= 0 ? 'positive' : 'negative'}>{money(tx.amount)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
