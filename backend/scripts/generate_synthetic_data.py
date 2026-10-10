"""
Synthetic Student Data Generator for HCLTech University AI Assistant
Conforms to Annex C schema and includes all required edge cases.
Namespace rules:
  - Student IDs: S1001 to S1035 (Preserves S9000-S9999 for judges)
  - Course codes: CS201, CS202, CS301, EC201, EC202, MA101 (Preserves JDG* for judges)
"""

import os
import csv
import random

SYNTHETIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/synthetic"))

PROGRAMMES = ["B.Tech CSE", "B.Tech ECE"]
BATCHES = [2022, 2023, 2024]

COURSES = [
    {"course_code": "CS201", "course_name": "Data Structures & Algorithms", "programme": "B.Tech CSE", "semester": 3, "credits": 4},
    {"course_code": "CS202", "course_name": "Computer Organization & Architecture", "programme": "B.Tech CSE", "semester": 3, "credits": 4},
    {"course_code": "CS301", "course_name": "Database Management Systems", "programme": "B.Tech CSE", "semester": 5, "credits": 4},
    {"course_code": "EC201", "course_name": "Digital System Design", "programme": "B.Tech ECE", "semester": 3, "credits": 4},
    {"course_code": "EC202", "course_name": "Signals & Systems", "programme": "B.Tech ECE", "semester": 3, "credits": 4},
    {"course_code": "MA101", "course_name": "Engineering Mathematics-I", "programme": "B.Tech CSE", "semester": 1, "credits": 4},
]

# 35 Synthetic student profiles (exceeding minimum 30)
STUDENT_DATA = [
    # Edge Case 1: Attendance exactly at threshold (75.0% in CS201 -> 30/40)
    {"id": "S1001", "name": "Aarav Sharma", "prog": "B.Tech CSE", "batch": 2023, "sem": 5, "cgpa": 8.42, "backlogs": 0, "edge": "attendance_exact_75"},
    # Edge Case 2: Attendance one class below threshold (72.5% in CS201 -> 29/40)
    {"id": "S1002", "name": "Diya Patel", "prog": "B.Tech CSE", "batch": 2023, "sem": 5, "cgpa": 7.85, "backlogs": 0, "edge": "attendance_one_below_75"},
    # Edge Case 3: Failed with marks just below pass mark (39/100 where pass is 40 in CS201)
    {"id": "S1003", "name": "Rohan Verma", "prog": "B.Tech CSE", "batch": 2023, "sem": 5, "cgpa": 6.10, "backlogs": 1, "edge": "failed_marks_39"},
    # Edge Case 4: Absent result in regular exam
    {"id": "S1004", "name": "Ananya Iyer", "prog": "B.Tech CSE", "batch": 2023, "sem": 5, "cgpa": 7.20, "backlogs": 1, "edge": "absent_result"},
    # Edge Case 5: Detained student (attendance 50% < 65% in CS201 -> 20/40)
    {"id": "S1005", "name": "Kabir Mehta", "prog": "B.Tech CSE", "batch": 2023, "sem": 5, "cgpa": 5.40, "backlogs": 1, "edge": "detained_attendance_50"},
    # Edge Case 6: Multiple backlogs (3 backlogs)
    {"id": "S1006", "name": "Ishaan Nair", "prog": "B.Tech ECE", "batch": 2022, "sem": 7, "cgpa": 5.80, "backlogs": 3, "edge": "multiple_backlogs"},
    # Edge Case 7: CGPA exactly at placement cut-off (6.50, 0 backlogs)
    {"id": "S1007", "name": "Meera Joshi", "prog": "B.Tech CSE", "batch": 2022, "sem": 7, "cgpa": 6.50, "backlogs": 0, "edge": "cgpa_exact_placement_cutoff"},
]

# Additional 28 standard students
ADDITIONAL_NAMES = [
    ("Arjun Reddy", "B.Tech CSE", 2023, 5, 8.90, 0),
    ("Pooja Choudhary", "B.Tech CSE", 2023, 5, 7.60, 0),
    ("Siddharth Rao", "B.Tech CSE", 2023, 5, 9.15, 0),
    ("Sneha Kulkarni", "B.Tech CSE", 2023, 5, 8.20, 0),
    ("Vikram Singhania", "B.Tech CSE", 2024, 3, 7.45, 0),
    ("Tanvi Deshmukh", "B.Tech CSE", 2024, 3, 8.35, 0),
    ("Aditya Malhotra", "B.Tech CSE", 2024, 3, 6.80, 0),
    ("Kavya Nambiar", "B.Tech CSE", 2024, 3, 9.05, 0),
    ("Rishi Banerjee", "B.Tech ECE", 2022, 7, 7.90, 0),
    ("Neha Kapoor", "B.Tech ECE", 2022, 7, 6.45, 1), # placement ineligible by CGPA & backlog
    ("Gaurav Bhatia", "B.Tech ECE", 2022, 7, 8.10, 0),
    ("Shruti Saxena", "B.Tech ECE", 2022, 7, 7.30, 0),
    ("Nikhil Gupta", "B.Tech ECE", 2023, 5, 8.55, 0),
    ("Riya Sen", "B.Tech ECE", 2023, 5, 6.70, 0),
    ("Varun Menon", "B.Tech ECE", 2023, 5, 7.15, 0),
    ("Anushka Das", "B.Tech ECE", 2023, 5, 8.75, 0),
    ("Kartik Pillai", "B.Tech ECE", 2024, 3, 7.95, 0),
    ("Bhavna Mishra", "B.Tech ECE", 2024, 3, 6.30, 1),
    ("Manish Tiwari", "B.Tech ECE", 2024, 3, 8.40, 0),
    ("Simran Gill", "B.Tech ECE", 2024, 3, 7.80, 0),
    ("Pranav Joshi", "B.Tech CSE", 2022, 7, 6.49, 0), # just 0.01 below placement cut-off
    ("Aarti Aggarwal", "B.Tech CSE", 2022, 7, 9.30, 0),
    ("Harsh Vardhan", "B.Tech CSE", 2022, 7, 7.70, 0),
    ("Sonalika Roy", "B.Tech CSE", 2023, 5, 8.10, 0),
    ("Devansh Goel", "B.Tech CSE", 2023, 5, 7.50, 0),
    ("Natasha Sethi", "B.Tech ECE", 2023, 5, 8.60, 0),
    ("Karan Oberoi", "B.Tech ECE", 2024, 3, 7.20, 0),
    ("Divya Rawat", "B.Tech ECE", 2024, 3, 8.00, 0),
]

