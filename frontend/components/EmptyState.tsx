export function EmptyState({ title, text }: { title: string; text: string }) {
  return (
    <div className="empty-state">
      <div className="empty-title">{title}</div>
      <div className="muted small">{text}</div>
    </div>
  );
}
