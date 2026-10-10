# University AI Assistant - Backend Service

FastAPI-powered backend service providing authoritative academic policy retrieval, hybrid vector search (ChromaDB), deterministic tool execution, and source precedence resolution.

---

## Features

- **FastAPI Core**: Fast, async REST API with automatic Swagger docs (`/docs`).
- **LangGraph State Machine**: Deterministic orchestration for query classification, policy retrieval, tool verification, and grounded answer synthesis.
- **ChromaDB Hybrid Search**: Persistent vector store with dense vector embeddings (`all-MiniLM-L6-v2`) and BM25 keyword boosting.
- **SQLite Database**: Authoritative source register, course rules, synthetic student records, and tamper-evident audit trail logs.
- **Live Document Ingestion**: `POST /ingest` extracts text, chunks, computes vector embeddings, and immediately updates the Source Register.
- **Annex A Precedence Engine**: Automatically resolves conflicts between higher-authority ordinances and newer departmental circulars.

---

## Directory Layout

```text
backend/
├── app/
│   ├── main.py              # FastAPI application entrypoint & middleware
│   ├── api/                 # API route handlers
│   │   ├── ask.py           # POST /ask query orchestration
│   │   ├── ingest.py        # POST /ingest document upload & indexing
│   │   ├── sources.py       # GET /sources live Source Register
│   │   ├── health.py        # GET /health system readiness probe
│   │   ├── audit.py         # GET /audit/{trace_id} observability trace
│   │   ├── admin.py         # Admin endpoints
│   │   └── student.py       # Student record endpoints
│   ├── graph/               # LangGraph workflow state machine
│   ├── rag/                 # ChromaDB client, PDF/DOCX extractors, hybrid search
│   ├── services/            # Policy precedence engine & LLM generation service
│   ├── tools/               # Deterministic calculation tools
│   ├── database/            # SQLite schema, migrations, connection pool
│   └── models/              # Pydantic v2 schemas
├── data/
│   ├── documents/           # Policy PDFs and Markdown source documents
│   ├── chroma/              # ChromaDB persistent vector database files
│   ├── university.db        # SQLite database file
│   └── source_register.csv  # Flat-file backup of authoritative Source Register
├── evaluation/              # 22-question accuracy and evaluation harness
├── scripts/                 # Ingestion, seeding, and validation scripts
│   ├── seed_documents.py    # Seeds ChromaDB vector DB and Source Register
│   ├── load_students.py     # Loads student records into SQLite
│   ├── generate_synthetic_data.py
│   └── validate_synthetic_data.py
├── tests/                   # Pytest unit and integration test suite
├── requirements.txt         # Python dependencies
└── Dockerfile               # Production container image
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- `pip` package manager

### 2. Environment Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Seed Database & Index Documents
To initialize the SQLite database and index all policy documents into the ChromaDB vector database:
```powershell
python scripts/seed_documents.py
```
This indexes:
- `ACAD-REG-2024` (Academic Regulations for B.Tech Programmes)
- `PLACE-POL-2025` (Campus Placement & Internship Policy 2025-2026)
- `CIRC-2026-ATT` (Circular: Revision of Minimum Attendance Threshold)
- `DEPT-FAQ-2026` (Department Student Helpdesk FAQ)
- `NITJ-ACAD-POLICY-2023` (NITJ Ordinances & Regulations for UG Programme 2023 PDF)
- `NITJ-PLACEMENT-POLICY-2026` (NITJ Placement & Internship Policy 2023-2027 Onwards)

### 4. Run Development Server
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/health`

---

## Configuration (`.env`)

Copy `.env.example` to `.env` if you want to customize settings:

```env
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173

# LLM Mode: 'mock' for local deterministic offline testing, or 'ollama' for live local inference
LLM_MODE=mock
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct

# Storage paths
SQLITE_DB_PATH=backend/data/university.db
CHROMA_PERSIST_DIR=backend/data/chroma
DOCUMENTS_STORAGE_DIR=backend/data/documents
```

---

## Running Tests & Evaluation

### Run Pytest Test Suite
```powershell
python -m pytest tests/ -v
```

### Run Evaluation Harness (22 Test Questions)
```powershell
python evaluation/run_evaluation.py
```
Results and metrics will be logged and output to `docs/EVALUATION_REPORT.md`.
