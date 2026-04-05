import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';

export default async function GoCardlessCallbackPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const requisitionId = typeof params.ref === 'string' ? params.ref : typeof params.requisition_id === 'string' ? params.requisition_id : null;

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Conexion bancaria devuelta" subtitle="El banco te ha devuelto al frontend; ahora toca refrescar y sincronizar la conexion." />
      <PageSection title="Siguiente paso" subtitle="FinHub aun no ata el callback automaticamente a una fila concreta, pero ya te deja volver a Conexiones y darle refresh/sync.">
        <div className="grid gap-4">
          <div className="px-3.5 py-3 rounded-xl border border-border bg-white/[0.02]">
            <strong>Referencia recibida:</strong> {requisitionId || '\u2014'}
          </div>
          <p className="text-sm text-muted-foreground">Si la autorizacion ha ido bien, vuelve a Conexiones, pulsa <strong>Refresh</strong> y luego <strong>Sync</strong>.</p>
          <div>
            <Button asChild>
              <Link href="/connections">Volver a Conexiones</Link>
            </Button>
          </div>
        </div>
      </PageSection>
    </div>
  );
}
