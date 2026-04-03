const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8081/api';

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: 'no-store', ...init });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json();
}

export type Overview = {
  today: string;
  account_count: number;
  institution_count: number;
  transaction_count: number;
  booked_income_month: string;
  booked_expense_month: string;
  net_month: string;
  planned_expense_upcoming: string;
  recurring_due_upcoming: string;
};

export type Account = { id: string; institution_id: string; name: string; iban_masked?: string | null; currency: string; kind: string; is_active: boolean; };
export type Transaction = { id: string; account_id: string; category_id?: string | null; category_name?: string | null; source_type: string; source_id: string; amount: string; currency: string; booked_at?: string | null; merchant_clean?: string | null; merchant_raw?: string | null; description_raw?: string | null; channel: string; status: string; };
export type RecurringSeries = { id: string; name: string; merchant_clean?: string | null; recurrence_type: string; interval_days?: number | null; typical_day_of_month?: number | null; amount_mean?: string | null; next_expected_date?: string | null; confidence?: string | null; state: string; };
export type RecurringOccurrence = { id: string; series_id: string; expected_date: string; expected_amount?: string | null; status: string; matched_transaction_id?: string | null; };
export type ManualPlannedItem = { id: string; name: string; amount: string; currency: string; expected_date?: string | null; recurrence_rule?: string | null; status: string; notes?: string | null; kind: string; merchant_hint?: string | null; };
export type BankConnection = { id: string; provider: string; requisition_id: string; reference: string; institution_external_id?: string | null; institution_name?: string | null; link?: string | null; status: string; last_synced_at?: string | null; error_message?: string | null; };
export type Category = { id: string; name: string; slug: string; color?: string | null; };
export type CurveDuplicateCandidate = { confidence: number; reason: string; curve_transaction: Transaction; bank_transaction: Transaction; };

export const api = {
  overview: () => fetchJson<Overview>('/overview'),
  accounts: () => fetchJson<Account[]>('/accounts'),
  transactions: () => fetchJson<Transaction[]>('/transactions?limit=200'),
  recurringSeries: () => fetchJson<RecurringSeries[]>('/recurring/series'),
  recurringCalendar: () => fetchJson<RecurringOccurrence[]>('/recurring/calendar?limit=20'),
  manualPlannedItems: () => fetchJson<ManualPlannedItem[]>('/manual/planned-items'),
  bankConnections: () => fetchJson<BankConnection[]>('/bank-connections'),
  categories: () => fetchJson<Category[]>('/categories'),
  curveDuplicates: () => fetchJson<CurveDuplicateCandidate[]>('/transactions/curve-duplicates'),
  gocardlessInstitutions: () => fetchJson<any>('/connectors/gocardless/institutions'),
  createManualPlannedItem: (payload: Record<string, unknown>) => fetchJson<ManualPlannedItem>('/manual/planned-items', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  updateTransactionCategory: (transactionId: string, categoryId: string | null) => fetchJson<Transaction>(`/transactions/${transactionId}/category`, {
    method: 'PATCH',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ category_id: categoryId }),
  }),
  refreshBankConnection: (connectionId: string) => fetchJson<BankConnection>(`/bank-connections/${connectionId}/refresh`, { method: 'POST' }),
};
