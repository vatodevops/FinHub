#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$ROOT_DIR/deploy/backups"
STAMP="$(date +%F-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if docker ps -q --filter name=finhub-postgres | grep -q .; then
  . "$ROOT_DIR/deploy/.env"
  export PGPASSWORD="$POSTGRES_PASSWORD"
  docker exec finhub-postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$BACKUP_DIR/finhub-${STAMP}.dump"
  cp "$ROOT_DIR/deploy/.env" "$BACKUP_DIR/env-${STAMP}.backup"
  echo "Backup creado:"
  echo "- $BACKUP_DIR/finhub-${STAMP}.dump"
  echo "- $BACKUP_DIR/env-${STAMP}.backup"
else
  echo "No hay contenedor finhub-postgres, saltando backup"
fi
