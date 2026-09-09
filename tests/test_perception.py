"""
Tests for the Perception and Provenance Layer.
Verifies PDF loading, page iteration, and quote verification against source files.
"""

from pathlib import Path
from backend.config import BASE_DIR
from backend.core.perception import DocumentPerception

STARTER_PDF = BASE_DIR.parent / "starter-datasets" / "starter-datasets" / "delhivery" / "03-delhivery-q4-fy24-earnings-presentation.pdf"


def test_perception_parsing():
    if not STARTER_PDF.exists():
        return

    pages = DocumentPerception.parse_pdf(STARTER_PDF)
    assert len(pages) == 27
    assert pages[0].page_number == 1
    assert "DELHIVERY" in pages[0].text.upper()


def test_quote_provenance_verification():
    if not STARTER_PDF.exists():
        return

    # Verify existing quote on page 1
    res = DocumentPerception.verify_quote_provenance(STARTER_PDF, 1, "National Stock Exchange of India Limited")
    assert res["verified"] is True

    # Verify non-existing quote fails
    res_fake = DocumentPerception.verify_quote_provenance(STARTER_PDF, 1, "This text definitely does not exist here")
    assert res_fake["verified"] is False
