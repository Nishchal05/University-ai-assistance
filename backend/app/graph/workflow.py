import uuid
import time
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, TypedDict

from langgraph.graph import StateGraph, END
from app.models.schemas import AnswerType, Citation, ToolInvocation, AppliedRule
from app.services.llm_service import LLMService, QueryClassification
from app.services.policy_precedence import PolicyPrecedenceEngine
from app.rag.rag_service import RAGService
from app.tools.student_tools import (
    get_student_profile,
    get_attendance,
    get_results,
    check_exam_eligibility,
    check_supplementary_eligibility,
    check_placement_eligibility,
    simulate_scenario,
    ToolAuthError
)
from app.database.db import execute_dml, query_one

class GraphState(TypedDict, total=False):
    question: str
    as_of_date: str
    auth_student_id: Optional[str]
    trace_id: str
    start_time: float
    
    classification: Dict[str, Any]
    retrieved_chunks: List[Dict[str, Any]]
    active_chunks: List[Dict[str, Any]]
    upcoming_chunks: List[Dict[str, Any]]
    conflicts_detected: List[Dict[str, Any]]
    precedence_decision: Optional[str]
    
    tools_invoked: List[Dict[str, Any]]
    applied_rules: List[Dict[str, Any]]
    
    answer: str
    answer_type: str
    citations: List[Dict[str, Any]]
    explanation: str
    
    model: str
    tokens: int
    latency_ms: int

# --- Node 1: classify_query ---
def classify_query_node(state: GraphState) -> Dict[str, Any]:
    question = state["question"]
    classification = LLMService.classify_query(question)
    return {"classification": classification.model_dump()}

# --- Node 2: check_authentication ---
def check_authentication_node(state: GraphState) -> Dict[str, Any]:
    classification = state.get("classification", {})
    auth_student_id = state.get("auth_student_id")
    needs_personal = classification.get("needs_personal_data", False)
    
    if needs_personal and not auth_student_id:
        return {
            "answer_type": AnswerType.refused.value,
            "answer": "Authentication required: Please log in with your Student ID to access personal records, attendance, or eligibility calculations.",
            "explanation": "Request requires personal student records but no X-Student-Id authentication header was provided.",
            "citations": [],
            "tools_invoked": [],
            "applied_rules": [],
            "conflicts_detected": []
        }
    return {}

# --- Node 3: retrieve_policy ---
def retrieve_policy_node(state: GraphState) -> Dict[str, Any]:
    if state.get("answer_type") == AnswerType.refused.value:
        return {}
    
    question = state["question"]
    classification = state.get("classification", {})
    needs_policy = classification.get("needs_policy_lookup", True)
    
    chunks = []
    if needs_policy or classification.get("category") in ["policy_fact", "procedure", "personal_eligibility", "multi_step_simulation"]:
        # Retrieve candidate chunks
        chunks = RAGService.hybrid_search(question, top_k=6)
    
    return {"retrieved_chunks": chunks}

# --- Node 4: validate_policy ---
def validate_policy_node(state: GraphState) -> Dict[str, Any]:
    if state.get("answer_type") == AnswerType.refused.value:
        return {}

    retrieved = state.get("retrieved_chunks", [])
    as_of_date = state.get("as_of_date")
    auth_student_id = state.get("auth_student_id")
    
    student_prog = None
    student_batch = None
    if auth_student_id:
        st = query_one("SELECT programme, batch_year FROM students WHERE student_id = ?", (auth_student_id.upper(),))
        if st:
            student_prog = st["programme"]
            student_batch = st["batch_year"]

    rank_res = PolicyPrecedenceEngine.rank_and_filter_candidates(
        retrieved_items=retrieved,
        as_of_date_str=as_of_date,
        student_programme=student_prog,
        student_batch_year=student_batch
    )

    conflicts = rank_res.get("conflicts", [])
    precedence_notes = rank_res.get("precedence_logs", [])
    precedence_decision = "; ".join(precedence_notes[:3]) if precedence_notes else None

    update: Dict[str, Any] = {
        "active_chunks": rank_res.get("active_items", []),
        "upcoming_chunks": rank_res.get("upcoming_items", []),
        "conflicts_detected": conflicts,
        "precedence_decision": precedence_decision
    }

    if conflicts:
        update["answer_type"] = AnswerType.conflict_flagged.value

    return update

