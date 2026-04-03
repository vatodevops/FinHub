type Institution = {
  id: string;
  name: string;
  countries?: string[];
  bic?: string;
};

export function InstitutionsList({ institutions }: { institutions: Institution[] }) {
  return (
    <div className="list">
      {institutions.map((item) => (
        <div key={item.id} className="list-item row-between">
          <div className="stack-xs">
            <strong>{item.name}</strong>
            <span className="muted small">{item.id}</span>
          </div>
          <span className="badge">{item.countries?.[0] || 'ES'}</span>
        </div>
      ))}
    </div>
  );
}
