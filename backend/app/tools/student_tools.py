from typing import Dict, Any, List, Optional
from datetime import datetime
from app.database.db import query_one, query_all

class ToolAuthError(Exception):
    """Raised when a tool is called for a student different from authorized context."""
    pass

def verify_student_authorization(requested_student_id: str, auth_student_id: Optional[str]):
    if not auth_student_id:
        raise ToolAuthError("Authentication required: no student identity provided in context.")
    if requested_student_id.upper() != auth_student_id.upper():
        raise ToolAuthError(f"Access denied: authorized as {auth_student_id}, cannot access {requested_student_id}.")

def get_student_profile(student_id: str, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    verify_student_authorization(student_id, auth_student_id)
    student = query_one(
        "SELECT student_id, full_name, programme, batch_year, current_semester, cgpa, active_backlogs FROM students WHERE student_id = ?",
        (student_id.upper(),)
    )
    if not student:
        return {"found": False, "error": f"Student {student_id} not found."}
    return {"found": True, "student": student}

def get_attendance(student_id: str, course_code: Optional[str] = None, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    verify_student_authorization(student_id, auth_student_id)
    if course_code:
        record = query_one(
            """
            SELECT a.student_id, a.course_code, c.course_name, a.classes_held, a.classes_attended
            FROM attendance a
            JOIN courses c ON a.course_code = c.course_code
            WHERE a.student_id = ? AND UPPER(a.course_code) = UPPER(?)
            """,
            (student_id.upper(), course_code.strip())
        )
        if not record:
            return {"found": False, "error": f"No attendance record for student {student_id} in course {course_code}."}
        
        held = record["classes_held"]
        attended = record["classes_attended"]
        pct = round((attended / held) * 100.0, 2) if held > 0 else 0.0
        return {
            "found": True,
            "student_id": student_id.upper(),
            "course_code": record["course_code"],
            "course_name": record["course_name"],
            "classes_held": held,
            "classes_attended": attended,
            "attendance_pct": pct
        }
    else:
        records = query_all(
            """
            SELECT a.student_id, a.course_code, c.course_name, a.classes_held, a.classes_attended
            FROM attendance a
            JOIN courses c ON a.course_code = c.course_code
            WHERE a.student_id = ?
            ORDER BY a.course_code
            """,
            (student_id.upper(),)
        )
        results = []
        for r in records:
            held = r["classes_held"]
            attended = r["classes_attended"]
            pct = round((attended / held) * 100.0, 2) if held > 0 else 0.0
            results.append({
                "course_code": r["course_code"],
                "course_name": r["course_name"],
                "classes_held": held,
                "classes_attended": attended,
                "attendance_pct": pct
            })
        return {"found": True, "student_id": student_id.upper(), "courses": results}

def get_results(student_id: str, course_code: Optional[str] = None, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    verify_student_authorization(student_id, auth_student_id)
    if course_code:
        rows = query_all(
            """
            SELECT r.student_id, r.course_code, c.course_name, r.exam_session, r.exam_type,
                   r.internal_marks, r.external_marks, r.total_marks, r.max_marks, r.result
            FROM results r
            JOIN courses c ON r.course_code = c.course_code
            WHERE r.student_id = ? AND UPPER(r.course_code) = UPPER(?)
            ORDER BY r.exam_session DESC
            """,
            (student_id.upper(), course_code.strip())
        )
        return {"found": len(rows) > 0, "results": rows}
    else:
        rows = query_all(
            """
            SELECT r.student_id, r.course_code, c.course_name, r.exam_session, r.exam_type,
                   r.internal_marks, r.external_marks, r.total_marks, r.max_marks, r.result
            FROM results r
            JOIN courses c ON r.course_code = c.course_code
            WHERE r.student_id = ?
            ORDER BY r.exam_session DESC, r.course_code
            """,
            (student_id.upper(),)
        )
        return {"found": len(rows) > 0, "results": rows}

def get_active_rules(as_of_date: str, parameter: Optional[str] = None, programme: str = "ALL", batch_year: Optional[int] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM rule_registry WHERE effective_from <= ? AND (effective_to IS NULL OR effective_to >= ?)"
    params = [as_of_date, as_of_date]
    if parameter:
        sql += " AND parameter = ?"
        params.append(parameter)
    
    rules = query_all(sql, tuple(params))
    filtered = []
    for r in rules:
        # Check scope programmes
        scope_p = r["scope_programmes"]
        if scope_p != "ALL" and programme != "ALL" and programme not in [p.strip() for p in scope_p.split(",")]:
            continue
        # Check scope batches
        scope_b = r["scope_batches"]
        if scope_b != "ALL" and batch_year is not None:
            if scope_b.endswith("+"):
                base_year = int(scope_b[:-1])
                if batch_year < base_year:
                    continue
            else:
                batches = [int(b.strip()) for b in scope_b.split(",") if b.strip().isdigit()]
                if batch_year not in batches:
                    continue
        filtered.append(r)
    return filtered

def check_exam_eligibility(student_id: str, course_code: str, as_of_date: str, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    verify_student_authorization(student_id, auth_student_id)
    profile_res = get_student_profile(student_id, auth_student_id)
    if not profile_res.get("found"):
        return {"result": "ERROR", "reason": "Student profile not found"}
    student = profile_res["student"]
    
    att_res = get_attendance(student_id, course_code, auth_student_id)
    if not att_res.get("found"):
        return {"result": "ERROR", "reason": f"No attendance record for course {course_code}"}
    
    att_pct = att_res["attendance_pct"]
    
    # Retrieve active attendance rules
    rules = get_active_rules(as_of_date, parameter="min_attendance_pct", programme=student["programme"], batch_year=student["batch_year"])
    
    # Select most specific or latest rule
    min_rule = next((r for r in rules if r["rule_id"] in ["ATT-MIN-02", "ATT-MIN-01"]), None)
    if not min_rule and rules:
        min_rule = rules[0]
    
    if not min_rule:
        # Default safety threshold from Academic Regulations
        min_threshold = 75.0
        rule_id = "ATT-MIN-01"
        source_doc = "ACAD-REG-2024"
    else:
        min_threshold = float(min_rule["value"])
        rule_id = min_rule["rule_id"]
        source_doc = min_rule["source_doc_id"]
        
    condonation_rule = query_one("SELECT * FROM rule_registry WHERE rule_id = 'ATT-COND-01'")
    if condonation_rule and condonation_rule.get("value"):
        v_str = str(condonation_rule["value"]).split("-")[0].strip()
        try:
            cond_threshold = float(v_str)
        except ValueError:
            cond_threshold = 65.0
    else:
        cond_threshold = 65.0
    
    if att_pct >= min_threshold:
        return {
            "result": "ELIGIBLE",
            "attendance_pct": att_pct,
            "required_pct": min_threshold,
            "rule_id": rule_id,
            "source_doc_id": source_doc,
            "clause": min_rule["source_section"] if min_rule else "7.2",
            "reason": f"Attendance is {att_pct}%, which satisfies the minimum required {min_threshold}%."
        }
    elif att_pct >= cond_threshold:
        return {
            "result": "CONDONATION_REQUIRED",
            "attendance_pct": att_pct,
            "required_pct": min_threshold,
            "condonation_threshold": cond_threshold,
            "rule_id": "ATT-COND-01",
            "source_doc_id": condonation_rule["source_doc_id"] if condonation_rule else "ACAD-REG-2024",
            "clause": condonation_rule["source_section"] if condonation_rule else "7.3",
            "reason": f"Attendance is {att_pct}%, which is below {min_threshold}% but eligible for condonation (>= {cond_threshold}%) on medical/competent authority grounds."
        }
    else:
        return {
            "result": "DETAINED",
            "attendance_pct": att_pct,
            "required_pct": min_threshold,
            "rule_id": rule_id,
            "source_doc_id": source_doc,
            "clause": min_rule["source_section"] if min_rule else "7.2",
            "reason": f"Attendance is {att_pct}%, which is below the condonable limit of {cond_threshold}%. Student is detained in {course_code}."
        }

def check_supplementary_eligibility(student_id: str, course_code: str, as_of_date: str, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    verify_student_authorization(student_id, auth_student_id)
    profile_res = get_student_profile(student_id, auth_student_id)
    if not profile_res.get("found"):
        return {"result": "ERROR", "reason": "Student profile not found"}
    
    # Check regular result
    results_res = get_results(student_id, course_code, auth_student_id)
    if not results_res.get("found") or not results_res["results"]:
        return {"result": "INELIGIBLE", "reason": f"No examination history found for course {course_code}."}
    
    latest_exam = results_res["results"][0]
    result_status = latest_exam["result"]
    
    # Also check attendance for condonation/detained status
    att_res = get_attendance(student_id, course_code, auth_student_id)
    att_pct = att_res.get("attendance_pct", 100.0) if att_res.get("found") else 100.0
    
    rule = query_one("SELECT * FROM rule_registry WHERE rule_id = 'SUPP-ELIG-01'")
    source_doc = rule["source_doc_id"] if rule else "ACAD-REG-2024"
    section = rule["source_section"] if rule else "8.4"
    
    if result_status == "DETAINED" or att_pct < 65.0:
        return {
            "result": "INELIGIBLE",
            "rule_id": "SUPP-ELIG-01",
            "source_doc_id": source_doc,
            "section": section,
            "reason": f"Student is detained in {course_code} due to low attendance ({att_pct}% < 65%). Must repeat the course."
        }
    elif result_status in ["FAIL", "ABSENT"]:
        return {
            "result": "ELIGIBLE",
            "rule_id": "SUPP-ELIG-01",
            "source_doc_id": source_doc,
            "section": section,
            "previous_result": result_status,
            "marks_obtained": latest_exam["total_marks"],
            "reason": f"Student obtained {result_status} ({latest_exam['total_marks']}/{latest_exam['max_marks']}) in regular exam and had adequate attendance. Eligible for supplementary examination."
        }
    elif result_status == "PASS":
        return {
            "result": "INELIGIBLE",
            "rule_id": "SUPP-ELIG-01",
            "source_doc_id": source_doc,
            "section": section,
            "reason": f"Student already passed {course_code} with {latest_exam['total_marks']}/{latest_exam['max_marks']} marks."
        }
    else:
        return {
            "result": "UNKNOWN",
            "reason": f"Exam status {result_status} does not match known eligibility criteria."
        }

def check_placement_eligibility(student_id: str, as_of_date: str, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    verify_student_authorization(student_id, auth_student_id)
    profile_res = get_student_profile(student_id, auth_student_id)
    if not profile_res.get("found"):
        return {"result": "ERROR", "reason": "Student profile not found"}
    student = profile_res["student"]
    
    cgpa_rule = query_one("SELECT * FROM rule_registry WHERE rule_id = 'PLACE-CGPA-01'")
    backlog_rule = query_one("SELECT * FROM rule_registry WHERE rule_id = 'PLACE-BACKLOG-01'")
    
    min_cgpa = float(cgpa_rule["value"]) if cgpa_rule else 6.5
    max_backlogs = int(backlog_rule["value"]) if backlog_rule else 0
    
    cgpa = student["cgpa"]
    backlogs = student["active_backlogs"]
    
    cgpa_ok = cgpa >= min_cgpa
    backlog_ok = backlogs <= max_backlogs
    
    if cgpa_ok and backlog_ok:
        return {
            "result": "ELIGIBLE",
            "cgpa": cgpa,
            "min_cgpa": min_cgpa,
            "active_backlogs": backlogs,
            "max_backlogs": max_backlogs,
            "applied_rules": ["PLACE-CGPA-01", "PLACE-BACKLOG-01"],
            "source_doc_id": "PLACE-POL-2025",
            "section": "3.1",
            "reason": f"CGPA of {cgpa} meets the >= {min_cgpa} threshold and has {backlogs} active backlogs."
        }
    else:
        reasons = []
        failed_rules = []
        if not cgpa_ok:
            reasons.append(f"CGPA {cgpa} is below minimum requirement {min_cgpa}")
            failed_rules.append("PLACE-CGPA-01")
        if not backlog_ok:
            reasons.append(f"{backlogs} active backlogs exceed maximum allowed ({max_backlogs})")
            failed_rules.append("PLACE-BACKLOG-01")
            
        return {
            "result": "INELIGIBLE",
            "cgpa": cgpa,
            "min_cgpa": min_cgpa,
            "active_backlogs": backlogs,
            "max_backlogs": max_backlogs,
            "applied_rules": failed_rules,
            "source_doc_id": "PLACE-POL-2025",
            "section": "3.1",
            "reason": "; ".join(reasons)
        }

def simulate_scenario(student_id: str, hypothetical_action: str, as_of_date: str, auth_student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Deterministic what-if simulation (e.g. passing supplementary exam reduces active backlogs).
    Does NOT mutate SQLite records!
    """
    verify_student_authorization(student_id, auth_student_id)
    profile_res = get_student_profile(student_id, auth_student_id)
    if not profile_res.get("found"):
        return {"result": "ERROR", "reason": "Student profile not found"}
    student = profile_res["student"].copy()
    
    baseline_cgpa = student["cgpa"]
    baseline_backlogs = student["active_backlogs"]
    
    # Calculate hypothetical projection
    action_lower = hypothetical_action.lower()
    projected_backlogs = baseline_backlogs
    notes = []
    
    if "pass" in action_lower and ("supplementary" in action_lower or "exam" in action_lower or "backlog" in action_lower):
        if projected_backlogs > 0:
            projected_backlogs -= 1
            notes.append(f"Hypothetical clearing of 1 course reduces active backlogs from {baseline_backlogs} to {projected_backlogs}.")
        else:
            notes.append("Student already has 0 active backlogs.")
            
    # Placement eligibility projection
    cgpa_rule = query_one("SELECT * FROM rule_registry WHERE rule_id = 'PLACE-CGPA-01'")
    min_cgpa = float(cgpa_rule["value"]) if cgpa_rule else 6.5
    
    hypothetical_placement_eligible = (baseline_cgpa >= min_cgpa) and (projected_backlogs == 0)
    
    return {
        "status": "simulated",
        "baseline": {
            "student_id": student["student_id"],
            "cgpa": baseline_cgpa,
            "active_backlogs": baseline_backlogs,
            "placement_eligible": (baseline_cgpa >= min_cgpa) and (baseline_backlogs == 0)
        },
        "projected": {
            "cgpa": baseline_cgpa,
            "active_backlogs": projected_backlogs,
            "placement_eligible": hypothetical_placement_eligible
        },
        "assumptions": notes,
        "mutation_occurred": False
    }