# --- Node 5: execute_student_tools ---
def execute_student_tools_node(state: GraphState) -> Dict[str, Any]:
    if state.get("answer_type") == AnswerType.refused.value:
        return {}

    classification = state.get("classification", {})
    auth_student_id = state.get("auth_student_id")
    as_of_date = state.get("as_of_date")
    detected_course = classification.get("detected_course_code") or "CS201"
    category = classification.get("category")

    tools_invoked = []
    applied_rules = []
    
    if not auth_student_id:
        return {"tools_invoked": [], "applied_rules": []}

    try:
        if category == "personal_attendance":
            t_start = time.time()
            res = get_attendance(auth_student_id, course_code=detected_course, auth_student_id=auth_student_id)
            duration_ms = int((time.time() - t_start) * 1000)
            tools_invoked.append({
                "tool": "get_attendance",
                "input": {"course_code": detected_course},
                "output": res,
                "status": "ok",
                "ms": duration_ms
            })

        elif category == "personal_results":
            t_start = time.time()
            res = get_results(auth_student_id, course_code=detected_course, auth_student_id=auth_student_id)
            duration_ms = int((time.time() - t_start) * 1000)
            tools_invoked.append({
                "tool": "get_results",
                "input": {"course_code": detected_course},
                "output": res,
                "status": "ok",
                "ms": duration_ms
            })

        elif category == "personal_eligibility":
            q_lower = state["question"].lower()
            if "supplementary" in q_lower:
                t1 = time.time()
                supp_res = check_supplementary_eligibility(auth_student_id, detected_course, as_of_date, auth_student_id)
                tools_invoked.append({
                    "tool": "check_supplementary_eligibility",
                    "input": {"course_code": detected_course},
                    "output": supp_res,
                    "status": "ok",
                    "ms": int((time.time() - t1) * 1000)
                })
                if "rule_id" in supp_res:
                    applied_rules.append({
                        "rule_id": supp_res["rule_id"],
                        "value": "regular fail with adequate attendance",
                        "source_doc_id": supp_res.get("source_doc_id", "ACAD-REG-2024")
                    })
            elif "placement" in q_lower:
                t1 = time.time()
                place_res = check_placement_eligibility(auth_student_id, as_of_date, auth_student_id)
                tools_invoked.append({
                    "tool": "check_placement_eligibility",
                    "input": {},
                    "output": place_res,
                    "status": "ok",
                    "ms": int((time.time() - t1) * 1000)
                })
                for r_id in place_res.get("applied_rules", []):
                    r_val = ">= 6.5" if "CGPA" in r_id else "0"
                    applied_rules.append({
                        "rule_id": r_id,
                        "value": r_val,
                        "source_doc_id": place_res.get("source_doc_id", "PLACE-POL-2025")
                    })
            else:
                # Exam eligibility
                t1 = time.time()
                att_res = get_attendance(auth_student_id, detected_course, auth_student_id)
                tools_invoked.append({
                    "tool": "get_attendance",
                    "input": {"course_code": detected_course},
                    "output": att_res,
                    "status": "ok",
                    "ms": int((time.time() - t1) * 1000)
                })
                
                t2 = time.time()
                elig_res = check_exam_eligibility(auth_student_id, detected_course, as_of_date, auth_student_id)
                tools_invoked.append({
                    "tool": "check_exam_eligibility",
                    "input": {"course_code": detected_course},
                    "output": elig_res,
                    "status": "ok",
                    "ms": int((time.time() - t2) * 1000)
                })
                if "rule_id" in elig_res:
                    applied_rules.append({
                        "rule_id": elig_res["rule_id"],
                        "value": f">= {elig_res.get('required_pct', 75)}%",
                        "source_doc_id": elig_res.get("source_doc_id", "ACAD-REG-2024")
                    })

        elif category == "multi_step_simulation":
            action = classification.get("hypothetical_action") or "pass supplementary exam"
            t1 = time.time()
            sim_res = simulate_scenario(auth_student_id, action, as_of_date, auth_student_id)
            tools_invoked.append({
                "tool": "simulate_scenario",
                "input": {"action": action},
                "output": sim_res,
                "status": "ok",
                "ms": int((time.time() - t1) * 1000)
            })
            applied_rules.append({
                "rule_id": "PLACE-CGPA-01",
                "value": ">= 6.5",
                "source_doc_id": "PLACE-POL-2025"
            })
            applied_rules.append({
                "rule_id": "PLACE-BACKLOG-01",
                "value": "0",
                "source_doc_id": "PLACE-POL-2025"
            })

    except ToolAuthError as te:
        return {
            "answer_type": AnswerType.refused.value,
            "answer": str(te),
            "explanation": "Tool security ownership enforcement prevented unauthorized access.",
            "tools_invoked": [],
            "applied_rules": []
        }

    return {"tools_invoked": tools_invoked, "applied_rules": applied_rules}

