# System Limitations and Boundary Conditions

This document identifies explicit technical limitations, known edge cases, and scope boundaries of the current MVP implementation.

---

## 1. Authentication and Identity Context
- **Limitation:** The demo frontend uses a synthetic student selector dropdown to attach the `X-Student-Id` header.
- **Production Requirement:** In an enterprise production deployment, the `X-Student-Id` header would be extracted and injected by an API Gateway after verifying a cryptographically signed OAuth2/OIDC JWT bearer token.

---

## 2. Document Processing and OCR
- **Current Scope:** PDF text extraction is handled via `pypdf`, DOCX via `python-docx`, and Markdown/Text via structured parsing.
- **Limitation:** Photocopied or scanned bitmap PDFs lacking native text streams require an OCR engine (such as Tesseract OCR or EasyOCR). Scanned image-only PDFs will yield empty text extraction unless pre-processed with an OCR pipeline.

---

## 3. Local LLM Latency & Hardware Dependencies
- **Dual Mode Support:** The backend supports both local Ollama (`qwen2.5:7b-instruct`) and deterministic Mock mode (`LLM_MODE=mock`).
- **Limitation:** Running local 7B-8B parameter models requires a minimum of 8 GB RAM and preferably an NVIDIA GPU for sub-second token generation. On CPU-only environments, Ollama inference latency can range from 3 to 10 seconds per query.

---

## 4. Multi-Clause Complex Supersessions
- **Handling:** The current Annex A precedence engine resolves document-level and clause-level supersessions using standard references (e.g. `ACAD-REG-2024#7.2`).
- **Limitation:** Ambiguous textual supersessions without explicit clause markers (e.g., *"this circular supersedes all previous circulars to the extent of any inconsistency"*) require human administrative confirmation and are flagged as `conflict_flagged` rather than resolved heuristically.

---

## 5. Temporal Validity
- Future circulars whose `effective_from > as_of_date` are correctly categorized as `upcoming` and excluded from current factual rules. However, notifications that have expired (`effective_to < as_of_date`) are excluded completely rather than being archived into historical transcripts.
