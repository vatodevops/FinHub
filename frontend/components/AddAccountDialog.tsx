'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

const ACCOUNT_TYPES = [
  { value: 'checking', label: 'Cuenta corriente', icon: '🏦', description: 'Cuenta bancaria principal para el dia a dia' },
  { value: 'savings', label: 'Cuenta de ahorro', icon: '💰', description: 'Cuenta para ahorrar con mejor rentabilidad' },
  { value: 'credit_card', label: 'Tarjeta de credito', icon: '💳', description: 'Linea de credito con pago aplazado' },
  { value: 'investment', label: 'Cuenta de inversion', icon: '📈', description: 'Broker, fondos o cartera de inversion' },
  { value: 'cash', label: 'Efectivo', icon: '💵', description: 'Dinero en efectivo o monedero' },
];

const CURRENCIES = ['EUR', 'USD', 'GBP'];

type Step = 'type' | 'details';

export function AddAccountDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const router = useRouter();
  const [step, setStep] = useState<Step>('type');
  const [selectedType, setSelectedType] = useState('');
  const [name, setName] = useState('');
  const [institutionName, setInstitutionName] = useState('');
  const [currency, setCurrency] = useState('EUR');
  const [initialBalance, setInitialBalance] = useState('');
  const [iban, setIban] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  function reset() {
    setStep('type');
    setSelectedType('');
    setName('');
    setInstitutionName('');
    setCurrency('EUR');
    setInitialBalance('');
    setIban('');
    setError('');
  }

  function handleClose() {
    reset();
    onClose();
  }

  function handleSelectType(type: string) {
    setSelectedType(type);
    setStep('details');
  }

  function handleBack() {
    setStep('type');
    setError('');
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError('El nombre es obligatorio');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await api.createAccount({
        name: name.trim(),
        kind: selectedType,
        currency,
        initial_balance: initialBalance ? parseFloat(initialBalance) : 0,
        iban: iban.trim() || null,
        institution_name: institutionName.trim() || null,
      });
      handleClose();
      router.refresh();
    } catch (err) {
      setError('Error al crear la cuenta. Intentalo de nuevo.');
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) return null;

  const selectedTypeInfo = ACCOUNT_TYPES.find((t) => t.value === selectedType);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={handleClose} />
      <div className="relative bg-[#0d1526] border border-border rounded-2xl w-full max-w-lg mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-3">
            {step === 'details' && (
              <button onClick={handleBack} className="text-muted-foreground hover:text-foreground transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
              </button>
            )}
            <h2 className="text-lg font-semibold text-foreground">
              {step === 'type' ? 'Nueva cuenta' : `Nueva ${selectedTypeInfo?.label.toLowerCase()}`}
            </h2>
          </div>
          <button onClick={handleClose} className="text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>

        {/* Step 1: Select type */}
        {step === 'type' && (
          <div className="p-6">
            <p className="text-muted-foreground text-sm mb-4">Selecciona el tipo de cuenta que quieres añadir.</p>
            <div className="grid gap-2">
              {ACCOUNT_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => handleSelectType(type.value)}
                  className="flex items-center gap-4 px-4 py-3.5 rounded-xl border border-border bg-white/[0.02] hover:bg-accent/8 hover:border-accent/20 transition-all text-left"
                >
                  <span className="text-2xl">{type.icon}</span>
                  <div>
                    <div className="font-medium text-foreground">{type.label}</div>
                    <div className="text-sm text-muted-foreground">{type.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Details form */}
        {step === 'details' && (
          <form onSubmit={handleSubmit} className="p-6">
            <div className="grid gap-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Nombre de la cuenta *</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={selectedType === 'checking' ? 'Ej: BBVA Nomina' : selectedType === 'credit_card' ? 'Ej: Visa BBVA' : 'Ej: Mi cuenta'}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                  autoFocus
                />
              </div>

              {/* Institution */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-1.5">Entidad / Banco</label>
                <input
                  type="text"
                  value={institutionName}
                  onChange={(e) => setInstitutionName(e.target.value)}
                  placeholder="Ej: BBVA, ING, Revolut..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                />
                <p className="text-xs text-muted-foreground mt-1">Opcional. Si no lo indicas se marcara como manual.</p>
              </div>

              {/* Currency + Initial balance row */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Divisa</label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground focus:outline-none focus:border-accent/40 transition-colors"
                  >
                    {CURRENCIES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">Saldo inicial</label>
                  <input
                    type="number"
                    step="0.01"
                    value={initialBalance}
                    onChange={(e) => setInitialBalance(e.target.value)}
                    placeholder="0.00"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                  />
                </div>
              </div>

              {/* IBAN - only for checking/savings */}
              {(selectedType === 'checking' || selectedType === 'savings') && (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1.5">IBAN</label>
                  <input
                    type="text"
                    value={iban}
                    onChange={(e) => setIban(e.target.value)}
                    placeholder="ES00 0000 0000 0000 0000 0000"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-border bg-white/[0.03] text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-accent/40 transition-colors"
                  />
                  <p className="text-xs text-muted-foreground mt-1">Opcional. Solo para tu referencia.</p>
                </div>
              )}

              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2.5 rounded-xl border border-border text-muted-foreground hover:text-foreground transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={submitting}
                className={cn(
                  'px-5 py-2.5 rounded-xl font-medium transition-colors',
                  'bg-accent text-white hover:bg-accent/90',
                  submitting && 'opacity-50 cursor-not-allowed'
                )}
              >
                {submitting ? 'Creando...' : 'Crear cuenta'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
