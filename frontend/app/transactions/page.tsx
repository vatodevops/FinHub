import { Topbar } from '@/components/Topbar';
import { TransactionsExplorer } from '@/components/TransactionsExplorer';
import { api } from '@/lib/api';

export default async function TransactionsPage() {
  const [transactions, categories, duplicateCandidates] = await Promise.all([
    api.transactions(),
    api.categories(),
    api.curveDuplicates(),
  ]);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Transacciones" subtitle="Busqueda, filtros, categorias reales y base para duplicados Curve." />
      <TransactionsExplorer transactions={transactions} categories={categories} duplicateCandidates={duplicateCandidates} />
    </div>
  );
}
