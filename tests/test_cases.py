"""
Verification tests for the 4 Mandatory Epistemic Reconciliation Cases:
1. Corroborated fact across documents, even if expressed differently.
2. A genuine or likely contradiction.
3. An apparent contradiction explained by context (time, scope, or units).
4. An extraction or reasoning failure found and how it is handled / improved.
"""

from backend.core.storage import KnowledgeStore
from backend.models.schemas import VerdictType, DivergenceDimension


def test_four_mandatory_cases_delhivery():
    store = KnowledgeStore()
    success = store.load_benchmark("delhivery")
    assert success is True

    verdicts = store.verdicts

    # Case 1: Corroboration exists
    corr = [v for v in verdicts if v.verdict_type == VerdictType.CORROBORATED]
    assert len(corr) >= 1
    # Check that it compares facts from different documents
    assert corr[0].facts[0].document_id != corr[0].facts[1].document_id
    assert "577.06" in corr[0].facts[0].value_raw

    # Case 3: Apparent Contradiction (Time)
    app_time = [v for v in verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION and v.divergence_dimension == DivergenceDimension.TIME]
    assert len(app_time) >= 1
    assert "PIN" in app_time[0].topic or "Revenue" in app_time[0].topic

    # Case 3: Apparent Contradiction (Scope)
    app_scope = [v for v in verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION and v.divergence_dimension == DivergenceDimension.SCOPE]
    assert len(app_scope) >= 1
    assert "Consolidated" in app_scope[0].explanation or "Standalone" in app_scope[0].explanation

    # Case 4: Audited Extraction Failure
    fail_cases = [v for v in verdicts if v.verdict_type == VerdictType.EXTRACTION_FAILURE]
    assert len(fail_cases) >= 1
    assert "audit_notes" in fail_cases[0].model_dump()


def test_four_mandatory_cases_macro():
    store = KnowledgeStore()
    success = store.load_benchmark("india-macroeconomy")
    assert success is True

    verdicts = store.verdicts

    # Case 1: Corroboration (e.g. Real GDP 9.2%)
    corr = [v for v in verdicts if v.verdict_type == VerdictType.CORROBORATED]
    assert len(corr) >= 1
    assert any("9.2" in f.value_raw for f in corr[0].facts)

    # Case 2: Genuine Contradiction (Forex Reserves)
    gen_con = [v for v in verdicts if v.verdict_type == VerdictType.GENUINE_CONTRADICTION]
    assert len(gen_con) >= 1
    assert "Reserves" in gen_con[0].topic or "Forex" in gen_con[0].topic

    # Case 3: Apparent Contradiction (Scope: Headline vs Core Inflation, or General vs Central Deficit)
    app_scope = [v for v in verdicts if v.verdict_type == VerdictType.APPARENT_CONTRADICTION and v.divergence_dimension == DivergenceDimension.SCOPE]
    assert len(app_scope) >= 1

    # Case 4: Extraction/Reasoning Failure (Deflator vs Real GDP column slippage)
    fail_cases = [v for v in verdicts if v.verdict_type == VerdictType.EXTRACTION_FAILURE]
    assert len(fail_cases) >= 1
