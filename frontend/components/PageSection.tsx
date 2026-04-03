import type { ReactNode } from 'react';

export function PageSection({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <section className="panel">
      <div className="section-head">
        <div>
          <h2>{title}</h2>
          {subtitle ? <div className="muted small">{subtitle}</div> : null}
        </div>
      </div>
      {children}
    </section>
  );
}
