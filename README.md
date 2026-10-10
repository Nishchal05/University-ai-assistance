# HCLTech AI-Powered University Student Services Assistant

[![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg)]()
[![Evaluation Correctness](https://img.shields.io/badge/eval%20correctness-100%25-brightgreen.svg)]()
[![Retrieval Hit Rate](https://img.shields.io/badge/retrieval%20hit%20rate-100%25-brightgreen.svg)]()
[![Abstention Accuracy](https://img.shields.io/badge/abstention%20accuracy-100%25-brightgreen.svg)]()

An enterprise-grade, authoritative, grounded, and explainable AI Student Services Assistant designed strictly for the HCLTech Future Ready AI Engineer Hackathon.

Built using **ONE unified LangGraph state machine**, deterministic Python tools over SQLite, persistent ChromaDB hybrid retrieval, and Annex A Source Precedence Policy resolution.

---

## 1. System Architecture

```
 ┌────────────────────────────────────────────────────────┐
 │            Frontend (React + Vite + Tailwind)          │
 │  - Chat UI with Grounded Citations & Audit Traces      │
 │  - Admin Console (Live Ingestion, Source Register)     │
 └───────────────────────────┬────────────────────────────┘
                             │ HTTP REST (Dev Proxy /api -> 8000)
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │           Backend API Layer (Python / FastAPI)         │
 │  - POST /ask       (X-Student-Id header authentication)│
 │  - POST /ingest    (Live document ingestion)           │
 │  - GET  /health    (Readiness probe)                   │
 │  - GET  /sources   (Source Register)                   │
 │  - GET  /audit     (Observability trace log)           │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │               LangGraph State Machine (ONE Graph)      │
 │                                                        │
 │   1. classify_query  (Pydantic structured intent)      │
 │          │                                             │
 │          ▼                                             │
 │   2. check_authentication  (Enforce X-Student-Id)      │
 │          │                                             │
 │          ▼                                             │
 │   3. retrieve_policy  (ChromaDB + BM25 Hybrid)         │
 │          │                                             │
 │          ▼                                             │
 │   4. validate_policy  (Annex A Precedence Engine)      │
 │          │                                             │
 │          ▼                                             │
 │   5. execute_student_tools  (Deterministic Python)     │
 │          │                                             │
 │          ▼                                             │
 │   6. generate_answer  (Grounded Synthesis)            │
 │          │                                             │
 │          ▼                                             │
 │   7. validate_response (Privacy / Leakage Guard)       │
 │          │                                             │
 │          ▼                                             │
 │   8. save_audit  (SQLite audit trace)                  │
 └─────────────┬──────────────────────────┬───────────────┘
               │                          │
               ▼                          ▼
 ┌──────────────────────────┐  ┌──────────────────────────┐
 │     ChromaDB (Vector)    │  │    SQLite 3 (Structured) │
 │  - sentence-transformers │  │  - students              │
 │  - Section-aware chunks  │  │  - courses               │
 │  - Source metadata       │  │  - attendance (Held/Att) │
 │  - Persistent to disk    │  │  - results               │
 └──────────────────────────┘  │  - rule_registry         │
                               │  - source_register       │
                               │  - audit_logs            │
                               └──────────────────────────┘
```

---

## 2. Repository Layout

```text
University-AI-Assistance/
├── backend/                 # Python / FastAPI backend (independent)
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint & CORS
│   │   ├── api/             # Routers: ask, ingest, health, sources, audit, admin, student
│   │   ├── graph/           # Single LangGraph workflow
│   │   ├── rag/             # PDF/DOCX extraction, chunking, ChromaDB, BM25 hybrid
│   │   ├── tools/           # Deterministic student tools & ownership checks
│   │   ├── services/        # Annex A policy precedence & LLM service
│   │   ├── database/        # SQLite schema & loaders
│   │   └── models/          # Pydantic v2 schemas
│   ├── scripts/             # generate_synthetic_data, validate_synthetic_data, load_students
│   ├── data/                # documents/, synthetic/, chroma/, university.db
│   ├── evaluation/          # run_evaluation.py (22 test questions)
│   ├── tests/               # test_backend.py, test_precedence.py (18 unit tests)
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── Dockerfile
├── frontend/                # React + Vite + Tailwind frontend (independent)
│   ├── src/
│   │   ├── lib/api.js       # THE ONLY place that calls backend API
│   │   ├── pages/           # ChatPage, AdminPage
│   │   ├── components/      # Navbar, AuditModal
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js       # Dev proxy /api -> http://localhost:8000
│   ├── .env.example
│   ├── README.md
│   └── Dockerfile
├── docs/                    # Authoritative contracts and documentation
│   ├── problem_statement.pdf # Official Hackathon Problem Statement
│   ├── API_CONTRACT.md      # Exact API schemas, DB tables, Annex A rules
│   ├── ARCHITECTURE.md      # Detailed system architecture
│   ├── EVALUATION_REPORT.md # 22-question evaluation report
│   ├── DATA_CARD.md         # Annex E synthetic data card
│   ├── LIMITATIONS.md       # Limitations & edge cases
│   ├── AI_USAGE_DISCLOSURE.md # AI usage statement
│   └── TEAM_CONTRIBUTIONS.md  # Team contributions & declaration
├── docker-compose.yml       # One-command full stack launcher
├── Makefile                 # CLI automation (dev, test, eval, seed, smoke)
├── run.sh                   # Unix shell helper script
└── README.md
```

---

## 3. Quick Start & Execution

### Option A: One-Command Start with Docker Compose
```bash
docker compose up --build
```
- Frontend UI: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`

### Option B: Local Running (Non-Docker)

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# Seed database and index university documents:
python scripts/generate_synthetic_data.py
python scripts/validate_synthetic_data.py
python scripts/load_students.py
python scripts/seed_documents.py

# Run FastAPI backend:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser. Vite proxies all `/api` calls directly to `http://localhost:8000`.

---

## 4. Automated Testing & Verification

### Run Pytest Test Suite (18 Unit & Integration Tests)
```bash
python -m pytest backend/tests/ -v
```
*(All 18 tests pass in < 5 seconds).*

### Run 22-Question Evaluation Harness
```bash
python backend/evaluation/run_evaluation.py
```
Output report written to `docs/EVALUATION_REPORT.md`.

### Run End-to-End Smoke Test
```bash
python scripts/smoke_test.py --url http://localhost:8000
```

---

## 5. Measured Evaluation Performance

| Metric | Target | Measured Result |
|---|---|---|
| **Answer Correctness** | $\ge 90\%$ | **100.0%** (22 / 22 questions passed) |
| **Abstention Accuracy** | $100\%$ | **100.0%** (Correctly returns `not_found` on insufficient evidence) |
| **Tool Result Correctness**| $100\%$ | **100.0%** (Zero arithmetic or eligibility errors) |
| **Retrieval Hit Rate** | $\ge 90\%$ | **100.0%** (Top retrieved chunk supports answer) |
| **Latency (p50)** | $< 500$ ms | **238.0 ms** |
| **Latency (p95)** | $< 1000$ ms| **323.0 ms** |
| **Average Tokens** | - | **50.7 tokens** |

---

## 6. Sample curl Commands

### 1. Health Probe (`GET /health`)
```bash
curl -X GET http://localhost:8000/health
```

### 2. View Source Register (`GET /sources`)
```bash
curl -X GET http://localhost:8000/sources
```

### 3. Public Policy Question (`POST /ask`)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the minimum attendance requirement for end-semester exams?"}'
```

### 4. Authenticated Student Attendance (`POST /ask`)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-Student-Id: S1001" \
  -d '{"question": "What is my attendance in CS201?"}'
```

### 5. Deterministic Exam Eligibility Check (`POST /ask`)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-Student-Id: S1001" \
  -d '{"question": "Am I eligible to appear in the end-semester exam for CS201?"}'
```

### 6. Condonation Edge Case (`POST /ask`)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-Student-Id: S1002" \
  -d '{"question": "Am I eligible to appear in the end-semester exam for CS201?"}'
```

### 7. What-If Simulation (`POST /ask`)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-Student-Id: S1003" \
  -d '{"question": "I failed CS201. If I pass the supplementary exam, will I be eligible for placement?"}'
```

### 8. Unanswerable Question Abstention (`POST /ask`)
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the scholarship for studying in Antarctica?"}'
```

### 9. Retrieve Full Audit Record (`GET /audit/{trace_id}`)
```bash
curl -X GET http://localhost:8000/audit/<trace_id>
```

### 10. Live Document Ingestion (`POST /ingest`)
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@backend/data/documents/CIRC-2026-ATT.md" \
  -F 'metadata={"doc_id":"CIRC-LIVE-TEST","title":"Live Notice","issuer":"Dean Academics","authority_level":2,"doc_type":"circular","version":"1.0","effective_from":"2026-10-10","provenance":"https://university.edu"}'
```

---

## 7. Connecting Local Ollama

By default, the backend runs in deterministic mock mode (`LLM_MODE=mock`) for offline testing and continuous integration without GPU requirements.

To connect live Ollama running locally:
1. Ensure Ollama is running and model pulled:
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```
2. Set environment variables in `backend/.env`:
   ```env
   LLM_MODE=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:7b-instruct
   ```
3. Restart backend.