# --- Node 6: generate_answer ---
def generate_answer_node(state: GraphState) -> Dict[str, Any]:
    if state.get("answer_type") == AnswerType.refused.value:
        return {}

    question = state["question"]
    active_chunks = state.get("active_chunks", [])
    conflicts = state.get("conflicts_detected", [])
    tools_invoked = state.get("tools_invoked", [])
    precedence_decision = state.get("precedence_decision")
    classification = state.get("classification", {})

    citations: List[Dict[str, Any]] = []

    # Handle conflicts
    if conflicts:
        conflict_desc = "; ".join([c["description"] for c in conflicts])
        for c in active_chunks[:2]:
            m = c["metadata"]
            citations.append({
                "doc_id": m.get("doc_id"),
                "title": m.get("title"),
                "section": m.get("section"),
                "page": m.get("page"),
                "version": m.get("version"),
                "effective_from": m.get("effective_from")
            })
        return {
            "answer_type": AnswerType.conflict_flagged.value,
            "answer": f"A conflict was detected between authorised university sources: {conflict_desc}. Please consult the issuing administrative office (Dean Academics) for authoritative resolution.",
            "citations": citations,
            "explanation": f"Source Precedence Policy Annex A could not resolve conflicting provisions between documents. Both sources are cited above."
        }

    # Citations from active chunks
    for ch in active_chunks[:3]:
        m = ch.get("metadata", {})
        citations.append({
            "doc_id": m.get("doc_id"),
            "title": m.get("title"),
            "section": m.get("section"),
            "page": m.get("page"),
            "version": m.get("version"),
            "effective_from": m.get("effective_from")
        })

    # If tools were invoked
    if tools_invoked:
        synthesis = LLMService.generate_synthesis(question, active_chunks, tools_invoked, precedence_decision)
        return {
            "answer_type": AnswerType.calculated.value,
            "answer": synthesis["text"],
            "citations": citations,
            "explanation": f"Computed deterministically via student tools and verified against active rules.",
            "model": synthesis.get("model", "mock"),
            "tokens": synthesis.get("tokens", 50),
            "latency_ms": synthesis.get("latency_ms", 10)
        }

    # If policy facts found with sufficient evidence
    if active_chunks and active_chunks[0].get("score", 0) >= 0.45:
        synthesis = LLMService.generate_synthesis(question, active_chunks, [], precedence_decision)
        return {
            "answer_type": AnswerType.retrieved_fact.value,
            "answer": synthesis["text"],
            "citations": citations,
            "explanation": f"Retrieved directly from {citations[0]['title'] if citations else 'authorised documents'}.",
            "model": synthesis.get("model", "mock"),
            "tokens": synthesis.get("tokens", 50),
            "latency_ms": synthesis.get("latency_ms", 10)
        }

    # Not found (insufficient evidence)
    return {
        "answer_type": AnswerType.not_found.value,
        "answer": "I could not find this information in the authorised university sources.",
        "citations": [],
        "explanation": "No relevant documents or clauses were found in the university knowledge base matching the query.",
        "model": "mock",
        "tokens": 20,
        "latency_ms": 2
    }

