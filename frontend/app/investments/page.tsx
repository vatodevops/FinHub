import { EmptyState } from '@/components/EmptyState';
import { PageSection } from '@/components/PageSection';
import { Topbar } from '@/components/Topbar';

export default function InvestmentsPage() {
  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Inversiones" subtitle="Preparado para MyInvestor, Indexa y el resto cuando entren conectores o importaciones." />
      <PageSection title="Bloque en preparacion" subtitle="Aqui acabara habiendo patrimonio, posiciones y evolucion historica.">
        <EmptyState title="Aun no hay conectores de inversion cerrados" text="La UI ya reserva su sitio para que el producto tenga estructura de app financiera completa, no solo de bancos." />
      </PageSection>
    </div>
  );
}
