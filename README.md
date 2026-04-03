# FinHub

Hub financiero personal self-hosted para consolidar bancos, inversiones y gasto con deduplicación de Curve.

## Objetivo del MVP

- Conectar bancos europeos vía Open Banking
- Sincronizar balances y transacciones automáticamente
- Tratar Curve como fuente principal de compras con tarjeta
- Evitar duplicados cuando el banco registre cargos `CRV-XXXX`
- Mostrar balance consolidado, ingresos, gastos y evolución mensual
- Dejar el bloque de inversiones preparado para una segunda fase

## Stack propuesto

- Backend: FastAPI
- DB: PostgreSQL
- Frontend: Next.js
- Workers/sync: Python async jobs / cron
- Infra local: Docker Compose

## Fases

### Fase 1
- Bancos
- Curve anti-duplicado
- Dashboard mensual
- Categorías básicas
- Balance consolidado

### Fase 2
- Inversiones
- Patrimonio neto
- Series históricas
- Reglas/alertas

## Estructura

- `docs/` diseño y decisiones
- `backend/` API y sync jobs
- `frontend/` panel web
- `infra/` compose y variables de entorno
