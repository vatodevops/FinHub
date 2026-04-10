#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: $0 <git-ref>" >&2
  exit 1
fi

REF="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

test -f deploy/.env

git fetch --all --tags --prune
git checkout "$REF"

./deploy/scripts/backup.sh
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env up -d --build

echo "Esperando health de producción..."
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8082/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

curl -fsS http://127.0.0.1:8082/api/health
echo
echo "Producción desplegada en ref: $REF"

