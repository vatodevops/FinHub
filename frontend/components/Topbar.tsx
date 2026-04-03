export function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="topbar">
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle ? <div className="page-subtitle">{subtitle}</div> : null}
      </div>
      <div className="topbar-actions">
        <div className="badge">Localhost mode</div>
      </div>
    </div>
  );
}
