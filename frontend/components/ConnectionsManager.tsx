'use client';

import { useMemo, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { api, type BankConnection } from '@/lib/api';

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
      setMessage('Conexion creada. Se abrira el flujo de autorizacion del banco.');
      if (data.link) {
        window.open(data.link, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'No se pudo crear la conexion');
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
    <div className="grid gap-4">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle>Conectar banco</CardTitle>
        </CardHeader>
        <CardContent>
          {!configured ? (
            <p className="text-muted-foreground text-sm">Falta configurar GoCardless en el backend para mostrar bancos reales y lanzar el flujo.</p>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-[1.2fr_2fr_auto] gap-2.5">
                <Input placeholder="Buscar banco" value={query} onChange={(e) => setQuery(e.target.value)} />
                <select className="flex h-9 w-full rounded-md border border-border bg-input px-3 py-1 text-sm text-foreground" value={institutionId} onChange={(e) => onInstitutionChange(e.target.value)}>
                  {filtered.map((item) => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
                <Button disabled={busy || !institutionId} onClick={connectBank}>{busy ? 'Creando...' : 'Conectar banco'}</Button>
              </div>
              <p className="text-sm text-muted-foreground mt-2.5">
                Se creara una requisition de Open Banking y se abrira la autorizacion del banco en una pestana aparte.
              </p>
            </>
          )}
          {message ? <p className="text-sm mt-3">{message}</p> : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle>Conexiones guardadas</CardTitle>
        </CardHeader>
        <CardContent>
          {connections.length === 0 ? (
            <p className="text-muted-foreground text-sm">Aun no hay bancos conectados.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Banco</TableHead>
                  <TableHead>Referencia</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {connections.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="grid gap-1">
                        <strong>{item.institution_name || item.institution_external_id || 'Banco'}</strong>
                        <span className="text-muted-foreground text-sm">{item.requisition_id}</span>
                      </div>
                    </TableCell>
                    <TableCell>{item.reference}</TableCell>
                    <TableCell><Badge variant="outline">{item.status}</Badge></TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {item.link ? (
                          <Button variant="secondary" size="sm" asChild>
                            <a href={item.link} target="_blank" rel="noreferrer">Autorizar</a>
                          </Button>
                        ) : null}
                        <Button variant="secondary" size="sm" onClick={async () => {
                          setMessage(null);
                          const refreshed = await api.refreshBankConnection(item.id);
                          setConnections((prev) => prev.map((row) => row.id === item.id ? refreshed : row));
                          setMessage('Conexion refrescada; si el banco ya devolvio cuentas, deberia pasar a linked.');
                        }}>
                          Refresh
                        </Button>
                        <Button variant="secondary" size="sm" onClick={() => syncConnection(item.id)} disabled={syncingId === item.id}>
                          {syncingId === item.id ? 'Sincronizando...' : 'Sync'}
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
