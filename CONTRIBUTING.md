# Contributing to FinHub

Thanks for considering contributing! 🎉

## How to contribute

### 🐛 Report bugs

Open an [issue](https://github.com/vatodevops/FinHub/issues) with:

- Steps to reproduce
- Expected vs actual behaviour
- Screenshots if relevant
- Browser / environment details

### 💡 Suggest features

Open an [issue](https://github.com/vatodevops/FinHub/issues) with:

- What problem you're trying to solve
- How you envision it working
- Any relevant context (banks, cards, workflows)

### 🛠️ Submit a PR

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run backend tests: `cd backend && pytest`
5. Commit with a descriptive message
6. Push and open a PR against `main`

## Development guidelines

- **Backend**: add tests for new services / endpoints. Use SQLAlchemy sessions, not raw SQL.
- **Frontend**: use Tailwind utility classes. Keep API calls in `lib/api.ts`.
- **Migrations**: run `alembic revision -m "..."` for schema changes and test both SQLite (dev) and PostgreSQL (CI).
- **Curve dedup**: if you touch reconciliation logic, make sure the Curve anti-duplicate rule is still respected (see `docs/architecture.md` §4).

## Code style

- Python: `black` + `ruff` compatible (we don't enforce a linter in CI yet, but keep it clean)
- Frontend: Prettier defaults

## Running locally

See [README.md](README.md) for local development setup.

## Questions?

Open a [discussion](https://github.com/vatodevops/FinHub/discussions) or tag the maintainers in an issue.