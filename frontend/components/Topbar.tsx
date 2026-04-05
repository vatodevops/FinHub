import { Badge } from '@/components/ui/badge';

export function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="flex justify-between items-start gap-4 mb-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight m-0 mb-1.5">{title}</h1>
        {subtitle ? <p className="text-muted-foreground m-0">{subtitle}</p> : null}
      </div>
      <Badge variant="outline">Localhost mode</Badge>
    </div>
  );
}
