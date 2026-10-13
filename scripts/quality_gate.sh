#!/usr/bin/env bash
# Quality gate sơ bộ (CI-style) — M1 Foundation.
# Exit 0 khi: backend pytest pass + frontend build pass + grep guards BR-10/BR-06.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/4] Backend tests (LLM_PROVIDER=mock, không gọi LLM thật)..."
(cd backend && pytest -q)

echo "[2/4] Frontend type-check + build..."
(cd frontend && npm run build)

echo "[3/4] BR-10: frontend/src không chứa URL tuyệt đối (localhost/127.0.0.1)..."
if grep -rnE "https?://(localhost|127\.0\.0\.1)" frontend/src 2>/dev/null; then
  echo "FAIL: frontend/src chứa URL tuyệt đối — phải dùng base root-relative /api (BR-10)"
  exit 1
fi
echo "OK"

echo "[4/4] BR-06: không có pattern khóa API trong repo..."
if grep -rnE "(sk-[A-Za-z0-9]{16,}|AIza[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})" \
    --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    --include="*.json" --include="*.yaml" --include="*.yml" --include="*.toml" \
    --include="*.md" --include="*.txt" . 2>/dev/null \
    | grep -v node_modules | grep -v package-lock.json; then
  echo "FAIL: phát hiện pattern khóa API trong repo (BR-06)"
  exit 1
fi
echo "OK"

echo "==> Quality gate PASSED"