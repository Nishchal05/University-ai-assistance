from fastapi import APIRouter, Header, HTTPException
from typing import Optional, List
from app.models.schemas import StudentProfileResponse, StudentSchema, AttendanceItem, ResultItem
from app.tools.student_tools import get_student_profile, get_attendance, get_results
from app.database.db import query_all

router = APIRouter()

@router.get("/student/all_ids")
async def get_all_student_ids():
    """Returns list of all available synthetic student IDs and names for the demo selector."""
    rows = query_all("SELECT student_id, full_name, programme, batch_year, current_semester FROM students ORDER BY student_id ASC")
    return [dict(r) for r in rows]

@router.get("/student/profile", response_model=StudentProfileResponse)
async def get_profile(x_student_id: Optional[str] = Header(None, alias="X-Student-Id")):
    if not x_student_id or not x_student_id.strip():
        raise HTTPException(status_code=401, detail="X-Student-Id header is required to access profile.")

    student_id = x_student_id.strip().upper()
    p_res = get_student_profile(student_id, student_id)
    if not p_res.get("found"):
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found.")

    att_res = get_attendance(student_id, auth_student_id=student_id)
    courses_att = att_res.get("courses", []) if att_res.get("found") else []

    res_data = get_results(student_id, auth_student_id=student_id)
    exam_results = res_data.get("results", []) if res_data.get("found") else []

    return StudentProfileResponse(
        student=StudentSchema(**p_res["student"]),
        attendance=[AttendanceItem(**c) for c in courses_att],
        results=[ResultItem(**r) for r in exam_results]
    )
