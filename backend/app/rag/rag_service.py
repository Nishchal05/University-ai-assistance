import os
import re
import math
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import pypdf
import docx

CHROMA_PERSIST_DIR = os.environ.get(
    "CHROMA_PERSIST_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../backend/data/chroma"))
)

COLLECTION_NAME = "university_docs"

_chroma_client = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _chroma_client

def get_doc_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)

class RAGService:
    @staticmethod
    def extract_text_from_file(file_path: str, filename: str) -> List[Dict[str, Any]]:
        """
        Extracts pages/sections from a file.
        Returns a list of segments: [{'text': str, 'page': int, 'section': str}]
        """
        lower = filename.lower()
        segments = []

        if lower.endswith(".pdf"):
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                # Automatic OCR fallback if page has no native text but contains images
                if not text.strip() and page.images:
                    try:
                        from rapidocr_onnxruntime import RapidOCR
                        from PIL import Image
                        import io
                        ocr = RapidOCR()
                        ocr_lines = []
                        for img_obj in page.images:
                            img = Image.open(io.BytesIO(img_obj.data))
                            res, _ = ocr(img)
                            if res:
                                ocr_lines.extend([line[1] for line in res])
                        text = "\n".join(ocr_lines)
                    except Exception:
                        pass

                if text.strip():
                    lines = text.split("\n")
                    sec = f"Page {page_idx + 1}"
                    for line in lines[:5]:
                        sec_match = re.search(r"(\b(?:Clause|Section|\d+\.\d+)\b[^\n]{0,40})", line, re.IGNORECASE)
                        if sec_match:
                            sec = sec_match.group(1).strip()
                            break
                    segments.append({
                        "text": text,
                        "page": page_idx + 1,
                        "section": sec
                    })

        elif lower.endswith(".docx"):
            doc = docx.Document(file_path)
            current_section = "General"
            current_paras = []
            page_estimate = 1
            para_count = 0

            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue
                para_count += 1
                if para_count % 15 == 0:
                    page_estimate += 1

                # Check if heading
                if p.style and "heading" in p.style.name.lower():
                    if current_paras:
                        segments.append({
                            "text": "\n".join(current_paras),
                            "page": page_estimate,
                            "section": current_section
                        })
                        current_paras = []
                    current_section = text
                else:
                    current_paras.append(text)

            if current_paras:
                segments.append({
                    "text": "\n".join(current_paras),
                    "page": page_estimate,
                    "section": current_section
                })

        else: # text or markdown
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            blocks = re.split(r"\n(?=#{1,4}\s+|\bClause\s+\d+|\bSection\s+\d+)", content)
            for idx, block in enumerate(blocks):
                lines = block.strip().split("\n")
                first_line = lines[0] if lines else "General"
                segments.append({
                    "text": block.strip(),
                    "page": (idx // 3) + 1,
                    "section": first_line[:50].strip("# ")
                })

        return segments

    @staticmethod
    def chunk_segments(segments: List[Dict[str, Any]], chunk_size: int = 500, overlap: int = 100) -> List[Dict[str, Any]]:
        chunks = []
        for seg in segments:
            text = seg["text"]
            page = seg["page"]
            section = seg["section"]

            if len(text) <= chunk_size:
                chunks.append({"text": text, "page": page, "section": section})
            else:
                start = 0
                while start < len(text):
                    end = min(start + chunk_size, len(text))
                    # snap to word boundary if possible
                    if end < len(text):
                        space_idx = text.rfind(" ", start, end)
                        if space_idx > start + chunk_size // 2:
                            end = space_idx
                    chunk_text = text[start:end].strip()
                    if chunk_text:
                        chunks.append({"text": chunk_text, "page": page, "section": section})
                    start = end - overlap if end < len(text) else len(text)
        return chunks

    @classmethod
    def index_document(cls, file_path: str, filename: str, metadata: Dict[str, Any]) -> int:
        segments = cls.extract_text_from_file(file_path, filename)
        chunks = cls.chunk_segments(segments)
        if not chunks:
            return 0

        collection = get_doc_collection()
        doc_id = metadata["doc_id"]

        # Delete existing chunks for this doc_id to support clean re-indexing
        try:
            collection.delete(where={"doc_id": doc_id})
        except Exception:
            pass

        ids = []
        documents = []
        metadatas = []

        for idx, ch in enumerate(chunks):
            chunk_id = f"{doc_id}_ch_{idx:04d}"
            # Extract section if clause pattern in chunk text
            clause_match = re.search(r"\b(\d+\.\d+|\bClause\s+\d+[\.\d]*)\b", ch["text"])
            chunk_section = clause_match.group(1) if clause_match else ch["section"]

            chunk_meta = {
                "doc_id": str(doc_id),
                "title": str(metadata.get("title", "")),
                "issuer": str(metadata.get("issuer", "")),
                "authority_level": int(metadata.get("authority_level", 1)),
                "doc_type": str(metadata.get("doc_type", "regulation")),
                "version": str(metadata.get("version", "1.0")),
                "effective_from": str(metadata.get("effective_from", "2024-01-01")),
                "effective_to": str(metadata.get("effective_to") or ""),
                "supersedes": str(metadata.get("supersedes") or ""),
                "scope_programmes": str(metadata.get("scope_programmes", "ALL")),
                "scope_batches": str(metadata.get("scope_batches", "ALL")),
                "page": int(ch["page"]),
                "section": str(chunk_section),
                "chunk_id": chunk_id
            }

            ids.append(chunk_id)
            documents.append(ch["text"])
            metadatas.append(chunk_meta)

        # Batch add to ChromaDB
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.add(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )

        return len(chunks)

    @classmethod
    def hybrid_search(cls, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        collection = get_doc_collection()
        total_count = collection.count()
        if total_count == 0:
            return []

        # 1. Semantic search with ChromaDB
        try:
            n_res = min(top_k * 2, total_count)
            sem_results = collection.query(
                query_texts=[query],
                n_results=n_res,
                include=["documents", "metadatas", "distances"]
            )
            items = []
            if sem_results and sem_results["ids"] and sem_results["ids"][0]:
                for idx, cid in enumerate(sem_results["ids"][0]):
                    dist = sem_results["distances"][0][idx] if "distances" in sem_results else 0.5
                    # Convert distance to similarity score
                    score = max(0.0, 1.0 - (dist / 2.0))
                    items.append({
                        "id": cid,
                        "text": sem_results["documents"][0][idx],
                        "metadata": sem_results["metadatas"][0][idx],
                        "score": round(score, 3)
                    })
        except Exception as e:
            items = []

        # 2. Keyword boost / BM25 fallback
        # If specific clauses, codes, or keywords match exactly, boost them
        query_terms = set(re.findall(r"\b[A-Za-z0-9\.\-%]{2,}\b", query.lower()))
        
        # Check all items in Chroma if semantic search missed exact clause matches
        all_data = collection.get(include=["documents", "metadatas"])
        bm25_items = []
        if all_data and all_data["ids"]:
            for idx, cid in enumerate(all_data["ids"]):
                doc_text = all_data["documents"][idx].lower()
                doc_meta = all_data["metadatas"][idx]
                matches = sum(1 for term in query_terms if term in doc_text)
                if matches > 0:
                    bm25_score = round(matches / (len(query_terms) + 1), 3)
                    bm25_items.append({
                        "id": cid,
                        "text": all_data["documents"][idx],
                        "metadata": doc_meta,
                        "bm25_score": bm25_score
                    })

        # Merge results
        merged_dict = {}
        for it in items:
            merged_dict[it["id"]] = it

        for bit in bm25_items:
            cid = bit["id"]
            if cid in merged_dict:
                merged_dict[cid]["score"] = round(merged_dict[cid]["score"] * 0.7 + bit["bm25_score"] * 0.3, 3)
            else:
                bit["score"] = round(bit["bm25_score"] * 0.6, 3)
                merged_dict[cid] = bit

        merged_list = list(merged_dict.values())
        merged_list.sort(key=lambda x: x["score"], reverse=True)
        return merged_list[:top_k]
