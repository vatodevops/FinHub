'use client';

import { cn } from '@/lib/utils';

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Eliminar',
  onConfirm,
  onCancel,
  destructive = true,
}: {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  destructive?: boolean;
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onCancel} />
      <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-sm mx-4 p-6 shadow-2xl">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <p className="text-muted-foreground text-sm mt-2">{message}</p>
        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors text-sm"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className={cn(
              'px-4 py-2 rounded-xl font-medium text-white text-sm transition-colors',
              destructive ? 'bg-destructive hover:bg-destructive/90' : 'bg-accent hover:bg-accent/90'
            )}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
