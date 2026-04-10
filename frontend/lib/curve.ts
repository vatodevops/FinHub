import type { Transaction } from './api';

export function looksLikeCurveDuplicate(tx: Transaction) {
  const text = `${tx.description_raw || ''} ${tx.merchant_raw || ''}`.toUpperCase();
  return tx.source_type === 'bank' && (text.includes('CRV-') || text.includes('CURVE'));
}

export function filterVisibleTransactions<T extends Transaction>(transactions: T[]) {
  return transactions.filter((tx) => !looksLikeCurveDuplicate(tx));
}
