"""
FastAPI Server for Epistemic Fact Knowledge Layer (EFKL).
Provides REST endpoints for PDF ingestion, epistemic claim extraction,
dialectic reconciliation inspection, and interactive evidence audits.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.models.schemas import (
    KnowledgeLayerState,
    ReconciliationVerdict,
    FactAtom,
    DocumentSummary,
    VerdictType,
)
from backend.core.storage import KnowledgeStore
from backend.core.perception import DocumentPerception
from backend.core.extractor import EpistemicExtractor
from backend.core.auditor import KnowledgeAuditor
from backend.config import UPLOADS_DIR, BASE_DIR

app = FastAPI(
    title="Epistemic Fact Knowledge Layer (EFKL)",
    description="Cross-Document Fact Extraction & Epistemic Dialectic Reconciliation Engine",
    version="1.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = KnowledgeStore()
extractor = EpistemicExtractor()

# If store is currently empty, load the Delhivery benchmark by default
if not store.facts:
    store.load_benchmark("delhivery")


@app.get("/api/state", response_model=KnowledgeLayerState)
def get_knowledge_state():
    """Returns the current state of documents, facts, and reconciliation verdicts."""
    return store.get_state()


@app.get("/api/facts", response_model=List[FactAtom])
def get_facts(
    doc_id: Optional[str] = None,
    entity: Optional[str] = None,
    search: Optional[str] = None
):
    """Query facts with optional filtering."""
    facts = list(store.facts.values())
    if doc_id:
        facts = [f for f in facts if doc_id.lower() in f.document_id.lower()]
    if entity:
        facts = [f for f in facts if entity.lower() in f.entity.lower()]
    if search:
        s = search.lower()
        facts = [f for f in facts if s in f.attribute.lower() or s in f.value_raw.lower() or s in f.quote.lower()]
    return facts


@app.get("/api/verdicts", response_model=List[ReconciliationVerdict])
def get_verdicts(verdict_type: Optional[VerdictType] = None):
    """Get reconciliation verdicts, optionally filtered by the 4 challenge case types."""
    if verdict_type:
        return [v for v in store.verdicts if v.verdict_type == verdict_type]
    return store.verdicts


@app.post("/api/load-dataset/{name}")
def load_dataset(name: str):
    """Loads one of the verified starter datasets ('delhivery' or 'india-macroeconomy')."""
    success = store.load_benchmark(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Benchmark dataset '{name}' not found")
    return {"message": f"Successfully loaded '{name}' dataset", "state": store.get_state()}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts arbitrary PDF uploads, extracts structured facts,
    and updates the cross-document reconciliation graph incrementally.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported")

    dest_path = UPLOADS_DIR / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Perception Layer
    try:
        pages = DocumentPerception.parse_pdf(dest_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {e}")

    # 2. Extract facts from each page
    new_facts: List[FactAtom] = []
    for page in pages:
        page_facts = extractor.extract_from_page(page)
        new_facts.extend(page_facts)

    doc_summary = DocumentSummary(
        document_id=file.filename,
        total_pages=len(pages),
        extracted_facts_count=len(new_facts),
        file_size_bytes=dest_path.stat().st_size,
        upload_timestamp=datetime.now().isoformat()
    )

    # 3. Ingest incrementally into KnowledgeStore
    store.ingest_facts(doc_summary, new_facts)

    return {
        "message": f"Successfully ingested {file.filename}",
        "pages_processed": len(pages),
        "facts_extracted": len(new_facts),
        "total_verdicts": len(store.verdicts)
    }


@app.get("/api/audit-provenance/{fact_id}")
def audit_provenance(fact_id: str):
    """
    Case 4 Auditor: Verifies whether a fact's quote is grounded in the source PDF.
    """
    fact = store.facts.get(fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")

    # Look in uploads dir first, then starter-datasets dirs
    potential_dirs = [
        UPLOADS_DIR,
        BASE_DIR.parent / "starter-datasets" / "starter-datasets" / "delhivery",
        BASE_DIR.parent / "starter-datasets" / "starter-datasets" / "india-macroeconomy",
    ]

    target_dir = None
    for d in potential_dirs:
        if (d / fact.document_id).exists():
            target_dir = d
            break

    if not target_dir:
        return {
            "fact_id": fact.id,
            "status": "SOURCE_NOT_ACCESSIBLE",
            "message": f"Source PDF '{fact.document_id}' not located in local storage"
        }

    audit_result = KnowledgeAuditor.audit_fact_provenance(fact, target_dir)
    failure_trap = KnowledgeAuditor.detect_known_failure_modes(fact)

    return {
        "fact": fact,
        "provenance_audit": audit_result,
        "failure_trap_diagnosis": failure_trap
    }


# Mount frontend static directory
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
def serve_index():
    index_file = BASE_DIR / "frontend" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Epistemic Fact Knowledge Layer API active"}
