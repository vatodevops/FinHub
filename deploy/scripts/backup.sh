#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$ROOT_DIR/deploy/backups"
STAMP="$(date +%F-%H%M%S)"
mkdir -p "$BACKUP_DIR"

docker cp finhub-backend:/data/finhub.db "$BACKUP_DIR/finhub-${STAMP}.db"
cp "$ROOT_DIR/deploy/.env" "$BACKUP_DIR/env-${STAMP}.backup"

echo "Backup creado:"
echo "- $BACKUP_DIR/finhub-${STAMP}.db"
echo "- $BACKUP_DIR/env-${STAMP}.backup"
