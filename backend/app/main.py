import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import init_db
from app.api.ask import router as ask_router
from app.api.ingest import router as ingest_router
from app.api.health import router as health_router
from app.api.sources import router as sources_router
from app.api.audit import router as audit_router
from app.api.admin import router as admin_router
from app.api.student import router as student_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables exist
    init_db()
    yield

app = FastAPI(
    title="HCLTech AI-Powered University Student Services Assistant",
    version="1.0.0",
    description="Authoritative, Grounded, and Explainable Student Services Assistant with Deterministic Tool Verification",
    lifespan=lifespan
)

# CORS Configuration
cors_origins_env = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(ask_router, tags=["Ask"])
app.include_router(ingest_router, tags=["Ingest"])
app.include_router(health_router, tags=["Health"])
app.include_router(sources_router, tags=["Sources"])
app.include_router(audit_router, tags=["Audit"])
app.include_router(admin_router, tags=["Admin"])
app.include_router(student_router, tags=["Student"])

@app.get("/")
def read_root():
    return {
        "service": "HCLTech AI-Powered University Student Services Assistant",
        "status": "online",
        "version": "1.0.0",
        "contract": "Annex C & Section 6",
        "docs_url": "/docs"
    }
