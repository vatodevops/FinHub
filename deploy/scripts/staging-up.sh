#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.pgtest.yml"
BACKEND_URL="http://127.0.0.1:18082/api/health"
FRONTEND_URL="http://127.0.0.1:13010"

cd "$ROOT_DIR"

docker compose -f "$COMPOSE_FILE" up -d --build

echo "Esperando a que staging responda..."
for _ in $(seq 1 30); do
  if curl -fsS "$BACKEND_URL" >/dev/null 2>&1 && curl -fsS "$FRONTEND_URL" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo
echo "Staging levantado:"
echo "- Frontend: $FRONTEND_URL"
echo "- Backend health: $BACKEND_URL"
echo
echo "Siguiente paso: ./deploy/scripts/staging-check.sh"

