#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT/.local-run"
for svc in backend frontend; do
  if [[ -f "$LOG_DIR/$svc.pid" ]]; then
    PID="$(cat "$LOG_DIR/$svc.pid")"
    kill "$PID" 2>/dev/null || true
    rm -f "$LOG_DIR/$svc.pid"
  fi
done

echo "FinHub parado."
