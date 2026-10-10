import os
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.rag.rag_service import get_doc_collection
from app.database.db import query_one
from app.services.llm_service import LLM_MODE

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    vector_status = "ok"
    chroma_chunks = 0
    try:
        col = get_doc_collection()
        chroma_chunks = col.count()
    except Exception as e:
        vector_status = f"error: {str(e)}"

    sqlite_status = "ok"
    student_count = 0
    rules_count = 0
    try:
        s_res = query_one("SELECT COUNT(*) as cnt FROM students")
        student_count = s_res["cnt"] if s_res else 0
        r_res = query_one("SELECT COUNT(*) as cnt FROM rule_registry")
        rules_count = r_res["cnt"] if r_res else 0
    except Exception as e:
        sqlite_status = f"error: {str(e)}"

    overall_status = "healthy" if (vector_status == "ok" and sqlite_status == "ok") else "degraded"

    return HealthResponse(
        status=overall_status,
        api="ok",
        vector_store=vector_status,
        sqlite=sqlite_status,
        llm="ok",
        llm_mode=LLM_MODE,
        details={
            "chroma_chunks": chroma_chunks,
            "student_records": student_count,
            "rules_count": rules_count
        }
    )
