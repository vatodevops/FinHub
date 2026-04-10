'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';

import { Sidebar } from '@/components/Sidebar';
import { api, ApiError, type User } from '@/lib/api';
import { AuthContext } from '@/lib/auth';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isLoginPage = pathname === '/login';
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const me = await api.me();
      setUser(me);
      return me;
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setUser(null);
        return null;
      }
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    await api.logout();
    setUser(null);
    router.replace('/login');
  }, [router]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    refresh()
      .then((me) => {
        if (cancelled) return;
        if (!me && !isLoginPage) {
          router.replace('/login');
        }
        if (me && isLoginPage) {
          router.replace('/');
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isLoginPage, pathname, refresh, router]);

  const value = useMemo(() => ({ user, loading, refresh, logout }), [user, loading, refresh, logout]);

  return (
    <AuthContext.Provider value={value}>
      {loading ? (
        <div className="min-h-screen grid place-items-center bg-[#08101d] text-muted-foreground">Cargando...</div>
      ) : isLoginPage ? (
        children
      ) : (
        <div className="min-h-screen grid grid-cols-1 lg:grid-cols-[260px_1fr]">
          <Sidebar />
          <main className="p-6">{children}</main>
        </div>
      )}
    </AuthContext.Provider>
  );
}
