'use client';

import { useMemo, useState } from 'react';

import { api, type BankConnection } from '../lib/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8081/api';

type Institution = {
  id: string;
  name: string;
  bic?: string;
  transaction_total_days?: string;
  countries?: string[];
  logo?: string;
};

export function ConnectionsManager({
  initialConnections,
  institutions,
  configured,
}: {
  initialConnections: BankConnection[];
  institutions: Institution[];
  configured: boolean;
}) {
  const [connections, setConnections] = useState(initialConnections);
  const [query, setQuery] = useState('');
  const [institutionId, setInstitutionId] = useState(institutions[0]?.id || '');
  const [institutionName, setInstitutionName] = useState(institutions[0]?.name || '');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [syncingId, setSyncingId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return institutions;
    return institutions.filter((item) => item.name.toLowerCase().includes(q) || item.id.toLowerCase().includes(q));
  }, [institutions, query]);

  function onInstitutionChange(nextId: string) {
    setInstitutionId(nextId);
    const found = institutions.find((item) => item.id === nextId);
    setInstitutionName(found?.name || 'Banco');
  }

  async function connectBank() {
    if (!institutionId) return;
    setBusy(true);
    setMessage(null);
    try {
      const reference = `finhub-${Date.now()}`;
      const url = `${API_BASE}/connectors/gocardless/requisition?institution_id=${encodeURIComponent(institutionId)}&reference=${encodeURIComponent(reference)}&institution_name=${encodeURIComponent(institutionName)}`;
      const res = await fetch(url, { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data?.error) {
        throw new Error(data?.error || `HTTP ${res.status}`);
      }
      setConnections((prev) => [data, ...prev]);
      setMessage('Conexión creada. Se abrirá el flujo de autorización del banco.');
      if (data.link) {
        window.open(data.link, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'No se pudo crear la conexión');
    } finally {
      setBusy(false);
    }
  }

  async function syncConnection(connectionId: string) {
    setSyncingId(connectionId);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/bank-connections/${connectionId}/sync`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data?.error) {
        throw new Error(data?.error || `HTTP ${res.status}`);
      }
      setConnections((prev) => prev.map((item) => item.id === connectionId ? { ...item, status: data.status, last_synced_at: new Date().toISOString() } : item));
      setMessage(`Sync hecho: ${data.transactions_upserted} movimientos revisados.`);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'No se pudo sincronizar');
    } finally {
      setSyncingId(null);
    }
  }

  return (
    <div className="section-stack">
      <div className="panel">
        <h2>Conectar banco</h2>
        {!configured ? (
          <div className="muted small">Falta configurar GoCardless en el backend para mostrar bancos reales y lanzar el flujo.</div>
        ) : (
          <>
            <div className="form-inline" style={{ gridTemplateColumns: '1.2fr 2fr auto' }}>
              <input className="input" placeholder="Buscar banco" value={query} onChange={(e) => setQuery(e.target.value)} />
              <select className="select" value={institutionId} onChange={(e) => onInstitutionChange(e.target.value)}>
                {filtered.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
              <button className="button" disabled={busy || !institutionId} onClick={connectBank}>{busy ? 'Creando...' : 'Conectar banco'}</button>
            </div>
            <div className="small muted" style={{ marginTop: 10 }}>
              Se creará una requisition de Open Banking y se abrirá la autorización del banco en una pestaña aparte.
            </div>
          </>
        )}
        {message ? <div className="small" style={{ marginTop: 12 }}>{message}</div> : null}
      </div>

      <div className="panel">
        <h2>Conexiones guardadas</h2>
        {connections.length === 0 ? (
          <div className="muted small">Aún no hay bancos conectados.</div>
        ) : (
          <table className="table">
            <thead><tr><th>Banco</th><th>Referencia</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
              {connections.map((item) => (
                <tr key={item.id}>
                  <td>
                    <div className="stack-xs">
                      <strong>{item.institution_name || item.institution_external_id || 'Banco'}</strong>
                      <span className="muted small">{item.requisition_id}</span>
                    </div>
                  </td>
                  <td>{item.reference}</td>
                  <td><span className="badge">{item.status}</span></td>
                  <td>
                    <div className="row-between" style={{ justifyContent: 'flex-start', gap: 8 }}>
                      {item.link ? (
                        <a className="button secondary small" href={item.link} target="_blank" rel="noreferrer">Autorizar</a>
                      ) : null}
                      <button className="button secondary small" onClick={async () => {
                        setMessage(null);
                        const refreshed = await api.refreshBankConnection(item.id);
                        setConnections((prev) => prev.map((row) => row.id === item.id ? refreshed : row));
                        setMessage('Conexión refrescada; si el banco ya devolvió cuentas, debería pasar a linked.');
                      }}>
                        Refresh
                      </button>
                      <button className="button secondary small" onClick={() => syncConnection(item.id)} disabled={syncingId === item.id}>
                        {syncingId === item.id ? 'Sincronizando...' : 'Sync'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
