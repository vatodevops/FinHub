#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./deploy/scripts/backup.sh
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d --build

echo "Esperando health de producción local..."
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8082/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo
echo "Producción actualizada:"
echo "- API: http://127.0.0.1:8082/api/health"
echo "- Frontend: http://127.0.0.1:3010"
echo "- Pública: https://finhub.vatotech.es"

