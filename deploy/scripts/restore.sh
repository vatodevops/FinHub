#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Uso: $0 /ruta/al/backup.db [ruta/al/env.backup]" >&2
  exit 1
fi
DB_BACKUP="$1"
ENV_BACKUP="${2:-}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

test -f "$DB_BACKUP"
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env stop backend frontend

docker run --rm -v deploy_finhub_data:/data -v "$(dirname "$DB_BACKUP"):/backup:ro" alpine sh -lc "cp /backup/$(basename "$DB_BACKUP") /data/finhub.db"

if [ -n "$ENV_BACKUP" ]; then
  test -f "$ENV_BACKUP"
  cp "$ENV_BACKUP" "$ROOT_DIR/deploy/.env"
fi

docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d backend frontend
echo "Restore completado"
