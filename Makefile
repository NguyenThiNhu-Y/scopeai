# Makefile — Presales Bidding Assistant (M1)
#
# Lệnh chính:
#   make test          # MỘT lệnh chạy toàn bộ test (backend pytest + frontend vitest + build)
#   make quality-gate  # Chạy scripts/quality_gate.sh (test + build + grep guards BR-06/BR-10)
#   make run           # Chạy app ở chế độ dev (backend :8000 + frontend :5173, Ctrl+C để dừng)
#   make preview       # Chạy Preview qua podman-compose (theo skill app-preview)

.PHONY: test test-backend test-frontend quality-gate run preview eval

test: test-backend test-frontend
	cd frontend && npm run build

test-backend:
	cd backend && pytest -q

test-frontend:
	cd frontend && npm run test

# Eval harness (thiet_ke_danh_gia.md §6) — dùng LLM_PROVIDER hiện tại, mặc định mock.
eval:
	cd backend && python -m eval.run_eval

quality-gate:
	bash scripts/quality_gate.sh

run:
	@set -e; \
	echo "==> Backend: uvicorn trên :8000"; \
	(cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000) & \
	BACKEND_PID=$$!; \
	trap 'kill $$BACKEND_PID 2>/dev/null || true' EXIT INT TERM; \
	echo "==> Frontend: Vite dev trên :5173 (proxy /api -> :8000)"; \
	cd frontend && npm run dev

preview:
	podman-compose -f podman-compose.preview.vibeflow.yaml up --build -d