"""
CLI Student and Rule Registry Loader
Usage:
    python backend/scripts/load_students.py --dir backend/data/synthetic
"""

import os
import csv
import argparse
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.db import init_db, execute_dml, execute_many

INITIAL_RULES = [
    (
        "ATT-MIN-01",
        "Minimum 75% attendance required in each course to appear in end-semester examination.",
        "min_attendance_pct",
        ">=",
        "75",
        "ALL",
        "ALL",
        "2024-07-01",
        None,
        "ACAD-REG-2024",
        "Clause 7.2"
    ),
    (
        "ATT-COND-01",
        "Attendance condonation between 65% and 75% on genuine medical grounds or sanctioned university duties.",
        "min_attendance_pct",
        "between",
        "65-75",
        "ALL",
        "ALL",
        "2024-07-01",
        None,
        "ACAD-REG-2024",
        "Clause 7.3"
    ),
    (
        "PASS-MIN-01",
        "Minimum 40 marks out of 100 required to pass a theory course.",
        "pass_marks",
        ">=",
        "40",
        "ALL",
        "ALL",
        "2024-07-01",
        None,
        "ACAD-REG-2024",
        "Clause 8.1"
    ),
    (
        "SUPP-ELIG-01",
        "Student who failed regular examination and has attendance >= 65% is eligible to appear in supplementary exam.",
        "supplementary_eligible",
        "==",
        "TRUE",
        "ALL",
        "ALL",
        "2024-07-01",
        None,
        "ACAD-REG-2024",
        "Clause 8.4"
    ),
    (
        "PLACE-CGPA-01",
        "Minimum CGPA of 6.50 required for campus placement registration and drive participation.",
        "placement_min_cgpa",
        ">=",
        "6.5",
        "ALL",
        "ALL",
        "2025-08-01",
        None,
        "PLACE-POL-2025",
        "Clause 3.1"
    ),
    (
        "PLACE-BACKLOG-01",
        "Student must have 0 active backlogs at the time of placement registration.",
        "placement_max_backlogs",
        "==",
        "0",
        "ALL",
        "ALL",
        "2025-08-01",
        None,
        "PLACE-POL-2025",
        "Clause 3.2"
    ),
    (
        "CIRC-ATT-2026",
        "Revised attendance norm: Minimum 80% attendance required for batch 2024+ onward.",
        "min_attendance_pct",
        ">=",
        "80",
        "ALL",
        "2024+",
        "2026-08-01",
        None,
        "CIRC-2026-ATT",
        "Section 1"
    )
]

def load_data(data_dir: str):
    print(f"Loading data from {data_dir} into SQLite database...")
    init_db()

    # 1. Populate rule registry
    execute_many(
        """
        INSERT OR REPLACE INTO rule_registry (
            rule_id, description, parameter, operator, value,
            scope_programmes, scope_batches, effective_from, effective_to,
            source_doc_id, source_section
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        INITIAL_RULES
    )
    print(f"Populated {len(INITIAL_RULES)} source-linked rules in rule_registry.")

    # 2. Load courses.csv
    courses_f = os.path.join(data_dir, "courses.csv")
    if os.path.exists(courses_f):
        with open(courses_f, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(r["course_code"].strip(), r["course_name"].strip(), r["programme"].strip(), int(r["semester"]), int(r["credits"])) for r in reader]
            execute_many("INSERT OR REPLACE INTO courses VALUES (?, ?, ?, ?, ?)", rows)
            print(f"Loaded {len(rows)} courses.")

    # 3. Load students.csv
    students_f = os.path.join(data_dir, "students.csv")
    if os.path.exists(students_f):
        with open(students_f, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(r["student_id"].strip(), r["full_name"].strip(), r["programme"].strip(), int(r["batch_year"]), int(r["current_semester"]), float(r["cgpa"]), int(r["active_backlogs"])) for r in reader]
            execute_many("INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
            print(f"Loaded {len(rows)} students.")

    # 4. Load attendance.csv
    att_f = os.path.join(data_dir, "attendance.csv")
    if os.path.exists(att_f):
        with open(att_f, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(r["student_id"].strip(), r["course_code"].strip(), int(r["classes_held"]), int(r["classes_attended"])) for r in reader]
            execute_many("INSERT OR REPLACE INTO attendance VALUES (?, ?, ?, ?)", rows)
            print(f"Loaded {len(rows)} attendance records.")

    # 5. Load results.csv
    res_f = os.path.join(data_dir, "results.csv")
    if os.path.exists(res_f):
        with open(res_f, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [(r["student_id"].strip(), r["course_code"].strip(), r["exam_session"].strip(), r["exam_type"].strip(), int(r["internal_marks"]), int(r["external_marks"]), int(r["total_marks"]), int(r.get("max_marks", 100)), r["result"].strip()) for r in reader]
            execute_many("INSERT OR REPLACE INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
            print(f"Loaded {len(rows)} results records.")

    print("Data loading completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load student data and rule registry")
    parser.add_argument("--dir", default="backend/data/synthetic", help="Path to synthetic data directory")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)
    load_data(target_dir)
