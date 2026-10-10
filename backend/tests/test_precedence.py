import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.services.policy_precedence import PolicyPrecedenceEngine

def test_annex_a_authority_precedence():
    doc_reg = {
        "doc_id": "ACAD-REG-2024",
        "title": "Academic Regulations",
        "authority_level": 1,
        "effective_from": "2024-07-01",
        "effective_to": None,
        "scope_programmes": "ALL",
        "scope_batches": "ALL"
    }
    doc_faq = {
        "doc_id": "DEPT-FAQ-2026",
        "title": "Department FAQ",
        "authority_level": 4,
        "effective_from": "2026-09-15",
        "effective_to": None,
        "scope_programmes": "ALL",
        "scope_batches": "ALL"
    }
    res = PolicyPrecedenceEngine.resolve_precedence(doc_reg, doc_faq)
    assert res["winner"]["doc_id"] == "ACAD-REG-2024"
    assert res["step"] == 3
    assert res["conflict"] is False

def test_annex_a_explicit_supersession():
    doc_reg = {
        "doc_id": "ACAD-REG-2024",
        "title": "Academic Regulations",
        "authority_level": 1,
        "effective_from": "2024-07-01",
        "scope_programmes": "ALL",
        "scope_batches": "ALL"
    }
    doc_circ = {
        "doc_id": "CIRC-2026-ATT",
        "title": "Revised Attendance Circular",
        "authority_level": 2,
        "effective_from": "2026-08-01",
        "supersedes": "ACAD-REG-2024#7.2",
        "scope_programmes": "ALL",
        "scope_batches": "2024+"
    }
    res = PolicyPrecedenceEngine.resolve_precedence(doc_circ, doc_reg)
    assert res["winner"]["doc_id"] == "CIRC-2026-ATT"
    assert res["step"] == 2
    assert res["conflict"] is False

def test_annex_a_recency_same_authority():
    doc_1 = {
        "doc_id": "CIRC-2025-01",
        "title": "Circular Jan 2025",
        "authority_level": 2,
        "effective_from": "2025-01-01"
    }
    doc_2 = {
        "doc_id": "CIRC-2025-09",
        "title": "Circular Sep 2025",
        "authority_level": 2,
        "effective_from": "2025-09-01"
    }
    res = PolicyPrecedenceEngine.resolve_precedence(doc_1, doc_2)
    assert res["winner"]["doc_id"] == "CIRC-2025-09"
    assert res["step"] == 4
    assert res["conflict"] is False

def test_annex_a_unresolved_conflict():
    doc_x = {
        "doc_id": "CIRC-2026-X",
        "title": "Notice X",
        "authority_level": 2,
        "effective_from": "2026-05-01",
        "supersedes": None
    }
    doc_y = {
        "doc_id": "CIRC-2026-Y",
        "title": "Notice Y",
        "authority_level": 2,
        "effective_from": "2026-05-01",
        "supersedes": None
    }
    res = PolicyPrecedenceEngine.resolve_precedence(doc_x, doc_y)
    assert res["conflict"] is True
    assert res["step"] == 5
