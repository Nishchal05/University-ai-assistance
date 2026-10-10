import os
import json
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.models.schemas import IngestResponse
from app.rag.rag_service import RAGService
from app.database.db import execute_dml

router = APIRouter()

DOCS_DIR = os.environ.get(
    "DOCUMENTS_STORAGE_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend/data/documents"))
)

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):
    try:
        meta_dict = json.loads(metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metadata JSON format: {str(e)}")

    # Validate required Source Register fields
    required_fields = ["doc_id", "title", "issuer", "authority_level", "doc_type", "version", "effective_from", "provenance"]
    for f in required_fields:
        if f not in meta_dict or str(meta_dict[f]).strip() == "":
            raise HTTPException(status_code=400, detail=f"Missing required metadata field: '{f}'")

    doc_id = str(meta_dict["doc_id"]).strip()
    os.makedirs(DOCS_DIR, exist_ok=True)
    file_location = os.path.join(DOCS_DIR, f"{doc_id}_{file.filename}")

    # Save uploaded file to disk
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Index into ChromaDB
    chunks_indexed = RAGService.index_document(
        file_path=file_location,
        filename=file.filename,
        metadata=meta_dict
    )

    # Upsert into source_register table in SQLite
    execute_dml(
        """
        INSERT OR REPLACE INTO source_register (
            doc_id, title, issuer, authority_level, doc_type, version,
            effective_from, effective_to, supersedes, scope_programmes,
            scope_batches, provenance, retrieved_on, synthetic, chunks_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc_id,
            meta_dict.get("title"),
            meta_dict.get("issuer"),
            int(meta_dict.get("authority_level", 1)),
            meta_dict.get("doc_type"),
            meta_dict.get("version"),
            meta_dict.get("effective_from"),
            meta_dict.get("effective_to"),
            meta_dict.get("supersedes"),
            meta_dict.get("scope_programmes", "ALL"),
            meta_dict.get("scope_batches", "ALL"),
            meta_dict.get("provenance"),
            meta_dict.get("retrieved_on", "2026-10-10"),
            meta_dict.get("synthetic", "N"),
            chunks_indexed
        )
    )

    return IngestResponse(
        doc_id=doc_id,
        chunks_indexed=chunks_indexed,
        status="success",
        message=f"Document {doc_id} successfully ingested with {chunks_indexed} chunks and registered."
    )