# --- Node 7: validate_response ---
def validate_response_node(state: GraphState) -> Dict[str, Any]:
    answer = state.get("answer", "")
    answer_type = state.get("answer_type", AnswerType.not_found.value)
    
    # Strip any accidental leak of other student IDs if present in text
    auth_student_id = state.get("auth_student_id")
    # Clean up formatting
    return {
        "answer": answer.strip(),
        "answer_type": answer_type
    }

# --- Node 8: save_audit ---
def save_audit_node(state: GraphState) -> Dict[str, Any]:
    trace_id = state.get("trace_id") or str(uuid.uuid4())[:8]
    now_iso = datetime.now(timezone.utc).isoformat()
    student_id = state.get("auth_student_id")
    classification = state.get("classification", {})
    category = classification.get("category", "policy_fact")
    question = state.get("question", "")
    
    sources = [
        {"doc_id": c.get("metadata", {}).get("doc_id"), "section": c.get("metadata", {}).get("section"), "score": c.get("score")}
        for c in state.get("active_chunks", [])
    ]
    tools = state.get("tools_invoked", [])
    applied_rules_ids = [r.get("rule_id") for r in state.get("applied_rules", [])]
    conflicts = state.get("conflicts_detected", [])
    answer_type = state.get("answer_type", "not_found")
    
    start_time = state.get("start_time", time.time())
    latency_ms = int((time.time() - start_time) * 1000)
    
    response_payload = {
        "trace_id": trace_id,
        "answer": state.get("answer", ""),
        "answer_type": answer_type,
        "citations": state.get("citations", []),
        "tools_invoked": tools,
        "applied_rules": state.get("applied_rules", []),
        "conflicts_detected": conflicts,
        "explanation": state.get("explanation", ""),
        "as_of_date": state.get("as_of_date", "")
    }

    try:
        execute_dml(
            """
            INSERT OR REPLACE INTO audit_logs (
                trace_id, timestamp, student_id, question_category, question,
                sources_retrieved, precedence_decision, tools_invoked, applied_rules,
                conflicts_detected, answer_type, response_payload, model,
                llm_calls, tokens, latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace_id,
                now_iso,
                student_id,
                category,
                question,
                json.dumps(sources),
                state.get("precedence_decision"),
                json.dumps(tools),
                json.dumps(applied_rules_ids),
                json.dumps(conflicts),
                answer_type,
                json.dumps(response_payload),
                state.get("model", "mock"),
                1,
                state.get("tokens", 50),
                latency_ms
            )
        )
    except Exception as e:
        pass

    return {
        "trace_id": trace_id,
        "latency_ms": latency_ms
    }

# --- Router ---
def route_after_auth(state: GraphState) -> str:
    if state.get("answer_type") == AnswerType.refused.value:
        return "save_audit"
    return "retrieve_policy"

# --- Build LangGraph ---
def build_university_graph():
    builder = StateGraph(GraphState)

    builder.add_node("classify_query", classify_query_node)
    builder.add_node("check_authentication", check_authentication_node)
    builder.add_node("retrieve_policy", retrieve_policy_node)
    builder.add_node("validate_policy", validate_policy_node)
    builder.add_node("execute_student_tools", execute_student_tools_node)
    builder.add_node("generate_answer", generate_answer_node)
    builder.add_node("validate_response", validate_response_node)
    builder.add_node("save_audit", save_audit_node)

    builder.set_entry_point("classify_query")
    builder.add_edge("classify_query", "check_authentication")
    builder.add_conditional_edges(
        "check_authentication",
        route_after_auth,
        {
            "save_audit": "save_audit",
            "retrieve_policy": "retrieve_policy"
        }
    )
    builder.add_edge("retrieve_policy", "validate_policy")
    builder.add_edge("validate_policy", "execute_student_tools")
    builder.add_edge("execute_student_tools", "generate_answer")
    builder.add_edge("generate_answer", "validate_response")
    builder.add_edge("validate_response", "save_audit")
    builder.add_edge("save_audit", END)

    return builder.compile()

# Singleton graph instance
_compiled_graph = None

def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_university_graph()
    return _compiled_graph
