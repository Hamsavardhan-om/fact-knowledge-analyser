"""
Adversarial Auditor & Failure Analysis Subsystem.
Implements automated self-reflection, quote provenance auditing, and failure diagnosis
as requested in Case 4 of the challenge.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from backend.models.schemas import FactAtom, ReconciliationVerdict, VerdictType
from backend.core.perception import DocumentPerception


class KnowledgeAuditor:
    """
    Audits extracted facts against raw PDF pages and identifies cognitive/extraction failures.
    """

    @staticmethod
    def audit_fact_provenance(fact: FactAtom, pdf_dir: Path | str) -> Dict[str, Any]:
        """
        Verifies that the fact's quote is grounded in the underlying PDF document.
        """
        pdf_path = Path(pdf_dir) / fact.document_id
        if not pdf_path.exists():
            return {
                "fact_id": fact.id,
                "status": "UNVERIFIED",
                "reason": f"PDF file not found at {pdf_path.name}"
            }

        verification = DocumentPerception.verify_quote_provenance(
            doc_path=pdf_path,
            page_number=fact.page_number,
            quote=fact.quote
        )

        return {
            "fact_id": fact.id,
            "document_id": fact.document_id,
            "page_number": fact.page_number,
            "status": "VERIFIED" if verification["verified"] else "FLAGGED_FAILURE",
            "details": verification
        }

    @staticmethod
    def detect_known_failure_modes(fact: FactAtom) -> Optional[Dict[str, Any]]:
        """
        Detects common extraction traps:
        1. Parenthesized negative numbers in financial tables parsed as positive.
        2. Serviced PIN codes confused with Registered Network Presence.
        3. Nine-month stub period revenue treated as full-year revenue.
        """
        quote_lower = fact.quote.lower()
        context_lower = (fact.context_window or "").lower()

        # Check for financial sign inversion
        if "(" in fact.quote and ")" in fact.quote and fact.value_numeric and fact.value_numeric > 0:
            return {
                "failure_type": "FINANCIAL_SIGN_INVERSION",
                "description": "Accounting convention uses parentheses '(X)' to signify negative value / net loss. Naive OCR or extraction treats this as positive.",
                "remediation": "Structural regex filters and table parsers must convert parenthesized values into negative floats."
            }

        # Check for 9-month vs annual confusion
        if "nine months" in quote_lower or "nine months" in context_lower:
            if fact.temporal_anchor and "FY" in fact.temporal_anchor and "9M" not in fact.temporal_anchor:
                return {
                    "failure_type": "STUB_PERIOD_TEMPORAL_CONFLATION",
                    "description": "Text explicitly refers to a 'nine months period ended', but was tagged as a full fiscal year.",
                    "remediation": "Extractor must preserve sub-annual qualifiers ('9M FYxx') to prevent false comparisons with full-year figures."
                }

        # Check for serviced vs presence PIN code conflation
        if "pin code" in quote_lower:
            if "serviced" in quote_lower and "presence" in fact.attribute.lower():
                return {
                    "failure_type": "SEMANTIC_METRIC_SLIPPAGE",
                    "description": "Document distinguishes 'PIN codes serviced' (deliveries fulfilled) from 'PIN codes presence' (physical infrastructure). Attributes were conflated.",
                    "remediation": "Attribute canonicalizer must differentiate operational delivery reach from infrastructure footprint."
                }

        return None
