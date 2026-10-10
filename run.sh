#!/usr/bin/env bash
set -e

COMMAND=$1

case "$COMMAND" in
  seed)
    echo "Seeding database and documents..."
    python backend/scripts/generate_synthetic_data.py
    python backend/scripts/validate_synthetic_data.py
    python backend/scripts/load_students.py
    python backend/scripts/seed_documents.py
    ;;
  test)
    echo "Running pytest test suite..."
    python -m pytest backend/tests/ -v
    ;;
  eval)
    echo "Running evaluation harness..."
    python backend/evaluation/run_evaluation.py
    ;;
  smoke)
    echo "Running smoke test..."
    python scripts/smoke_test.py --url http://localhost:8000
    ;;
  dev)
    echo "Starting backend and frontend..."
    (cd backend && uvicorn app.main:app --reload --port 8000) &
    (cd frontend && npm run dev) &
    wait
    ;;
  docker)
    docker compose up --build
    ;;
  *)
    echo "Usage: ./run.sh [seed|test|eval|smoke|dev|docker]"
    exit 1
    ;;
esac
