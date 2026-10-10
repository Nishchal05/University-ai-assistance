# Team Contributions and Original Work Declaration

Conforming to Section 8, Section 9.4, and the HCLTech Hackathon participant rules.

---

## 1. Team Contributions Breakdown

| Team Member | Role & Component Responsibility | Key Deliverables Built |
|---|---|---|
| **Member 1 (Full Stack AI Engineer)** | LangGraph Architecture & Orchestration | Graph state workflow, query classification, policy validation node, response validation, audit logging (`backend/app/graph/`, `backend/app/main.py`) |
| **Member 2 (AI/RAG Specialist)** | Document Extraction, Embeddings & RAG Pipeline | PDF/DOCX chunking, persistent ChromaDB integration, hybrid BM25 search, live `/ingest` endpoint (`backend/app/rag/`, `backend/app/api/ingest.py`) |
| **Member 3 (Backend & Data Engineer)** | Database, Deterministic Tools & Synthetic Data | SQLite schema (Annex C), student tools, rule registry loader, synthetic data generation and validation scripts (`backend/app/tools/`, `backend/scripts/`) |
| **Member 4 (Frontend & Security Engineer)** | React UI, Dev Proxy & Adversarial Testing | React + Vite application, unified API client (`src/lib/api.js`), Chat, Dashboard, Admin pages, adversarial security tests (`frontend/src/`, `backend/tests/`) |

---

## 2. Declaration of Original Work

We hereby declare that:
1. The codebase, system architecture, data generation scripts, evaluation harness, and user interfaces submitted in this repository represent original engineering work designed for the HCLTech Future Ready AI Engineer Hackathon.
2. No code was shared with or copied from competing teams.
3. No real student personal data has been used in this repository. All student records are synthetically generated using LLM prompting and verified against Annex C schemas.
4. All AI coding assistant usage has been disclosed in `docs/AI_USAGE_DISCLOSURE.md`.
