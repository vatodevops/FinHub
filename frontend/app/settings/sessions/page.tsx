'use client';

import { useEffect, useState } from 'react';
import { LogOut, Trash2 } from 'lucide-react';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { Badge } from '@/components/ui/badge';
import { api, AuthSession } from '@/lib/api';

function formatDate(value?: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleString('es-ES', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

function shortenUA(ua?: string | null) {
  if (!ua) return 'Cliente desconocido';
  const m =
    ua.match(/(Edg|Chrome|Firefox|Safari|CriOS|FxiOS)\/[\d.]+/) ||
    ua.match(/[A-Za-z]+\/[\d.]+/);
  const browser = m ? m[0] : ua.slice(0, 40);
  let os = 'Otro';
  if (/Windows/.test(ua)) os = 'Windows';
  else if (/Mac OS X/.test(ua)) os = 'macOS';
  else if (/Android/.test(ua)) os = 'Android';
  else if (/iPhone|iPad|iOS/.test(ua)) os = 'iOS';
  else if (/Linux/.test(ua)) os = 'Linux';
  return `${browser} · ${os}`;
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<AuthSession[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revokeTarget, setRevokeTarget] = useState<AuthSession | null>(null);
  const [confirmAll, setConfirmAll] = useState(false);
  const [busy, setBusy] = useState(false);

  function refresh() {
    api
      .listSessions()
      .then((rows) => {
        setSessions(rows);
        setError(null);
      })
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleRevoke() {
    if (!revokeTarget) return;
    setBusy(true);
    try {
      await api.revokeSession(revokeTarget.id);
      setRevokeTarget(null);
      refresh();
    } finally {
      setBusy(false);
    }
  }

  async function handleLogoutAll() {
    setBusy(true);
    try {
      await api.logoutAll();
      window.location.href = '/login';
    } finally {
      setBusy(false);
      setConfirmAll(false);
    }
  }

  const others = (sessions ?? []).filter((s) => !s.current);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar
        title="Sesiones activas"
        subtitle="Dispositivos donde tu cuenta está abierta. Revoca cualquiera que no reconozcas."
      />

      <PageSection
        title="Tus sesiones"
        subtitle={
          sessions
            ? `${sessions.length} sesión${sessions.length === 1 ? '' : 'es'} activa${sessions.length === 1 ? '' : 's'}.`
            : 'Cargando…'
        }
        action={
          others.length > 0 ? (
            <button
              onClick={() => setConfirmAll(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border text-sm text-muted-foreground hover:text-foreground hover:bg-accent/8 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Cerrar todas
            </button>
          ) : null
        }
      >
        {error ? (
          <div className="text-sm text-destructive">{error}</div>
        ) : !sessions ? (
          <div className="text-sm text-muted-foreground">Cargando sesiones…</div>
        ) : sessions.length === 0 ? (
          <div className="text-sm text-muted-foreground">No hay sesiones registradas.</div>
        ) : (
          <ul className="grid gap-3">
            {sessions.map((s) => (
              <li
                key={s.id}
                className="flex items-start justify-between gap-4 rounded-xl border border-border bg-white/[0.02] p-4"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-foreground truncate">
                      {shortenUA(s.user_agent)}
                    </span>
                    {s.current ? <Badge>Esta sesión</Badge> : null}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">
                    IP {s.ip_address || 'desconocida'} · Última actividad {formatDate(s.last_seen_at)}
                  </div>
                  <div className="mt-0.5 text-xs text-muted-foreground">
                    Iniciada {formatDate(s.created_at)} · Expira {formatDate(s.expires_at)}
                  </div>
                </div>
                {!s.current && (
                  <button
                    onClick={() => setRevokeTarget(s)}
                    className="shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg border border-border text-sm text-muted-foreground hover:text-destructive hover:border-destructive/40 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Revocar
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </PageSection>

      <ConfirmDialog
        open={!!revokeTarget}
        title="Revocar sesión"
        message={`Cerrarás la sesión en ${shortenUA(revokeTarget?.user_agent)}. Tendrás que volver a iniciar sesión en ese dispositivo.`}
        confirmLabel={busy ? 'Revocando…' : 'Revocar'}
        onCancel={() => setRevokeTarget(null)}
        onConfirm={handleRevoke}
      />

      <ConfirmDialog
        open={confirmAll}
        title="Cerrar todas las sesiones"
        message="Se cerrarán todas tus sesiones, incluida esta. Tendrás que volver a iniciar sesión."
        confirmLabel={busy ? 'Cerrando…' : 'Cerrar todas'}
        onCancel={() => setConfirmAll(false)}
        onConfirm={handleLogoutAll}
      />
    </div>
  );
}
