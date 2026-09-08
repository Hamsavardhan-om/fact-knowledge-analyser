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
