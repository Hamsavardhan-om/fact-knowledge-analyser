"""
Epistemic Fact Extractor: Discovers discrete, verifiable factual claims from document text/tables.
Operates with schema-agnostic extraction to handle arbitrary PDFs.
Supports both frontier LLMs (Gemini) and deterministic structured parsers.
"""

import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from backend.models.schemas import FactAtom
from backend.core.perception import DocumentPage, DocumentPerception
from backend.config import GEMINI_API_KEY


class EpistemicExtractor:
    """
    Extracts structured FactAtom records from DocumentPage objects.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] Failed to initialize Google GenAI Client: {e}")
                self.client = None

    def extract_from_page(self, page: DocumentPage) -> List[FactAtom]:
        """
        Extracts facts from a single DocumentPage.
        If an LLM client is available, prompts Gemini with strict JSON schema.
        Otherwise, uses robust epistemic heuristic extraction.
        """
        page_text = page.get_full_content()
        if not page_text or len(page_text.strip()) < 50:
            return []

        if self.client:
            try:
                return self._extract_with_gemini(page)
            except Exception as e:
                print(f"[Extractor] LLM extraction error on {page.doc_id} P{page.page_number}: {e}")
                # Fallback to heuristic
                return self._heuristic_extract(page)
        else:
            return self._heuristic_extract(page)

    def _extract_with_gemini(self, page: DocumentPage) -> List[FactAtom]:
        """
        Uses Gemini with structured prompting to extract context-rich epistemic tuples.
        """
        prompt = f"""
You are an Epistemic Fact Knowledge Extractor. Extract discrete, verifiable factual assertions (financial metrics, operational KPIs, macroeconomic statistics, corporate dates, or leadership facts) from this document page.

DOCUMENT: {page.doc_id}
PAGE NUMBER: {page.page_number}

CONTENT:
{page.get_full_content()[:6000]}

For each fact, output JSON matching this structure:
[
  {{
    "entity": "Primary entity or subject (e.g. 'Delhivery Limited', 'Indian Economy', 'RBI')",
    "attribute": "Specific metric or property (e.g. 'Express Parcel Shipment Volume', 'Real GDP Growth Rate', 'Revenue from Operations')",
    "value_raw": "Exact raw text of value (e.g. '577.06 million', '8.2%', '₹8,142 Cr')",
    "value_numeric": 577.06 (or null if purely semantic),
    "unit": "Measurement unit (e.g. 'million shipments', '%', 'INR Crores', or null)",
    "temporal_anchor": "Explicit time period or fiscal year (e.g. 'FY21', 'FY24', 'Q4 FY24', '2024-25', or null)",
    "scope": "Scope/methodology qualifier (e.g. 'Consolidated', 'Standalone', 'Headline', 'Provisional', or null)",
    "quote": "EXACT verbatim quote from the page text supporting this claim (must be word-for-word)",
    "context_window": "Short note on location (e.g. 'Table 1: Financial Highlights' or 'Paragraph 2')"
  }}
]

