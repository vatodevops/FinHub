'use client';

import { useEffect, useState } from 'react';
import { Topbar } from '@/components/Topbar';
import { TransactionsExplorer } from '@/components/TransactionsExplorer';
import { api, type Account, type Category, type CurveDuplicateCandidate, type Transaction } from '@/lib/api';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [duplicates, setDuplicates] = useState<CurveDuplicateCandidate[]>([]);

  function refresh() {
    Promise.all([
      api.transactions(),
      api.categories(),
      api.accounts(),
      api.curveDuplicates(),
    ]).then(([t, c, a, d]) => {
      setTransactions(t);
      setCategories(c);
      setAccounts(a);
      setDuplicates(d);
    });
  }

  useEffect(() => { refresh(); }, []);

  return (
    <div className="max-w-[1440px] mx-auto">
      <Topbar title="Transacciones" subtitle="Gestiona todos tus movimientos, filtra, categoriza y añade nuevos." />
      <TransactionsExplorer
        transactions={transactions}
        categories={categories}
        accounts={accounts}
        duplicateCandidates={duplicates}
        onRefresh={refresh}
      />
    </div>
  );
}
