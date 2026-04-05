import './globals.css';
import type { ReactNode } from 'react';

import { Sidebar } from '@/components/Sidebar';

export const metadata = {
  title: 'FinHub',
  description: 'Personal finance hub',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body>
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-[260px_1fr]">
          <Sidebar />
          <main className="p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
