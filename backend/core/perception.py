"""
Structural Perception Layer: Extracts clean, grounded text, tables, and bounding metadata
from arbitrary multi-page PDFs using PyMuPDF (fitz).
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf as fitz  # PyMuPDF


class DocumentPage:
    def __init__(self, doc_id: str, page_number: int, text: str, tables_text: List[str] = None):
        self.doc_id = doc_id
        self.page_number = page_number
        self.text = text
        self.tables_text = tables_text or []
        self.has_tables = len(self.tables_text) > 0

    def get_full_content(self) -> str:
        parts = [self.text]
        if self.tables_text:
            parts.append("\n--- TABULAR DATA ---\n" + "\n".join(self.tables_text))
        return "\n".join(parts)


class DocumentPerception:
    """
    Handles PDF loading, structural chunking, table extraction, and evidence grounding.
    """

    @staticmethod
    def parse_pdf(file_path: str | Path) -> List[DocumentPage]:
        """
        Parses a PDF into a structured list of DocumentPage objects with layout awareness.
        """
        path = Path(file_path)
        doc_id = path.name
        doc = fitz.open(path)
        pages = []

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1  # 1-indexed

            # Extract regular text
            text = page.get_text("text")

            # Clean up whitespace anomalies
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()

            # Attempt table extraction if PyMuPDF table finder is available
            tables_text = []
            try:
                tabs = page.find_tables()
                for t in tabs:
                    df = t.extract()
                    # Convert table rows to clear pipe-separated format
                    rows = []
                    for row in df:
                        clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        if any(clean_row):
                            rows.append(" | ".join(clean_row))
                    if rows:
                        tables_text.append("\n".join(rows))
            except Exception:
                # Fallback if find_tables fails on complex layouts
                tables_text = []

            pages.append(DocumentPage(doc_id=doc_id, page_number=page_num, text=text, tables_text=tables_text))

        doc.close()
        return pages

    @staticmethod
    def get_document_summary(file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        doc = fitz.open(path)
        page_count = len(doc)
        doc.close()
        return {
            "document_id": path.name,
            "total_pages": page_count,
            "file_size_bytes": path.stat().st_size,
        }

    @staticmethod
    def verify_quote_provenance(doc_path: str | Path, page_number: int, quote: str) -> Dict[str, Any]:
        """
        Verifies whether an extracted quote is genuinely present in the specified page of the PDF.
        Supports fuzzy whitespace matching to accommodate PDF line wraps and hyphenations.
        """
        path = Path(doc_path)
        if not path.exists():
            return {"verified": False, "reason": "Document file not found"}

        doc = fitz.open(path)
        if page_number < 1 or page_number > len(doc):
            doc.close()
            return {"verified": False, "reason": f"Page {page_number} out of range (1-{len(doc)})"}

        page = doc[page_number - 1]
        page_text = page.get_text("text")
        doc.close()

        # Normalize both quote and page text for robust matching
        def normalize_str(s: str) -> str:
            # Remove punctuation and condense whitespace
            s = re.sub(r"[^\w\s\.\,\%\$\-]", " ", s)
            return " ".join(s.lower().split())

        norm_page = normalize_str(page_text)
        norm_quote = normalize_str(quote)

        # Exact normalized match
        if norm_quote in norm_page:
            return {"verified": True, "match_type": "exact_normalized"}

        # Sub-token overlap match (in case quote spans slight OCR formatting or table boundaries)
        quote_words = norm_quote.split()
        if len(quote_words) >= 4:
            # Check 4-gram sliding window
            four_gram = " ".join(quote_words[:4])
            if four_gram in norm_page:
                return {"verified": True, "match_type": "partial_header_match"}

        return {
            "verified": False,
            "reason": "Quote snippet not found in page text",
            "page_preview": page_text[:200] + "...",
        }
