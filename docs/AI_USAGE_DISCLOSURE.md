# AI Usage Disclosure Statement

Conforming to Section 8, Section 10, and ethical AI development guidelines of the HCLTech Hackathon.

---

## 1. AI Coding Assistants Used
- **Assistant:** Antigravity AI (powered by Google DeepMind Advanced Agentic Coding).
- **Scope of Generation:**
  - Automated scaffolding of FastAPI routers and Pydantic schemas.
  - Implementation of LangGraph workflow node routing.
  - Automated generation of the 35-student synthetic dataset adhering to Annex C constraints.
  - React + Tailwind UI components (Chat, Dashboard, Admin).
  - Test suites (`backend/tests/test_backend.py`, `backend/tests/test_precedence.py`) and evaluation harness (`backend/evaluation/run_evaluation.py`).

---

## 2. Verification and Human-in-the-Loop Validation
Every component generated was subjected to strict verification:
1. **Schema Validation:** The synthetic dataset was passed through `backend/scripts/validate_synthetic_data.py`, verifying 0 violations across 124 attendance and 124 result rows.
2. **Automated Unit Testing:** Pytest suite was executed against all 18 test cases with 100% pass rate.
3. **Annex A Precedence Rules:** Verified against worked examples in Section A.3 of the Problem Statement.
4. **Deterministic Calculation Invariant:** Ensured arithmetic and eligibility checks are executed strictly in deterministic Python code without LLM arithmetic.
5. **Evaluation Harness:** Executed across 22 test questions, verifying 100% abstention accuracy, 100% tool result correctness, and 100% retrieval hit rate.
