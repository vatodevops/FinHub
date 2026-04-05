import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export function MetricCard({ label, value, hint, tone }: { label: string; value: string; hint?: string; tone?: 'positive' | 'negative' }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <p className="text-muted-foreground text-sm">{label}</p>
        <p className={cn('text-3xl font-bold mt-2', tone === 'positive' && 'text-success', tone === 'negative' && 'text-destructive')}>
          {value}
        </p>
        {hint ? <p className="text-muted-foreground text-sm mt-1">{hint}</p> : null}
      </CardContent>
    </Card>
  );
}
