export function EmptyState({ title, text }: { title: string; text: string }) {
  return (
    <div className="py-5 px-3 border border-dashed border-border rounded-xl">
      <p className="font-bold mb-1">{title}</p>
      <p className="text-muted-foreground text-sm">{text}</p>
    </div>
  );
}
