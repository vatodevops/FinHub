# Backend

FastAPI backend para:
- conectores bancarios
- normalización de transacciones
- deduplicación Curve
- agregados mensuales
- holdings / patrimonio (fase 2)

## Arranque local

```bash
cd projects/finhub/infra
docker compose up -d

cd ../backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload --port 8081
```

## Endpoints iniciales

- `GET /`
- `GET /api/health`
- `GET /api/overview`
- `GET /api/institutions`
- `GET /api/accounts`
- `GET /api/transactions`
- `GET /api/recurring/series`
- `GET /api/recurring/calendar`
- `GET /api/recurring/suggestions`
- `GET /api/manual/planned-items`
- `POST /api/manual/planned-items`
- `GET /api/connectors/gocardless/institutions`
- `POST /api/connectors/gocardless/requisition`
- `GET /api/bank-connections`
- `POST /api/bank-connections/{connection_id}/sync`

## GoCardless / Open Banking

El backend ya trae cliente HTTP base para GoCardless Bank Account Data.

Falta aún cerrar:
- persistencia de requisitions/connections
- sync automático a base de datos
- renovación de consentimientos

Pero ya están preparados:
- listado de instituciones
- creación de requisition de conexión
