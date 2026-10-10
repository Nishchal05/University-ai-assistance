# HCLTech AI-Powered University Student Services Assistant
## Complete API and System Contract

Extracted from and conforming strictly to the authoritative Problem Statement and Participant Guide.

---

## 1. System Endpoints

### 1.1 `POST /ask`
Submit a question to the assistant.

- **Headers:**
  - `Content-Type: application/json`
  - `X-Student-Id`: *(Optional, string)* e.g. `"S1001"`. Attached ONLY when a student is authenticated in the client. Never extracted from question text.

- **Request Body:**
  ```json
  {
    "question": "Am I eligible to appear in the end-semester exam for CS201?",
    "as_of_date": "2026-10-06"
  }
  ```
  - `question`: *(Required, string)* The student or guest query.
  - `as_of_date`: *(Optional, string, YYYY-MM-DD)* Effective date for temporal policy lookup and eligibility evaluation. Defaults to current server date if omitted.

- **Response Status:** `200 OK`
- **Response Body Schema (Mandatory):**
  ```json
  {
    "trace_id": "7f3c2a9e",
    "answer": "You are eligible to appear in the end-semester exam for CS201.",
    "answer_type": "calculated",
    "citations": [
      {
        "doc_id": "ACAD-REG-2024",
        "title": "Academic Regulations",
        "section": "7.2",
        "page": 14,
        "version": "3.1",
        "effective_from": "2024-07-01"
      }
    ],
    "tools_invoked": [
      {
        "tool": "get_attendance",
        "input": {"course_code": "CS201"},
        "output": {
          "classes_held": 40,
          "classes_attended": 31,
          "attendance_pct": 77.5
        }
      },
      {
        "tool": "check_exam_eligibility",
        "input": {"course_code": "CS201"},
        "output": {"result": "ELIGIBLE", "rule_id": "ATT-MIN-01"}
      }
    ],
    "applied_rules": [
      {
        "rule_id": "ATT-MIN-01",
        "value": ">= 75%",
        "source_doc_id": "ACAD-REG-2024"
      }
    ],
    "conflicts_detected": [],
    "explanation": "Your attendance in CS201 is 77.5%, above the 75% minimum in clause 7.2.",
    "as_of_date": "2026-10-06"
  }
  ```

