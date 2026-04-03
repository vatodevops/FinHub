# FinHub local

## Arranque rápido

```bash
cd /root/.openclaw/workspace/projects/finhub
chmod +x run-local.sh stop-local.sh
./run-local.sh
```

Luego abre:
- <http://localhost:3001>

## URLs
- Frontend: <http://localhost:3001>
- Backend API: <http://localhost:8081/api>
- Health: <http://localhost:8081/api/health>
- Overview: <http://localhost:8081/api/overview>

## Parar

```bash
./stop-local.sh
```

## Reiniciar solo el frontend

Si ves errores raros de Next tipo `.next/... ENOENT`, reinícialo limpio:

```bash
./restart-frontend.sh
```

## Resetear la base SQLite local

Si metemos cambios de esquema y prefieres regenerar el entorno demo:

```bash
./reset-local-db.sh
```

## Notas
- En modo local usa SQLite (`backend/finhub.db`) para que no dependas de Docker ni PostgreSQL.
- Si luego lo pasamos a VM/producción, volvemos a PostgreSQL.
