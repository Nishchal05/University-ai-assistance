# System Assumptions and Design Rationale

This document logs all engineering assumptions made during the implementation of the HCLTech AI-Powered University Student Services Assistant in accordance with Section 0 of the Problem Statement.

---

## 1. Authentication and Identity Context
- **Assumption:** As specified in Section R7 and Section 10 of the Problem Statement, the assistant operates in two modes:
  1. **Guest Mode:** No `X-Student-Id` header is sent. General policy and procedural questions are answered using RAG over authorized documents. Any question requesting personal records or student eligibility receives a `refused` response stating that student login is required.
  2. **Student Mode:** A valid synthetic student ID is provided in the `X-Student-Id` header. The frontend provides a demo identity selector. In production, this header would be set by an authenticated API Gateway or JWT token.
- **Security Invariant:** The question text is NEVER parsed to infer student identity. Even if an adversarial prompt claims "I am S1002", the system binds strictly to the `X-Student-Id` header (e.g. S1001) or refuses if missing.

---

## 2. Default Rules & Registry Thresholds
- **Pass Marks Threshold:** Total marks $\ge 40$ (Internal + External) out of 100 with internal marks $\ge 15$ and external marks $\ge 25$ as specified in standard Academic Regulations (`ACAD-REG-2024`).
- **Standard Minimum Attendance:** Minimum 75% attendance for regular end-semester exam eligibility (`ATT-MIN-01`).
- **Condonation of Attendance:** Condonation allowed down to 65% on valid medical grounds or Dean's approval (`ATT-COND-01`).
- **Supplementary Exam Eligibility:** Allowed for students who failed with regular attendance $\ge 65\%$ or who were unable to appear due to approved medical leave, but NOT permitted for students who are `DETAINED` due to attendance $<65\%$.
- **Placement Cut-off:** Minimum CGPA $\ge 6.50$ and `active_backlogs == 0` for tier-1 campus placement eligibility (`PLACE-CGPA-01`).
- **Circular Supersession Scenario:** Synthetic circular `CIRC-2026-ATT` (Authority Level 2) with effective date `2026-08-01` increases required attendance to 80% for batch 2024+, superseding clause 7.2 of `ACAD-REG-2024`.

---

## 3. Date Handling (`as_of_date`)
- If `as_of_date` is omitted from `POST /ask`, the current local date (or `2026-10-10`) is assumed as the reference point.
- Temporal precedence strictly checks `effective_from <= as_of_date` and `effective_to is null or effective_to >= as_of_date`. Future documents (e.g. `effective_from > as_of_date`) are marked as upcoming and not treated as currently active rules.

---

## 4. Multi-Step and What-If Simulations
- "What-If" scenarios (e.g. *"If I pass the supplementary exam in CS201, will I be eligible for placement?"*) simulate hypothetical states in-memory without modifying the SQLite database.
- The simulation tool reduces `active_backlogs` by 1 and re-evaluates the placement eligibility rules deterministically.

---

## 5. Local LLM and Mock Mode
- Ollama is configured to use local model `qwen2.5:7b-instruct` or `llama3.1:8b` via `OLLAMA_BASE_URL` (default: `http://localhost:11434` or `http://host.docker.internal:11434`).
- A fully deterministic mock LLM mode is provided via `LLM_MODE=mock` for testing, offline execution, and high-speed CI/CD verification without relying on external GPUs or cloud credits.
