from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class PolicyPrecedenceEngine:
    """
    Implements the Source Precedence Policy strictly according to Annex A:
    1. Applicability (effective dates, programme, batch)
    2. Explicit supersession (Authority 1 or 2 only)
    3. Authority level (1 > 2 > 3 > 4 > 5)
    4. Recency (later effective_from within same authority)
    5. Unresolved conflict -> conflict_flagged
    """

    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except Exception:
            return None

    @classmethod
    def filter_applicable_documents(
        cls,
        documents: List[Dict[str, Any]],
        as_of_date_str: str,
        student_programme: Optional[str] = None,
        student_batch_year: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Step 1: Returns (applicable_docs, upcoming_docs)
        """
        as_of_date = cls.parse_date(as_of_date_str) or datetime.now()
        applicable = []
        upcoming = []

        for doc in documents:
            eff_from = cls.parse_date(doc.get("effective_from"))
            eff_to = cls.parse_date(doc.get("effective_to"))

            # Check future effectiveness
            if eff_from and eff_from > as_of_date:
                upcoming.append(doc)
                continue

            # Check expired effectiveness
            if eff_to and eff_to < as_of_date:
                continue

            # Check programme scope
            scope_p = doc.get("scope_programmes", "ALL")
            if scope_p != "ALL" and student_programme:
                allowed_progs = [p.strip().upper() for p in scope_p.split(",")]
                if student_programme.strip().upper() not in allowed_progs:
                    continue

            # Check batch scope
            scope_b = str(doc.get("scope_batches", "ALL")).strip()
            if scope_b != "ALL" and student_batch_year is not None:
                if scope_b.endswith("+"):
                    try:
                        base_year = int(scope_b[:-1])
                        if student_batch_year < base_year:
                            continue
                    except ValueError:
                        pass
                else:
                    try:
                        allowed_batches = [int(b.strip()) for b in scope_b.split(",") if b.strip().isdigit()]
                        if student_batch_year not in allowed_batches:
                            continue
                    except ValueError:
                        pass

            applicable.append(doc)

        return applicable, upcoming

    @classmethod
    def resolve_precedence(
        cls,
        doc_a: Dict[str, Any],
        doc_b: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares two applicable documents according to Annex A steps 2, 3, 4.
        Returns {
            'winner': doc_a | doc_b | None,
            'loser': doc_b | doc_a | None,
            'step': int,
            'reason': str,
            'conflict': bool
        }
        """
        doc_a_id = doc_a.get("doc_id", "")
        doc_b_id = doc_b.get("doc_id", "")
        
        # If same document, no conflict
        if doc_a_id == doc_b_id:
            return {
                "winner": doc_a,
                "loser": None,
                "step": 1,
                "reason": f"Same document {doc_a_id}.",
                "conflict": False
            }

        auth_a = int(doc_a.get("authority_level", 5))
        auth_b = int(doc_b.get("authority_level", 5))

        # Level 5 is informational only and can never override anything
        if auth_a == 5 and auth_b < 5:
            return {
                "winner": doc_b,
                "loser": doc_a,
                "step": 3,
                "reason": f"{doc_a_id} is Level 5 informational and cannot override Level {auth_b} {doc_b_id}.",
                "conflict": False
            }
        if auth_b == 5 and auth_a < 5:
            return {
                "winner": doc_a,
                "loser": doc_b,
                "step": 3,
                "reason": f"{doc_b_id} is Level 5 informational and cannot override Level {auth_a} {doc_a_id}.",
                "conflict": False
            }

        # Step 2: Explicit Supersession (authority 1 or 2 only)
        supersedes_a = [s.strip().split("#")[0] for s in str(doc_a.get("supersedes", "")).split(";") if s.strip()]
        supersedes_b = [s.strip().split("#")[0] for s in str(doc_b.get("supersedes", "")).split(";") if s.strip()]

        if doc_b_id in supersedes_a and auth_a in [1, 2]:
            return {
                "winner": doc_a,
                "loser": doc_b,
                "step": 2,
                "reason": f"{doc_a_id} explicitly supersedes {doc_b_id} (step 2).",
                "conflict": False
            }
        if doc_a_id in supersedes_b and auth_b in [1, 2]:
            return {
                "winner": doc_b,
                "loser": doc_a,
                "step": 2,
                "reason": f"{doc_b_id} explicitly supersedes {doc_a_id} (step 2).",
                "conflict": False
            }

        # Step 3: Authority Level (lower number = higher authority)
        if auth_a < auth_b:
            return {
                "winner": doc_a,
                "loser": doc_b,
                "step": 3,
                "reason": f"{doc_a_id} (Authority Level {auth_a}) prevails over {doc_b_id} (Authority Level {auth_b}) (step 3).",
                "conflict": False
            }
        elif auth_b < auth_a:
            return {
                "winner": doc_b,
                "loser": doc_a,
                "step": 3,
                "reason": f"{doc_b_id} (Authority Level {auth_b}) prevails over {doc_a_id} (Authority Level {auth_a}) (step 3).",
                "conflict": False
            }

        # Step 4: Recency within same authority level
        date_a = cls.parse_date(doc_a.get("effective_from")) or datetime.min
        date_b = cls.parse_date(doc_b.get("effective_from")) or datetime.min

        if date_a > date_b:
            return {
                "winner": doc_a,
                "loser": doc_b,
                "step": 4,
                "reason": f"{doc_a_id} prevails over {doc_b_id} by later effective date (step 4).",
                "conflict": False
            }
        elif date_b > date_a:
            return {
                "winner": doc_b,
                "loser": doc_a,
                "step": 4,
                "reason": f"{doc_b_id} prevails over {doc_a_id} by later effective date (step 4).",
                "conflict": False
            }

        # Only if same authority, same date, and different documents on conflicting clauses
        return {
            "winner": None,
            "loser": None,
            "step": 5,
            "reason": f"Unresolvable conflict between {doc_a_id} and {doc_b_id}: same authority level {auth_a} and identical effective dates without explicit supersession.",
            "conflict": True
        }

    @classmethod
    def rank_and_filter_candidates(
        cls,
        retrieved_items: List[Dict[str, Any]],
        as_of_date_str: str,
        student_programme: Optional[str] = None,
        student_batch_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Filters and evaluates retrieved document items under Annex A.
        Returns:
            - active_items: applicable items in precedence order
            - upcoming_items: upcoming items (future effective date)
            - conflicts: detected conflicts
            - precedence_logs: explanation of decisions
        """
        # Deduplicate docs by doc_id
        docs_by_id = {}
        for item in retrieved_items:
            m = item.get("metadata", {})
            d_id = m.get("doc_id")
            if d_id and d_id not in docs_by_id:
                docs_by_id[d_id] = m
        all_docs = list(docs_by_id.values())

        applicable_docs, upcoming_docs = cls.filter_applicable_documents(
            all_docs, as_of_date_str, student_programme, student_batch_year
        )

        applicable_doc_ids = {d.get("doc_id") for d in applicable_docs}
        active_items = [it for it in retrieved_items if it.get("metadata", {}).get("doc_id") in applicable_doc_ids]
        upcoming_items = [it for it in retrieved_items if it.get("metadata", {}).get("doc_id") in {d.get("doc_id") for d in upcoming_docs}]

        # Check pairwise conflicts and supersessions across applicable docs
        conflicts = []
        precedence_logs = []
        superseded_targets = []  # list of (target_doc_id, target_clause or None)

        for i in range(len(applicable_docs)):
            for j in range(i + 1, len(applicable_docs)):
                doc_1 = applicable_docs[i]
                doc_2 = applicable_docs[j]
                
                d1_id = doc_1.get("doc_id")
                d2_id = doc_2.get("doc_id")
                
                # Check explicit supersession clause
                sup1 = str(doc_1.get("supersedes", "")).split(";")
                sup2 = str(doc_2.get("supersedes", ""))
                
                # If doc_1 supersedes doc_2
                for s in sup1:
                    s = s.strip()
                    if s:
                        parts = s.split("#")
                        target_id = parts[0].strip()
                        target_clause = parts[1].strip() if len(parts) > 1 else None
                        if target_id == d2_id and int(doc_1.get("authority_level", 5)) in [1, 2]:
                            superseded_targets.append((target_id, target_clause))
                            precedence_logs.append(f"{d1_id} supersedes {s} (step 2)")

                for s in str(doc_2.get("supersedes", "")).split(";"):
                    s = s.strip()
                    if s:
                        parts = s.split("#")
                        target_id = parts[0].strip()
                        target_clause = parts[1].strip() if len(parts) > 1 else None
                        if target_id == d1_id and int(doc_2.get("authority_level", 5)) in [1, 2]:
                            superseded_targets.append((target_id, target_clause))
                            precedence_logs.append(f"{d2_id} supersedes {s} (step 2)")

        # Filter out superseded chunks
        filtered_active_items = []
        for it in active_items:
            m = it.get("metadata", {})
            c_doc = m.get("doc_id")
            c_sec = m.get("section", "")
            
            is_dropped = False
            for target_id, target_clause in superseded_targets:
                if c_doc == target_id:
                    if not target_clause or (target_clause in c_sec):
                        is_dropped = True
                        break
            if not is_dropped:
                filtered_active_items.append(it)

        active_items = filtered_active_items

        # Precedence sort:
        # Step 2: Documents that explicitly superseded others prevail over superseded docs
        superseding_doc_ids = {t[0] for t in superseded_targets}
        # In our loop, doc_1 or doc_2 was the superseder:
        active_superseders = set()
        for doc in applicable_docs:
            if doc.get("doc_id") and any(doc.get("doc_id") in str(s) for s in [d.get("supersedes", "") for d in applicable_docs]):
                pass
            if doc.get("supersedes"):
                active_superseders.add(doc.get("doc_id"))

        def sort_key(it):
            m = it.get("metadata", {})
            d_id = m.get("doc_id")
            score = it.get("score", 0.0)
            is_superseder = 0 if d_id in active_superseders else 1
            auth = int(m.get("authority_level", 5))
            # Primary: is_superseder (Annex A step 2), then similarity score bucket, then authority
            score_bucket = -int(score * 10)  # groups scores by 0.1 bands
            return (is_superseder, score_bucket, auth, -score)

        active_items.sort(key=sort_key)

        return {
            "active_items": active_items,
            "upcoming_items": upcoming_items,
            "conflicts": conflicts,
            "precedence_logs": precedence_logs,
            "discarded_doc_ids": [t[0] for t in superseded_targets]
        }
