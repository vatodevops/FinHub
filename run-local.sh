#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
LOG_DIR="$ROOT/.local-run"
mkdir -p "$LOG_DIR"

cd "$BACKEND"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -e .
cp -n .env.example .env >/dev/null 2>&1 || true
python -m app.db.init_local
nohup .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8081 > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$LOG_DIR/backend.pid"

deactivate || true

cd "$FRONTEND"
npm install --silent
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$LOG_DIR/frontend.pid"

cat <<EOF
FinHub arrancado.

Frontend: http://localhost:3001
Backend API: http://localhost:8081/api
Health: http://localhost:8081/api/health
Overview: http://localhost:8081/api/overview

Logs:
- $LOG_DIR/backend.log
- $LOG_DIR/frontend.log
EOF
