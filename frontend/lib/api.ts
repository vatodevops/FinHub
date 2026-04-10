const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data?.detail || data?.error || `API error ${res.status}`;
  } catch {
    return `API error ${res.status}`;
  }
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: 'no-store',
    credentials: 'include',
    ...init,
  });
  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }
  return res.json();
}

async function fetchVoid(path: string, init?: RequestInit): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: 'no-store',
    credentials: 'include',
    ...init,
  });
  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }
}

export type User = { id: string; email: string; full_name?: string | null; is_active: boolean; };
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
export type Account = { id: string; institution_id: string; name: string; iban_masked?: string | null; currency: string; kind: string; is_active: boolean; institution_name?: string | null; balance?: string | null; };
export type Transaction = { id: string; account_id: string; category_id?: string | null; category_name?: string | null; source_type: string; source_id: string; amount: string; currency: string; booked_at?: string | null; merchant_clean?: string | null; merchant_raw?: string | null; description_raw?: string | null; channel: string; status: string; };
export type RecurringSeries = { id: string; name: string; merchant_clean?: string | null; recurrence_type: string; interval_days?: number | null; typical_day_of_month?: number | null; amount_mean?: string | null; next_expected_date?: string | null; confidence?: string | null; state: string; };
export type RecurringOccurrence = { id: string; series_id: string; expected_date: string; expected_amount?: string | null; status: string; matched_transaction_id?: string | null; };
export type ManualPlannedItem = { id: string; name: string; amount: string; currency: string; expected_date?: string | null; recurrence_rule?: string | null; status: string; notes?: string | null; kind: string; merchant_hint?: string | null; };
export type BankConnection = { id: string; provider: string; requisition_id: string; reference: string; institution_external_id?: string | null; institution_name?: string | null; link?: string | null; status: string; last_synced_at?: string | null; error_message?: string | null; };
export type Category = { id: string; name: string; slug: string; color?: string | null; icon?: string | null; parent_id?: string | null; };
export type CurveDuplicateCandidate = { confidence: number; reason: string; curve_transaction: Transaction; bank_transaction: Transaction; };
export type Budget = { id: string; category_id: string; category_name?: string | null; category_color?: string | null; amount_limit: string; spent: string; period: string; month: number; year: number; };
export type MonthlySummary = { month: string; income: string; expense: string; net: string; };
export type CategoryBreakdown = { category_id: string | null; category_name: string; category_color: string | null; total: string; percentage: number; };
export type NetWorthPoint = { month: string; total: string; };

export const api = {
  register: (payload: Record<string, unknown>) => fetchJson<User>('/auth/register', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  login: (payload: Record<string, unknown>) => fetchJson<User>('/auth/login', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  }),
  logout: () => fetchVoid('/auth/logout', { method: 'POST' }),
  me: () => fetchJson<User>('/auth/me'),

  overview: () => fetchJson<Overview>('/overview'),
  accounts: () => fetchJson<Account[]>('/accounts'),
  createAccount: (payload: Record<string, unknown>) => fetchJson<Account>('/accounts', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  updateAccount: (id: string, payload: Record<string, unknown>) => fetchJson<Account>(`/accounts/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  deleteAccount: (id: string) => fetchVoid(`/accounts/${id}`, { method: 'DELETE' }),
  transactions: (params?: Record<string, string>) => {
    const query = new URLSearchParams({ limit: '200', ...params }).toString();
    return fetchJson<Transaction[]>(`/transactions?${query}`);
  },
  createTransaction: (payload: Record<string, unknown>) => fetchJson<Transaction>('/transactions', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  updateTransaction: (id: string, payload: Record<string, unknown>) => fetchJson<Transaction>(`/transactions/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  deleteTransaction: (id: string) => fetchVoid(`/transactions/${id}`, { method: 'DELETE' }),
  updateTransactionCategory: (transactionId: string, categoryId: string | null) => fetchJson<Transaction>(`/transactions/${transactionId}/category`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ category_id: categoryId }) }),
  createTransfer: (payload: Record<string, unknown>) => fetchJson<Transaction[]>('/transactions/transfer', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  curveDuplicates: () => fetchJson<CurveDuplicateCandidate[]>('/transactions/curve-duplicates'),
  categories: () => fetchJson<Category[]>('/categories'),
  createCategory: (payload: Record<string, unknown>) => fetchJson<Category>('/categories', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  updateCategory: (id: string, payload: Record<string, unknown>) => fetchJson<Category>(`/categories/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  deleteCategory: (id: string) => fetchVoid(`/categories/${id}`, { method: 'DELETE' }),
  recurringSeries: () => fetchJson<RecurringSeries[]>('/recurring/series'),
  createRecurringSeries: (payload: Record<string, unknown>) => fetchJson<RecurringSeries>('/recurring/series', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  updateRecurringSeries: (id: string, payload: Record<string, unknown>) => fetchJson<RecurringSeries>(`/recurring/series/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  deleteRecurringSeries: (id: string) => fetchVoid(`/recurring/series/${id}`, { method: 'DELETE' }),
  recurringCalendar: () => fetchJson<RecurringOccurrence[]>('/recurring/calendar?limit=20'),
  manualPlannedItems: () => fetchJson<ManualPlannedItem[]>('/manual/planned-items'),
  createManualPlannedItem: (payload: Record<string, unknown>) => fetchJson<ManualPlannedItem>('/manual/planned-items', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  deleteManualPlannedItem: (id: string) => fetchVoid(`/manual/planned-items/${id}`, { method: 'DELETE' }),
  budgets: (month?: number, year?: number) => {
    const params = new URLSearchParams();
    if (month) params.set('month', String(month));
    if (year) params.set('year', String(year));
    return fetchJson<Budget[]>(`/budgets?${params.toString()}`);
  },
  createBudget: (payload: Record<string, unknown>) => fetchJson<Budget>('/budgets', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  updateBudget: (id: string, payload: Record<string, unknown>) => fetchJson<Budget>(`/budgets/${id}`, { method: 'PATCH', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) }),
  deleteBudget: (id: string) => fetchVoid(`/budgets/${id}`, { method: 'DELETE' }),
  monthlySummary: (months?: number) => fetchJson<MonthlySummary[]>(`/reports/monthly-summary?months=${months || 6}`),
  categoryBreakdown: (month?: string) => {
    const q = month ? `?month=${month}` : '';
    return fetchJson<CategoryBreakdown[]>(`/reports/by-category${q}`);
  },
  netWorth: (months?: number) => fetchJson<NetWorthPoint[]>(`/reports/net-worth?months=${months || 12}`),
  bankConnections: () => fetchJson<BankConnection[]>('/bank-connections'),
  refreshBankConnection: (connectionId: string) => fetchJson<BankConnection>(`/bank-connections/${connectionId}/refresh`, { method: 'POST' }),
  gocardlessInstitutions: () => fetchJson<any>('/connectors/gocardless/institutions'),
};
