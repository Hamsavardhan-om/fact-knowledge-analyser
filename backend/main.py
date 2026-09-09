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
    """Returns the current state of benchmark documents, facts, and reconciliation verdicts."""
    return store.get_state()


@app.get("/api/custom-state", response_model=KnowledgeLayerState)
def get_custom_knowledge_state():
    """Returns the state of user-uploaded documents, facts, and reconciliation verdicts."""
    return store.get_custom_state()


@app.get("/api/facts", response_model=List[FactAtom])
def get_facts(
    doc_id: Optional[str] = None,
    entity: Optional[str] = None,
    search: Optional[str] = None
):
    """Query facts with optional filtering."""
    facts = list(store.facts.values()) + list(store.custom_facts.values())
    if doc_id:
        facts = [f for f in facts if doc_id.lower() in f.document_id.lower()]
    if entity:
        facts = [f for f in facts if entity.lower() in f.entity.lower()]
    if search:
        s = search.lower()
        facts = [f for f in facts if s in f.attribute.lower() or s in f.value_raw.lower() or s in f.quote.lower()]
    return facts


@app.get("/api/documents")
def get_documents_with_facts(source: str = Query(default="benchmark")):
    """Returns documents along with their extracted facts.
    source='benchmark': returns only the active benchmark dataset documents (3 documents).
    source='custom': returns only user-uploaded documents.
    source='all': returns both.
    """
    target_docs = {}
    target_facts = {}

    if source in ("benchmark", "all"):
        target_docs.update(store.documents)
        target_facts.update(store.facts)

    if source in ("custom", "all"):
        target_docs.update(store.custom_documents)
        target_facts.update(store.custom_facts)

    docs = []
    for doc_id, doc in target_docs.items():
        doc_facts = [f for f in target_facts.values() if f.document_id == doc_id]
        docs.append({
            "document_id": doc.document_id,
            "total_pages": doc.total_pages,
            "extracted_facts_count": len(doc_facts),
            "file_size_bytes": doc.file_size_bytes,
            "upload_timestamp": doc.upload_timestamp,
            "is_benchmark": doc.is_benchmark,
            "benchmark_name": doc.benchmark_name,
            "facts": [f.model_dump() for f in doc_facts]
        })
    return docs


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
    and updates the user's custom upload knowledge layer.
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
        upload_timestamp=datetime.now().isoformat(),
        is_benchmark=False,
        benchmark_name=None,
        facts=new_facts
    )

    # 3. Ingest incrementally into KnowledgeStore (custom uploads isolated)
    store.ingest_facts(doc_summary, new_facts)

    return {
        "message": f"Successfully ingested {file.filename}",
        "pages_processed": len(pages),
        "facts_extracted": len(new_facts),
        "custom_documents_count": len(store.custom_documents)
    }


@app.get("/api/audit-provenance/{fact_id}")
def audit_provenance(fact_id: str):
    """
    Case 4 Auditor: Verifies whether a fact's quote is grounded in the source PDF.
    """
    fact = store.facts.get(fact_id) or store.custom_facts.get(fact_id)
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
