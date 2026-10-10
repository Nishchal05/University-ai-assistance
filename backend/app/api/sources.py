from fastapi import APIRouter
from typing import List
from app.models.schemas import SourceRegisterItem
from app.database.db import query_all

router = APIRouter()

@router.get("/sources", response_model=List[SourceRegisterItem])
async def get_sources():
    rows = query_all("SELECT * FROM source_register ORDER BY authority_level ASC, effective_from DESC")
    return [
        SourceRegisterItem(
            doc_id=r["doc_id"],
            title=r["title"],
            issuer=r["issuer"],
            authority_level=r["authority_level"],
            doc_type=r["doc_type"],
            version=r["version"],
            effective_from=r["effective_from"],
            effective_to=r["effective_to"],
            supersedes=r["supersedes"],
            scope_programmes=r["scope_programmes"],
            scope_batches=r["scope_batches"],
            provenance=r["provenance"],
            retrieved_on=r["retrieved_on"],
            synthetic=r["synthetic"],
            chunks_count=r["chunks_count"]
        )
        for r in rows
    ]
