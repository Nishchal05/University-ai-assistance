from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AnswerType(str, Enum):
    retrieved_fact = "retrieved_fact"
    calculated = "calculated"
    not_found = "not_found"
    clarification_needed = "clarification_needed"
    refused = "refused"
    conflict_flagged = "conflict_flagged"

class Citation(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    page: Optional[int] = None
    version: Optional[str] = None
    effective_from: Optional[str] = None

class ToolInvocation(BaseModel):
    tool: str
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    status: Optional[str] = "ok"
    ms: Optional[int] = None

class AppliedRule(BaseModel):
    rule_id: str
    value: str
    source_doc_id: str

class ConflictItem(BaseModel):
    doc_ids: List[str]
    description: str

class AskRequest(BaseModel):
    question: str
    as_of_date: Optional[str] = None

class AskResponse(BaseModel):
    trace_id: str
    answer: str
    answer_type: AnswerType
    citations: List[Citation] = Field(default_factory=list)
    tools_invoked: List[ToolInvocation] = Field(default_factory=list)
    applied_rules: List[AppliedRule] = Field(default_factory=list)
    conflicts_detected: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str
    as_of_date: str

class SourceRegisterItem(BaseModel):
    doc_id: str
    title: str
    issuer: str
    authority_level: int
    doc_type: str
    version: str
    effective_from: str
    effective_to: Optional[str] = None
    supersedes: Optional[str] = None
    scope_programmes: str = "ALL"
    scope_batches: str = "ALL"
    provenance: str
    retrieved_on: str
    synthetic: str = "N"
    chunks_count: Optional[int] = 0

class IngestResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    api: str
    vector_store: str
    sqlite: str
    llm: str
    llm_mode: str
    details: Dict[str, Any]

class AuditRecord(BaseModel):
    trace_id: str
    timestamp: str
    student_id: Optional[str] = None
    question_category: str
    question: str
    sources_retrieved: List[Dict[str, Any]] = Field(default_factory=list)
    precedence_decision: Optional[str] = None
    tools_invoked: List[Dict[str, Any]] = Field(default_factory=list)
    applied_rules: List[str] = Field(default_factory=list)
    conflicts_detected: List[Dict[str, Any]] = Field(default_factory=list)
    answer_type: AnswerType
    response_payload: Optional[Dict[str, Any]] = None
    model: str
    llm_calls: int = 1
    tokens: int = 0
    latency_ms: int = 0

class StudentSchema(BaseModel):
    student_id: str
    full_name: str
    programme: str
    batch_year: int
    current_semester: int
    cgpa: float
    active_backlogs: int

class CourseSchema(BaseModel):
    course_code: str
    course_name: str
    programme: str
    semester: int
    credits: int

class AttendanceItem(BaseModel):
    course_code: str
    course_name: Optional[str] = None
    classes_held: int
    classes_attended: int
    attendance_pct: float

class ResultItem(BaseModel):
    course_code: str
    course_name: Optional[str] = None
    exam_session: str
    exam_type: str
    internal_marks: int
    external_marks: int
    total_marks: int
    max_marks: int
    result: str

class StudentProfileResponse(BaseModel):
    student: StudentSchema
    attendance: List[AttendanceItem]
    results: List[ResultItem]
