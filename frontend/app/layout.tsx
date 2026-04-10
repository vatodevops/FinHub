import './globals.css';
import type { ReactNode } from 'react';

import { AppShell } from '@/components/AppShell';

export const metadata = {
  title: 'FinHub',
  description: 'Personal finance hub',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
