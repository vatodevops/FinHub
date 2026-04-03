import { EmptyState } from '../../components/EmptyState';
import { PageSection } from '../../components/PageSection';
import { Topbar } from '../../components/Topbar';

export default function InvestmentsPage() {
  return (
    <main className="page">
      <Topbar title="Inversiones" subtitle="Preparado para MyInvestor, Indexa y el resto cuando entren conectores o importaciones." />
      <PageSection title="Bloque en preparación" subtitle="Aquí acabará habiendo patrimonio, posiciones y evolución histórica.">
        <EmptyState title="Aún no hay conectores de inversión cerrados" text="La UI ya reserva su sitio para que el producto tenga estructura de app financiera completa, no solo de bancos." />
      </PageSection>
    </main>
  );
}
