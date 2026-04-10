#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="http://127.0.0.1:18082/api/health"
FRONTEND_URL="http://127.0.0.1:13010"

echo "== Backend health =="
curl -fsS "$BACKEND_URL"
echo
echo
echo "== Frontend =="
curl -fsS "$FRONTEND_URL" | grep -o '<title>.*</title>' || echo "Frontend responde OK"
echo

