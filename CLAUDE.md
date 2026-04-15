# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FinHub is a self-hosted personal finance hub consolidating European bank accounts, card spend (with Curve deduplication), manual planned expenses, budgets, and (fase 2) investments. Stack: FastAPI + SQLAlchemy + Alembic backend, Next.js 15 / React 19 frontend, PostgreSQL in production and SQLite locally.

## Common commands

### Local dev (both services)
- Start everything: `./run-local.sh` — creates backend venv, installs deps, runs `app.db.init_local` to seed SQLite, starts uvicorn on `:8081` and `next dev` on `:3001`. PIDs/logs in `.local-run/`.
- Stop: `./stop-local.sh`
- Restart only frontend (fixes `.next/... ENOENT` issues): `./restart-frontend.sh`
- Reset SQLite demo DB: `./reset-local-db.sh`

### Backend (from `backend/`)
- Install: `pip install -e .[test]`
- Run dev: `uvicorn app.main:app --reload --port 8081`
- Migrations: `alembic upgrade head` (new revision: `alembic revision -m "..."`)
- Seed local SQLite + migrate: `python -m app.db.init_local`
- Tests: `pytest` | single file: `pytest tests/test_transactions.py` | single test: `pytest tests/test_transactions.py::test_name -v`

### Frontend (from `frontend/`)
- Dev: `npm run dev` (port 3001)
- Build / start: `npm run build` && `npm run start`
- No lint/test scripts are defined.

### Production (VPS)
- Compose file: `deploy/docker-compose.prod.yml` — backend on `127.0.0.1:8082`, frontend on `127.0.0.1:3010`, `finhub-postgres` service. Public TLS termination via Traefik/Pangolin (`/opt/pangolin/config/traefik/dynamic_config.yml` on host).
- Backup / restore: `deploy/scripts/backup.sh`, `deploy/scripts/restore.sh <dump> [env.backup]`. Dumps land in `deploy/backups/`.

## Architecture

### Runtime-selected database
`backend/app/core/config.py` exposes a single `database_url` (default `sqlite:///./finhub.db`). Local dev uses SQLite; prod uses Postgres via env var. Alembic migrations must stay compatible with both dialects — see existing revisions in `backend/alembic/versions/` for patterns (they're numbered `YYYYMMDD_NNNN_*.py`).

### Backend layout (`backend/app/`)
- `main.py` — FastAPI app, CORS, `RequestLoggingMiddleware`, `AppError` → JSON exception handler. All routes mounted under `/api`.
- `api/routers/` — one module per domain (accounts, transactions, overview, recurring, manual, budgets, connectors, institutions, reports, auth, health). Aggregated in `api/routers/__init__.py`.
- `api/deps/` — FastAPI dependencies (DB session, current user).
- `core/` — `config` (pydantic-settings), `exceptions` (`AppError` hierarchy), `logging`.
- `models/` — SQLAlchemy ORM. `entities.py` holds the core domain (institutions, accounts, transactions, etc.); feature-specific files for `auth`, `bank_connection`, `budget`, `categories`, `manual`, `recurring`.
- `schemas/` — Pydantic request/response models, separated from ORM models.
- `services/` — business logic kept out of routers:
  - `overview.py`, `reconciliation.py`, `duplicates.py`, `recurring_detection.py`
  - `sync/bank_sync.py` — persistence of bank-connection sync runs
  - `connectors/banks/` — external provider clients (GoCardless / Nordigen Bank Account Data)
- `db/` — engine/session, seed + `init_local` entrypoint.

### Curve anti-duplicate rule (core domain concept)
A bank transaction whose descriptor matches `CRV-` / `CURVE` and mirrors a Curve transaction (same amount, currency, close in time) is treated as settlement/shadow — Curve is canonical, bank entry does not add to spend. Transfers, direct debits, cash withdrawals, and non-Curve card charges are NOT deduplicated. Ambiguous matches (same-amount repeats, partial refunds, FX, Curve go-back-in-time) go to a review queue. See `docs/architecture.md` §4 and `services/duplicates.py` / `services/reconciliation.py`.

### Canonical transaction model
Every normalized transaction carries: `source_type` (`bank|curve|broker`), external `source_id`, `account_id`, `amount`, `currency`, `booked_at`, `value_at`, `merchant_raw`/`merchant_clean`, `description_raw`, `channel` (`card|transfer|direct_debit|cash|fee`), `status`, and a dedup `fingerprint`.

### Auth
Session-cookie auth (`auth_session_cookie=finhub_session`, 30-day) with local users plus Google OAuth (`/api/auth/google/callback`, redirect fixed to `https://finhub.vatotech.es/api/auth/google/callback` in prod). OAuth state is validated via the `finhub_oauth_state` cookie.

### Frontend (`frontend/`)
Next.js 15 App Router, React 19, Tailwind 4, Radix UI, Recharts. Routes under `app/`: `login`, `accounts`, `transactions`, `budgets`, `calendar`, `connections`, `connectors`, `investments`, `manual`, `reports`, `scheduled`. Shared helpers in `lib/api.ts` (API client, expects `http://localhost:8081/api` by default) and `lib/auth.tsx` (session context).

## Docs worth reading before non-trivial work
- `docs/architecture.md` — data sources, component responsibilities, Curve rule, MVP roadmap.
- `docs/recurring-payments.md`, `docs/manual-planned-expenses.md` — feature specs.
- `docs/open_questions.md` — undecided design points.
- `deploy/README_PROD.md` — production layout and proxy wiring.
