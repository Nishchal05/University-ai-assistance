"""
Ingestion and Seeding Script for University Documents & Source Register
Creates official and synthetic test documents, records them in Source Register,
and indexes them directly into ChromaDB and SQLite.
"""

import os
import csv
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.db import init_db, execute_dml
from app.rag.rag_service import RAGService

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/documents"))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

DOCUMENTS = [
    {
        "doc_id": "ACAD-REG-2024",
        "title": "Academic Regulations for B.Tech Programmes",
        "issuer": "Office of the Dean (Academics) & Senate",
        "authority_level": 1,
        "doc_type": "regulation",
        "version": "3.1",
        "effective_from": "2024-07-01",
        "effective_to": "",
        "supersedes": "ACAD-REG-2021",
        "scope_programmes": "B.Tech CSE, B.Tech ECE",
        "scope_batches": "ALL",
        "provenance": "https://www.nitj.ac.in/academic/regulations_btech_2024.pdf",
        "retrieved_on": "2026-10-05",
        "synthetic": "N",
        "filename": "ACAD-REG-2024.md",
        "content": """# Academic Regulations for B.Tech Programmes (ACAD-REG-2024)
Office of the Dean (Academics), Version 3.1, Effective from 2024-07-01.

## Section 1: Preamble and Scope
These regulations govern all undergraduate Bachelor of Technology (B.Tech) programmes offered by the National Institute of Technology. All enrolled students in B.Tech CSE and B.Tech ECE are bound by these ordinances.

## Section 7: Attendance Requirements and Condonation
Clause 7.1: Regular Attendance
Students are expected to attend all lectures, tutorials, and laboratory sessions scheduled for each registered course.

Clause 7.2: Minimum Attendance for End-Semester Examinations
A student must secure a minimum attendance of 75% in each registered course to be eligible to appear in the end-semester examinations. Students securing less than 75% attendance are not permitted to appear in the regular end-semester examination and will be marked ineligible unless condonation is granted under Clause 7.3.

Clause 7.3: Condonation of Attendance Shortage
On valid grounds of prolonged illness, hospitalization, or participation in institute-approved sports/cultural/academic competitions, the Dean (Academics) may condone attendance shortage up to 10%. That is, students having attendance between 65% and 75% may be permitted to appear upon producing verified documentary proof and medical certificates.
Students with attendance strictly below 65% under no circumstances shall be eligible for condonation and shall be declared 'DETAINED' in that course.

## Section 8: Examination, Grading and Passing Standards
Clause 8.1: Minimum Passing Standards
The evaluation consists of continuous internal assessment (internal marks: 50) and end-semester written examination (external marks: 50), totaling 100 marks.
To pass a theory course, a student must secure a minimum of 40 marks in total (internal + external marks). Students securing less than 40 marks receive grade 'F' (FAIL).

Clause 8.4: Supplementary Examinations
Supplementary examinations are conducted once every academic session for students who:
(a) Appeared in the regular examination and secured an 'F' grade (FAIL), OR
(b) Were granted approved medical absence during regular examination sessions.
A student who was 'DETAINED' due to attendance shortage (< 65%) is NOT eligible to appear in supplementary examinations and must repeat the course in a subsequent semester.

## Section 9: Academic Backlogs and Progression
Clause 9.1: Backlog Definition
An active backlog is defined as any course in which a student has obtained grade 'F', 'ABSENT', or 'DETAINED' and has not yet cleared the course in subsequent exam sessions.
"""
    },
    {
        "doc_id": "PLACE-POL-2025",
        "title": "Campus Placement and Internship Policy 2025-2026",
        "issuer": "Centre for Training & Placement (CTP)",
        "authority_level": 2,
        "doc_type": "circular",
        "version": "2.0",
        "effective_from": "2025-08-01",
        "effective_to": "",
        "supersedes": "PLACE-POL-2024",
        "scope_programmes": "ALL",
        "scope_batches": "2022, 2023",
        "provenance": "https://www.nitj.ac.in/placement/policy_2025.pdf",
        "retrieved_on": "2026-10-05",
        "synthetic": "N",
        "filename": "PLACE-POL-2025.md",
        "content": """# Campus Placement and Internship Policy 2025-2026 (PLACE-POL-2025)
Centre for Training & Placement (CTP), Effective from 2025-08-01.

## Section 1: Objective
This policy regulates campus placement drives, registration guidelines, and recruiter eligibility criteria for graduating students.

## Section 3: Eligibility Criteria for Placement Drives
Clause 3.1: Academic CGPA Cut-off
To register with the Centre for Training & Placement and participate in campus recruitment drives, a student must possess a Cumulative Grade Point Average (CGPA) of at least 6.50 at the beginning of the 7th semester. Specific recruiting companies may enforce higher thresholds (e.g. 7.00 or 8.00), but 6.50 is the institute baseline.

Clause 3.2: Backlog Restrictions
A student must have ZERO (0) active backlogs at the time of placement registration. Students with pending backlogs are barred from registering until all backlogs are officially cleared and result notifications are published.

Clause 3.3: One-Student One-Job Policy
Once a student secures a standard campus placement job offer, they are considered placed and may only apply for designated 'Dream' category offers (salary package > 1.5x of existing offer).
"""
    },
    {
        "doc_id": "CIRC-2026-ATT",
        "title": "Circular: Revision of Minimum Attendance Threshold for Newly Admitted Batches",
        "issuer": "Office of the Dean (Academics)",
        "authority_level": 2,
        "doc_type": "circular",
        "version": "1.0",
        "effective_from": "2026-08-01",
        "effective_to": "",
        "supersedes": "ACAD-REG-2024#7.2",
        "scope_programmes": "ALL",
        "scope_batches": "2024+",
        "provenance": "https://www.nitj.ac.in/notices/circular_att_2026.pdf",
        "retrieved_on": "2026-10-06",
        "synthetic": "Y",
        "filename": "CIRC-2026-ATT.md",
        "content": """# Notification: Revision of Minimum Attendance Norms (CIRC-2026-ATT)
Office of the Dean (Academics), Ref No: NITJ/DA/2026/842, Date: 2026-08-01.

## Section 1: Supersession of Clause 7.2 for Batch 2024 Onward
Pursuant to Senate resolution dated July 20, 2026, the minimum attendance requirement for students of Batch 2024 and subsequent batches is hereby enhanced to 80% (eighty percent) in each registered course.
This notification explicitly supersedes Clause 7.2 of Academic Regulations ACAD-REG-2024 with respect to Batch 2024+ students.
Students of previous batches (Batch 2023, Batch 2022) shall continue to be governed by the 75% attendance requirement in ACAD-REG-2024.
"""
    },
    {
        "doc_id": "DEPT-FAQ-2026",
        "title": "Department Student Helpdesk FAQ",
        "issuer": "Department Student Affairs Committee",
        "authority_level": 4,
        "doc_type": "faq",
        "version": "1.1",
        "effective_from": "2026-09-15",
        "effective_to": "",
        "supersedes": "",
        "scope_programmes": "ALL",
        "scope_batches": "ALL",
        "provenance": "https://www.nitj.ac.in/faq/student_helpdesk_2026.html",
        "retrieved_on": "2026-10-06",
        "synthetic": "Y",
        "filename": "DEPT-FAQ-2026.md",
        "content": """# Department Student Helpdesk FAQ (DEPT-FAQ-2026)
Student Affairs Informal Helpdesk, Version 1.1, Effective: 2026-09-15.

## Q1: Is 65% attendance enough to sit in examinations?
Informal answer: Yes, generally professors allow any student with 65% attendance to sit in the exam without any formal medical clearance.

## Q2: Can I sit in placements if I have 1 backlog?
Informal answer: Sometimes companies do not check backlogs if you promise to clear them.
"""
    },
    {
        "doc_id": "NITJ-ACAD-POLICY-2023",
        "title": "Ordinances and Regulations for Undergraduate Programme 2023",
        "issuer": "Dr B R Ambedkar National Institute of Technology Jalandhar",
        "authority_level": 1,
        "doc_type": "regulation",
        "version": "2023.1",
        "effective_from": "2023-08-01",
        "effective_to": "",
        "supersedes": "ACAD-REG-2021",
        "scope_programmes": "ALL",
        "scope_batches": "2023+",
        "provenance": "NITJ Official Website",
        "retrieved_on": "2026-10-10",
        "synthetic": "N",
        "filename": "NITJ-UNIVERSITY-ACADEMIC POLICY.pdf"
    },
    {
        "doc_id": "NITJ-PLACEMENT-POLICY-2026",
        "title": "Placement & Internship Policy (2023-2027 Batch Onwards)",
        "issuer": "Centre for Training & Placement, NIT Jalandhar",
        "authority_level": 2,
        "doc_type": "circular",
        "version": "2026-NEP",
        "effective_from": "2023-08-01",
        "effective_to": "",
        "supersedes": "PLACE-POL-2024",
        "scope_programmes": "ALL",
        "scope_batches": "2023+",
        "provenance": "NITJ Centre for Training & Placement",
        "retrieved_on": "2026-10-10",
        "synthetic": "N",
        "filename": "NITJ-PLACEMENT-POLICY-2026.md"
    }
]