for idx, (nm, prog, batch, sem, cgpa, backlogs) in enumerate(ADDITIONAL_NAMES, start=8):
    STUDENT_DATA.append({
        "id": f"S{1000 + idx}",
        "name": nm,
        "prog": prog,
        "batch": batch,
        "sem": sem,
        "cgpa": cgpa,
        "backlogs": backlogs,
        "edge": "standard"
    })

def generate_csvs():
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)

    # 1. students.csv
    students_file = os.path.join(SYNTHETIC_DIR, "students.csv")
    with open(students_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"])
        for s in STUDENT_DATA:
            writer.writerow([s["id"], s["name"], s["prog"], s["batch"], s["sem"], s["cgpa"], s["backlogs"]])

    # 2. courses.csv
    courses_file = os.path.join(SYNTHETIC_DIR, "courses.csv")
    with open(courses_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["course_code", "course_name", "programme", "semester", "credits"])
        for c in COURSES:
            writer.writerow([c["course_code"], c["course_name"], c["programme"], c["semester"], c["credits"]])

    # 3. attendance.csv & 4. results.csv
    attendance_rows = []
    results_rows = []

    for s in STUDENT_DATA:
        sid = s["id"]
        prog = s["prog"]
        edge = s["edge"]

        applicable_courses = [c["course_code"] for c in COURSES if c["programme"] == prog or c["course_code"] == "MA101"]

        for c_code in applicable_courses:
            held = 40
            attended = 34 # 85% default

            # Handle edge cases for primary course CS201 / EC201
            if c_code in ["CS201", "EC201"]:
                if edge == "attendance_exact_75":
                    attended = 30 # exactly 75.0%
                elif edge == "attendance_one_below_75":
                    attended = 29 # exactly 72.5% (one class below)
                elif edge == "detained_attendance_50":
                    attended = 20 # exactly 50.0% (< 65% -> DETAINED)
                elif edge == "multiple_backlogs":
                    attended = 26 # 65.0%
                elif edge == "cgpa_exact_placement_cutoff":
                    attended = 32 # 80.0%
            elif c_code in ["CS202", "EC202"]:
                if edge == "multiple_backlogs":
                    attended = 28
            attendance_rows.append([sid, c_code, held, attended])

            # Generate examination results
            internal = 35
            external = 45
            total = internal + external
            res = "PASS"

            if c_code in ["CS201", "EC201"]:
                if edge == "failed_marks_39":
                    internal = 15
                    external = 24
                    total = 39 # Just 1 below pass mark of 40!
                    res = "FAIL"
                elif edge == "absent_result":
                    internal = 28
                    external = 0
                    total = 28
                    res = "ABSENT"
                elif edge == "detained_attendance_50":
                    internal = 10
                    external = 0
                    total = 10
                    res = "DETAINED"
                elif edge == "multiple_backlogs":
                    internal = 12
                    external = 20
                    total = 32
                    res = "FAIL"
            elif c_code in ["CS202", "EC202"]:
                if edge == "multiple_backlogs":
                    internal = 14
                    external = 22
                    total = 36
                    res = "FAIL"

            results_rows.append([
                sid, c_code, "2025-DEC", "REGULAR", internal, external, total, 100, res
            ])

    att_file = os.path.join(SYNTHETIC_DIR, "attendance.csv")
    with open(att_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "course_code", "classes_held", "classes_attended"])
        writer.writerows(attendance_rows)

    res_file = os.path.join(SYNTHETIC_DIR, "results.csv")
    with open(res_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks", "total_marks", "max_marks", "result"])
        writer.writerows(results_rows)

    print(f"Generated {len(STUDENT_DATA)} students, {len(COURSES)} courses, {len(attendance_rows)} attendance rows, {len(results_rows)} results rows in {SYNTHETIC_DIR}.")

if __name__ == "__main__":
    generate_csvs()
