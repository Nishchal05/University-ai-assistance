# System Architecture Documentation

The **HCLTech AI-Powered University Student Services Assistant** is designed strictly around the principle: **the simplest architecture that meets all functional requirements scores highest**.

Instead of over-engineering seven autonomous uncoordinated agents, the system employs **one unified LangGraph state machine** backed by deterministic code tools, vector retrieval, and Annex A precedence resolution.

---

## 1. High-Level Architecture Overview

```
 ┌────────────────────────────────────────────────────────┐
 │            Frontend (React + Vite + Tailwind)          │
 │  - Chat UI with Citation & Calculation Cards          │
 │  - Student Dashboard (Attendance, Results, Eligibility)│
 │  - Admin Console (Live Ingestion, Source Register)     │
 └───────────────────────────┬────────────────────────────┘
                             │ HTTP REST (Contract)
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

## 2. Why One Graph Instead of Multiple Disconnected Agents?
1. **Deterministic Authority:** Academic eligibility calculations and attendance percentages must never be computed via LLM probabilistic arithmetic. Writing deterministic Python tools directly in the execution graph guarantees 100% calculation accuracy.
2. **Strict Flow Order:** Policy retrieval and Annex A validation must precede tool execution and synthesis. A directed acyclic graph ensures each gate is enforced in order.
3. **Traceability:** Every decision (from classification to precedence to tool output) is captured within one unified GraphState, producing an exact audit trail (`trace_id`).

---

## 3. Core Workflow Pipeline

### Step 1: Query Classification (`classify_query`)
- Categorizes query into: `policy_fact`, `procedure`, `personal_attendance`, `personal_results`, `personal_eligibility`, `multi_step_simulation`, or `not_answerable`.
- Flags whether personal data, calculations, or policy lookups are needed.
- If classification is uncertain regarding personal data, takes the safer route (requires login).

### Step 2: Authentication Guardrail (`check_authentication`)
- The student's identity is bound **strictly** to the `X-Student-Id` header.
- The system NEVER infers or trusts student identity from message text.
- If personal data is requested without `X-Student-Id`, immediately returns `answer_type: refused`.

### Step 3: Hybrid Knowledge Retrieval (`retrieve_policy`)
- Uses ChromaDB persistent storage with `all-MiniLM-L6-v2` ONNX embeddings.
- Combines semantic similarity with BM25 keyword matching for exact clause numbers (e.g. `Clause 7.2`) and rule IDs (e.g. `ATT-MIN-01`).

### Step 4: Annex A Policy Precedence Validation (`validate_policy`)
Evaluates candidate documents in strict Annex A order:
1. **Applicability:** Checks `effective_from <= as_of_date <= effective_to`, and verifies programme and batch scope.
2. **Explicit Supersession:** A circular at Authority Level 1 or 2 explicitly superseding a prior regulation clause replaces it.
3. **Authority Level:** Regulations (Level 1) prevail over Circulars (Level 2), Notices (Level 3), FAQs (Level 4), and Unofficial posts (Level 5).
4. **Recency:** Later `effective_from` prevails between documents of identical authority.
5. **Unresolved:** Returns `conflict_flagged`, cites both sources, and advises the issuing office.

### Step 5: Deterministic Student Tools (`execute_student_tools`)
- Reads from SQLite using parameterized queries.
- `attendance_pct = classes_attended / classes_held * 100` is computed dynamically.
- Thresholds are read from `rule_registry`, never hardcoded constants.
- What-If simulations calculate in-memory hypothetical projections without mutating SQLite.

### Step 6: Grounded Synthesis (`generate_answer`)
- LLM (or mock generator) synthesizes an explanation referencing the cited clauses and tool calculations.
- If evidence is below relevance threshold: returns `not_found` with *"I could not find this information in the authorised university sources."*

### Step 7: Response Validation (`validate_response`)
- Verifies output against privacy leakage, ensuring another student's data is never revealed.

### Step 8: Audit Persistence (`save_audit`)
- Writes full structured audit record into `audit_logs` SQLite table.
