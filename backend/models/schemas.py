"""
Core Pydantic models for the Epistemic Fact Knowledge Layer (EFKL).
Defines schemas for documents, epistemic fact atoms, clusters, and dialectic reconciliation verdicts.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VerdictType(str, Enum):
    CORROBORATED = "CORROBORATED"
    GENUINE_CONTRADICTION = "GENUINE_CONTRADICTION"
    APPARENT_CONTRADICTION = "APPARENT_CONTRADICTION"
    EXTRACTION_FAILURE = "EXTRACTION_FAILURE"


class DivergenceDimension(str, Enum):
    TIME = "TIME"
    SCOPE = "SCOPE"
    UNIT = "UNIT"
    METHODOLOGY = "METHODOLOGY"
    NONE = "NONE"


class FactAtom(BaseModel):
    id: str = Field(..., description="Unique deterministic identifier for the fact")
    document_id: str = Field(..., description="Filename or ID of the source PDF")
    page_number: int = Field(..., description="Page number where the evidence is located (1-indexed)")
    entity: str = Field(..., description="Entity name (e.g., 'Delhivery Limited', 'Indian Economy')")
    attribute: str = Field(..., description="Canonical or extracted attribute name (e.g., 'Express Parcel Volume', 'Real GDP Growth')")
    value_raw: str = Field(..., description="Raw text representation of the value")
    value_numeric: Optional[float] = Field(None, description="Parsed numeric value if applicable")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'million shipments', '%', 'INR Crores')")
    temporal_anchor: Optional[str] = Field(None, description="Time anchor (e.g., 'FY20-21', 'FY24', 'Q4 FY24', '2024-25')")
    scope: Optional[str] = Field(None, description="Scope qualifier (e.g., 'Consolidated', 'Standalone', 'Headline', 'Provisional')")
    quote: str = Field(..., description="Verbatim quote from the document supporting this fact")
    context_window: Optional[str] = Field(None, description="Surrounding text or table caption for grounding")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    extraction_flags: List[str] = Field(default_factory=list, description="Quality flags or warnings")


class ReconciliationVerdict(BaseModel):
    id: str = Field(..., description="Unique ID for this reconciliation evaluation")
    topic: str = Field(..., description="Discourse topic or concept connecting the facts")
    verdict_type: VerdictType = Field(..., description="Reconciliation classification")
    fact_ids: List[str] = Field(..., description="IDs of the facts being compared")
    facts: List[FactAtom] = Field(default_factory=list, description="Full FactAtom objects involved")
    summary: str = Field(..., description="High-level summary of the finding")
    explanation: str = Field(..., description="Detailed dialectic reasoning showing why they agree, clash, or reconcile")
    divergence_dimension: Optional[DivergenceDimension] = Field(None, description="Dimension explaining the apparent conflict")
    audit_notes: Optional[str] = Field(None, description="Audit observations or notes on limitations/failures")


class DocumentSummary(BaseModel):
    document_id: str
    total_pages: int
    extracted_facts_count: int
    file_size_bytes: int
    upload_timestamp: str
    is_benchmark: bool = Field(default=False)
    benchmark_name: Optional[str] = Field(default=None)


class KnowledgeLayerState(BaseModel):
    documents: List[DocumentSummary]
    total_facts: int
    total_verdicts: int
    verdict_counts: Dict[str, int]
    verdicts: List[ReconciliationVerdict]
    all_facts: List[FactAtom]
