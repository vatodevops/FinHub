export function MetricCard({ label, value, hint, tone }: { label: string; value: string; hint?: string; tone?: 'positive' | 'negative'; }) {
  return (
    <div className="panel">
      <div className="muted small">{label}</div>
      <div className={`kpi ${tone || ''}`}>{value}</div>
      {hint ? <div className="muted small">{hint}</div> : null}
    </div>
  );
}
