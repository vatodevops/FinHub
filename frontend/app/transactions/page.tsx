import { Topbar } from '../../components/Topbar';
import { TransactionsExplorer } from '../../components/TransactionsExplorer';
import { api } from '../../lib/api';

export default async function TransactionsPage() {
  const [transactions, categories, duplicateCandidates] = await Promise.all([
    api.transactions(),
    api.categories(),
    api.curveDuplicates(),
  ]);

  return (
    <main className="page">
      <Topbar title="Transacciones" subtitle="Búsqueda, filtros, categorías reales y base para duplicados Curve." />
      <TransactionsExplorer transactions={transactions} categories={categories} duplicateCandidates={duplicateCandidates} />
    </main>
  );
}
