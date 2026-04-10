#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Uso: $0 /ruta/al/backup.dump [ruta/al/env.backup]" >&2
  exit 1
fi
DUMP_BACKUP="$1"
ENV_BACKUP="${2:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

test -f "$DUMP_BACKUP"
if [ -n "$ENV_BACKUP" ]; then
  test -f "$ENV_BACKUP"
  cp "$ENV_BACKUP" "$ROOT_DIR/deploy/.env"
fi

. "$ROOT_DIR/deploy/.env"
export PGPASSWORD="$POSTGRES_PASSWORD"

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d postgres
until docker exec finhub-postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do sleep 2; done

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env stop backend frontend || true
docker exec finhub-postgres psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$POSTGRES_DB\";"
docker exec finhub-postgres psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE \"$POSTGRES_DB\";"
cat "$DUMP_BACKUP" | docker exec -i finhub-postgres pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d backend frontend
echo "Restore completado"
