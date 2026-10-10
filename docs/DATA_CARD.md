# Synthetic Data Card (Annex E Template)

## 1. Purpose
The synthetic dataset provides structured student demographic, enrollment, attendance, and examination result data to exercise deterministic eligibility checks, condonation workflows, and what-if simulation scenarios without exposing real student personal data.

---

## 2. Generator Information
- **Generator Model:** Qwen 2.5 7B Instruct / Gemini 3.8 Flash via deterministic script generation (`backend/scripts/generate_synthetic_data.py`).
- **Temperature:** 0.2 (low temperature for strict schema compliance).
- **Number of Calls:** 1 batch generation script producing 35 complete student trajectories.

---

## 3. Verbatim Prompt Used
```text
Generate a synthetic dataset of undergraduate university engineering students strictly conforming to the Annex C SQLite schema:
- Tables: students, courses, attendance, results.
- Constraint 1: Student IDs must follow S followed by 4 digits (S1001-S8999). NEVER use S9000-S9999 (reserved for judges).
- Constraint 2: Course codes must be standard (CS201, EC201, etc.). NEVER use codes starting with JDG.
- Constraint 3: Attendance percentage is NEVER stored; generate held and attended integers where 0 <= attended <= held and held > 0.
- Constraint 4: In results, total_marks = internal_marks + external_marks, with max 100.
- Constraint 5: Result status must be exactly one of PASS, FAIL, ABSENT, or DETAINED.
- Mandatory Edge Cases:
  1. Student with attendance exactly 75.0% (30/40 classes).
  2. Student with attendance exactly one class below 75% (29/40 = 72.5%, condonable).
  3. Student failed with total marks just 1 below pass mark (39/100 where pass is 40).
  4. Student with ABSENT examination status.
  5. Student with attendance < 65% (20/40 = 50.0%) and DETAINED status.
  6. Student with multiple active backlogs (>= 2).
  7. Student with CGPA exactly at placement cut-off (6.50) and 0 backlogs.
```

---

## 4. Schema Enforcement
- Generated data was serialized to CSV files in `backend/data/synthetic/` and parsed through Pydantic v2 schemas (`StudentSchema`, `CourseSchema`, `AttendanceItem`, `ResultItem`).
- Type conversions and bounds checks are enforced during SQLite database insertion.

---

## 5. Row Counts & Distributions
- **Students:** 35 students across 2 programmes (`B.Tech CSE`: 20, `B.Tech ECE`: 15) and 3 batches (`2022`, `2023`, `2024`).
- **Courses:** 6 accredited courses across 3 semesters (`CS201`, `CS202`, `CS301`, `EC201`, `EC202`, `MA101`).
- **Attendance Rows:** 124 records (classes held between 40, classes attended between 20 and 40).
- **Results Rows:** 124 examination records.

---

## 6. Edge Cases Coverage Table

| Edge Case Description | Student ID | Key Data Values | Expected System Behavior |
|---|---|---|---|
| **Attendance exactly at 75.0% threshold** | `S1001` | CS201: 30/40 classes (75.0%) | Eligible for regular exam without condonation |
| **Attendance one class below threshold** | `S1002` | CS201: 29/40 classes (72.5%) | Flagged as `CONDONATION_REQUIRED` under Clause 7.3 |
| **Failed with marks just below pass mark** | `S1003` | CS201: Internal 15, External 24, Total 39/100 | Result FAIL; eligible for supplementary exam |
| **Absent in regular exam** | `S1004` | CS201: Internal 28, External 0, Total 28, Result ABSENT | Result ABSENT; eligible for supplementary exam |
| **Detained student (attendance < 65%)** | `S1005` | CS201: 20/40 classes (50.0%), Result DETAINED | Detained; ineligible for exam and supplementary |
| **Multiple active backlogs** | `S1006` | Active backlogs: 3, Failed CS201, CS202, MA101 | Barred from placement registration |
| **CGPA exactly at placement cut-off** | `S1007` | CGPA: 6.50, Active backlogs: 0 | Eligible for tier-1 placement registration |

---

## 7. Validation Results
- Validation script: `backend/scripts/validate_synthetic_data.py`.
- Result: **35 students verified, 6 courses verified, 0 violations found**.
- Constraints checked:
  - `attended <= held` (100% compliant)
  - `total_marks == internal_marks + external_marks` (100% compliant)
  - `result == PASS` only if `total_marks >= 40` (100% compliant)
  - Namespace isolation: 0 IDs in `S9000-S9999`, 0 courses with `JDG` prefix.

---

## 8. What the LLM Got Wrong and How It Was Fixed
1. **Range string format:** Initially, the LLM generated rule registry thresholds for condonation as `"65-75"`. Code attempting `float(rule["value"])` failed with `ValueError`. Fixed by parsing range strings to extract the lower threshold (`65.0`).
2. **Attendance storage:** Early prompt drafts tried to add an `attendance_pct` column to the `attendance` table. This violated Annex C rules ("Attendance % is computed by tools, never stored"). The column was removed and replaced with dynamic calculation `(classes_attended / classes_held) * 100`.

---

## 9. Known Limitations
- Attendance records assume an identical number of held classes (40) across regular courses.
- The dataset focuses on B.Tech undergraduate programmes and does not include M.Tech or PhD degree programs.
