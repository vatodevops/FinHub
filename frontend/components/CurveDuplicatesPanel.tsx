import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import type { CurveDuplicateCandidate } from '@/lib/api';

function money(value: string) {
  const n = Number(value || 0);
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
}

export function CurveDuplicatesPanel({ items }: { items: CurveDuplicateCandidate[] }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle>Posibles duplicados Curve</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Confidence</TableHead>
              <TableHead>Curve</TableHead>
              <TableHead>Banco</TableHead>
              <TableHead>Importe</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item, idx) => (
              <TableRow key={`${item.curve_transaction.id}-${item.bank_transaction.id}-${idx}`}>
                <TableCell>{Math.round(item.confidence * 100)}%</TableCell>
                <TableCell>{item.curve_transaction.merchant_clean || item.curve_transaction.merchant_raw || '\u2014'}</TableCell>
                <TableCell>{item.bank_transaction.description_raw || item.bank_transaction.merchant_raw || '\u2014'}</TableCell>
                <TableCell>{money(item.bank_transaction.amount)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
