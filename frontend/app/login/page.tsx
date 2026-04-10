'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { api, ApiError } from '@/lib/api';
import { cn } from '@/lib/utils';

type Mode = 'login' | 'register';

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>('login');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (mode === 'register' && password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    setSubmitting(true);
    try {
      if (mode === 'register') {
        await api.register({ full_name: fullName.trim() || null, email: email.trim(), password });
      } else {
        await api.login({ email: email.trim(), password });
      }
      router.replace('/');
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo iniciar sesion');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen grid place-items-center bg-[radial-gradient(circle_at_top,#182847_0%,#08101d_55%)] p-6">
      <div className="w-full max-w-md rounded-3xl border border-border bg-[#0d1526]/95 shadow-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-11 h-11 grid place-items-center rounded-2xl bg-linear-to-b from-[#7aaeff] to-[#4779ff] text-[#07111f] font-black text-lg">F</div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">FinHub</h1>
            <p className="text-sm text-muted-foreground">Acceso privado a tu workspace financiero</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 p-1 rounded-2xl bg-white/[0.03] border border-border mb-6">
          <button onClick={() => { setMode('login'); setError(''); }} className={cn('px-4 py-2.5 rounded-xl text-sm transition-colors', mode === 'login' ? 'bg-accent text-white' : 'text-muted-foreground hover:text-foreground')}>
            Entrar
          </button>
          <button onClick={() => { setMode('register'); setError(''); }} className={cn('px-4 py-2.5 rounded-xl text-sm transition-colors', mode === 'register' ? 'bg-accent text-white' : 'text-muted-foreground hover:text-foreground')}>
            Crear cuenta
          </button>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4">
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Nombre</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40" placeholder="Ej: Alejandro" />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40" placeholder="tu@email.com" required />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1.5">Contraseña</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40" placeholder="Minimo 8 caracteres" required minLength={8} />
          </div>

          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-foreground mb-1.5">Repetir contraseña</label>
              <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40" placeholder="Repite la contraseña" required minLength={8} />
            </div>
          )}

          {error ? <p className="text-sm text-destructive">{error}</p> : null}

          <button type="submit" disabled={submitting} className="mt-2 px-5 py-3 rounded-xl font-medium bg-accent text-white hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            {submitting ? 'Procesando...' : mode === 'register' ? 'Crear cuenta y entrar' : 'Entrar'}
          </button>
        </form>

        <p className="text-xs text-muted-foreground mt-5">
          Esta primera version protege el acceso a la app. Google OAuth lo metemos despues como proveedor adicional.
        </p>
      </div>
    </div>
  );
}
