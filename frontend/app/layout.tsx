import './globals.css';
import type { ReactNode } from 'react';

import { Sidebar } from '../components/Sidebar';

export const metadata = {
  title: 'FinHub',
  description: 'Personal finance hub',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body>
        <div className="app-shell">
          <Sidebar />
          <div className="content-shell">{children}</div>
        </div>
      </body>
    </html>
  );
}
