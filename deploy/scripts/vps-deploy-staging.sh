#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: $0 <git-ref>" >&2
  exit 1
fi

REF="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

test -f deploy/.env.staging

git fetch --all --tags --prune
git checkout "$REF"

docker compose -f deploy/docker-compose.staging.yml --env-file deploy/.env.staging up -d --build

echo "Esperando health de staging..."
for _ in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8083/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

curl -fsS http://127.0.0.1:8083/api/health
echo
echo "Staging desplegado en ref: $REF"

