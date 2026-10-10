.PHONY: help dev dev-backend dev-frontend test eval seed build clean smoke

help:
	@echo "Available commands:"
	@echo "  make seed        - Generate synthetic data, validate, and seed documents"
	@echo "  make test        - Run backend pytest test suite"
	@echo "  make eval        - Run 22-question evaluation harness and generate report"
	@echo "  make dev-backend - Run FastAPI backend with uvicorn"
	@echo "  make dev-frontend- Run React Vite dev server"
	@echo "  make smoke       - Run end-to-end smoke test"
	@echo "  make docker-up   - Run backend and frontend via docker-compose"

seed:
	python backend/scripts/generate_synthetic_data.py
	python backend/scripts/validate_synthetic_data.py
	python backend/scripts/load_students.py
	python backend/scripts/seed_documents.py

test:
	python -m pytest backend/tests/ -v

eval:
	python backend/evaluation/run_evaluation.py

smoke:
	python scripts/smoke_test.py --url http://localhost:8000

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build
