#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND="$ROOT/frontend"
LOG_DIR="$ROOT/.local-run"
mkdir -p "$LOG_DIR"

if [[ -f "$LOG_DIR/frontend.pid" ]]; then
  kill -9 "$(cat "$LOG_DIR/frontend.pid")" 2>/dev/null || true
  rm -f "$LOG_DIR/frontend.pid"
fi

# Mata cualquier proceso escuchando en 3001, aunque el pid file esté desfasado
for pid in $(ss -ltnp '( sport = :3001 )' 2>/dev/null | sed -n 's/.*pid=\([0-9]\+\).*/\1/p' | sort -u); do
  kill -9 "$pid" 2>/dev/null || true
done
fuser -k 3001/tcp 2>/dev/null || true

# Espera a que el puerto quede libre de verdad
for _ in $(seq 1 20); do
  if ! ss -ltn '( sport = :3001 )' | grep -q 3001; then
    break
  fi
  sleep 0.3
done

rm -rf "$FRONTEND/.next"
cd "$FRONTEND"
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$LOG_DIR/frontend.pid"

echo "Frontend reiniciado en http://localhost:3001"
