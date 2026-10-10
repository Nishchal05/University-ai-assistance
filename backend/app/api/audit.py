import json
from fastapi import APIRouter, HTTPException
from app.models.schemas import AuditRecord, AnswerType
from app.database.db import query_one

router = APIRouter()

@router.get("/audit/{trace_id}", response_model=AuditRecord)
async def get_audit_record(trace_id: str):
    row = query_one("SELECT * FROM audit_logs WHERE trace_id = ?", (trace_id.strip(),))
    if not row:
        raise HTTPException(status_code=404, detail=f"Audit trace {trace_id} not found.")

    return AuditRecord(
        trace_id=row["trace_id"],
        timestamp=row["timestamp"],
        student_id=row["student_id"],
        question_category=row["question_category"],
        question=row["question"],
        sources_retrieved=json.loads(row["sources_retrieved"] or "[]"),
        precedence_decision=row["precedence_decision"],
        tools_invoked=json.loads(row["tools_invoked"] or "[]"),
        applied_rules=json.loads(row["applied_rules"] or "[]"),
        conflicts_detected=json.loads(row["conflicts_detected"] or "[]"),
        answer_type=AnswerType(row["answer_type"]),
        response_payload=json.loads(row["response_payload"] or "{}"),
        model=row["model"],
        llm_calls=row["llm_calls"],
        tokens=row["tokens"],
        latency_ms=row["latency_ms"]
    )