- **Answer Types (`answer_type`):**
  - `retrieved_fact`: Answer comes directly from cited document text.
  - `calculated`: Answer is computed by a deterministic tool, explained by the LLM.
  - `not_found`: Authorised sources do not contain sufficient evidence. Message: *"I could not find this information in the authorised university sources."*
  - `clarification_needed`: Query is ambiguous (e.g., course unspecified) and assistant prompts back.
  - `refused`: Request unauthorized (attempt to access another student's data, or personal query without `X-Student-Id`).
  - `conflict_flagged`: Precedence policy detected unresolvable conflict between documents; both cited and issuing office recommended.

---

### 1.2 `POST /ingest`
Live multipart upload to ingest and index new university documents without restart.

- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Binary file (.pdf, .docx, .txt, .md).
  - `metadata`: JSON string matching the Source Register fields:
    ```json
    {
      "doc_id": "CIRC-2026-09",
      "title": "Revised Attendance Policy Circular",
      "issuer": "Office of the Dean (Academics)",
      "authority_level": 2,
      "doc_type": "circular",
      "version": "1.0",
      "effective_from": "2026-08-01",
      "effective_to": null,
      "supersedes": "ACAD-REG-2024#7.2",
      "scope_programmes": "ALL",
      "scope_batches": "ALL",
      "provenance": "https://university.edu/notices/2026-09.pdf",
      "retrieved_on": "2026-10-06",
      "synthetic": "N"
    }
    ```
- **Response Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "doc_id": "CIRC-2026-09",
    "chunks_indexed": 12,
    "status": "success",
    "message": "Document ingested and immediately available for search."
  }
  ```

---

### 1.3 `GET /health`
System health and readiness check across all underlying subsystems.

- **Response Body:**
  ```json
  {
    "status": "healthy",
    "api": "ok",
    "vector_store": "ok",
    "sqlite": "ok",
    "llm": "ok",
    "llm_mode": "mock",
    "details": {
      "chroma_collections": 1,
      "chroma_chunks": 48,
      "student_records": 32,
      "rules_count": 8
    }
  }
  ```

---

### 1.4 `GET /sources`
Retrieve the complete Source Register containing all ingested documents and their metadata.

- **Response Body:**
  ```json
  [
    {
      "doc_id": "ACAD-REG-2024",
      "title": "Academic Regulations for B.Tech",
      "issuer": "Office of the Dean (Academics)",
      "authority_level": 1,
      "doc_type": "regulation",
      "version": "3.1",
      "effective_from": "2024-07-01",
      "effective_to": null,
      "supersedes": "ACAD-REG-2021#7.2",
      "scope_programmes": "B.Tech",
      "scope_batches": "ALL",
      "provenance": "https://university.edu/regulations/btech_2024.pdf",
      "retrieved_on": "2026-10-05",
      "synthetic": "N",
      "chunks_count": 28
    }
  ]
  ```

---

### 1.5 `GET /audit/{trace_id}`
Retrieve the full audit record for any past invocation.

- **Response Body:**
  ```json
  {
    "trace_id": "7f3c2a9e",
    "timestamp": "2026-10-06T14:02:11Z",
    "student_id": "S1001",
    "question_category": "personal_eligibility",
    "question": "Am I eligible to appear in the end-semester exam for CS201?",
    "sources_retrieved": [
      {"doc_id": "ACAD-REG-2024", "section": "7.2", "score": 0.82}
    ],
    "precedence_decision": "Applied ACAD-REG-2024#7.2 (Authority 1)",
    "tools_invoked": [
      {"tool": "get_attendance", "status": "ok", "ms": 4},
      {"tool": "check_exam_eligibility", "status": "ok", "ms": 2}
    ],
    "applied_rules": ["ATT-MIN-01"],
    "conflicts_detected": [],
    "answer_type": "calculated",
    "model": "qwen2.5:7b-instruct",
    "llm_calls": 2,
    "tokens": 1420,
    "latency_ms": 182
  }
  ```

---

### 1.6 `POST /admin/load_students`
Admin/judge endpoint to dynamically load student records from CSV files in the Annex C schema.

- **Content-Type:** `multipart/form-data`
- **Files:** `students` (CSV), `courses` (optional CSV), `attendance` (optional CSV), `results` (optional CSV).
- **Response:**
  ```json
  {
    "status": "success",
    "loaded": {
      "students": 10,
      "courses": 4,
      "attendance": 20,
      "results": 15
    }
  }
  ```

---

### 1.7 `GET /student/profile`
Utility endpoint for frontend dashboard (authorized via `X-Student-Id`).

- **Response:**
  ```json
  {
    "student": {
      "student_id": "S1001",
      "full_name": "Aarav Sharma",
      "programme": "B.Tech CSE",
      "batch_year": 2023,
      "current_semester": 5,
      "cgpa": 8.42,
      "active_backlogs": 0
    },
    "attendance": [
      {
        "course_code": "CS201",
        "course_name": "Data Structures",
        "classes_held": 40,
        "classes_attended": 31,
        "attendance_pct": 77.5
      }
    ],
    "results": [
      {
        "course_code": "CS201",
        "course_name": "Data Structures",
        "exam_session": "2025-DEC",
        "exam_type": "REGULAR",
        "internal_marks": 36,
        "external_marks": 45,
        "total_marks": 81,
        "max_marks": 100,
        "result": "PASS"
      }
    ]
  }
  ```

---

## 2. Mandatory SQLite Database Schema (Annex C)

### Table: `students`
| Column | Type | Rules |
|---|---|---|
| `student_id` | TEXT PRIMARY KEY | Format `S` followed by 4 digits (e.g. `S1001`). Reserved for judges: `S9000`–`S9999` |
| `full_name` | TEXT | Synthetic names only |
| `programme` | TEXT | e.g. `B.Tech CSE`, `B.Tech ECE` |
| `batch_year` | INTEGER | Year of admission, e.g. `2023` |
| `current_semester` | INTEGER | 1–10 |
| `cgpa` | REAL | 0.00–10.00 |
| `active_backlogs` | INTEGER | >= 0 |

### Table: `courses`
| Column | Type | Rules |
|---|---|---|
| `course_code` | TEXT PRIMARY KEY | e.g. `CS201`. Reserved for judges: starts with `JDG` |
| `course_name` | TEXT | Name of course |
| `programme` | TEXT | Must match `students.programme` |
| `semester` | INTEGER | Target semester (1–10) |
| `credits` | INTEGER | Course credits |

### Table: `attendance`
| Column | Type | Rules |
|---|---|---|
| `student_id` | TEXT | Foreign Key (`students.student_id`) |
| `course_code` | TEXT | Foreign Key (`courses.course_code`) |
| `classes_held` | INTEGER | > 0 |
| `classes_attended` | INTEGER | 0 <= attended <= held. **Attendance % is NEVER stored; computed dynamically by tools** |
| PRIMARY KEY | `(student_id, course_code)` | Unique enrollment per student-course |

### Table: `results`
| Column | Type | Rules |
|---|---|---|
| `student_id` | TEXT | Foreign Key (`students.student_id`) |
| `course_code` | TEXT | Foreign Key (`courses.course_code`) |
| `exam_session` | TEXT | e.g. `2025-DEC`, `2026-MAY` |
| `exam_type` | TEXT | `REGULAR` or `SUPPLEMENTARY` |
| `internal_marks` | INTEGER | >= 0 |
| `external_marks` | INTEGER | >= 0 |
| `total_marks` | INTEGER | Must equal `internal_marks + external_marks` |
| `max_marks` | INTEGER | Typically 100 |
| `result` | TEXT | `PASS`, `FAIL`, `ABSENT`, or `DETAINED` |
| PRIMARY KEY | `(student_id, course_code, exam_session, exam_type)` | |

### Table: `rule_registry`
| Column | Type | Rules |
|---|---|---|
| `rule_id` | TEXT PRIMARY KEY | e.g. `ATT-MIN-01` |
| `description` | TEXT | Plain language explanation of rule |
| `parameter` | TEXT | e.g. `min_attendance_pct`, `pass_marks`, `placement_min_cgpa` |
| `operator` | TEXT | `>=`, `<=`, `==`, `between` |
| `value` | TEXT | Threshold value (e.g. `75`, `40`, `6.5`) |
| `scope_programmes` | TEXT | `ALL` or comma-separated list |
| `scope_batches` | TEXT | `ALL` or format like `2023+` |
| `effective_from` | TEXT | `YYYY-MM-DD` |
| `effective_to` | TEXT | `YYYY-MM-DD` or empty / null |
| `source_doc_id` | TEXT | Must exist in Source Register |
| `source_section` | TEXT | Clause, section or page in source doc |

### Table: `audit_logs`
| Column | Type | Rules |
|---|---|---|
| `trace_id` | TEXT PRIMARY KEY | UUID or hex string |
| `timestamp` | TEXT | ISO 8601 UTC timestamp |
| `student_id` | TEXT | May be null/empty for guest requests |
| `question_category` | TEXT | Categorization (e.g., `personal_eligibility`, `policy_fact`) |
| `question` | TEXT | Query string |
| `sources_retrieved` | TEXT | JSON list of retrieved documents & sections |
| `precedence_decision` | TEXT | Precedence logic note |
| `tools_invoked` | TEXT | JSON list of invoked tools with status and runtime |
| `applied_rules` | TEXT | JSON list of rule IDs applied |
| `conflicts_detected` | TEXT | JSON list of conflicts |
| `answer_type` | TEXT | Answer type enum |
| `response_payload` | TEXT | Full response JSON |
| `model` | TEXT | Model name (e.g., `mock` or `qwen2.5:7b-instruct`) |
| `llm_calls` | INTEGER | Number of LLM passes |
| `tokens` | INTEGER | Token count |
| `latency_ms` | INTEGER | Request latency in milliseconds |

---

## 3. Annex A — Source Precedence Policy Rules (Mandatory Order)

1. **Applicability:**
   Filter documents where:
   - `effective_from <= as_of_date`
   - `effective_to` is empty/null OR `effective_to >= as_of_date`
   - `scope_programmes` matches student's programme OR is `"ALL"`
   - `scope_batches` matches student's admission year OR is `"ALL"`
   *(Documents not yet effective are excluded from current facts, noted as upcoming changes where relevant).*

2. **Explicit Supersession:**
   If Document A explicitly declares `supersedes: Document B` (or specific clause) AND Document A is issued at Authority Level 1 or 2, Document A replaces Document B.

3. **Authority Level:**
   A higher-authority document prevails over a lower-authority document, regardless of date:
   - Level 1: Statutes, Ordinances, Academic Regulations
   - Level 2: Official Circulars & Notifications (Dean Academics, Registrar, Controller of Exams)
   - Level 3: Department Notices (Head of Department)
   - Level 4: Handbooks and Helpdesk FAQs
   - Level 5: Unofficial Content (Informational only; can NEVER override any other document)

4. **Recency:**
   Between documents of the *same* authority level, the document with the later `effective_from` prevails.

5. **Unresolved:**
   If steps 1–4 do not resolve a direct contradiction, the system MUST return:
   - `answer_type: conflict_flagged`
   - `citations`: list both conflicting sources
   - Explanation describing both conflicting clauses and advising the student to contact the relevant administrative office.

---

## 4. Judge-Reserved Namespaces
- **Student IDs:** `S9000` to `S9999` are strictly reserved for judge test datasets.
- **Course Codes:** Course codes with prefix `JDG` (e.g. `JDG101`, `JDG302`) are strictly reserved for judge test datasets.
- **Synthetic Data Generation:** Synthetic student generator will strictly use `S1001`–`S8999` and standard course codes (`CS201`, `EC201`, `MA101`, etc.).

---

## 5. Synthetic Data Minimums
- Students: $\ge 30$
- Programmes: $\ge 2$ (`B.Tech CSE`, `B.Tech ECE`)
- Batches: $\ge 2$ (`2022`, `2023`, `2024`)
- Courses: $\ge 6$ (`CS201`, `CS202`, `CS301`, `EC201`, `EC202`, `MA101`)
- Explicit Edge Cases:
  1. Attendance exactly at threshold (75.0%)
  2. Attendance one class below threshold (e.g. 72.5% or 74.0%)
  3. Failed course with marks just below pass mark (e.g. 39/100 where passing is 40)
  4. Absent result (`result = 'ABSENT'`)
  5. Detained student (`result = 'DETAINED'`)
  6. Student with multiple backlogs ($\ge 2$)
  7. CGPA exactly at placement cut-off (e.g. 6.50)
