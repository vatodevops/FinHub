import { EmptyState } from '@/components/EmptyState';
import { ConnectionsManager } from '@/components/ConnectionsManager';
import { InstitutionsList } from '@/components/InstitutionsList';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';
import { api } from '@/lib/api';

export default async function ConnectionsPage() {
  const [connections, institutions] = await Promise.all([
    api.bankConnections(),
    api.gocardlessInstitutions(),
  ]);

  const configured = !('error' in institutions);
  const institutionList = Array.isArray(institutions) ? institutions.slice(0, 18) : [];

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Conexiones" subtitle="Open Banking real, estado de enlaces y sincronizacion inicial de bancos." />
      <div className="grid grid-cols-1 lg:grid-cols-[1.15fr_0.85fr] gap-4">
        <ConnectionsManager
          initialConnections={connections}
          institutions={institutionList}
          configured={configured}
        />

        <PageSection
          title="Instituciones disponibles"
          subtitle={configured ? 'Bancos visibles desde GoCardless para ES.' : 'Falta configurar GoCardless en backend.'}
        >
          {!configured ? (
            <EmptyState
              title="GoCardless no configurado"
              text="Rellena GOCARDLESS_SECRET_ID y GOCARDLESS_SECRET_KEY para poder conectar bancos reales desde esta pantalla."
            />
          ) : (
            <InstitutionsList institutions={institutionList} />
          )}
        </PageSection>
      </div>
    </div>
  );
}
