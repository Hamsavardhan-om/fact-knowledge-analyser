"""
Tests for the Dialectic Reconciliation Engine.
Verifies proper classification of Corroboration, Apparent Contradictions,
Genuine Contradictions, and Failures.
"""

import pytest
from backend.models.schemas import FactAtom, VerdictType, DivergenceDimension
from backend.core.reconciler import DialecticReconciler


@pytest.fixture
def reconciler():
    return DialecticReconciler()


def test_corroboration_identical_facts(reconciler):
    f1 = FactAtom(
        id="f1",
        document_id="doc_a.pdf",
        page_number=10,
        entity="Delhivery",
        attribute="Express Parcel Volume",
        value_raw="577.06 million",
        value_numeric=577.06,
        unit="million",
        temporal_anchor="FY21",
        scope="Consolidated",
        quote="Express parcel volume was 577.06 million in FY21"
    )
    f2 = FactAtom(
        id="f2",
        document_id="doc_b.pdf",
        page_number=4,
        entity="Delhivery",
        attribute="Express Parcel Volume",
        value_raw="577.06 million orders",
        value_numeric=577.06,
        unit="million",
        temporal_anchor="FY21",
        scope="Consolidated",
        quote="Historical FY21 orders were 577.06 million"
    )

    verdict = reconciler.reconcile_pair("Delhivery Express Parcel", f1, f2)
    assert verdict.verdict_type == VerdictType.CORROBORATED
    assert verdict.divergence_dimension == DivergenceDimension.NONE


def test_apparent_contradiction_temporal_drift(reconciler):
    f1 = FactAtom(
        id="f1",
        document_id="prospectus_2022.pdf",
        page_number=47,
        entity="Delhivery",
        attribute="PIN Codes Serviced",
        value_raw="17,488",
        value_numeric=17488.0,
        unit="pins",
        temporal_anchor="Dec 2021",
        scope="Network",
        quote="serviced 17,488 PIN codes as of Dec 2021"
    )
    f2 = FactAtom(
        id="f2",
        document_id="annual_report_2024.pdf",
        page_number=2,
        entity="Delhivery",
        attribute="PIN Codes Serviced",
        value_raw="18,793",
        value_numeric=18793.0,
        unit="pins",
        temporal_anchor="FY24",
        scope="Network",
        quote="18,793 pin codes covered in FY24"
    )

    verdict = reconciler.reconcile_pair("PIN Codes Reach", f1, f2)
    assert verdict.verdict_type == VerdictType.APPARENT_CONTRADICTION
    assert verdict.divergence_dimension == DivergenceDimension.TIME


def test_apparent_contradiction_scope_divergence(reconciler):
    f1 = FactAtom(
        id="f1",
        document_id="annual_report.pdf",
        page_number=35,
        entity="Delhivery",
        attribute="Revenue",
        value_raw="8,141.65 Cr",
        value_numeric=8141.65,
        unit="Cr",
        temporal_anchor="FY24",
        scope="Consolidated",
        quote="Consolidated revenue 8141.65 Cr"
    )
    f2 = FactAtom(
        id="f2",
        document_id="annual_report.pdf",
        page_number=112,
        entity="Delhivery",
        attribute="Revenue",
        value_raw="7,858.91 Cr",
        value_numeric=7858.91,
        unit="Cr",
        temporal_anchor="FY24",
        scope="Standalone",
        quote="Standalone revenue 7858.91 Cr"
    )

    verdict = reconciler.reconcile_pair("Revenue Scope", f1, f2)
    assert verdict.verdict_type == VerdictType.APPARENT_CONTRADICTION
    assert verdict.divergence_dimension == DivergenceDimension.SCOPE


def test_genuine_contradiction_identical_context(reconciler):
    f1 = FactAtom(
        id="f1",
        document_id="doc_a.pdf",
        page_number=1,
        entity="RBI",
        attribute="Forex Reserves",
        value_raw="USD 640.3B",
        value_numeric=640.3,
        unit="USD B",
        temporal_anchor="End-March 2024",
        scope="Total Reserves",
        quote="Forex reserves stood at USD 640.3B as of end-March 2024"
    )
    f2 = FactAtom(
        id="f2",
        document_id="doc_b.pdf",
        page_number=90,
        entity="RBI",
        attribute="Forex Reserves",
        value_raw="USD 651.5B",
        value_numeric=651.5,
        unit="USD B",
        temporal_anchor="End-March 2024",
        scope="Total Reserves",
        quote="Forex reserves stood at USD 651.5B as at end-March 2024"
    )

    verdict = reconciler.reconcile_pair("Forex Reserves Conflict", f1, f2)
    assert verdict.verdict_type == VerdictType.GENUINE_CONTRADICTION
    assert verdict.divergence_dimension == DivergenceDimension.NONE


def test_reconcile_all_clusters(reconciler):
    f1 = FactAtom(
        id="f1",
        document_id="doc_a.pdf",
        page_number=1,
        entity="Delhivery",
        attribute="Volume",
        value_raw="500M",
        value_numeric=500.0,
        quote="Volume was 500M"
    )
    f2 = FactAtom(
        id="f2",
        document_id="doc_b.pdf",
        page_number=2,
        entity="Delhivery",
        attribute="Volume",
        value_raw="500M",
        value_numeric=500.0,
        quote="Delivered 500M"
    )
    clusters = {"Delhivery: Volume": [f1, f2]}
    verdicts = reconciler.reconcile_all_clusters(clusters)
    assert len(verdicts) == 1
    assert verdicts[0].verdict_type == VerdictType.CORROBORATED


def test_custom_upload_persists_across_benchmark_swaps():
    from backend.core.storage import KnowledgeStore
    from backend.models.schemas import DocumentSummary

    store = KnowledgeStore()
    
    # 1. Ingest a custom user document
    doc = DocumentSummary(
        document_id="user_uploaded_financials.pdf",
        total_pages=5,
        extracted_facts_count=1,
        file_size_bytes=50000,
        upload_timestamp="2026-09-09T00:00:00"
    )
    fact = FactAtom(
        id="custom_fact_999",
        document_id="user_uploaded_financials.pdf",
        page_number=1,
        entity="Acme Corp",
        attribute="Net Profit",
        value_raw="$100M",
        quote="Net profit reached $100M"
    )
    store.ingest_facts(doc, [fact])
    assert "user_uploaded_financials.pdf" in store.documents
    assert "custom_fact_999" in store.facts

    # 2. Swap benchmark to Delhivery
    store.load_benchmark("delhivery")
    assert "user_uploaded_financials.pdf" in store.documents, "Custom uploaded doc must NOT vanish on benchmark load!"
    assert "custom_fact_999" in store.facts, "Custom uploaded fact must NOT vanish on benchmark load!"
    assert any("delhivery" in d.lower() for d in store.documents.keys())

    # 3. Swap benchmark to India Macro
    store.load_benchmark("india-macroeconomy")
    assert "user_uploaded_financials.pdf" in store.documents, "Custom uploaded doc must NOT vanish on macro benchmark load!"
    assert "custom_fact_999" in store.facts, "Custom uploaded fact must NOT vanish on macro benchmark load!"
    assert any("rbi" in d.lower() for d in store.documents.keys())


