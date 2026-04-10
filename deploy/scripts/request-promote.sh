#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_FILE="$ROOT_DIR/deploy/.last-promote-request.txt"

cd "$ROOT_DIR"

COMMIT="$(git rev-parse --short HEAD)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
STATUS="clean"
if [[ -n "$(git status --short)" ]]; then
  STATUS="dirty"
fi

BACKEND_HEALTH="FAIL"
FRONTEND_STATUS="FAIL"
if curl -fsS http://127.0.0.1:18082/api/health >/dev/null 2>&1; then
  BACKEND_HEALTH="OK"
fi
if curl -fsS http://127.0.0.1:13010 >/dev/null 2>&1; then
  FRONTEND_STATUS="OK"
fi

cat > "$OUT_FILE" <<EOF
Promote FinHub listo.

- rama: $BRANCH
- commit: $COMMIT
- git status: $STATUS
- staging backend health: $BACKEND_HEALTH
- staging frontend: $FRONTEND_STATUS

Pásale este mensaje a Vato para producción:
"Haz promote de FinHub a producción con el commit $COMMIT. Staging backend=$BACKEND_HEALTH, frontend=$FRONTEND_STATUS, rama=$BRANCH, git_status=$STATUS."
EOF

cat "$OUT_FILE"

