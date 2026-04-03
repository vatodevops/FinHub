import Link from 'next/link';

import { PageSection } from '../../../../components/PageSection';
import { Topbar } from '../../../../components/Topbar';

export default async function GoCardlessCallbackPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const requisitionId = typeof params.ref === 'string' ? params.ref : typeof params.requisition_id === 'string' ? params.requisition_id : null;

  return (
    <main className="page">
      <Topbar title="Conexión bancaria devuelta" subtitle="El banco te ha devuelto al frontend; ahora toca refrescar y sincronizar la conexión." />
      <PageSection title="Siguiente paso" subtitle="FinHub aún no ata el callback automáticamente a una fila concreta, pero ya te deja volver a Conexiones y darle refresh/sync.">
        <div className="section-stack">
          <div className="list-item">
            <strong>Referencia recibida:</strong> {requisitionId || '—'}
          </div>
          <div className="small muted">Si la autorización ha ido bien, vuelve a Conexiones, pulsa <strong>Refresh</strong> y luego <strong>Sync</strong>.</div>
          <div>
            <Link href="/connections" className="button">Volver a Conexiones</Link>
          </div>
        </div>
      </PageSection>
    </main>
  );
}
