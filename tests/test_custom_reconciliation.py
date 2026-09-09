"""
Tests for section-specific dialectic comparison and custom 4-case reconciliation engine.
"""

from backend.core.storage import KnowledgeStore
from backend.models.schemas import VerdictType, DivergenceDimension


def test_section_reconciliation_delhivery():
    store = KnowledgeStore()
    state = store.get_section_state('delhivery')
    assert state["section"] == 'delhivery'
    assert state["total_documents"] == 3
    assert state["total_verdicts"] == 6

    counts = state["verdict_counts"]
    assert counts[VerdictType.CORROBORATED.value] >= 1
    assert counts[VerdictType.APPARENT_CONTRADICTION.value] >= 1
    assert counts[VerdictType.EXTRACTION_FAILURE.value] >= 1


def test_section_reconciliation_macro():
    state = KnowledgeStore().get_section_state('india-macroeconomy')
    assert 'macro' in state["section"] or 'india' in state["section"]
    assert state["total_documents"] == 3
    assert state["total_verdicts"] == 6

    counts = state['verdict_counts']
    assert counts[VerdictType.CORROBORATED.value] >= 1
    assert counts[VerdictType.GENUINE_CONTRADICTION.value] >= 1
    assert counts[VerdictType.APPARENT_CONTRADICTION.value] >= 1
    assert counts[VerdictType.EXTRACTION_FAILURE.value] >= 1


def test_custom_upload_four_case_reconciliation():
    from backend.models.schemas import DocumentSummary, FactAtom
    store = KnowledgeStore()
    if not store.custom_facts:
        f1 = FactAtom(
            id="test_batch_1",
            document_id="doc_a.pdf",
            page_number=1,
            entity="Cognizant",
            attribute="Target Graduation Batch",
            value_raw="graduating in 2027",
            quote="Candidates graduating in 2027 are eligible"
        )
        f2 = FactAtom(
            id="test_batch_2",
            document_id="doc_a.pdf",
            page_number=2,
            entity="Cognizant",
            attribute="Target Graduation Batch",
            value_raw="graduating in 2027",
            quote="Eligible students graduating in 2027 batch"
        )
        f3 = FactAtom(
            id="test_comp_high",
            document_id="doc_a.pdf",
            page_number=3,
            entity="Cognizant",
            attribute="Role Compensation Package",
            value_raw="INR 18 LPA",
            value_numeric=18.0,
            quote="Compensation offered is INR 18 LPA"
        )
        f4 = FactAtom(
            id="test_comp_low",
            document_id="doc_a.pdf",
            page_number=7,
            entity="Cognizant",
            attribute="Role Compensation Package",
            value_raw="CTC: 6.75 LPA",
            value_numeric=6.75,
            quote="Designated track CTC: 6.75 LPA"
        )
        store.custom_facts = {f.id: f for f in [f1, f2, f3, f4]}
        store.custom_documents = {
            "doc_a.pdf": DocumentSummary(
                document_id="doc_a.pdf",
                total_pages=10,
                extracted_facts_count=4,
                file_size_bytes=2048,
                upload_timestamp="2026-01-01T00:00:00",
                is_benchmark=False
            )
        }
    verdicts = store.reconcile_custom_uploads()
    assert len(verdicts) >= 4

    types = {v.verdict_type for v in verdicts}
    assert VerdictType.CORROBORATED in types
    assert VerdictType.GENUINE_CONTRADICTION in types
    assert VerdictType.APPARENT_CONTRADICTION in types
    assert VerdictType.EXTRACTION_FAILURE in types

    corr_v = [v for v in verdicts if v.verdict_type == VerdictType.CORROBORATED][0]
    assert len(corr_v.facts) >= 2

    app_v = [v for v in verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION][0]
    assert app_v.divergence_dimension in (DivergenceDimension.SCOPE, DivergenceDimension.TIME, DivergenceDimension.UNIT)

    fail_v = [v for v in verdicts if v.verdict_type == VerdictType.EXTRACTION_FAILURE][0]
    assert "audit_notes" in fail_v.model_dump()
    assert len(fail_v.audit_notes) > 0


def test_custom_upload_deletion_and_missing_file_flow():
    from fastapi.testclient import TestClient
    from backend.main import app, store
    from backend.models.schemas import DocumentSummary, FactAtom

    client = TestClient(app)

    # Ingest a temporary test doc
    test_doc_id = "temp_test_doc.pdf"
    doc_summary = DocumentSummary(
        document_id=test_doc_id,
        total_pages=2,
        extracted_facts_count=2,
        file_size_bytes=1024,
        upload_timestamp="2026-01-01T00:00:00",
        is_benchmark=False,
        benchmark_name=None
    )
    f1 = FactAtom(
        id="fact_temp_1",
        document_id=test_doc_id,
        page_number=1,
        entity="Delhivery",
        attribute="Express Parcel Volume",
        value_raw="100 million",
        value_numeric=100.0,
        quote="Temporary fact test quote.",
        temporal_anchor="FY23",
        unit="million shipments"
    )
    store.ingest_facts(doc_summary, [f1])
    assert test_doc_id in store.custom_documents

    # Delete the document
    del_res = client.delete(f"/api/custom-documents/{test_doc_id}")
    assert del_res.status_code == 200
    assert test_doc_id not in store.custom_documents

    # Clear all to ensure it's empty
    client.delete("/api/custom-documents")
    assert len(store.custom_documents) == 0

    # Attempt to run comparison on empty custom section
    rec_res = client.post("/api/reconcile/custom")
    assert rec_res.status_code == 404
    assert "File is missing" in rec_res.json()["detail"]

    # Check section state also returns the error message
    state = store.get_section_state("custom")
    assert "File is missing" in state.get("error", "")

