"""
Validation Script for Annex C Synthetic Student Data
Enforces logical constraints, schema compliance, and namespace isolation.
"""

import os
import csv
import sys
import re

SYNTHETIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/synthetic"))

def validate_dataset(dir_path: str = SYNTHETIC_DIR) -> bool:
    print(f"--- Running Annex C Synthetic Data Validation on {dir_path} ---")
    violations = []

    # 1. Validate students.csv
    students_file = os.path.join(dir_path, "students.csv")
    if not os.path.exists(students_file):
        print(f"ERROR: {students_file} not found.")
        return False

    student_ids = set()
    with open(students_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        req_cols = {"student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"}
        if not req_cols.issubset(reader.fieldnames):
            violations.append(f"students.csv missing mandatory columns: {req_cols - set(reader.fieldnames)}")
        
        for idx, row in enumerate(reader, start=2):
            sid = row["student_id"].strip()
            student_ids.add(sid)
            # Namespace check
            if re.match(r"^S9\d{3}$", sid):
                violations.append(f"Line {idx}: {sid} encroaches on judge-reserved namespace S9000-S9999!")
            if not re.match(r"^S\d{4}$", sid):
                violations.append(f"Line {idx}: {sid} invalid format (must be S followed by 4 digits)")
            
            cgpa = float(row["cgpa"])
            if not (0.0 <= cgpa <= 10.0):
                violations.append(f"Line {idx} ({sid}): CGPA {cgpa} out of range [0.0, 10.0]")
            
            backlogs = int(row["active_backlogs"])
            if backlogs < 0:
                violations.append(f"Line {idx} ({sid}): active_backlogs cannot be negative")

    # 2. Validate courses.csv
    courses_file = os.path.join(dir_path, "courses.csv")
    course_codes = set()
    if os.path.exists(courses_file):
        with open(courses_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=2):
                c_code = row["course_code"].strip()
                course_codes.add(c_code)
                if c_code.startswith("JDG"):
                    violations.append(f"Line {idx}: {c_code} encroaches on judge-reserved namespace (starts with JDG)!")

    # 3. Validate attendance.csv
    att_file = os.path.join(dir_path, "attendance.csv")
    if os.path.exists(att_file):
        with open(att_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=2):
                sid = row["student_id"].strip()
                ccode = row["course_code"].strip()
                held = int(row["classes_held"])
                attended = int(row["classes_attended"])

                if held <= 0:
                    violations.append(f"Line {idx} ({sid}, {ccode}): classes_held must be > 0 (got {held})")
                if attended < 0:
                    violations.append(f"Line {idx} ({sid}, {ccode}): classes_attended cannot be negative (got {attended})")
                if attended > held:
                    violations.append(f"Line {idx} ({sid}, {ccode}): classes_attended ({attended}) > classes_held ({held}) violation!")

    # 4. Validate results.csv
    res_file = os.path.join(dir_path, "results.csv")
    if os.path.exists(res_file):
        with open(res_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=2):
                sid = row["student_id"].strip()
                ccode = row["course_code"].strip()
                internal = int(row["internal_marks"])
                external = int(row["external_marks"])
                total = int(row["total_marks"])
                max_m = int(row.get("max_marks", 100))
                result = row["result"].strip()

                if internal < 0 or external < 0:
                    violations.append(f"Line {idx} ({sid}, {ccode}): negative marks found")
                if total != (internal + external):
                    violations.append(f"Line {idx} ({sid}, {ccode}): total ({total}) != internal ({internal}) + external ({external})")
                if total > max_m:
                    violations.append(f"Line {idx} ({sid}, {ccode}): total ({total}) > max_marks ({max_m})")

                if result not in ["PASS", "FAIL", "ABSENT", "DETAINED"]:
                    violations.append(f"Line {idx} ({sid}, {ccode}): invalid result status '{result}'")
                
                # Check consistency
                if result == "PASS" and total < 40:
                    violations.append(f"Line {idx} ({sid}, {ccode}): result PASS but total marks {total} < 40")
                if result == "FAIL" and total >= 40:
                    violations.append(f"Line {idx} ({sid}, {ccode}): result FAIL but total marks {total} >= 40")

    # Output Summary
    print(f"Total synthetic students checked: {len(student_ids)}")
    print(f"Total courses checked: {len(course_codes)}")
    if violations:
        print(f"FAILED: Found {len(violations)} constraint violations:")
        for v in violations[:15]:
            print(f"  - {v}")
        return False
    else:
        print("SUCCESS: 0 violations found. All Annex C schema and logical constraints satisfied!")
        return True

if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