def seed_documents():
    print("--- Seeding University Documents and Source Register ---")
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db()

    csv_path = os.path.join(DATA_DIR, "source_register.csv")
    csv_rows = []

    for d in DOCUMENTS:
        # 1. Write document file if inline content provided
        doc_path = os.path.join(DOCS_DIR, d["filename"])
        if "content" in d:
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(d["content"].strip())
        elif not os.path.exists(doc_path):
            print(f"Skipping {d['doc_id']}: file {doc_path} not found.")
            continue

        # 2. Index in ChromaDB
        chunks = RAGService.index_document(doc_path, d["filename"], d)
        print(f"Indexed {d['doc_id']} ({d['title']}) with {chunks} chunks into ChromaDB.")

        # 3. Insert into SQLite source_register
        execute_dml(
            """
            INSERT OR REPLACE INTO source_register (
                doc_id, title, issuer, authority_level, doc_type, version,
                effective_from, effective_to, supersedes, scope_programmes,
                scope_batches, provenance, retrieved_on, synthetic, chunks_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                d["doc_id"], d["title"], d["issuer"], d["authority_level"],
                d["doc_type"], d["version"], d["effective_from"], d["effective_to"],
                d["supersedes"], d["scope_programmes"], d["scope_batches"],
                d["provenance"], d["retrieved_on"], d["synthetic"], chunks
            )
        )

        csv_rows.append([
            d["doc_id"], d["title"], d["issuer"], d["authority_level"],
            d["doc_type"], d["version"], d["effective_from"], d["effective_to"],
            d["supersedes"], d["scope_programmes"], d["scope_batches"],
            d["provenance"], d["retrieved_on"], d["synthetic"]
        ])

    # 4. Save Source Register CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "doc_id", "title", "issuer", "authority_level", "doc_type", "version",
            "effective_from", "effective_to", "supersedes", "scope_programmes",
            "scope_batches", "provenance", "retrieved_on", "synthetic"
        ])
        writer.writerows(csv_rows)

    print(f"Saved {len(csv_rows)} records to {csv_path} and SQLite source_register table.")

if __name__ == "__main__":
    seed_documents()