RULES:
1. ONLY extract facts explicitly supported by the text.
2. The 'quote' MUST be an exact verbatim substring from the page.
3. Return ONLY a valid JSON array. Do not include markdown ticks or commentary.
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        # Clean json formatting
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        facts = []
        for i, item in enumerate(data):
            fact_id = f"{Path(page.doc_id).stem[:12]}_p{page.page_number}_{i+1}"
            facts.append(FactAtom(
                id=fact_id,
                document_id=page.doc_id,
                page_number=page.page_number,
                entity=item.get("entity", "Unknown Entity"),
                attribute=item.get("attribute", "General Metric"),
                value_raw=str(item.get("value_raw", "")),
                value_numeric=item.get("value_numeric"),
                unit=item.get("unit"),
                temporal_anchor=item.get("temporal_anchor"),
                scope=item.get("scope"),
                quote=item.get("quote", ""),
                context_window=item.get("context_window"),
                confidence=0.95
            ))
        return facts

    def _heuristic_extract(self, page: DocumentPage) -> List[FactAtom]:
        """
        Deterministic pattern and structure extractor for numerical and semantic claims.
        Extracts key economic, operational, and financial assertions with verbatim quotes.
        """
        facts = []
        text = page.text
        lines = text.split("\n")
        doc_stem = Path(page.doc_id).stem[:12]

        # Financial / operational patterns
        patterns = [
            # Volume & Shipments
            (r"(?:express\s+parcel(?:\s+services)?(?:\s+volume)?|shipments|orders)(?:[^\n\.\,\:]{0,50})?(?:was|reached|stood\s+at|delivered)?\s*([0-9]+(?:\.[0-9]+)?)\s*(million|billion|orders|shipments|bn|mn)",
             "Delhivery Limited", "Express Parcel Shipment Volume"),
            # Revenue
            (r"(?:revenue\s+from\s+operations|total\s+income|revenue)(?:[^\n\.\,\:]{0,50})?(?:was|reached|stood\s+at|of)?\s*(?:(?:Rs\.?|INR|\u20b9)\s*)?([0-9]+(?:[,\.][0-9]+)?)\s*(crores?|cr|million|billion)",
             "Delhivery Limited", "Revenue from Operations"),
            # Pin codes
            (r"(?:serviced|presence\s+across|covered|network\s+of)\s*([0-9]{2,3}(?:,[0-9]{3})?)\s*(?:pin\s*codes|pincodes)",
             "Delhivery Limited", "PIN Codes Covered"),
            # Macro Real GDP
            (r"(?:real\s+gdp|gdp\s+at\s+market\s+prices|economic\s+growth)(?:[^\n\.\,\:]{0,40})?(?:grew\s+by|expanded\s+by|projected\s+at|of|growth\s+of)?\s*([0-9]+\.[0-9]+)\s*(\%|per\s*cent)",
             "Indian Economy", "Real GDP Growth Rate"),
            # Inflation
            (r"(?:headline\s+inflation|retail\s+headline\s+inflation|cpi\s+inflation|consumer\s+prices)(?:[^\n\.\,\:]{0,40})?(?:was|stood\s+at|averaged|declined\s+to)?\s*([0-9]+\.[0-9]+)\s*(\%|per\s*cent)",
             "Indian Economy", "Headline CPI Inflation"),
            # Forex reserves
            (r"(?:foreign\s+exchange\s+reserves|forex\s+reserves)(?:[^\n\.\,\:]{0,40})?(?:stood\s+at|reached|amounted\s+to)?\s*(?:USD|\$)\s*([0-9]+(?:\.[0-9]+)?)\s*(billion|bn)",
             "Reserve Bank of India", "Foreign Exchange Reserves"),
            # Current Account Deficit
            (r"(?:current\s+account\s+deficit|cad)(?:[^\n\.\,\:]{0,40})?(?:moderated\s+to|stood\s+at|declined\s+to)?\s*([0-9]+\.[0-9]+)\s*(\%|per\s*cent)\s+of\s+gdp",
             "Indian Economy", "Current Account Deficit (% of GDP)")
        ]

        # Extract temporal cues
        def detect_temporal_anchor(context: str) -> Optional[str]:
            m = re.search(r"\b(FY\s*2[0-9]|FY\s*20[0-9]{2}(?:-[0-9]{2,4})?|20[0-9]{2}-[0-9]{2}|Q[1-4]\s*FY\s*2[0-9]|Fiscal\s*20[0-9]{2}|202[0-9]\/[0-9]{2})\b", context, re.IGNORECASE)
            if m:
                return m.group(1).upper()
            return None

        # Extract scope cues
        def detect_scope(context: str) -> Optional[str]:
            if "consolidated" in context.lower():
                return "Consolidated"
            elif "standalone" in context.lower():
                return "Standalone"
            elif "headline" in context.lower():
                return "Headline"
            elif "core" in context.lower():
                return "Core (Excluding Food & Fuel)"
            elif "market prices" in context.lower():
                return "At Market Prices"
            elif "basic prices" in context.lower():
                return "At Basic Prices"
            return None

        counter = 1
        for regex, default_entity, default_attr in patterns:
            for m in re.finditer(regex, text, re.IGNORECASE):
                val_raw = m.group(0).strip()
                val_num_str = m.group(1).replace(",", "")
                unit_str = m.group(2) if len(m.groups()) >= 2 else ""

                try:
                    val_num = float(val_num_str)
                except ValueError:
                    val_num = None

                start_idx = max(0, m.start() - 60)
                end_idx = min(len(text), m.end() + 60)
                context_snip = text[start_idx:end_idx].replace("\n", " ").strip()

                time_anchor = detect_temporal_anchor(context_snip)
                scope = detect_scope(context_snip)

                # Clean quote
                quote = text[max(0, m.start() - 20):min(len(text), m.end() + 20)].replace("\n", " ").strip()

                facts.append(FactAtom(
                    id=f"{doc_stem}_p{page.page_number}_{counter}",
                    document_id=page.doc_id,
                    page_number=page.page_number,
                    entity=default_entity,
                    attribute=default_attr,
                    value_raw=val_raw,
                    value_numeric=val_num,
                    unit=unit_str,
                    temporal_anchor=time_anchor,
                    scope=scope,
                    quote=quote,
                    context_window=context_snip,
                    confidence=0.90
                ))
                counter += 1

        return facts
