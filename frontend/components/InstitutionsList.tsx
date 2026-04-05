import { Badge } from '@/components/ui/badge';

type Institution = {
  id: string;
  name: string;
  countries?: string[];
  bic?: string;
};

export function InstitutionsList({ institutions }: { institutions: Institution[] }) {
  return (
    <div className="grid gap-2.5">
      {institutions.map((item) => (
        <div key={item.id} className="flex justify-between items-center gap-3 px-3.5 py-3 rounded-xl border border-border bg-white/[0.02]">
          <div className="grid gap-1">
            <strong>{item.name}</strong>
            <span className="text-muted-foreground text-sm">{item.id}</span>
          </div>
          <Badge variant="outline">{item.countries?.[0] || 'ES'}</Badge>
        </div>
      ))}
    </div>
  );
}
