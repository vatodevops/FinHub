# Arquitectura inicial — FinHub

## 1. Fuentes de datos

### Bancos
Fuente preferida:
- GoCardless Bank Account Data (PSD2 / Nordigen)

Alternativas a evaluar después:
- Salt Edge
- Powens / Budget Insight
- Tink

### Inversiones
Estrategia por conector:
- API oficial si existe
- CSV/statement automatizable si no existe API
- scraping solo como último recurso

Plataformas prioritarias a investigar:
- MyInvestor
- Indexa Capital
- Trade Republic
- Degiro
- Interactive Brokers
- Scalable Capital
- XTB
- Binance / Coinbase (si entra cripto)

## 2. Componentes

### Backend (FastAPI)
Responsabilidades:
- auth local básica
- API REST
- conectores externos
- motor de normalización
- deduplicación Curve
- agregados mensuales

### DB (PostgreSQL)
Tablas principales:
- institutions
- accounts
- cards
- transactions
- transaction_links
- holdings
- positions
- sync_runs
- categories
- merchants

### Frontend
Vistas MVP:
- overview
- cuentas
- transacciones
- gasto mensual
- ingresos vs gastos
- auditoría de duplicados

### Worker de sync
Tareas:
- refresh de balances
- fetch de transacciones
- recalcular agregados
- reconciliación / deduplicación

## 3. Modelo de transacción canónica

Cada transacción normalizada tendrá:
- source_type (`bank`, `curve`, `broker`)
- source_id externo
- account_id
- amount
- currency
- booked_at
- value_at
- merchant_raw
- merchant_clean
- description_raw
- channel (`card`, `transfer`, `direct_debit`, `cash`, `fee`)
- status
- fingerprint

## 4. Regla Curve anti-duplicado

### Objetivo
Contar una compra con tarjeta una sola vez.

### Regla base
Si existe una transacción `curve` y una transacción bancaria con:
- mismo importe
- misma moneda o moneda equivalente ya convertida
- fecha/hora cercana
- descriptor bancario que contenga `CRV-`, `CURVE`, o patrón equivalente

Entonces:
- `curve` = transacción canónica de compra
- movimiento del banco = transacción de liquidación / shadow
- no suma doble en el gasto

### Casos que NO deben deduplicarse
- transferencias
- domiciliaciones
- retiradas de efectivo
- compras directas con la tarjeta del banco sin pasar por Curve

### Casos ambiguos
Se mandan a una cola de revisión interna en UI:
- mismo importe repetido varias veces el mismo día
- devoluciones parciales
- cambio de divisa
- go-back-in-time de Curve

## 5. Categorías del MVP

- vivienda
- supermercado
- restaurantes
- transporte
- viajes
- salud
- deporte
- suscripciones
- compras
- efectivo/comisiones
- ingresos
- transferencias internas
- inversión

## 6. Roadmap técnico

### MVP-0
- repo
- compose
- postgres
- fastapi
- next.js
- esquema inicial

### MVP-1
- conexión a 1 agregador bancario
- ingestión de cuentas y transacciones
- dashboard básico

### MVP-2
- lógica Curve
- métricas mensuales
- revisión manual de duplicados

### MVP-3
- inversión / holdings
- patrimonio neto

## 7. Hosting recomendado (final)

Para producción personal:
- Debian 12
- 2 vCPU
- 4 GB RAM
- 40 GB SSD

Con margen cómodo:
- 4 vCPU
- 8 GB RAM
- 80 GB SSD
