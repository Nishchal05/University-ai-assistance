import uuid
import time
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from app.models.schemas import AskRequest, AskResponse, AnswerType
from app.graph.workflow import get_graph

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    x_student_id: Optional[str] = Header(None, alias="X-Student-Id")
):
    trace_id = str(uuid.uuid4())[:8]
    as_of_date = request.as_of_date or datetime.now().strftime("%Y-%m-%d")
    
    # Clean student id
    auth_student_id = x_student_id.strip() if x_student_id and x_student_id.strip() else None

    # Execute LangGraph workflow
    graph = get_graph()
    initial_state = {
        "question": request.question,
        "as_of_date": as_of_date,
        "auth_student_id": auth_student_id,
        "trace_id": trace_id,
        "start_time": time.time(),
        "retrieved_chunks": [],
        "active_chunks": [],
        "upcoming_chunks": [],
        "conflicts_detected": [],
        "tools_invoked": [],
        "applied_rules": [],
        "citations": [],
        "answer_type": AnswerType.not_found.value,
        "answer": "",
        "explanation": ""
    }

    final_state = graph.invoke(initial_state)

    return AskResponse(
        trace_id=trace_id,
        answer=final_state.get("answer", ""),
        answer_type=final_state.get("answer_type", AnswerType.not_found.value),
        citations=final_state.get("citations", []),
        tools_invoked=final_state.get("tools_invoked", []),
        applied_rules=final_state.get("applied_rules", []),
        conflicts_detected=final_state.get("conflicts_detected", []),
        explanation=final_state.get("explanation", ""),
        as_of_date=as_of_date
    )
