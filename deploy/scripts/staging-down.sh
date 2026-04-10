#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.pgtest.yml"

cd "$ROOT_DIR"
docker compose -f "$COMPOSE_FILE" down
echo "Staging parado"

