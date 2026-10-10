import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

DB_PATH = os.environ.get("SQLITE_DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend/data/university.db")))

def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        programme TEXT NOT NULL,
        batch_year INTEGER NOT NULL,
        current_semester INTEGER NOT NULL,
        cgpa REAL NOT NULL,
        active_backlogs INTEGER NOT NULL
    );
    """)

    # 2. courses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_code TEXT PRIMARY KEY,
        course_name TEXT NOT NULL,
        programme TEXT NOT NULL,
        semester INTEGER NOT NULL,
        credits INTEGER NOT NULL
    );
    """)

    # 3. attendance (attendance % NEVER stored; computed dynamically)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        student_id TEXT NOT NULL,
        course_code TEXT NOT NULL,
        classes_held INTEGER NOT NULL,
        classes_attended INTEGER NOT NULL,
        PRIMARY KEY (student_id, course_code),
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE
    );
    """)

    # 4. results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        student_id TEXT NOT NULL,
        course_code TEXT NOT NULL,
        exam_session TEXT NOT NULL,
        exam_type TEXT NOT NULL,
        internal_marks INTEGER NOT NULL,
        external_marks INTEGER NOT NULL,
        total_marks INTEGER NOT NULL,
        max_marks INTEGER NOT NULL,
        result TEXT NOT NULL,
        PRIMARY KEY (student_id, course_code, exam_session, exam_type),
        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE
    );
    """)

    # 5. rule_registry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rule_registry (
        rule_id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        parameter TEXT NOT NULL,
        operator TEXT NOT NULL,
        value TEXT NOT NULL,
        scope_programmes TEXT NOT NULL,
        scope_batches TEXT NOT NULL,
        effective_from TEXT NOT NULL,
        effective_to TEXT,
        source_doc_id TEXT NOT NULL,
        source_section TEXT NOT NULL
    );
    """)

    # 6. source_register (tracks ingested docs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source_register (
        doc_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        issuer TEXT NOT NULL,
        authority_level INTEGER NOT NULL,
        doc_type TEXT NOT NULL,
        version TEXT NOT NULL,
        effective_from TEXT NOT NULL,
        effective_to TEXT,
        supersedes TEXT,
        scope_programmes TEXT NOT NULL,
        scope_batches TEXT NOT NULL,
        provenance TEXT NOT NULL,
        retrieved_on TEXT NOT NULL,
        synthetic TEXT NOT NULL DEFAULT 'N',
        chunks_count INTEGER NOT NULL DEFAULT 0
    );
    """)

    # 7. audit_logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        trace_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        student_id TEXT,
        question_category TEXT NOT NULL,
        question TEXT NOT NULL,
        sources_retrieved TEXT NOT NULL,
        precedence_decision TEXT,
        tools_invoked TEXT NOT NULL,
        applied_rules TEXT NOT NULL,
        conflicts_detected TEXT NOT NULL,
        answer_type TEXT NOT NULL,
        response_payload TEXT NOT NULL,
        model TEXT NOT NULL,
        llm_calls INTEGER NOT NULL,
        tokens INTEGER NOT NULL,
        latency_ms INTEGER NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def query_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def execute_dml(statement: str, params: tuple = ()) -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(statement, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def execute_many(statement: str, params_list: List[tuple]) -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(statement, params_list)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
