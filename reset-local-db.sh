#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"

rm -f "$BACKEND/finhub.db"
cd "$BACKEND"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q -e .
else
  source .venv/bin/activate
fi
python -m app.db.init_local

echo "SQLite local reinicializada en $BACKEND/finhub.db"
