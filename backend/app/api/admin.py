import csv
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from app.database.db import execute_dml, execute_many

router = APIRouter()

@router.post("/admin/load_students")
async def load_test_students(
    students_csv: Optional[UploadFile] = File(None),
    courses_csv: Optional[UploadFile] = File(None),
    attendance_csv: Optional[UploadFile] = File(None),
    results_csv: Optional[UploadFile] = File(None)
):
    loaded_counts = {"students": 0, "courses": 0, "attendance": 0, "results": 0}

    # 1. Students CSV
    if students_csv:
        content = await students_csv.read()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        rows = []
        for r in reader:
            rows.append((
                r["student_id"].strip(),
                r["full_name"].strip(),
                r["programme"].strip(),
                int(r["batch_year"]),
                int(r["current_semester"]),
                float(r["cgpa"]),
                int(r["active_backlogs"])
            ))
        if rows:
            execute_many(
                """
                INSERT OR REPLACE INTO students (
                    student_id, full_name, programme, batch_year, current_semester, cgpa, active_backlogs
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                rows
            )
            loaded_counts["students"] = len(rows)

    # 2. Courses CSV
    if courses_csv:
        content = await courses_csv.read()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        rows = []
        for r in reader:
            rows.append((
                r["course_code"].strip(),
                r["course_name"].strip(),
                r["programme"].strip(),
                int(r["semester"]),
                int(r["credits"])
            ))
        if rows:
            execute_many(
                """
                INSERT OR REPLACE INTO courses (
                    course_code, course_name, programme, semester, credits
                ) VALUES (?, ?, ?, ?, ?)
                """,
                rows
            )
            loaded_counts["courses"] = len(rows)

    # 3. Attendance CSV
    if attendance_csv:
        content = await attendance_csv.read()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        rows = []
        for r in reader:
            rows.append((
                r["student_id"].strip(),
                r["course_code"].strip(),
                int(r["classes_held"]),
                int(r["classes_attended"])
            ))
        if rows:
            execute_many(
                """
                INSERT OR REPLACE INTO attendance (
                    student_id, course_code, classes_held, classes_attended
                ) VALUES (?, ?, ?, ?)
                """,
                rows
            )
            loaded_counts["attendance"] = len(rows)

    # 4. Results CSV
    if results_csv:
        content = await results_csv.read()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        rows = []
        for r in reader:
            rows.append((
                r["student_id"].strip(),
                r["course_code"].strip(),
                r["exam_session"].strip(),
                r["exam_type"].strip(),
                int(r["internal_marks"]),
                int(r["external_marks"]),
                int(r["total_marks"]),
                int(r.get("max_marks", 100)),
                r["result"].strip()
            ))
        if rows:
            execute_many(
                """
                INSERT OR REPLACE INTO results (
                    student_id, course_code, exam_session, exam_type, internal_marks,
                    external_marks, total_marks, max_marks, result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows
            )
            loaded_counts["results"] = len(rows)

    return {
        "status": "success",
        "loaded": loaded_counts
    }
