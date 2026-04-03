import type { CurveDuplicateCandidate } from '../lib/api';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export function CurveDuplicatesPanel({ items }: { items: CurveDuplicateCandidate[] }) {
  return (
    <div className="panel">
      <h2>Posibles duplicados Curve</h2>
      <table className="table">
        <thead><tr><th>Confidence</th><th>Curve</th><th>Banco</th><th>Importe</th></tr></thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={`${item.curve_transaction.id}-${item.bank_transaction.id}-${idx}`}>
              <td>{Math.round(item.confidence * 100)}%</td>
              <td>{item.curve_transaction.merchant_clean || item.curve_transaction.merchant_raw || '—'}</td>
              <td>{item.bank_transaction.description_raw || item.bank_transaction.merchant_raw || '—'}</td>
              <td>{money(item.bank_transaction.amount)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
